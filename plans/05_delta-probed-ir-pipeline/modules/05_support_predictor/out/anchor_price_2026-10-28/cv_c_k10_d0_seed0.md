# Proxy transfer check — k = 10, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 10; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 3.83 | 3.10 | 4.86 | 6.83 | 0.362 (6 failed) | 84 |
| scratch | 0 | 5.28 | 7.03 | 5.37 | 11.11 | 0.420 (4 failed) | 60 |
