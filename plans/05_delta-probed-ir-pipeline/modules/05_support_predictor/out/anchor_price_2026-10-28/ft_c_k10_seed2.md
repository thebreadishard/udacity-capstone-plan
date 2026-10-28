# Proxy transfer check — k = 10, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 4.24 | 2.77 | 5.31 | 7.06 | 0.300 (4 failed) | 80 |
| head_all | 1 | 3.64 | 3.39 | 5.64 | 6.66 | 0.325 (4 failed) | 70 |
| head_all | 2 | 3.50 | 3.36 | 5.23 | 7.24 | 0.286 (4 failed) | 89 |
