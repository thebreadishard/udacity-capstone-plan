# Proxy transfer check — k = 200, seed 0

Base `base_a_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.29 | 77.18 | 31.57 | 35.37 | 0.766 (14 failed) | – |
| head_l2 | 0 | 9.48 | 12.96 | 8.79 | 12.25 | 0.576 (11 failed) | 48 |
| head | 0 | 4.33 | 7.70 | 4.54 | 5.79 | 0.345 (4 failed) | 45 |
| head_all | 0 | 1.72 | 2.01 | 2.74 | 3.27 | 0.210 (4 failed) | 70 |
| scratch | 0 | 1.59 | 1.76 | 2.66 | 3.55 | 0.187 (4 failed) | 977 |
