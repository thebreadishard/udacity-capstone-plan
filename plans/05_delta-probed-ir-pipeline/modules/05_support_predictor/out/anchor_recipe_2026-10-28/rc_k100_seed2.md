# Proxy transfer check — k = 100, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all_es | 0 | 2.68 | 2.57 | 3.28 | 4.44 | 0.242 (4 failed) | 60 |
| body1_es | 0 | 2.19 | 2.72 | 2.99 | 4.23 | 0.218 (4 failed) | 141 |
| head_all_es | 1 | 2.97 | 2.98 | 3.38 | 4.63 | 0.258 (4 failed) | 59 |
| body1_es | 1 | 2.32 | 2.79 | 2.96 | 4.21 | 0.234 (4 failed) | 85 |
| head_all_es | 2 | 2.17 | 2.10 | 2.78 | 4.11 | 0.228 (4 failed) | 122 |
| body1_es | 2 | 2.52 | 2.92 | 3.59 | 4.90 | 0.246 (4 failed) | 74 |
