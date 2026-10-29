# Proxy transfer check — k = 200, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| head_all | 0 | 1.85 | 2.76 | 2.80 | 3.37 | 0.201 (4 failed) | 72 |
| head_all_es | 0 | 1.68 | 1.74 | 2.71 | 3.35 | 0.205 (4 failed) | 137 |
| body1_es | 0 | 1.53 | 1.59 | 2.54 | 3.05 | 0.182 (4 failed) | 285 |
