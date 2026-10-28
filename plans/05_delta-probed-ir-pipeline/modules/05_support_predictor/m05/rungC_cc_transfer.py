"""Lever 1 / T3 (2 Oct 2026): does the proxy-trained hybrid model transfer to coupled-cluster level on an anchor it never saw?

Leave-one-anchor-out over the CCSD(T) anchors: the high level of each anchor becomes its CC Hessian (`substitute_cc`, the analytic B3LYP as the
low level), the proxy-trained model (`rungC_train.py --save-model`) is fine-tuned on the other anchors in every enabled mode (from α alone to
the whole head with α) and read out on the held-out one with the registered read-outs (ring-coupling ratio against the zero rule,
corrected ω rms, per-family diagonal rms). A fit on all anchors (`--predict`, the saved fold predictions, the out-of-plane subset fits)
uses `--fit-mode`: by default the whole head (set three's diagnosis, 21 Oct 2026: held-out CH-oop 12.29 → 6.54 cm⁻¹ against the last
layer with the λ = 1 pull, three seeds; the proxy check of 22 Oct agrees); that λ = 1 standard of 7 Oct is the preset `--fit-mode head_l2`.
Beside it: the zero rule, the proxy model as it is (no fine-tune), and a per-class α scaling fitted on the training anchors (the SQM-like
transfer, no network). Every number traces to the anchor files named on the command line.
Pinned by `tests/test_rungC_cc_transfer_regression.py`.

    python m05/rungC_cc_transfer.py corpus/molecules <model.pt> <out_prefix> --anchor A_8448043181=<hessian_ccsd_t.npz> [--anchor ...] \\
        [--epochs 300] [--lr 1e-3] [--held <id> ...] [--oop-diagonal-model --oop-fit-sizes 4,8]

Anchor set three's read (`probes/anchor_set3_read.py`) runs it with --held (only the original anchors are folds) and --oop-fit-sizes.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import os
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor_registry as AR
import e7_rungB_reread_analytic as RR
import e7_t2_posthoc as PH
import e7_t2_sqm as T2
import mode_blocks as MB
import model_registry as MR
import rungC_intensities as RI
from learning_curve_layerA import AMU2AU, HARTREE2CM, normal_modes
from rungC_equivariant import Z_OF, charge_index
from rungC_train import (
    LossSettings,
    _terms,
    freeze_for_transfer,
    load_hybrid_model,
    loss_settings,
    molecule_tensors,
    pattern_class_scales,
    predictor,
    readouts,
    record_paths,
)

LORA_SEED = 0          # the adapter's random start; torch's default generator is seeded from the clock (16 Oct 2026: 14.44 / 14.05 cm⁻¹)
FAMILY_ROWS = ("ring-ip", "CH-stretch", "CH-oop", "other")
KEPT = ("coupling_ratio", "coupling_rms", "coupling_zero_rms", "corrected_freq_rms", "corrected_freq_rms_zero_rule", "dH_residual_ratio",
        "diag_rms")
SUBSETS_PER_SIZE = 5   # anchor set three, amendment of 14 Oct 2026: five random subsets per size below 'all', numpy seed 0,
SUBSET_SEED = 0        # every subset when there are no more than five


def anchor_subsets(pool: list[str], k: int, n: int = SUBSETS_PER_SIZE, seed: int = SUBSET_SEED) -> list[tuple[str, ...]]:
    """The subsets of k anchors a read along the anchor count uses: all of them when there are at most n, else n distinct ones drawn
    with numpy's generator at `seed` — the same draw for the same pool, whatever order the pool is given in."""
    if not 0 < k <= len(pool):
        raise ValueError(f"a subset of {k} from a pool of {len(pool)}")
    every = list(itertools.combinations(sorted(pool), k))
    if len(every) <= n:
        return every
    picked = np.random.default_rng(seed).choice(len(every), size=n, replace=False)
    return [every[i] for i in sorted(picked)]


def _geometry(mol_dir: Path) -> dict:
    return json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))


def low_level_file(mol_dir: Path) -> Path:
    """The low-level Hessian of an anchor or a predicted molecule: the analytic B3LYP where it exists, else the FD one."""
    analytic = mol_dir / "hessian_b3lyp_analytic.npz"
    return analytic if analytic.exists() else mol_dir / "hessian_b3lyp.npz"


def substitute_cc(m: dict, lo_npz: Path, cc_npz: Path) -> dict:
    """Make the CC Hessian the high level of a corpus molecule entry (the counterpart of `e7_rungB_reread_analytic.substitute`): K, F_high,
    dH_true and the derived mode data follow the CC Hessian; the low level is the file given (the analytic B3LYP where it exists)."""
    lo = np.load(lo_npz)["H_projected"]
    hi = np.load(cc_npz)["H_projected"]
    masses = m["masses"]
    w, f, V, _ = normal_modes(lo, masses)
    mm = np.repeat(masses * AMU2AU, 3)
    dH = hi - lo
    Km = V.T @ (dH / np.sqrt(np.outer(mm, mm))) @ V
    om = np.sqrt(np.abs(w))
    K = (Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM).astype(np.float32)
    Fl, _ = T2.to_internal(lo, m["B"])
    Fh, _ = T2.to_internal(hi, m["B"])
    if len(m["family"]) != len(f):
        raise RuntimeError(f"mode count changed ({len(m['family'])} vs {len(f)})")
    m.update(V=V, w=w, freq=f, K=K, target=np.diag(K).astype(np.float32), F_low=Fl, F_high=Fh, H_low=lo, dH_true=dH, high_level="ccsd_t",
             cc_file=str(cc_npz), low_file=Path(lo_npz).name)
    return m


