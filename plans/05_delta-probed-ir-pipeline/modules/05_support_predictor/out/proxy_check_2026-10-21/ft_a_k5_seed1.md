# Proxy transfer check — k = 5, seed 1

Base `base_a_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.72 | 78.09 | 31.32 | 35.09 | 0.773 (11 failed) | – |
| head_l2 | 0 | 9.71 | 9.04 | 9.56 | 13.30 | 0.572 (8 failed) | 39 |
| head | 0 | 4.72 | 6.12 | 5.39 | 6.37 | 0.413 (4 failed) | 36 |
| head_all | 0 | 4.76 | 5.58 | 7.20 | 8.35 | 0.389 (5 failed) | 52 |
| scratch | 0 | 8.58 | 4.34 | 8.51 | 9.88 | 0.551 (4 failed) | 16 |
| head_l2 | 1 | 9.71 | 9.79 | 9.45 | 24.68 | 0.582 (15 failed) | 44 |
| head | 1 | 4.96 | 5.74 | 5.92 | 7.75 | 0.404 (4 failed) | 44 |
| head_all | 1 | 4.27 | 4.65 | 7.29 | 8.53 | 0.379 (4 failed) | 66 |
| scratch | 1 | 8.94 | 5.50 | 7.20 | 9.36 | 0.446 (4 failed) | 21 |
| head_l2 | 2 | 9.35 | 11.75 | 9.21 | 14.09 | 0.568 (13 failed) | 46 |
| head | 2 | 4.12 | 5.32 | 5.35 | 5.56 | 0.365 (5 failed) | 45 |
| head_all | 2 | 4.65 | 4.56 | 5.98 | 7.40 | 0.331 (5 failed) | 69 |
| scratch | 2 | 7.14 | 5.39 | 7.32 | 9.07 | 0.447 (4 failed) | 14 |
