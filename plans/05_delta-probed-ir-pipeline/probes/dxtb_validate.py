"""Validation of dxtb's GFN2-xTB before it makes S2's xtb force fields (18 Oct 2026; S2 amendment 4) — runs in the WSL env `dxtb`.

    python dxtb_validate.py <ref.json> [<ref.json> ...] --out <dir>

Upstream: dxtb's test/test_properties/test_hessian.py makes the same calls (Calculator(numbers, par, opts=...), calc.hessian(positions,
charge), calc.hessian_numerical) with GFN1-xTB at atol/rtol 1e-5; GFN2's energies are tested in test/test_scf/test_elements_gfn2.py and
test/test_singlepoint/refs/gfn2. Here, for each molecule at its reference geometry and at a displaced one (0.05 bohr, seed 0):
  - energy and gradient against the xtb 6.7.1 binary (`--acc 0.0001`): pass |ΔE| ≤ 1e-6 E_h, max |Δg| ≤ 1e-5 E_h/bohr;
  - the autograd Hessian against central differences of dxtb's autograd forces (step 1e-4 bohr): pass max |ΔH| ≤ 1e-5 E_h/bohr² (the
    upstream test's atol; dxtb's own NumericalCalculator, differences of energies, gave no result for water in 50 minutes);
  - no projection: |H·t| for the three translations ≤ 1e-8 (a Cartesian Hessian is translation-invariant; xtb's file is also
    rotation-projected, which is wrong away from a minimum).
Writes <dir>/dxtb_validate.json and prints PASS or FAIL per check.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import torch
from dxtb import GFN2_XTB
from dxtb.calculators import AutogradCalculator   # GFN2's analytical gradient is not implemented in dxtb 0.4.0

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from xtb_hessians_for_qff import XTB, write_xyz  # noqa: E402

Z = {"H": 1, "C": 6, "N": 7, "O": 8, "F": 9, "S": 16, "Cl": 17}
# the upstream test's options, with the libcint integral driver: dxtb 0.4.0's PyTorch drivers lack GFN2's multipole integrals
OPTS = {"maxiter": 200, "mixer": "anderson", "scf_mode": "full", "verbosity": 0, "f_atol": 1e-10, "x_atol": 1e-10, "int_driver": "libcint"}
TOL_E, TOL_G, TOL_H, TOL_T = 1e-6, 1e-5, 1e-5, 1e-8
FD_STEP = 1e-4                         # bohr
DD = {"dtype": torch.double, "device": torch.device("cpu")}


def xtb_energy_gradient(symbols, geom_bohr):
    """The xtb binary's GFN2 energy (E_h) and gradient (E_h/bohr) at --acc 0.0001."""
    work = tempfile.mkdtemp(prefix="xtbv_")
    write_xyz(os.path.join(work, "in.xyz"), symbols, geom_bohr)
    out = subprocess.run([XTB, "in.xyz", "--gfn", "2", "--acc", "0.0001", "--grad"], cwd=work, capture_output=True, text=True, check=True).stdout
    energy = next(float(ln.split()[3]) for ln in out.splitlines() if "TOTAL ENERGY" in ln)
    with open(os.path.join(work, "gradient"), encoding="utf-8") as fh:
        rows = [ln for ln in fh.read().splitlines() if ln.strip() and not ln.startswith("$") and "cycle" not in ln]
    n = len(symbols)
    return energy, np.array([[float(v.replace("D", "E")) for v in r.split()] for r in rows[n:2 * n]])


def forces_fd_hessian(calc, pos):
    """Central differences of the autograd forces: H[:, k] = −(F(x + h e_k) − F(x − h e_k)) / 2h, symmetrised."""
    x = pos.detach().reshape(-1)
    n = x.numel()
    H = np.zeros((n, n))
    for k in range(n):
        cols = []
        for s in (1.0, -1.0):
            xk = x.clone()
            xk[k] += s * FD_STEP
            calc.reset()
            cols.append(calc.forces(xk.reshape(-1, 3).requires_grad_(True), 0).detach().numpy().reshape(-1))
        H[:, k] = -(cols[0] - cols[1]) / (2 * FD_STEP)
    return 0.5 * (H + H.T)


def check_geometry(symbols, geom_bohr):
    numbers = torch.tensor([Z[s] for s in symbols])
    pos = torch.tensor(np.asarray(geom_bohr).reshape(-1, 3), **DD)
    calc = AutogradCalculator(numbers, GFN2_XTB, opts=OPTS, **DD)
    e = float(calc.energy(pos.clone(), 0))
    g = -calc.forces(pos.clone().requires_grad_(True), 0).detach().numpy()
    calc.reset()
    h = calc.hessian(pos.clone().requires_grad_(True), 0, matrix=True).detach().numpy()
    h_num = forces_fd_hessian(calc, pos)
    e_x, g_x = xtb_energy_gradient(symbols, geom_bohr)
    n = len(symbols)
    t = np.zeros((3 * n, 3))
    for a in range(n):
        t[3 * a:3 * a + 3] = np.eye(3)
    return {"dE": abs(e - e_x), "dG": float(np.abs(g - g_x).max()), "dH_autograd_vs_numerical": float(np.abs(h - h_num).max()),
            "translation_residual": float(np.abs(h @ t).max()), "max_H": float(np.abs(h).max())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("refs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    results, ok = {}, True
    for path in a.refs:
        with open(path, encoding="utf-8") as fh:
            ref = json.load(fh)
        sym, x = ref["molecule"]["symbols"], np.array(ref["molecule"]["geometry"], float).reshape(-1, 3)
        for label, geom in (("reference", x), ("displaced", x + rng.normal(0, 0.05, x.shape))):
            r = check_geometry(sym, geom)
            r["pass"] = bool(r["dE"] <= TOL_E and r["dG"] <= TOL_G and r["dH_autograd_vs_numerical"] <= TOL_H and r["translation_residual"] <= TOL_T)
            ok &= r["pass"]
            results[f"{path} [{label}]"] = r
            print(f"{os.path.basename(os.path.dirname(os.path.dirname(path)))}/{label}: dE {r['dE']:.1e}  dG {r['dG']:.1e}  "
                  f"dH {r['dH_autograd_vs_numerical']:.1e}  |Ht| {r['translation_residual']:.1e}  -> {'PASS' if r['pass'] else 'FAIL'}", flush=True)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "dxtb_validate.json"), "w", encoding="utf-8") as fh:
        json.dump({"tolerances": {"E": TOL_E, "G": TOL_G, "H": TOL_H, "translation": TOL_T}, "results": results, "pass": ok}, fh, indent=1)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
