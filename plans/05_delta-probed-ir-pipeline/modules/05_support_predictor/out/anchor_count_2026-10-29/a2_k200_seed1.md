# Proxy transfer check — k = 200, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| body1_es | 0 | 1.58 | 1.55 | 2.52 | 3.26 | 0.186 (4 failed) | 233 |
