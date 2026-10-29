# Proxy transfer check — k = 120, seed 1

Base `base_c_model_n750_seed1.pt`; read set 343 molecules (intensity on 124); reservoir 200; 3000 steps per fine-tune.

| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |
|---|---|---|---|---|---|---|---|
| zero rule | – | 19.94 | 43.36 | 21.90 | 17.34 | 0.562 (4 failed) | – |
| base as is | – | 35.00 | 78.40 | 32.51 | 37.09 | 0.544 (18 failed) | – |
| body1_es | 0 | 2.14 | 2.50 | 3.17 | 4.66 | 0.231 (4 failed) | 104 |
| head_all_es | 0 | 2.29 | 2.41 | 3.26 | 4.29 | 0.238 (4 failed) | 102 |
| head_all | 0 | 2.79 | 2.50 | 2.86 | 4.40 | 0.232 (4 failed) | 67 |
| body1_es | 1 | 2.01 | 2.39 | 2.94 | 4.20 | 0.227 (4 failed) | 127 |
| head_all_es | 1 | 2.36 | 3.05 | 2.84 | 3.95 | 0.223 (4 failed) | 149 |
| head_all | 1 | 2.26 | 2.73 | 2.76 | 3.98 | 0.221 (4 failed) | 71 |
| body1_es | 2 | 2.14 | 2.91 | 3.67 | 4.20 | 0.230 (4 failed) | 165 |
| head_all_es | 2 | 2.39 | 2.14 | 3.51 | 4.39 | 0.237 (4 failed) | 86 |
| head_all | 2 | 3.55 | 7.06 | 3.65 | 4.64 | 0.271 (4 failed) | 70 |
