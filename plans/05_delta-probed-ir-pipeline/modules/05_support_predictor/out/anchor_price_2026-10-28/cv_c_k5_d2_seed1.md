# Proxy transfer check — k = 5, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 5.84 | 4.05 | 6.23 | 8.23 | 0.405 (4 failed) | 93 |
| scratch | 0 | 7.64 | 6.36 | 6.07 | 9.71 | 0.431 (4 failed) | 22 |
