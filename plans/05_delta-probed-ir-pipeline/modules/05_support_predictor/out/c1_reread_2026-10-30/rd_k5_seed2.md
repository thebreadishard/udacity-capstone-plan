# Proxy transfer check — k = 5, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 7.34 | 12.17 | 8.71 | 9.50 | 0.468 (5 failed) | 11 |
| body1_es | 1 | 7.96 | 7.00 | 6.64 | 8.78 | 0.446 (4 failed) | 15 |
| body1_es | 2 | 5.51 | 5.92 | 6.85 | 8.60 | 0.408 (5 failed) | 10 |
