# Proxy transfer check — k = 50, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 3.42 | 2.77 | 3.39 | 4.61 | 0.246 (4 failed) | 70 |
| head_all | 1 | 3.00 | 2.57 | 3.22 | 4.53 | 0.235 (4 failed) | 70 |
| head_all | 2 | 2.89 | 3.20 | 4.52 | 5.20 | 0.260 (4 failed) | 67 |
