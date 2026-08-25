"""Numerical probe for Round-2 blocking issue 7.

Question: can a Delta x ~ 0.2 A voxel grid carry an all-electron molecular
density well enough for the Distilled Plan's E_es and its 0.01% charge-integral
requirement (section 8, item 9)?

Method: build an all-electron model density for H2O from Clementi-Raimondi
Slater orbitals (exact cusps, exact electron count, no SCF needed), then measure
on a uniform grid:

  1. electron-count quadrature error vs grid spacing;
  2. the egg-box artifact -- rigidly translating the molecule through one grid
     cell must not change any energy, so every observed change is pure
     discretization error;
  3. the same two quantities under the proposed reference split, where the
     promolecular part is handled analytically and only the smooth deformation
     density touches the grid.

This is a model-density probe, not a CCSD one. It exists to settle the spec
question before the PySCF campaign is designed. The equivalent measurement on a
real CCSD 1-RDM cube remains a Phase 0 deliverable.

Run: python probes/issue07_grid_representability.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.special import erf

BOHR = 0.52917721067  # angstrom per bohr
HA_PER_BOHR_TO_MEV_PER_ANG = 27211.386 / BOHR

# Clementi-Raimondi effective exponents, bohr^-1: (n, zeta, occupancy)
SHELLS = {
    "H": [(1, 1.0000, 1)],
    "O": [(1, 7.6579, 2), (2, 2.2458, 2), (2, 2.2266, 4)],
}
NUCLEAR_CHARGE = {"H": 1.0, "O": 8.0}


def _sto_radial_squared(n: int, zeta: float, r: np.ndarray) -> np.ndarray:
    if n == 1:
        radial = 2.0 * zeta**1.5 * np.exp(-zeta * r)
    elif n == 2:
        radial = (2.0 * zeta) ** 2.5 / np.sqrt(24.0) * r * np.exp(-zeta * r)
    else:
        raise ValueError(f"unsupported principal quantum number {n}")
    return radial * radial


def atom_density(symbol: str, r: np.ndarray) -> np.ndarray:
    """Spherically averaged free-atom density in electrons/bohr^3."""
    total = np.zeros_like(r)
    for n, zeta, occ in SHELLS[symbol]:
        total += occ * _sto_radial_squared(n, zeta, r)
    return total / (4.0 * np.pi)


def water_geometry() -> tuple[list[str], np.ndarray]:
    """Experimental gas-phase H2O, centred on the nuclear centroid, in bohr."""
    bond = 0.9572 / BOHR
    half_angle = np.deg2rad(104.52) / 2.0
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [bond * np.sin(half_angle), 0.0, bond * np.cos(half_angle)],
            [-bond * np.sin(half_angle), 0.0, bond * np.cos(half_angle)],
        ]
    )
    return ["O", "H", "H"], coords - coords.mean(axis=0)


def deformation_charges(
    coords: np.ndarray, width_bond_ang: float = 0.35
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A charge-neutral bond-accumulation / atom-depletion caricature.

    Amplitude (~0.2 e/A^3 peak) and width are chosen to match published
    deformation-density maps; only its smoothness matters for this probe.
    """
    q = 0.15
    width_bond = width_bond_ang / BOHR
    width_atom = max(0.55 / BOHR, 1.5 * width_bond)
    centres = [(coords[0] + coords[1]) / 2.0, (coords[0] + coords[2]) / 2.0]
    amplitudes = [q, q]
    widths = [width_bond, width_bond]
    for atom in coords:
        centres.append(atom)
        amplitudes.append(-2.0 * q / 3.0)
        widths.append(width_atom)
    return np.array(centres), np.array(amplitudes), np.array(widths)


def _gaussian(r2: np.ndarray, charge: float, width: float) -> np.ndarray:
    return charge * (2.0 * np.pi * width * width) ** -1.5 * np.exp(-r2 / (2.0 * width * width))


