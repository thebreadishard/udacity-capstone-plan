"""VPT2 fundamentals from a stored semi-numerical force field through Psience, in Cartesian normal modes or in Z-matrix internals
(TASKS 173, software ledger row 55; the user, 4 Nov 2026: 'Ja, pak het zo aan met Psience').

Why: in rectilinear normal coordinates a hindered methyl rotor's cubic and quartic constants are huge and cancel in the coupled
fundamentals; Psience (McCoy group, MIT, `pip install mccoygroup-psience`) runs the same VPT2 in curvilinear internal coordinates,
which decides whether zeroing the torsion's couplings is a correction or an error (`reports/Methylrotor in anharmonische IR.md`).

Input: a folder of qcschema Hessian records (the reference and the ±disp displacements along reduced normal coordinates that
`src/dpir/qff.py` reads). Psience takes the Hessian's derivatives along its own mass-weighted normal modes Q′ ('mixed' derivatives,
as Gaussian writes them to an fchk); ours are along our reduced modes q. The two mode sets are related by T = A⁺ (∂x/∂Q′), which
must be diagonal (a sign and a scale per mode) — the script refuses otherwise, so Psience's mode conventions cannot enter silently.
Upstream example making the same calls: Psience `ci/tests/VPT2Tests.py` (`VPTRunner.run_simple`/`construct` on HOH_freq.fchk, with
and without `internals=[[0,-1,-1,-1],[1,0,-1,-1],[2,0,1,-1]]`).

    ~/psience/bin/python probes/psience_vpt2_bridge.py <hess_dir> --disp 0.10 [--zmatrix '[[0,-1,-1,-1],...]'] --out <json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dpir import qff as Q

OFF_DIAGONAL_LIMIT = 1e-6    # largest |T_kl| / |T_kk| allowed between our modes and Psience's (k ≠ l)
MIXED_MODE = "averaged"      # Psience's mixed-derivative symmetrisation: the mean of the routes, as qff.py assembles φ_iijj


def displaced_hessians(hess_dir: str, disp: float) -> tuple[Q.Harmonic, Q.HessianRecord, dict[int, np.ndarray], dict[int, np.ndarray]]:
    """Our harmonic analysis and the Cartesian Hessians displaced +disp / −disp along each reduced mode, as `qff_from_records` pairs them."""
    recs = Q.load_results(hess_dir)
    i0 = Q.reference_index(recs)
    ref = recs[i0]
    harm = Q.harmonic(ref.H, ref.symbols, ref.geom)
    harm, asg, _ = Q.align_degenerate_subspaces(harm, recs, i0, disp)
    Hp: dict[int, np.ndarray] = {}
    Hn: dict[int, np.ndarray] = {}
    for k, (mode, sign, _dQ, _resid) in asg.items():
        slot = Hp if sign > 0 else Hn
        if mode in slot:
            raise ValueError(f"{recs[k].file}: mode {mode} {'+' if sign > 0 else '−'} is already taken")
        slot[mode] = recs[k].H
    missing = [i for i in range(len(harm.omega)) if i not in Hp or i not in Hn]
    if missing:
        raise ValueError(f"modes without a ± pair: {missing}")
    return harm, ref, Hp, Hn


def psience_molecule(ref: Q.HessianRecord, derivatives: list[np.ndarray], internals: list | None, normal_modes=None):
    """A Psience Molecule at the reference geometry (bohr) with our masses (amu), the given potential derivatives and modes."""
    from Psience.Molecools import Molecule
    masses = [Q.MASS[s] for s in ref.symbols]
    return Molecule(ref.symbols, ref.geom.reshape(-1, 3), masses=masses, potential_derivatives=derivatives, internals=internals,
                    normal_modes=normal_modes)


def vibrational_hessian(ref: Q.HessianRecord) -> np.ndarray:
    """The reference Hessian with translations and rotations projected out (our projector): the stored one leaks a rotation of a few
    cm⁻¹ that Psience would keep as a fourth 'mode' of water."""
    m = Q.atomic_masses_me(ref.symbols)
    sq = np.repeat(np.sqrt(m), 3)
    P = Q.translation_rotation_projector(ref.geom, m)
    F = ref.H / sq[:, None] / sq[None, :]
    return sq[:, None] * (P @ F @ P) * sq[None, :]


def mode_map(harm: Q.Harmonic, xQ: np.ndarray) -> np.ndarray:
    """T[k, l] = ∂q_k/∂Q′_l between our reduced modes q and Psience's modes Q′; refused unless diagonal."""
    T = np.linalg.pinv(harm.A) @ xQ
    d = np.abs(np.diag(T))
    off = np.abs(T - np.diag(np.diag(T)))
    worst = float((off / d[:, None]).max()) if T.size else 0.0
    if not worst <= OFF_DIAGONAL_LIMIT:
        raise ValueError(f"our modes and Psience's are not one-to-one (largest off-diagonal ratio {worst:.2e} > {OFF_DIAGONAL_LIMIT:.0e}); "
                         "a degenerate subspace or a different Hessian/mass set")
    return T


