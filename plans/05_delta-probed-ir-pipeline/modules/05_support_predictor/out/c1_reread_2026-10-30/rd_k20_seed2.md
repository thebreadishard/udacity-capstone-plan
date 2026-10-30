# Proxy transfer check — k = 20, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 4.11 | 4.98 | 3.86 | 6.08 | 0.291 (4 failed) | 34 |
| body1_es | 1 | 3.72 | 5.17 | 4.96 | 6.71 | 0.302 (4 failed) | 34 |
| body1_es | 2 | 4.19 | 4.37 | 4.16 | 6.13 | 0.334 (4 failed) | 27 |
