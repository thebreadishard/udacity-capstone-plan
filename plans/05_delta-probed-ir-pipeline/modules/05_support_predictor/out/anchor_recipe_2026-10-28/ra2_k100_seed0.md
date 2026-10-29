# Proxy transfer check — k = 100, seed 0

Base `base_a2_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.60 | 77.95 | 31.14 | 34.24 | 0.770 (14 failed) | – |
| head_all | 0 | 2.09 | 1.90 | 2.81 | 3.48 | 0.209 (4 failed) | 69 |
| head_all_es | 0 | 2.06 | 2.06 | 3.10 | 3.94 | 0.229 (4 failed) | 74 |
| body1_es | 0 | 1.93 | 3.04 | 3.04 | 3.92 | 0.206 (4 failed) | 88 |
| head_all | 1 | 2.23 | 1.86 | 4.11 | 4.02 | 0.234 (4 failed) | 71 |
| head_all_es | 1 | 1.88 | 2.10 | 3.30 | 3.54 | 0.220 (4 failed) | 79 |
| body1_es | 1 | 2.03 | 2.21 | 3.05 | 3.85 | 0.222 (4 failed) | 88 |
| head_all | 2 | 1.85 | 1.90 | 3.36 | 3.97 | 0.199 (4 failed) | 70 |
| head_all_es | 2 | 2.10 | 2.36 | 4.15 | 4.25 | 0.223 (4 failed) | 64 |
| body1_es | 2 | 2.07 | 2.15 | 3.53 | 4.07 | 0.222 (4 failed) | 107 |
