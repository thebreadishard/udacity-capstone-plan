"""Rung C — train the equivariant Δ-Hessian model on the pair model's pool and read it out with the pair model's own read-outs.

Registered as recipe C1 on 27 Sep 2026 (`PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`); the levers since then are switches
of `rungC_config.TrainConfig`, and the carried recipe is `probes/chain_runner.RECIPE_V11` (hybrid head on pattern f, `--aux both`, early
stopping on an inner validation set). Same pool, sizes, seeds and hold-outs as `e7_rungB_pairs.py` (E6 splits, or `--split layerB`), same
analytic-Hessian substitution and read-out functions: the model's Cartesian ΔH is projected to the pair model's internal coordinates with the
pseudo-inverse of the Wilson B. Output: a JSON record (zero rule, per size and seed the read-outs on each hold-out, wall time) and a
markdown table beside it; with `--save-model` the trained hybrid model per size and seed.

    python m05/rungC_train.py corpus/molecules out/E7_rungC_<date> --use-analytic [--sizes 45,100,all] [--seeds 0,1,2] [--threads 8] …
    python m05/rungC_train.py corpus/molecules out/_smoke --smoke          # 5 molecules, 2 epochs, seed 0: mechanics only"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
import e6_learning_curve as E6
import e7_t2_posthoc as PH
import e7_t2_sqm as T2
import rungC_intensities as RI
from e7_rungB_pairs import molecule_pairs, readouts
from rungC_config import KRING_WEIGHT, SMOKE_HOLDOUT, SMOKE_POOL, TrainConfig, parse_config
from rungC_equivariant import (
    AGGREGATION,
    BOHR2ANG,
    LOSS_SCALE,
    DeltaHessianModel,
    console_utf8_safe,
    hinge_classes,
    load_molecule,
    load_state_compat,
    to_torch,
)
from rungC_hybrid import HybridDeltaFModel, input_scales, pair_feature_stats, primitive_parity, primitive_pool_matrix
from rungC_targets import SCALE_LIMIT, cached_pattern_target, readout_residual, scale_ratio, weighted_residual

from dpir.provenance import provenance


class Scaled(torch.nn.Module):
    """The equivariant model with a fixed output scale: the training set's RMS ΔH (the pair model scales its targets per class the same way;
    without it the head starts four orders of magnitude above the targets and spends its epochs shrinking). Equivariance is untouched."""

    def __init__(self, model: DeltaHessianModel, scale: float, class_scale=None):
        super().__init__()
        self.model, self.scale = model, float(scale)
        # one scale per entry class (own block, bonded pair, non-bonded pair) when given
        self.class_scale = None if class_scale is None else [float(x) for x in class_scale]

    def scale_tensor(self, t):
        if self.class_scale is None:
            return self.scale
        s = torch.as_tensor(self.class_scale, dtype=torch.float32)[t["cls"]]      # n × n
        return s.repeat_interleave(3, 0).repeat_interleave(3, 1)                     # 3n × 3n

    def forward(self, Z, pos, H_low, t=None):
        return self.model(Z, pos, H_low) * (self.scale if t is None else self.scale_tensor(t))


COV_RADIUS_ANG = {1: 0.31, 6: 0.76, 7: 0.71, 8: 0.66, 9: 0.57, 16: 1.05, 17: 1.02}


def entry_classes(m: dict) -> torch.Tensor:
    """n × n long tensor: 0 = the atom's own 3×3 block, 1 = a bonded pair (distance < 1.25 × the sum of covalent radii), 2 = any other pair."""
    pos = np.asarray(m["pos"], float)
    Z = np.asarray(m["Z"])
    r = np.array([COV_RADIUS_ANG.get(int(z), 0.8) for z in Z]) / BOHR2ANG
    d = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=-1)
    cls = np.full(d.shape, 2, dtype=np.int64)
    cls[d < 1.25 * (r[:, None] + r[None, :])] = 1
    np.fill_diagonal(cls, 0)
    return torch.as_tensor(cls)


PAIR_CLASS_NAMES = ("diag_bond", "diag_angle", "diag_dihedral", "diag_other", "off_bondbond", "off_other", "off_twobond", "off_dist2",
                    "off_dist3")   # e7_rungB_pairs classes 0–8 (6 = pattern d, 7 = e, 8 = f)
PATTERN_SCALE_FLOOR = 0.1   # no class scale below this fraction of the largest: unfloored scales let the Cartesian head fit noise (1 Oct 2026)


def _checked_pairs(mol_dir: Path, m: dict, pattern: str, what: str, return_atoms: bool = False) -> tuple[dict, tuple]:
    """(geometry, molecule_pairs output): the pair model's pattern on the molecule's own geometry. Its Wilson B must equal the loader's (same
    geomeTRIC construction) — a mismatch is refused, not tolerated."""
    g = json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))
    out = molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"], float), np.asarray(m["F_low"], float), return_atoms=return_atoms,
                         pattern=pattern)
    B = out[3]
    if B.shape != np.asarray(m["B"]).shape or not np.allclose(B, m["B"], atol=1e-8):
        raise ValueError(f"{mol_dir.name}: the pattern builder's primitives differ from the loader's B matrix — {what} refused")
    return g, out


def hybrid_tensors(mol_dir: Path, m: dict, pattern: str = "c") -> dict:
    """The hybrid head's inputs for one molecule: pattern pairs (P, 2) and their classes (P,), the (K, N) primitive mean-pooling matrix, the
    internal low-level force constants F_int (K, K), the Wilson B matrix (K, 3N) and the primitives' parities, in the primitive order of the
    loader's B."""
    g, (pairs, feat, pcls, B, atoms) = _checked_pairs(mol_dir, m, pattern, "hybrid head", return_atoms=True)
    podd, psin = primitive_parity(g["symbols"], np.asarray(g["coords_bohr"], float))
    if len(podd) != B.shape[0]:
        raise ValueError(f"{mol_dir.name}: {len(podd)} parities for {B.shape[0]} primitives")
    return dict(podd=torch.as_tensor(podd), psin=torch.as_tensor(psin, dtype=torch.float32), pairs=torch.as_tensor(pairs, dtype=torch.long),
                pcls=torch.as_tensor(pcls, dtype=torch.long), pfeat=torch.as_tensor(feat, dtype=torch.float32),
                prim_pool=primitive_pool_matrix(atoms, len(g["symbols"])), F_int=torch.as_tensor(np.asarray(m["F_low"], float), dtype=torch.float32),
                B=torch.as_tensor(B, dtype=torch.float32))


def pattern_classes(mol_dir: Path, m: dict, pattern: str = "c") -> torch.Tensor:
    """K × K long tensor: the pair model's pattern with its class on every entry of the pattern (both triangles) and −1 elsewhere, in the
    primitive order of `m["B"]`."""
    _g, (pairs, _feat, pcls, B) = _checked_pairs(mol_dir, m, pattern, "pattern term")
    K = B.shape[0]
    cls = torch.full((K, K), -1, dtype=torch.long)
    for (i, j), c in zip(pairs.tolist(), pcls.tolist(), strict=True):
        cls[i, j] = c
        cls[j, i] = c
    return cls


