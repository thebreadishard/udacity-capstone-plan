"""Gate consistency arithmetic for Round-2 blocking issue 8.

The Distilled Plan states artifact tolerances in Hartree and the Phase 1
acceptance gate in meV/A, and then feeds the artifacts back into the Phase 1
gate as a "noise floor". This script does the unit algebra that shows the
resulting gate is self-loosening, and derives a coherent replacement set.

Key conversion. A grid artifact that is periodic over one cell, with
peak-to-peak energy amplitude A and period dx, implies a peak force artifact

    max |dE/dx| = pi * A / dx

so an artifact tolerance quoted in Hartree is a force tolerance in disguise,
and the two must be quoted together or not at all.

Run: python probes/issue08_gate_consistency.py
"""

from __future__ import annotations

HARTREE_EV = 27.211386245988
BOHR_ANG = 0.529177210903
KB_HA_PER_K = 3.166811563e-6

MEV_PER_HA = HARTREE_EV * 1000.0


def eggbox_energy_to_force(amplitude_ha: float, dx_ang: float) -> tuple[float, float]:
    """Peak force artifact implied by a cell-periodic energy artifact."""
    force_ha_per_ang = 3.141592653589793 * amplitude_ha / dx_ang
    return force_ha_per_ang * BOHR_ANG, force_ha_per_ang * MEV_PER_HA


def force_to_eggbox_energy(force_mev_per_ang: float, dx_ang: float) -> float:
    """Energy artifact tolerance implied by a force artifact budget."""
    force_ha_per_ang = force_mev_per_ang / MEV_PER_HA
    return force_ha_per_ang * dx_ang / 3.141592653589793


def au_to_mev_per_ang(force_au: float) -> float:
    return force_au * MEV_PER_HA / BOHR_ANG


def mev_per_ang_to_au(force_mev_per_ang: float) -> float:
    return force_mev_per_ang * BOHR_ANG / MEV_PER_HA


def drift_gate(n_atoms: int, temperature_k: float, trajectory_ps: float, fraction: float):
    """Drift budget from the vibrational energy the trajectory is supposed to hold."""
    e_vib = (3 * n_atoms - 6) * KB_HA_PER_K * temperature_k
    total = fraction * e_vib
    return e_vib, total, total / trajectory_ps


