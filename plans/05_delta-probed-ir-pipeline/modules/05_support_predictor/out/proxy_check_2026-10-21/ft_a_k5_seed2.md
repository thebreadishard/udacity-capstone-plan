# Proxy transfer check — k = 5, seed 2

Base `base_a_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.53 | 77.39 | 31.62 | 34.74 | 0.788 (17 failed) | – |
| head_l2 | 0 | 9.58 | 12.77 | 9.37 | 12.49 | 0.570 (9 failed) | 40 |
| head | 0 | 4.68 | 5.75 | 6.01 | 7.70 | 0.428 (4 failed) | 38 |
| head_all | 0 | 4.56 | 4.13 | 6.35 | 7.88 | 0.356 (4 failed) | 54 |
| scratch | 0 | 7.37 | 8.94 | 6.29 | 9.06 | 0.466 (4 failed) | 12 |
| head_l2 | 1 | 9.66 | 12.57 | 10.61 | 22.05 | 0.585 (7 failed) | 47 |
| head | 1 | 4.65 | 5.27 | 6.05 | 8.46 | 0.415 (4 failed) | 45 |
| head_all | 1 | 4.44 | 3.81 | 6.98 | 7.82 | 0.369 (4 failed) | 66 |
| scratch | 1 | 8.55 | 5.62 | 8.43 | 10.63 | 0.500 (4 failed) | 29 |
| head_l2 | 2 | 9.34 | 14.10 | 8.79 | 13.29 | 0.539 (15 failed) | 45 |
| head | 2 | 3.87 | 5.60 | 5.15 | 6.02 | 0.335 (4 failed) | 45 |
| head_all | 2 | 4.03 | 3.31 | 5.66 | 7.06 | 0.333 (4 failed) | 68 |
| scratch | 2 | 6.89 | 6.17 | 5.79 | 8.37 | 0.416 (4 failed) | 18 |
