# Proxy transfer check — k = 100, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 2.12 | 2.34 | 2.76 | 4.24 | 0.232 (4 failed) | 152 |
| head_all_es | 0 | 2.68 | 2.57 | 3.28 | 4.44 | 0.242 (4 failed) | 59 |
| head_all | 0 | 2.84 | 2.36 | 3.44 | 4.20 | 0.278 (4 failed) | 69 |
| body1_es | 1 | 2.32 | 2.79 | 2.96 | 4.21 | 0.235 (4 failed) | 87 |
| head_all_es | 1 | 2.97 | 2.98 | 3.38 | 4.63 | 0.258 (4 failed) | 58 |
| head_all | 1 | 2.21 | 2.05 | 3.12 | 4.25 | 0.208 (4 failed) | 69 |
| body1_es | 2 | 2.52 | 2.92 | 3.59 | 4.90 | 0.246 (4 failed) | 74 |
| head_all_es | 2 | 2.17 | 2.10 | 2.78 | 4.11 | 0.228 (4 failed) | 133 |
| head_all | 2 | 2.25 | 2.23 | 3.05 | 3.98 | 0.232 (4 failed) | 69 |
