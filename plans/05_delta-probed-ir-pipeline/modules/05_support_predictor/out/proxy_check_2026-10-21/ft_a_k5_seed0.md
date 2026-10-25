# Proxy transfer check — k = 5, seed 0

Base `base_a_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.29 | 77.18 | 31.57 | 35.37 | 0.766 (14 failed) | – |
| head_l2 | 0 | 10.15 | 10.45 | 8.21 | 12.37 | 0.577 (10 failed) | 39 |
| head | 0 | 5.10 | 6.94 | 6.19 | 7.67 | 0.445 (5 failed) | 36 |
| head_all | 0 | 4.74 | 3.81 | 6.89 | 7.51 | 0.383 (4 failed) | 53 |
| scratch | 0 | 8.74 | 4.83 | 7.95 | 9.24 | 0.520 (4 failed) | 12 |
| head_l2 | 1 | 10.07 | 12.82 | 8.98 | 23.97 | 0.574 (16 failed) | 46 |
| head | 1 | 4.61 | 4.92 | 6.25 | 7.53 | 0.414 (4 failed) | 46 |
| head_all | 1 | 3.96 | 2.99 | 6.50 | 8.37 | 0.309 (6 failed) | 68 |
| scratch | 1 | 8.97 | 4.30 | 7.73 | 9.66 | 0.461 (4 failed) | 23 |
| head_l2 | 2 | 9.57 | 14.05 | 7.32 | 13.65 | 0.577 (13 failed) | 46 |
| head | 2 | 4.28 | 7.59 | 6.82 | 7.47 | 0.416 (4 failed) | 45 |
| head_all | 2 | 3.76 | 4.09 | 6.07 | 7.32 | 0.330 (5 failed) | 69 |
| scratch | 2 | 6.77 | 4.80 | 6.73 | 8.56 | 0.445 (4 failed) | 15 |
