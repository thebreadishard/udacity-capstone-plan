# Proxy transfer check — k = 5, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 5.11 | 5.42 | 6.80 | 9.40 | 0.402 (4 failed) | 54 |
| head_all | 1 | 5.72 | 3.70 | 6.61 | 10.34 | 0.414 (4 failed) | 65 |
| head_all | 2 | 5.13 | 5.42 | 6.57 | 7.78 | 0.370 (4 failed) | 68 |
