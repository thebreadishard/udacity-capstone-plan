# X12 — decay of the B3LYP/6-31G* Hessian with bond-graph distance, benzene → coronene (2026-09-12 19:55)

Hessians from plan 02 (git `57a7910`), mass-weighted (amu → mₑ), 3×3 atom-pair blocks; median block norm per bond-graph distance; decay factor per bond from a log-linear fit over distances ≥ 1 (on-atom blocks excluded); band test = zero every block at graph distance ≥ d*, largest harmonic shift (X2's rule). Sanity per molecule: the highest C–H stretch frequency and the number of imaginary modes.

| molecule | C | H | max graph distance | decay factor per bond, all d ≥ 1 | same, d = 1…4 only | median norm d = 1 / d = 3 / d = max | band shift zeroing blocks at d ≥ 2 / ≥ 3 / ≥ 4 (cm⁻¹) | top ν (cm⁻¹) | imag |
|---|---|---|---|---|---|---|---|---|---|
| benzene | 6 | 6 | 5 | 0.383 | **0.277** | 3.56e-05 / 1.64e-06 / 7.73e-07 | 162.7 / 145.9 / 25.8 | 3210 | 0 |
| naphthalene | 10 | 8 | 7 | 0.343 | **0.251** | 1.91e-05 / 1.57e-06 / 3.45e-08 | 261.0 / 461.9 / 28.9 | 3208 | 0 |
| anthracene | 14 | 10 | 9 | 0.420 | **0.252** | 1.99e-05 / 1.30e-06 / 2.22e-08 | 226.0 / 338.9 / 30.0 | 3208 | 0 |
| phenanthrene | 14 | 10 | 9 | 0.443 | **0.257** | 1.84e-05 / 1.34e-06 / 3.71e-08 | 229.3 / 153.8 / 48.3 | 3224 | 0 |
| tetracene | 18 | 12 | 11 | 0.531 | **0.271** | 1.66e-05 / 1.33e-06 / 2.90e-08 | 344.2 / 275.7 / 137.8 | 3208 | 0 |
| chrysene | 18 | 12 | 11 | 0.560 | **0.260** | 1.85e-05 / 1.31e-06 / 4.01e-08 | 330.7 / 268.1 / 61.2 | 3232 | 0 |
| triphenylene | 18 | 12 | 9 | 0.576 | **0.293** | 1.82e-05 / 1.31e-06 / 1.31e-07 | 269.3 / 114.7 / 245.5 | 3240 | 1 |
| pyrene | 16 | 10 | 9 | 0.507 | **0.268** | 1.71e-05 / 1.27e-06 / 7.83e-08 | 235.4 / 133.5 / 52.9 | 3207 | 0 |
| coronene | 24 | 12 | 9 | 0.656 | **0.351** | 1.44e-05 / 1.34e-06 / 2.87e-07 | 233.2 / 290.0 / 122.6 | 3203 | 1 |

Per-distance profiles (median block norm; pairs in brackets):

- **benzene**: d=0: 1.22e-04 (12), d=1: 3.56e-05 (12), d=2: 5.03e-06 (18), d=3: 1.64e-06 (21), d=4: 7.20e-07 (12), d=5: 7.73e-07 (3)
- **naphthalene**: d=0: 4.64e-05 (18), d=1: 1.91e-05 (19), d=2: 4.96e-06 (30), d=3: 1.57e-06 (38), d=4: 2.78e-07 (32), d=5: 1.53e-07 (22), d=6: 6.55e-08 (10), d=7: 3.45e-08 (2)
- **anthracene**: d=0: 4.66e-05 (24), d=1: 1.99e-05 (26), d=2: 3.80e-06 (42), d=3: 1.30e-06 (55), d=4: 2.89e-07 (52), d=5: 1.79e-07 (41), d=6: 5.07e-08 (28), d=7: 2.73e-08 (20), d=8: 2.21e-08 (10), d=9: 2.22e-08 (2)
- **phenanthrene**: d=0: 4.70e-05 (24), d=1: 1.84e-05 (26), d=2: 4.25e-06 (42), d=3: 1.34e-06 (55), d=4: 2.93e-07 (52), d=5: 1.63e-07 (45), d=6: 5.44e-08 (32), d=7: 3.94e-08 (17), d=8: 2.57e-08 (6), d=9: 3.71e-08 (1)
- **tetracene**: d=0: 4.67e-05 (30), d=1: 1.66e-05 (33), d=2: 3.75e-06 (54), d=3: 1.33e-06 (72), d=4: 3.03e-07 (72), d=5: 2.18e-07 (60), d=6: 5.63e-08 (46), d=7: 5.38e-08 (38), d=8: 3.88e-08 (28), d=9: 2.42e-08 (20), d=10: 2.36e-08 (10), d=11: 2.90e-08 (2)
- **chrysene**: d=0: 4.71e-05 (30), d=1: 1.85e-05 (33), d=2: 4.16e-06 (54), d=3: 1.31e-06 (72), d=4: 3.03e-07 (72), d=5: 1.74e-07 (68), d=6: 8.76e-08 (54), d=7: 6.80e-08 (36), d=8: 5.69e-08 (24), d=9: 4.05e-08 (15), d=10: 4.23e-08 (6), d=11: 4.01e-08 (1)
- **triphenylene**: d=0: 4.69e-05 (30), d=1: 1.82e-05 (33), d=2: 4.46e-06 (54), d=3: 1.31e-06 (72), d=4: 4.57e-07 (72), d=5: 3.43e-07 (72), d=6: 2.92e-07 (66), d=7: 2.59e-07 (45), d=8: 1.77e-07 (18), d=9: 1.31e-07 (3)
- **pyrene**: d=0: 4.70e-05 (26), d=1: 1.71e-05 (29), d=2: 3.99e-06 (48), d=3: 1.27e-06 (64), d=4: 3.11e-07 (64), d=5: 1.63e-07 (56), d=6: 8.93e-08 (38), d=7: 8.33e-08 (19), d=8: 6.14e-08 (6), d=9: 7.83e-08 (1)
- **coronene**: d=0: 4.61e-05 (36), d=1: 1.44e-05 (42), d=2: 3.48e-06 (72), d=3: 1.34e-06 (99), d=4: 6.05e-07 (108), d=5: 5.33e-07 (105), d=6: 4.77e-07 (84), d=7: 4.07e-07 (66), d=8: 3.33e-07 (42), d=9: 2.87e-07 (12)

Reading: a decay factor per bond that is stable across the series is the mean-field 'range' the correction will be compared against (X9 at benzene: the correction's share of the Hessian rises with distance). The band test says how far the *DFT* Hessian's own blocks matter at 0.5 cm⁻¹ — the reference for what a Cartesian truncation of any correction would have to beat. B3LYP/6-31G* only; no correction tensor beyond benzene exists yet.

Constants: {"git_commit": "57a7910", "bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "n_zero_modes": 6, "distance_cuts_for_band_test": [2, 3, 4], "files": {"benzene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/benzene.npz", "naphthalene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/naphthalene.npz", "anthracene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/anthracene.npz", "phenanthrene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/02_freq_phenanthrene.npz", "tetracene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/03_freq_tetracene.npz", "chrysene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/04_freq_chrysene.npz", "triphenylene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/05_freq_triphenylene.npz", "pyrene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/06_freq_pyrene.npz", "coronene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/07_freq_coronene.npz"}}