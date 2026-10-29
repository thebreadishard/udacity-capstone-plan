# Proxy transfer check — k = 170, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 1.95 | 1.88 | 3.24 | 4.00 | 0.195 (4 failed) | 232 |
| head_all_es | 0 | 2.10 | 1.67 | 2.97 | 4.16 | 0.227 (4 failed) | 265 |
| head_all | 0 | 2.62 | 2.39 | 3.99 | 4.58 | 0.243 (4 failed) | 70 |
| body1_es | 1 | 1.73 | 1.95 | 2.70 | 3.85 | 0.205 (4 failed) | 241 |
| head_all_es | 1 | 1.96 | 2.34 | 2.69 | 3.76 | 0.221 (4 failed) | 268 |
| head_all | 1 | 2.32 | 2.08 | 2.94 | 4.19 | 0.214 (4 failed) | 70 |
| body1_es | 2 | 2.06 | 2.12 | 3.19 | 4.08 | 0.221 (4 failed) | 170 |
| head_all_es | 2 | 2.16 | 3.05 | 3.08 | 3.76 | 0.235 (4 failed) | 221 |
| head_all | 2 | 2.19 | 2.04 | 3.10 | 4.11 | 0.243 (4 failed) | 73 |
