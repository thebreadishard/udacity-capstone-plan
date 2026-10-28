# Proxy transfer check — k = 10, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 10; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 4.64 | 5.19 | 6.06 | 6.90 | 0.351 (4 failed) | 83 |
| scratch | 0 | 6.36 | 5.50 | 6.40 | 8.15 | 0.466 (4 failed) | 32 |
