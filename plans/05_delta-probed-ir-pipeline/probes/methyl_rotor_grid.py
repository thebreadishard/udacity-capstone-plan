"""Energies of 4-methylimidazole on a (torsion, CH3 bend, CH3 bend) grid for the variational check of TASKS 176
(`GoalGathering/notes/PreRegistration_2026-11-04_Methyl_Rotor_Variational.md`, part B; the user, 4 Nov 2026: 'Ja, doe optie 4 met optie 2
ernaast').

A point is the G reference geometry displaced along the reduced normal modes 20 and 21 (A[:,20] q₂₀ + A[:,21] q₂₁, `dpir.qff.harmonic`),
then the three methyl H turned by Δτ about the displaced C1→C0 axis, so the bends ride with the top. q on the Gauss–Hermite points of the
reduced coordinate, τ on equally spaced points over 360°. Energies with the Hessian runs' RKS (`rks_setup`, `converged_scf`), one json per
lane, written after every point, so a second call resumes.

    python probes/methyl_rotor_grid.py <out_dir> --lane 0 --lanes 12 [--n-tau 24 --n-q 11] [--reuse <coarser grid dir>] [--smoke] [--dry-run]

--reuse seeds the lanes with a coarser τ grid's energies (TASKS 176's 48-point grid on the 24-point one), read only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dpir.qff import HessianRecord, harmonic, load_results  # noqa: E402  after the src path

REFERENCE = HERE / "results_m1" / "s2_anharmonic_2026-10-18" / "s2" / "B_151c8ce719" / "G" / "refhess"
METHYL_C, RING_C, RING_NEXT = 0, 1, 2       # the torsion H6–C0–C1–C2 and the top's axis C1→C0
TOP = (6, 7, 8)                             # the methyl H
BENDS = (20, 21)                            # the CH3 bends (harmonic 1507.5 and 1521.1 cm⁻¹)
XC, BASIS, GRID, CONV = "b3lyp", "6-31g*", "75,302", 1e-11


def reference() -> HessianRecord:
    """The G setting's reference record (geometry in bohr, its Hessian)."""
    recs = load_results(str(REFERENCE))
    if len(recs) != 1:
        raise SystemExit(f"{REFERENCE}: expected one reference record, found {len(recs)}")
    return recs[0]


def dihedral(x: np.ndarray, i: int, j: int, k: int, m: int) -> float:
    """The dihedral i–j–k–m in degrees, (−180, 180]."""
    b0, b1, b2 = x[i] - x[j], x[k] - x[j], x[m] - x[k]
    b1 = b1 / np.linalg.norm(b1)
    v, w = b0 - np.dot(b0, b1) * b1, b2 - np.dot(b2, b1) * b1
    return float(np.degrees(np.arctan2(np.dot(np.cross(b1, v), w), np.dot(v, w))))


def turn_top(x: np.ndarray, angle_deg: float) -> np.ndarray:
    """The methyl H turned by angle_deg about the C1→C0 axis (Rodrigues), every other atom left in place."""
    axis = x[METHYL_C] - x[RING_C]
    k = axis / np.linalg.norm(axis)
    a = np.radians(angle_deg)
    out = x.copy()
    for h in TOP:
        r = x[h] - x[METHYL_C]
        out[h] = x[METHYL_C] + r * np.cos(a) + np.cross(k, r) * np.sin(a) + k * np.dot(k, r) * (1 - np.cos(a))
    return out


def tau_of(x: np.ndarray) -> float:
    """The registered torsion H6–C0–C1–C2 in degrees."""
    return dihedral(x, TOP[0], METHYL_C, RING_C, RING_NEXT)


