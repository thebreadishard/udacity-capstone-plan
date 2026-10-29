# Proxy transfer check — k = 170, seed 0

Base `base_a2_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.60 | 77.95 | 31.14 | 34.24 | 0.770 (14 failed) | – |
| body1_es | 0 | 1.83 | 2.81 | 2.86 | 3.39 | 0.190 (4 failed) | 106 |
| body1_es | 1 | 1.79 | 1.89 | 2.59 | 3.29 | 0.189 (4 failed) | 128 |
| body1_es | 2 | 1.70 | 2.05 | 2.60 | 3.16 | 0.218 (4 failed) | 212 |
