# Proxy transfer check — k = 20, seed 2

Base `base_a_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.53 | 77.39 | 31.62 | 34.74 | 0.788 (17 failed) | – |
| head_l2 | 0 | 9.17 | 12.93 | 8.51 | 13.48 | 0.567 (12 failed) | 52 |
| head | 0 | 4.43 | 6.05 | 5.00 | 6.37 | 0.393 (5 failed) | 50 |
| head_all | 0 | 2.79 | 2.53 | 3.88 | 4.77 | 0.355 (4 failed) | 77 |
| scratch | 0 | 6.80 | 5.52 | 5.72 | 8.06 | 0.421 (4 failed) | 26 |
| head_l2 | 1 | 8.61 | 13.66 | 7.87 | 12.44 | 0.514 (12 failed) | 47 |
| head | 1 | 4.58 | 5.46 | 5.40 | 6.57 | 0.393 (4 failed) | 45 |
| head_all | 1 | 2.48 | 2.35 | 3.63 | 4.87 | 0.277 (4 failed) | 70 |
| scratch | 1 | 4.87 | 3.55 | 5.42 | 6.80 | 0.361 (4 failed) | 88 |
| head_l2 | 2 | 8.84 | 14.72 | 8.82 | 12.58 | 0.518 (11 failed) | 43 |
| head | 2 | 4.65 | 5.63 | 5.27 | 6.31 | 0.413 (4 failed) | 42 |
| head_all | 2 | 2.97 | 2.54 | 4.17 | 4.44 | 0.261 (4 failed) | 65 |
| scratch | 2 | 5.08 | 3.36 | 5.42 | 6.79 | 0.393 (4 failed) | 56 |
