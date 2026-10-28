# Proxy transfer check — k = 5, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 6.42 | 5.07 | 5.61 | 8.11 | 0.425 (5 failed) | 95 |
| scratch | 0 | 6.50 | 4.78 | 6.02 | 9.43 | 0.445 (4 failed) | 32 |
