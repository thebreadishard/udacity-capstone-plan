# Proxy transfer check — k = 40, seed 1

Base `base_b_model_n607_seed1.pt`; read set 27 molecules (intensity on 17); reservoir 40; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 20.84 | 43.28 | 22.76 | 15.41 | 0.445 | – |
| base as is | – | 2.23 | 1.13 | 3.12 | 4.38 | 0.296 | – |
| head_l2 | 0 | 2.15 | 1.20 | 3.11 | 4.46 | 0.285 | 59 |
| head | 0 | 2.11 | 1.43 | 3.00 | 3.74 | 0.273 | 56 |
| head_all | 0 | 2.68 | 1.81 | 2.05 | 3.21 | 0.228 | 101 |
| scratch | 0 | 2.35 | 2.51 | 2.40 | 5.30 | 0.276 | 300 |
