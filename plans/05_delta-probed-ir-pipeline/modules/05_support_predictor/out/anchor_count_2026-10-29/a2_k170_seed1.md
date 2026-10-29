# Proxy transfer check — k = 170, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| body1_es | 0 | 1.94 | 1.87 | 2.62 | 3.37 | 0.201 (4 failed) | 182 |
| body1_es | 1 | 1.79 | 1.68 | 2.95 | 3.33 | 0.193 (4 failed) | 214 |
| body1_es | 2 | 1.57 | 1.69 | 2.77 | 3.04 | 0.194 (4 failed) | 212 |
