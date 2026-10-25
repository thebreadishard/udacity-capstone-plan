# Proxy transfer check — k = 200, seed 2

Base `base_a_model_n750_seed2.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.53 | 77.39 | 31.62 | 34.74 | 0.788 (17 failed) | – |
| head_l2 | 0 | 9.18 | 14.15 | 10.56 | 13.03 | 0.517 (12 failed) | 47 |
| head | 0 | 4.09 | 6.94 | 4.74 | 5.79 | 0.354 (4 failed) | 45 |
| head_all | 0 | 1.70 | 1.83 | 2.85 | 3.24 | 0.191 (4 failed) | 71 |
| scratch | 0 | 1.80 | 1.96 | 2.97 | 3.65 | 0.230 (4 failed) | 1046 |
