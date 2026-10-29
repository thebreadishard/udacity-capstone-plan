# Proxy transfer check — k = 100, seed 1

Base `base_a2_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.42 | 78.18 | 31.34 | 34.44 | 0.773 (13 failed) | – |
| head_all | 0 | 1.90 | 2.13 | 2.75 | 3.36 | 0.192 (4 failed) | 70 |
| head_all_es | 0 | 2.20 | 2.82 | 3.00 | 3.59 | 0.209 (4 failed) | 99 |
| body1_es | 0 | 1.96 | 1.92 | 3.27 | 3.73 | 0.208 (4 failed) | 131 |
| head_all | 1 | 2.78 | 2.15 | 2.96 | 3.53 | 0.211 (4 failed) | 72 |
| head_all_es | 1 | 1.96 | 2.33 | 3.01 | 3.31 | 0.206 (4 failed) | 87 |
| body1_es | 1 | 2.29 | 2.92 | 3.13 | 3.51 | 0.213 (4 failed) | 118 |
| head_all | 2 | 2.04 | 2.05 | 3.16 | 3.44 | 0.195 (4 failed) | 72 |
| head_all_es | 2 | 2.04 | 1.91 | 2.92 | 3.86 | 0.212 (4 failed) | 116 |
| body1_es | 2 | 2.23 | 2.26 | 3.23 | 4.47 | 0.214 (5 failed) | 94 |
