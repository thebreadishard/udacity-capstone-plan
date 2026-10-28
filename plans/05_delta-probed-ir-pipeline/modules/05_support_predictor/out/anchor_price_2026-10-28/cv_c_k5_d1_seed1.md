# Proxy transfer check — k = 5, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 4.37 | 4.53 | 5.42 | 7.82 | 0.324 (6 failed) | 98 |
| scratch | 0 | 5.68 | 4.10 | 5.55 | 7.84 | 0.428 (4 failed) | 42 |
