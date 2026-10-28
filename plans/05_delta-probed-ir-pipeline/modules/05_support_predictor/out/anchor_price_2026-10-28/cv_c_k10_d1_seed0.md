# Proxy transfer check — k = 10, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 10; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 4.48 | 3.36 | 4.94 | 6.82 | 0.351 (4 failed) | 97 |
| scratch | 0 | 5.81 | 3.89 | 5.95 | 8.39 | 0.417 (4 failed) | 68 |
