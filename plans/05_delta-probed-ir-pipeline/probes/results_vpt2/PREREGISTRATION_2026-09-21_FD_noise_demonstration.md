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

**T2, read 13:1x (61 analytic pyscf B3LYP/6-31G* Hessians, grid 99/590, SCF 1e-11, 358 min on hel1-14 at 4 threads under load; `pyscf_hessians_d005.log`; assembled by `qff_from_hessians.py --disp 0.05` → `qff_benzene_pyscf_analytic_2026-09-21.md`).**

| quantity | psi4 FD Hessians, step 0.05 (20–21 Sep) | prediction for T2 | T2 measured | verdict |
|---|---|---|---|---|
| route disagreement, median | 22.4 cm⁻¹ | < 1 | **0.1** | as predicted |
| route disagreement, 90th percentile | 107 | — | 5.9 | — |
| route disagreement, maximum | 1,264.5 | < 10 | **46.8** | above the bound; see below |
| a1g ring breathing, ν − ω | −216.9 | between −5 and −30 | **−16.0** (1021.7 → 1005.7) | as predicted |
| splitting of degenerate partners | tens of cm⁻¹ | < 3 | **≤ 0.1** on every pair | as predicted |

The median falls by a factor 200 and the fundamentals are physical: the three bands of the three-band test come out at 852.0 (e1g, experiment 849), 1005.7 (a1g,
992) and 1327.2 (b2u Kekulé, 1310) against harmonic 865.2 / 1021.7 / 1358.5 — the anharmonic correction removes most of the harmonic gap and the rest
is the B3LYP/6-31G* error that ΔH addresses. Every degenerate pair agrees to 0.1 cm⁻¹ (raw and symmetrised columns identical), so the degeneracy question of
§6 of the three-band note is closed: the earlier splittings were noise.

The maximum (46.8 cm⁻¹) does not meet the < 10 bound, and its structure says why: the per-displacement fit (`route_noise_structure.py`) puts all of the
residual on the degenerate pairs, with *identical* values for the two partners (25/26 and 27/28: 15 cm⁻¹ each; 16/17: 11; 13/14: 5; every other mode 0).
Numerical noise would not do that; a rotation of the analysis basis inside a degenerate subspace at the displaced geometries would (the assignment
residual of the mode matching is 3.5 × 10⁻², all in those subspaces). So the residual is a property of how the diagnostic handles exactly degenerate modes, not of
the Hessians; the same shows in the cubic spread (median 0.00, one outlier of 625 cm⁻¹ on a degenerate triple). That is a known limitation to fix in
`qff_from_hessians.py` (a symmetry-adapted or projected treatment of degenerate subspaces), not a counter-example to the claim. Frequency scaling
is again absent (Spearman −0.10), as it was for the noisy set.

**Verdict on the claim, with T1 still running (30 of 61 at 13:1x):** T2 alone already shows that replacing the finite-difference input Hessians by analytic ones, at the
same geometries and the same step, removes the disagreement and the unphysical fundamentals. That is the demonstration for our case. T1 will say whether a
larger step alone is enough with psi4's FD Hessians; the pipeline choice does not wait for it: **the anharmonic step of the spectrum pipeline uses analytic
Hessians (pyscf) whenever the functional has none in psi4** — for the user to confirm tonight; sheet 8 then says "VPT2 (pyVPT2 on pyscf Hessians)".

**T1, read 16:3x (61 psi4 FD Hessians at `DISP_SIZE` 0.20, 3-point, 10.0 h on hel1-14 at 8 threads under load; `benzene_vpt2_d020_hel1-14.log`; assembled by
`qff_from_hessians.py --disp 0.20` → `qff_benzene_d020_2026-09-21.md`).**

| quantity | step 0.05 (20–21 Sep) | prediction for T1 | T1 measured | verdict |
|---|---|---|---|---|
| route disagreement, median | 22.4 cm⁻¹ | ≈ 1.4 (accept ≤ 3) | **2.3** | as predicted (factor 10, not 16) |
| route disagreement, 90th percentile | 107 | — | 11.0 | — |
| route disagreement, maximum | 1,264.5 | ≈ 80 (accept ≤ 150) | **110.1** | as predicted |
| a1g ring breathing, ν − ω | −216.9 | between −5 and −30 | **−28.0** symmetrised (−31.0 raw) | at the edge of the band |
| splitting of degenerate partners | tens of cm⁻¹ | < 3 | 1.2–1.5 symmetrised (up to 4.4 raw) | as predicted after symmetrisation |
| cubic route spread, maximum | 218.6 | — | 40.8 | — |