def grid_points(n_tau: int, n_q: int) -> list[dict]:
    """Every (Δτ, q₂₀, q₂₁) point, τ outermost; q on the Gauss–Hermite nodes of the reduced coordinate."""
    nodes = np.polynomial.hermite.hermgauss(n_q)[0]
    return [{"index": (t * n_q + a) * n_q + b, "k_tau": t, "i20": a, "i21": b, "dtau_deg": 360.0 * t / n_tau,
             "q20": float(nodes[a]), "q21": float(nodes[b])}
            for t in range(n_tau) for a in range(n_q) for b in range(n_q)]


def geometry(x0: np.ndarray, A: np.ndarray, point: dict) -> np.ndarray:
    """The point's geometry (bohr, (N, 3)): displaced along the two bends, then the top turned."""
    x = x0 + (A[:, BENDS[0]] * point["q20"] + A[:, BENDS[1]] * point["q21"]).reshape(-1, 3)
    return turn_top(x, point["dtau_deg"])


def write_json(path: Path, obj) -> None:
    """A record moved over its target; the temp name is the process's own, since every lane writes the same grid.json."""
    tmp = path.with_suffix(f"{path.suffix}.tmp{os.getpid()}")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    tmp.replace(path)


def load_grid(grid_dir: Path) -> tuple[dict, dict[str, float]]:
    """A grid directory's grid.json and the union of its lanes' energies."""
    meta = json.loads((grid_dir / "grid.json").read_text(encoding="utf-8"))
    E: dict[str, float] = {}
    for f in sorted(grid_dir.glob("energies_lane*.json")):
        E |= json.loads(f.read_text(encoding="utf-8"))
    return meta, E


def reused_energies(old_meta: dict, old_E: dict[str, float], points: list[dict], n_tau: int, n_q: int, level: list) -> dict[str, float]:
    """The energies of a coarser τ grid at this grid's indices: same q nodes and level, n_tau a multiple of the old one, every old point
    computed; each mapped point must sit at the same Δτ and q, else the reuse is refused."""
    if old_meta["n_q"] != n_q or list(old_meta["level"]) != list(level):
        raise SystemExit(f"reuse refused: n_q {old_meta['n_q']} / level {old_meta['level']} against {n_q} / {level}")
    if n_tau % old_meta["n_tau"] != 0 or n_tau == old_meta["n_tau"]:
        raise SystemExit(f"reuse refused: n_tau {n_tau} is not a finer multiple of {old_meta['n_tau']}")
    step = n_tau // old_meta["n_tau"]
    by_index = {p["index"]: p for p in points}
    out: dict[str, float] = {}
    for p in old_meta["points"]:
        if str(p["index"]) not in old_E:
            raise SystemExit(f"reuse refused: old point {p['index']} has no energy")
        new = by_index[(p["k_tau"] * step * n_q + p["i20"]) * n_q + p["i21"]]
        if abs(new["dtau_deg"] - p["dtau_deg"]) > 1e-9 or abs(new["q20"] - p["q20"]) > 1e-12 or abs(new["q21"] - p["q21"]) > 1e-12:
            raise SystemExit(f"reuse refused: old point {p['index']} does not sit on new point {new['index']}")
        out[str(new["index"])] = old_E[str(p["index"])]
    return out


