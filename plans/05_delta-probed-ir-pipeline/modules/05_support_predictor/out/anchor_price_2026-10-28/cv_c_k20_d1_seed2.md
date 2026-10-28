# Proxy transfer check — k = 20, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 20; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 9.07 | 7.89 | 4.64 | 5.76 | 0.342 (4 failed) | 84 |
| scratch | 0 | 5.01 | 5.78 | 5.18 | 6.70 | 0.408 (4 failed) | 74 |
