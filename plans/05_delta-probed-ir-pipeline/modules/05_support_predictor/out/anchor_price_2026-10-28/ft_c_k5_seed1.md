# Proxy transfer check — k = 5, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| head_all | 0 | 5.34 | 4.55 | 6.13 | 8.81 | 0.399 (4 failed) | 54 |
| head_all | 1 | 4.69 | 4.89 | 7.08 | 8.37 | 0.372 (4 failed) | 65 |
| head_all | 2 | 4.72 | 4.22 | 7.17 | 7.94 | 0.362 (5 failed) | 68 |
