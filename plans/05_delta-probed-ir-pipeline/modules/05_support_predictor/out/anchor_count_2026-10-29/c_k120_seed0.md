# Proxy transfer check — k = 120, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 2.26 | 2.57 | 3.95 | 5.03 | 0.235 (4 failed) | 128 |
| head_all_es | 0 | 2.28 | 2.26 | 2.99 | 4.27 | 0.236 (4 failed) | 185 |
| head_all | 0 | 2.72 | 3.29 | 3.67 | 4.90 | 0.235 (4 failed) | 68 |
| body1_es | 1 | 2.05 | 2.29 | 3.41 | 4.44 | 0.225 (4 failed) | 132 |
| head_all_es | 1 | 2.29 | 2.24 | 3.52 | 4.58 | 0.212 (4 failed) | 88 |
| head_all | 1 | 2.26 | 2.47 | 3.49 | 4.56 | 0.240 (4 failed) | 71 |
| body1_es | 2 | 2.07 | 1.76 | 3.29 | 4.29 | 0.201 (4 failed) | 327 |
| head_all_es | 2 | 2.53 | 2.22 | 3.12 | 4.61 | 0.256 (4 failed) | 209 |
| head_all | 2 | 2.71 | 3.27 | 3.68 | 4.95 | 0.264 (4 failed) | 79 |