def mixed_derivatives(T: np.ndarray, H0: np.ndarray, Hp: dict[int, np.ndarray], Hn: dict[int, np.ndarray], disp: float) -> list[np.ndarray]:
    """∂H/∂Q′_l (modes, 3N, 3N) and ∂²H/∂Q′_l² on the diagonal of (modes, modes, 3N, 3N), the off-diagonal pairs left zero as in a
    Gaussian fchk (the semi-diagonal force field), by central differences along our modes carried to Psience's modes by T."""
    n = T.shape[0]
    t = np.diag(T)
    third = np.array([t[k] * (Hp[k] - Hn[k]) / (2 * disp) for k in range(n)])
    fourth = np.zeros((n, n, *H0.shape))
    for k in range(n):
        fourth[k, k] = t[k] ** 2 * (Hp[k] + Hn[k] - 2 * H0) / disp**2
    return [third, fourth]


def fundamentals(mol, internals: list | None, n_modes: int, excluded: list[int]) -> np.ndarray:
    """Psience's VPT2 fundamental frequencies (cm⁻¹), no degeneracy handling, in Psience's mode order; the excluded modes are taken
    out of the VPT2 (`mode_selection`, a reduced-dimensional treatment — the decoupling of `qff_noise_diagnosis.py --decouple-below`)
    and come back as NaN."""
    from Psience.VPT2 import VPTRunner
    kept = [k for k in range(n_modes) if k not in excluded]
    selection = {"mode_selection": kept} if excluded else {}
    runner, _ = VPTRunner.construct(mol, 1, internals=internals, mixed_derivative_handling_mode=MIXED_MODE, **selection)
    wfns = runner.get_wavefunctions()
    eng = np.asarray(wfns.energies_to_order())
    states = np.asarray(wfns.corrs.states.excitations)
    if states.shape[1] != len(kept):
        raise ValueError(f"Psience's states span {states.shape[1]} modes, {len(kept)} were kept")
    ground = int(np.flatnonzero(states.sum(1) == 0)[0])
    nu = np.full(n_modes, np.nan)
    for row in np.flatnonzero(states.sum(1) == 1):
        nu[kept[int(np.argmax(states[row]))]] = eng[row] - eng[ground]
    if np.isnan(nu[kept]).any():
        raise ValueError("Psience returned no fundamental for some kept mode")
    return nu * Q.HARTREE_CM


def run(hess_dir: str, disp: float, internals: list | None, excluded: list[int]) -> dict:
    """Our VPT2 and Psience's on one force field, mode by mode."""
    harm, ref, Hp, Hn = displaced_hessians(hess_dir, disp)
    grad = np.zeros(len(ref.geom))
    H_vib = vibrational_hessian(ref)
    base = psience_molecule(ref, [grad, H_vib], None)
    # Psience's own trans/rot projection leaves a −2.4 cm⁻¹ 'mode' on water even for this projected Hessian; without it the three
    # vibrations match ours to 1e-8 cm⁻¹ (4 Nov), so the modes are built unprojected and handed to the molecule that runs VPT2
    modes = base.get_normal_modes(project_transrot=False)
    xQ = np.asarray(modes.coords_by_modes).T   # Psience's axes: (modes, coords)
    if xQ.shape != harm.A.shape:
        raise ValueError(f"Psience finds {xQ.shape[1]} modes, we find {harm.A.shape[1]}")
    T = mode_map(harm, xQ)
    mol = psience_molecule(ref, [grad, H_vib, *mixed_derivatives(T, ref.H, Hp, Hn, disp)], internals, normal_modes=modes)
    w_ps = np.asarray(modes.freqs) * Q.HARTREE_CM
    nu_ps = fundamentals(mol, internals, len(harm.omega), excluded)
    qff, harm_q, ref_q, info = Q.qff_from_records(Q.load_results(hess_dir), disp, allow_noisy=True)
    B = Q.rotational_constants(ref_q.geom, ref_q.symbols)
    zeta = Q.coriolis_zeta(harm_q.q, ref_q.symbols)
    nu_ours, _, _ = Q.vpt2(qff.omega_cm, qff.phi3, qff.phi4, B, zeta, fermi_window=0.0)
    return {"hess_dir": hess_dir, "disp": disp, "internals": internals, "excluded_modes": excluded, "mixed_derivative_handling_mode": MIXED_MODE,
            "omega_ours_cm": qff.omega_cm.tolist(), "omega_psience_cm": w_ps.tolist(), "nu_ours_cm": nu_ours.tolist(),
            "nu_psience_cm": nu_ps.tolist(), "mode_map_diagonal": np.diag(T).tolist(),
            "quartic_route_disagreement_max_cm": info["quartic_route_disagreement_max"]}


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hess_dir")
    ap.add_argument("--disp", type=float, required=True, help="the step of the stored displacements, in reduced normal coordinates")
    ap.add_argument("--zmatrix", default=None, help="Psience internals as JSON rows [atom, bond, angle, dihedral]; omitted: Cartesian")
    ap.add_argument("--exclude-modes", default="", help="comma-separated mode indices taken out of the VPT2 (our ascending-ω order)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    internals = json.loads(args.zmatrix) if args.zmatrix else None
    excluded = [int(k) for k in args.exclude_modes.split(",") if k.strip()]
    rec = run(args.hess_dir, args.disp, internals, excluded)
    tmp = Path(args.out + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    tmp.replace(args.out)
    for k, (wo, wp, no, npk) in enumerate(zip(rec["omega_ours_cm"], rec["omega_psience_cm"], rec["nu_ours_cm"], rec["nu_psience_cm"], strict=True)):
        print(f"mode {k:2d}  ω ours {wo:9.2f}  Psience {wp:9.2f}   ν ours {no:9.2f}  Psience {npk:9.2f}  Δν {npk - no:+7.2f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