def load_cc_apt(apt_npz: Path, mol_dir: Path, tol: float = 1e-6) -> np.ndarray:
    """A CC atomic polar tensor (3 × 3N, from `cc_dipole_capture` in the E8 run) for the intensity read-out (TASKS 32); refused unless it was
    computed at the corpus geometry the normal modes come from (max coordinate difference ≤ tol bohr)."""
    z = np.load(apt_npz)
    d = float(np.abs(np.asarray(z["coords_bohr"], float) - np.asarray(_geometry(mol_dir)["coords_bohr"], float)).max())
    if d > tol:
        raise SystemExit(f"{apt_npz}: computed {d:.1e} bohr away from {mol_dir.name}'s corpus geometry — not this molecule's APT")
    return np.asarray(z["apt"], float)


def predict_cartesian(model, t: dict) -> np.ndarray:
    """The model's Cartesian ΔH for one molecule's tensors (TASKS 36: the quantity the spot checks compare after adding the low level)."""
    model.eval()
    with torch.no_grad():
        return model(t["Z"], t["pos"], t["H_low"], t).numpy().astype(float)


@dataclass(frozen=True)
class Prediction:
    """One predicted molecule as `--predict` (TASKS 36) and `--save-fold-predictions` (TASKS 45) write it: the Cartesian ΔH, the low level it
    is added to, the fine-tune mode, the anchors the fit saw, the proxy model, and — for a fold — the held-out anchor."""

    dH_pred: np.ndarray
    H_low: np.ndarray
    low_level: str
    mode: str
    anchors: list[str]
    model: str
    final_loss: float | None
    held: str | None = None

    def save(self, path: Path) -> Path:
        np.savez(path, dH_pred=self.dH_pred, H_low=self.H_low, low_level=self.low_level, mode=self.mode, anchors=np.array(self.anchors),
                 model=self.model, final_loss=(np.nan if self.final_loss is None else self.final_loss), held=(self.held or ""))
        return path


FIT_MODES = ("head_all", "head", "head_l2")   # the modes a fit on all anchors may use; the first is the default


def loaded_molecule(mol_dir: Path, m: dict) -> dict:
    """What `rungC_equivariant.load_molecule` returns, built from a (CC-substituted) corpus entry."""
    g = _geometry(mol_dir)
    sym = [s.upper() for s in g["symbols"]]
    return dict(id=mol_dir.name, symbols=sym, Z=np.array([Z_OF[s] for s in sym]), pos=np.asarray(g["coords_bohr"], float),
                masses=np.asarray(g["masses_amu"], float), H_low=m["H_low"], dH_true=m["dH_true"], analytic=True, qidx=charge_index(g))


class LowRankLinear(torch.nn.Module):
    """W x + b with W = W₀ + A Bᵀ, W₀ frozen, A (out × r) zero-initialised and B (in × r) random: the layer starts as W₀ and the tune moves it
    along a rank-r subspace (lever 6, 3 Oct 2026; the LoRA construction of Hu et al. 2021 on a dense layer). B is drawn from its own seeded
    generator, so a run is reproducible and the global generator is untouched."""

    def __init__(self, base: torch.nn.Linear, rank: int, seed: int = LORA_SEED):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad_(False)
        self.A = torch.nn.Parameter(torch.zeros(base.out_features, rank))
        start = torch.Generator().manual_seed(seed)
        self.B = torch.nn.Parameter(torch.randn(base.in_features, rank, generator=start) / rank ** 0.5)

    def forward(self, x):
        return self.base(x) + (x @ self.B) @ self.A.T


def attach_lora(model, rank: int, seed: int = LORA_SEED) -> list:
    """Replace the head's middle linear layer by its low-rank-adapted copy; returns the adapter parameters."""
    idx = [k for k, m in enumerate(model.head) if isinstance(m, torch.nn.Linear)][1]
    lora = LowRankLinear(model.head[idx], rank, seed)
    model.head[idx] = lora
    return [lora.A, lora.B]


@dataclass(frozen=True)
class FinetuneSettings:
    """How a fold's model is fine-tuned: epochs and learning rate, the weight of the auxiliary term, the L2 pull toward the proxy-trained
    last layer (mode 'head_l2'), the adapter rank (mode 'lora') and the patience of an early-stopped fine-tune (`finetune_early_stopped`)."""

    epochs: int
    lr: float
    aux_weight: float
    head_l2: float = 0.0
    lora_rank: int = 0
    patience: int = 0