def pattern_class_scales(tensors: dict, ids: list) -> torch.Tensor:
    """One standardisation scale per pair class: the RMS of the true internal ΔF over the pattern entries of that class across `ids` (the fit
    molecules of the seed only — nothing from the inner validation or the hold-outs). A class absent from the fit set keeps scale 1."""
    sq, cnt = torch.zeros(len(PAIR_CLASS_NAMES), dtype=torch.float64), torch.zeros(len(PAIR_CLASS_NAMES), dtype=torch.float64)
    for i in ids:
        t = tensors[i]
        d2 = (t["dF_true"].double() ** 2)
        for c in range(len(PAIR_CLASS_NAMES)):
            mask = t["pat_cls"] == c
            sq[c] += d2[mask].sum()
            cnt[c] += int(mask.sum())
    scale = torch.sqrt(sq / cnt.clamp_min(1))
    scale[cnt == 0] = 1.0
    scale = torch.maximum(scale, PATTERN_SCALE_FLOOR * scale.max())
    return scale.float()


LOW_CM = 700.0   # 'other' modes below this uncorrected ω are their own family in the K-diagonal term's 'family-low' form (chain 34c)


def kring_tensors(masses: np.ndarray, V: np.ndarray, w: np.ndarray, family: list, dH_true: np.ndarray, dtype=torch.float32) -> dict:
    """The read-out map as tensors. K = kscale ⊙ (Cm ΔH Cmᵀ) with Cm = Vᵀ M^-1/2 (M × 3N) is the mode-basis coupling matrix in cm⁻¹ that
    `e7_t2_posthoc.k_of` computes from ΔF (identical up to the B reconstruction); `ring` = the ring-family modes the (a)/(b) read-outs are
    taken on; K_true and the block's mean square for the relative term (1 when the molecule has no ring mode); one code per mode family, and
    a second code array with 'other' split at LOW_CM."""
    mm = np.repeat(np.asarray(masses, float) * PH.AMU2AU, 3)
    om = np.sqrt(np.abs(np.asarray(w, float)))
    Cm = np.asarray(V, float).T / np.sqrt(mm)[None, :]
    kscale = PH.HARTREE2CM / (2 * np.sqrt(np.outer(om, om)))
    ring = np.where(np.asarray(family) == E6.RING)[0]
    K_true = kscale * (Cm @ np.asarray(dH_true, float) @ Cm.T)
    norm = float(np.mean(K_true[np.ix_(ring, ring)] ** 2)) if len(ring) else 1.0
    codes = np.unique(np.asarray(family, dtype=str), return_inverse=True)[1]
    fam_low = [("other-low" if (f == "other" and o * PH.HARTREE2CM < LOW_CM) else ("other-mid" if f == "other" else f))
               for f, o in zip(family, om, strict=True)]
    codes_low = np.unique(np.asarray(fam_low, dtype=str), return_inverse=True)[1]
    return dict(Cm=torch.as_tensor(Cm, dtype=dtype), kscale=torch.as_tensor(kscale, dtype=dtype), ring=torch.as_tensor(ring, dtype=torch.long),
                K_true=torch.as_tensor(K_true, dtype=dtype), K_norm=torch.tensor(max(norm, 1e-30), dtype=dtype),
                fam_code=torch.as_tensor(np.asarray(codes).reshape(-1), dtype=torch.long),
                fam_code_low=torch.as_tensor(np.asarray(codes_low).reshape(-1), dtype=torch.long))


@dataclass(frozen=True, eq=False)
class LossSettings:
    """The auxiliary term of the loss, explicit: `mode` 'all' (registered) = relative MSE over every entry of B⁺ᵀ ΔH B⁺; 'pattern' = MSE over
    the pair model's pattern only, each entry divided by its class scale (`class_scale`, fitted on the fit molecules); 'kring' = the
    ring-mode block of K; 'both' = pattern + kring_weight · kring (+ kdiag_weight · the K-diagonal term in its `kdiag_mode` form)."""

    mode: str = "all"
    kring_weight: float = KRING_WEIGHT
    kdiag_weight: float = 0.0
    kdiag_mode: str = "all"
    class_scale: torch.Tensor | None = None

    def __post_init__(self):
        if self.mode not in ("all", "pattern", "kring", "both"):
            raise ValueError(f"aux mode {self.mode!r}: 'all', 'pattern', 'kring' or 'both'")
        if self.mode in ("pattern", "both") and self.class_scale is None:
            raise ValueError(f"aux mode {self.mode!r} divides by the pattern class scales: class_scale is required")


def _pattern_term(class_scale: torch.Tensor, t: dict, dF_p: torch.Tensor) -> torch.Tensor:
    cls = t["pat_cls"]
    on = cls >= 0
    scale = class_scale[cls.clamp_min(0)]
    return (((dF_p - t["dF_true"]) / scale) ** 2)[on].mean()


def _kring_term(t, pred, main):
    r = t["ring"]
    if r.numel() == 0:
        return main * 0.0
    K = (t["Cm"] @ pred @ t["Cm"].T) * t["kscale"]
    return ((K - t["K_true"])[r][:, r] ** 2).mean() / t["K_norm"]


def _kdiag_term(t, pred, mode: str = "all"):
    """Mean square of the diagonal of K_pred − K_true over all modes, relative to the diagonal's own mean square. 'family' (decision 53): the
    same relative mean square per mode family, averaged over the families the molecule has — the low-K families (CH-oop, other) then weigh
    as much as the C–H stretches, whose K grows with ω and carries the 'all' term; 'family-low' splits 'other' at LOW_CM."""
    K = (t["Cm"] @ pred @ t["Cm"].T) * t["kscale"]
    d_pred, d_true = torch.diagonal(K), torch.diagonal(t["K_true"])
    if mode == "all":
        return ((d_pred - d_true) ** 2).mean() / (d_true ** 2).mean().clamp_min(1e-30)
    if mode not in ("family", "family-low"):
        raise ValueError(f"kdiag mode {mode!r}: 'all', 'family' or 'family-low'")
    code = t["fam_code_low"] if mode == "family-low" else t["fam_code"]
    terms = []
    for c in torch.unique(code):
        on = code == c
        terms.append(((d_pred[on] - d_true[on]) ** 2).mean() / (d_true[on] ** 2).mean().clamp_min(1e-30))
    return torch.stack(terms).mean()


def _terms(model, t: dict, loss: LossSettings):
    """(main, aux, prediction): the registered main term (mass-weighted Cartesian MSE) and the auxiliary term `loss` describes."""
    pred = model(t["Z"], t["pos"], t["H_low"], t)
    main = ((pred - t["dH_true"]) * t["mw"] * LOSS_SCALE).pow(2).mean()
    dF_p = t["Bp"].T @ pred @ t["Bp"]
    if loss.mode == "pattern":
        aux = _pattern_term(loss.class_scale, t, dF_p)
    elif loss.mode == "kring":
        aux = _kring_term(t, pred, main)
    elif loss.mode == "both":
        aux = _pattern_term(loss.class_scale, t, dF_p) + loss.kring_weight * _kring_term(t, pred, main)
        if loss.kdiag_weight:
            aux = aux + loss.kdiag_weight * _kdiag_term(t, pred, loss.kdiag_mode)
    else:
        aux = ((dF_p - t["dF_true"]) ** 2).mean() / t["dF_norm"]        # relative: the raw internal term is ~1e9 in a.u.
    return main, aux, pred


def inner_split(train_ids: list, seed: int, fraction: float) -> tuple[list, list]:
    """(validation ids, fit ids): a deterministic per-seed split of the training ids (seed offset 1000 keeps it independent of the training
    seed's permutation). fraction <= 0 returns ([], train_ids)."""
    if fraction <= 0:
        return [], list(train_ids)
    perm = np.random.default_rng(1000 + seed).permutation(len(train_ids))
    n_val = max(1, round(fraction * len(train_ids)))
    return [train_ids[k] for k in sorted(perm[:n_val])], [train_ids[k] for k in sorted(perm[n_val:])]


