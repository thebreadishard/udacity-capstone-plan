# Proxy transfer check — k = 5, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 4.34 | 4.48 | 5.95 | 8.61 | 0.350 (5 failed) | 87 |
| scratch | 0 | 6.13 | 5.70 | 6.00 | 8.72 | 0.421 (4 failed) | 42 |
