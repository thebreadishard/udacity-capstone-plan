# Proxy transfer check — k = 5, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 5; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 6.33 | 5.31 | 5.38 | 7.88 | 0.400 (4 failed) | 104 |
| scratch | 0 | 7.11 | 4.91 | 6.23 | 8.97 | 0.433 (4 failed) | 15 |
