# E5 — skip-gram analogue: mode embeddings from the coupling context (2026-09-19 18:56); held-out RMS in cm⁻¹, 12 molecules

Training: 30 molecules, 43791 mode pairs, 1500 steps, seeds 0–2. Readings: ring diagonal win < 10 (Transformer 12.4); ring coupling ratio to zero rule win ≤ 0.7.

| encoder | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring couplings RMS / zero | ratio | ring block RMS / median rule | probe ring |
|---|---|---|---|---|---|---|---|---|
| E5-tok | 5.42 | 5.61 | 13.99 | 18.08 | 9.79 / 5.49 | 1.78 | 4.77 / 4.03 | 15.93 |
| E5-atoms | 9.72 | 8.59 | 17.61 | 14.03 | 7.49 / 5.49 | 1.36 | 5.63 / 4.03 | 18.56 |
