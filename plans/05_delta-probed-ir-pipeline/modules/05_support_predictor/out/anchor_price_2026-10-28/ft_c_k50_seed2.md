# Proxy transfer check — k = 50, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 3.03 | 3.14 | 3.50 | 4.57 | 0.214 (4 failed) | 73 |
| head_all | 1 | 2.71 | 3.14 | 3.59 | 4.70 | 0.249 (4 failed) | 76 |
| head_all | 2 | 2.59 | 2.46 | 3.66 | 5.38 | 0.262 (4 failed) | 70 |
