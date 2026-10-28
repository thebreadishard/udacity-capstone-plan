# Proxy transfer check — k = 20, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 20; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 7.16 | 5.28 | 4.34 | 5.56 | 0.301 (4 failed) | 87 |
| scratch | 0 | 4.24 | 5.40 | 5.04 | 7.48 | 0.404 (5 failed) | 134 |
