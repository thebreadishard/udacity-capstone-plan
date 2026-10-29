# Proxy transfer check — k = 100, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all_es | 0 | 2.47 | 2.48 | 3.12 | 4.18 | 0.234 (4 failed) | 111 |
| body1_es | 0 | 2.47 | 4.56 | 3.31 | 4.49 | 0.235 (4 failed) | 132 |
| head_all_es | 1 | 2.54 | 2.33 | 3.72 | 4.52 | 0.247 (4 failed) | 100 |
| body1_es | 1 | 2.34 | 2.82 | 3.86 | 4.73 | 0.231 (4 failed) | 76 |
| head_all_es | 2 | 2.69 | 2.85 | 4.08 | 5.36 | 0.231 (4 failed) | 71 |
| body1_es | 2 | 2.95 | 3.59 | 5.03 | 5.82 | 0.274 (4 failed) | 70 |
