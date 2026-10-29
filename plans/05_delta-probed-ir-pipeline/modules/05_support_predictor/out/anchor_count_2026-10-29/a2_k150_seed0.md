# Proxy transfer check — k = 150, seed 0

Base `base_a2_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.60 | 77.95 | 31.14 | 34.24 | 0.770 (14 failed) | – |
| body1_es | 0 | 1.83 | 2.35 | 2.59 | 3.12 | 0.206 (4 failed) | 233 |
| body1_es | 1 | 1.71 | 2.06 | 2.77 | 3.37 | 0.183 (4 failed) | 140 |
| body1_es | 2 | 1.86 | 2.30 | 2.90 | 3.76 | 0.205 (4 failed) | 115 |
