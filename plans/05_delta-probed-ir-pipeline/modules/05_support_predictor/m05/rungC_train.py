"""Rung C — train the equivariant Δ-Hessian model (`rungC_equivariant.py`) on the pair model's pool and read it out with the pair model's own read-outs
(pre-registration `PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`, R1–R3 and R5 here; R4, the within-orbit spread, holds by construction
and is checked by `tests/test_rungC_equivariance.py`). Built 27 September 2026 as desk work; **nothing is run on the pool before the user's word**
(the Sunday-evening decision; `Decision_Memo_2026-09-27_RungC_Tonight.md`).

Same pool, sizes, seeds and hold-outs as `e7_rungB_pairs.py` (E6 splits, or `--split layerB`), same analytic-Hessian substitution, same read-out
functions (`readouts` of e7: E6 ratios per class, T2's basis-free corrected ω, the Cartesian residual ratio) — the equivariant model's Cartesian ΔH is
projected to the pair model's internal coordinates with the pseudo-inverse of the Wilson B, exactly the auxiliary term of the registered loss.
Fixed recipe (C1, from scratch): AdamW 1e-3, weight decay 1e-4, one molecule per step, `--epochs` passes over the training set (default 60 as the pair
model's fixed recipe), loss = mass-weighted MSE + 0.1 × internal ΔF term; no early stopping, no tuning (the fair-chance search applies to rung C as to
the pair model: a flat result under this one recipe licenses nothing). Output JSON mirrors e7's: zero rule, per size and seed the read-outs on (a) and (b)
(and (c) for the layer-B split), wall time; a markdown table beside it.

    python m05/rungC_train.py corpus/molecules out/E7_rungC_<date> --use-analytic [--sizes 45,100,all] [--seeds 0,1,2] [--epochs 60] [--threads 8]
    python m05/rungC_train.py corpus/molecules out/_smoke --smoke          # 5 molecules, 2 epochs, seed 0: mechanics only"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_posthoc as PH  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import rungC_intensities as RI  # noqa: E402
from e7_rungB_pairs import molecule_pairs, readouts  # noqa: E402
from rungC_equivariant import (  # noqa: E402
    AGGREGATION,
    AGGREGATIONS,
    BOHR2ANG,
    LOSS_SCALE,
    N_BLOCKS,
    N_S,
    DeltaHessianModel,
    console_utf8_safe,
    load_molecule,
    load_state_compat,
    to_torch,
)
from rungC_hybrid import HybridDeltaFModel, input_scales, pair_feature_stats, primitive_pool_matrix  # noqa: E402
from rungC_targets import LAM_REL, SCALE_LIMIT, cached_pattern_ls_target, scale_ratio, weighted_residual  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

AUX_WEIGHT = 0.1


class Scaled(torch.nn.Module):
    """The equivariant model with a fixed output scale: the training set's RMS ΔH (build note of 27 Sep — the pair model scales its targets per class the
    same way; without it the head starts four orders of magnitude above the targets and spends its epochs shrinking). Equivariance is untouched."""

    def __init__(self, model: DeltaHessianModel, scale: float, class_scale=None):
        super().__init__()
        self.model, self.scale = model, float(scale)
        # search stage 1 (27 Sep): one scale per entry class (own block, bonded pair, non-bonded pair)
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
                    "off_dist3")   # e7_rungB_pairs classes 0–8 (6 = pattern d, 7 = e, 8 = f; 1 Oct 2026)
PATTERN_SCALE_FLOOR = 0.1   # 1 Oct 2026: no class scale below this fraction of the largest (the unfloored scales let the Cartesian head fit noise)


def hybrid_tensors(mol_dir: Path, m: dict, pattern: str = "c") -> dict:
    """The hybrid head's inputs for one molecule (30 Sep 2026): pattern pairs (P, 2) and their classes (P,), the (K, N) primitive mean-pooling
    matrix, the internal low-level force constants F_int (K, K) and the Wilson B matrix (K, 3N), all in the primitive order of the loader's B
    (checked, as in pattern_classes)."""
    g = json.load(open(mol_dir / "geometry.json"))
    pairs, feat, pcls, B, atoms = molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"], float), np.asarray(m["F_low"], float), return_atoms=True,
                                                 pattern=pattern)
    if B.shape != np.asarray(m["B"]).shape or not np.allclose(B, m["B"], atol=1e-8):
        raise ValueError(f"{mol_dir.name}: the pattern builder's primitives differ from the loader's B matrix — hybrid head refused")
    return dict(pairs=torch.as_tensor(pairs, dtype=torch.long), pcls=torch.as_tensor(pcls, dtype=torch.long), pfeat=torch.as_tensor(feat, dtype=torch.float32),
                prim_pool=primitive_pool_matrix(atoms, len(g["symbols"])), F_int=torch.as_tensor(np.asarray(m["F_low"], float), dtype=torch.float32),
                B=torch.as_tensor(B, dtype=torch.float32))


def pattern_classes(mol_dir: Path, m: dict, pattern: str = "c") -> torch.Tensor:
    """K × K long tensor: the pair model's pattern with its class (0–5) on every entry of the pattern (both triangles) and −1 elsewhere, in the
    primitive order of `m["B"]`. Built with e7_rungB_pairs.molecule_pairs on the molecule's own geometry; the B matrix it returns must equal the
    loader's (same geomeTRIC construction) — a mismatch is refused, not tolerated (30 Sep 2026, rank-2 change after the external reviews)."""
    g = json.load(open(mol_dir / "geometry.json"))
    pairs, _feat, pcls, B = molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"], float), np.asarray(m["F_low"], float), pattern=pattern)
    if B.shape != np.asarray(m["B"]).shape or not np.allclose(B, m["B"], atol=1e-8):
        raise ValueError(f"{mol_dir.name}: the pattern builder's primitives differ from the loader's B matrix — pattern term refused")
    K = B.shape[0]
    cls = torch.full((K, K), -1, dtype=torch.long)
    for (i, j), c in zip(pairs.tolist(), pcls.tolist(), strict=True):
        cls[i, j] = c
        cls[j, i] = c
    return cls


