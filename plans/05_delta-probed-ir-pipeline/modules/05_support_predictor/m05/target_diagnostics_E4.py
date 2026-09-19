"""E4 — is the per-mode proxy target unstable under mode mixing, and is the family-mean shift the transferable quantity?
(19 September 2026; pre-registered as E4 in PreRegistration_2026-09-19_E_Series_Learned_Mode_Embeddings.md)

E4a  per mode: first-order shift (projection of H_high on the low mode) vs matched-eigenvalue shift (ω_high,j − ω_low,i for
     the best-overlap high mode j); per family RMS of the difference, median best overlap, fraction of overlaps < 0.9.
E4b  per molecule and family: the mixing-invariant family-mean shift Tr(P_F ΔH P_F) / (2 Σ ω_i) [cm⁻¹]; ridge on molecule-level
     tokens across held-out molecules (same hash split), against the zero rule and the median over training molecules.
numpy only.  Usage: python target_diagnostics_E4.py <corpus/molecules dir> <out prefix>
"""
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from learning_curve_layerA import AMU2AU, FAMILIES, HARTREE2CM, molecule_features, normal_modes  # noqa: E402
from learning_curve_layerA_v2_descriptors import atom_classes, H_CLASSES  # noqa: E402
from embedding_experiments_E import molecule_level_tokens, ridge_fit_predict  # noqa: E402


def rms(x):
    x = np.asarray(x, float); return float(np.sqrt(np.mean(x ** 2))) if x.size else float("nan")


def analyse(mol_dir):
    base = molecule_features(mol_dir)
    g = json.load(open(mol_dir / "geometry.json")); masses = np.asarray(g["masses_amu"]); symbols = g["symbols"]
    lo = np.load(mol_dir / "hessian_b3lyp.npz"); hi = np.load(mol_dir / "hessian_wb97x.npz")
    w_lo, f_lo, V_lo, _ = normal_modes(lo["H_projected"], masses)
    w_hi, f_hi, V_hi, Hm_hi = normal_modes(hi["H_projected"], masses)
    S = np.abs(V_lo.T @ V_hi)                        # (M, M) overlaps
    j = S.argmax(1); best = S.max(1)
    matched = f_hi[j] - f_lo                         # matched-eigenvalue shift
    first = base["target"]                           # first-order shift
    fam = np.array(base["family"])
    # E4b: family-mean shift, mixing invariant: Tr(P_F ΔH_mw P_F) / (2 Σ ω) with ΔH_mw = H_hi_mw − H_lo_mw, in the low-mode basis
    m = np.repeat(masses * AMU2AU, 3)
    dH = hi["H_projected"] / np.sqrt(np.outer(m, m)) - lo["H_projected"] / np.sqrt(np.outer(m, m))
    fam_mean = {}
    for F in FAMILIES:
        idx = np.where(fam == F)[0]
        if len(idx) == 0:
            fam_mean[F] = None; continue
        P = V_lo[:, idx]
        tr = np.trace(P.T @ dH @ P)
        fam_mean[F] = float(tr / (2 * np.sqrt(np.abs(w_lo[idx])).sum()) * HARTREE2CM)
    cls, n_rings = atom_classes(symbols, g["coords_bohr"])
    hcounts = np.array([cls.count(c) for c in H_CLASSES], float) / 10.0
    mtok = np.concatenate([molecule_level_tokens(mol_dir), hcounts])
    return dict(id=mol_dir.name, fam=fam, first=first, matched=matched, best=best, fam_mean=fam_mean, mtok=mtok,
                first_mean={F: float(first[fam == F].mean()) if (fam == F).any() else None for F in FAMILIES})


