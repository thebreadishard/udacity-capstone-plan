"""Composite anchor level, test 1 (`GoalGathering/notes/Design_2026-10-04_Composite_Anchor_Level_DZ_TZ.md`, registered 4 Oct 2026 14:5x): the basis
step Δ_X = H_kk(X/cc-pVTZ) − H_kk(X/cc-pVDZ) of a cheap level X (B3LYP, MP2 with frozen core) on the coordinates where the CCSD(T) step was measured,
beside that measured Δ_CC. Finite differences of analytic gradients with the anchors' step; the analytic B3LYP Hessian at cc-pVDZ as the second route
for the B3LYP numbers. pyscf, under WSL qc05.

    python probes/cc_composite_basis_check.py <geometry.json> <out_prefix> [--oop-check <cc_basis_oop_check json>] [--ks 2,18,20] [--levels b3lyp,mp2]
                                               [--threads 4] [--step 0.005] [--grid 99,590] [--frozen auto] [--max-memory 8000]
    python probes/cc_composite_basis_check.py --smoke <out_prefix>          # water, ks 0,1,2, both levels, both bases (seconds)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

BASES = ("cc-pvdz", "cc-pvtz")
CORE = {"H": 0, "C": 1, "N": 1, "O": 1, "F": 1, "S": 5, "Cl": 5}
WATER = dict(symbols=["O", "H", "H"], coords_bohr=[[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])


def build(symbols, coords, basis, max_memory, cart=False):
    """cart=True selects Cartesian d functions (the corpus's 6-31G* convention, `corpus/analytic_hessians.py`); the cc-pVnZ anchors use spherical."""
    from pyscf import gto
    return gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords, strict=True)], unit="Bohr", basis=basis, cart=cart, symmetry=False, verbose=0, max_memory=max_memory)


def b3lyp_mf(mol, grid):
    from pyscf import dft
    mf = dft.RKS(mol); mf.xc = "b3lyp"; mf.grids.atom_grid = grid; mf.grids.prune = None; mf.conv_tol = 1e-11
    e = mf.kernel()
    if not mf.converged:
        raise RuntimeError("B3LYP SCF not converged")
    return mf, float(e)


def gradient(level, symbols, coords, basis, grid, frozen, max_memory, cart=False):
    """The analytic nuclear gradient (3N, flattened) at one geometry for X = b3lyp | mp2."""
    from pyscf import mp, scf
    mol = build(symbols, coords, basis, max_memory, cart)
    if level == "b3lyp":
        mf, _ = b3lyp_mf(mol, grid)
        return mf.nuc_grad_method().kernel().ravel()
    mf = scf.RHF(mol); mf.conv_tol = 1e-11; mf.kernel()
    if not mf.converged:
        raise RuntimeError("RHF not converged")
    pt = mp.MP2(mf, frozen=frozen or None); pt.kernel()
    return pt.nuc_grad_method().kernel().ravel()


def fd_curvature(level, symbols, x0, k, basis, step, grid, frozen, max_memory, cart=False):
    """H_kk and the whole row H_k,: by central differences of the gradient along Cartesian coordinate k."""
    rows = []
    for s in (+1, -1):
        x = np.array(x0, float).ravel(); x[k] += s * step
        rows.append(gradient(level, symbols, x.reshape(-1, 3), basis, grid, frozen, max_memory, cart))
    row = (rows[0] - rows[1]) / (2 * step)
    return float(row[k]), row