def pattern_class_scales(tensors: dict, ids: list) -> torch.Tensor:
    """One standardisation scale per pair class: the RMS of the true internal ΔF over the pattern entries of that class across `ids` (the fit molecules
    of the seed only — nothing from the inner validation or the hold-outs). A class absent from the fit set keeps scale 1."""
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
    scale = torch.maximum(scale, PATTERN_SCALE_FLOOR * scale.max())   # 1 Oct 2026 floor (outcome of 00:0x)
    return scale.float()


LOW_CM = 700.0   # chain 34c (4 Oct 2026): 'other' modes below this uncorrected ω are their own family in the K-diagonal term (the low-mode read of 08:2x)


def kring_tensors(masses: np.ndarray, V: np.ndarray, w: np.ndarray, family: list, dH_true: np.ndarray, dtype=torch.float32) -> dict:
    """Lever 3 / H8 (1 Oct 2026): the read-out map as tensors. K = kscale ⊙ (Cm ΔH Cmᵀ) with Cm = Vᵀ M^-1/2 (M × 3N) is the mode-basis coupling
    matrix in cm⁻¹ that `e7_t2_posthoc.k_of` computes from ΔF (identical up to the B reconstruction); `ring` = the ring-family modes the (a)/(b)
    read-outs are taken on; K_true and the block's mean square for the relative term (1 when the molecule has no ring mode)."""
    mm = np.repeat(np.asarray(masses, float) * PH.AMU2AU, 3)
    om = np.sqrt(np.abs(np.asarray(w, float)))
    Cm = np.asarray(V, float).T / np.sqrt(mm)[None, :]
    kscale = PH.HARTREE2CM / (2 * np.sqrt(np.outer(om, om)))
    ring = np.where(np.asarray(family) == E6.RING)[0]
    K_true = kscale * (Cm @ np.asarray(dH_true, float) @ Cm.T)
    norm = float(np.mean(K_true[np.ix_(ring, ring)] ** 2)) if len(ring) else 1.0
    codes = np.unique(np.asarray(family, dtype=str), return_inverse=True)[1]              # chain 34 (3 Oct 2026): one code per family label
    fam_low = [("other-low" if (f == "other" and o * PH.HARTREE2CM < LOW_CM) else ("other-mid" if f == "other" else f)) for f, o in zip(family, om, strict=True)]
    codes_low = np.unique(np.asarray(fam_low, dtype=str), return_inverse=True)[1]        # chain 34c (4 Oct 2026): 'other' split at LOW_CM
    return dict(Cm=torch.as_tensor(Cm, dtype=dtype), kscale=torch.as_tensor(kscale, dtype=dtype), ring=torch.as_tensor(ring, dtype=torch.long),
                K_true=torch.as_tensor(K_true, dtype=dtype), K_norm=torch.tensor(max(norm, 1e-30), dtype=dtype),
                fam_code=torch.as_tensor(np.asarray(codes).reshape(-1), dtype=torch.long),
                fam_code_low=torch.as_tensor(np.asarray(codes_low).reshape(-1), dtype=torch.long))


def _pattern_term(model, t, dF_p):
    cls = t["pat_cls"]
    on = cls >= 0
    scale = model.aux_class_scale[cls.clamp_min(0)]
    return (((dF_p - t["dF_true"]) / scale) ** 2)[on].mean()


def _kring_term(t, pred, main):
    r = t["ring"]
    if r.numel() == 0:
        return main * 0.0
    K = (t["Cm"] @ pred @ t["Cm"].T) * t["kscale"]
    return ((K - t["K_true"])[r][:, r] ** 2).mean() / t["K_norm"]


def _kdiag_term(t, pred, mode: str = "all"):
    """Lever 5 (2 Oct 2026): mean square of the diagonal of K_pred − K_true over all modes, relative to the diagonal's own mean square.
    mode 'family' (chain 34, 3 Oct 2026, decision 53): the same relative mean square per mode family, averaged over the families the molecule has —
    the low-K families (CH-oop, other) then weigh as much as the C–H stretches, whose K grows with ω and carries the 'all' term."""
    K = (t["Cm"] @ pred @ t["Cm"].T) * t["kscale"]
    d_pred, d_true = torch.diagonal(K), torch.diagonal(t["K_true"])
    if mode == "all":
        return ((d_pred - d_true) ** 2).mean() / (d_true ** 2).mean().clamp_min(1e-30)
    if mode not in ("family", "family-low"):
        raise ValueError(f"kdiag mode {mode!r}: 'all', 'family' or 'family-low'")
    code = t["fam_code_low"] if mode == "family-low" else t["fam_code"]        # 'family-low' (chain 34c, 4 Oct 2026): 'other' split at LOW_CM
    terms = []
    for c in torch.unique(code):
        on = code == c
        terms.append(((d_pred[on] - d_true[on]) ** 2).mean() / (d_true[on] ** 2).mean().clamp_min(1e-30))
    return torch.stack(terms).mean()


def _terms(model, t):
    """Registered main term (mass-weighted Cartesian MSE) and the auxiliary term, with the per-molecule scale tensor when the model has one.
    Auxiliary term: 'all' (registered) = relative MSE over every entry of B⁺ᵀ ΔH B⁺; 'pattern' (30 Sep 2026) = MSE over the pair model's pattern only,
    each entry divided by its class scale (`model.aux_class_scale`, fitted on the fit molecules); 'kring' (1 Oct) = the ring-mode block of K;
    'both' (1 Oct, lever 3b) = pattern + kring, equal weights."""
    pred = model(t["Z"], t["pos"], t["H_low"], t)
    main = ((pred - t["dH_true"]) * t["mw"] * LOSS_SCALE).pow(2).mean()
    dF_p = t["Bp"].T @ pred @ t["Bp"]
    mode = getattr(model, "aux_mode", "all")
    if mode == "pattern":
        aux = _pattern_term(model, t, dF_p)
    elif mode == "kring":
        aux = _kring_term(t, pred, main)
    elif mode == "both":
        aux = _pattern_term(model, t, dF_p) + getattr(model, "kring_weight", 1.0) * _kring_term(t, pred, main)
        kd = getattr(model, "kdiag_weight", 0.0)
        if kd:
            aux = aux + kd * _kdiag_term(t, pred, getattr(model, "kdiag_mode", "all"))
    else:
        aux = ((dF_p - t["dF_true"]) ** 2).mean() / t["dF_norm"]        # relative internal-ΔF term (build note of 27 Sep: the raw term is ~1e9 in a.u.)
    return main, aux, pred


