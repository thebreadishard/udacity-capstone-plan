# Proxy transfer check — k = 20, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 20; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 6.42 | 3.78 | 4.57 | 6.83 | 0.349 (5 failed) | 86 |
| scratch | 0 | 4.45 | 3.39 | 5.73 | 6.90 | 0.388 (5 failed) | 92 |