def main():
    mdir = Path(sys.argv[1]); prefix = sys.argv[2]
    mols = [analyse(d) for d in sorted(p for p in mdir.iterdir() if (p / "hessian_wb97x.npz").exists())]
    mols.sort(key=lambda r: hashlib.sha1(r["id"].encode()).hexdigest())
    n_test = max(1, math.ceil(0.25 * len(mols))); test, pool = mols[:n_test], mols[n_test:]
    out = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_molecules": len(mols), "n_test": n_test, "E4a": {}, "E4b": {}}
    print("E4a — first-order vs matched-eigenvalue shift, all 45 molecules")
    for F in FAMILIES:
        d = np.concatenate([(r["first"] - r["matched"])[r["fam"] == F] for r in mols])
        b = np.concatenate([r["best"][r["fam"] == F] for r in mols])
        fo = np.concatenate([r["first"][r["fam"] == F] for r in mols]); ma = np.concatenate([r["matched"][r["fam"] == F] for r in mols])
        out["E4a"][F] = dict(n=int(len(d)), rms_diff=rms(d), median_best_overlap=float(np.median(b)), frac_overlap_below_0_9=float((b < 0.9).mean()),
                             rms_first=rms(fo), rms_matched=rms(ma), sd_first=float(fo.std()), sd_matched=float(ma.std()))
        print(f"  {F:11s} n={len(d):4d}  RMS(first − matched) {rms(d):6.2f}  median overlap {np.median(b):.3f}  frac<0.9 {(b < 0.9).mean():.2f}  "
              f"sd first {fo.std():.2f} sd matched {ma.std():.2f}")
    # also: the learning-curve target's spread explained by mixing: correlation of |first − matched| with (1 − best)
    print("E4b — family-mean shift (mixing-invariant) across molecules; ridge on molecule-level tokens; held-out molecules")
    Xtr = np.stack([r["mtok"] for r in pool]); Xte = np.stack([r["mtok"] for r in test])
    for F in FAMILIES:
        ytr = np.array([r["fam_mean"][F] if r["fam_mean"][F] is not None else np.nan for r in pool])
        yte = np.array([r["fam_mean"][F] if r["fam_mean"][F] is not None else np.nan for r in test])
        ok_tr, ok_te = ~np.isnan(ytr), ~np.isnan(yte)
        if ok_tr.sum() < 5 or ok_te.sum() < 2:
            out["E4b"][F] = {"note": "too few molecules with this family"}; continue
        pred, lam = ridge_fit_predict(Xtr[ok_tr], ytr[ok_tr], Xte[ok_te], [r["id"] for r, o in zip(pool, ok_tr) if o])
        med = float(np.median(ytr[ok_tr]))
        # within-molecule spread of per-mode shifts around the family mean (what a per-mode model must additionally explain)
        within = np.concatenate([(r["first"][r["fam"] == F] - r["first"][r["fam"] == F].mean()) for r in mols if (r["fam"] == F).sum() > 1])
        out["E4b"][F] = dict(n_train=int(ok_tr.sum()), n_test=int(ok_te.sum()), rms_ridge=rms(pred - yte[ok_te]), rms_median_rule=rms(yte[ok_te] - med),
                             rms_zero=rms(yte[ok_te]), sd_family_mean_across_molecules=float(np.nanstd(np.array([r["fam_mean"][F] for r in mols], float))),
                             rms_within_molecule_spread=rms(within), lam=lam)
        e = out["E4b"][F]
        print(f"  {F:11s} family-mean across molecules: sd {e['sd_family_mean_across_molecules']:6.2f} | held-out RMS: ridge {e['rms_ridge']:6.2f}  median rule {e['rms_median_rule']:6.2f}  zero {e['rms_zero']:6.2f} | within-molecule per-mode spread {e['rms_within_molecule_spread']:6.2f}")
    json.dump(out, open(prefix + ".json", "w"), indent=1)
    md = [f"# E4 — target diagnostics ({out['date']}), 45 molecules, 12 held out", "",
          "## E4a per-mode target: first-order shift vs matched-eigenvalue shift", "",
          "| family | modes | RMS(first − matched) | median best overlap | frac overlap < 0.9 | sd first | sd matched |", "|---|---|---|---|---|---|---|"]
    for F in FAMILIES:
        e = out["E4a"][F]; md.append(f"| {F} | {e['n']} | {e['rms_diff']:.2f} | {e['median_best_overlap']:.3f} | {e['frac_overlap_below_0_9']:.2f} | {e['sd_first']:.2f} | {e['sd_matched']:.2f} |")
    md += ["", "## E4b family-mean shift (mixing-invariant) across molecules", "",
           "| family | sd across molecules | ridge (held-out) | median rule | zero | within-molecule per-mode spread |", "|---|---|---|---|---|---|"]
    for F in FAMILIES:
        e = out["E4b"][F]
        if "note" in e: md.append(f"| {F} | {e['note']} |||||"); continue
        md.append(f"| {F} | {e['sd_family_mean_across_molecules']:.2f} | {e['rms_ridge']:.2f} | {e['rms_median_rule']:.2f} | {e['rms_zero']:.2f} | {e['rms_within_molecule_spread']:.2f} |")
    open(prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", prefix + ".json/.md")


if __name__ == "__main__":
    main()
