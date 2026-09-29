"""R5 of anchor set two (pre-registration 2026-09-29): diagonal against couplings, a desk test on every molecule with a CC Hessian.

For ΔH = H_CC − H_B3LYP (analytic pyscf B3LYP as the low level, `--use-analytic` of e9_cc_readout) the corrected harmonic frequencies are
computed three ways (E7's `corrected_frequencies`, same-family blocks): with the full correction K (the truth), with its diagonal only, and with
no correction (the zero rule = B3LYP itself). Per family the read is the share of the zero rule's RMS error that the diagonal alone removes,
1 − RMS(diag − full) / RMS(zero − full). Prediction on record: ≥ 70 % for the in-plane ring family, less out of plane.

Usage: python r5_diag_vs_coupling.py <molecules dir> <out prefix> --pair <mol_id>=<hessian_ccsd_t.npz> [--pair ...] [--use-analytic] [--label text]
       a pair may name a folder outside the corpus as <path to folder>=<npz> when the folder holds geometry.json and hessian_b3lyp*.npz (the cation).
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from e9_cc_readout import load_molecule  # noqa: E402
from learning_curve_layerA import FAMILIES  # noqa: E402


def read_molecule(m: dict) -> dict:
    """Per family: RMS of the zero rule and of the diagonal-only correction against the full correction, and the share removed."""
    K = m["K"]
    w_full, _ = T2.corrected_frequencies(m, K)
    w_diag, _ = T2.corrected_frequencies(m, np.diag(np.diag(K)))
    w_zero, _ = T2.corrected_frequencies(m, np.zeros_like(K))
    fam = np.array(m["family"])
    out = {"n_modes": int(len(fam)), "families": {}}
    for F in [*FAMILIES, "all"]:
        sel = np.ones(len(fam), bool) if F == "all" else fam == F
        if not sel.any():
            continue
        rz = E6.rms(w_zero[sel] - w_full[sel]); rd = E6.rms(w_diag[sel] - w_full[sel])
        out["families"][F] = {"n": int(sel.sum()), "rms_zero_rule": rz, "rms_diag_only": rd, "share_removed_by_diagonal": float(1 - rd / rz) if rz > 0 else float("nan")}
    out["offdiag_over_diag_frobenius"] = float(np.linalg.norm(K - np.diag(np.diag(K))) / np.linalg.norm(np.diag(K)))
    return out


def resolve(mdir: Path, spec: str):
    mol, npz = spec.split("=", 1)
    p = Path(mol)
    if p.is_dir():                                   # a folder outside the corpus (the cation)
        return p.parent, p.name, Path(npz)
    return mdir, mol, Path(npz)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("Usage:")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--pair", action="append", required=True, help="<mol_id or folder>=<hessian_ccsd_t.npz>")
    ap.add_argument("--use-analytic", action="store_true"); ap.add_argument("--label", default="R5")
    a = ap.parse_args(argv); t0 = time.time()
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "label": a.label, "use_analytic": a.use_analytic, "molecules": {}}
    rows = []
    for spec in a.pair:
        mdir, mol_id, npz = resolve(Path(a.molecules), spec)
        m = load_molecule(mdir, mol_id, npz, a.use_analytic)
        r = read_molecule(m); r["low_level"] = m["low_source"]; r["cc_hessian"] = str(npz)
        res["molecules"][mol_id] = r
        for F, x in r["families"].items():
            rows.append((mol_id, F, x["n"], x["rms_zero_rule"], x["rms_diag_only"], x["share_removed_by_diagonal"]))
        print(f"{mol_id}: " + " | ".join(f"{F} {x['share_removed_by_diagonal'] * 100:.0f} % (zero {x['rms_zero_rule']:.1f} → diag {x['rms_diag_only']:.1f} cm⁻¹, n={x['n']})"
                                       for F, x in r["families"].items()), flush=True)
    res["seconds"] = round(time.time() - t0, 1)
    Path(a.out_prefix).parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(a.out_prefix + ".json", "w", encoding="utf-8"), indent=1, default=float)
    md = [f"# R5 — diagonal against couplings ({res['label']}, {res['date']}); low level {'pyscf analytic' if a.use_analytic else 'corpus psi4 FD'} B3LYP", "",
          "Share of the zero rule's RMS frequency error (B3LYP against CC, same-family blocks) that the diagonal of the CC correction alone removes; "
          "prediction on record: ≥ 70 % in plane (ring-ip), less out of plane.", "",
          "| molecule | family | modes | RMS zero rule | RMS diagonal only | removed by the diagonal |", "|---|---|---|---|---|---|"]
    md += [f"| {mid} | {F} | {n} | {rz:.2f} | {rd:.2f} | **{s * 100:.0f} %** |" for mid, F, n, rz, rd, s in rows]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix, f"in {res['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
