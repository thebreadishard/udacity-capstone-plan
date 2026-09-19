# Learning curve, second pass — environment descriptors as the one change (2026-09-19 16:44)

45 molecules, 12 held out (same hash split as the first pass), 600 steps, seeds [0, 1, 2]; held-out RMS in cm⁻¹, A / B.

| n_train | CH-stretch | CH-oop | ring-ip | other | train (all) A / B |
|---|---|---|---|---|---|
| 5 | 2.89 / **1.90** | 5.69 / **4.78** | 14.99 / **15.51** | 37.47 / **35.78** | 3.57 / 1.80 |
| 10 | 1.91 / **1.81** | 5.04 / **4.42** | 12.87 / **12.87** | 31.90 / **36.21** | 4.60 / 2.07 |
| 20 | 1.86 / **1.54** | 4.10 / **4.39** | 12.19 / **12.18** | 28.99 / **32.53** | 7.03 / 5.34 |
| 30 | 1.87 / **1.60** | 4.55 / **5.04** | 12.44 / **12.38** | 25.39 / **28.48** | 7.60 / 4.99 |

Zero rule: CH-stretch 43.76, CH-oop 23.59, ring-ip 21.89, other 14.85
Slopes A: CH-stretch -0.23, CH-oop -0.15, ring-ip -0.11, other -0.21
Slopes B: CH-stretch -0.11, CH-oop +0.02, ring-ip -0.13, other -0.12
