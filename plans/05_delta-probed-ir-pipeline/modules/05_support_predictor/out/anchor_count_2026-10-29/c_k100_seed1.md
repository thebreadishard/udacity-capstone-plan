# Proxy transfer check — k = 100, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 2.19 | 2.73 | 3.21 | 4.39 | 0.232 (4 failed) | 108 |
| head_all_es | 0 | 2.36 | 2.40 | 3.19 | 4.61 | 0.269 (5 failed) | 80 |
| head_all | 0 | 2.36 | 2.51 | 3.24 | 4.75 | 0.239 (4 failed) | 68 |
| body1_es | 1 | 2.13 | 1.92 | 2.91 | 3.98 | 0.232 (4 failed) | 128 |
| head_all_es | 1 | 2.62 | 4.54 | 3.61 | 4.68 | 0.246 (4 failed) | 82 |
| head_all | 1 | 2.70 | 2.09 | 3.02 | 4.16 | 0.235 (4 failed) | 73 |
| body1_es | 2 | 2.49 | 2.69 | 3.25 | 4.43 | 0.225 (4 failed) | 132 |
| head_all_es | 2 | 2.35 | 2.72 | 2.86 | 4.13 | 0.214 (4 failed) | 107 |
| head_all | 2 | 2.45 | 2.83 | 3.69 | 5.02 | 0.243 (4 failed) | 70 |
