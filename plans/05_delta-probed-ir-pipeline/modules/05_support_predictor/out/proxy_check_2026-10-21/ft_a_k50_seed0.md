# Proxy transfer check — k = 50, seed 0

Base `base_a_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.29 | 77.18 | 31.57 | 35.37 | 0.766 (14 failed) | – |
| head_l2 | 0 | 9.66 | 12.21 | 7.91 | 12.48 | 0.550 (14 failed) | 49 |
| head | 0 | 4.38 | 5.68 | 4.84 | 5.46 | 0.349 (4 failed) | 47 |
| head_all | 0 | 2.20 | 2.44 | 3.99 | 4.14 | 0.230 (4 failed) | 70 |
| scratch | 0 | 3.62 | 2.82 | 5.39 | 6.29 | 0.292 (4 failed) | 129 |
| head_l2 | 1 | 9.91 | 9.67 | 9.19 | 12.41 | 0.559 (16 failed) | 47 |
| head | 1 | 4.62 | 6.89 | 4.38 | 5.75 | 0.358 (4 failed) | 46 |
| head_all | 1 | 2.52 | 3.27 | 3.57 | 4.71 | 0.237 (4 failed) | 72 |
| scratch | 1 | 2.94 | 3.96 | 4.55 | 5.48 | 0.293 (4 failed) | 218 |
| head_l2 | 2 | 9.60 | 12.39 | 8.99 | 12.36 | 0.569 (11 failed) | 44 |
| head | 2 | 4.38 | 5.85 | 4.76 | 5.49 | 0.359 (4 failed) | 45 |
| head_all | 2 | 2.16 | 2.35 | 3.51 | 3.99 | 0.230 (4 failed) | 72 |
| scratch | 2 | 2.88 | 2.89 | 5.05 | 5.88 | 0.284 (5 failed) | 319 |
