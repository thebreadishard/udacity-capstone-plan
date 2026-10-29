# Proxy transfer check — k = 100, seed 2

Base `base_a2_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.32 | 77.92 | 31.88 | 35.51 | 0.771 (15 failed) | – |
| head_all | 0 | 1.84 | 1.98 | 2.91 | 3.38 | 0.229 (4 failed) | 70 |
| head_all_es | 0 | 2.21 | 1.95 | 3.01 | 3.57 | 0.212 (4 failed) | 86 |
| body1_es | 0 | 2.01 | 2.47 | 3.37 | 3.67 | 0.221 (4 failed) | 98 |
| head_all | 1 | 2.01 | 1.98 | 3.10 | 3.68 | 0.206 (4 failed) | 72 |
| head_all_es | 1 | 2.14 | 1.86 | 3.36 | 3.83 | 0.234 (4 failed) | 84 |
| body1_es | 1 | 1.93 | 2.67 | 3.12 | 3.57 | 0.200 (4 failed) | 117 |
| head_all | 2 | 2.43 | 2.73 | 3.51 | 3.57 | 0.200 (4 failed) | 70 |
| head_all_es | 2 | 2.11 | 1.72 | 3.19 | 3.43 | 0.203 (4 failed) | 109 |
| body1_es | 2 | 1.99 | 1.94 | 2.63 | 3.49 | 0.194 (4 failed) | 150 |
