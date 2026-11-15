# Handoff — aromir, stage 1 (the low level), 15 November 2026

Written from a cloud session (the laptop was not reachable). TASKS 73. The user, 15 Nov: a first version of `aromir` before the
supervisor meeting of 25 Nov, preferably with network v1.4; decisions of that morning — pyscf + geomeTRIC as the engine, the anharmonic
position included, v1.3 if v1.4 is late, the repository public, 0.1 = a working `aromir spectrum` with certificate and model card
(PyPI, conda-forge, the Hub and the reproduction test stay with v1.0).

## What is in `thebreadishard/aromir` (commit 4ef9586, branch `main`)

`src/aromir/`: `constants`, `errors`, `molecule` (Geometry), `admission` (the refusals), `geometry` (canonical order, start geometry),
`dft` (the level, SCF with the second-order finish), `optimisation` (geomeTRIC), `response` (the kept response, the residual check, the
polar tensor), `lowlevel`, `vibrations`, `spectrum`, `records`, `pipeline`, `cli` (`aromir check`, `aromir baseline`).
79 tests, 99.7 % branch coverage; ruff with all rules, mypy strict; CI on Linux and macOS.

**Not in it yet:** the ΔH network and its weights, the anharmonic step, the certificate, the family rule, the low-mode repair, the
training code. `aromir spectrum` does not exist until the network does.

## Validation (number and counterpart)

- Hessian on water against this repository's label route (`corpus/apt.py` `hessian_with_response`): 1.1e-12 hartree/bohr².
- Polar tensor on water against the label route (`refine_response` + `apt_from_mo1`): 3.6e-14 e; against finite differences of the
  dipole: 1.2e-5 e.
- Modes, projected Hessian, positions and intensities on water against `corpus/vibrations.py` and `apt.intensities`: 3.2e-11 cm⁻¹,
  1.8e-14, 1.9e-11 km/mol.
- Benzene end to end in the cloud container (4 threads): optimisation 5 steps in 205 s, max force 6.7e-6 hartree/bohr; Hessian and APT
  720 s; response residual 2.5e-8, sum rule 1.1e-4 e; 30 bands, CH-oop 694.58 cm⁻¹ at 77.5 km/mol.
- Environment: pyscf 2.15.0, geomeTRIC 1.1.1, RDKit 2026.9.2, numpy 2.5.4, Python 3.13.

The comparison script is not in either repository (it imports both); it is reproduced by running `lowlevel.compute` and the label
route's functions on the water geometry of `tests/conftest.py`.

## Findings for this repository (each wants a TASKS row; proposed here because the laptop holds uncommitted work on TASKS.md's branch)

1. **`probes/engine_check.py` does not learn whether geomeTRIC converged.** It calls pyscf's `geometric_solver.optimize`, which
   returns the last geometry either way (`kernel` catches `GeomOptNotConvergedError` and returns `conv`; `optimize` drops it;
   `assert_convergence=True` only asserts the SCF gradients). The engine check's eight geometries carry their recorded max force, so
   they can be checked after the fact: read `max_force_au` in each `result.json`. aromir calls `kernel` and raises.
2. **pyscf 2.15.0's Krylov solver now falls back to per-root solves** ("Krylov solver reached subspace convergence but true residual
   … exceeds tolerance. Falling back to per-root solve"). On water and benzene the residual before our refinement was 2.3e-9 and
   2.5e-8 with zero rounds. This bears on design point 2 (the guard goes when a released pyscf never needs it): the registered
   measurement — the two cases and one full batch of APTs — can now be run on 2.15.0.
3. **Atom masses.** aromir takes NIST isotope masses (H 1.00782503223, …). The corpus's `geometry.json` masses are psi4's and are not
   in git; compare one folder's `masses_amu` with `aromir.constants.ELEMENTS` before the network is ported (a difference moves every
   frequency).
4. **Deliberate differences from pipeline 0.9**, to be listed in the model card: vibrational modes are the 3N−6 of the projected
   space (no |ω| > 20 cm⁻¹ threshold, so a real mode below 20 cm⁻¹ is listed); the second-order SCF finish is always the fallback;
   one molecule at a time (a SMILES with a dot is refused).

## Next stages, in order

1. **The network's inference path**: `m05/rungC_equivariant.py` (body), `rungC_hybrid.py` (head), `internal_coords.py`,
   `e7_t2_sqm.internals` / `to_internal`, `e7_rungB_pairs.molecule_pairs`, `rungC_train.input_tensors` / `load_hybrid_model` /
   `tensor_config`, `rungC_infer.py`. Regression: both codes on `tests/data/rungC_cc_pin_model.pt` and on a random-initialised model,
   ΔH equal to the bit on benzene and phenanthrene.
2. **The weights**: v1.3's three checkpoints (and v1.4's when carried) converted to safetensors with a JSON recipe — from the laptop.
3. **The family rule and the certificate** (`m08/live_certificate.py`, `m08/licence.py`), numbers read from the evaluation records.
4. **The printed anharmonic position** (`PreRegistration_2026-11-14_Printed_Band_Position.md`; TASKS 211, 219).
5. **The low-mode repair in the label route** (TASKS 216; needs `corpus/grid_response_blocked.py` and pyscf 2.15).
6. `aromir spectrum`, the model card, release 0.1.
