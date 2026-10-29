# Proxy transfer check — k = 200, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 1.62 | 1.60 | 2.49 | 3.48 | 0.187 (4 failed) | 372 |
| head_all_es | 0 | 2.14 | 2.00 | 2.90 | 3.61 | 0.233 (4 failed) | 195 |
| head_all | 0 | 1.98 | 5.20 | 3.39 | 4.17 | 0.212 (4 failed) | 70 |
