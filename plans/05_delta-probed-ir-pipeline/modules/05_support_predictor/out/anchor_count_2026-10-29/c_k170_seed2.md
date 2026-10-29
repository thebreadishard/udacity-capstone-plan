# Proxy transfer check — k = 170, seed 2

Base `base_c_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.84 | 77.71 | 33.00 | 38.34 | 0.539 (19 failed) | – |
| body1_es | 0 | 1.91 | 2.28 | 3.10 | 3.98 | 0.197 (4 failed) | 153 |
| head_all_es | 0 | 2.12 | 2.08 | 2.67 | 3.86 | 0.221 (4 failed) | 111 |
| head_all | 0 | 2.22 | 3.50 | 3.19 | 4.25 | 0.244 (4 failed) | 69 |
| body1_es | 1 | 2.01 | 2.36 | 2.83 | 3.75 | 0.216 (4 failed) | 192 |
| head_all_es | 1 | 1.99 | 1.83 | 3.16 | 3.89 | 0.217 (4 failed) | 173 |
| head_all | 1 | 2.36 | 3.97 | 2.79 | 3.90 | 0.213 (4 failed) | 70 |
| body1_es | 2 | 2.21 | 2.36 | 2.97 | 4.02 | 0.221 (4 failed) | 128 |
| head_all_es | 2 | 2.05 | 3.02 | 2.71 | 3.76 | 0.225 (4 failed) | 150 |
| head_all | 2 | 2.23 | 2.06 | 2.82 | 3.90 | 0.238 (4 failed) | 70 |