def _trainable(model, mode: str, settings: FinetuneSettings) -> list:
    params = freeze_for_transfer(model)
    if mode in ("head_all", "head_all_body1"):
        extra = [p for p in model.head.parameters() if not p.requires_grad]
        if mode == "head_all_body1":
            extra += list(model.body.blocks[-1].parameters())
        for p in extra:
            p.requires_grad_(True)
        params = params + extra
    if mode in ("alpha", "lora"):
        for p in model.head[-1].parameters():
            p.requires_grad_(False)
        params = [model.alpha] if model.alpha is not None else []
        if not params:
            raise SystemExit(f"mode '{mode}' needs a model with the SQM α (trained with --sqm-scale)")
        if mode == "lora":
            params = params + attach_lora(model, settings.lora_rank)
    return params


def finetune(model, loss_cfg: LossSettings, train: dict, mode: str, settings: FinetuneSettings, log=print) -> list:
    """Fine-tune on the training anchors (`train`: id → tensors, in step order) with the loss the model was trained with (`loss_cfg`), its
    pattern class scales refitted on the anchors: mode 'head' = head's last layer + α; 'head_l2' = the same with the penalty
    head_l2 · ‖W − W₀‖² toward the proxy-trained last layer (T3b); 'alpha' = α only; 'lora' = α and a rank-r adapter on the head's middle
    layer; 'head_all' = every layer of the head + α; 'head_all_body1' = 'head_all' and the body's last interaction block; 'none' = no
    training. Returns the loss history."""
    if mode == "none":
        return []
    w0, opt, fit_loss = _tuning(model, loss_cfg, train, mode, settings)
    hist = []
    for ep in range(settings.epochs):
        hist.append(_epoch(model, opt, train, fit_loss, settings, w0))
        if (ep + 1) % 50 == 0:
            log(f"    epoch {ep + 1}/{settings.epochs}: loss {hist[-1]:.4g}")
    model.eval()
    return hist


def _tuning(model, loss_cfg: LossSettings, train: dict, mode: str, settings: FinetuneSettings) -> tuple:
    """(the proxy-trained last layer for the pull of 'head_l2', the optimiser, the loss with its pattern class scales refitted on `train`)."""
    w0 = [p.detach().clone() for p in model.head[-1].parameters()] if mode == "head_l2" else []
    params = _trainable(model, mode, settings)
    fit_loss = replace(loss_cfg, class_scale=pattern_class_scales(train, list(train)))
    return w0, torch.optim.Adam(params, lr=settings.lr), fit_loss


def _epoch(model, opt, train: dict, fit_loss: LossSettings, settings: FinetuneSettings, w0: list) -> float:
    """One pass over the training anchors in their order, one optimiser step per molecule; the mean loss of the pass."""
    model.train()
    tot = 0.0
    for t in train.values():
        opt.zero_grad()
        main, aux, _ = _terms(model, t, fit_loss)
        loss = main + settings.aux_weight * aux
        if w0:
            loss = loss + settings.head_l2 * sum(((p - q) ** 2).sum() for p, q in zip(model.head[-1].parameters(), w0, strict=True))
        loss.backward()
        opt.step()
        tot += loss.item()
    return tot / len(train)


def mean_loss(model, tensors: dict, fit_loss: LossSettings, aux_weight: float) -> float:
    """The fit term (main + aux_weight · aux, no pull) averaged over `tensors`, the model in eval mode and without gradients."""
    model.eval()
    losses = []
    with torch.no_grad():
        for t in tensors.values():
            main, aux, _ = _terms(model, t, fit_loss)
            losses.append((main + aux_weight * aux).item())
    return float(np.mean(losses))


@dataclass(frozen=True)
class EarlyStopped:
    """An early-stopped fine-tune (decision 51): the training and validation loss per epoch and the epoch whose weights were kept (1-based)."""

    hist: list
    val_hist: list
    best_epoch: int


def finetune_early_stopped(model, loss_cfg: LossSettings, anchors: tuple[dict, dict], mode: str, settings: FinetuneSettings,
                           log=print) -> EarlyStopped:
    """`finetune` on the fit anchors of `anchors` = (fit, val) with decision 51's stop: after every epoch the loss on the validation
    anchors (with the fit anchors' class scales); training ends settings.patience epochs after the best validation epoch, or at
    settings.epochs, and the best epoch's weights are restored."""
    fit, val = anchors
    patience = settings.patience
    if mode == "none" or not fit or not val or patience < 1:
        raise ValueError(f"an early-stopped fine-tune needs a training mode, fit and validation anchors and patience ≥ 1 (mode {mode!r}, "
                         f"{len(fit)} fit, {len(val)} validation, patience {patience})")
    w0, opt, fit_loss = _tuning(model, loss_cfg, fit, mode, settings)
    hist, val_hist, best, best_ep, best_state = [], [], float("inf"), 0, None
    for ep in range(settings.epochs):
        hist.append(_epoch(model, opt, fit, fit_loss, settings, w0))
        val_hist.append(mean_loss(model, val, fit_loss, settings.aux_weight))
        if val_hist[-1] < best:
            best, best_ep, best_state = val_hist[-1], ep, copy.deepcopy(model.state_dict())
        elif ep - best_ep >= patience:
            break
        if (ep + 1) % 10 == 0:
            log(f"    epoch {ep + 1}/{settings.epochs}: loss {hist[-1]:.4g}, validation {val_hist[-1]:.4g} (best {best:.4g} at {best_ep + 1})")
    model.load_state_dict(best_state)
    model.eval()
    return EarlyStopped(hist, val_hist, best_ep + 1)