def inner_split(train_ids: list, seed: int, fraction: float) -> tuple[list, list]:
    """(validation ids, fit ids): a deterministic per-seed split of the training ids for the search's stage read-out (seed offset 1000 keeps it
    independent of the training seed's permutation). fraction <= 0 returns ([], train_ids)."""
    if fraction <= 0:
        return [], list(train_ids)
    perm = np.random.default_rng(1000 + seed).permutation(len(train_ids))
    n_val = max(1, int(round(fraction * len(train_ids))))
    return [train_ids[k] for k in sorted(perm[:n_val])], [train_ids[k] for k in sorted(perm[n_val:])]


def load_pretrained_body(path: str | Path, reinit_head: bool = True, seed: int = 0, aggregation: str = AGGREGATION,
                         target_elements: list[int] | None = None, pretrained_elements: list[int] | None = None) -> DeltaHessianModel:
    """A fresh DeltaHessianModel carrying the body of a `rungC_pretrain.py` checkpoint; the output head re-initialised (the registered C2 recipe:
    "the output head re-initialised and the whole network fine-tuned on ΔH") unless asked otherwise. The checkpoint's aggregation must equal the
    requested one (a checkpoint without the key predates 28 Sep 2026 and is a sum body): a setting that travels unexamined is the E8 lesson.
    With `target_elements`, the embedding rows of elements the pretraining never saw (QM9: no S, Cl — the cause of the 27 Sep blow-up, found by
    the design check on 28 Sep) are set to the mean of the trained rows; the checkpoint's own element list is used, or `pretrained_elements` for a
    checkpoint from before 28 Sep, and a checkpoint without either is refused. The reset list is kept as `model.reset_elements`."""
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
    """Lever 2a (1 Oct 2026): the body of a `rungC_pretrain.py` checkpoint under the hybrid head. Same checks as `load_pretrained_body`
    (aggregation must match, unseen element rows reset to the trained mean); the checkpoint's Cartesian head travels along unused — the hybrid's
    own head is fresh by construction. Returns the reset element list."""
    pre = load_pretrained_body(pretrained, reinit_head=False, seed=seed, aggregation=aggregation, target_elements=target_elements,
                               pretrained_elements=pretrained_elements)
    load_state_compat(model.body, pre.state_dict())
    return list(pre.reset_elements)


def check_pretrained_transfer(body: torch.nn.Module, tensors: dict, ids: list, limit: float = 1e3) -> float:
    """Body pre-flight (incident of 27 Sep 22:4x: a sum-pooled body pretrained on QM9 was finite on 12–18-atom molecules and 1e15–1e18 on
    23-atom fused rings). Runs the body on every training molecule; raises if any raw output is non-finite or above `limit` (a fresh sum body
    gives 15–35 on the corpus). Returns the worst |output|; since 28 Sep run for every body, fresh or pretrained, so the record holds it."""
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


def inner_val_aux(model, tensors: dict, ids: list) -> float:
    model.eval()
    with torch.no_grad():
        return float(np.mean([float(_terms(model, tensors[i])[1]) for i in ids])) if ids else float("nan")


