"""Lever 1 / T3 (2 Oct 2026): does the proxy-trained hybrid model transfer to coupled-cluster level on an anchor it never saw?

Leave-one-anchor-out over the CCSD(T)/cc-pVDZ anchors (benzene, fluorobenzene, pyridine, naphthalene): the high level of each anchor becomes its CC Hessian
(`substitute_cc`, the analytic B3LYP as the low level), the proxy-trained model (`rungC_train.py --save-model`) is fine-tuned on three anchors with only
the head's last layer and the SQM α trainable (`freeze_for_transfer`), and read out on the fourth with the registered read-outs (ring-coupling ratio
against the zero rule, corrected ω rms, per-family diagonal rms). Beside it: the zero rule, the proxy model as it is (no fine-tune), and a per-class α
scaling fitted on the three anchors (the SQM-like transfer, no network). Every number traces to the anchor files named on the command line.

    python m05/rungC_cc_transfer.py corpus/molecules <model.pt> <out_prefix> --anchor A_8448043181=<hessian_ccsd_t.npz> [--anchor ...] [--epochs 300] [--lr 1e-3]
"""
import argparse
import copy
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e7_rungB_reread_analytic as RR  # noqa: E402
import e7_t2_posthoc as PH  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from learning_curve_layerA import AMU2AU, HARTREE2CM, normal_modes  # noqa: E402
from rungC_equivariant import Z_OF  # noqa: E402
from rungC_train import (  # noqa: E402
    _terms,
    freeze_for_transfer,
    load_hybrid_model,
    molecule_tensors,
    pattern_class_scales,
    predictor,
    readouts,
)


def substitute_cc(m: dict, lo_npz: Path, cc_npz: Path) -> dict:
    """Make the CC Hessian the high level of a corpus molecule entry (the counterpart of `e7_rungB_reread_analytic.substitute`): K, F_high, dH_true and the
    derived mode data follow the CC Hessian; the low level is the file given (the analytic B3LYP where it exists)."""
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
    m.update(V=V, w=w, freq=f, K=K, target=np.diag(K).astype(np.float32), F_low=Fl, F_high=Fh, H_low=lo, dH_true=dH, high_level="ccsd_t", cc_file=str(cc_npz))
    return m


def loaded_molecule(mol_dir: Path, m: dict) -> dict:
    """What `rungC_equivariant.load_molecule` returns, built from a (CC-substituted) corpus entry."""
    g = json.load(open(mol_dir / "geometry.json", encoding="utf-8"))
    sym = [s.upper() for s in g["symbols"]]
    return dict(id=mol_dir.name, symbols=sym, Z=np.array([Z_OF[s] for s in sym]), pos=np.asarray(g["coords_bohr"], float),
                masses=np.asarray(g["masses_amu"], float), H_low=m["H_low"], dH_true=m["dH_true"], analytic=True)


def finetune(model, tensors: dict, train_ids: list, epochs: int, lr: float, mode: str, aux_weight: float, log=print, head_l2: float = 0.0) -> list:
    """Fine-tune on the training anchors: mode 'head' = head's last layer + α; 'head_l2' = the same with the penalty head_l2 · ‖W − W₀‖² toward the
    proxy-trained last layer (T3b, 14:2x); 'alpha' = α only; 'none' = no training. Returns the loss history."""
    if mode == "none":
        return []
    params = freeze_for_transfer(model)
    w0 = [p.detach().clone() for p in model.head[-1].parameters()] if mode == "head_l2" else []
    if mode == "alpha":
        for p in model.head[-1].parameters():
            p.requires_grad_(False)
        params = [model.alpha] if model.alpha is not None else []
        if not params:
            raise SystemExit("mode 'alpha' needs a model with the SQM α (trained with --sqm-scale)")
    model.aux_class_scale = pattern_class_scales(tensors, train_ids)
    opt = torch.optim.Adam(params, lr=lr)
    hist = []
    for ep in range(epochs):
        model.train()
        tot = 0.0
        for i in train_ids:
            opt.zero_grad()
            main, aux, _ = _terms(model, tensors[i])
            loss = main + aux_weight * aux
            if w0:
                loss = loss + head_l2 * sum(((p - q) ** 2).sum() for p, q in zip(model.head[-1].parameters(), w0, strict=True))
            loss.backward()
            opt.step()
            tot += loss.item()
        hist.append(tot / len(train_ids))
        if (ep + 1) % 50 == 0:
            log(f"    epoch {ep + 1}/{epochs}: loss {hist[-1]:.4g}")
    model.eval()
    return hist


