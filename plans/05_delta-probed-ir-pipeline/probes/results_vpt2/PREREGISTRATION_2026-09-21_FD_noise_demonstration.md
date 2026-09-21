# Pre-registration, 21 September 2026 08:2x — demonstrating the cause of the benzene VPT2 failure

*Written before the two test runs report. The claim under test is the one recorded in `BENZENE_THREE_BAND_TEST_2026-09-20.md` §7:
the semi-diagonal quartic constants φ_iijj of benzene (B3LYP/6-31G*, psi4 1.10.2, pyVPT2 0.1.2, `DISP_SIZE` 0.05) are dominated by
numerical noise, because psi4's B3LYP Hessians are themselves finite differences of gradients and the second finite difference at
a step of 0.05 amplifies that noise by 1/0.05² = 400. Measured on the existing run (`qff_benzene_2026-09-21.md`): the two independent
routes to each φ_iijj disagree by a median of 22.4 cm⁻¹, 90th percentile 107, maximum 1,264.5 cm⁻¹ (435 pairs).*

## The two tests running on hel1-14 and what each must show

| test | what changes | prediction if the claim is right | prediction if it is wrong (e.g. degeneracy handling, resonance treatment, a real feature of the potential) |
|---|---|---|---|
| **T1** psi4 FD Hessians, `DISP_SIZE` 0.20 (tag `_d020`, 3-point psi4 Hessians, same molecule, same level, 61 Hessians) | only the outer step: 0.05 → 0.20 | the route disagreement falls by ≈ (0.20/0.05)² = 16: median ≈ 1.4 cm⁻¹ (accept ≤ 3), maximum ≈ 80 cm⁻¹ (accept ≤ 150); the fundamentals become physical: the a1g ring breathing at ν − ω between −5 and −30 cm⁻¹ (was −217), degenerate partners split by < 3 cm⁻¹ (were tens) | the disagreement stays at tens of cm⁻¹; the breathing mode stays far off |
| **T2** pyscf analytic B3LYP Hessians at the *same 61 geometries* (`pyscf_hessians_for_qff.py`, grid 99/590, SCF 1e-11; directory `pyscf_hessians_d005_grid99_590`), assembled with the same `DISP_SIZE` 0.05 by `qff_from_hessians.py` | only the source of the Hessians: finite-difference → analytic | the route disagreement falls to the grid/SCF level: median < 1 cm⁻¹, maximum < 10 cm⁻¹; the fundamentals become physical as in T1 | the disagreement stays at tens of cm⁻¹ |

Both tests change one thing each. If T1 and T2 both come out as predicted, the cause is demonstrated for our case: noise in the
input Hessians, amplified by the small step. If T2 is clean and T1 is not, the psi4 finite-difference Hessians carry a noise that a
larger step alone does not cure (then the pipeline route is analytic Hessians, full stop). If neither is clean, the claim is wrong and
the degeneracy question of §6 comes back.

## What the existing data already say (post-hoc, not a pre-registration; `probes/route_noise_structure.py` on the npz of 21 September)

- The disagreement does **not** scale with the frequencies of the pair: Spearman correlation of |route a − route b| with
  √(ω_i⁻² + ω_j⁻²) is +0.01, with |φ_iijj| +0.19. An isotropic Cartesian noise would have given the frequency scaling. So the noise
  is not a uniform floor; it sits in particular displaced-geometry Hessians.
- Per displaced mode, the Hessians displaced along the two 622 cm⁻¹ modes (e2g, indices 2 and 3) carry by far the largest
  disagreement (fitted s_k ≈ 310–420 cm⁻¹), then a C–H stretch (25) and the 1021 cm⁻¹ mode (12); several displaced modes carry
  none. Degenerate partners do not always share their s_k (mode 25: 236, its partner 26: 115), which is what per-geometry numerical
  noise looks like and what a physical feature would not do.
- The cubic constants φ_ijk, which need only one finite difference of the Hessians (noise ∝ 1/d instead of 1/d²), have a route
  spread far smaller in the same run (`qff_benzene_2026-09-21.md`: median 0.24 cm⁻¹ against 22.4, maximum 219 against 1,265), as the noise picture predicts.

## What this does and does not demonstrate for Mackie et al. 2021's "cause unknown"

Our mechanism (finite differences of finite differences) is not theirs (Gaussian, analytic Hessians). What T1/T2 can show is the
general point: the two-route (or symmetry-partner) disagreement of φ_iijj is a direct, cheap measure of the numerical quality of a
quartic force field, and the standard checks are silent about it. Whether *their* instabilities have a numerical component is a
separate test: the same diagnostic on naphthalene and a four-ring PAH with analytic Hessians at their level and their step. That is
gate E's prerequisite (2) in the PI assessment; naphthalene costs ≈ 1–2 days on hel1-14 after the current jobs (97 analytic
Hessians), a four-ring PAH about a week. Not started; on the to-do.

## Reading the results

`python probes/qff_from_hessians.py <cache_dir> --disp 0.20` for T1 (cache `cache_benzene_d020`) and
`python probes/qff_from_hessians.py <pyscf_dir> --disp 0.05` for T2; then `python probes/route_noise_structure.py <npz>` for the
structure. The outcome is recorded below this line when it is in, with the run stamps.

## Results

*(pending)*