def energy_function(lib_log, threads: int):
    """B3LYP/6-31G* (75,302) energies with the Hessian runs' RKS, pyscf's own log in lib_log."""
    from library_log import pyscf_mole
    from pyscf import lib
    from pyscf_hessians_for_qff import rks_setup
    from scf_converge import converged_scf
    lib.num_threads(threads)

    def energy(symbols: list[str], x: np.ndarray) -> float:
        mol = pyscf_mole(lib_log, atom=[(s, tuple(r)) for s, r in zip(symbols, x, strict=True)], unit="Bohr", basis=BASIS, symmetry=False)
        return float(converged_scf(rks_setup(mol, XC, GRID, CONV), 200, log=lambda m: print(m, flush=True))[1])
    return energy


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Command line; --smoke is four points (τ on four values, q = 0)."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir")
    ap.add_argument("--lane", type=int, default=0)
    ap.add_argument("--lanes", type=int, default=1)
    ap.add_argument("--n-tau", type=int, default=24)
    ap.add_argument("--n-q", type=int, default=11)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="write grid.json and check the geometries; no energy")
    ap.add_argument("--reuse", help="a coarser grid directory whose energies seed this one (read only)")
    a = ap.parse_args(argv)
    if a.smoke and a.reuse:
        raise SystemExit("--smoke and --reuse do not combine (the smoke's four τ values are no multiple of a real grid)")
    if a.reuse and Path(a.reuse).resolve() == Path(a.out_dir).resolve():
        raise SystemExit("--reuse must name another directory than out_dir: the reused grid is read only")
    if a.smoke:
        a.n_tau, a.n_q = 4, 1
    if a.n_q % 2 != 1 or a.n_tau % 2 != 0:
        raise SystemExit("--n-q must be odd (q = 0 on the grid) and --n-tau even (the 12-point subset)")
    if not 0 <= a.lane < a.lanes:
        raise SystemExit(f"--lane {a.lane} outside 0..{a.lanes - 1}")
    return a


def main(argv: list[str] | None = None) -> int:
    """Stage the grid, then compute this lane's energies."""
    from library_log import PYSCF_LOG_NAME
    a = parse_args(argv)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ref = reference()
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    x0 = ref.geom.reshape(-1, 3)
    points = grid_points(a.n_tau, a.n_q)
    tau0 = tau_of(x0)
    for p in (p for p in points if p["i20"] == p["i21"] == a.n_q // 2):   # at q = 0 the turned top must sit at τ₀ + Δτ
        got = (tau_of(geometry(x0, harm.A, p)) - tau0 - p["dtau_deg"] + 180.0) % 360.0 - 180.0
        if abs(got) > 1e-6:
            raise SystemExit(f"point {p['index']}: torsion off by {got:.2e}°")
    level = [XC, BASIS, GRID, CONV]
    reused = reused_energies(*load_grid(Path(a.reuse)), points, a.n_tau, a.n_q, level) if a.reuse else {}
    write_json(out / "grid.json", {"reference": str(REFERENCE), "tau0_deg": tau0, "n_tau": a.n_tau, "n_q": a.n_q, "bends": list(BENDS),
                                   "omega_cm": [float(harm.omega_cm[b]) for b in BENDS], "level": level, "points": points,
                                   "reused_from": a.reuse, "n_reused": len(reused)})
    if a.dry_run:
        print(f"dry run: {len(points)} points ({len(reused)} reused), τ₀ {tau0:.3f}°, ω {harm.omega_cm[BENDS[0]]:.1f} / "
              f"{harm.omega_cm[BENDS[1]]:.1f}", flush=True)
        return 0
    ck = out / f"energies_lane{a.lane:02d}.json"
    E = json.loads(ck.read_text(encoding="utf-8")) if ck.exists() else {}
    mine = [p for p in points if p["index"] % a.lanes == a.lane]
    for p in mine:
        key = str(p["index"])
        if key in reused and E.setdefault(key, reused[key]) != reused[key]:
            raise SystemExit(f"point {key}: lane checkpoint {E[key]} differs from the reused {reused[key]}")
    write_json(ck, E)
    with open(out / f"lane{a.lane:02d}_{PYSCF_LOG_NAME}", "a", encoding="utf-8") as lib_log:
        energy = energy_function(lib_log, a.threads)
        for n, p in enumerate(mine, 1):
            key = str(p["index"])
            if key in E:
                continue
            t0 = time.time()
            E[key] = energy(ref.symbols, geometry(x0, harm.A, p))
            write_json(ck, E)
            print(f"[{time.strftime('%H:%M:%S')}] lane {a.lane} {n}/{len(mine)} point {key} E = {E[key]:.12f} ({time.time() - t0:.0f} s)",
                  flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
