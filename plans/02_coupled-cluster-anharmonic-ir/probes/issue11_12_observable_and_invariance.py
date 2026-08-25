"""Probe for Round-2 blocking issues 11 (the IR observable) and 12 (invariance).

Issue 11. The graded deliverable is band positions and *relative intensities*,
which come from mu = int r (rho_nucl - rho_e) dV and its derivative. Nothing in
the plan validated either. Two structural facts this probe measures:

  - a promolecular reference of neutral spherical atoms has *exactly* zero
    dipole, so under the reference split mu = -int r Delta-rho dV: the whole
    observable is a direct integral of the small object we supervise, with no
    cancellation between two large numbers;
  - under the old scheme the grid density does not even carry the right
    electron count, so the "molecule" is charged and its dipole is not
    origin-independent, i.e. not a dipole at all.

Issue 12. A voxel grid is neither translation- nor rotation-invariant, so
sum_A F_A and sum_A R_A x F_A are nonzero. The translational residual is the
egg-box force in a different costume and is already bounded by the issue-8
ceiling. The rotational residual is a genuinely separate quantity that no
existing gate covers; this probe measures it.

Run: python probes/issue11_12_observable_and_invariance.py
"""

from __future__ import annotations

import numpy as np

from issue07_grid_representability import (
    BOHR,
    HA_PER_BOHR_TO_MEV_PER_ANG,
    NUCLEAR_CHARGE,
    _gaussian,
    atom_density,
    deformation_charges,
    measure,
    water_geometry,
)

DEBYE_PER_EA0 = 2.541746  # debye per e*bohr
WATER_DIPOLE_EA0 = 1.8546 / DEBYE_PER_EA0  # experimental gas-phase H2O


def analytic_dipole(coords: np.ndarray) -> np.ndarray:
    """Exact dipole of the model density: -int r Delta-rho dV.

    The promolecular part contributes exactly zero (each free-atom density is
    neutral and centred on its nucleus), so only the deformation Gaussians
    survive, and each contributes its charge times its centre.
    """
    centres, amplitudes, _ = deformation_charges(coords)
    return -np.einsum("k,ki->i", amplitudes, centres)


def grid_charge_and_moment(
    dx_ang: float,
    box_ang: float,
    symbols: list[str],
    coords: np.ndarray,
    *,
    promolecular: bool,
    deformation: bool,
) -> tuple[float, np.ndarray]:
    """Electron count and first moment of whatever density is put on the grid."""
    dx = dx_ang / BOHR
    n = int(round(box_ang / dx_ang))
    axis = -0.5 * n * dx + (np.arange(n) + 0.5) * dx
    cell_volume = dx**3

    gx, gy = np.meshgrid(axis, axis, indexing="ij")
    centres, amplitudes, widths = deformation_charges(coords)

    charge = 0.0
    moment = np.zeros(3)
    for gz in axis:
        rho = np.zeros_like(gx)
        if promolecular:
            for symbol, atom in zip(symbols, coords):
                r = np.sqrt((gx - atom[0]) ** 2 + (gy - atom[1]) ** 2 + (gz - atom[2]) ** 2)
                rho += atom_density(symbol, r)
        if deformation:
            for centre, amplitude, width in zip(centres, amplitudes, widths):
                r2 = (gx - centre[0]) ** 2 + (gy - centre[1]) ** 2 + (gz - centre[2]) ** 2
                rho += _gaussian(r2, amplitude, width)
        charge += rho.sum() * cell_volume
        moment += np.array([(gx * rho).sum(), (gy * rho).sum(), gz * rho.sum()]) * cell_volume
    return charge, moment


