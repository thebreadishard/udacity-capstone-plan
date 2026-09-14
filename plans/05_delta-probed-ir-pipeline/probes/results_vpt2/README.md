# pyVPT2 self-test (2026-09-14, environment `vpt2`: pyVPT2 0.1.2, psi4 1.10.2, qcelemental 0.30.1, qcengine 0.34.2, libxc-c 7.0.0; Windows, 8 threads)

Water, B3LYP/6-31G*, DF-SCF, e/d convergence 1e-10, pyVPT2 defaults (DISP_SIZE 0.05, FD = HESSIAN, FD_ACC 2, FERMI on). Result schema saved as `water_b3lyp_631gs_vpt2.json` (fields: omega, nu, harmonic_zpve, anharmonic_zpve, harmonic_intensity, chi, phi_ijk, phi_iijj, rotational_constants, zeta).

| mode | harmonic omega (cm-1) | VPT2 nu (cm-1) | harmonic intensity (km/mol) |
|---|---|---|---|
| bend | 1683.6 | 1631.6 | 78.9 |
| sym. stretch | 3871.0 | 3701.2 | 2.4 |
| asym. stretch | 3997.7 | 3809.5 | 22.6 |

No Fermi resonance detected; cubic and quartic consistency checks passed. The install route and its two packaging faults are in `GoalGathering/notes/Software_Changes_Ledger.md` rows 10-11. Intensities are harmonic only (pyVPT2 has no VPT2 intensities): the reason for idea I6 in the mandate ledger.
