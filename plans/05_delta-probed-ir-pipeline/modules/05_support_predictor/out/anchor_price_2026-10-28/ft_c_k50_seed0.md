# Proxy transfer check — k = 50, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 4.12 | 4.07 | 3.93 | 4.90 | 0.248 (4 failed) | 73 |
| head_all | 1 | 3.19 | 2.80 | 4.20 | 4.92 | 0.254 (4 failed) | 71 |
| head_all | 2 | 2.68 | 3.90 | 4.08 | 4.96 | 0.249 (4 failed) | 66 |
