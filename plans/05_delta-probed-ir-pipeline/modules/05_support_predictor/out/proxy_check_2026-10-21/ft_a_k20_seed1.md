# Proxy transfer check — k = 20, seed 1

Base `base_a_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.72 | 78.09 | 31.32 | 35.09 | 0.773 (11 failed) | – |
| head_l2 | 0 | 9.09 | 10.41 | 8.81 | 14.12 | 0.557 (15 failed) | 51 |
| head | 0 | 4.83 | 5.70 | 5.45 | 6.58 | 0.422 (4 failed) | 49 |
| head_all | 0 | 3.27 | 4.41 | 3.99 | 5.16 | 0.291 (4 failed) | 76 |
| scratch | 0 | 4.18 | 5.08 | 4.51 | 7.16 | 0.371 (4 failed) | 137 |
| head_l2 | 1 | 8.47 | 11.40 | 7.77 | 12.75 | 0.539 (12 failed) | 47 |
| head | 1 | 4.69 | 7.41 | 5.67 | 6.49 | 0.418 (4 failed) | 46 |
| head_all | 1 | 2.68 | 2.86 | 3.73 | 4.77 | 0.273 (4 failed) | 75 |
| scratch | 1 | 3.92 | 4.16 | 4.90 | 6.58 | 0.332 (4 failed) | 144 |
| head_l2 | 2 | 8.70 | 11.80 | 8.89 | 12.60 | 0.524 (9 failed) | 44 |
| head | 2 | 5.34 | 6.31 | 5.55 | 6.87 | 0.400 (4 failed) | 43 |
| head_all | 2 | 2.74 | 2.58 | 3.92 | 4.41 | 0.267 (4 failed) | 65 |
| scratch | 2 | 4.54 | 4.22 | 4.90 | 6.47 | 0.406 (4 failed) | 92 |