def train_one(train_ids: list, tensors: dict, seed: int, epochs: int, lr: float = 1e-3, log=print, aux_weight: float = AUX_WEIGHT,
              loss_mode: str = "registered", scale_mode: str = "rms", val_ids: list | None = None, patience: int = 0,
              pretrained: str | None = None, aggregation: str = AGGREGATION,
              pretrained_elements: list[int] | None = None, aux_mode: str = "all", tensor_input: bool = False, head: str = "cartesian",
              sqm_scale: bool = False, pair_features: bool = False, hybrid_hidden: int = 128, body_blocks: int = N_BLOCKS,
              body_width: int = N_S, kring_weight: float = 1.0, kdiag_weight: float = 0.0, kdiag_mode: str = "all") -> tuple[torch.nn.Module, list]:
    """Defaults = the registered recipe C1 of 19:50 (27 Sep). The other values are the cells of the fair-chance search registered at 20:0x:
    aux_weight 1.0; loss_mode 'internal' (the relative internal-ΔF term alone); scale_mode 'class' (one output scale per entry class: diagonal
    3×3 block, bonded pair, non-bonded pair — the pair model's per-class standardisation); val_ids = inner validation molecules held out of the
    training ids (the stage read-out), patience > 0 = early stopping on their internal term with the best state restored."""
    torch.manual_seed(seed)
    scale = float(np.sqrt(np.mean([float((tensors[i]["dH_true"] ** 2).mean()) for i in train_ids])))
    class_scale = None
    if scale_mode == "class":
        sq, cnt = np.zeros(3), np.zeros(3)
        for i in train_ids:
            t = tensors[i]
            c = t["cls"].repeat_interleave(3, 0).repeat_interleave(3, 1).numpy()
            d2 = (t["dH_true"] ** 2).numpy()
            for k in range(3):
                sq[k] += d2[c == k].sum()
                cnt[k] += (c == k).sum()
        class_scale = np.sqrt(sq / np.maximum(cnt, 1))
    target_elements = sorted({int(z) for i in train_ids for z in tensors[i]["Z"].tolist()})
    if pretrained and tensor_input:
        raise ValueError("--tensor-input is a fresh-body variant (30 Sep 2026); the pretrained bodies carry no weights for it")
    if pretrained and (body_blocks, body_width) != (N_BLOCKS, N_S):
        raise ValueError(f"--body-blocks/--body-width ({body_blocks}, {body_width}) do not fit a pretrained body ({N_BLOCKS}, {N_S})")
    if head == "hybrid":
        if aux_mode not in ("pattern", "kring", "both"):
            raise ValueError("--head hybrid needs --aux pattern, kring or both (its output lives on the pattern; the registered rank-3 run uses the pattern term)")
        n_pf = int(tensors[train_ids[0]]["pfeat"].shape[1]) if pair_features else 0
        model = HybridDeltaFModel(aggregation=aggregation, tensor_input=tensor_input, sqm_scale=sqm_scale,
                                  class_scale=pattern_class_scales(tensors, train_ids), n_pair_features=n_pf, hidden=hybrid_hidden,
                                  n_s=body_width, n_v=body_width, n_blocks=body_blocks)
        model.set_input_scales(input_scales(tensors, train_ids))
        if pretrained:
            reset = attach_pretrained_body(model, pretrained, seed, aggregation, target_elements, pretrained_elements)
            log(f"  pretrained body {Path(pretrained).name} under the hybrid head (lever 2a, 1 Oct 2026)"
                + (f"; element embeddings absent from pretraining reset to the trained mean: Z = {reset}" if reset else ""))
        if pair_features:
            model.set_pair_feature_stats(*pair_feature_stats(tensors, train_ids))
            log(f"  rung B's {n_pf} pair features added to the hybrid head (standardised on the fit molecules)")
        log(f"  hybrid head: {sum(p.numel() for p in model.parameters()):,} parameters; F_low input scales "
            + ", ".join(f"{x:.3g}" for x in model.flow_scale.tolist()) + ("; SQM α per class on" if sqm_scale else ""))
        log(f"  {'pretrained' if pretrained else 'fresh'} {aggregation} body pre-flight: worst |output| "
            f"{check_pretrained_transfer(model.body, tensors, train_ids):.3g} on the training molecules")
        model.scale, model.class_scale_values = 1.0, None
    else:
        body = (load_pretrained_body(pretrained, reinit_head=True, seed=seed, aggregation=aggregation, target_elements=target_elements,
                                     pretrained_elements=pretrained_elements) if pretrained
                else DeltaHessianModel(n_s=body_width, n_v=body_width, n_blocks=body_blocks, aggregation=aggregation, tensor_input=tensor_input))
        if pretrained and body.reset_elements:
            log(f"  element embeddings absent from pretraining reset to the trained mean: Z = {body.reset_elements}")
        log(f"  {'pretrained' if pretrained else 'fresh'} {aggregation} body pre-flight: worst |output| "
            f"{check_pretrained_transfer(body, tensors, train_ids):.3g} on the training molecules")
        model = Scaled(body, scale, class_scale)
    model.aux_mode = aux_mode
    model.kring_weight = float(kring_weight)                            # lever 3b weight search (1 Oct 2026): scales the kring term inside 'both'
    model.kdiag_weight = float(kdiag_weight)                            # lever 5 (2 Oct 2026): the diagonal of K over all modes inside 'both'
    model.kdiag_mode = kdiag_mode                                       # chain 34 (3 Oct 2026): 'all' or 'family' (per-family relative mse, averaged)
    model.aux_class_scale = pattern_class_scales(tensors, train_ids) if aux_mode in ("pattern", "both") else None
    if aux_mode == "pattern":
        log("  internal term on the pair model's pattern; class scales " + ", ".join(f"{n} {s:.3g}" for n, s in zip(PAIR_CLASS_NAMES, model.aux_class_scale.tolist(), strict=True)))
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    rng = np.random.default_rng(seed)
    hist, t0 = [], time.time()
    best, best_state, best_ep, since = float("inf"), None, 0, 0
    for ep in range(epochs):
        model.train()
        tot_main = tot_aux = 0.0
        for k in rng.permutation(len(train_ids)):
            t = tensors[train_ids[k]]
            opt.zero_grad()
            main, aux, _pred = _terms(model, t)
            loss = aux if loss_mode == "internal" else main + aux_weight * aux
            if not torch.isfinite(loss):
                raise RuntimeError(f"non-finite loss at epoch {ep + 1}, molecule {train_ids[k]} — aborting instead of training through NaN "
                                   "(guard of 27 Sep; a diverged run is an incident, not a result)")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot_main += float(main.detach())
            tot_aux += float(aux.detach())
        rec = dict(epoch=ep + 1, main=tot_main / len(train_ids), aux=tot_aux / len(train_ids))
        if val_ids:
            rec["val_aux"] = inner_val_aux(model, tensors, val_ids)
            if rec["val_aux"] < best - 1e-9:
                best, best_ep, since = rec["val_aux"], ep + 1, 0
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            else:
                since += 1
        hist.append(rec)
        if (ep + 1) % 10 == 0 or ep == 0 or ep + 1 == epochs:
            val_txt = f" val {rec['val_aux']:.4g}" if val_ids else ""
            log(f"    seed {seed} epoch {ep + 1}/{epochs}: loss main {rec['main']:.4g} aux {rec['aux']:.4g}{val_txt} ({time.time() - t0:.0f} s)")
        if patience and val_ids and since >= patience:
            log(f"    seed {seed}: early stop at epoch {ep + 1}, best inner val {best:.4g} at epoch {best_ep}")
            break
    if best_state is not None and patience:
        model.load_state_dict(best_state)
    model.best_epoch = best_ep if val_ids else None
    model.class_scale_values = None if class_scale is None else [float(x) for x in class_scale]
    return model, hist


APT_FILES = ("dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz")           # probes/dipole_derivs_cphf.py (2 Oct 2026; 1.3e-5 vs FD on water), probes/dipole_derivs_fd.py
PER_MOLECULE_KEYS = ("coupling_ratio", "coupling_rms", "coupling_zero_rms", "corrected_freq_rms", "dH_residual_ratio",
                     "spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms", "intensity_rel_rms_zero_rule", "n_modes")