def load_pretrained_body(path: str | Path, reinit_head: bool = True, seed: int = 0, aggregation: str = AGGREGATION,
                         target_elements: list[int] | None = None, pretrained_elements: list[int] | None = None) -> DeltaHessianModel:
    """A fresh DeltaHessianModel carrying the body of a `rungC_pretrain.py` checkpoint; the output head re-initialised (the registered C2 recipe)
    unless asked otherwise. The checkpoint's aggregation must equal the requested one (a checkpoint without the key predates 28 Sep 2026 and is
    a sum body): a setting that travels unexamined is the E8 lesson. With `target_elements`, the embedding rows of elements the pretraining
    never saw (QM9: no S, Cl — the cause of the 27 Sep blow-up) are set to the mean of the trained rows; the checkpoint's own element list is
    used, or `pretrained_elements` for a checkpoint from before 28 Sep, and a checkpoint without either is refused. The reset list is kept as
    `model.reset_elements`."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    ck_agg = ck.get("aggregation", "sum")
    if ck_agg != aggregation:
        raise ValueError(f"{path}: checkpoint body uses {ck_agg} aggregation, the run asks for {aggregation} — pretrain again with the requested "
                         "aggregation or pass --aggregation to match")
    model = DeltaHessianModel(aggregation=aggregation)
    load_state_compat(model, ck["body_state"])
    model.reset_elements = []
    if target_elements is not None:
        seen = ck.get("elements") or pretrained_elements
        if not seen:
            raise ValueError(f"{path}: the checkpoint carries no element list (pretraining before 28 Sep 2026) — pass --pretrained-elements, "
                             "e.g. 1,6,7,8,9 for Hessian QM9, so the untrained element embeddings can be reset")
        seen = sorted({int(z) for z in seen})
        unseen = sorted({int(z) for z in target_elements} - set(seen))
        if unseen:
            with torch.no_grad():
                model.emb.weight[unseen] = model.emb.weight[seen].mean(0)
            model.reset_elements = unseen
    if reinit_head:
        torch.manual_seed(seed)
        for layer in model.head:
            if hasattr(layer, "reset_parameters"):
                layer.reset_parameters()
    return model


def attach_pretrained_body(model: HybridDeltaFModel, pretrained: str | Path, seed: int, aggregation: str,
                           target_elements: list[int] | None = None, pretrained_elements: list[int] | None = None) -> list[int]:
    """The body of a `rungC_pretrain.py` checkpoint under the hybrid head, with the checks of `load_pretrained_body`; the checkpoint's
    Cartesian head travels along unused — the hybrid's own head is fresh by construction. Returns the reset element list."""
    pre = load_pretrained_body(pretrained, reinit_head=False, seed=seed, aggregation=aggregation, target_elements=target_elements,
                               pretrained_elements=pretrained_elements)
    load_state_compat(model.body, pre.state_dict())
    return list(pre.reset_elements)


def check_pretrained_transfer(body: torch.nn.Module, tensors: dict, ids: list, limit: float = 1e3) -> float:
    """Body pre-flight (27 Sep 22:4x: a sum-pooled body pretrained on QM9 was finite on 12–18-atom molecules and 1e15–1e18 on 23-atom fused
    rings). Runs the body on every training molecule; raises if any raw output is non-finite or above `limit` (a fresh sum body gives 15–35 on
    the corpus). Returns the worst |output|, run for every body, fresh or pretrained, so the record holds it."""
    worst, worst_id = 0.0, None
    with torch.no_grad():
        for mid in ids:
            t = tensors[mid]
            out = body(t["Z"], t["pos"], t["H_low"])
            m = float(out.abs().max()) if torch.isfinite(out).all() else float("inf")
            if m > worst:
                worst, worst_id = m, mid
    if worst > limit:
        raise RuntimeError(f"pretrained body output {worst:.3g} on {worst_id} exceeds {limit:g} before fine-tuning — the body does not transfer to "
                           "this molecule size/density (pre-flight of 27 Sep; fine-tuning it would diverge)")
    return worst


def inner_val_aux(model, tensors: dict, ids: list, loss: LossSettings) -> float:
    model.eval()
    with torch.no_grad():
        return float(np.mean([float(_terms(model, tensors[i], loss)[1]) for i in ids])) if ids else float("nan")


@dataclass
class Trained:
    """A trained model with what the record needs about it."""

    model: torch.nn.Module
    history: list
    loss: LossSettings
    best_epoch: int | None
    output_scale: float = 1.0
    class_scale: list[float] | None = None


def entry_class_scales(tensors: dict, train_ids: list) -> np.ndarray:
    """RMS ΔH per entry class (own block, bonded pair, non-bonded pair) over the training molecules."""
    sq, cnt = np.zeros(3), np.zeros(3)
    for i in train_ids:
        t = tensors[i]
        c = t["cls"].repeat_interleave(3, 0).repeat_interleave(3, 1).numpy()
        d2 = (t["dH_true"] ** 2).numpy()
        for k in range(3):
            sq[k] += d2[c == k].sum()
            cnt[k] += (c == k).sum()
    return np.sqrt(sq / np.maximum(cnt, 1))


def _training_elements(tensors: dict, train_ids: list) -> list[int]:
    return sorted({int(z) for i in train_ids for z in tensors[i]["Z"].tolist()})


def _hybrid_model(cfg: TrainConfig, tensors: dict, train_ids: list, seed: int, class_scale: torch.Tensor, log) -> HybridDeltaFModel:
    n_pf = int(tensors[train_ids[0]]["pfeat"].shape[1]) if cfg.pair_features else 0
    model = HybridDeltaFModel(aggregation=cfg.aggregation, tensor_input=cfg.tensor_input, sqm_scale=cfg.sqm_scale, class_scale=class_scale,
                              n_pair_features=n_pf, hidden=cfg.hybrid_hidden, n_s=cfg.body_width, n_v=cfg.body_width, n_blocks=cfg.body_blocks,
                              parity_odd=cfg.parity_odd_mixed)
    model.set_input_scales(input_scales(tensors, train_ids))
    if cfg.pretrained:
        reset = attach_pretrained_body(model, cfg.pretrained, seed, cfg.aggregation, _training_elements(tensors, train_ids), cfg.pretrained_elements)
        log(f"  pretrained body {Path(cfg.pretrained).name} under the hybrid head"
            + (f"; element embeddings absent from pretraining reset to the trained mean: Z = {reset}" if reset else ""))
    if cfg.pair_features:
        model.set_pair_feature_stats(*pair_feature_stats(tensors, train_ids))
        log(f"  rung B's {n_pf} pair features added to the hybrid head (standardised on the fit molecules)")
    log(f"  hybrid head: {sum(p.numel() for p in model.parameters()):,} parameters; F_low input scales "
        + ", ".join(f"{x:.3g}" for x in model.flow_scale.tolist()) + ("; SQM α per class on" if cfg.sqm_scale else ""))
    log(f"  {'pretrained' if cfg.pretrained else 'fresh'} {cfg.aggregation} body pre-flight: worst |output| "
        f"{check_pretrained_transfer(model.body, tensors, train_ids):.3g} on the training molecules")
    return model


