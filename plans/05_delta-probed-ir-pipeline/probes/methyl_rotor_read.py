"""The reads of `GoalGathering/notes/PreRegistration_2026-11-04_Methyl_Rotor_Variational.md` (TASKS 176/177; the user, 4 Nov 2026: 'Ja, doe
optie 4 met optie 2 ernaast'), by the lines registered there before any computation.

    python probes/methyl_rotor_read.py scan <scan_dir> --out <json>
    python probes/methyl_rotor_read.py grid <grid_dir> --scan <scan read json> --out <json>

`scan`: V3/V6 from the relaxed scan, the internal-rotation constant F of the reference, the 1D torsional levels. `grid`: product DVR on the
(τ, q₂₀, q₂₁) grid — periodic Fourier DVR in τ, harmonic-oscillator DVR in q — with H = −F ∂²/∂τ² + Σ (ω_i/2)(−∂²/∂q_i²) + V; the CH3
bend fundamentals on V_full and on V_nt (no torsion–bend coupling), against the full-dimensional VPT2 Δ in both coordinate sets
(amendment 1: a three-mode VPT2 loses the cancellation of the torsion's large quartic and is not defined here).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dpir.qff import HARTREE_CM, MASS, ROT_CONST_AMU_A2_CM  # noqa: E402  after the src path

MICROWAVE_V3_CM = 317.20      # Gougoula et al., J. Chem. Phys. 2019 (repository records; to check in the paper before a document cites it)
V3_TOLERANCE = 0.15
PERIODIC_CM = 0.5
FREE_ROTOR_M = 30
CONVERGED_CM = 0.3
AGREE_CM = 1.5
SPURIOUS_VPT2_CM = 3.0
MIN_CHARACTER = 0.5
BEND_WINDOW_CM = 400.0        # the bend fundamentals are looked for within this of the harmonic bends
TOP, AXIS = (6, 7, 8), (1, 0)  # methyl H; the top's axis C1→C0 (0-based, as methyl_rotor_grid.py)
BOHR_ANGSTROM = 0.529177210903
BRIDGE = HERE / "results_m1" / "psience_bridge_2026-11-04"   # TASKS 173's full-dimensional Psience runs (Cartesian, coupled / torsion out)


# ---------------------------------------------------------------------------------------------------------------------- part A


def fit_v3_v6(tau_rad: np.ndarray, e_cm: np.ndarray) -> tuple[float, float, float]:
    """(V3, V6, offset) of E = c + V3/2 (1 − cos 3τ) + V6/2 (1 − cos 6τ), least squares."""
    X = np.column_stack([np.ones_like(tau_rad), (1 - np.cos(3 * tau_rad)) / 2, (1 - np.cos(6 * tau_rad)) / 2])
    c, v3, v6 = np.linalg.lstsq(X, e_cm, rcond=None)[0]
    return float(v3), float(v6), float(c)


def internal_rotation_constant(symbols: list[str], geom_bohr: np.ndarray) -> float:
    """F = ħ²/(2 I_r) in cm⁻¹, I_r = I_α (1 − Σ_g λ_g² I_α / I_g): the top's moment about its axis, reduced by the whole molecule's."""
    m = np.array([MASS[s] for s in symbols])
    x = geom_bohr.reshape(-1, 3) * BOHR_ANGSTROM
    x = x - (m[:, None] * x).sum(0) / m.sum()
    inertia = sum(mi * (np.dot(r, r) * np.eye(3) - np.outer(r, r)) for mi, r in zip(m, x, strict=True))
    moments, axes = np.linalg.eigh(inertia)
    k = x[AXIS[1]] - x[AXIS[0]]
    k = k / np.linalg.norm(k)
    i_alpha = sum(m[h] * np.sum(np.cross(k, x[h] - x[AXIS[1]]) ** 2) for h in TOP)
    lam = axes.T @ k
    i_r = i_alpha * (1 - np.sum(lam**2 * i_alpha / moments))
    return float(ROT_CONST_AMU_A2_CM / i_r)


def torsion_levels(F: float, v3: float, v6: float, m_max: int = FREE_ROTOR_M) -> np.ndarray:
    """Eigenvalues (cm⁻¹, ascending) of −F d²/dτ² + V3/2 (1 − cos 3τ) + V6/2 (1 − cos 6τ) in the free-rotor basis |m| ≤ m_max."""
    ms = np.arange(-m_max, m_max + 1)
    H = np.diag(F * ms.astype(float) ** 2 + v3 / 2 + v6 / 2)
    for shift, v in ((3, v3), (6, v6)):
        H += np.diag(np.full(len(ms) - shift, -v / 4), shift) + np.diag(np.full(len(ms) - shift, -v / 4), -shift)
    return np.linalg.eigvalsh(H)


def read_scan(scan_dir: Path) -> dict:
    """Part A by its registered line."""
    recs = sorted((json.loads(p.read_text(encoding="utf-8")) for p in scan_dir.glob("scan_k*.json")), key=lambda r: r["k"])
    if [r["k"] for r in recs] != list(range(13)):
        raise SystemExit(f"{scan_dir}: scan points {[r['k'] for r in recs]}, expected 0..12")
    e = np.array([r["energy"] for r in recs]) * HARTREE_CM
    e = e - e[0]
    tau = np.radians([(r["achieved_deg"] - r["tau0_deg"]) % 360.0 for r in recs])
    periodic = float(abs(e[12] - e[0]))
    v3, v6, c = fit_v3_v6(tau[:12], e[:12])
    ref = recs[0]
    F = internal_rotation_constant(ref["symbols"], np.array(ref["geometry_bohr"]))
    lv = torsion_levels(F, v3, v6)
    res = {"energies_cm": e.tolist(), "tau_deg": np.degrees(tau).tolist(), "periodicity_cm": periodic, "V3_cm": v3, "V6_cm": v6,
           "fit_rms_cm": float(np.sqrt(np.mean((c + v3 * (1 - np.cos(3 * tau[:12])) / 2 + v6 * (1 - np.cos(6 * tau[:12])) / 2 - e[:12]) ** 2))),
           "F_cm": F, "torsional_fundamental_cm": float(lv[3:6].mean() - lv[0:3].mean()), "ground_splitting_cm": float(lv[2] - lv[0]),
           "V3_from_harmonic_108_cm": float((108.0 / 3) ** 2 / F), "microwave_V3_cm": MICROWAVE_V3_CM}
    off = (v3 - MICROWAVE_V3_CM) / MICROWAVE_V3_CM
    if periodic > PERIODIC_CM:
        res["verdict"] = f"scan not converged (|E(120°) − E(0°)| = {periodic:.2f} cm⁻¹ > {PERIODIC_CM}); no verdict"
    elif abs(off) <= V3_TOLERANCE:
        res["verdict"] = f"B3LYP's barrier within 15 % of the microwave value ({100 * off:+.1f} %)"
    else:
        res["verdict"] = f"B3LYP's barrier off by {100 * off:+.1f} %"
    return res


# ---------------------------------------------------------------------------------------------------------------------- part B


def fourier_dvr_kinetic(n: int) -> np.ndarray:
    """−d²/dτ² on n equally spaced points over 2π (periodic sinc DVR, n even; Colbert & Miller 1992)."""
    if n % 2:
        raise ValueError("the periodic DVR here needs an even number of points")
    d = np.subtract.outer(np.arange(n), np.arange(n))
    with np.errstate(divide="ignore", invalid="ignore"):
        T = (-1.0) ** d / (2 * np.sin(np.pi * d / n) ** 2)
    T[np.arange(n), np.arange(n)] = n**2 / 12 + 1 / 6
    return T


def ho_dvr(n: int, omega: float) -> tuple[np.ndarray, np.ndarray]:
    """Nodes (the Gauss–Hermite points) and (ω/2)(−d²/dq²) of the reduced coordinate in the harmonic-oscillator DVR."""
    k = np.arange(1, n)
    qmat = np.diag(np.sqrt(k / 2), 1) + np.diag(np.sqrt(k / 2), -1)
    nodes, U = np.linalg.eigh(qmat)
    nn = np.arange(n)
    off = np.sqrt((nn[:-2] + 1) * (nn[:-2] + 2)) / 2
    p2 = np.diag(nn + 0.5) - np.diag(off, 2) - np.diag(off, -2)   # p² in the first n oscillator functions (the DVR's finite basis)
    return nodes, U.T @ (omega / 2 * p2) @ U


def dvr_states(V: np.ndarray, F: float, omega: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues and eigenvectors of the product-DVR Hamiltonian on V (n_τ, n_q, n_q), cm⁻¹."""
    nt, nq, _ = V.shape
    Tt = F * fourier_dvr_kinetic(nt)
    T1 = ho_dvr(nq, omega[0])[1]
    T2 = ho_dvr(nq, omega[1])[1]
    It, Iq = np.eye(nt), np.eye(nq)
    H = np.kron(np.kron(Tt, Iq), Iq) + np.kron(np.kron(It, T1), Iq) + np.kron(np.kron(It, Iq), T2) + np.diag(V.ravel())
    return np.linalg.eigh(H)


