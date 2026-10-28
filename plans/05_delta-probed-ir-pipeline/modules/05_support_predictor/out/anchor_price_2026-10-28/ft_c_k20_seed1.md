# Proxy transfer check — k = 20, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 3.62 | 3.35 | 3.79 | 5.23 | 0.319 (4 failed) | 97 |
| head_all | 1 | 3.36 | 3.47 | 4.53 | 6.23 | 0.296 (4 failed) | 82 |
| head_all | 2 | 4.19 | 4.03 | 3.92 | 5.40 | 0.310 (4 failed) | 66 |