def _cartesian_body(cfg: TrainConfig, tensors: dict, train_ids: list, seed: int, log) -> DeltaHessianModel:
    if cfg.pretrained:
        body = load_pretrained_body(cfg.pretrained, reinit_head=True, seed=seed, aggregation=cfg.aggregation,
                                    target_elements=_training_elements(tensors, train_ids), pretrained_elements=cfg.pretrained_elements)
        if body.reset_elements:
            log(f"  element embeddings absent from pretraining reset to the trained mean: Z = {body.reset_elements}")
    else:
        body = DeltaHessianModel(n_s=cfg.body_width, n_v=cfg.body_width, n_blocks=cfg.body_blocks, aggregation=cfg.aggregation,
                                 tensor_input=cfg.tensor_input)
    log(f"  {'pretrained' if cfg.pretrained else 'fresh'} {cfg.aggregation} body pre-flight: worst |output| "
        f"{check_pretrained_transfer(body, tensors, train_ids):.3g} on the training molecules")
    return body


@dataclass(frozen=True)
class Fold:
    """The molecules one model trains on (`fit_ids`) and stops on (`val_ids`, may be empty), with their tensors."""

    tensors: dict
    fit_ids: list
    val_ids: list


def _fit(model, loss: LossSettings, cfg: TrainConfig, fold: Fold, seed: int, log) -> tuple[list, int]:
    """AdamW, one molecule per step, gradient norm clipped at 5; with validation ids the best state on their auxiliary term is kept and,
    with patience, restored. Returns (history, best epoch)."""
    tensors, train_ids, val_ids = fold.tensors, fold.fit_ids, fold.val_ids
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    rng = np.random.default_rng(seed)
    hist, t0 = [], time.time()
    best, best_state, best_ep, since = float("inf"), None, 0, 0
    for ep in range(cfg.epochs):
        model.train()
        tot_main = tot_aux = 0.0
        for k in rng.permutation(len(train_ids)):
            t = tensors[train_ids[k]]
            opt.zero_grad()
            main, aux, _pred = _terms(model, t, loss)
            total = aux if cfg.loss == "internal" else main + cfg.aux_weight * aux
            if not torch.isfinite(total):
                raise RuntimeError(f"non-finite loss at epoch {ep + 1}, molecule {train_ids[k]} — aborting instead of training through NaN "
                                   "(a diverged run is an incident, not a result)")
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot_main += float(main.detach())
            tot_aux += float(aux.detach())
        rec = dict(epoch=ep + 1, main=tot_main / len(train_ids), aux=tot_aux / len(train_ids))
        if val_ids:
            rec["val_aux"] = inner_val_aux(model, tensors, val_ids, loss)
            if rec["val_aux"] < best - 1e-9:
                best, best_ep, since = rec["val_aux"], ep + 1, 0
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            else:
                since += 1
        hist.append(rec)
        if (ep + 1) % 10 == 0 or ep == 0 or ep + 1 == cfg.epochs:
            val_txt = f" val {rec['val_aux']:.4g}" if val_ids else ""
            log(f"    seed {seed} epoch {ep + 1}/{cfg.epochs}: loss main {rec['main']:.4g} aux {rec['aux']:.4g}{val_txt} ({time.time() - t0:.0f} s)")
        if cfg.patience and val_ids and since >= cfg.patience:
            log(f"    seed {seed}: early stop at epoch {ep + 1}, best inner val {best:.4g} at epoch {best_ep}")
            break
    if best_state is not None and cfg.patience:
        model.load_state_dict(best_state)
    return hist, best_ep


def train_one(train_ids: list, tensors: dict, seed: int, cfg: TrainConfig, val_ids: list | None = None, log=print) -> Trained:
    """Train one model on `train_ids` with the settings of `cfg`, which must be resolved (its epochs set); `val_ids` = inner validation
    molecules held out of the training ids."""
    if cfg.epochs is None:
        raise ValueError("train_one needs a resolved config (TrainConfig.resolved()): epochs is not set")
    torch.manual_seed(seed)
    pattern_scales = pattern_class_scales(tensors, train_ids) if cfg.head == "hybrid" or cfg.aux in ("pattern", "both") else None
    if cfg.head == "hybrid":
        model = _hybrid_model(cfg, tensors, train_ids, seed, pattern_scales, log)
        body, output_scale, class_scale = model.body, 1.0, None
    else:
        output_scale = float(np.sqrt(np.mean([float((tensors[i]["dH_true"] ** 2).mean()) for i in train_ids])))
        class_scale = entry_class_scales(tensors, train_ids) if cfg.scale == "class" else None
        body = _cartesian_body(cfg, tensors, train_ids, seed, log)
        model = Scaled(body, output_scale, class_scale)
    body.h_emb.weight.requires_grad_(cfg.hinge_feature)                  # the hinge input stays frozen at zero unless asked (chain 36)
    loss = LossSettings(mode=cfg.aux, kring_weight=cfg.kring_weight, kdiag_weight=cfg.kdiag_weight, kdiag_mode=cfg.kdiag_mode,
                        class_scale=pattern_scales.clone() if cfg.aux in ("pattern", "both") else None)   # not the model's buffer itself
    if cfg.aux == "pattern":
        log("  internal term on the pair model's pattern; class scales "
            + ", ".join(f"{n} {s:.3g}" for n, s in zip(PAIR_CLASS_NAMES, loss.class_scale.tolist(), strict=True)))
    hist, best_ep = _fit(model, loss, cfg, Fold(tensors, train_ids, val_ids or []), seed, log)
    return Trained(model=model, history=hist, loss=loss, best_epoch=best_ep if val_ids else None, output_scale=output_scale,
                   class_scale=None if class_scale is None else [float(x) for x in class_scale])


APT_FILES = ("dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz")           # probes/dipole_derivs_cphf.py (1.3e-5 vs FD on water), probes/dipole_derivs_fd.py
PER_MOLECULE_KEYS = ("coupling_ratio", "coupling_rms", "coupling_zero_rms", "corrected_freq_rms", "dH_residual_ratio",
                     "spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms", "intensity_rel_rms_zero_rule",
                     "intensity_rel_rms_matched", "intensity_rel_rms_zero_rule_matched", "n_modes")


def per_molecule_readouts(mols: dict, ids: list, tr: list, dF_of) -> dict:
    """The hold-out read-outs molecule by molecule, so a ratio over ten molecules shows what it is made of, with the spectrum read-outs where
    an APT exists. A molecule without two ring modes has no coupling ratio (NaN from the read-out), which is kept as such."""
    out = {}
    for i in ids:
        r = readouts(mols, [i], tr, dF_of)
        failed = None
        if "apt" in mols.get(i, {}):
            B = mols[i]["B"]
            try:
                r.update(RI.intensity_readout(mols[i]["H_low"], mols[i]["dH_true"], B.T @ dF_of(i) @ B, mols[i]["masses"], mols[i]["apt"]))
            except RI.ModeCountChanged as e:
                failed = str(e)
        out[i] = {k: (None if isinstance(r.get(k), float) and np.isnan(r[k]) else r.get(k)) for k in PER_MOLECULE_KEYS}
        if failed:
            out[i][RI.FAILED] = failed
    return out


