# Proxy transfer check — k = 120, seed 2

Base `base_a2_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.32 | 77.92 | 31.88 | 35.51 | 0.771 (15 failed) | – |
| body1_es | 0 | 2.09 | 1.93 | 2.80 | 3.39 | 0.235 (4 failed) | 133 |
| body1_es | 1 | 1.80 | 1.99 | 2.72 | 3.37 | 0.211 (4 failed) | 196 |
| body1_es | 2 | 2.02 | 2.03 | 3.32 | 3.91 | 0.221 (4 failed) | 133 |
