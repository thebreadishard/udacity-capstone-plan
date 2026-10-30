# Proxy transfer check — k = 5, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 5.59 | 7.15 | 7.74 | 8.88 | 0.411 (4 failed) | 14 |
| body1_es | 1 | 6.64 | 5.29 | 8.43 | 8.49 | 0.460 (4 failed) | 11 |
| body1_es | 2 | 5.83 | 6.09 | 7.51 | 8.61 | 0.426 (4 failed) | 21 |