def measure(
    dx_ang: float,
    box_ang: float,
    symbols: list[str],
    coords: np.ndarray,
    *,
    promolecular: bool,
    deformation: bool,
    deform_width_ang: float = 0.35,
) -> tuple[float, float]:
    """Return (electron count on the grid, smeared electron-nuclear energy).

    Both are computed with the midpoint rule. `promolecular`/`deformation`
    select which pieces of the density are placed on the grid; the nuclear
    kernel is always the sigma = 1.5*dx Hockney-Eastwood-compatible smeared form
    required by Distilled Plan section 6.1.
    """
    dx = dx_ang / BOHR
    n = int(round(box_ang / dx_ang))
    axis = -0.5 * n * dx + (np.arange(n) + 0.5) * dx
    sigma = 1.5 * dx
    cell_volume = dx**3

    gx, gy = np.meshgrid(axis, axis, indexing="ij")
    centres, amplitudes, widths = deformation_charges(coords, deform_width_ang)

    electrons = 0.0
    energy = 0.0
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

        potential = np.zeros_like(gx)
        for symbol, atom in zip(symbols, coords):
            r = np.sqrt((gx - atom[0]) ** 2 + (gy - atom[1]) ** 2 + (gz - atom[2]) ** 2)
            r = np.maximum(r, 1e-12)
            potential -= NUCLEAR_CHARGE[symbol] * erf(r / (np.sqrt(2.0) * sigma)) / r

        electrons += rho.sum() * cell_volume
        energy += (rho * potential).sum() * cell_volume
    return electrons, energy


def spacing_sweep(symbols: list[str], coords: np.ndarray) -> list[dict]:
    rows = []
    for dx_ang in (0.40, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05):
        n_all, _ = measure(dx_ang, 8.0, symbols, coords, promolecular=True, deformation=True)
        n_def, _ = measure(dx_ang, 8.0, symbols, coords, promolecular=False, deformation=True)
        rows.append(
            {
                "dx_angstrom": dx_ang,
                "n_electrons_all_electron": n_all,
                "rel_err_all_electron": abs(n_all - 10.0) / 10.0,
                "n_electrons_deformation": n_def,
                "abs_err_deformation": abs(n_def),
            }
        )
    return rows


def eggbox_scan(
    dx_ang: float,
    symbols: list[str],
    coords: np.ndarray,
    *,
    promolecular: bool,
    deformation: bool,
    n_steps: int = 21,
    deform_width_ang: float = 0.35,
) -> dict:
    """Translate the molecule through one grid cell; exact answer is constant."""
    dx = dx_ang / BOHR
    offsets = np.linspace(0.0, dx, n_steps, endpoint=False)
    electrons, energies = [], []
    for offset in offsets:
        shifted = coords + np.array([offset, 0.0, 0.0])
        n_e, energy = measure(
            dx_ang,
            8.0,
            symbols,
            shifted,
            promolecular=promolecular,
            deformation=deformation,
            deform_width_ang=deform_width_ang,
        )
        electrons.append(n_e)
        energies.append(energy)

    electrons = np.array(electrons)
    energies = np.array(energies)
    # Periodic derivative: the artifact has period dx by construction.
    gradient = (np.roll(energies, -1) - np.roll(energies, 1)) / (2.0 * (dx / n_steps))
    max_force = float(np.abs(gradient).max())
    return {
        "offsets_bohr": offsets,
        "electrons": electrons,
        "energies_hartree": energies,
        "electron_swing": float(electrons.max() - electrons.min()),
        "energy_swing_hartree": float(energies.max() - energies.min()),
        "max_force_ha_per_bohr": max_force,
        "max_force_mev_per_ang": max_force * HA_PER_BOHR_TO_MEV_PER_ANG,
    }


def width_sensitivity(symbols: list[str], coords: np.ndarray, dx_ang: float) -> list[dict]:
    """How sharp may the deformation density be before the split stops helping?"""
    rows = []
    for ratio in (0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00):
        width_ang = ratio * dx_ang
        result = eggbox_scan(
            dx_ang,
            symbols,
            coords,
            promolecular=False,
            deformation=True,
            deform_width_ang=width_ang,
        )
        rows.append(
            {
                "width_over_dx": ratio,
                "width_angstrom": width_ang,
                "electron_swing": result["electron_swing"],
                "force_mev_per_ang": result["max_force_mev_per_ang"],
            }
        )
    return rows


