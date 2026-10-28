# Proxy transfer check — k = 100, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 2.66 | 2.92 | 3.28 | 4.57 | 0.232 (4 failed) | 70 |
| head_all | 1 | 2.97 | 2.70 | 4.42 | 4.91 | 0.264 (4 failed) | 69 |
| head_all | 2 | 2.45 | 2.21 | 3.22 | 4.43 | 0.253 (4 failed) | 69 |
