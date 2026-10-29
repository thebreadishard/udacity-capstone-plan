# Proxy transfer check — k = 100, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 2.23 | 3.49 | 3.53 | 4.67 | 0.229 (4 failed) | 136 |
| head_all_es | 0 | 2.47 | 2.48 | 3.12 | 4.18 | 0.234 (4 failed) | 120 |
| head_all | 0 | 2.66 | 2.92 | 3.28 | 4.57 | 0.232 (4 failed) | 73 |
| body1_es | 1 | 2.34 | 2.82 | 3.86 | 4.73 | 0.231 (4 failed) | 86 |
| head_all_es | 1 | 2.54 | 2.33 | 3.72 | 4.52 | 0.247 (4 failed) | 119 |
| head_all | 1 | 2.97 | 2.70 | 4.42 | 4.91 | 0.264 (4 failed) | 81 |
| body1_es | 2 | 2.80 | 3.27 | 4.76 | 5.57 | 0.260 (4 failed) | 78 |
| head_all_es | 2 | 2.69 | 2.85 | 4.08 | 5.36 | 0.231 (4 failed) | 84 |
| head_all | 2 | 2.45 | 2.21 | 3.22 | 4.43 | 0.253 (4 failed) | 83 |
