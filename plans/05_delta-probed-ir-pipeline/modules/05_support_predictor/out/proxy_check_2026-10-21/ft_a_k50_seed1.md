# Proxy transfer check — k = 50, seed 1

Base `base_a_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.72 | 78.09 | 31.32 | 35.09 | 0.773 (11 failed) | – |
| head_l2 | 0 | 9.18 | 10.83 | 9.06 | 13.54 | 0.531 (12 failed) | 47 |
| head | 0 | 4.46 | 5.01 | 4.89 | 4.95 | 0.379 (4 failed) | 46 |
| head_all | 0 | 3.44 | 2.95 | 3.55 | 4.11 | 0.204 (4 failed) | 71 |
| scratch | 0 | 2.78 | 2.53 | 4.41 | 5.43 | 0.258 (4 failed) | 209 |
| head_l2 | 1 | 9.45 | 8.27 | 10.48 | 13.00 | 0.530 (10 failed) | 46 |
| head | 1 | 4.98 | 4.90 | 4.80 | 5.31 | 0.363 (4 failed) | 45 |
| head_all | 1 | 2.47 | 2.44 | 4.26 | 4.19 | 0.235 (4 failed) | 70 |
| scratch | 1 | 3.07 | 2.59 | 4.64 | 5.55 | 0.267 (4 failed) | 182 |
| head_l2 | 2 | 9.28 | 11.25 | 10.27 | 13.43 | 0.532 (15 failed) | 44 |
| head | 2 | 4.41 | 5.02 | 4.68 | 5.15 | 0.368 (4 failed) | 44 |
| head_all | 2 | 2.62 | 2.66 | 4.55 | 4.80 | 0.226 (4 failed) | 67 |
| scratch | 2 | 3.23 | 2.87 | 4.95 | 5.59 | 0.301 (4 failed) | 225 |
