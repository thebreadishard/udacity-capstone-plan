# Proxy transfer check — k = 120, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 2.20 | 3.87 | 3.33 | 4.35 | 0.242 (4 failed) | 113 |
| head_all_es | 0 | 2.28 | 2.20 | 3.43 | 4.24 | 0.222 (4 failed) | 120 |
| head_all | 0 | 2.22 | 2.89 | 3.28 | 4.70 | 0.258 (4 failed) | 75 |
| body1_es | 1 | 2.05 | 2.26 | 2.97 | 3.76 | 0.228 (4 failed) | 260 |
| head_all_es | 1 | 2.16 | 2.49 | 2.89 | 3.91 | 0.219 (4 failed) | 112 |
| head_all | 1 | 2.29 | 2.50 | 3.26 | 4.49 | 0.234 (4 failed) | 70 |
| body1_es | 2 | 2.48 | 2.60 | 3.48 | 4.50 | 0.243 (4 failed) | 81 |
| head_all_es | 2 | 2.52 | 3.31 | 3.51 | 4.34 | 0.253 (4 failed) | 105 |
| head_all | 2 | 2.25 | 2.69 | 3.44 | 4.10 | 0.248 (4 failed) | 70 |
