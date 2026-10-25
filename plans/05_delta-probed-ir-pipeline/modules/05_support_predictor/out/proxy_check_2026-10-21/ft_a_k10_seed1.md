# Proxy transfer check — k = 10, seed 1

Base `base_a_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.72 | 78.09 | 31.32 | 35.09 | 0.773 (11 failed) | – |
| head_l2 | 0 | 9.44 | 11.82 | 10.19 | 26.15 | 0.543 (9 failed) | 50 |
| head | 0 | 4.29 | 5.61 | 5.17 | 6.20 | 0.340 (4 failed) | 48 |
| head_all | 0 | 3.87 | 4.04 | 4.68 | 6.58 | 0.326 (4 failed) | 77 |
| scratch | 0 | 4.49 | 4.08 | 6.30 | 9.47 | 0.381 (4 failed) | 68 |
| head_l2 | 1 | 9.14 | 9.29 | 8.39 | 13.28 | 0.550 (14 failed) | 42 |
| head | 1 | 4.55 | 6.07 | 5.43 | 6.36 | 0.394 (4 failed) | 43 |
| head_all | 1 | 3.60 | 4.48 | 5.25 | 6.26 | 0.286 (4 failed) | 66 |
| scratch | 1 | 6.73 | 3.91 | 6.76 | 8.62 | 0.424 (4 failed) | 20 |
| head_l2 | 2 | 9.54 | 9.20 | 8.47 | 15.87 | 0.574 (9 failed) | 54 |
| head | 2 | 4.27 | 6.23 | 5.15 | 6.25 | 0.380 (5 failed) | 53 |
| head_all | 2 | 3.77 | 3.52 | 4.98 | 5.92 | 0.261 (4 failed) | 90 |
| scratch | 2 | 4.68 | 3.69 | 5.74 | 8.16 | 0.372 (4 failed) | 64 |
