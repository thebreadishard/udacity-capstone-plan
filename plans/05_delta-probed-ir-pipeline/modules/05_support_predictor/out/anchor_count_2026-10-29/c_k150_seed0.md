# Proxy transfer check — k = 150, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 1.73 | 2.11 | 2.67 | 3.73 | 0.211 (4 failed) | 325 |
| head_all_es | 0 | 2.15 | 3.35 | 2.92 | 3.99 | 0.210 (4 failed) | 183 |
| head_all | 0 | 2.28 | 2.27 | 3.29 | 4.53 | 0.248 (4 failed) | 74 |
| body1_es | 1 | 2.08 | 2.91 | 3.35 | 4.23 | 0.206 (4 failed) | 172 |
| head_all_es | 1 | 2.38 | 2.75 | 3.33 | 4.45 | 0.216 (4 failed) | 104 |
| head_all | 1 | 2.92 | 2.64 | 3.96 | 5.11 | 0.246 (4 failed) | 68 |
| body1_es | 2 | 2.24 | 2.58 | 3.64 | 4.80 | 0.220 (4 failed) | 123 |
| head_all_es | 2 | 2.07 | 2.05 | 3.22 | 4.38 | 0.216 (4 failed) | 157 |
| head_all | 2 | 2.32 | 3.60 | 3.28 | 4.47 | 0.236 (4 failed) | 86 |