def pool_sizes(spec: str, n_pool: int) -> list[int]:
    """The training pool sizes of --sizes: integers, 'all' (the whole pool) or 'half' (half of a pool whose size is known only at the run),
    each capped at the pool, sorted and without repeats."""
    named = {"all": n_pool, "half": n_pool // 2}
    return sorted({min(named[s] if s in named else int(s), n_pool) for s in spec.split(",")})


def size_split(pool: list, n_atoms: dict, test_min_atoms: int = 0, pool_max_atoms: int = 0) -> tuple[list, list]:
    """Size extrapolation (TASKS 35): (training pool, hold-out (s)). Pool molecules with ≥ test_min_atoms atoms become hold-out (s) and never
    train; with pool_max_atoms the pool keeps only molecules of ≤ that many atoms. 0 switches either off. Order is kept."""
    test = [i for i in pool if test_min_atoms and n_atoms[i] >= test_min_atoms]
    held = set(test)
    keep = [i for i in pool if i not in held and (not pool_max_atoms or n_atoms[i] <= pool_max_atoms)]
    if test_min_atoms and not test:
        raise SystemExit(f"--size-test-min-atoms {test_min_atoms}: no pool molecule is that large")
    return keep, test


def selection_split(pool: list, mols: dict, seed: int, fraction: float) -> tuple[list, list]:
    """(pool without the selection set, the selection set): whole scaffold cores (the unit hold-out (b) is split by) in the order of a
    seeded permutation, until at least `fraction` of the pool is drawn. Siblings never sit on both sides, so the set measures what the
    hold-outs measure — a new family — and not a memorised one. The pool keeps its order."""
    cores = sorted({mols[i]["core"] for i in pool})
    order = [cores[k] for k in np.random.default_rng(seed).permutation(len(cores))]
    by_core = {c: [i for i in pool if mols[i]["core"] == c] for c in cores}
    chosen: set = set()
    n = 0
    for c in order:
        if n >= fraction * len(pool):
            break
        chosen.add(c)
        n += len(by_core[c])
    if len(chosen) == len(cores):
        raise SystemExit(f"--selection-split: a fraction of {fraction:g} takes every scaffold core of the pool")
    return [i for i in pool if mols[i]["core"] not in chosen], [i for i in pool if mols[i]["core"] in chosen]


def exclude_pool_ids(pool: list, path: str | None) -> tuple[list, list]:
    """Coverage ablation: drop the ids listed one per line in `path` from the training pool ('#' lines are comments); returns (pool,
    dropped). Refuses an empty intersection (a wrong file would silently run the full pool)."""
    if not path:
        return pool, []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    wanted = {s.strip() for s in lines if s.strip() and not s.startswith("#")}
    dropped = [i for i in pool if i in wanted]
    if not dropped:
        raise SystemExit(f"--exclude-ids-file {path}: none of its {len(wanted)} ids is in the pool")
    return [i for i in pool if i not in wanted], dropped


def record_paths(prefix) -> tuple[Path, Path]:
    """(json, md) for an output prefix, by concatenation — `Path.with_suffix` treats everything after the first dot as the suffix (2 Oct 2026:
    `T3b_l20.01_seed0_…` became `T3b_l20.json`, and the λ 0.01 and 0.1 records overwrote each other)."""
    return Path(f"{prefix}.json"), Path(f"{prefix}.md")


def load_corpus(molecules: str, use_analytic: bool, log=print) -> tuple:
    """The corpus as the trainer sees it: the rung-B loader's entries, E6's splits, the analytic second-route Hessians substituted where both exist
    (`--use-analytic`), molecules with an imaginary mode dropped, and the atomic polar tensors attached where a passed file exists (CPHF route first).
    Returns (mols, test_a, test_b, cores, pool, substituted)."""
    mols = T2.load(molecules, analytic_only_ok=use_analytic)                # analytic-only folders only under --use-analytic (TASKS 49)
    test_a, test_b, cores, pool = E6.splits(mols)
    substituted = []
    if use_analytic:
        import e7_rungB_reread_analytic as RR
        for i, m in mols.items():
            d = Path(molecules) / i
            if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists():
                RR.substitute(m, d)
                substituted.append(i)
        log(f"analytic second-route Hessians substituted for {len(substituted)} molecules")
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    n_apt = 0
    for i, m in mols.items():
        for name in APT_FILES:
            p = Path(molecules) / i / name
            if p.exists():
                z = np.load(p)
                if bool(z["passed"]):
                    m["apt"] = np.asarray(z["apt"], float)
                    m["apt_file"] = name
                    n_apt += 1
                break
    if n_apt:
        log(f"atomic polar tensors found for {n_apt} molecules: intensity read-outs on (lever 5, registered 2 Oct 2026 06:5x)")
    test_a = [i for i in test_a if i in mols]
    test_b = [i for i in test_b if i in mols]
    pool = [i for i in pool if i in mols]
    return mols, test_a, test_b, cores, pool, substituted


def molecule_tensors(i: str, m: dict, mol: dict, mol_dir: Path, cfg, cache_dir: Path,   # noqa: PLR0913  shared with five probes as it is
                     target_residuals: dict | None = None) -> dict:
    """The tensors one molecule contributes to training and read-out: the Cartesian inputs and truth (`m`, as `load_molecule` returns it, or a
    CC-substituted equivalent), B⁺ and the projected internal ΔF, the entry classes, the kring tensors, the pattern classes (and the ls/kfit
    target when asked), the hybrid tensors. `cfg` carries aux, head, pattern, aux_target, ls_lam and zero_hlow (a TrainConfig, or a namespace
    built from a saved model's record); `mol` is the rung-B loader's entry (B, F_low, masses, V, w, family)."""
    t = to_torch(m)
    t["Bp"] = torch.as_tensor(np.linalg.pinv(mol["B"]), dtype=torch.float32)
    t["dF_true"] = t["Bp"].T @ t["dH_true"] @ t["Bp"]
    t["dF_norm"] = (t["dF_true"] ** 2).mean().clamp_min(1e-30)
    t["cls"] = entry_classes(m)
    t["qidx"] = torch.tensor(int(mol.get("qidx", 0)), dtype=torch.long)       # charge state of the row (pool 3)
    t["hidx"] = torch.as_tensor(m["hidx"] if "hidx" in m else hinge_classes(m["symbols"], m["pos"]), dtype=torch.long)
    if cfg.aux in ("kring", "both"):
        t.update(kring_tensors(mol["masses"], mol["V"], mol["w"], mol["family"], m["dH_true"]))
    if cfg.aux in ("pattern", "both") or cfg.head == "hybrid":            # the hybrid's class scales need the pattern classes under any aux term
        t["pat_cls"] = pattern_classes(mol_dir, mol, cfg.pattern)
        if cfg.aux_target in ("ls", "kfit"):
            target = pattern_target(i, m, mol, t, cfg, cache_dir)
            if target_residuals is not None:
                target_residuals[i] = target.residuals(m, mol, cfg.aux_target)
            t["dF_true"] = torch.as_tensor(target.X, dtype=torch.float32)
    if cfg.head == "hybrid":
        t.update(hybrid_tensors(mol_dir, mol, cfg.pattern))
    if cfg.zero_hlow:
        t["H_low"] = torch.zeros_like(t["H_low"])
    return t


@dataclass(frozen=True, eq=False)
class PatternTarget:
    """An ls or kfit target on the pattern (`X`) beside the projected one it replaces, with their size ratio and whether it came from the cache."""

    X: np.ndarray
    projected: np.ndarray
    ratio: float
    cached: bool

    def residuals(self, m: dict, mol: dict, kind: str) -> dict:
        """How much of the true ΔH each target reconstructs, in the mass-weighted Cartesian metric and in the read-out's."""
        system = (m["dH_true"], mol["B"], m["masses"])
        return {"projected": weighted_residual(*system, self.projected), kind: weighted_residual(*system, self.X), "scale_ratio": self.ratio,
                "from_cache": self.cached, "readout_projected": readout_residual(*system, mol["w"], mol["V"], self.projected),
                "readout_target": readout_residual(*system, mol["w"], mol["V"], self.X)}


def pattern_target(i: str, m: dict, mol: dict, t: dict, cfg, cache_dir: Path) -> PatternTarget:
    """The ls or kfit target on the pattern (cached), refused when its entries outgrow the projected target's."""
    mask = (t["pat_cls"] >= 0).numpy()
    X, cached = cached_pattern_target(cache_dir, i, cfg.pattern, m["dH_true"], mol["B"], m["masses"], mask, lam_rel=cfg.ls_lam,
                                      kind=cfg.aux_target, w=mol["w"], V=mol["V"])
    projected = np.where(mask, t["dF_true"].numpy(), 0.0)
    ratio = scale_ratio(X, projected)                                 # the cache refuses to store such a target; a stale file is caught here
    if ratio > SCALE_LIMIT:
        raise RuntimeError(f"{i}: {cfg.aux_target} target entries {ratio:.3g}× the projected target's (cached: {cached}) — the blow-ups of 1 Oct "
                           f"11:4x / 12:2x; delete the cache file or raise --ls-lam (now {cfg.ls_lam:g})")
    return PatternTarget(X=X, projected=projected, ratio=ratio, cached=cached)


def save_hybrid_model(model: HybridDeltaFModel, loss: LossSettings, path: Path, args: dict, n: int, seed: int,   # noqa: PLR0913  the record's fields
                      train_ids: list | None = None) -> None:
    """The trained hybrid model with everything needed to rebuild it — state (buffers included), the loss settings, constructor arguments, the
    run's arguments and provenance (decision 55), and the pool it was trained on (inner validation included), so a later read does not
    re-derive it from a grown corpus."""
    ctor = dict(aggregation=args["aggregation"], tensor_input=bool(args["tensor_input"]), sqm_scale=bool(args["sqm_scale"]),
                n_pair_features=int(model.n_pair_features), hidden=int(model.head[0].out_features), n_s=int(model.body.blocks[0].n_s),
                n_v=int(model.body.n_v), n_blocks=len(model.body.blocks), parity_odd=bool(model.parity_odd))
    torch.save({"state": model.state_dict(), "ctor": ctor, "aux_mode": loss.mode,
                "aux_class_scale": None if loss.class_scale is None else loss.class_scale.clone(),
                "kring_weight": float(loss.kring_weight), "kdiag_weight": float(loss.kdiag_weight), "kdiag_mode": loss.kdiag_mode,
                "pattern": args["pattern"], "aux_target": args["aux_target"], "ls_lam": args["ls_lam"], "head": args["head"],
                "n": n, "seed": seed, "args": args, "provenance": provenance(),
                "train_ids": None if train_ids is None else list(train_ids)}, path)


def load_hybrid_model(path: Path) -> tuple[HybridDeltaFModel, dict]:
    """(model, record) from `save_hybrid_model`; the record carries the settings a later read needs (pattern, aux, aux_target, ls_lam, args),
    and `loss_settings(record)` the loss it was trained with."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    model = HybridDeltaFModel(**ck["ctor"])
    load_state_compat(model, ck["state"])                                      # pre-3-Oct records: charge rows stay zero
    return model, ck


def loss_settings(record: dict) -> LossSettings:
    """The loss a saved model was trained with; records before 3 Oct 2026 carry no kdiag mode (the all-mode term)."""
    return LossSettings(mode=record["aux_mode"], kring_weight=record["kring_weight"], kdiag_weight=record["kdiag_weight"],
                        kdiag_mode=record.get("kdiag_mode", "all"), class_scale=record["aux_class_scale"])


def freeze_for_transfer(model: HybridDeltaFModel) -> list:
    """Only the head's last linear layer and the SQM α stay trainable; the encoder, the pooled-feature layers and the input scales are
    frozen. Returns the trainable parameters."""
    for p in model.parameters():
        p.requires_grad_(False)
    train = list(model.head[-1].parameters()) + ([model.alpha] if model.alpha is not None else [])
    for p in train:
        p.requires_grad_(True)
    return train


def predictor(model: torch.nn.Module, tensors: dict, mols: dict):
    """dF_of(i): the model's Cartesian ΔH projected to the pair model's internal coordinates (B⁺ᵀ ΔH B⁺), as `readouts` expects."""
    cache = {}

    def dF_of(i):
        if i not in cache:
            t = tensors[i]
            model.eval()
            with torch.no_grad():
                dH = model(t["Z"], t["pos"], t["H_low"], t).numpy().astype(float)
            Bp = np.linalg.pinv(mols[i]["B"])
            cache[i] = Bp.T @ dH @ Bp
        return cache[i]
    return dF_of


@dataclass
class Corpus:
    """The molecules one run reads, and how they are split."""

    mols: dict
    pool: list
    tests: dict                     # hold-out name ('a', 'b', 's', and 'c' per size under --split layerB) → ids
    cores: list
    sizes: list[int]
    seeds: list[int]
    n_atoms: dict
    excluded: list = field(default_factory=list)
    substituted: list = field(default_factory=list)


def select_corpus(cfg: TrainConfig, log) -> Corpus:
    """The corpus, its pool and hold-outs under the run's split, ablations and modes (--smoke, --overfit-one)."""
    mols, test_a, test_b, cores, pool, substituted = load_corpus(cfg.molecules, cfg.use_analytic, log)
    nat = {i: len(m["masses"]) for i, m in mols.items()}
    if cfg.split == "e6" and cfg.pool_layers:
        keep = set(cfg.pool_layers.split(","))
        pool = [i for i in pool if mols[i]["layer"] in keep]
    pool, excluded = exclude_pool_ids(pool, cfg.exclude_ids_file)
    pool, test_s = size_split(pool, nat, cfg.size_test_min_atoms, cfg.pool_max_atoms)
    if test_s or cfg.pool_max_atoms:
        log(f"size split: hold-out (s) {len(test_s)} molecules of ≥ {cfg.size_test_min_atoms} atoms; pool {len(pool)}"
            + (f" of ≤ {cfg.pool_max_atoms} atoms" if cfg.pool_max_atoms else ""))
    if excluded:
        log(f"coverage ablation: {len(excluded)} pool molecules excluded ({Path(cfg.exclude_ids_file).name}); pool {len(pool)}")
    if cfg.split == "layerB":
        pool = sorted((i for i, m in mols.items() if m["layer"] == "B"), key=E6.sha)
        test_a = sorted(i for i, m in mols.items() if m["layer"] == "A")
        if not pool:
            raise SystemExit("--split layerB: no admitted layer-B molecules under the molecules directory")
    test_sel: list = []
    if cfg.selection:
        pool, test_sel = selection_split(pool, mols, *cfg.selection)
        log(f"selection set: {len(test_sel)} molecules of {len({mols[i]['core'] for i in test_sel})} scaffold cores (seed, fraction "
            f"{cfg.selection}); pool {len(pool)}")
    sizes, seeds = pool_sizes(cfg.sizes, len(pool)), cfg.seed_list
    if cfg.smoke:
        sizes, seeds = [min(SMOKE_POOL, len(pool))], [0]
        test_a, test_b, test_s = test_a[:SMOKE_HOLDOUT], test_b[:SMOKE_HOLDOUT], test_s[:SMOKE_HOLDOUT]
    if cfg.overfit_one:
        if cfg.overfit_one not in mols:
            raise SystemExit(f"--overfit-one {cfg.overfit_one}: not an admitted molecule of this corpus")
        pool, sizes, test_a, test_b = [cfg.overfit_one], [1], [cfg.overfit_one], [cfg.overfit_one]
    tests = {"a": test_a, "b": test_b} | ({"s": test_s} if test_s else {}) | ({"sel": test_sel} if test_sel else {})
    return Corpus(mols=mols, pool=pool, tests=tests, cores=cores, sizes=sizes, seeds=seeds, n_atoms=nat, excluded=excluded, substituted=substituted)


def distort_blocks(dH: np.ndarray, masses: np.ndarray, V: np.ndarray, w: np.ndarray, family: list,  # noqa: PLR0913  the paper's operands
                   factors: dict[str, tuple[float, float]]) -> np.ndarray:
    """ΔH with each named family's diagonal block in the mode basis rescaled in two parts: X = M^-1/2 ΔH M^-1/2, B = V_fᵀ X V_f over the
    family's (mass-weighted, orthonormal) modes; its mean part A = diag(2ω_k · m), m the mean over the family of the first-order shift
    B_kk / 2ω_k, so that A carries exactly the family's mean shift; B → a·A + b·(B − A), then back. The anchors' CC correction differs from
    the proxy mainly by that mean shift (TASKS 82), so the two parts get their own factors. With a = b the block is scaled whole and ω
    cancels. Blocks between families, the other families and the part outside the vibrational modes are unchanged; the mass unit cancels."""
    sq = np.sqrt(np.repeat(np.asarray(masses, float), 3))
    X = np.asarray(dH, float) / np.outer(sq, sq)
    fam = np.asarray(family)
    two_omega = 2.0 * np.sqrt(np.abs(np.asarray(w, float)))
    out = X.copy()
    for name, (a, b) in factors.items():
        on = fam == name
        if not on.any():
            continue
        Vf = np.asarray(V, float)[:, on]
        B = Vf.T @ X @ Vf
        A = np.diag(two_omega[on] * np.mean(np.diag(B) / two_omega[on]))
        out += Vf @ (a * A + b * (B - A) - B) @ Vf.T
    return out * np.outer(sq, sq)


def distort_families(dH: np.ndarray, masses: np.ndarray, V: np.ndarray, family: list, scales: dict[str, float]) -> np.ndarray:
    """ΔH with each named family's diagonal block in the mode basis multiplied by its factor (proxy check (a)): `distort_blocks` with the
    same factor on both parts, where the frequencies cancel."""
    return distort_blocks(dH, masses, V, np.ones(len(family)), family, {name: (s, s) for name, s in scales.items()})


def build_tensors(cfg: TrainConfig, corpus: Corpus) -> tuple[dict, dict]:
    """(tensors, target residuals) for every molecule the run trains or reads: the largest pool cut, every hold-out, and under --split
    layerB the A2 layer (hold-out (c) is chosen per size from it). Under --family-scale (`distort_families`) or --distortion-file
    (`distort_blocks`, per molecule) the training label is distorted before every target is derived from it."""
    needed = set(corpus.pool[: corpus.sizes[-1]]).union(*corpus.tests.values())
    if cfg.split == "layerB":
        needed |= {i for i, m in corpus.mols.items() if m["layer"] == "A2"}
    distortion = cfg.distortion
    if distortion and (missing := distortion.missing(needed)):
        raise ValueError(f"--distortion-file {cfg.distortion_file}: no context for {len(missing)} molecules the run reads, first {missing[:5]}")
    tensors, target_residuals = {}, {}
    cache_dir = Path(cfg.out_prefix).parent / "ls_targets"
    for i in sorted(needed):
        d = Path(cfg.molecules) / i
        m, mol = load_molecule(d, use_analytic=cfg.use_analytic), corpus.mols[i]
        if cfg.family_scales:
            m = {**m, "dH_true": distort_families(m["dH_true"], mol["masses"], mol["V"], mol["family"], cfg.family_scales)}
        elif distortion:
            m = {**m, "dH_true": distort_blocks(m["dH_true"], mol["masses"], mol["V"], mol["w"], mol["family"], distortion.factors(i))}
        tensors[i] = molecule_tensors(i, m, mol, d, cfg, cache_dir, target_residuals)
    return tensors, target_residuals


def zero_rule(mols: dict, ids: list, tr: list) -> dict:
    return readouts(mols, ids, tr, lambda i: np.zeros_like(mols[i]["F_low"]))


def new_record(cfg: TrainConfig, corpus: Corpus, target_residuals: dict) -> dict:
    """The record's header: every setting, the corpus and its splits, the zero rule on each hold-out; `curve` is filled per size."""
    t = corpus.tests
    return dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), smoke=cfg.smoke, provenance=provenance(),
                model="rungC_equivariant C1 (from scratch; output scaled by the training set's RMS ΔH, or per entry class)",
                excluded_ids=corpus.excluded, exclude_ids_file=cfg.exclude_ids_file, size_test_min_atoms=cfg.size_test_min_atoms,
                pool_max_atoms=cfg.pool_max_atoms, holdout_s=t.get("s", []),
                n_molecules=len(corpus.mols), holdout_a=t["a"], holdout_b=t["b"], scaffold_cores=corpus.cores, pool=len(corpus.pool),
                pool_ids=corpus.pool, pool_layers=cfg.pool_layers, sizes=corpus.sizes, seeds=corpus.seeds, epochs=cfg.epochs, lr=cfg.lr,
                weight_decay=cfg.weight_decay,
                aux_weight=cfg.aux_weight, loss=cfg.loss, scale=cfg.scale, inner_val=cfg.inner_val, patience=cfg.patience,
                pretrained=cfg.pretrained, aggregation=cfg.aggregation, pretrained_elements=cfg.pretrained_elements, aux_mode=cfg.aux,
                zero_hlow=cfg.zero_hlow, overfit_one=cfg.overfit_one, tensor_input=cfg.tensor_input, head=cfg.head, sqm_scale=cfg.sqm_scale,
                pair_features=cfg.pair_features, parity_odd_mixed=cfg.parity_odd_mixed, hybrid_hidden=cfg.hybrid_hidden, pattern=cfg.pattern,
                body_blocks=cfg.body_blocks, body_width=cfg.body_width, aux_target=cfg.aux_target, ls_lam=cfg.ls_lam,
                kring_weight=cfg.kring_weight, kdiag_weight=cfg.kdiag_weight, kdiag_mode=cfg.kdiag_mode, hinge_feature=cfg.hinge_feature,
                target_residuals=target_residuals, pair_class_names=list(PAIR_CLASS_NAMES), substituted_analytic=corpus.substituted,
                curve={}, zero_rule={h: zero_rule(corpus.mols, ids, corpus.pool) for h, ids in t.items() if ids},
                **({"family_scale": cfg.family_scale} if cfg.family_scale else {}),
                **({"distortion_file": cfg.distortion_file} if cfg.distortion_file else {}),
                **({"selection_split": cfg.selection_split, "holdout_sel": t["sel"]} if "sel" in t else {}))


