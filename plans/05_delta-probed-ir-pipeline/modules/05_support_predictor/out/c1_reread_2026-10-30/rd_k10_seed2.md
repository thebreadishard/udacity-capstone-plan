# Proxy transfer check — k = 10, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 5.23 | 7.09 | 6.41 | 8.37 | 0.420 (4 failed) | 22 |
| body1_es | 1 | 4.66 | 5.32 | 5.63 | 7.76 | 0.358 (4 failed) | 14 |
| body1_es | 2 | 3.76 | 6.41 | 5.66 | 7.38 | 0.318 (4 failed) | 32 |