def main() -> None:
    dx = 0.20
    phase1_target_mev = 1.0
    current_eggbox_ha = 1.0e-4
    current_fd_gate_au = 1.0e-5
    current_drift_ha_per_ps = 1.0e-5

    print("=" * 74)
    print("A. The current gates, in one unit")
    print("=" * 74)
    eb_au, eb_mev = eggbox_energy_to_force(current_eggbox_ha, dx)
    print(f"  Phase 0 egg-box    <= {current_eggbox_ha:8.1e} Ha   over dx = {dx} A")
    print(f"      implied force  =  {eb_au:8.2e} a.u. = {eb_mev:10.1f} meV/A")
    print(f"  Phase 0 FD check   <= {current_fd_gate_au:8.1e} a.u. = {au_to_mev_per_ang(current_fd_gate_au):10.3f} meV/A")
    print(f"  Phase 1 target     <= {phase1_target_mev:8.1f} meV/A")
    print()
    print(f"  egg-box force artifact / Phase 0 FD gate : {eb_mev / au_to_mev_per_ang(current_fd_gate_au):10.1f} x")
    print(f"  egg-box force artifact / Phase 1 target  : {eb_mev / phase1_target_mev:10.1f} x")
    print()
    noise_floor = max(eb_mev, au_to_mev_per_ang(current_fd_gate_au))
    effective = max(phase1_target_mev, 3.0 * noise_floor)
    print("  Phase 1 gate is max(1 meV/A, 3 x noise floor), and the plan defines")
    print("  the noise floor to include the egg-box force residual, so:")
    print(f"      noise floor        = {noise_floor:10.1f} meV/A")
    print(f"      effective gate     = {effective:10.1f} meV/A   <-- self-loosened by {effective / phase1_target_mev:.0f}x")
    print()

    print("=" * 74)
    print("B. Proposed: derive the artifact budget from the acceptance gate")
    print("=" * 74)
    safety = 10.0
    ceiling_mev = phase1_target_mev / safety
    print(f"  Phase 1 acceptance gate                   : {phase1_target_mev:8.2f} meV/A")
    print(f"  Safety factor (artifact must not dominate): {safety:8.0f} x")
    print(f"  => total engine artifact ceiling          : {ceiling_mev:8.2f} meV/A"
          f"  ({mev_per_ang_to_au(ceiling_mev):.2e} a.u.)")
    print()
    print("  Back-converted egg-box energy tolerance:")
    print(f"{'dx (A)':>8} {'A_max (Ha)':>14} {'A_max (meV)':>14} {'vs current 1e-4 Ha':>20}")
    for dx_i in (0.15, 0.20, 0.25, 0.30):
        a_max = force_to_eggbox_energy(ceiling_mev, dx_i)
        print(
            f"{dx_i:8.2f} {a_max:14.2e} {a_max * MEV_PER_HA:14.2e}"
            f" {current_eggbox_ha / a_max:19.0f}x tighter"
        )
    print()
    fd_gate_mev = ceiling_mev / 2.0
    print(f"  Autograd-vs-FD gate (float64, must sit below the ceiling):")
    print(f"      {fd_gate_mev:.3f} meV/A = {mev_per_ang_to_au(fd_gate_mev):.2e} a.u."
          f"  (current: {current_fd_gate_au:.0e} a.u.)")
    print("      NOTE: this check cannot see the egg-box. Autograd and finite")
    print("      differences read the same corrupted E and agree on a wrong force.")
    print()

    print("=" * 74)
    print("C. Energy drift, stated over the production trajectory")
    print("=" * 74)
    for n_atoms, label, ps in ((3, "H2O", 50.0), (12, "C6H6", 20.0)):
        e_vib, total, rate = drift_gate(n_atoms, 300.0, ps, 0.01)
        print(f"  {label:5s} {ps:5.1f} ps, 300 K: E_vib = {e_vib:.3e} Ha,"
              f" 1% budget = {total:.2e} Ha => {rate:.2e} Ha/ps")
    _, _, h2o_rate = drift_gate(3, 300.0, 50.0, 0.01)
    print(f"\n  current gate {current_drift_ha_per_ps:.0e} Ha/ps is {current_drift_ha_per_ps / h2o_rate:.0f}x"
          f" looser than a 1% budget over a 50 ps H2O run")
    print(f"  (at {current_drift_ha_per_ps:.0e} Ha/ps the 50 ps drift is"
          f" {100 * current_drift_ha_per_ps * 50.0 / drift_gate(3, 300.0, 50.0, 1.0)[0]:.0f}%"
          f" of the vibrational energy the trajectory is supposed to hold)")
    print()

    print("=" * 74)
    print("D. Is the proposed ceiling reachable?")
    print("=" * 74)
    measured_scheme_b = 1.7405e-03  # probes/issue07_grid_representability.py, dx = 0.20 A
    measured_scheme_a = 1.5868e06
    print(f"  measured, full rho on grid   : {measured_scheme_a:.2e} meV/A"
          f"  -> ceiling missed by {measured_scheme_a / ceiling_mev:.1e}x")
    print(f"  measured, deformation only   : {measured_scheme_b:.2e} meV/A"
          f"  -> {ceiling_mev / measured_scheme_b:.0f}x headroom")
    print("\n  The issue-7 reference split is what makes the issue-8 ceiling reachable.")
    print("  Under the old representation the tightened gate was unreachable by")
    print(f"  {measured_scheme_a / ceiling_mev:.0e}x, which is why the loose Hartree tolerance")
    print("  survived unchallenged.")


if __name__ == "__main__":
    main()
