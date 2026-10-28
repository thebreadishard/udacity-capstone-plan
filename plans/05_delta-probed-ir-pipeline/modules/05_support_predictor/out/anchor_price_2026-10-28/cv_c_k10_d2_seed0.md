# Proxy transfer check — k = 10, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 10; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| head_all | 0 | 3.75 | 4.52 | 4.97 | 7.21 | 0.330 (5 failed) | 87 |
| scratch | 0 | 5.98 | 4.96 | 6.76 | 8.23 | 0.413 (4 failed) | 46 |
