# Proxy transfer check — k = 20, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 20; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 4.04 | 7.26 | 3.98 | 5.57 | 0.333 (4 failed) | 89 |
| scratch | 0 | 3.48 | 3.72 | 4.52 | 6.69 | 0.367 (4 failed) | 170 |
