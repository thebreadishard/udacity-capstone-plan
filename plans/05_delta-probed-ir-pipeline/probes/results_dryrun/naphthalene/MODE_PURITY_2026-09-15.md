# Irrep purity of the naphthalene factory modes (15 September 2026, 11:xx; measured, zero cost)

`python factory_mode_purity.py --molecule naphthalene --modes 11,12,22,31,45` on the stage A built by `factory_to_stageA.py` from the corpus factory's B3LYP/6-31G* Hessian (psi4, `symmetry c1`, geometry D₂h to 7.45 × 10⁻⁵ bohr). Frame: principal axes, z out of plane; the Mulliken labels are those of this frame.

D₂h, all eight operations found within 10⁻³ bohr; 8 irreps; **minimum purity 0.998586**; orthonormality after projection 1.3 × 10⁻⁴, 6.7 × 10⁻¹⁶ after block re-orthonormalisation.

| mode | ω (cm⁻¹) | family | irrep | 1 − purity | admixture amplitude √(1−purity) | max change of a component |
|---|---|---|---|---|---|---|
| 11 | 776.1 | ring-ip | Ag | 2.86e-04 | 1.7e-02 | 7.9e-03 |
| 12 | 785.3 | CH-oop | B3g | 2.41e-04 | 1.6e-02 | 6.0e-03 |
| 22 | 1045.1 | CH-ip-bend | B3u | 1.43e-06 | 1.2e-03 | 4.6e-04 |
| 31 | 1409.9 | CC-stretch | B3u | 2.08e-04 | 1.4e-02 | 7.5e-03 |
| 45 | 3194.7 | CH-stretch | B2u | 1.41e-03 | 3.8e-02 | 1.6e-02 |

Irrep counts: Ag 9, Au 4, B1g 8, B1u 4, B2g 3, B2u 8, B3g 4, B3u 8 (= 9/8/8/8 in-plane and 4/3/4/4 out-of-plane, the D₂h count of `deck_counts_planar.py` in a permuted axis convention). Least pure mode: 45 (a CH stretch; the near-degenerate CH-stretch pairs mix most).

## What it explains and what it predicts

- **The odd parts of M3 scale with the admixture amplitude.** Mode 12: ε = 1.6 × 10⁻², odd(1) = −34.2 µE_h composite; mode 22: ε = 1.2 × 10⁻³, odd(1) = −2.4 µE_h. Ratio of amplitudes 13, ratio of odd parts 14. The mechanism is a linear force term: the coupled-cluster (and SCF) gradient at the B3LYP geometry is not zero along Ag, and an Ag admixture ε in a b-mode's vector picks it up as ε·(g·u_Ag)·q. The geometry's 7 × 10⁻⁵ bohr deviation from D₂h is the smaller part; the mode vectors' impurity from a `symmetry c1` Hessian of that geometry is the larger part.
- **Pre-registered prediction for mode 31** (its ± pairs finish ≈ 13:45 today): ε = 1.4 × 10⁻² → an odd part of the same order as mode 12's, |odd(1)| ≈ 10–40 µE_h in the composite, linear in q; the sign is not predicted (it depends on the direction of the admixed Ag component). If mode 31's odd part were instead ≲ 1 µE_h, the mechanism above would be wrong.
  **Outcome (13:43, `results_m1/M3_EVEN_ODD_READING_2026-09-15.md`): the prediction as registered failed, the mechanism held.** Composite odd part +1.8 / +1.0 µE_h at q = 0.5 / 1 (neither in the band nor below the refutation line); the components are as predicted — SCF +20.6 / +37.0, LNO-CCSD(T) −18.8 / −36.0 µE_h, linear in q, the order of mode 12's and 30–60 × mode 22's — and cancel in the composite at this mode because the SCF and correlation gradients along the admixed Ag direction are equal and opposite. The registration should have been made on the components; recorded as a failed registration with the lesson.
- **What the dry run's stage A now does about it** (`dryrun_dft_delta_recovery.py --symmetrised`, patched today): the geometry averaged over the D₂h orbit (4 × 10⁻¹⁶ bohr) and every mode projected onto its irrep (impurity → rounding level), so that a non-totally-symmetric pattern is irrep-pure and the force term vanishes by symmetry — the two prerequisites of decision 37. The test is the odd part along the same three modes in the dry run's DFT energies (X16's I14 item): ≲ 1 µE_h at q = 1 passes.
- For the deck: after projection the single-sided response of decision 37 is admissible for the 39 non-Ag modes of naphthalene (9 Ag modes keep their ± pairs), which is where lever H's × 0.62 comes from.
