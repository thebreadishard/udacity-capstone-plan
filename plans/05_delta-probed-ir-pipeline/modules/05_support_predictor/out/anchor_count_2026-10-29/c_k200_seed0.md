# Proxy transfer check — k = 200, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 1.75 | 1.83 | 2.85 | 3.74 | 0.196 (4 failed) | 278 |
| head_all_es | 0 | 2.03 | 1.87 | 2.68 | 3.76 | 0.200 (4 failed) | 204 |
| head_all | 0 | 2.27 | 2.39 | 3.33 | 5.09 | 0.246 (4 failed) | 70 |
