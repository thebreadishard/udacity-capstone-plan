# Proxy transfer check — k = 150, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 2.06 | 2.05 | 3.27 | 4.01 | 0.225 (4 failed) | 143 |
| head_all_es | 0 | 2.02 | 1.93 | 2.88 | 4.08 | 0.210 (4 failed) | 109 |
| head_all | 0 | 2.16 | 2.54 | 3.01 | 4.13 | 0.226 (4 failed) | 72 |
| body1_es | 1 | 2.43 | 2.74 | 3.56 | 4.51 | 0.219 (4 failed) | 111 |
| head_all_es | 1 | 1.94 | 2.47 | 2.78 | 3.79 | 0.211 (4 failed) | 131 |
| head_all | 1 | 2.14 | 2.00 | 3.22 | 4.21 | 0.225 (4 failed) | 69 |
| body1_es | 2 | 1.90 | 2.02 | 2.75 | 3.71 | 0.219 (4 failed) | 191 |
| head_all_es | 2 | 2.09 | 1.81 | 2.98 | 3.87 | 0.213 (4 failed) | 165 |
| head_all | 2 | 2.55 | 3.73 | 3.14 | 4.40 | 0.242 (4 failed) | 69 |
