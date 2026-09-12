# X5 — atom-pair structure of the benzene Δ₂ in mass-weighted Cartesian coordinates (2026-09-12 17:40)

Validation of the transform against the stored full Hessian difference projected on the vibrational subspace: best reading 'mass_weighted_by_Minv', relative residual 2.371e-15 (the other reading: 9.217e+03). A residual at the probing-error level means the mapping is right; a residual of order 1 would mean the stored Hessians are in other units.

**Spectrum.** Numerical rank 30 of 30; Frobenius fraction in the top k eigen-directions: k=1: 0.073, k=2: 0.146, k=3: 0.211, k=5: 0.339, k=10: 0.593, k=15: 0.817, k=20: 0.964, k=30: 1.000.

**Atom-pair blocks** (3×3 blocks of the 36×36 matrix; fraction of the total Frobenius norm²; noise floor = RMS block norm under X2's per-element noise, 200 draws):

| pair type | blocks | fraction of ‖Δ‖²_F | median block norm | median noise floor | blocks > 3× floor |
|---|---|---|---|---|---|
| on-atom | 12 | 0.719 | 3.254e-06 | 4.863e-09 | 12 |
| CH bonded | 6 | 0.170 | 1.782e-06 | 3.989e-09 | 6 |
| CC non-bonded | 9 | 0.054 | 8.076e-07 | 2.686e-09 | 9 |
| CC bonded | 6 | 0.046 | 9.267e-07 | 2.766e-09 | 6 |
| CH non-bonded | 30 | 0.009 | 1.405e-07 | 3.893e-09 | 30 |
| HH non-bonded | 15 | 0.003 | 1.220e-07 | 5.452e-09 | 15 |

Blocks above 3× the noise floor: 78 of 78.

Distance profile of the off-atom blocks (median block norm per distance shell, bohr):

| distance | pairs | median block norm |
|---|---|---|
| 2.1 | 6 | 1.782e-06 |
| 2.6 | 6 | 9.267e-07 |
| 4.1 | 12 | 2.431e-07 |
| 4.6 | 6 | 8.068e-07 |
| 4.7 | 6 | 2.148e-07 |
| 5.3 | 3 | 8.429e-07 |
| 6.4 | 12 | 1.398e-07 |
| 7.3 | 6 | 8.115e-08 |
| 8.1 | 6 | 4.814e-08 |
| 9.4 | 3 | 1.220e-07 |

Reading aid: S1 (real-space locality) predicts the norm concentrated in on-atom and bonded blocks and decaying with distance; S2 (low rank) predicts a steep Frobenius fraction in few eigen-directions. Units are the npz's own (E_h per mass-weighted bohr²); only ratios are read.

Constants: {"sigma_E_uEh": 0.5, "element_uncertainty_rule": "delta = sigma_E / 2 per q^2 element (X2)", "n_noise_draws": 200, "seed": 0, "bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "top_k": [1, 2, 3, 5, 10, 15, 20, 30]}