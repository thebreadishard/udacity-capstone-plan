# anchors_2026-10-03 — coupled-cluster anchors (plan 05)

CCSD(T)/cc-pVDZ Cartesian Hessians of aromatic molecules by central finite differences (step as listed) of analytic gradients with the triples
lambda equations solved explicitly, at the B3LYP/6-31G* geometry of the corpus row. One directory per molecule:

- `hessian_ccsd_t.npz` — `H_raw`, `H_projected` (translations/rotations projected out; hartree/bohr²), `freq_cm`; `apt_ccsd_t.npz` (dipole derivatives) where computed;
- `reference.npz` — energy, gradient, coordinates (bohr), charge, spin at the reference geometry;
- `grad_<k>_<sign>.npy`, `ener_<k>_<sign>.npy`, `dip_<k>_<sign>.npy` — gradient, energy and dipole at displacement k, ±;
- `e8_fd.log`, `run.log`, `chain.log`, `partial_*.log` — the run record with the checks; `two_route_check.*` where the check ran separately.

| molecule | atoms | frozen core | gradients | FD asymmetry (a.u.) | sum rule (E_h/a0²) | energy route (E_h/a0²) |
|---|---|---|---|---|---|---|
| benzene | 12 | 6 | 72 | 5.2e-05 | 1.3e-05 | 5.2e-05 |
| fluorobenzene | 12 | 7 | 72 | 2.3e-05 | 5.4e-06 | 1.0e-04 |
| pyridine | 11 | 6 | 66 | 8.6e-06 | 3.9e-06 | 7.6e-05 |
| naphthalene | 18 | 10 | 108 | 1.6e-05 | 2.5e-06 | 4.1e-05 |

The manifest beside the archive lists SHA-256 and size per file and the repository commit. Licence CC BY 4.0. Produced by
`probes/e8_cc_hessian_fd.py` (symmetry reconstruction `probes/e8_symmetry.py`) in https://github.com/thebreadishard/udacity-capstone-plan.
