# Proxy transfer check — k = 20, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 20; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 4.41 | 7.41 | 4.65 | 5.80 | 0.287 (4 failed) | 86 |
| scratch | 0 | 3.84 | 3.99 | 4.67 | 6.87 | 0.335 (4 failed) | 139 |
