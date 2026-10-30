# Proxy transfer check — k = 10, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 5.10 | 6.09 | 6.31 | 7.64 | 0.362 (4 failed) | 29 |
| body1_es | 1 | 4.38 | 5.20 | 5.28 | 7.50 | 0.373 (4 failed) | 16 |
| body1_es | 2 | 3.95 | 4.67 | 5.62 | 7.67 | 0.372 (5 failed) | 28 |
