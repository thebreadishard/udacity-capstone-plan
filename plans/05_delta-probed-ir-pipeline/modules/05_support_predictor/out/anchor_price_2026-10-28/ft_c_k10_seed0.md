# Proxy transfer check — k = 10, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 3.70 | 3.83 | 4.89 | 6.65 | 0.342 (4 failed) | 76 |
| head_all | 1 | 4.12 | 3.45 | 5.16 | 6.61 | 0.321 (4 failed) | 64 |
| head_all | 2 | 3.60 | 3.42 | 5.29 | 7.17 | 0.295 (4 failed) | 86 |
