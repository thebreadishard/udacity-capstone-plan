# Proxy transfer check — k = 100, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all_es | 0 | 2.36 | 2.40 | 3.19 | 4.61 | 0.269 (5 failed) | 88 |
| body1_es | 0 | 2.20 | 2.18 | 3.20 | 4.23 | 0.219 (4 failed) | 121 |
| head_all_es | 1 | 2.62 | 4.54 | 3.61 | 4.68 | 0.246 (4 failed) | 85 |
| body1_es | 1 | 2.28 | 1.91 | 3.39 | 4.36 | 0.219 (4 failed) | 114 |
| head_all_es | 2 | 2.35 | 2.72 | 2.86 | 4.13 | 0.214 (4 failed) | 118 |
| body1_es | 2 | 2.26 | 2.52 | 3.12 | 4.22 | 0.216 (4 failed) | 154 |
