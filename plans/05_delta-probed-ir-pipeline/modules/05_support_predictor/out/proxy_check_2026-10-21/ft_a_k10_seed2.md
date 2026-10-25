# Proxy transfer check — k = 10, seed 2

Base `base_a_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.53 | 77.39 | 31.62 | 34.74 | 0.788 (17 failed) | – |
| head_l2 | 0 | 9.46 | 13.12 | 9.61 | 21.05 | 0.580 (9 failed) | 50 |
| head | 0 | 4.27 | 5.76 | 5.40 | 6.73 | 0.418 (4 failed) | 47 |
| head_all | 0 | 3.14 | 3.13 | 5.13 | 6.13 | 0.301 (4 failed) | 76 |
| scratch | 0 | 4.67 | 2.77 | 5.88 | 8.88 | 0.364 (4 failed) | 77 |
| head_l2 | 1 | 9.06 | 13.98 | 7.97 | 12.71 | 0.546 (11 failed) | 43 |
| head | 1 | 4.25 | 4.91 | 5.26 | 6.35 | 0.369 (4 failed) | 42 |
| head_all | 1 | 3.89 | 3.54 | 5.14 | 6.30 | 0.362 (4 failed) | 65 |
| scratch | 1 | 5.79 | 5.88 | 6.56 | 8.14 | 0.422 (4 failed) | 43 |
| head_l2 | 2 | 9.57 | 12.50 | 8.08 | 14.81 | 0.562 (12 failed) | 53 |
| head | 2 | 3.73 | 5.58 | 4.84 | 6.35 | 0.353 (5 failed) | 52 |
| head_all | 2 | 2.99 | 2.72 | 4.50 | 5.97 | 0.282 (4 failed) | 84 |
| scratch | 2 | 5.47 | 6.53 | 5.77 | 8.58 | 0.376 (4 failed) | 81 |
