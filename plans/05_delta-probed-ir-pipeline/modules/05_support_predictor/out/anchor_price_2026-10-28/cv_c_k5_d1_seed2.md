# Proxy transfer check — k = 5, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 4.60 | 4.60 | 6.39 | 8.07 | 0.335 (4 failed) | 94 |
| scratch | 0 | 7.17 | 4.61 | 5.61 | 8.16 | 0.426 (4 failed) | 29 |