def family_freq_rms(m: dict, K_pred: np.ndarray) -> dict:
    """The corrected-ω error (as `e7_t2_sqm.basis_free`: Ω² + 2√(ω_i ω_j) K, K_pred against K_true, modes paired in sorted order) split by family — each
    corrected mode takes the family of the uncorrected mode it overlaps most. T3's line reads the 'ring-ip' entry (in-plane ω ≤ 3 cm⁻¹ rms)."""
    wt, Ut = T2.corrected_frequencies(m, m["K"])
    wp, _ = T2.corrected_frequencies(m, K_pred)
    fam = np.array(m["family"])[np.argmax(np.abs(Ut), axis=0)]
    return {f: float(np.sqrt(np.mean((wp - wt)[fam == f] ** 2))) for f in sorted(set(fam))}


def alpha_scaling_baseline(mols: dict, tensors: dict, train_ids: list, held: str) -> np.ndarray:
    """SQM-like transfer without a network: one factor per pair class, least squares of ΔF_cc on F_low over the training anchors' pattern entries,
    applied to the held-out anchor's pattern. Returns the predicted ΔF (K × K) of the held-out anchor."""
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("model")
    ap.add_argument("out_prefix")
    ap.add_argument("--anchor", action="append", required=True, help="<corpus id>=<hessian_ccsd_t.npz>")
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--aux-weight", type=float, default=1.0)
    ap.add_argument("--head-l2", type=float, default=0.0, help="T3b (2 Oct 2026): L2 penalty toward the proxy-trained last layer; > 0 adds the column network_head_l2")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    t0 = time.time()
    anchors = dict(s.split("=", 1) for s in a.anchor)
    mdir = Path(a.molecules)
    mols = T2.load(mdir)
    model0, ck = load_hybrid_model(Path(a.model))
    cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
    print(f"model {Path(a.model).name}: pattern {cfg.pattern}, aux {cfg.aux}, target {cfg.aux_target}; anchors {sorted(anchors)}", flush=True)
    tensors, lows = {}, {}
    for i, cc in anchors.items():
        d = mdir / i
        lo = d / "hessian_b3lyp_analytic.npz" if (d / "hessian_b3lyp_analytic.npz").exists() else d / "hessian_b3lyp.npz"
        lows[i] = lo.name
        if lo.name.endswith("_analytic.npz") and (d / "hessian_wb97x_analytic.npz").exists():
            RR.substitute(mols[i], d)                       # the loader's K and family on the analytic low level first (as the trainer does)
        substitute_cc(mols[i], lo, Path(cc))
        tensors[i] = molecule_tensors(i, loaded_molecule(d, mols[i]), mols[i], d, cfg, Path(a.out_prefix).parent / "ls_targets")
    ids = sorted(anchors)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "model": a.model, "model_record": {k: ck[k] for k in ("pattern", "aux_mode", "aux_target", "n", "seed")},
           "anchors": anchors, "low_level": lows, "epochs": a.epochs, "lr": a.lr, "aux_weight": a.aux_weight, "head_l2": a.head_l2, "folds": {}}
    keep = ("coupling_ratio", "coupling_rms", "coupling_zero_rms", "corrected_freq_rms", "corrected_freq_rms_zero_rule", "dH_residual_ratio", "diag_rms")

    def read(held, tr, dF_of):
        r = {k: v for k, v in readouts(mols, [held], tr, dF_of).items() if k in keep}
        r["freq_rms_by_family"] = family_freq_rms(mols[held], PH.k_of(mols[held], dF_of(held)))
        return r

    for held in ids:
        tr = [i for i in ids if i != held]
        fold = {"train": tr}
        fold["zero_rule"] = read(held, tr, lambda i: np.zeros_like(mols[i]["F_low"]))
        fold["alpha_scaling"] = read(held, tr, lambda i, tr=tr: alpha_scaling_baseline(mols, tensors, tr, i))
        for mode in ("none", "alpha", "head") + (("head_l2",) if a.head_l2 > 0 else ()):
            model = copy.deepcopy(model0)
            tag = f"[{held} {mode}]"
            hist = finetune(model, tensors, tr, a.epochs, a.lr, mode, a.aux_weight, log=lambda s, tag=tag: print(f"  {tag} {s}", flush=True), head_l2=a.head_l2)
            fold[f"network_{mode}"] = {**read(held, tr, predictor(model, tensors, mols)), "final_loss": (hist[-1] if hist else None)}
        res["folds"][held] = fold
        print(f"{held}: zero ω {fold['zero_rule']['corrected_freq_rms']:.2f} | α-scaling {fold['alpha_scaling']['coupling_ratio']:.2f} / {fold['alpha_scaling']['corrected_freq_rms']:.2f} | "
              f"network as is {fold['network_none']['coupling_ratio']:.2f} / {fold['network_none']['corrected_freq_rms']:.2f} | α tuned {fold['network_alpha']['coupling_ratio']:.2f} / "
              f"{fold['network_alpha']['corrected_freq_rms']:.2f} | head tuned {fold['network_head']['coupling_ratio']:.2f} / {fold['network_head']['corrected_freq_rms']:.2f}"
              + (f" | head L2 {a.head_l2:g}: {fold['network_head_l2']['coupling_ratio']:.2f} / {fold['network_head_l2']['freq_rms_by_family'].get('ring-ip', float('nan')):.2f} ring-ip" if a.head_l2 > 0 else ""), flush=True)
    res["seconds"] = round(time.time() - t0)
    out = Path(a.out_prefix)
    json.dump(res, open(out.with_suffix(".json"), "w"), indent=1)
    lines = [f"# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ ({res['date']})", "", f"Model `{Path(a.model).name}` ({res['model_record']}); fine-tune {a.epochs} epochs at lr {a.lr:g}, "
             f"aux weight {a.aux_weight:g}; low levels {lows}.", "",
             "| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned |" + (f" head tuned, L2 {a.head_l2:g} |" if a.head_l2 > 0 else ""),
             "|---|---|---|---|---|---|---|" + ("---|" if a.head_l2 > 0 else "")]
    for held, f in res["folds"].items():
        cols = ("zero_rule", "alpha_scaling", "network_none", "network_alpha", "network_head") + (("network_head_l2",) if a.head_l2 > 0 else ())
        for key, label in (("coupling_ratio", "ring-coupling ratio"), ("corrected_freq_rms", "ω rms, all modes (cm⁻¹)"), ("dH_residual_ratio", "ΔH residual")):
            lines.append(f"| {held} | {label} | " + " | ".join(f"{f[c][key]:.2f}" for c in cols) + " |")
        for fam in ("ring-ip", "CH-stretch", "CH-oop", "other"):
            lines.append(f"| {held} | ω rms {fam} (cm⁻¹) | " + " | ".join(f"{f[c]['freq_rms_by_family'].get(fam, float('nan')):.2f}" for c in cols) + " |")
        fams = f["network_head"]["diag_rms"]
        lines.append(f"| {held} | per-family diag rms, head tuned | — | — | — | — | " + ", ".join(f"{k} {v:.1f}" for k, v in fams.items()) + " |")
    lines += ["", f"{res['seconds']} s."]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