def family_freq_rms(m: dict, K_pred: np.ndarray) -> dict:
    """The corrected-ω error (as `e7_t2_sqm.basis_free`: Ω² + 2√(ω_i ω_j) K, K_pred against K_true, modes paired in sorted order) split by
    family — each corrected mode takes the family of the uncorrected mode it overlaps most. T3's line reads the 'ring-ip' entry."""
    wt, Ut = T2.corrected_frequencies(m, m["K"])
    wp, _ = T2.corrected_frequencies(m, K_pred)
    fam = np.array(m["family"])[np.argmax(np.abs(Ut), axis=0)]
    return {f: float(np.sqrt(np.mean((wp - wt)[fam == f] ** 2))) for f in sorted(set(fam))}


def alpha_scaling_baseline(mols: dict, tensors: dict, train_ids: list, held: str) -> np.ndarray:
    """SQM-like transfer without a network: one factor per pair class, least squares of ΔF_cc on F_low over the training anchors' pattern
    entries, applied to the held-out anchor's pattern. Returns the predicted ΔF (K × K) of the held-out anchor."""
    num, den = {}, {}
    for i in train_ids:
        cls = tensors[i]["pat_cls"].numpy()
        dF, F = tensors[i]["dF_true"].numpy(), np.asarray(mols[i]["F_low"], float)
        for c in np.unique(cls[cls >= 0]):
            on = cls == c
            num[c] = num.get(c, 0.0) + float((dF[on] * F[on]).sum())
            den[c] = den.get(c, 0.0) + float((F[on] ** 2).sum())
    alpha = {c: (num[c] / den[c] if den[c] > 0 else 0.0) for c in num}
    cls = tensors[held]["pat_cls"].numpy()
    F = np.asarray(mols[held]["F_low"], float)
    pred = np.zeros_like(F)
    for c, a in alpha.items():
        pred[cls == c] = a * F[cls == c]
    return pred


@dataclass
class Anchors:
    """The anchors of one read: the corpus entries with the CC Hessian as their high level, their tensors, low-level files, CC APTs and
    geometries; `mols` also holds every other corpus molecule (for --predict)."""

    mols: dict
    tensors: dict
    ids: list[str]
    low_files: dict[str, str]
    apts: dict[str, np.ndarray]
    geoms: dict[str, dict]

    def coords(self, i: str) -> np.ndarray:
        return np.asarray(self.geoms[i]["coords_bohr"], float)


def prepare_anchors(mdir: Path, anchors: dict[str, str], apt_args: list[str], cfg, cache_dir: Path) -> Anchors:
    """The corpus with each anchor's CC Hessian substituted (the loader's K and family on the analytic low level first, as the trainer does)."""
    mols = T2.load(mdir)
    tensors, low_files = {}, {}
    for i, cc in anchors.items():
        d = mdir / i
        lo = low_level_file(d)
        low_files[i] = lo.name
        if lo.name.endswith("_analytic.npz") and (d / "hessian_wb97x_analytic.npz").exists():
            RR.substitute(mols[i], d)
        substitute_cc(mols[i], lo, Path(cc))
        tensors[i] = molecule_tensors(i, loaded_molecule(d, mols[i]), mols[i], d, cfg, cache_dir)
    ids = sorted(anchors)
    apts = {i: load_cc_apt(Path(p), mdir / i) for i, p in (s.split("=", 1) for s in apt_args)}
    return Anchors(mols=mols, tensors=tensors, ids=ids, low_files=low_files, apts=apts, geoms={i: _geometry(mdir / i) for i in ids})


def oop_low_predictor(an: Anchors, dF_of):
    """TASKS 51: the arm of R-A's fail branch on a predictor — its couplings between out-of-plane modes from the low level (cached per
    molecule, as `predictor` is)."""
    cache = {}

    def f(i):
        if i not in cache:
            m = an.mols[i]
            cache[i] = MB.oop_couplings_from_low_internal(dF_of(i), m["B"], m["H_low"], m["masses"], an.coords(i))
        return cache[i]
    return f


def oop_shift_coefficients(an: Anchors, train_ids: list[str]) -> np.ndarray:
    """TASKS 51: (a, b, c) of the out-of-plane shift model, fitted on the training anchors' truth only (dH_true = CC minus the low level)."""
    rows = []
    for i in train_ids:
        m = an.mols[i]
        Vo, fo, h = MB.oop_modes(m["H_low"], m["masses"], an.coords(i), an.geoms[i]["symbols"])
        rows.append((fo, h, MB.oop_shifts(m["dH_true"], Vo, fo, m["masses"])))
    return MB.fit_oop_shift(rows)


def oop_model_predictor(an: Anchors, dF_of, coef: np.ndarray):
    """TASKS 51: a predictor with its out-of-plane block replaced by the shift model's (cached per molecule)."""
    cache = {}

    def f(i):
        if i not in cache:
            m = an.mols[i]
            block = lambda dH: MB.oop_block_from_model(dH, m["H_low"], m["masses"], an.coords(i), an.geoms[i]["symbols"], coef)  # noqa: E731
            cache[i] = MB.internal(dF_of(i), m["B"], block)
        return cache[i]
    return f


