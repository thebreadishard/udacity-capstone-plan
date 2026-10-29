# Proxy transfer check — k = 170, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 2.10 | 2.72 | 2.99 | 4.17 | 0.229 (4 failed) | 190 |
| head_all_es | 0 | 2.21 | 2.97 | 3.07 | 3.81 | 0.216 (4 failed) | 112 |
| head_all | 0 | 1.99 | 2.02 | 3.16 | 4.48 | 0.222 (4 failed) | 72 |
| body1_es | 1 | 2.27 | 2.09 | 3.14 | 4.39 | 0.244 (4 failed) | 88 |
| head_all_es | 1 | 2.45 | 2.44 | 2.67 | 3.64 | 0.223 (4 failed) | 157 |
| head_all | 1 | 2.19 | 2.50 | 3.00 | 3.95 | 0.214 (4 failed) | 69 |
| body1_es | 2 | 2.19 | 2.03 | 2.64 | 3.64 | 0.200 (4 failed) | 366 |
| head_all_es | 2 | 1.99 | 2.56 | 2.71 | 3.64 | 0.219 (4 failed) | 212 |
| head_all | 2 | 1.99 | 1.88 | 2.83 | 3.96 | 0.218 (4 failed) | 71 |
