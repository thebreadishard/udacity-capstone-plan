"""Set-three diagnosis, A7 (21 Oct 2026): which part of the CC correction runs against the proxy? numpy only (beside the night's runs).

The anchor's correction to the low level splits as ΔH_CC = [CC/DZ − B3LYP/6-31G*] (the method part, at a double-zeta basis) + [MP2/TZ −
MP2/DZ] (the basis step of the composite). Per anchor with a valid CC/DZ Hessian, in the low level's mode basis (analytic B3LYP, mass-
weighted, translations and rotations projected), the first-order shifts K_kk of each part and of the proxy (ωB97X − B3LYP, the network's
pretraining target) are compared per family (the corpus rule of e8_cc_locality): correlation with the proxy, slope on the proxy, rms, the
mean shift and the slope of the centred shifts (the two factors of the anchor price's distortion, TASKS 82).

    python probes/set3_decompose.py <out_dir>        → <out_dir>/decompose.json, printed table
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_cc_locality as L  # noqa: E402
import set3_diagnosis as D  # noqa: E402  (numpy only: no torch beside the night's runs)
from qc_common import AMU2AU, HARTREE2CM  # noqa: E402

M05 = PLAN / "modules" / "05_support_predictor"
FAMS = ("CH-oop", "other", "ring-ip", "CH-stretch")


def projected(path: Path) -> np.ndarray:
    with np.load(path) as z:
        return np.asarray(z["H_projected"], float)


def shifts(dH: np.ndarray, V: np.ndarray, w: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """First-order frequency shifts (cm⁻¹) of the low level's modes under ΔH: K_kk = (Vᵀ ΔH_mw V)_kk / 2ω_k."""
    mm = np.repeat(masses * AMU2AU, 3)
    Km = V.T @ (dH / np.sqrt(np.outer(mm, mm))) @ V
    return np.diag(Km) / (2 * np.sqrt(np.abs(w))) * HARTREE2CM


def compare(a: np.ndarray, b: np.ndarray) -> dict:
    ac, bc = a - a.mean(), b - b.mean()
    return {"corr": float(np.corrcoef(a, b)[0, 1]) if len(a) > 2 else float("nan"), "slope": float(a @ b / (b @ b)),
            "rms": float(np.sqrt(np.mean(a ** 2))), "mean": float(a.mean()), "centred_slope": float(ac @ bc / (bc @ bc))}


def anchor_parts(mol_dir: Path, tz: Path, dz: Path) -> dict:
    g = json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))
    sym, x, masses = [s.capitalize() for s in g["symbols"]], np.asarray(g["coords_bohr"], float), np.asarray(g["masses_amu"], float)
    low = projected(mol_dir / "hessian_b3lyp_analytic.npz")
    w, freq, V = L.normal_modes(low, masses)
    fam = L.families(freq, V, sym, masses, x)
    parts = {"proxy": projected(mol_dir / "hessian_wb97x_analytic.npz") - low, "total": projected(tz) - low,
             "method (CC/DZ - B3LYP)": projected(dz) - low, "basis step (TZ - DZ)": projected(tz) - projected(dz)}
    k = {name: shifts(dH, V, w, masses) for name, dH in parts.items()}
    out = {}
    for f in FAMS:
        sel = fam == f
        if sel.sum() >= 3:
            out[f] = {name: compare(k[name][sel], k["proxy"][sel]) for name in parts if name != "proxy"}
            out[f]["proxy rms"] = float(np.sqrt(np.mean(k["proxy"][sel] ** 2)))
            out[f]["proxy mean"] = float(np.mean(k["proxy"][sel]))
            out[f]["n"] = int(sel.sum())
    return out


def main(out_dir: Path) -> int:
    names = {**D.S3.ORIGINALS, **D.S3.NEW}
    tz = D.anchors()
    res = {}
    for i, dz in D.dz_files().items():
        res[names[i]] = {"id": i, **anchor_parts(out_dir / "corpus" / "molecules" / i, Path(tz[i]), dz)}
    (out_dir / "decompose.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for f in FAMS:
        print(f"== {f}: correlation with the proxy shifts (slope) | rms of the part / of the proxy, cm-1")
        for mol, r in res.items():
            if f in r:
                print(f"  {mol:15s} n {r[f]['n']:2d} | " + " | ".join(f"{p}: {v['corr']:+.2f} ({v['slope']:+.2f}) rms {v['rms']:.1f}"
                                                                     for p, v in r[f].items() if isinstance(v, dict))
                      + f" | proxy rms {r[f]['proxy rms']:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve()))
