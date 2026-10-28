# Proxy transfer check — k = 100, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 2.36 | 2.51 | 3.24 | 4.75 | 0.239 (4 failed) | 71 |
| head_all | 1 | 2.70 | 2.09 | 3.02 | 4.16 | 0.235 (4 failed) | 70 |
| head_all | 2 | 2.45 | 2.83 | 3.69 | 5.02 | 0.243 (4 failed) | 69 |
