# Proxy transfer check — k = 5, seed 0

Base `base_c_model_n750_seed0.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 34.70 | 77.44 | 31.91 | 36.17 | 0.522 (19 failed) | – |
| body1_es | 0 | 7.54 | 7.55 | 7.91 | 8.67 | 0.535 (4 failed) | 17 |
| body1_es | 1 | 6.49 | 7.03 | 7.61 | 9.85 | 0.484 (4 failed) | 14 |
| body1_es | 2 | 5.57 | 6.63 | 6.23 | 8.44 | 0.440 (4 failed) | 11 |
