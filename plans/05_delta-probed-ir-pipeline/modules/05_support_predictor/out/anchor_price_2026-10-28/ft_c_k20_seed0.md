# Proxy transfer check — k = 20, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 3.59 | 4.99 | 4.05 | 6.02 | 0.347 (4 failed) | 78 |
| head_all | 1 | 3.29 | 3.06 | 3.73 | 5.28 | 0.276 (4 failed) | 70 |
| head_all | 2 | 5.64 | 4.82 | 3.83 | 5.25 | 0.320 (4 failed) | 64 |