def table_header(cfg: TrainConfig, date: str) -> list[str]:
    recipe = (f"recipe: lr {cfg.lr}, epochs {cfg.epochs}, loss {cfg.loss}, aux weight {cfg.aux_weight}, internal term {cfg.aux}, output scale "
              f"{cfg.scale}, inner validation {cfg.inner_val}, patience {cfg.patience}; pool layers {cfg.pool_layers}; {cfg.aggregation} aggregation")
    if cfg.zero_hlow:
        recipe += "; H_low input zeroed (diagnostic 1)"
    if cfg.overfit_one:
        recipe += f"; overfit-one {cfg.overfit_one} (diagnostic 2)"
    if cfg.tensor_input:
        recipe += "; rank-2 tensor input"
    if cfg.head == "hybrid":
        recipe += f"; hybrid head{' + SQM α' if cfg.sqm_scale else ''}{' + rung B pair features' if cfg.pair_features else ''}"
    if cfg.pattern != "c":
        recipe += f"; pattern {cfg.pattern}"
    if cfg.aux_target in ("ls", "kfit"):
        recipe += f"; {cfg.aux_target} pattern target (λ_rel {cfg.ls_lam:g})"
    return [f"# Rung C (equivariant ΔH, C1 from scratch) — {cfg.out_prefix} ({date}){' — SMOKE, not a result' if cfg.smoke else ''}", "",
            recipe, "",
            "| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |",
            "|---|---|---|---|---|---|---|---|---|---|"]


