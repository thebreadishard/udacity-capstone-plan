# Proxy transfer check — k = 100, seed 0

Base `base_a_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 26.29 | 77.18 | 31.57 | 35.37 | 0.766 (14 failed) | – |
| head_l2 | 0 | 9.37 | 14.55 | 8.72 | 11.95 | 0.553 (11 failed) | 47 |
| head | 0 | 4.48 | 8.01 | 4.61 | 5.86 | 0.368 (4 failed) | 45 |
| head_all | 0 | 2.18 | 2.42 | 3.20 | 3.54 | 0.207 (4 failed) | 70 |
| scratch | 0 | 2.29 | 2.08 | 3.52 | 4.59 | 0.237 (4 failed) | 457 |
| head_l2 | 1 | 8.99 | 14.24 | 7.47 | 11.94 | 0.562 (12 failed) | 46 |
| head | 1 | 4.46 | 8.80 | 4.70 | 5.82 | 0.359 (4 failed) | 45 |
| head_all | 1 | 1.90 | 2.00 | 3.03 | 3.67 | 0.224 (4 failed) | 71 |
| scratch | 1 | 1.96 | 1.95 | 3.09 | 4.14 | 0.227 (4 failed) | 665 |
| head_l2 | 2 | 9.27 | 14.29 | 8.42 | 12.25 | 0.555 (14 failed) | 46 |
| head | 2 | 4.20 | 8.97 | 4.56 | 5.63 | 0.348 (4 failed) | 45 |
| head_all | 2 | 1.95 | 1.92 | 3.49 | 3.64 | 0.195 (4 failed) | 70 |
| scratch | 2 | 2.30 | 2.28 | 3.72 | 4.53 | 0.243 (4 failed) | 436 |
