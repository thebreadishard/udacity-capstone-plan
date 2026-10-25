# Proxy transfer check — k = 20, seed 0

Base `base_a_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.29 | 77.18 | 31.57 | 35.37 | 0.766 (14 failed) | – |
| head_l2 | 0 | 9.31 | 12.76 | 8.07 | 13.19 | 0.579 (10 failed) | 52 |
| head | 0 | 4.56 | 6.42 | 5.46 | 6.04 | 0.428 (4 failed) | 49 |
| head_all | 0 | 3.44 | 2.69 | 4.04 | 4.90 | 0.252 (4 failed) | 80 |
| scratch | 0 | 6.75 | 6.18 | 5.82 | 8.07 | 0.440 (4 failed) | 28 |
| head_l2 | 1 | 8.77 | 15.11 | 6.72 | 12.43 | 0.564 (15 failed) | 49 |
| head | 1 | 4.64 | 6.23 | 5.43 | 6.13 | 0.375 (4 failed) | 46 |
| head_all | 1 | 2.98 | 2.56 | 5.03 | 5.14 | 0.259 (4 failed) | 72 |
| scratch | 1 | 3.50 | 4.55 | 5.61 | 6.80 | 0.304 (4 failed) | 141 |
| head_l2 | 2 | 9.09 | 14.05 | 7.38 | 11.74 | 0.549 (13 failed) | 44 |
| head | 2 | 4.98 | 7.16 | 5.12 | 6.05 | 0.407 (4 failed) | 44 |
| head_all | 2 | 3.03 | 2.33 | 3.94 | 4.38 | 0.261 (4 failed) | 67 |
| scratch | 2 | 5.99 | 3.55 | 6.14 | 7.53 | 0.406 (5 failed) | 36 |