def oop_subset_reads(an: Anchors, held: str, train_ids: list[str], dF_of, sizes: list[int]) -> dict[str, list[dict]]:
    """Arm M along the anchor count: per size k, the out-of-plane model fitted on each of `anchor_subsets(train_ids, k)` and read on the
    held-out anchor with the network's in-plane block (`dF_of`, the fold's standard mode fine-tuned on every training anchor)."""
    out = {}
    for k in sizes:
        rows = []
        for sub in anchor_subsets(train_ids, k):
            coef = oop_shift_coefficients(an, list(sub))
            rows.append({"train": list(sub), "coef": [float(c) for c in coef],
                         "read": read(an, held, train_ids, oop_model_predictor(an, dF_of, coef))})
        out[str(k)] = rows
    return out


def read(an: Anchors, held: str, train_ids: list[str], dF_of) -> dict:
    """The registered read-outs on the held-out anchor, the corrected ω per family, and the intensities where its CC APT is given (TASKS 32)."""
    m = an.mols[held]
    r = {k: v for k, v in readouts(an.mols, [held], train_ids, dF_of).items() if k in KEPT}
    r["freq_rms_by_family"] = family_freq_rms(m, PH.k_of(m, dF_of(held)))
    if held in an.apts:
        r["intensity"] = RI.intensity_readout(m["H_low"], m["dH_true"], m["B"].T @ dF_of(held) @ m["B"], m["masses"], an.apts[held])
    return r


def scale_last_layer(model, c: float) -> None:
    """The head's last layer (weights and bias) times c, in place: the start of a fold's fine-tune with --init-scale."""
    with torch.no_grad():
        for p in model.head[-1].parameters():
            p.mul_(c)


def enabled_modes(a) -> tuple[str, ...]:
    """The fine-tune modes the switches make available."""
    return ("none", "alpha", "head") + (("head_l2",) if a.head_l2 > 0 else ()) + (("lora",) if a.lora_rank > 0 else ()) + ("head_all",)


def fold_modes(a) -> tuple[str, ...]:
    """The modes a fold runs: every enabled one, or those --modes names."""
    return tuple(m for m in enabled_modes(a) if not a.modes or m in a.modes)


def training_anchors(ids: list[str], held: str, in_sample: bool) -> list[str]:
    """A fold's fine-tune pool: the other anchors, or every anchor with --in-sample (the ceiling: the held-out one is seen)."""
    return list(ids) if in_sample else [i for i in ids if i != held]


def zero(an: Anchors):
    return lambda i: np.zeros_like(an.mols[i]["F_low"])


def run_fold(an: Anchors, held: str, model0, loss_cfg: LossSettings, a) -> dict:
    """One leave-one-anchor-out fold: the zero rule, the α scaling, the out-of-plane model alone when asked, and the network in every
    fine-tune mode (with its out-of-plane variants and the saved prediction of the fit mode when asked)."""
    tr = training_anchors(an.ids, held, a.in_sample)
    fold = {"train": tr, "zero_rule": read(an, held, tr, zero(an)),
            "alpha_scaling": read(an, held, tr, lambda i: alpha_scaling_baseline(an.mols, an.tensors, tr, i))}
    coef = None
    if a.oop_diagonal_model:
        coef = oop_shift_coefficients(an, tr)
        fold["oop_model_coef"] = [float(c) for c in coef]
        fold["oop_model_only"] = read(an, held, tr, oop_model_predictor(an, zero(an), coef))
    settings = FinetuneSettings(a.epochs, a.lr, a.aux_weight, a.head_l2, a.lora_rank)
    for mode in fold_modes(a):
        model = copy.deepcopy(model0)
        if a.init_scale != 1.0:
            scale_last_layer(model, a.init_scale)
        tag = f"[{held} {mode}]"
        hist = finetune(model, loss_cfg, {i: an.tensors[i] for i in tr}, mode, settings, log=lambda s, tag=tag: print(f"  {tag} {s}", flush=True))
        fold[f"network_{mode}"] = {**read(an, held, tr, predictor(model, an.tensors, an.mols)), "final_loss": (hist[-1] if hist else None)}
        if a.oop_couplings_low and mode in ("head", "head_l2"):
            fold[f"network_{mode}_ooplow"] = read(an, held, tr, oop_low_predictor(an, predictor(model, an.tensors, an.mols)))
        if coef is not None and mode in ("head", "head_l2"):
            fold[f"network_{mode}_oopmodel"] = read(an, held, tr, oop_model_predictor(an, predictor(model, an.tensors, an.mols), coef))
        if a.oop_fit_sizes and mode == a.fit_mode:
            fold["oop_fit_subsets"] = oop_subset_reads(an, held, tr, predictor(model, an.tensors, an.mols), a.oop_fit_sizes)
        if a.save_fold_predictions and mode == a.fit_mode:
            pred = Prediction(predict_cartesian(model, an.tensors[held]), an.mols[held]["H_low"], an.mols[held]["low_file"], mode, tr, a.model,
                              hist[-1] if hist else None, held=held)
            fold["saved_prediction"] = str(pred.save(Path(f"{a.out_prefix}_fold_{held}.npz")))
    return fold


