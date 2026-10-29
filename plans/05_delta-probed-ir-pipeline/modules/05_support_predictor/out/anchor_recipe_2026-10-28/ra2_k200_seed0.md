# Proxy transfer check — k = 200, seed 0

Base `base_a2_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.60 | 77.95 | 31.14 | 34.24 | 0.770 (14 failed) | – |
| head_all | 0 | 1.79 | 2.12 | 2.78 | 3.33 | 0.224 (4 failed) | 72 |
| head_all_es | 0 | 1.62 | 2.39 | 2.55 | 3.06 | 0.185 (4 failed) | 197 |
| body1_es | 0 | 1.61 | 1.61 | 2.47 | 3.10 | 0.199 (4 failed) | 226 |