def per_molecule_readouts(mols: dict, ids: list, tr: list, dF_of) -> dict:
    """H7 (1 Oct 2026): the hold-out read-outs molecule by molecule, so a ratio over ten molecules shows what it is made of. A molecule without
    two ring modes has no coupling ratio (NaN from the read-out), which is kept as such."""
    out = {}
    for i in ids:
        r = readouts(mols, [i], tr, dF_of)
        if "apt" in mols.get(i, {}):                                       # lever 5 step 2 (2 Oct 2026): the spectrum read-outs where an APT exists
            B = mols[i]["B"]
            r.update(RI.intensity_readout(mols[i]["H_low"], mols[i]["dH_true"], B.T @ dF_of(i) @ B, mols[i]["masses"], mols[i]["apt"]))
        out[i] = {k: (None if isinstance(r.get(k), float) and np.isnan(r[k]) else r.get(k)) for k in PER_MOLECULE_KEYS}
    return out


def exclude_pool_ids(pool: list, path: str | None) -> tuple[list, list]:
    """Coverage ablation (2 Oct 2026): drop the ids listed one per line in `path` from the training pool; returns (pool, dropped). Refuses an empty
    intersection (a wrong file would silently run the full pool)."""
    if not path:
        return pool, []
    wanted = {s.strip() for s in open(path, encoding="utf-8") if s.strip()}
    dropped = [i for i in pool if i in wanted]
    if not dropped:
        raise SystemExit(f"--exclude-ids-file {path}: none of its {len(wanted)} ids is in the pool")
    return [i for i in pool if i not in wanted], dropped


def record_paths(prefix) -> tuple[Path, Path]:
    """(json, md) for an output prefix, by concatenation — `Path.with_suffix` treats everything after the first dot as the suffix (2 Oct 2026 14:4x:
    `T3b_l20.01_seed0_…` became `T3b_l20.json`, and the λ 0.01 and 0.1 records overwrote each other)."""
    return Path(f"{prefix}.json"), Path(f"{prefix}.md")


def load_corpus(molecules: str, use_analytic: bool, log=print) -> tuple:
    """The corpus as the trainer sees it: the rung-B loader's entries, E6's splits, the analytic second-route Hessians substituted where both exist
    (`--use-analytic`), molecules with an imaginary mode dropped, and the atomic polar tensors attached where a passed file exists (CPHF route first).
    Returns (mols, test_a, test_b, cores, pool, substituted). Factored out of main on 2 Oct 2026 for probes/rungC_eval_saved.py."""
    mols = T2.load(molecules)
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
    for i, m in mols.items():                                              # lever 5 step 2: atomic polar tensors where present (CPHF route first, FD second)
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


def molecule_tensors(i: str, m: dict, mol: dict, mol_dir: Path, cfg, cache_dir: Path, target_residuals: dict | None = None) -> dict:
    """The tensors one molecule contributes to training and read-out: the Cartesian inputs and truth (`m`, as `load_molecule` returns it, or a CC-substituted
    equivalent), B⁺ and the projected internal ΔF, the entry classes, the kring tensors, the pattern classes (and the LS target when asked), the hybrid
    tensors. `cfg` carries aux, head, pattern, aux_target, ls_lam, zero_hlow (the trainer's namespace or a SimpleNamespace); `mol` is the rung-B loader's
    entry (B, F_low, masses, V, w, family). Factored out of main on 2 Oct 2026 so that the CC-transfer script builds anchors with the same code."""
    t = to_torch(m)
    t["Bp"] = torch.as_tensor(np.linalg.pinv(mol["B"]), dtype=torch.float32)
    t["dF_true"] = t["Bp"].T @ t["dH_true"] @ t["Bp"]
    t["dF_norm"] = (t["dF_true"] ** 2).mean().clamp_min(1e-30)
    t["cls"] = entry_classes(m)
    t["qidx"] = torch.tensor(int(mol.get("qidx", 0)), dtype=torch.long)       # pool 3 (3 Oct 2026): charge state of the row
    if cfg.aux in ("kring", "both"):
        t.update(kring_tensors(mol["masses"], mol["V"], mol["w"], mol["family"], m["dH_true"]))
    if cfg.aux in ("pattern", "both") or cfg.head == "hybrid":            # the hybrid's class scales need the pattern classes under any aux term
        t["pat_cls"] = pattern_classes(mol_dir, mol, cfg.pattern)
        if cfg.aux_target == "ls":                                          # lever 4 (1 Oct 2026): the pattern-consistent target
            mask = (t["pat_cls"] >= 0).numpy()
            X, cached = cached_pattern_ls_target(cache_dir, i, cfg.pattern, m["dH_true"], mol["B"], m["masses"], mask, lam_rel=cfg.ls_lam)
            projected = np.where(mask, t["dF_true"].numpy(), 0.0)
            ratio = scale_ratio(X, projected)                                 # the cache refuses to store such a target; a stale file is caught here
            if ratio > SCALE_LIMIT:
                raise RuntimeError(f"{i}: LS target entries {ratio:.3g}× the projected target's (cached: {cached}) — the blow-ups of 1 Oct 11:4x / "
                                   f"12:2x; delete the cache file or raise --ls-lam (now {cfg.ls_lam:g})")
            if target_residuals is not None:
                target_residuals[i] = {"projected": weighted_residual(m["dH_true"], mol["B"], m["masses"], projected),
                                       "ls": weighted_residual(m["dH_true"], mol["B"], m["masses"], X), "scale_ratio": ratio, "from_cache": cached}
            t["dF_true"] = torch.as_tensor(X, dtype=torch.float32)
    if cfg.head == "hybrid":
        t.update(hybrid_tensors(mol_dir, mol, cfg.pattern))
    if getattr(cfg, "zero_hlow", False):
        t["H_low"] = torch.zeros_like(t["H_low"])
    return t


HYBRID_CTOR_KEYS = ("aggregation", "tensor_input", "sqm_scale", "n_pair_features", "hidden", "n_s", "n_v", "n_blocks")


