# Proxy transfer check — k = 200, seed 2

Base `base_a2_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.32 | 77.92 | 31.88 | 35.51 | 0.771 (15 failed) | – |
| head_all | 0 | 1.80 | 1.56 | 2.78 | 3.37 | 0.190 (4 failed) | 72 |
| head_all_es | 0 | 1.94 | 2.46 | 2.61 | 3.11 | 0.192 (4 failed) | 154 |
| body1_es | 0 | 1.83 | 1.81 | 2.65 | 3.13 | 0.205 (4 failed) | 280 |
