# Proxy transfer check — k = 150, seed 2

Base `base_a2_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.32 | 77.92 | 31.88 | 35.51 | 0.771 (15 failed) | – |
| body1_es | 0 | 1.96 | 2.74 | 2.74 | 3.36 | 0.212 (4 failed) | 138 |
| body1_es | 1 | 1.92 | 1.85 | 2.91 | 3.47 | 0.211 (4 failed) | 186 |
| body1_es | 2 | 1.93 | 1.73 | 2.79 | 3.30 | 0.188 (4 failed) | 204 |
