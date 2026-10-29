# Imaginary-mode molecules — second route (analytic pyscf Hessians, grid 99/590) against deck v1 finite differences

| molecule | B3LYP lowest: corpus → analytic | ωB97X lowest: corpus → analytic | noise on real modes (max |Δω|) | verdict |
|---|---|---|---|---|
| quinoline+OH+ (P3c_001ea7d3a5) | 109.5 → 109.2 (real in both) | 122.3 → 127.6 (real in both) | b3lyp 0.5, wb97x 6.2 | no imaginary mode in the corpus |
| quinoline+CONH2+ (P3c_0028cdfd85) | 38.4 → 32.5 (real in both) | -482.5 → -482.6 (genuine) | b3lyp 5.8, wb97x 7.1 | genuine imaginary mode(s) — stays excluded |
| pyridine+SH+ (P3c_00e041576d) | 137.1 → 137.0 (real in both) | 159.0 → 160.9 (real in both) | b3lyp 0.8, wb97x 10.1 | no imaginary mode in the corpus |
| naphthalene+ (P3c_01f3186607) | 158.1 → 158.1 (real in both) | 166.5 → 165.2 (real in both) | b3lyp 0.4, wb97x 3.8 | no imaginary mode in the corpus |
| pyridine+OH+ (P3c_02d75f732a) | 161.0 → 161.4 (real in both) | 175.8 → 177.1 (real in both) | b3lyp 0.7, wb97x 7.0 | no imaginary mode in the corpus |
| benzene+CN+OCH3+ (P3c_03923c2081) | 100.4 → 100.3 (real in both) | 117.3 → 114.3 (real in both) | b3lyp 1.4, wb97x 27.2 | no imaginary mode in the corpus |
| benzene+CH3+NO2+ (P3c_03bf20e8fe) | 26.9 → 24.8 (real in both) | 29.3 → 96.4 (real in both) | b3lyp 2.3, wb97x 67.1 | no imaginary mode in the corpus |
| benzene+OCH3+NO2+ (P3c_049751d07c) | 40.9 → 48.4 (real in both) | 106.3 → 111.4 (real in both) | b3lyp 7.5, wb97x 8.9 | no imaginary mode in the corpus |
| pyridine+CH3+F+ (P3c_0617e12945) | 54.2 → 53.2 (real in both) | 121.5 → 117.1 (real in both) | b3lyp 2.6, wb97x 12.3 | no imaginary mode in the corpus |
| naphthalene+COOH+ (P3c_07cadc7923) | 55.4 → 58.9 (real in both) | 91.8 → 94.2 (real in both) | b3lyp 3.5, wb97x 5.1 | no imaginary mode in the corpus |
| fluoranthene+CONH2+ (P3c_097651503c) | 49.0 → 50.9 (real in both) | 65.1 → 63.2 (real in both) | b3lyp 3.7, wb97x 5.0 | no imaginary mode in the corpus |
| benzene+CH3+Cl+ (P3c_09978bbd5d) | 102.0 → 102.7 (real in both) | 159.3 → 135.8 (real in both) | b3lyp 0.7, wb97x 23.5 | no imaginary mode in the corpus |
| phenanthrene+CONH2+ (P3c_09d0b3be91) | 24.7 → 24.6 (real in both) | 58.1 → 57.1 (real in both) | b3lyp 2.0, wb97x 3.8 | no imaginary mode in the corpus |
| phenanthrene+Cl+ (P3c_0a2c2f12b8) | 59.0 → 58.5 (real in both) | 64.1 → 74.0 (real in both) | b3lyp 2.3, wb97x 9.9 | no imaginary mode in the corpus |
| quinoline+CF3+ (P3c_0aed490e42) | 67.5 → 45.6 (real in both) | 84.3 → 70.1 (real in both) | b3lyp 21.8, wb97x 14.2 | no imaginary mode in the corpus |
| naphthalene+OH+CN+ (P3c_0da4a5aea1) | 64.9 → 64.8 (real in both) | 84.2 → 82.3 (real in both) | b3lyp 0.7, wb97x 3.7 | no imaginary mode in the corpus |
| benzene+COOH+COOH+ (P3c_0ef4494cfc) | 40.7 → 32.2 (real in both) | 79.3 → 76.8 (real in both) | b3lyp 8.5, wb97x 3.5 | no imaginary mode in the corpus |
| anthracene+OCH3+ (P3c_0f1a2bd718) | -53.4 → -52.5 (genuine) | 4.8 → -22.6 (analytic imaginary, corpus real) | b3lyp 2.3, wb97x 13.6 | genuine imaginary mode(s) — stays excluded |
| naphthalene+CN+vinyl+ (P3c_0f27b44587) | 48.1 → 46.6 (real in both) | 59.8 → 65.8 (real in both) | b3lyp 1.8, wb97x 6.0 | no imaginary mode in the corpus |
| benzene+OCH3+SH+ (P3c_10bab624bc) | 107.3 → 107.2 (real in both) | 117.4 → 113.9 (real in both) | b3lyp 2.1, wb97x 34.3 | no imaginary mode in the corpus |
| benzene+CHO+CHO+ (P3c_11644318c3) | 63.2 → 60.7 (real in both) | -13.3 → -1275.8 (genuine) | b3lyp 4.1, wb97x 119.9 | genuine imaginary mode(s) — stays excluded |
| naphthalene+CONH2+ (P3c_11d1915b38) | 49.9 → 51.8 (real in both) | 90.8 → 90.6 (real in both) | b3lyp 1.9, wb97x 5.1 | no imaginary mode in the corpus |
| naphthalene+NO2+CF3+ (P3c_134d596518) | 25.9 → 9.5 (real in both) | 59.7 → 55.5 (real in both) | b3lyp 16.4, wb97x 4.2 | no imaginary mode in the corpus |
| benzene+COOH+NO2+ (P3c_1428bc8164) | 57.0 → 55.8 (real in both) | 72.6 → 67.6 (real in both) | b3lyp 1.1, wb97x 6.6 | no imaginary mode in the corpus |
| quinoline+COOH+ (P3c_1519881f69) | 45.2 → 47.9 (real in both) | 88.9 → 89.4 (real in both) | b3lyp 2.7, wb97x 2.8 | no imaginary mode in the corpus |
| naphthalene+Cl+ (P3c_16116c90de) | 104.3 → 104.2 (real in both) | 121.9 → 120.0 (real in both) | b3lyp 0.6, wb97x 5.9 | no imaginary mode in the corpus |
| benzene+OH+CF3+ (P3c_16769b963f) | 48.3 → 55.1 (real in both) | 72.8 → 78.0 (real in both) | b3lyp 6.8, wb97x 5.3 | no imaginary mode in the corpus |
| naphthalene+CN+ethynyl+ (P3c_168ec38a52) | 80.3 → 80.3 (real in both) | 99.4 → 93.3 (real in both) | b3lyp 2.1, wb97x 6.4 | no imaginary mode in the corpus |
| benzene+OCH3+CONH2+ (P3c_170b47dadd) | 52.5 → 50.0 (real in both) | 68.3 → 69.0 (real in both) | b3lyp 2.5, wb97x 13.8 | no imaginary mode in the corpus |
| pyridine+CH3+ethynyl+ (P3c_17f1611949) | -160.8 → -161.5 (genuine) | 115.7 → 111.2 (real in both) | b3lyp 3.5, wb97x 28.9 | genuine imaginary mode(s) — stays excluded |
| benzene+CH3+OH+ (P3c_188d8de09c) | -29.0 → -28.6 (genuine) | 130.3 → 92.3 (real in both) | b3lyp 0.4, wb97x 38.1 | genuine imaginary mode(s) — stays excluded |
| naphthalene+F+CN+ (P3c_18c473d7dd) | 82.8 → 83.8 (real in both) | 98.3 → 99.0 (real in both) | b3lyp 1.1, wb97x 3.6 | no imaginary mode in the corpus |
| phenanthrene+NO2+ (P3c_19eaf39036) | 33.2 → 37.3 (real in both) | 67.8 → 70.9 (real in both) | b3lyp 4.0, wb97x 3.8 | no imaginary mode in the corpus |
| benzene+F+CONH2+ (P3c_1a41c96f37) | 75.7 → 71.3 (real in both) | 72.5 → 69.6 (real in both) | b3lyp 4.4, wb97x 5.5 | no imaginary mode in the corpus |
| benzene+NH2+CF3+ (P3c_1c07e976be) | 7.5 → 12.5 (real in both) | 46.1 → 44.0 (real in both) | b3lyp 5.0, wb97x 8.8 | no imaginary mode in the corpus |
| naphthalene+NH2+OCH3+ (P3c_1f8e4687bd) | 78.8 → 78.7 (real in both) | 98.4 → 96.7 (real in both) | b3lyp 0.8, wb97x 5.7 | no imaginary mode in the corpus |
| naphthalene+NH2+COOH+ (P3c_20332edd59) | 47.1 → 47.8 (real in both) | 66.2 → 68.9 (real in both) | b3lyp 1.3, wb97x 5.3 | no imaginary mode in the corpus |
| pyrene+vinyl+ (P3c_20747fd501) | -59.6 → -60.3 (genuine) | -19.6 → -58.0 (genuine) | b3lyp 1.6, wb97x 4.3 | genuine imaginary mode(s) — stays excluded |
| anthracene+NO2+ (P3c_20e59f3897) | 59.5 → 65.5 (real in both) | 85.6 → 87.0 (real in both) | b3lyp 6.0, wb97x 4.2 | no imaginary mode in the corpus |
| phenanthrene+CF3+ (P3c_238c9ced38) | 43.7 → 41.7 (real in both) | 60.7 → 59.9 (real in both) | b3lyp 6.9, wb97x 5.6 | no imaginary mode in the corpus |
| pyrene+OCH3+ (P3c_25fe240a5d) | 71.0 → 70.5 (real in both) | 84.2 → 85.3 (real in both) | b3lyp 4.0, wb97x 7.5 | no imaginary mode in the corpus |
| anthracene+F+ (P3c_25fed68b27) | 67.6 → 71.4 (real in both) | 80.6 → 86.5 (real in both) | b3lyp 3.9, wb97x 5.9 | no imaginary mode in the corpus |
| anthracene+COOH+ (P3c_29caedd47d) | 2.4 → 9.8 (real in both) | 71.2 → 72.6 (real in both) | b3lyp 7.4, wb97x 2.7 | no imaginary mode in the corpus |
| pyrene+OH+ (P3c_2d6f59a2bf) | 89.5 → 89.7 (real in both) | 101.2 → 99.4 (real in both) | b3lyp 1.5, wb97x 3.5 | no imaginary mode in the corpus |
| fluoranthene+CH3+ (P3c_2f079d63a1) | -75.4 → -75.8 (genuine) | -120.6 → -22.7 (genuine) | b3lyp 2.6, wb97x 5.3 | genuine imaginary mode(s) — stays excluded |
| fluoranthene+Cl+ (P3c_311e979a14) | 60.5 → 60.3 (real in both) | 75.6 → 73.5 (real in both) | b3lyp 3.4, wb97x 4.0 | no imaginary mode in the corpus |
| fluoranthene+CN+ (P3c_331729cd47) | 73.4 → 71.8 (real in both) | 78.8 → 80.2 (real in both) | b3lyp 4.2, wb97x 5.6 | no imaginary mode in the corpus |
| pyrene+NO2+ (P3c_35c01ca552) | 54.8 → 55.6 (real in both) | 80.5 → 81.9 (real in both) | b3lyp 1.6, wb97x 3.5 | no imaginary mode in the corpus |
| fluoranthene+ (P3c_428228e5a5) | 99.0 → 99.3 (real in both) | 113.7 → 115.7 (real in both) | b3lyp 3.2, wb97x 3.5 | no imaginary mode in the corpus |
| naphthalene+vinyl+SH+ (P3c_476dc42b85) | 55.0 → 55.7 (real in both) | 79.9 → 75.3 (real in both) | b3lyp 1.0, wb97x 22.0 | no imaginary mode in the corpus |
| phenanthrene+ (P3c_541c53d1a5) | 81.2 → 80.8 (real in both) | 86.3 → 94.5 (real in both) | b3lyp 0.9, wb97x 8.2 | no imaginary mode in the corpus |
| naphthalene+OH+vinyl+ (P3c_55cca3aaf2) | 57.8 → 57.4 (real in both) | 75.8 → 77.6 (real in both) | b3lyp 0.9, wb97x 13.0 | no imaginary mode in the corpus |
| naphthalene+OCH3+vinyl+ (P3c_5d15d13032) | 41.6 → 43.9 (real in both) | 78.2 → 74.2 (real in both) | b3lyp 2.3, wb97x 22.7 | no imaginary mode in the corpus |
| naphthalene+CHO+COOH+ (P3c_67a14c45e8) | 17.4 → 20.3 (real in both) | 55.2 → 58.8 (real in both) | b3lyp 2.9, wb97x 6.1 | no imaginary mode in the corpus |
| pyridine+ (P3c_6e858b26e5) | 294.9 → 295.5 (real in both) | 373.9 → 359.3 (real in both) | b3lyp 1.4, wb97x 14.6 | no imaginary mode in the corpus |
| benzene+ (P3c_8448043181) | 238.7 → 246.5 (real in both) | 298.7 → 298.9 (real in both) | b3lyp 7.9, wb97x 7.1 | no imaginary mode in the corpus |
| benzene+F+ (P3c_8b12a55d3a) | 189.3 → 189.3 (real in both) | 200.9 → 199.6 (real in both) | b3lyp 0.5, wb97x 7.6 | no imaginary mode in the corpus |
| anthracene+ (P3c_a1e6ec1862) | 86.6 → 86.6 (real in both) | 101.7 → 101.5 (real in both) | b3lyp 0.8, wb97x 4.3 | no imaginary mode in the corpus |
| pyrene+ (P3c_cce0ad25a5) | 102.1 → 102.3 (real in both) | 108.4 → 109.4 (real in both) | b3lyp 2.5, wb97x 3.3 | no imaginary mode in the corpus |
| quinoline+ (P3c_ff98e1160d) | 159.7 → 159.7 (real in both) | 172.4 → 173.4 (real in both) | b3lyp 0.5, wb97x 5.1 | no imaginary mode in the corpus |

60 molecules read; 0 healed (analytic route replaces the corpus Hessians in the next release), 7 genuine, 0 not yet available.
