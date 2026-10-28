# Proxy transfer check — k = 5, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 4.93 | 5.06 | 5.80 | 7.51 | 0.381 (4 failed) | 55 |
| head_all | 1 | 5.38 | 4.59 | 7.44 | 8.80 | 0.401 (4 failed) | 66 |
| head_all | 2 | 4.19 | 4.63 | 7.04 | 7.66 | 0.356 (4 failed) | 68 |
