# Proxy transfer check — k = 170, seed 2

Base `base_a2_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.32 | 77.92 | 31.88 | 35.51 | 0.771 (15 failed) | – |
| body1_es | 0 | 1.66 | 1.53 | 2.75 | 3.22 | 0.193 (4 failed) | 187 |
| body1_es | 1 | 1.82 | 1.63 | 2.67 | 3.33 | 0.191 (4 failed) | 159 |
| body1_es | 2 | 1.69 | 1.56 | 2.59 | 3.03 | 0.184 (4 failed) | 286 |
