# Proxy transfer check — k = 150, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 2.03 | 2.13 | 2.95 | 3.84 | 0.205 (4 failed) | 148 |
| head_all_es | 0 | 2.04 | 2.01 | 2.81 | 3.87 | 0.213 (4 failed) | 112 |
| head_all | 0 | 2.28 | 2.95 | 2.82 | 3.97 | 0.237 (4 failed) | 67 |
| body1_es | 1 | 1.98 | 2.51 | 3.18 | 4.01 | 0.220 (4 failed) | 189 |
| head_all_es | 1 | 2.15 | 2.14 | 3.17 | 3.92 | 0.206 (4 failed) | 187 |
| head_all | 1 | 2.47 | 3.46 | 3.92 | 4.44 | 0.226 (4 failed) | 70 |
| body1_es | 2 | 1.98 | 2.92 | 2.86 | 3.82 | 0.223 (4 failed) | 162 |
| head_all_es | 2 | 2.13 | 1.83 | 2.62 | 4.05 | 0.215 (4 failed) | 129 |
| head_all | 2 | 2.05 | 2.06 | 3.01 | 4.36 | 0.215 (4 failed) | 69 |
