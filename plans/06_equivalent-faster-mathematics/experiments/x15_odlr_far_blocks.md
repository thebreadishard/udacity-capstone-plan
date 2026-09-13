# X15 — off-diagonal low rank of the DFT Hessian's far blocks, at band level (B3LYP/6-31G*, plan 02 git 57a7910; 2026-09-13 09:21)

Groups A and B along the long inertial axis (first/last third; first/second half). Block H_AB of the mass-weighted Hessian: singular values relative to the largest, numerical rank at three relative thresholds, and the largest harmonic band shift when H_AB (and H_BA) is replaced by its rank-r truncation; r* = smallest r with shift ≤ 0.5 cm⁻¹. Losing condition for ODLR at plan 05's tolerance: r* above a third of the block dimension.

## distant thirds

| molecule | atoms A/B | block dim | min A–B distance (bohr) | rank at 1e-2 / 1e-3 / 1e-4 | shift r=0 / 1 / 3 / 6 (cm⁻¹) | **r\* (0.5 cm⁻¹)** | r\*/dim |
|---|---|---|---|---|---|---|---|
| naphthalene | 6/6 | 18×18 | 4.7 | 12 / 16 / 17 | 44.7 / 32.7 / 26.8 / 26.8 | **14** | 0.78 |
| anthracene | 8/8 | 24×24 | 9.4 | 14 / 22 / 24 | 4.3 / 2.6 / 2.5 / 1.9 | **9** | 0.38 |
| phenanthrene | 8/8 | 24×24 | 5.4 | 13 / 21 / 23 | 14.8 / 14.8 / 4.6 / 2.6 | **15** | 0.62 |
| tetracene | 10/10 | 30×30 | 9.3 | 14 / 25 / 30 | 19.3 / 3.7 / 3.4 / 2.6 | **13** | 0.43 |
| chrysene | 10/10 | 30×30 | 8.3 | 22 / 29 / 30 | 3.4 / 3.3 / 3.6 / 0.5 | **9** | 0.30 |
| triphenylene | 10/10 | 30×30 | 6.4 | 24 / 29 / 30 | 21.9 / 18.0 / 146.6 / 5.1 | **20** | 0.67 |
| pyrene | 8/8 | 24×24 | 5.4 | 17 / 22 / 24 | 28.4 / 18.4 / 8.5 / 2.9 | **19** | 0.79 |
| coronene | 12/12 | 36×36 | 7.1 | 30 / 34 / 35 | 257.4 / 259.7 / 233.5 / 9.4 | **30** | 0.83 |

## halves

| molecule | atoms A/B | block dim | min A–B distance (bohr) | rank at 1e-2 / 1e-3 / 1e-4 | shift r=0 / 1 / 3 / 6 (cm⁻¹) | **r\* (0.5 cm⁻¹)** | r\*/dim |
|---|---|---|---|---|---|---|---|
| naphthalene | 9/9 | 27×27 | 2.7 | 15 / 23 / 26 | 186.3 / 172.3 / 171.7 / 38.4 | **22** | 0.81 |
| anthracene | 12/12 | 36×36 | 2.1 | 12 / 19 / 32 | 151.7 / 149.9 / 110.2 / 56.4 | **27** | 0.75 |
| phenanthrene | 12/12 | 36×36 | 2.6 | 17 / 26 / 33 | 119.1 / 119.1 / 112.9 / 101.9 | **27** | 0.75 |
| tetracene | 15/15 | 45×45 | 2.7 | 15 / 28 / 40 | 120.5 / 109.4 / 82.3 / 74.3 | **23** | 0.51 |
| chrysene | 15/15 | 45×45 | 2.0 | 14 / 24 / 38 | 160.1 / 545.8 / 109.5 / 77.7 | **28** | 0.62 |
| triphenylene | 15/15 | 45×45 | 2.0 | 23 / 35 / 43 | 358.0 / 357.9 / 329.1 / 319.5 | **33** | 0.73 |
| pyrene | 13/13 | 39×39 | 2.6 | 23 / 34 / 38 | 131.5 / 122.0 / 127.6 / 90.3 | **33** | 0.85 |
| coronene | 18/18 | 54×54 | 2.7 | 39 / 51 / 54 | 432.6 / 419.4 / 91.8 / 90.4 | **48** | 0.89 |

Top relative singular values (distant thirds):

- **naphthalene**: 1.0e+00, 4.8e-01, 2.5e-01, 1.2e-01, 9.8e-02, 8.4e-02, 5.0e-02, 4.6e-02, 2.3e-02, 2.2e-02, 2.2e-02, 1.0e-02
- **anthracene**: 1.0e+00, 1.8e-01, 9.4e-02, 6.0e-02, 5.7e-02, 4.4e-02, 3.4e-02, 3.0e-02, 2.6e-02, 2.0e-02, 1.9e-02, 1.4e-02
- **phenanthrene**: 1.0e+00, 1.5e-01, 1.4e-01, 1.2e-01, 6.4e-02, 5.7e-02, 4.2e-02, 3.9e-02, 2.6e-02, 2.2e-02, 2.0e-02, 1.6e-02
- **tetracene**: 1.0e+00, 1.5e-01, 8.1e-02, 7.4e-02, 3.9e-02, 3.6e-02, 3.0e-02, 2.6e-02, 2.3e-02, 1.8e-02, 1.4e-02, 1.3e-02
- **chrysene**: 1.0e+00, 5.6e-01, 4.2e-01, 2.3e-01, 1.9e-01, 1.4e-01, 1.3e-01, 1.2e-01, 9.4e-02, 7.3e-02, 6.4e-02, 5.1e-02
- **triphenylene**: 1.0e+00, 9.3e-01, 6.9e-01, 5.9e-01, 4.4e-01, 4.2e-01, 3.3e-01, 2.5e-01, 2.3e-01, 1.8e-01, 1.7e-01, 1.5e-01
- **pyrene**: 1.0e+00, 4.3e-01, 1.6e-01, 1.3e-01, 9.5e-02, 7.2e-02, 5.6e-02, 4.6e-02, 3.6e-02, 3.1e-02, 2.8e-02, 1.7e-02
- **coronene**: 1.0e+00, 8.5e-01, 6.9e-01, 5.1e-01, 3.9e-01, 3.2e-01, 2.9e-01, 2.3e-01, 2.1e-01, 1.8e-01, 1.6e-01, 1.3e-01

Reading: O1NumHess's ODLR predicts few dominant singular values in far blocks. The band-level r* says how many of them plan 05's 0.5 cm⁻¹ actually needs — if r* is a small fraction of the block dimension, a low-rank far part is a licensed structure for the DFT Hessian at this tolerance (the correction Δ₂ is a separate question, X15 on naphthalene later). Triphenylene and coronene files carry one imaginary mode each (X12).

Constants: {"git_commit": "57a7910", "n_zero_modes": 6, "tolerance_cm": 0.5, "rank_thresholds_rel": [0.01, 0.001, 0.0001], "report_ranks": [0, 1, 2, 3, 6, 9, 12], "files": {"naphthalene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/naphthalene.npz", "anthracene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/anthracene.npz", "phenanthrene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/02_freq_phenanthrene.npz", "tetracene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/03_freq_tetracene.npz", "chrysene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/04_freq_chrysene.npz", "triphenylene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/05_freq_triphenylene.npz", "pyrene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/06_freq_pyrene.npz", "coronene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/07_freq_coronene.npz"}}