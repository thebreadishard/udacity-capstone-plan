# Proxy transfer check — k = 100, seed 2

Base `base_a_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.53 | 77.39 | 31.62 | 34.74 | 0.788 (17 failed) | – |
| head_l2 | 0 | 9.00 | 15.90 | 9.93 | 12.69 | 0.520 (11 failed) | 46 |
| head | 0 | 4.37 | 7.28 | 4.88 | 5.79 | 0.410 (4 failed) | 44 |
| head_all | 0 | 1.89 | 1.99 | 2.84 | 3.74 | 0.231 (4 failed) | 68 |
| scratch | 0 | 2.28 | 2.20 | 3.37 | 4.47 | 0.255 (4 failed) | 525 |
| head_l2 | 1 | 8.77 | 15.64 | 9.12 | 12.20 | 0.516 (10 failed) | 46 |
| head | 1 | 4.43 | 7.06 | 4.75 | 5.79 | 0.406 (4 failed) | 46 |
| head_all | 1 | 1.92 | 1.94 | 3.46 | 3.76 | 0.201 (4 failed) | 70 |
| scratch | 1 | 2.09 | 2.12 | 3.11 | 4.21 | 0.221 (4 failed) | 600 |
| head_l2 | 2 | 8.96 | 16.02 | 9.97 | 12.61 | 0.529 (10 failed) | 45 |
| head | 2 | 4.20 | 8.02 | 4.55 | 5.58 | 0.348 (4 failed) | 45 |
| head_all | 2 | 2.07 | 1.94 | 3.16 | 3.69 | 0.229 (4 failed) | 69 |
| scratch | 2 | 2.12 | 2.19 | 3.30 | 4.68 | 0.248 (4 failed) | 460 |
