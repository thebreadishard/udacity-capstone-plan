# Proxy transfer check — k = 100, seed 0

Base `base_a2_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.60 | 77.95 | 31.14 | 34.24 | 0.770 (14 failed) | – |
| body1_es | 0 | 1.90 | 2.72 | 3.08 | 4.06 | 0.211 (4 failed) | 85 |
| body1_es | 1 | 1.96 | 2.16 | 3.33 | 4.06 | 0.248 (4 failed) | 85 |
| body1_es | 2 | 2.22 | 2.63 | 3.84 | 4.38 | 0.245 (4 failed) | 84 |