def peak_amplitudes(symbols: list[str], coords: np.ndarray) -> tuple[float, float]:
    centres, amplitudes, widths = deformation_charges(coords)
    rho_peak = float(atom_density("O", np.array([0.0]))[0])
    fine = np.linspace(-4.0, 4.0, 2001)
    gx, gy = np.meshgrid(fine, fine, indexing="ij")
    best = 0.0
    for gz in np.linspace(-2.0, 2.0, 81):
        slab = np.zeros_like(gx)
        for centre, amplitude, width in zip(centres, amplitudes, widths):
            r2 = (gx - centre[0]) ** 2 + (gy - centre[1]) ** 2 + (gz - centre[2]) ** 2
            slab += _gaussian(r2, amplitude, width)
        best = max(best, float(np.abs(slab).max()))
    return rho_peak, best


def main() -> None:
    symbols, coords = water_geometry()
    dx_ang = 0.20

    print("Issue-7 probe: H2O, Clementi-Roetti-style all-electron model density")
    print(f"box = 8.0 A, nuclear smearing sigma = 1.5*dx, reference dx = {dx_ang} A\n")

    rho_peak, def_peak = peak_amplitudes(symbols, coords)
    print("Peak amplitudes (e/bohr^3)")
    print(f"  all-electron density at the O nucleus : {rho_peak:12.3f}")
    print(f"  deformation density (max |.|)         : {def_peak:12.6f}")
    print(f"  ratio                                 : {rho_peak / def_peak:12.1f}\n")

    print("Electron-count quadrature error vs grid spacing")
    print(f"{'dx (A)':>8} {'N_grid (all-e)':>16} {'rel. err':>12} {'N_grid (deform)':>17} {'abs. err':>12}")
    rows = spacing_sweep(symbols, coords)
    for row in rows:
        print(
            f"{row['dx_angstrom']:8.2f} {row['n_electrons_all_electron']:16.4f}"
            f" {row['rel_err_all_electron']:12.2e} {row['n_electrons_deformation']:17.3e}"
            f" {row['abs_err_deformation']:12.2e}"
        )
    print()

    print(f"Egg-box: rigid translation through one cell at dx = {dx_ang} A")
    scheme_a = eggbox_scan(dx_ang, symbols, coords, promolecular=True, deformation=True)
    scheme_b = eggbox_scan(dx_ang, symbols, coords, promolecular=False, deformation=True)
    for label, result in (("A: full rho on grid", scheme_a), ("B: deformation only", scheme_b)):
        print(f"  {label}")
        print(f"    electron-count swing      : {result['electron_swing']:.4e} e")
        print(f"    E_ne swing                : {result['energy_swing_hartree']:.4e} Ha")
        print(
            f"    implied force artifact    : {result['max_force_ha_per_bohr']:.4e} a.u."
            f"  ({result['max_force_mev_per_ang']:.4e} meV/A)"
        )
    ratio = scheme_a["max_force_mev_per_ang"] / max(scheme_b["max_force_mev_per_ang"], 1e-30)
    print(f"\n  scheme A / scheme B force artifact ratio : {ratio:.3e}")

    print(f"\nScheme B sensitivity: how sharp may the deformation density be? (dx = {dx_ang} A)")
    print(f"{'w/dx':>6} {'w (A)':>8} {'N swing (e)':>14} {'force (meV/A)':>16}")
    for row in width_sensitivity(symbols, coords, dx_ang):
        print(
            f"{row['width_over_dx']:6.2f} {row['width_angstrom']:8.2f}"
            f" {row['electron_swing']:14.2e} {row['force_mev_per_ang']:16.2e}"
        )

    out = Path(__file__).with_name("issue07_eggbox_scan.csv")
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scheme", "offset_bohr", "n_electrons", "e_ne_hartree"])
        for label, result in (("A_full_rho", scheme_a), ("B_deformation_only", scheme_b)):
            for offset, n_e, energy in zip(
                result["offsets_bohr"], result["electrons"], result["energies_hartree"]
            ):
                writer.writerow([label, f"{offset:.10f}", f"{n_e:.10f}", f"{energy:.10f}"])
    print(f"\nwrote {out.name}")


if __name__ == "__main__":
    main()