def separable_bases(V: np.ndarray, F: float, omega: tuple[float, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The 1D eigenvectors of the separable surface: τ on V(τ, 0, 0), each bend on its cut through τ₀ with the other bend at 0."""
    nt, nq, _ = V.shape
    c = nq // 2
    Ut = np.linalg.eigh(F * fourier_dvr_kinetic(nt) + np.diag(V[:, c, c]))[1]
    U1 = np.linalg.eigh(ho_dvr(nq, omega[0])[1] + np.diag(V[0, :, c]))[1]
    U2 = np.linalg.eigh(ho_dvr(nq, omega[1])[1] + np.diag(V[0, c, :]))[1]
    return Ut, U1, U2


def bend_fundamentals(V: np.ndarray, F: float, omega: tuple[float, float]) -> dict:
    """ν₂₀ and ν₂₁ (cm⁻¹): the lowest states whose largest torsional-ground character is (1, 0) or (0, 1), against the ground state."""
    E, psi = dvr_states(V, F, omega)
    Ut, U1, U2 = separable_bases(V, F, omega)
    nt, nq, _ = V.shape
    labels = {(0, 0): None, (1, 0): None, (0, 1): None}
    chars = {}
    for s in np.flatnonzero(E - E[0] < max(omega) + BEND_WINDOW_CM):
        c = np.einsum("tab,ti,aj,bk->ijk", psi[:, s].reshape(nt, nq, nq), Ut[:, :3], U1[:, :2], U2[:, :2])
        w = {lab: float(np.sum(c[:, lab[0], lab[1]] ** 2)) for lab in labels}
        best = max(w, key=w.get)
        if labels[best] is None and w[best] >= MIN_CHARACTER:
            labels[best], chars[best] = s, w[best]
    if any(v is None for v in labels.values()):
        raise ValueError(f"no state with character ≥ {MIN_CHARACTER} for {[k for k, v in labels.items() if v is None]}")
    g = E[labels[(0, 0)]]
    return {"nu20": float(E[labels[(1, 0)]] - g), "nu21": float(E[labels[(0, 1)]] - g),
            "characters": {f"{k[0]}{k[1]}": v for k, v in chars.items()}}


def no_torsion_coupling(V: np.ndarray) -> np.ndarray:
    """V_nt(τ, q) = V(τ, 0, 0) + V(τ₀, q₂₀, q₂₁) − V₀: the bend–bend coupling kept, the torsion's coupling to the bends removed."""
    c = V.shape[1] // 2
    return V[:, c, c][:, None, None] + V[0][None, :, :] - V[0, c, c]


def coupling_shifts(V: np.ndarray, F: float, omega: tuple[float, float]) -> dict:
    """Δ_var,i = ν_i(V_full) − ν_i(V_nt) and both sets of ν."""
    full = bend_fundamentals(V, F, omega)
    nt = bend_fundamentals(no_torsion_coupling(V), F, omega)
    return {"full": full, "no_torsion_coupling": nt, "delta20": full["nu20"] - nt["nu20"], "delta21": full["nu21"] - nt["nu21"]}


def grid_potential(grid_dir: Path) -> tuple[np.ndarray, dict]:
    """V (n_τ, n_q, n_q) in cm⁻¹ above its minimum, from grid.json and the lanes' energies; a missing point stops the read."""
    meta = json.loads((grid_dir / "grid.json").read_text(encoding="utf-8"))
    E: dict[str, float] = {}
    for f in sorted(grid_dir.glob("energies_lane*.json")):
        E |= json.loads(f.read_text(encoding="utf-8"))
    V = np.full((meta["n_tau"], meta["n_q"], meta["n_q"]), np.nan)
    for p in meta["points"]:
        if str(p["index"]) not in E:
            raise SystemExit(f"{grid_dir}: point {p['index']} has no energy")
        V[p["k_tau"], p["i20"], p["i21"]] = E[str(p["index"])]
    V = (V - np.nanmin(V)) * HARTREE_CM
    return V, meta


def full_dimension_delta(coords: str, modes: tuple[int, int]) -> dict[int, float]:
    """ν_i(all modes) − ν_i(torsion out) of TASKS 173's Psience runs in one coordinate set ('cart' or 'zmat'), cm⁻¹."""
    nu = {tag: json.loads((BRIDGE / f"bridge_4mi_{coords}{tag}.json").read_text(encoding="utf-8"))["nu_psience_cm"] for tag in ("", "_dec")}
    return {i: nu[""][i] - nu["_dec"][i] for i in modes}


def read_grid(grid_dir: Path, scan_read: dict) -> dict:
    """Part B by its registered line (with amendment 1)."""
    V, meta = grid_potential(grid_dir)
    F = scan_read["F_cm"]
    omega = tuple(meta["omega_cm"])
    b20, b21 = meta["bends"]
    shifts = coupling_shifts(V, F, omega)
    sub = coupling_shifts(V[::2], F, omega)
    conv = max(abs(sub["delta20"] - shifts["delta20"]), abs(sub["delta21"] - shifts["delta21"]))
    d_vpt2 = {coords: full_dimension_delta(coords, (b20, b21)) for coords in ("cart", "zmat")}
    res = {"F_cm": F, "omega_cm": list(omega), "variational": shifts, "tau_subset_12": sub, "convergence_cm": conv,
           "delta_vpt2_full_dimension": {c: {str(k): v for k, v in d.items()} for c, d in d_vpt2.items()}}
    dv = (shifts["delta20"], shifts["delta21"])
    if conv > CONVERGED_CM:
        res["verdict"] = f"not converged (12-point τ subset moves Δ_var by {conv:.2f} cm⁻¹ > {CONVERGED_CM}); no verdict"
    elif all(abs(dv[n] - d_vpt2[c][b]) <= AGREE_CM for c in d_vpt2 for n, b in enumerate((b20, b21))):
        res["verdict"] = "VPT2's torsion–bend coupling holds variationally: a hindered methyl keeps its coupled VPT2 value"
    elif abs(dv[0]) <= AGREE_CM and all(d_vpt2[c][b20] >= SPURIOUS_VPT2_CM for c in d_vpt2):
        res["verdict"] = "VPT2's torsion–bend coupling is spurious here: decouple a hindered methyl"
    else:
        res["verdict"] = "neither branch; reported as it is, no verdict"
    return res


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="part", required=True)
    s = sub.add_parser("scan")
    s.add_argument("scan_dir")
    s.add_argument("--out", required=True)
    g = sub.add_parser("grid")
    g.add_argument("grid_dir")
    g.add_argument("--scan", required=True)
    g.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.part == "scan":
        res = read_scan(Path(a.scan_dir))
    else:
        load = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
        res = read_grid(Path(a.grid_dir), load(a.scan))
    out = Path(a.out)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(res, indent=1), encoding="utf-8")
    tmp.replace(out)
    print(res["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