def holdout_c(corpus: Corpus, tr: list, res: dict, n: int) -> list:
    """--split layerB: hold-out (c) for pool size n = the A2 molecules larger than any training molecule and not in hold-out (b)."""
    nmax = max(corpus.n_atoms[i] for i in tr)
    test_b = set(corpus.tests["b"])
    ids = sorted(i for i, m in corpus.mols.items() if m["layer"] == "A2" and corpus.n_atoms[i] > nmax and i not in test_b)
    res.setdefault("holdout_c", {})[str(n)] = dict(n_atoms_above=nmax, ids=ids)
    if ids:
        res.setdefault("zero_rule_c", {})[str(n)] = zero_rule(corpus.mols, ids, tr)
    return ids


def train_and_read(cfg: TrainConfig, corpus: Corpus, tensors: dict, n: int, seed: int, log) -> tuple[dict, list[str]]:
    """One seed on the first n pool molecules: train, save when asked, read out every hold-out. Returns the record entry and its table rows."""
    t1 = time.time()
    tr = corpus.pool[:n]
    val_ids, fit_ids = inner_split(tr, seed, cfg.inner_val)
    trained = train_one(fit_ids, tensors, seed, cfg, val_ids, log)
    model = trained.model
    dF_of = predictor(model, tensors, corpus.mols)
    if cfg.save_model:
        path = Path(f"{cfg.out_prefix}_model_n{n}_seed{seed}.pt")
        # an optional key only when used, so checkpoints without it keep their settings
        unused = {k for k, v in (("family_scale", cfg.family_scale), ("distortion_file", cfg.distortion_file),
                                 ("selection_split", cfg.selection_split)) if v is None}
        save_hybrid_model(model, trained.loss, path, cfg.model_dump(exclude=unused), n, seed, train_ids=tr)
        log(f"  model saved: {path}")
    out = {"seed": seed, "train_history": trained.history, "output_scale": trained.output_scale, "class_scale": trained.class_scale,
           "aux_class_scale": None if trained.loss.class_scale is None else trained.loss.class_scale.tolist(),
           "seconds": round(time.time() - t1, 1), "inner_val_ids": val_ids,
           "inner_val_aux": inner_val_aux(model, tensors, val_ids, trained.loss) if val_ids else None, "best_epoch": trained.best_epoch}
    if val_ids:
        log(f"  n={n} seed {seed}: inner validation internal term {out['inner_val_aux']:.4g} on {len(val_ids)} molecules (fit on {len(fit_ids)})")
    rows = []
    for h, ids in corpus.tests.items():
        if not ids:
            continue
        r = readouts(corpus.mols, ids, tr, dF_of)
        r["per_molecule"] = per_molecule_readouts(corpus.mols, ids, tr, dF_of)
        r.update(RI.aggregate(r["per_molecule"]))
        if r.get("intensity_failed_n"):
            log(f"  n={n} seed {seed} ({h}): {r['intensity_failed_n']} molecules without an intensity read-out (a mode crossed the threshold)")
        out[h] = r
        rows.append(f"| {n} | {seed} | ({h}) | {r['coupling_rms']:.2f} | {r['coupling_zero_rms']:.2f} | {r['coupling_ratio']:.2f} | "
                    f"{r['corrected_freq_rms']:.2f} | {r['corrected_freq_rms_zero_rule']:.2f} | {r['dH_residual_ratio']:.3f} | {out['seconds']:.0f} |")
        log(f"  n={n} seed {seed} ({h}): ring couplings {r['coupling_rms']:.2f} vs zero {r['coupling_zero_rms']:.2f} "
            f"(ratio {r['coupling_ratio']:.2f}) | corrected ω "
            f"{r['corrected_freq_rms']:.2f} (zero {r['corrected_freq_rms_zero_rule']:.2f}) | ΔH residual ratio {r['dH_residual_ratio']:.3f}")
    return out, rows