def fold_line(held: str, fold: dict, a) -> str:
    """The fold's console line: ring-coupling ratio / ω rms per column, ring-ip ω for the L2 and adapter columns."""
    def pair(col: str) -> str:
        return f"{fold[col]['coupling_ratio']:.2f} / {fold[col]['corrected_freq_rms']:.2f}"

    def ring_ip(col: str) -> str:
        return f"{fold[col]['coupling_ratio']:.2f} / {fold[col]['freq_rms_by_family'].get('ring-ip', float('nan')):.2f} ring-ip"

    line = f"{held}: zero ω {fold['zero_rule']['corrected_freq_rms']:.2f} | α-scaling {pair('alpha_scaling')}"
    for col, label in (("network_none", "network as is"), ("network_alpha", "α tuned"), ("network_head", "head tuned")):
        if col in fold:                                  # --modes leaves some out
            line += f" | {label} {pair(col)}"
    if "network_head_l2" in fold:
        line += f" | head L2 {a.head_l2:g}: {ring_ip('network_head_l2')}"
    if "network_lora" in fold:
        line += f" | lora r{a.lora_rank}: {ring_ip('network_lora')}"
    if "network_head_all" in fold:
        line += f" | whole head: {ring_ip('network_head_all')}"
    return line


def fit_and_predict(an: Anchors, mdir: Path, model0, loss_cfg: LossSettings, cfg, a) -> dict:
    """TASKS 36: fit on all anchors in the fit mode and write the predicted ΔH of every --predict molecule (never an anchor)."""
    clash = sorted(set(a.predict) & set(an.ids))
    if clash:
        raise SystemExit(f"--predict {clash}: anchors are read leave-one-out, not predicted from a fit that saw them")
    model = copy.deepcopy(model0)
    mode = a.fit_mode
    settings = FinetuneSettings(a.epochs, a.lr, a.aux_weight, a.head_l2)
    hist = finetune(model, loss_cfg, {i: an.tensors[i] for i in an.ids}, mode, settings, log=lambda s: print(f"  [fit all {mode}] {s}", flush=True))
    out = {}
    for i in a.predict:
        d = mdir / i
        lo = low_level_file(d)
        if lo.name.endswith("_analytic.npz") and (d / "hessian_wb97x_analytic.npz").exists():
            RR.substitute(an.mols[i], d)
        t = molecule_tensors(i, loaded_molecule(d, an.mols[i]), an.mols[i], d, cfg, Path(a.out_prefix).parent / "ls_targets")
        path = Prediction(predict_cartesian(model, t), np.load(lo)["H_projected"], lo.name, mode, an.ids, a.model,
                          hist[-1] if hist else None).save(Path(f"{a.out_prefix}_predict_{i}.npz"))
        out[i] = dict(file=str(path), low_level=lo.name, mode=mode)
        print(f"predicted {i} ({lo.name}, fit on {len(an.ids)} anchors, {mode}) → {path}", flush=True)
    return out


def table_columns(a) -> list[tuple[str, str]]:
    """(fold key, column header) of the markdown table, in the order of the switches."""
    l2 = f"L2 {a.head_l2:g}"
    cols = [("zero_rule", "zero rule"), ("alpha_scaling", "α scaling (training anchors)"), ("network_none", "network as is"),
            ("network_alpha", "network, α tuned"), ("network_head", "network, head tuned")]
    if a.head_l2 > 0:
        cols.append(("network_head_l2", f"head tuned, {l2}"))
    if a.lora_rank > 0:
        cols.append(("network_lora", f"α + rank-{a.lora_rank} adapter"))
    cols.append(("network_head_all", "network, whole head tuned"))
    if a.oop_couplings_low:
        cols.append(("network_head_ooplow", "head tuned, oop couplings from the low level"))
        if a.head_l2 > 0:
            cols.append(("network_head_l2_ooplow", f"head tuned {l2}, oop couplings from the low level"))
    if a.oop_diagonal_model:
        cols += [("oop_model_only", "low level + oop model"), ("network_head_oopmodel", " head tuned, oop block from the model")]
        if a.head_l2 > 0:
            cols.append(("network_head_l2_oopmodel", f"head tuned {l2}, oop block from the model"))
    return cols


