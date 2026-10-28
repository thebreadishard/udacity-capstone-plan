# Proxy transfer check — k = 20, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 3.46 | 3.22 | 4.01 | 5.50 | 0.280 (5 failed) | 80 |
| head_all | 1 | 3.02 | 3.29 | 3.86 | 5.09 | 0.286 (4 failed) | 69 |
| head_all | 2 | 6.09 | 4.65 | 4.18 | 5.77 | 0.307 (6 failed) | 67 |
