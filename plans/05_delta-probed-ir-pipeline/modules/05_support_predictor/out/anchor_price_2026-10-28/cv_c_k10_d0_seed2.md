# Proxy transfer check — k = 10, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 10; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 3.41 | 3.02 | 4.46 | 5.97 | 0.337 (4 failed) | 92 |
| scratch | 0 | 5.96 | 6.62 | 5.73 | 6.83 | 0.453 (4 failed) | 58 |
