# Proxy transfer check — k = 5, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 4.54 | 4.41 | 5.88 | 7.55 | 0.373 (4 failed) | 102 |
| scratch | 0 | 7.15 | 6.61 | 6.14 | 9.14 | 0.425 (4 failed) | 15 |
