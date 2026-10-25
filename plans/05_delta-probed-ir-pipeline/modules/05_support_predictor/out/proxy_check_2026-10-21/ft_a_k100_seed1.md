# Proxy transfer check — k = 100, seed 1

Base `base_a_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.72 | 78.09 | 31.32 | 35.09 | 0.773 (11 failed) | – |
| head_l2 | 0 | 9.01 | 12.86 | 9.99 | 12.91 | 0.540 (8 failed) | 46 |
| head | 0 | 4.83 | 6.04 | 5.27 | 6.05 | 0.371 (4 failed) | 44 |
| head_all | 0 | 2.06 | 2.79 | 3.25 | 4.23 | 0.202 (4 failed) | 67 |
| scratch | 0 | 2.11 | 2.24 | 3.21 | 4.22 | 0.246 (4 failed) | 629 |
| head_l2 | 1 | 8.74 | 11.91 | 9.18 | 12.73 | 0.529 (10 failed) | 45 |
| head | 1 | 4.67 | 6.36 | 5.43 | 5.93 | 0.359 (4 failed) | 45 |
| head_all | 1 | 1.88 | 2.93 | 2.82 | 3.90 | 0.213 (4 failed) | 70 |
| scratch | 1 | 2.15 | 2.08 | 3.69 | 4.35 | 0.245 (4 failed) | 586 |
| head_l2 | 2 | 8.96 | 12.76 | 9.79 | 13.29 | 0.531 (13 failed) | 45 |
| head | 2 | 4.36 | 7.55 | 4.89 | 5.35 | 0.359 (4 failed) | 45 |
| head_all | 2 | 2.02 | 2.34 | 3.24 | 3.54 | 0.181 (4 failed) | 69 |
| scratch | 2 | 2.47 | 2.22 | 3.67 | 5.09 | 0.268 (4 failed) | 323 |