def save_hybrid_model(model: HybridDeltaFModel, path: Path, args: dict, n: int, seed: int) -> None:
    """Lever 1 / T3 (2 Oct 2026): the trained hybrid model with everything needed to rebuild it — state (buffers included), aux settings, constructor arguments."""
    ctor = dict(aggregation=args["aggregation"], tensor_input=bool(args["tensor_input"]), sqm_scale=bool(args["sqm_scale"]),
                n_pair_features=int(model.n_pair_features), hidden=int(model.head[0].out_features), n_s=int(model.body.blocks[0].n_s),
                n_v=int(model.body.n_v), n_blocks=len(model.body.blocks))
    torch.save({"state": model.state_dict(), "ctor": ctor, "aux_mode": model.aux_mode,
                "aux_class_scale": None if model.aux_class_scale is None else model.aux_class_scale.clone(),
                "kring_weight": float(getattr(model, "kring_weight", 1.0)), "kdiag_weight": float(getattr(model, "kdiag_weight", 0.0)),
                "kdiag_mode": getattr(model, "kdiag_mode", "all"),
                "pattern": args["pattern"], "aux_target": args["aux_target"], "ls_lam": args["ls_lam"], "head": args["head"],
                "n": n, "seed": seed, "args": args, "provenance": provenance()}, path)   # decision 55: commit + command in the model file