def write_record(prefix: str, res: dict, lines: list[str]) -> None:
    """The JSON record and its markdown table, each written to a temporary file and moved over the target."""
    json_path, md_path = record_paths(prefix)
    for path, text in ((json_path, json.dumps(res, indent=1)), (md_path, "\n".join(lines))):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)


def log_line(s: str) -> None:
    print(s, flush=True)


def main(argv: list[str] | None = None) -> int:
    console_utf8_safe()
    cfg = parse_config(argv, __doc__.splitlines()[0]).resolved()
    torch.set_num_threads(cfg.threads)
    t_start = time.time()
    corpus = select_corpus(cfg, log_line)
    tensors, target_residuals = build_tensors(cfg, corpus)
    if cfg.family_scales or cfg.distortion_file:
        log_line(f"training labels distorted ({cfg.family_scale or cfg.distortion_file}); the read-outs compare with the undistorted labels")
    n_params = sum(p.numel() for p in DeltaHessianModel(n_s=cfg.body_width, n_v=cfg.body_width, n_blocks=cfg.body_blocks,
                                                        tensor_input=cfg.tensor_input).parameters())
    t = corpus.tests
    log_line(f"{len(corpus.mols)} molecules; pool {len(corpus.pool)}; hold-out (a) {len(t['a'])}, (b) {len(t['b'])} ({corpus.cores}); "
             f"sizes {corpus.sizes}; seeds {corpus.seeds}; epochs {cfg.epochs}; threads {cfg.threads}; model {n_params:,} parameters, "
             f"{cfg.aggregation} aggregation" + (" — SMOKE" if cfg.smoke else ""))
    res = new_record(cfg, corpus, target_residuals)
    lines = table_header(cfg, res["date"])
    for n in corpus.sizes:
        if cfg.split == "layerB":
            corpus.tests["c"] = holdout_c(corpus, corpus.pool[:n], res, n)
        row = {"n": n, "per_seed": []}
        for seed in corpus.seeds:
            out, rows = train_and_read(cfg, corpus, tensors, n, seed, log_line)
            row["per_seed"].append(out)
            lines += rows
        res["curve"][str(n)] = row
    res["seconds"] = round(time.time() - t_start, 1)
    lines += ["", f"wall {res['seconds']:.0f} s; read-out keys: {sorted(next(iter(res['zero_rule'].values())).keys())}", ""]
    write_record(cfg.out_prefix, res, lines)
    log_line(f"wrote {cfg.out_prefix}.json/.md in {res['seconds']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