The noise falls with the step as a second finite difference of noisy input must (factor 10 against the pure-noise factor 16; the remainder is the
truncation error that a step of 0.20 buys, visible as the flat frequency dependence again, Spearman +0.11). The fundamentals become physical here too:
e1g 848.5 (experiment 849), a1g 992.5 (992), b2u 1321.9 (1310).

**T1 against T2.** The two clean sets do not give the same anharmonic shifts: the breathing mode moves −28 at step 0.20 with FD input and −16 at step
0.05 with analytic input; the Kekulé mode −34.7 against −31.4. That difference is the step-size systematic (sextic and higher terms at 0.20) plus
whatever noise T1 still carries (median 2.3 against 0.1); it is not decided by the experiment, because the B3LYP/6-31G* harmonic error is in the
same numbers. The pre-registered claim is confirmed by both tests: the 20 September failure was finite-difference noise, cured by a larger step and
removed by analytic input. Which step the analytic route should use is a convergence question, not a noise question: T3 = analytic Hessians at 0.10
(61 more pyscf Hessians, ≈ 6 h on hel1-14) would bracket it. On the to-do, after the user's word.

**Closing verdict 16:3x: claim demonstrated for our case (T1 and T2 as predicted on every noise statistic; fundamentals physical in both).** The pipeline
recommendation stands: analytic Hessians (pyscf) for the anharmonic step wherever psi4 has none; step size to be set by T3.

**Addendum 18:2x — the degenerate-subspace residual was the diagnostic's, and is gone.** `qff_from_hessians.py` now rotates its analysis basis inside each
exactly degenerate subspace onto the displacement directions it finds (nearest orthogonal matrix), then assigns. On the T2 set the assignment residual
drops from 3.5 × 10⁻² to 5.7 × 10⁻³ and the route disagreement to **median 0.1, 90th percentile 0.2, maximum 0.9 cm⁻¹** (was 46.8); the cubic outlier
falls from 625 to 24 cm⁻¹. T2 therefore meets every pre-registered bound, including the maximum. The fundamentals move slightly with the cleaner
constants: ring breathing −17.3 (was −16.0), the three bands 850.6 / 1004.4 / 1324.1 against 849 / 992 / 1310 (`qff_benzene_pyscf_analytic_2026-09-21.md`,
regenerated). The psi4 sets are unchanged by the fix, because their displacements were made in the basis the analysis already finds (assignment residual
2 × 10⁻¹³ at step 0.05, 8 × 10⁻¹³ at 0.20): 22.4 / 107.0 / 1264.5 and 2.3 / 11.0 / 110.1 as before, so the numbers in the pyVPT2 issue and PR stand.

**Addendum 21:2x — T3 read: the step size does not matter on analytic Hessians; the T1/T2 difference was the psi4 input.** **T3 (analytic pyscf Hessians, step 0.10, 61 geometries from `make_qff_displacements.py`; hel1-14, 210 min; `qff_benzene_pyscf_analytic_d010_2026-09-21.md`):** route disagreement median 0.02, 90th percentile 0.10, maximum 0.44 cm⁻¹ (T2 at 0.05: 0.1 / 0.2 / 0.9); cubic route spread maximum 0.4; assignment residual 5.6 × 10⁻¹⁵ (our own displacements, exactly in the analysis basis); degenerate partners equal to 0.1. Fundamentals: ring breathing −17.4 (T2 −17.3; T1 with psi4 FD Hessians at 0.20: −28.0), the three bands 850.6 / 1004.4 / 1324.0 (T2: 850.6 / 1004.4 / 1324.1). Per-displacement noise model: every s_k = 0 at the print precision; the residual correlation with 1/ω (Spearman +0.40) is on numbers of 0.0–0.4 cm⁻¹ and carries no weight.
Conclusion: doubling the step on analytic Hessians changes the fundamentals by ≤ 0.1 cm⁻¹ and halves the residual route noise, so the
−28 versus −17 of T1 against T2 is not a step-size systematic of the quartic differences but the finite-difference psi4 Hessians at step
0.20 (noise of the input scaled by the larger step). **Pipeline setting (decision 46 B): step 0.10 in reduced coordinates on analytic
Hessians**, with the two-route disagreement printed as the error bar of every run. Pyscf B3LYP/6-31G* (grid 99/590, SCF 1e-11) is the
Hessian source for the anharmonic step; psi4 finite-difference Hessians are not used for quartic constants.
