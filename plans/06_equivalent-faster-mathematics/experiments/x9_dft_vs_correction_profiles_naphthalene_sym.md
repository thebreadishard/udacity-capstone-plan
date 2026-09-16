# X9 — the DFT Hessian and the correction side by side, by bond-graph distance (naphthalene_sym, 2026-09-16 08:58)

Sanity: harmonic frequencies from the mass-weighted H_low against the dry run's own list, max |diff| 2.00e-05 cm⁻¹. Blocks are 3×3 atom-pair blocks of the mass-weighted matrices (units E_h per mass-weighted bohr²; only ratios are read).

## Norm level: median block norm per bond-graph distance

| graph distance | pairs | median ‖H_low[A,B]‖ | median ‖Δ[A,B]‖ | median ratio Δ/H_low | max ratio |
|---|---|---|---|---|---|
| 0 | 18 | 4.643e-05 | 1.606e-06 | **0.0346** | 0.0346 |
| 1 | 19 | 1.909e-05 | 9.482e-07 | **0.0497** | 0.0820 |
| 2 | 30 | 4.955e-06 | 2.539e-07 | **0.0512** | 0.2098 |
| 3 | 38 | 1.572e-06 | 1.106e-07 | **0.0703** | 0.4640 |
| 4 | 32 | 2.791e-07 | 2.224e-08 | **0.0797** | 0.3609 |
| 5 | 22 | 1.543e-07 | 1.554e-08 | **0.1008** | 0.3305 |
| 6 | 10 | 6.441e-08 | 1.275e-08 | **0.1980** | 0.2552 |
| 7 | 2 | 3.578e-08 | 7.510e-09 | **0.2099** | 0.2358 |

By pair type:

| graph distance | type | pairs | median H_low | median Δ | median ratio |
|---|---|---|---|---|---|
| 0 | CC | 10 | 4.635e-05 | 1.600e-06 | 0.0345 |
| 0 | HH | 8 | 1.983e-04 | 4.989e-06 | 0.0252 |
| 1 | CC | 11 | 1.519e-05 | 7.946e-07 | 0.0496 |
| 1 | CH | 8 | 5.429e-05 | 1.690e-06 | 0.0311 |
| 2 | CC | 14 | 3.727e-06 | 6.397e-07 | 0.1756 |
| 2 | CH | 16 | 5.072e-06 | 2.424e-07 | 0.0482 |
| 3 | CC | 12 | 1.843e-06 | 4.946e-07 | 0.2698 |
| 3 | CH | 20 | 1.271e-06 | 7.292e-08 | 0.0624 |
| 3 | HH | 6 | 2.714e-06 | 2.652e-07 | 0.0977 |
| 4 | CC | 6 | 9.476e-07 | 3.404e-07 | 0.3592 |
| 4 | CH | 20 | 2.170e-07 | 1.184e-08 | 0.0702 |
| 4 | HH | 6 | 9.507e-07 | 4.938e-08 | 0.0529 |
| 5 | CC | 2 | 9.800e-07 | 3.234e-07 | 0.3300 |
| 5 | CH | 12 | 1.540e-07 | 1.554e-08 | 0.0977 |
| 5 | HH | 8 | 2.100e-07 | 1.153e-08 | 0.0615 |
| 6 | CH | 4 | 6.467e-08 | 1.328e-08 | 0.2055 |
| 6 | HH | 6 | 5.514e-08 | 8.171e-09 | 0.1318 |
| 7 | HH | 2 | 3.578e-08 | 7.510e-09 | 0.2082 |

## Band level: zero every block at graph distance ≥ d*, largest band shift (exact harmonic positions)

| blocks kept | H_low alone: max shift (cm⁻¹) | Δ alone: max shift (cm⁻¹) | bands > 0.5 (Δ) | ratio Δ/H_low |
|---|---|---|---|---|
| graph distance < 1 | 398.70 | 88.18 | 48 | 0.2212 |
| graph distance < 2 | 260.66 | 32.36 | 39 | 0.1242 |
| graph distance < 3 | 461.53 | 18.64 | 39 | 0.0404 |
| graph distance < 4 | 28.74 | 10.47 | 25 | 0.3642 |
| graph distance < 5 | 20.85 | 5.41 | 19 | 0.2595 |
| graph distance < 6 | 2.85 | 0.37 | 0 | 0.1314 |

Reading: T3′ predicts the ratio column to fall with distance (the correction shorter-ranged than the Hessian) and the band-level far-block dependence of Δ to be a small fraction of H_low's. Losing condition at benzene: neither falls. Benzene's graph-distance range (≤ 3) is short; naphthalene (≤ 5) is the first informative case, as for X5/X8. Stand-in caveat: Δ here is BHHLYP − B3LYP, not CC − DFT.

Constants: {"bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "n_zero_modes": 6, "distance_cuts_for_band_test": [1, 2, 3, 4, 5, 6], "cuts_note": "cuts given on the command line for this run (the pre-stated benzene cuts are 1,2,3)"}