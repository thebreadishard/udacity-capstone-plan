# Proxy transfer check — k = 100, seed 2

Base `base_a2_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.32 | 77.92 | 31.88 | 35.51 | 0.771 (15 failed) | – |
| body1_es | 0 | 2.01 | 2.47 | 3.37 | 3.67 | 0.220 (4 failed) | 97 |
| body1_es | 1 | 1.93 | 2.69 | 3.12 | 3.58 | 0.200 (4 failed) | 118 |
| body1_es | 2 | 1.99 | 1.88 | 3.07 | 3.60 | 0.200 (4 failed) | 111 |
