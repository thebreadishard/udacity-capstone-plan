# Proxy transfer check — k = 20, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 3.90 | 5.61 | 4.05 | 5.94 | 0.311 (4 failed) | 32 |
| body1_es | 1 | 4.30 | 4.45 | 6.23 | 7.09 | 0.311 (4 failed) | 22 |
| body1_es | 2 | 3.35 | 4.25 | 4.70 | 5.85 | 0.305 (4 failed) | 23 |
