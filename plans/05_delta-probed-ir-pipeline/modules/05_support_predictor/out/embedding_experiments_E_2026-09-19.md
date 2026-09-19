# E-series — learned mode embeddings (2026-09-19 17:33); held-out RMS in cm⁻¹, same 12 molecules as the learning curves

| experiment (n_train = 30) | CH-stretch | CH-oop | ring-ip | other |
|---|---|---|---|---|
| E0 ridge, first-pass tokens | 2.28 | 7.98 | 17.62 | 11.40 |
| E2 ridge, + molecule tokens | 2.70 | 8.11 | 17.64 | 11.23 |
| E2 Transformer, + molecule tokens | 1.85 | 3.93 | 12.37 | 24.50 |
| E1 contrastive embedding + ridge (mean of seeds) | 12.21 | 9.18 | 19.30 | 13.30 |
| E1b supervised encoder, direct (mean of seeds) | 10.35 | 7.21 | 19.04 | 12.82 |

E1 probe curve (seed 0): n=5: ring-ip 26.22; n=10: ring-ip 19.83; n=20: ring-ip 19.59; n=30: ring-ip 19.69
Reference (first pass, Transformer, n=30): C–H stretch 1.78, C–H oop 4.31, ring-ip 12.41, other 26.6; family-median rule ring-ip 18.5; zero rule 21.9.
