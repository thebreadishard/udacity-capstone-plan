# Learning curve, layer A proxy (ωB97X − B3LYP first-order shifts) — 2026-09-19 10:12

45 molecules; 12 held out (hash order); seeds [0, 1, 2]; 600 epochs; RMS in cm⁻¹ on held-out modes.

| n_train | CH-stretch model / median / zero | CH-oop model / median / zero | ring-ip model / median / zero | other model / median / zero | all (model) | train |
|---|---|---|---|---|---|---|
| 5 | 2.44 / 1.73 / 43.76 | 5.80 / 8.55 / 23.59 | 14.87 / 18.56 / 21.89 | 38.52 / 11.23 / 14.85 | 24.27 | 3.70 |
| 10 | 1.89 / 1.73 / 43.76 | 5.30 / 8.60 / 23.59 | 13.10 / 18.65 / 21.89 | 31.27 / 11.19 / 14.85 | 19.98 | 4.62 |
| 20 | 1.79 / 1.73 / 43.76 | 4.22 / 8.55 / 23.59 | 12.51 / 18.49 / 21.89 | 29.32 / 11.14 / 14.85 | 18.77 | 6.84 |
| 30 | 1.78 / 1.73 / 43.76 | 4.31 / 8.51 / 23.59 | 12.41 / 18.49 / 21.89 | 26.63 / 11.14 / 14.85 | 17.62 | 8.25 |

Power-law slope of log RMS vs log n per family: CH-stretch -0.17, CH-oop -0.19, ring-ip -0.10, other -0.19

Held-out modes per family: CH-stretch 107, CH-oop 71, ring-ip 287, other 231
