# E5 — skip-gram analogue: mode embeddings from the coupling context (2026-09-19 18:31); held-out RMS in cm⁻¹, 12 molecules

Training: 30 molecules, 43791 mode pairs, 1500 steps, seeds 0–2. Readings: ring diagonal win < 10 (Transformer 12.4); ring coupling ratio to zero rule win ≤ 0.7.

| encoder | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring couplings RMS / zero | ratio | ring block RMS / median rule | probe ring |
|---|---|---|---|---|---|---|---|---|
| E5-tok | 35.68 | 20.54 | 20.26 | 15.21 | 5.67 / 5.49 | 1.03 | 11.16 / 4.03 | 16.78 |
| E5-atoms | 43.08 | 23.06 | 21.67 | 14.58 | 5.52 / 5.49 | 1.00 | 12.39 / 4.03 | 19.88 |
