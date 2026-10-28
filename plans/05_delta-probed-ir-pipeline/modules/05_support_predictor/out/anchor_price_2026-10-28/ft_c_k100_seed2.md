# Proxy transfer check — k = 100, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 2.84 | 2.36 | 3.44 | 4.20 | 0.278 (4 failed) | 70 |
| head_all | 1 | 2.21 | 2.05 | 3.12 | 4.25 | 0.208 (4 failed) | 69 |
| head_all | 2 | 2.25 | 2.23 | 3.05 | 3.98 | 0.232 (4 failed) | 69 |
