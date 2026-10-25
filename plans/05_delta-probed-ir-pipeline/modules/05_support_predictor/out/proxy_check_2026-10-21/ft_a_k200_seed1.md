# Proxy transfer check — k = 200, seed 1

Base `base_a_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.72 | 78.09 | 31.32 | 35.09 | 0.773 (11 failed) | – |
| head_l2 | 0 | 9.17 | 11.54 | 10.35 | 13.30 | 0.535 (7 failed) | 47 |
| head | 0 | 4.25 | 6.58 | 5.11 | 5.83 | 0.361 (4 failed) | 45 |
| head_all | 0 | 1.71 | 1.88 | 2.87 | 3.44 | 0.196 (4 failed) | 69 |
| scratch | 0 | 1.83 | 2.26 | 2.74 | 3.70 | 0.213 (4 failed) | 875 |
