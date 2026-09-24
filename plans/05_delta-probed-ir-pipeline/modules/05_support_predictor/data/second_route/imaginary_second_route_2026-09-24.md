# Imaginary-mode molecules — second route (analytic pyscf Hessians, grid 99/590) against deck v1 finite differences

| molecule | B3LYP lowest: corpus → analytic | ωB97X lowest: corpus → analytic | noise on real modes (max |Δω|) | verdict |
|---|---|---|---|---|
| phenanthridine+CF3 (A2_0420908ebe) | -39.4 → -33.6 (genuine) | 38.8 → 41.0 (real in both) | b3lyp 4.0, wb97x 3.5 | genuine imaginary mode(s) — stays excluded |
| carbazole+SH (A2_13bafae8e0) | 57.3 → 58.7 (real in both) | 79.9 → 79.1 (real in both) | b3lyp 1.4, wb97x 3.6 | no imaginary mode in the corpus |
| phenanthrene+CH3 (A2_13eea56ee5) | 71.3 → 71.2 (real in both) | -31.0 → 90.6 (healed) | b3lyp 1.4, wb97x 9.4 | healed — analytic route replaces the corpus Hessians |
| carbazole+vinyl (A2_197913eb9c) | -87.3 → -86.7 (genuine) | 28.3 → -82.0 (analytic imaginary, corpus real) | b3lyp 1.6, wb97x 10.9 | genuine imaginary mode(s) — stays excluded |
| phenanthridine+CH3 (A2_1c29b66c9d) | 71.3 → 70.7 (real in both) | -51.6 → 95.1 (healed) | b3lyp 1.3, wb97x 7.1 | healed — analytic route replaces the corpus Hessians |
| pyrene+vinyl (A2_20747fd501) | -109.7 → -110.0 (genuine) | -100.4 → -113.1 (genuine) | b3lyp 1.2, wb97x 5.0 | genuine imaginary mode(s) — stays excluded |
| anthracene+NO2 (A2_20e59f3897) | -76.4 → -73.8 (genuine) | 69.9 → 73.3 (real in both) | b3lyp 1.4, wb97x 3.7 | genuine imaginary mode(s) — stays excluded |
| phenanthrene+NO2 (A2_220d2c107b) | -52.2 → -48.4 (genuine) | 41.4 → 47.9 (real in both) | b3lyp 2.9, wb97x 6.5 | genuine imaginary mode(s) — stays excluded |
| carbazole+SH (A2_22d0e8105c) | 78.1 → 77.6 (real in both) | 100.2 → 98.7 (real in both) | b3lyp 2.0, wb97x 10.2 | no imaginary mode in the corpus |
| fluorene+CF3 (A2_28eed45ad3) | -20.5 → 32.4 (healed) | 52.0 → 63.5 (real in both) | b3lyp 3.8, wb97x 11.5 | healed — analytic route replaces the corpus Hessians |
| carbazole+CF3 (A2_2a0b78bd2b) | -46.8 → -35.4 (genuine) | 37.6 → 44.1 (real in both) | b3lyp 2.9, wb97x 15.1 | genuine imaginary mode(s) — stays excluded |
| pyrene+CH3 (A2_2b693cf6e7) | 32.5 → 30.5 (real in both) | -41.6 → 68.3 (healed) | b3lyp 5.6, wb97x 5.1 | healed — analytic route replaces the corpus Hessians |
| fluorene+NO2 (A2_2c22216564) | -42.8 → -35.6 (genuine) | 88.2 → 92.2 (real in both) | b3lyp 1.2, wb97x 4.2 | genuine imaginary mode(s) — stays excluded |
| quinoxaline+NO2 (A2_3020175511) | -59.6 → -57.5 (genuine) | 86.7 → 88.0 (real in both) | b3lyp 0.6, wb97x 4.1 | genuine imaginary mode(s) — stays excluded |
| phenazine+vinyl (A2_330b4d6d8d) | -34.4 → -32.0 (genuine) | 79.1 → 46.8 (real in both) | b3lyp 0.6, wb97x 32.2 | genuine imaginary mode(s) — stays excluded |
| phenanthridine+NO2 (A2_356c370f21) | -50.1 → -45.8 (genuine) | 56.2 → 56.1 (real in both) | b3lyp 2.6, wb97x 3.5 | genuine imaginary mode(s) — stays excluded |
| acenaphthylene+vinyl (A2_3802542cb6) | -82.5 → -81.2 (genuine) | -86.0 → -79.2 (genuine) | b3lyp 1.4, wb97x 4.4 | genuine imaginary mode(s) — stays excluded |
| biphenylene+CH3 (A2_3a2982dd85) | 82.0 → 83.2 (real in both) | -36.9 → 97.2 (healed) | b3lyp 1.2, wb97x 12.1 | healed — analytic route replaces the corpus Hessians |
| phenanthrene+Cl (A2_3c2cf09504) | -23.7 → -24.1 (genuine) | 43.1 → 35.2 (real in both) | b3lyp 1.0, wb97x 7.9 | genuine imaginary mode(s) — stays excluded |
| diphenylacetylene (A_014f8519af) | -54.7 → -22.2 (genuine) | -592.5 → 54.5 (healed) | b3lyp 5.5, wb97x 80.2 | genuine imaginary mode(s) — stays excluded |
| 9-methylanthracene (A_78896cfe24) | -48.3 → -50.8 (genuine) | -114.2 → -48.6 (genuine) | b3lyp 2.0, wb97x 3.2 | genuine imaginary mode(s) — stays excluded |
| benzene (A_8448043181) | 414.9 → 415.4 (real in both) | 422.9 → 425.5 (real in both) | b3lyp 22.9, wb97x 132.3 | no imaginary mode in the corpus |
| 2-phenylpyridine (A_b90527ca2d) | -37.4 → -37.7 (genuine) | 29.0 → 37.3 (real in both) | b3lyp 0.5, wb97x 8.3 | genuine imaginary mode(s) — stays excluded |

23 molecules read; 5 healed (analytic route replaces the corpus Hessians in the next release), 15 genuine, 0 not yet available.
