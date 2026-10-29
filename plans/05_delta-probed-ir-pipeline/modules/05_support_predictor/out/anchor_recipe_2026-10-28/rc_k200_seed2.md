# Proxy transfer check — k = 200, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all_es | 0 | 2.04 | 2.39 | 2.62 | 3.53 | 0.213 (4 failed) | 201 |
| body1_es | 0 | 1.95 | 1.92 | 3.23 | 3.85 | 0.219 (4 failed) | 187 |
