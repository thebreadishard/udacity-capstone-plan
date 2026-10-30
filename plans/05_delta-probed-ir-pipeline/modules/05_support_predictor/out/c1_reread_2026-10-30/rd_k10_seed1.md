# Proxy transfer check — k = 10, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 4.47 | 7.66 | 6.00 | 7.70 | 0.337 (4 failed) | 17 |
| body1_es | 1 | 4.40 | 5.45 | 6.56 | 7.76 | 0.368 (5 failed) | 13 |
| body1_es | 2 | 3.47 | 4.36 | 5.80 | 6.95 | 0.301 (5 failed) | 17 |
