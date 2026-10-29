# Proxy transfer check — k = 200, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all_es | 0 | 2.03 | 1.87 | 2.68 | 3.76 | 0.200 (4 failed) | 202 |
| body1_es | 0 | 1.72 | 1.86 | 2.63 | 3.63 | 0.192 (4 failed) | 303 |
