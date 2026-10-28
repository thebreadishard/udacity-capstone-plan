# Proxy transfer check — k = 20, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 20; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| head_all | 0 | 5.79 | 6.64 | 4.98 | 6.38 | 0.308 (4 failed) | 88 |
| scratch | 0 | 3.61 | 4.59 | 5.88 | 6.84 | 0.339 (4 failed) | 159 |
