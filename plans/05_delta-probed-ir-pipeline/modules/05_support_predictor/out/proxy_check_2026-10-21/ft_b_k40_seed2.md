# Proxy transfer check — k = 40, seed 2

Base `base_b_model_n607_seed2.pt`; read set 27 molecules (intensity on 17); reservoir 40; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 20.84 | 43.28 | 22.76 | 15.41 | 0.445 | – |
| base as is | – | 2.11 | 1.30 | 2.55 | 3.69 | 0.242 | – |
| head_l2 | 0 | 2.03 | 2.87 | 2.51 | 3.64 | 0.226 | 63 |
| head | 0 | 2.08 | 2.63 | 2.72 | 3.53 | 0.224 | 61 |
| head_all | 0 | 1.83 | 2.95 | 2.32 | 3.37 | 0.206 | 107 |
| scratch | 0 | 2.20 | 3.06 | 2.62 | 4.89 | 0.267 | 322 |
