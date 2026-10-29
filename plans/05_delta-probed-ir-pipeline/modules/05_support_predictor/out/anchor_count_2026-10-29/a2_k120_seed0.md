# Proxy transfer check — k = 120, seed 0

Base `base_a2_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.60 | 77.95 | 31.14 | 34.24 | 0.770 (14 failed) | – |
| body1_es | 0 | 1.79 | 2.13 | 2.94 | 3.61 | 0.219 (4 failed) | 128 |
| body1_es | 1 | 1.99 | 2.20 | 2.87 | 3.43 | 0.231 (4 failed) | 145 |
| body1_es | 2 | 2.02 | 2.40 | 3.15 | 3.79 | 0.204 (4 failed) | 115 |