def analytic_b3lyp_diag(symbols, x0, basis, grid, max_memory):
    mol = build(symbols, x0, basis, max_memory)
    mf, _ = b3lyp_mf(mol, grid)
    n = len(symbols)
    H = mf.Hessian().kernel().transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
    return np.diag(0.5 * (H + H.T)).copy()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("geometry", nargs="?")
    ap.add_argument("out_prefix")
    ap.add_argument("--oop-check", default=None, help="cc_basis_oop_check json: its rows give the coordinates and Δ_CC")
    ap.add_argument("--ks", default=None, help="comma list of Cartesian coordinates (default: the oop-check rows)")
    ap.add_argument("--levels", default="b3lyp,mp2")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--step", type=float, default=0.005)
    ap.add_argument("--grid", default="99,590")
    ap.add_argument("--frozen", default="auto", help="MP2 frozen core: 'auto' = one orbital per C/N/O/F, five per S/Cl (the anchors' rule), or an integer")
    ap.add_argument("--max-memory", type=int, default=8000)
    ap.add_argument("--smoke", action="store_true", help="water, ks 0,1,2: the mechanics and the two-route check in seconds")
    a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads)
    grid = tuple(int(v) for v in a.grid.split(","))
    if a.smoke:
        symbols, x0 = WATER["symbols"], np.array(WATER["coords_bohr"], float)
        ks, dcc = [0, 1, 2], {}
    else:
        g = json.loads(Path(a.geometry).read_text(encoding="utf-8"))
        symbols, x0 = [s.capitalize() for s in g["symbols"]], np.asarray(g["coords_bohr"], float)
        dcc = {}
        if a.oop_check:
            for r in json.loads(Path(a.oop_check).read_text(encoding="utf-8"))["rows"]:
                dcc[int(r["k"])] = dict(d_cc=float(r["H_cc_tz"] - r["H_cc_dz"]), oop=float(r["oop_fraction"]), atom=r["atom"], xyz=r["xyz"])
        ks = [int(v) for v in a.ks.split(",")] if a.ks else sorted(dcc)
    frozen = sum(CORE[s] for s in symbols) if a.frozen == "auto" else int(a.frozen)
    levels = [v.strip() for v in a.levels.split(",") if v.strip()]
    t0 = time.time()
    log = lambda s: print(f"[{datetime.now():%H:%M:%S}] {s}", flush=True)  # noqa: E731
    out = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), geometry=a.geometry, step=a.step, grid=grid, frozen=frozen, levels=levels, ks=ks, rows=[])
    hkk = {}                                                        # (level, basis, k) -> H_kk ; rows kept in the npz
    row_store = {}
    for level in levels:
        for basis in BASES:
            for k in ks:
                t1 = time.time()
                h, row = fd_curvature(level, symbols, x0, k, basis, a.step, grid, frozen, a.max_memory)
                hkk[(level, basis, k)] = h; row_store[f"{level}_{basis}_k{k}"] = row
                log(f"{level} {basis} k={k}: H_kk {h:+.6f} ({time.time() - t1:.0f} s)")
    second_route = {}
    if "b3lyp" in levels:
        t1 = time.time()
        diag = analytic_b3lyp_diag(symbols, x0, BASES[0], grid, a.max_memory)
        for k in ks:
            second_route[k] = dict(analytic=float(diag[k]), fd=hkk[("b3lyp", BASES[0], k)], diff=float(abs(diag[k] - hkk[("b3lyp", BASES[0], k)])))
        log(f"analytic B3LYP/{BASES[0]} Hessian: max |analytic − FD| on ks {max(v['diff'] for v in second_route.values()):.1e} a.u. ({time.time() - t1:.0f} s)")
    for k in ks:
        r = dict(k=k, **dcc.get(k, {}))
        for level in levels:
            d = hkk[(level, BASES[1], k)] - hkk[(level, BASES[0], k)]
            r[f"d_{level}"] = float(d)
            r[f"H_{level}_dz"] = hkk[(level, BASES[0], k)]; r[f"H_{level}_tz"] = hkk[(level, BASES[1], k)]
            if "d_cc" in r:
                r[f"ratio_{level}"] = float(d / r["d_cc"]) if r["d_cc"] else float("nan")
                r[f"tracks_{level}"] = bool(abs(d - r["d_cc"]) <= 0.2 * abs(r["d_cc"]))
        if k in second_route:
            r["b3lyp_two_route"] = second_route[k]["diff"]
        out["rows"].append(r)
    out["seconds"] = round(time.time() - t0)
    np.savez(a.out_prefix + "_rows.npz", **row_store)
    Path(a.out_prefix + ".json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    head = ["k"] + (["atom xyz", "oop", "Δ_CC"] if dcc else []) + [f"Δ_{lv}" for lv in levels] + ([f"{lv}/CC" for lv in levels] if dcc else []) + ["B3LYP two-route"]
    md = [f"# Composite anchor level, test 1 — basis step TZ−DZ per level on {'water (smoke)' if a.smoke else Path(a.geometry).parent.name} — {out['date']}", "",
          f"Step {a.step} bohr, grid {grid}, MP2 frozen core {frozen}; levels {levels}; {out['seconds']} s at {a.threads} threads. A level *tracks* a coordinate "
          "when |Δ_X − Δ_CC| ≤ 0.2 |Δ_CC|.", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in out["rows"]:
        cells = [str(r["k"])]
        if dcc:
            cells += [f"{r.get('atom', '')} {r.get('xyz', '')}", f"{r.get('oop', float('nan')):.2f}", f"{r['d_cc']:+.5f}"]
        cells += [f"{r[f'd_{lv}']:+.5f}" for lv in levels]
        if dcc:
            cells += [f"{r[f'ratio_{lv}']:+.2f}{' tracks' if r[f'tracks_{lv}'] else ''}" for lv in levels]
        cells += [f"{r['b3lyp_two_route']:.1e}" if "b3lyp_two_route" in r else "—"]
        md.append("| " + " | ".join(cells) + " |")
    if dcc:
        for lv in levels:
            n = sum(r[f"tracks_{lv}"] for r in out["rows"])
            md.append(f"\n**{lv}** tracks {n} of {len(out['rows'])} coordinates.")
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
