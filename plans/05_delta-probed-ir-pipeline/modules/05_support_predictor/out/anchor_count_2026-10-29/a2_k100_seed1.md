# Proxy transfer check — k = 100, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| body1_es | 0 | 2.31 | 2.36 | 4.38 | 4.26 | 0.227 (4 failed) | 137 |
| body1_es | 1 | 2.03 | 3.23 | 2.83 | 3.43 | 0.193 (4 failed) | 141 |
| body1_es | 2 | 2.03 | 2.03 | 2.94 | 4.13 | 0.218 (4 failed) | 126 |
