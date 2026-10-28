# Proxy transfer check — k = 10, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 10; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 4.39 | 4.57 | 5.25 | 6.12 | 0.352 (4 failed) | 82 |
| scratch | 0 | 6.33 | 7.28 | 5.62 | 8.09 | 0.418 (4 failed) | 74 |