def table_lines(res: dict, a) -> list[str]:
    """The record as a markdown table: per held-out anchor the read-outs of every column."""
    cols = table_columns(a)
    first = next(iter(res["folds"].values()), None)
    if first is not None:
        cols = [c for c in cols if c[0] in first]                  # --modes leaves some modes out
    lines = [f"# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ ({res['date']})", "",
             f"Model `{Path(a.model).name}` ({res['model_record']}); fine-tune {a.epochs} epochs at lr {a.lr:g}, aux weight {a.aux_weight:g}; "
             f"low levels {res['low_level']}.", "",
             "| held-out anchor | read-out | " + " | ".join(h for _, h in cols) + " |",
             "|---|---|" + "---|" * len(cols)]
    keys = [k for k, _ in cols]
    for held, f in res["folds"].items():
        for key, label in (("coupling_ratio", "ring-coupling ratio"), ("corrected_freq_rms", "ω rms, all modes (cm⁻¹)"),
                           ("dH_residual_ratio", "ΔH residual")):
            lines.append(f"| {held} | {label} | " + " | ".join(f"{f[c][key]:.2f}" for c in keys) + " |")
        for fam in FAMILY_ROWS:
            lines.append(f"| {held} | ω rms {fam} (cm⁻¹) | " + " | ".join(f"{f[c]['freq_rms_by_family'].get(fam, float('nan')):.2f}" for c in keys)
                         + " |")
        if "intensity" in f["zero_rule"]:                            # the held-out anchor has a CC APT
            for key, label in (("spectrum_overlap", "spectrum overlap (CC APT)"),
                               ("intensity_rel_rms_matched", "intensity rel. rms, modes matched by eigenvector (CC APT)"),
                               ("intensity_rel_rms", "intensity rel. rms (CC APT)")):
                lines.append(f"| {held} | {label} | " + " | ".join(f"{f[c]['intensity'][key]:.3f}" for c in keys) + " |")
        if "network_head" in f:
            fams = f["network_head"]["diag_rms"]
            lines.append(f"| {held} | per-family diag rms, head tuned | — | — | — | — | " + ", ".join(f"{k} {v:.1f}" for k, v in fams.items()) + " |")
    return [*lines, "", f"{res['seconds']} s."]


def write_record(prefix: str, res: dict, lines: list[str]) -> None:
    """The JSON record and its markdown table, each written to a temporary file and moved over the target."""
    json_path, md_path = record_paths(prefix)
    for path, text in ((json_path, json.dumps(res, indent=1)), (md_path, "\n".join(lines) + "\n")):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)


def _sizes(text: str) -> list[int]:
    """'4,8' → [4, 8]: positive subset sizes, each once, ascending."""
    try:
        sizes = sorted({int(s) for s in text.split(",")})
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"{text!r}: comma-separated whole numbers") from e
    if not sizes or sizes[0] < 1:
        raise argparse.ArgumentTypeError(f"{text!r}: sizes are at least 1")
    return sizes


def check_switches(a, anchors: dict[str, str]) -> None:
    """Switches that do not combine are refused before the corpus or the model is loaded."""
    unknown = sorted(set(a.held) - set(anchors))
    if unknown:
        raise SystemExit(f"--held {unknown}: not among the anchors")
    if a.held and a.skip_folds:
        raise SystemExit("--held names the folds to run; --skip-folds runs none")
    if a.oop_fit_sizes and not a.oop_diagonal_model:
        raise SystemExit("--oop-fit-sizes refits the out-of-plane model of --oop-diagonal-model; give both")
    if a.oop_fit_sizes and a.oop_fit_sizes[-1] >= len(anchors) - 1:
        raise SystemExit(f"--oop-fit-sizes {a.oop_fit_sizes}: a fold trains on {len(anchors) - 1} anchors; every size must be smaller")
    unknown_modes = sorted(set(a.modes) - set(enabled_modes(a)))
    if unknown_modes:
        raise SystemExit(f"--modes {unknown_modes}: not enabled (available: {', '.join(enabled_modes(a))})")
    if a.fit_mode not in enabled_modes(a):
        raise SystemExit(f"--fit-mode {a.fit_mode}: not enabled (mode head_l2 needs --head-l2 > 0)")
    fit_switches = [s for s, on in (("--save-fold-predictions", a.save_fold_predictions), ("--oop-fit-sizes", a.oop_fit_sizes)) if on]
    if fit_switches and a.fit_mode not in fold_modes(a):
        raise SystemExit(f"{' and '.join(fit_switches)} read the fit mode {a.fit_mode}, which --modes leaves out")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("model")
    ap.add_argument("out_prefix")
    ap.add_argument("--anchor", action="append", required=True, help="<corpus id>=<hessian_ccsd_t.npz>")
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--aux-weight", type=float, default=1.0)
    ap.add_argument("--head-l2", type=float, default=0.0, help="T3b: L2 penalty toward the proxy-trained last layer; > 0 adds the column network_head_l2")
    ap.add_argument("--lora-rank", type=int, default=0, help="lever 6: α plus a rank-r adapter on the head's middle layer; > 0 adds the column network_lora")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--predict", action="append", default=[], help="TASKS 36: a corpus id that is not an anchor — fit on all anchors and write "
                    "its predicted ΔH to <out_prefix>_predict_<id>.npz")
    ap.add_argument("--save-fold-predictions", action="store_true", help="TASKS 45: keep each fold's ΔH of the TZ-tier standard mode as "
                    "<out_prefix>_fold_<held>.npz (the Atlas draws it as the network's test series beside the anchor)")
    ap.add_argument("--skip-folds", action="store_true", help="with --predict: no leave-one-anchor-out read, only the fit on all anchors")
    ap.add_argument("--apt", action="append", default=[], help="TASKS 32: <corpus id>=<apt_ccsd_t.npz> — the held-out anchor's intensity "
                    "read-out with its CC APT")
    ap.add_argument("--oop-couplings-low", action="store_true", help="TASKS 51: read each head-tuned fold also with the couplings between "
                    "out-of-plane modes from the low level; adds the columns network_head_ooplow (and network_head_l2_ooplow)")
    ap.add_argument("--oop-diagonal-model", action="store_true", help="TASKS 51, R-A's fail branch: per fold, fit the out-of-plane shift model "
                    "on the training anchors; adds oop_model_only and network_head_oopmodel (and network_head_l2_oopmodel)")
    ap.add_argument("--modes", type=lambda s: [m for m in s.split(",") if m], default=[], help="run only these fine-tune modes "
                    "(comma-separated, among the enabled ones); default every enabled mode")
    ap.add_argument("--in-sample", action="store_true", help="diagnosis: each fold also trains on its held-out anchor (the capacity "
                    "ceiling - not a transfer read)")
    ap.add_argument("--init-scale", type=float, default=1.0, help="diagnosis: multiply the head's last layer by this before each fold's "
                    "fine-tune (0: no proxy knowledge in it; negative: the proxy's direction reversed); the L2 pull goes toward the scaled weights")
    ap.add_argument("--fit-mode", choices=FIT_MODES, default=FIT_MODES[0], help="the mode of a fit on all anchors (--predict, the saved "
                    "fold predictions, the out-of-plane subset fits): the whole head (default), the last layer, or the λ standard of 7 Oct "
                    "(head_l2, with --head-l2)")
    ap.add_argument("--held", action="append", default=[], help="anchor set three's R-A: only these anchors are held out, one fold each; "
                    "the other anchors stay in every fold's fine-tune pool (default: every anchor is a fold)")
    ap.add_argument("--oop-fit-sizes", type=_sizes, default=[], help="with --oop-diagonal-model, arm M along the anchor count: per fold also "
                    "fit the out-of-plane model on subsets of k of the fold's training anchors (comma-separated k, five subsets each, numpy "
                    "seed 0) and read it with the fit mode's in-plane block")
    ap.add_argument("--allow-any-model", action="store_true", help="decision 55: use a model whose registry status is not 'carried' — named "
                    "in the record")
    ap.add_argument("--allow-any-anchor", action="store_true", help="use an anchor file that is not its molecule's carried entry in the anchor "
                    "registry (modules/ANCHORS.md) — named in the record")
    ap.add_argument("--allow-mixed-tiers", action="store_true", help="anchors on several tiers in one read (chain 33 showed why not) — named "
                    "in the record")
    return ap