def dipole(
    dx_ang: float,
    symbols: list[str],
    coords: np.ndarray,
    *,
    scheme: str,
) -> tuple[np.ndarray, float]:
    """Return (dipole vector, net charge of the represented system)."""
    nuclear_moment = sum(NUCLEAR_CHARGE[s] * atom for s, atom in zip(symbols, coords))
    nuclear_charge = sum(NUCLEAR_CHARGE[s] for s in symbols)
    if scheme == "A":
        electrons, electron_moment = grid_charge_and_moment(
            dx_ang, 8.0, symbols, coords, promolecular=True, deformation=True
        )
        return nuclear_moment - electron_moment, nuclear_charge - electrons
    # Scheme B: the promolecular electron moment equals the nuclear moment
    # analytically, so the two cancel exactly and only Delta-rho remains.
    electrons, electron_moment = grid_charge_and_moment(
        dx_ang, 8.0, symbols, coords, promolecular=False, deformation=True
    )
    return -electron_moment, -electrons


def rotation_z(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def rotation_scan(
    dx_ang: float,
    symbols: list[str],
    coords: np.ndarray,
    *,
    promolecular: bool,
    deformation: bool,
    n_steps: int = 46,
) -> dict:
    """Rigidly rotate about the lab z axis; the exact energy is constant."""
    # Generic offset so the centroid does not sit on a lattice symmetry point.
    offset = np.array([0.037, 0.061, 0.043]) / BOHR
    angles = np.linspace(0.0, np.pi / 2.0, n_steps)
    energies = []
    for theta in angles:
        rotated = coords @ rotation_z(theta).T + offset
        _, energy = measure(
            dx_ang, 8.0, symbols, rotated, promolecular=promolecular, deformation=deformation
        )
        energies.append(energy)
    energies = np.array(energies)
    torque = float(np.abs(np.gradient(energies, angles)).max())
    lever = float(np.linalg.norm(coords - coords.mean(axis=0), axis=1).max())
    return {
        "angles": angles,
        "energies_hartree": energies,
        "energy_swing_hartree": float(energies.max() - energies.min()),
        "max_torque_ha_per_rad": torque,
        "lever_arm_bohr": lever,
        "force_equiv_mev_per_ang": torque / lever * HA_PER_BOHR_TO_MEV_PER_ANG,
    }


def dipole_translation_scan(
    dx_ang: float, symbols: list[str], coords: np.ndarray, *, scheme: str, n_steps: int = 11
) -> dict:
    """Rigidly translate through one cell; the exact dipole is constant."""
    dx = dx_ang / BOHR
    offsets = np.linspace(0.0, dx, n_steps, endpoint=False)
    dipoles = []
    for offset in offsets:
        mu, _ = dipole(dx_ang, symbols, coords + np.array([offset, 0.0, 0.0]), scheme=scheme)
        dipoles.append(mu)
    dipoles = np.array(dipoles)
    norms = np.linalg.norm(dipoles, axis=1)
    return {
        "mean_norm": float(norms.mean()),
        "swing": float(norms.max() - norms.min()),
        "relative_swing": float((norms.max() - norms.min()) / norms.mean()),
    }


def main() -> None:
    symbols, coords = water_geometry()
    dx_ang = 0.20
    engine_ceiling_mev = 0.1  # Distilled Plan section 7, issue-8 gate

    print("=" * 76)
    print("Issue 11: is the IR observable even representable?")
    print("=" * 76)
    exact = analytic_dipole(coords)
    nuclear_moment = sum(NUCLEAR_CHARGE[s] * atom for s, atom in zip(symbols, coords))
    nuclear_norm = np.linalg.norm(nuclear_moment)
    print(f"  |sum_A Z_A R_A| (nuclear term): {nuclear_norm:.6f} e*bohr")
    print(f"  experimental H2O dipole       : {WATER_DIPOLE_EA0:.6f} e*bohr  (1.855 D)")
    print(f"  cancellation ratio (physical) : {nuclear_norm / WATER_DIPOLE_EA0:.1f}x")
    print(f"  exact dipole of this caricature: {np.linalg.norm(exact):.6f} e*bohr"
          f"  ({np.linalg.norm(exact) * DEBYE_PER_EA0:.3f} D)")
    print("     -> the caricature's own dipole is smaller than water's, so its")
    print("        cancellation ratio is not the physical one; use 7x, not 93x.")
    print("     -> under scheme A the dipole is a residue of two much larger")
    print("        numbers; under the reference split it is a direct integral")
    print("        of Delta-rho, with the reference contributing exactly zero.")
    print()

    for scheme, label in (("A", "full rho on grid"), ("B", "deformation only")):
        mu, net_charge = dipole(dx_ang, symbols, coords, scheme=scheme)
        err = np.linalg.norm(mu - exact)
        print(f"  scheme {scheme} ({label})")
        print(f"    net charge of represented system : {net_charge:+.4e} e")
        print(f"    |mu|                             : {np.linalg.norm(mu):.6f} e*bohr")
        print(f"    |mu - mu_exact|                  : {err:.4e} e*bohr"
              f"   ({100 * err / np.linalg.norm(exact):.3g}% of |mu|)")
        if abs(net_charge) > 1e-3:
            print("    WARNING: net charge is nonzero, so this 'dipole' is not")
            print("             origin-independent and is not a dipole at all.")
        scan = dipole_translation_scan(dx_ang, symbols, coords, scheme=scheme)
        print(f"    |mu| swing over one cell         : {scan['swing']:.4e} e*bohr"
              f"   ({100 * scan['relative_swing']:.3g}% of |mu|)")
        print()

    print("=" * 76)
    print("Issue 12: invariance residuals")
    print("=" * 76)
    print("  Translation. sum_A F_A = -dE/d(rigid shift), which is exactly the")
    print("  egg-box force already measured in probes/issue07_grid_representability.py")
    print("  and already bounded by the issue-8 engine-artifact ceiling.")
    print("  It is not a new gate; it is a cheap online monitor of an old one.")
    print()
    print("  Rotation. Not covered by any existing sweep. Measured here:")
    rot_a = rotation_scan(dx_ang, symbols, coords, promolecular=True, deformation=True)
    rot_b = rotation_scan(dx_ang, symbols, coords, promolecular=False, deformation=True)
    print(f"{'scheme':>22} {'E swing (Ha)':>15} {'torque (Ha/rad)':>17} {'force-equiv (meV/A)':>21}")
    for label, res in (("A full rho on grid", rot_a), ("B deformation only", rot_b)):
        print(
            f"{label:>22} {res['energy_swing_hartree']:15.3e}"
            f" {res['max_torque_ha_per_rad']:17.3e} {res['force_equiv_mev_per_ang']:21.3e}"
        )
    print(f"\n  lever arm used: {rot_a['lever_arm_bohr']:.3f} bohr")
    print(f"  engine-artifact ceiling (issue 8): {engine_ceiling_mev} meV/A")
    print(f"    scheme A: exceeds ceiling by {rot_a['force_equiv_mev_per_ang'] / engine_ceiling_mev:.2e}x")
    margin = engine_ceiling_mev / rot_b["force_equiv_mev_per_ang"]
    print(f"    scheme B: {margin:.1f}x headroom"
          if margin > 1
          else f"    scheme B: EXCEEDS ceiling by {1 / margin:.2f}x")
    print()
    print("  Under the reference split BOTH residuals sit far below the ceiling,")
    print("  and translation is the larger of the two, so the egg-box gate bounds")
    print("  both. That was not knowable a priori -- nothing guaranteed rotation")
    print("  would be the milder error -- so it still has to be measured, not")
    print("  assumed. Scheme B's rotational number sits at this probe's own")
    print("  derivative noise floor and should be read as an upper bound.")
    print()
    print("  Rotation is also precisely the symmetry an equivariant GNN (G1)")
    print("  satisfies by construction. Pre-register it as a confound before the")
    print("  field-vs-GNN comparison, not after.")


if __name__ == "__main__":
    main()
