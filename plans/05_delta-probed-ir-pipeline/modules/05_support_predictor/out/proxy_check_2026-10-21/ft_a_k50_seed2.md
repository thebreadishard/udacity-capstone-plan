# Proxy transfer check — k = 50, seed 2

Base `base_a_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.53 | 77.39 | 31.62 | 34.74 | 0.788 (17 failed) | – |
| head_l2 | 0 | 9.30 | 13.17 | 8.97 | 12.87 | 0.540 (11 failed) | 48 |
| head | 0 | 4.15 | 5.08 | 4.85 | 5.28 | 0.336 (4 failed) | 45 |
| head_all | 0 | 2.83 | 2.51 | 4.05 | 4.49 | 0.238 (4 failed) | 69 |
| scratch | 0 | 2.72 | 2.85 | 3.80 | 5.10 | 0.261 (4 failed) | 276 |
| head_l2 | 1 | 9.41 | 11.03 | 10.43 | 12.62 | 0.540 (11 failed) | 45 |
| head | 1 | 4.44 | 5.97 | 4.55 | 5.31 | 0.350 (4 failed) | 45 |
| head_all | 1 | 3.04 | 2.91 | 3.28 | 3.96 | 0.218 (4 failed) | 70 |
| scratch | 1 | 3.99 | 3.74 | 5.31 | 6.32 | 0.323 (4 failed) | 138 |
| head_l2 | 2 | 9.28 | 13.30 | 9.78 | 12.68 | 0.541 (11 failed) | 45 |
| head | 2 | 4.14 | 5.21 | 4.66 | 5.29 | 0.339 (4 failed) | 44 |
| head_all | 2 | 2.30 | 2.97 | 3.51 | 4.11 | 0.213 (4 failed) | 68 |
| scratch | 2 | 3.53 | 2.96 | 4.72 | 5.58 | 0.317 (4 failed) | 159 |