def main() -> int:
    a = build_parser().parse_args()
    torch.set_num_threads(a.threads)
    t0 = time.time()
    anchors = dict(s.split("=", 1) for s in a.anchor)
    check_switches(a, anchors)
    found = {i: AR.require_carried_anchor(i, Path(p), allow=a.allow_any_anchor) for i, p in anchors.items()}   # the anchor registry
    tier = AR.require_one_tier(found, allow=a.allow_mixed_tiers)
    mdir = Path(a.molecules)
    MR.require_carried(Path(a.model), allow=a.allow_any_model)                    # decision 55: reads run on carried models
    model0, ck = load_hybrid_model(Path(a.model))
    loss_cfg = loss_settings(ck)
    cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"],
                          zero_hlow=False)
    print(f"model {Path(a.model).name}: pattern {cfg.pattern}, aux {cfg.aux}, target {cfg.aux_target}; anchors {sorted(anchors)}", flush=True)
    an = prepare_anchors(mdir, anchors, a.apt, cfg, Path(a.out_prefix).parent / "ls_targets")
    registry = {i: (dict(level=e["level"], tier=e["tier"], sha16=e["sha16"]) if e else "not carried (--allow-any-anchor)") for i, e in found.items()}
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "model": a.model,
           "model_record": {k: ck[k] for k in ("pattern", "aux_mode", "aux_target", "n", "seed")}, "anchors": anchors,
           "anchor_registry": registry, "tier": tier, "low_level": an.low_files, "epochs": a.epochs, "lr": a.lr, "aux_weight": a.aux_weight,
           "head_l2": a.head_l2, "lora_rank": a.lora_rank, "oop_couplings_low": a.oop_couplings_low, "oop_diagonal_model": a.oop_diagonal_model,
           "folds": {}}
    used = (("held", sorted(a.held)), ("oop_fit_sizes", a.oop_fit_sizes), ("modes", a.modes), ("in_sample", a.in_sample),
            ("fit_mode", a.fit_mode), ("init_scale", None if a.init_scale == 1.0 else a.init_scale))
    res.update({k: v for k, v in used if v is not None and v is not False and v != []})   # only when used (0.0 is a value): the pin's record stays
    folds = [] if a.skip_folds else (sorted(a.held) or an.ids)
    for held in folds:
        res["folds"][held] = run_fold(an, held, model0, loss_cfg, a)
        print(fold_line(held, res["folds"][held], a), flush=True)
    if a.predict:
        res["predict"] = fit_and_predict(an, mdir, model0, loss_cfg, cfg, a)
    res["seconds"] = round(time.time() - t0)
    lines = table_lines(res, a)
    write_record(a.out_prefix, res, lines)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
