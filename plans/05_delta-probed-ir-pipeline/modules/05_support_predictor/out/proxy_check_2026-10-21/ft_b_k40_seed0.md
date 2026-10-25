# Proxy transfer check — k = 40, seed 0

Base `base_b_model_n607_seed0.pt`; read set 27 molecules (intensity on 17); reservoir 40; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 20.84 | 43.28 | 22.76 | 15.41 | 0.445 | – |
| base as is | – | 2.19 | 1.23 | 2.31 | 3.69 | 0.240 | – |
| head_l2 | 0 | 2.23 | 2.63 | 2.35 | 3.61 | 0.224 | 61 |
| head | 0 | 2.15 | 2.13 | 2.57 | 3.35 | 0.228 | 57 |
| head_all | 0 | 2.34 | 1.90 | 2.34 | 3.53 | 0.212 | 102 |
| scratch | 0 | 2.54 | 2.99 | 3.53 | 5.79 | 0.308 | 187 |
