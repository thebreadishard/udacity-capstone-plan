# X9 — the DFT Hessian and the correction side by side, by bond-graph distance (benzene, 2026-09-12 19:44)

Sanity: harmonic frequencies from the mass-weighted H_low against the dry run's own list, max |diff| 2.00e-05 cm⁻¹. Blocks are 3×3 atom-pair blocks of the mass-weighted matrices (units E_h per mass-weighted bohr²; only ratios are read).

## Norm level: median block norm per bond-graph distance

| graph distance | pairs | median ‖H_low[A,B]‖ | median ‖Δ[A,B]‖ | median ratio Δ/H_low | max ratio |
|---|---|---|---|---|---|
| 0 | 12 | 1.224e-04 | 3.284e-06 | **0.0268** | 0.0336 |
| 1 | 12 | 3.573e-05 | 1.317e-06 | **0.0369** | 0.0544 |
| 2 | 18 | 5.051e-06 | 2.434e-07 | **0.0482** | 0.1895 |
| 3 | 21 | 1.480e-06 | 9.572e-08 | **0.0647** | 0.2615 |
| 4 | 12 | 6.124e-07 | 3.329e-08 | **0.0543** | 0.0568 |
| 5 | 3 | 7.519e-07 | 4.202e-08 | **0.0559** | 0.0559 |

By pair type:

| graph distance | type | pairs | median H_low | median Δ | median ratio |
|---|---|---|---|---|---|
| 0 | CC | 6 | 4.625e-05 | 1.549e-06 | 0.0335 |
| 0 | HH | 6 | 1.986e-04 | 5.015e-06 | 0.0253 |
| 1 | CC | 6 | 1.704e-05 | 9.253e-07 | 0.0543 |
| 1 | CH | 6 | 5.442e-05 | 1.709e-06 | 0.0314 |
| 2 | CC | 6 | 4.322e-06 | 8.154e-07 | 0.1886 |
| 2 | CH | 12 | 5.053e-06 | 2.422e-07 | 0.0479 |
| 3 | CC | 3 | 3.203e-06 | 8.341e-07 | 0.2604 |
| 3 | CH | 12 | 1.475e-06 | 9.411e-08 | 0.0637 |
| 3 | HH | 6 | 2.276e-06 | 1.837e-07 | 0.0807 |
| 4 | CH | 6 | 2.499e-07 | 1.139e-08 | 0.0456 |
| 4 | HH | 6 | 9.731e-07 | 5.484e-08 | 0.0563 |
| 5 | HH | 3 | 7.519e-07 | 4.202e-08 | 0.0559 |

## Band level: zero every block at graph distance ≥ d*, largest band shift (exact harmonic positions)

| blocks kept | H_low alone: max shift (cm⁻¹) | Δ alone: max shift (cm⁻¹) | bands > 0.5 (Δ) | ratio Δ/H_low |
|---|---|---|---|---|
| graph distance < 1 | 401.76 | 37.03 | 29 | 0.0922 |
| graph distance < 2 | 164.25 | 31.95 | 25 | 0.1945 |
| graph distance < 3 | 146.62 | 13.06 | 20 | 0.0891 |

Reading: T3′ predicts the ratio column to fall with distance (the correction shorter-ranged than the Hessian) and the band-level far-block dependence of Δ to be a small fraction of H_low's. Losing condition at benzene: neither falls. Benzene's graph-distance range (≤ 3) is short; naphthalene (≤ 5) is the first informative case, as for X5/X8. Stand-in caveat: Δ here is BHHLYP − B3LYP, not CC − DFT.

Constants: {"bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "n_zero_modes": 6, "distance_cuts_for_band_test": [1, 2, 3]}