# X11 — substitution products on the X10-selected patterns (benzene, mode space, 2026-09-12 19:50)

Counting code: X1c's. Pattern = diagonal + the listed pairs; k = triangular-substitution colours (two sequential colourings of G_u(L_π), the smaller proper one), maxr = Coleman & Moré's lower bound; recovery verified numerically. Energies: direct measurement 2M + 2n (naive convention, a lower bound on a real deck); products 2·g·k gradient-equivalents; g* = (2M + 2n)/(2k) is the gradient-to-energy cost ratio below which products win.

| pattern | pairs | elements | direct energies (2M + 2n) | maxr | k (products) | g* | recovery error |
|---|---|---|---|---|---|---|---|
| X10 P1 DFT-only 1/|w_i^2-w_j^2|: diagonal + top-19 pairs (0.5 cm⁻¹) | 19 | 49 | 98 | 3 | **4** | 12.2 | 1.1e-16 |
| X10 P2 oracle |Delta_ij|: diagonal + top-17 pairs (0.5 cm⁻¹) | 17 | 47 | 94 | 3 | **3** | 15.7 | 0.0e+00 |
| X10 P3 oracle drop-one effect: diagonal + top-6 pairs (0.5 cm⁻¹) | 6 | 36 | 72 | 2 | **2** | 18.0 | 0.0e+00 |
| symmetry prior: diagonal + all 47 eligible pairs | 47 | 77 | 154 | 7 | **7** | 11.0 | 1.1e-16 |
| X1c noise pattern θ = 0.5 µE_h (|Δ_ij| > θ) | 87 | 117 | 234 | 6 | **7** | 16.7 | 2.2e-16 |
| dense | 435 | 465 | 930 | 30 | **30** | 15.5 | 0.0e+00 |

Reading: if k falls with the pattern, the two savings stack (fewer products on a smaller pattern); if k stays near the diagonal's floor, the substitution count is already set by the diagonal + a few couplings and X10 adds nothing to S5's side — it then only helps the energies-only deck. One molecule, one stand-in; naphthalene repeats the count.

Constants: {"theta_reference_uEh": 0.5, "random_seed": 0}