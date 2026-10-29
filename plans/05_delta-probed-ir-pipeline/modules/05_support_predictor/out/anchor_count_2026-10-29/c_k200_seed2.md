# Proxy transfer check — k = 200, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 1.75 | 1.86 | 2.85 | 3.54 | 0.207 (4 failed) | 256 |
| head_all_es | 0 | 2.04 | 2.39 | 2.62 | 3.53 | 0.213 (4 failed) | 198 |
| head_all | 0 | 2.27 | 3.07 | 3.28 | 4.26 | 0.248 (4 failed) | 70 |
