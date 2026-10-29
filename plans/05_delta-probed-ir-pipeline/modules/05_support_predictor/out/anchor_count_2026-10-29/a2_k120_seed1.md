# Proxy transfer check — k = 120, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| body1_es | 0 | 2.03 | 2.03 | 3.11 | 3.73 | 0.212 (4 failed) | 112 |
| body1_es | 1 | 1.80 | 2.01 | 2.88 | 3.26 | 0.214 (4 failed) | 170 |
| body1_es | 2 | 1.93 | 2.03 | 2.80 | 3.53 | 0.204 (4 failed) | 125 |
