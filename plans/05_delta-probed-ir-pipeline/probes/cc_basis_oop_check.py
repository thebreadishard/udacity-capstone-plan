"""Odds lever 2 (3 Oct 2026): is the large CC correction of the out-of-plane modes a basis-set effect? For the displacement coordinates of a partial
cc-pVTZ run (grad_<k>_<sign>.npy and ener_<k>_<sign>.npy), the diagonal curvature H_kk at cc-pVTZ (gradient route and energy route) against the cc-pVDZ
anchor's H_kk and the analytic B3LYP H_kk of the same molecule: the CC correction ΔH_kk = H_kk(CC) − H_kk(B3LYP) at DZ and at TZ, and the share of the DZ
correction that the basis step removes. One row per coordinate, with its out-of-plane fraction.

    python probes/cc_basis_oop_check.py <tz partial dir> <dz anchor dir> <molecule dir with hessian_b3lyp_analytic.npz>
"""
import json
import os
import sys
from datetime import datetime

import numpy as np


def main() -> int:
    tz, dz, mol = sys.argv[1:4]
    ref = np.load(os.path.join(tz, "reference.npz"))
    x0 = np.asarray(ref["coords_bohr"], float); e0 = float(ref["energy"])
    hdz = np.load(os.path.join(dz, "hessian_ccsd_t.npz")); H_dz = hdz["H_raw"]; h = float(hdz["step"])
    H_b3 = np.load(os.path.join(mol, "hessian_b3lyp_analytic.npz"))["H_raw"]
    xc = x0 - x0.mean(0); normal = np.linalg.eigh(xc.T @ xc)[1][:, 0]
    ks = sorted({int(f[5:7]) for f in os.listdir(tz) if f.startswith("grad_") and f.endswith("_p.npy")})
    rows = []
    for k in ks:
        gp, gm = (np.load(os.path.join(tz, f"grad_{k:02d}_{s}.npy")).ravel() for s in ("p", "m"))
        hkk_tz = float((gp[k] - gm[k]) / (2 * h))
        ep, em = (float(np.load(os.path.join(tz, f"ener_{k:02d}_{s}.npy"))) for s in ("p", "m"))
        hkk_tz_e = (ep + em - 2 * e0) / h ** 2
        d_dz, d_tz = float(H_dz[k, k] - H_b3[k, k]), hkk_tz - float(H_b3[k, k])
        rows.append(dict(k=k, atom=k // 3, xyz="xyz"[k % 3], oop_fraction=float(abs(normal[k % 3])), H_b3lyp=float(H_b3[k, k]), H_cc_dz=float(H_dz[k, k]),
                         H_cc_tz=hkk_tz, H_cc_tz_energy_route=hkk_tz_e, two_route_tz=abs(hkk_tz - hkk_tz_e), dH_dz=d_dz, dH_tz=d_tz,
                         basis_share_of_dz_correction=(d_dz - d_tz) / d_dz if d_dz else float("nan")))
    print("| k | atom xyz | oop | H B3LYP | H CC/DZ | H CC/TZ (grad) | TZ two-route | ΔH DZ | ΔH TZ | share removed by the basis |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['k']} | {r['atom']} {r['xyz']} | {r['oop_fraction']:.2f} | {r['H_b3lyp']:.5f} | {r['H_cc_dz']:.5f} | {r['H_cc_tz']:.5f} | {r['two_route_tz']:.1e} | "
              f"{r['dH_dz']:+.5f} | {r['dH_tz']:+.5f} | {100 * r['basis_share_of_dz_correction']:+.0f} % |")
    out = os.path.join(tz, f"cc_basis_oop_check_{datetime.now():%Y-%m-%d}.json")
    json.dump(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), tz=tz, dz=dz, molecule=mol, step=h, rows=rows), open(out, "w"), indent=1)
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
