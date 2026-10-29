# Proxy transfer check — k = 150, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| body1_es | 0 | 1.86 | 2.02 | 2.89 | 3.72 | 0.208 (4 failed) | 139 |
| body1_es | 1 | 1.85 | 2.13 | 2.77 | 3.75 | 0.212 (4 failed) | 110 |
| body1_es | 2 | 2.06 | 2.03 | 3.18 | 3.45 | 0.194 (4 failed) | 145 |
