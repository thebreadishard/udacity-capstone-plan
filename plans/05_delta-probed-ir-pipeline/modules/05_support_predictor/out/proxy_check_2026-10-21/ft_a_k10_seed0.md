# Proxy transfer check — k = 10, seed 0

Base `base_a_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.29 | 77.18 | 31.57 | 35.37 | 0.766 (14 failed) | – |
| head_l2 | 0 | 9.71 | 13.17 | 8.36 | 22.37 | 0.564 (14 failed) | 51 |
| head | 0 | 4.77 | 5.98 | 5.21 | 7.00 | 0.371 (6 failed) | 48 |
| head_all | 0 | 3.79 | 3.83 | 5.00 | 6.54 | 0.295 (4 failed) | 77 |
| scratch | 0 | 6.98 | 5.48 | 6.19 | 8.52 | 0.430 (4 failed) | 19 |
| head_l2 | 1 | 9.49 | 12.94 | 7.29 | 12.57 | 0.571 (18 failed) | 45 |
| head | 1 | 4.70 | 8.04 | 5.60 | 6.27 | 0.427 (4 failed) | 44 |
| head_all | 1 | 3.52 | 3.85 | 6.22 | 7.52 | 0.323 (4 failed) | 68 |
| scratch | 1 | 6.03 | 6.28 | 6.67 | 8.78 | 0.427 (4 failed) | 44 |
| head_l2 | 2 | 9.77 | 12.20 | 7.61 | 14.47 | 0.565 (8 failed) | 53 |
| head | 2 | 3.81 | 7.46 | 4.98 | 7.09 | 0.386 (4 failed) | 52 |
| head_all | 2 | 3.54 | 3.55 | 4.85 | 6.43 | 0.295 (4 failed) | 84 |
| scratch | 2 | 4.79 | 3.83 | 6.54 | 8.48 | 0.372 (5 failed) | 71 |