def load_hybrid_model(path: Path) -> tuple[HybridDeltaFModel, dict]:
    """(model, record) from `save_hybrid_model`; the record carries the settings the transfer script needs (pattern, aux, aux_target, ls_lam, args)."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    model = HybridDeltaFModel(**ck["ctor"])
    load_state_compat(model, ck["state"])                                      # pre-3-Oct records: charge rows stay zero
    model.aux_mode = ck["aux_mode"]
    model.aux_class_scale = ck["aux_class_scale"]
    model.kring_weight, model.kdiag_weight = ck["kring_weight"], ck["kdiag_weight"]
    model.kdiag_mode = ck.get("kdiag_mode", "all")                      # records before 3 Oct 2026 carry no mode: the all-mode term
    model.scale, model.class_scale_values = 1.0, None
    return model, ck


def freeze_for_transfer(model: HybridDeltaFModel) -> list:
    """Lever 1 / T3: only the head's last linear layer and the SQM α stay trainable; the encoder, the pooled-feature layers and the input scales are frozen.
    Returns the trainable parameters."""
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


def main() -> int:
    console_utf8_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--sizes", default="45,100,175", help="the pair model's registered sizes; 'all' = the whole pool")
    ap.add_argument("--pool-layers", default="A,A2",
                    help="split e6: keep only these layers in the pool (the registered floor's pool was layer A + A2; layer B entered the corpus later)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--epochs", type=int, default=None, help="default 60 (2 under --smoke unless given)")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--split", default="e6", help="e6 (default) or layerB, as in e7_rungB_pairs.py")
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="5 pool molecules, 2 epochs, seed 0, hold-outs cut to 3 each: mechanics only, never a result")
    ap.add_argument("--aux-weight", type=float, default=AUX_WEIGHT,
                    help="search stage 1 (27 Sep 20:0x): weight of the internal term beside the Cartesian one (registered 0.1)")
    ap.add_argument("--loss", default="registered", choices=["registered", "internal"],
                    help="search stage 1: 'internal' = the relative internal-ΔF term alone")
    ap.add_argument("--scale", default="rms", choices=["rms", "class"],
                    help="search stage 1: output scale = training RMS ΔH (registered) or one per entry class")
    ap.add_argument("--inner-val", type=float, default=0.0,
                    help="search: fraction of the training ids held out per seed as inner validation (the stage read-out)")
    ap.add_argument("--patience", type=int, default=0, help="search stage 2: early stopping on the inner validation term, best state restored (0 = off)")
    ap.add_argument("--kring-weight", type=float, default=1.0, help="lever 3b (1 Oct 2026): weight of the kring term inside --aux both (the pattern term keeps weight 1)")
    ap.add_argument("--kdiag-mode", default="all", choices=["all", "family", "family-low"], help="chain 34c (4 Oct 2026): 'family-low' = as 'family' with the 'other' modes below 700 cm⁻¹ as their own family; chain 34 (3 Oct 2026, decision 53): 'family' = the K-diagonal term as the mean "
                    "over mode families of the per-family relative mse, so that CH-oop and other weigh as much as the C–H stretches; 'all' = one relative mse over all modes")
    ap.add_argument("--kdiag-weight", type=float, default=0.0, help="lever 5 (2 Oct 2026): weight of a term on the diagonal of K over all modes inside --aux both (0 = off)")
    ap.add_argument("--save-model", action="store_true", help="lever 1 / T3 (2 Oct 2026): save the trained hybrid model per size and seed next to the record")
    ap.add_argument("--exclude-ids-file", default=None, help="coverage ablation (2 Oct 2026): ids (one per line) dropped from the training pool; hold-outs untouched")
    ap.add_argument("--aux", default="all", choices=["all", "pattern", "kring", "both"],
                    help="internal term: 'all' (registered) or 'pattern' (30 Sep 2026, rank 2 of the external reviews: the pair model's pattern only, one "
                         "standardisation scale per pair class from the fit molecules)")
    ap.add_argument("--zero-hlow", action="store_true", help="diagnostic 1 (30 Sep 2026): zero the B3LYP Hessian input channels; the ratio must collapse towards the zero rule")
    ap.add_argument("--tensor-input", action="store_true", help="rank 1 (30 Sep 2026, external reviews): the B3LYP 3×3 pair blocks as rank-2 equivariant edge features (fresh body only)")
    ap.add_argument("--head", default="cartesian", choices=["cartesian", "hybrid"],
                    help="rank 3 (30 Sep 2026): 'hybrid' = equivariant encoder → ΔF on the pair model's pattern (with F_low,pq/pp/qq as inputs) → ΔH = Bᵀ ΔF B; needs --aux pattern")
    ap.add_argument("--sqm-scale", action="store_true", help="hybrid head: add α_class · F_low,pq to the residual (one α per pair class, initialised at 0)")
    ap.add_argument("--pair-features", action="store_true", help="hybrid head (1 Oct 2026): rung B's 66 pair features beside the encoder's features — does the learned environment add anything to hand-made topology?")
    ap.add_argument("--hybrid-hidden", type=int, default=128, help="hybrid head: width of its MLP (search stage H1, 1 Oct 2026; 128 = the 00:4x model)")
    ap.add_argument("--pattern", default="c", choices=["c", "d", "e", "f"], help="lever 1 (1 Oct 2026): 'c' = the registered pattern; 'd' = (c) + disjoint pairs one bond apart (off_twobond); "
                    "'e' / 'f' = up to two / three bonds apart (off_dist2 / off_dist3)")
    ap.add_argument("--aux-target", default="projected", choices=["projected", "ls"],
                    help="lever 4 (1 Oct 2026): target of the pattern term — 'projected' = B⁺ᵀ ΔH B⁺ on the pattern (registered), 'ls' = the mass-weighted "
                         "least-squares ΔF supported on the pattern (rungC_targets), whose reconstruction is the head's true ceiling")
    ap.add_argument("--ls-lam", type=float, default=LAM_REL, help="lever 4: ridge of the LS target toward the projected truth, relative to the normal matrix's "
                    "mean diagonal (0 = plain least squares — explodes on redundant internals, 1 Oct 11:4x)")
    ap.add_argument("--body-blocks", type=int, default=N_BLOCKS, help="lever 2c (1 Oct 2026): interaction blocks of a fresh body (registered: 3)")
    ap.add_argument("--body-width", type=int, default=N_S, help="lever 2c (1 Oct 2026): scalar and vector channels of a fresh body (registered: 64)")
    ap.add_argument("--overfit-one", default=None, metavar="ID",
                    help="diagnostic 2 (30 Sep 2026): pool, size and both hold-outs = this one molecule; no inner validation, no early stopping; must reach ratio << 0.1")
    ap.add_argument("--pretrained", default=None, help="C2: a `rungC_pretrain.py` checkpoint; its body is loaded, the head re-initialised per seed")
    ap.add_argument("--aggregation", default=AGGREGATION, choices=list(AGGREGATIONS),
                    help="neighbour-message pooling in the body: mean (default since 28 Sep) or sum (the body registered on 25 Sep)")
    ap.add_argument("--pretrained-elements", default=None,
                    help="comma list of atomic numbers a pre-28-Sep checkpoint was trained on (Hessian QM9: 1,6,7,8,9); newer checkpoints carry it")
    a = ap.parse_args()
    a.pretrained_elements = [int(z) for z in a.pretrained_elements.split(",")] if a.pretrained_elements else None
    torch.set_num_threads(a.threads)
    t_start = time.time()
    log = lambda s: print(s, flush=True)  # noqa: E731

    mols, test_a, test_b, cores, pool, substituted = load_corpus(a.molecules, a.use_analytic, log)
    nat = {i: len(m["masses"]) for i, m in mols.items()}
    if a.split == "e6" and a.pool_layers:
        keep = set(a.pool_layers.split(","))
        pool = [i for i in pool if mols[i]["layer"] in keep]
    pool, excluded = exclude_pool_ids(pool, a.exclude_ids_file)
    if excluded:
        log(f"coverage ablation: {len(excluded)} pool molecules excluded ({Path(a.exclude_ids_file).name}); pool {len(pool)}")
    if a.split == "layerB":
        pool = sorted((i for i, m in mols.items() if m["layer"] == "B"), key=E6.sha)
        test_a = sorted(i for i, m in mols.items() if m["layer"] == "A")
        assert pool, "no admitted layer-B molecules under the molecules directory"
    sizes = sorted({min(int(s) if s != "all" else len(pool), len(pool)) for s in a.sizes.split(",")})
    seeds = [int(s) for s in a.seeds.split(",")]
    if a.smoke:
        sizes, seeds, a.epochs = [min(5, len(pool))], [0], (a.epochs or 2)
        test_a, test_b = test_a[:3], test_b[:3]
    if a.overfit_one:
        if a.overfit_one not in mols:
            raise SystemExit(f"--overfit-one {a.overfit_one}: not an admitted molecule of this corpus")
        pool, sizes, test_a, test_b = [a.overfit_one], [1], [a.overfit_one], [a.overfit_one]
        a.inner_val, a.patience = 0.0, 0
    a.epochs = a.epochs or 60

    # tensors for the equivariant model (Cartesian; the registered inputs), plus B⁺ for the auxiliary term and the read-out projection
    needed = set(pool[: sizes[-1]]) | set(test_a) | set(test_b)
    if a.split == "layerB":
        needed |= {i for i, m in mols.items() if m["layer"] == "A2"}
    tensors, target_residuals = {}, {}
    for i in sorted(needed):
        m = load_molecule(Path(a.molecules) / i, use_analytic=a.use_analytic)
        tensors[i] = molecule_tensors(i, m, mols[i], Path(a.molecules) / i, a, Path(a.out_prefix).parent / "ls_targets", target_residuals)
    log(f"{len(mols)} molecules; pool {len(pool)}; hold-out (a) {len(test_a)}, (b) {len(test_b)} ({cores}); sizes {sizes}; seeds {seeds}; epochs {a.epochs}; "
        f"threads {a.threads}; model {sum(p.numel() for p in DeltaHessianModel(n_s=a.body_width, n_v=a.body_width, n_blocks=a.body_blocks, tensor_input=a.tensor_input).parameters()):,} "
        f"parameters, {a.aggregation} aggregation"
        + (" — SMOKE" if a.smoke else ""))

    tests = {"a": test_a, "b": test_b}
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), smoke=a.smoke, provenance=provenance(),
               model="rungC_equivariant C1 (from scratch; output scaled by the training set's RMS ΔH, or per entry class)",
               excluded_ids=excluded, exclude_ids_file=a.exclude_ids_file,
               n_molecules=len(mols), holdout_a=test_a, holdout_b=test_b, scaffold_cores=cores, pool=len(pool), pool_ids=pool, pool_layers=a.pool_layers,
               sizes=sizes, seeds=seeds, epochs=a.epochs, lr=a.lr, aux_weight=a.aux_weight, loss=a.loss, scale=a.scale, inner_val=a.inner_val,
               patience=a.patience, pretrained=a.pretrained, aggregation=a.aggregation, pretrained_elements=a.pretrained_elements,
               aux_mode=a.aux, zero_hlow=a.zero_hlow, overfit_one=a.overfit_one, tensor_input=a.tensor_input, head=a.head, sqm_scale=a.sqm_scale,
               pair_features=a.pair_features, hybrid_hidden=a.hybrid_hidden, pattern=a.pattern, body_blocks=a.body_blocks, body_width=a.body_width,
               aux_target=a.aux_target, ls_lam=a.ls_lam, kring_weight=a.kring_weight, kdiag_weight=a.kdiag_weight, kdiag_mode=a.kdiag_mode, target_residuals=target_residuals,
               pair_class_names=list(PAIR_CLASS_NAMES),
               substituted_analytic=substituted, curve={})
    res["zero_rule"] = {h: readouts(mols, ids, pool, lambda i: np.zeros_like(mols[i]["F_low"])) for h, ids in tests.items() if ids}
    lines = [f"# Rung C (equivariant ΔH, C1 from scratch) — {a.out_prefix} ({res['date']}){' — SMOKE, not a result' if a.smoke else ''}", "",
             f"recipe: lr {a.lr}, epochs {a.epochs}, loss {a.loss}, aux weight {a.aux_weight}, internal term {a.aux}, output scale {a.scale}, "
             f"inner validation {a.inner_val}, patience {a.patience}; pool layers {a.pool_layers}; {a.aggregation} aggregation"
             + ("; H_low input zeroed (diagnostic 1)" if a.zero_hlow else "") + (f"; overfit-one {a.overfit_one} (diagnostic 2)" if a.overfit_one else "")
             + ("; rank-2 tensor input" if a.tensor_input else "") + (f"; hybrid head{' + SQM α' if a.sqm_scale else ''}{' + rung B pair features' if a.pair_features else ''}" if a.head == "hybrid" else "")
             + (f"; pattern {a.pattern}" if a.pattern != "c" else "") + (f"; LS pattern target (λ_rel {a.ls_lam:g})" if a.aux_target == "ls" else ""), "",
             "| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for n in sizes:
        tr = pool[:n]
        if a.split == "layerB":
            nmax = max(nat[i] for i in tr)
            tests["c"] = sorted(i for i, m in mols.items() if m["layer"] == "A2" and nat[i] > nmax and i not in set(test_b))
            res.setdefault("holdout_c", {})[str(n)] = dict(n_atoms_above=nmax, ids=tests["c"])
            if tests["c"]:
                res.setdefault("zero_rule_c", {})[str(n)] = readouts(mols, tests["c"], tr, lambda i: np.zeros_like(mols[i]["F_low"]))
        row = {"n": n, "per_seed": []}
        for seed in seeds:
            t1 = time.time()
            val_ids, fit_ids = inner_split(tr, seed, a.inner_val)
            model, hist = train_one(fit_ids, tensors, seed, a.epochs, a.lr, log, a.aux_weight, a.loss, a.scale, val_ids, a.patience, a.pretrained,
                                    a.aggregation, a.pretrained_elements, aux_mode=a.aux, tensor_input=a.tensor_input, head=a.head, sqm_scale=a.sqm_scale,
                                    pair_features=a.pair_features, hybrid_hidden=a.hybrid_hidden, body_blocks=a.body_blocks, body_width=a.body_width,
                                    kring_weight=a.kring_weight, kdiag_weight=a.kdiag_weight, kdiag_mode=a.kdiag_mode)
            dF_of = predictor(model, tensors, mols)
            if a.save_model:
                if a.head != "hybrid":
                    raise SystemExit("--save-model is written for the hybrid head (the model the CC transfer uses)")
                save_hybrid_model(model, Path(f"{a.out_prefix}_model_n{n}_seed{seed}.pt"), vars(a), n, seed)
                log(f"  model saved: {a.out_prefix}_model_n{n}_seed{seed}.pt")
            out = {"seed": seed, "train_history": hist, "output_scale": model.scale, "class_scale": model.class_scale_values,
                   "aux_class_scale": (None if model.aux_class_scale is None else model.aux_class_scale.tolist()),
                   "seconds": round(time.time() - t1, 1), "inner_val_ids": val_ids,
                   "inner_val_aux": (inner_val_aux(model, tensors, val_ids) if val_ids else None), "best_epoch": model.best_epoch}
            if val_ids:
                log(f"  n={n} seed {seed}: inner validation internal term {out['inner_val_aux']:.4g} on {len(val_ids)} molecules (fit on {len(fit_ids)})")
            for h, ids in tests.items():
                if not ids:
                    continue
                r = readouts(mols, ids, tr, dF_of)
                r["per_molecule"] = per_molecule_readouts(mols, ids, tr, dF_of)
                r.update(RI.aggregate(r["per_molecule"]))
                out[h] = r
                z = res["zero_rule"][h] if h in res["zero_rule"] else res["zero_rule_c"][str(n)]
                lines.append(f"| {n} | {seed} | ({h}) | {r['coupling_rms']:.2f} | {r['coupling_zero_rms']:.2f} | {r['coupling_ratio']:.2f} | "
                             f"{r['corrected_freq_rms']:.2f} | "
                             f"{r['corrected_freq_rms_zero_rule']:.2f} | {r['dH_residual_ratio']:.3f} | {out['seconds']:.0f} |")
                log(f"  n={n} seed {seed} ({h}): ring couplings {r['coupling_rms']:.2f} vs zero {r['coupling_zero_rms']:.2f} "
                    f"(ratio {r['coupling_ratio']:.2f}) | corrected ω "
                    f"{r['corrected_freq_rms']:.2f} (zero {r['corrected_freq_rms_zero_rule']:.2f}) | ΔH residual ratio {r['dH_residual_ratio']:.3f}")
                del z
            row["per_seed"].append(out)
        res["curve"][str(n)] = row
    res["seconds"] = round(time.time() - t_start, 1)
    lines += ["", f"wall {res['seconds']:.0f} s; read-out keys: {sorted(k for k in next(iter(res['zero_rule'].values())).keys())}", ""]
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    log(f"wrote {a.out_prefix}.json/.md in {res['seconds']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
