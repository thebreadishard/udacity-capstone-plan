# Pattern-proposer simulation — pool all, 2026-09-28 03:01

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.27 | 100 % |
| K_off_0p3 | P1_seed0 | 4 | 1.13 | 50 % |
| K_off_0p3 | P2_seed0 | 4 | 1.16 | 50 % |
| K_off_0p3 | P12_seed0 | 4 | 1.15 | 50 % |
| K_off_0p3 | P1_seed1 | 4 | 1.22 | 50 % |
| K_off_0p3 | P2_seed1 | 4 | 1.19 | 25 % |
| K_off_0p3 | P12_seed1 | 4 | 1.12 | 50 % |
| K_off_0p3 | P1_seed2 | 4 | 1.36 | 25 % |
| K_off_0p3 | P2_seed2 | 4 | 1.35 | 25 % |
| K_off_0p3 | P12_seed2 | 4 | 1.13 | 50 % |
| K_off_0p3 | P0A | 4 | 1.12 | 50 % |
| K_off_0p3 | P1A_seed0 | 4 | 1.34 | 25 % |
| K_off_0p3 | P2A_seed0 | 4 | 1.22 | 50 % |
| K_off_0p3 | P1A_seed1 | 4 | 1.32 | 25 % |
| K_off_0p3 | P2A_seed1 | 4 | 1.35 | 25 % |
| K_off_0p3 | P1A_seed2 | 4 | 1.33 | 25 % |
| K_off_0p3 | P2A_seed2 | 4 | 1.41 | 25 % |
| K_off_0p1 | P3_oracle | 3 | 0.49 | 100 % |
| K_off_0p1 | P1_seed0 | 3 | 1.20 | 33 % |
| K_off_0p1 | P2_seed0 | 3 | 1.07 | 33 % |
| K_off_0p1 | P12_seed0 | 3 | 0.82 | 67 % |
| K_off_0p1 | P1_seed1 | 3 | 0.88 | 67 % |
| K_off_0p1 | P2_seed1 | 3 | 0.93 | 67 % |
| K_off_0p1 | P12_seed1 | 3 | 1.02 | 33 % |
| K_off_0p1 | P1_seed2 | 3 | 1.12 | 33 % |
| K_off_0p1 | P2_seed2 | 3 | 0.90 | 67 % |
| K_off_0p1 | P12_seed2 | 3 | 1.15 | 33 % |
| K_off_0p1 | P0A | 3 | 1.00 | 33 % |
| K_off_0p1 | P1A_seed0 | 3 | 1.02 | 33 % |
| K_off_0p1 | P2A_seed0 | 3 | 1.00 | 33 % |
| K_off_0p1 | P1A_seed1 | 3 | 1.20 | 33 % |
| K_off_0p1 | P2A_seed1 | 3 | 0.90 | 67 % |
| K_off_0p1 | P1A_seed2 | 3 | 1.12 | 33 % |
| K_off_0p1 | P2A_seed2 | 3 | 0.93 | 67 % |
| n10_inband | P3_oracle | 4 | 0.96 | 50 % |
| n10_inband | P1_seed0 | 4 | 1.50 | 0 % |
| n10_inband | P2_seed0 | 4 | 1.49 | 25 % |
| n10_inband | P12_seed0 | 4 | 1.35 | 25 % |
| n10_inband | P1_seed1 | 4 | 1.60 | 0 % |
| n10_inband | P2_seed1 | 4 | 1.58 | 25 % |
| n10_inband | P12_seed1 | 4 | 1.50 | 25 % |
| n10_inband | P1_seed2 | 4 | 1.41 | 0 % |
| n10_inband | P2_seed2 | 4 | 1.48 | 25 % |
| n10_inband | P12_seed2 | 4 | 1.40 | 25 % |
| n10_inband | P0A | 4 | 1.32 | 25 % |
| n10_inband | P1A_seed0 | 4 | 1.46 | 0 % |
| n10_inband | P2A_seed0 | 4 | 1.54 | 25 % |
| n10_inband | P1A_seed1 | 4 | 1.46 | 0 % |
| n10_inband | P2A_seed1 | 4 | 1.51 | 25 % |
| n10_inband | P1A_seed2 | 4 | 1.43 | 0 % |
| n10_inband | P2A_seed2 | 4 | 1.56 | 25 % |
| n10_all | P3_oracle | 5 | 0.43 | 100 % |
| n10_all | P1_seed0 | 5 | 0.94 | 60 % |
| n10_all | P2_seed0 | 5 | 0.84 | 80 % |
| n10_all | P12_seed0 | 5 | 0.86 | 60 % |
| n10_all | P1_seed1 | 5 | 0.90 | 60 % |
| n10_all | P2_seed1 | 5 | 0.82 | 80 % |
| n10_all | P12_seed1 | 5 | 0.84 | 60 % |
| n10_all | P1_seed2 | 5 | 0.88 | 60 % |
| n10_all | P2_seed2 | 5 | 0.84 | 100 % |
| n10_all | P12_seed2 | 5 | 0.86 | 60 % |
| n10_all | P0A | 5 | 0.93 | 100 % |
| n10_all | P1A_seed0 | 5 | 0.80 | 80 % |
| n10_all | P2A_seed0 | 5 | 0.81 | 100 % |
| n10_all | P1A_seed1 | 5 | 0.80 | 80 % |
| n10_all | P2A_seed1 | 5 | 0.84 | 100 % |
| n10_all | P1A_seed2 | 5 | 0.81 | 100 % |
| n10_all | P2A_seed2 | 5 | 0.80 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.36 | 100 % |
| K_off_0p3 | P1_seed0 | 4 | 1.14 | 50 % |
| K_off_0p3 | P2_seed0 | 4 | 0.97 | 50 % |
| K_off_0p3 | P12_seed0 | 4 | 1.00 | 50 % |
| K_off_0p3 | P1_seed1 | 4 | 1.22 | 25 % |
| K_off_0p3 | P2_seed1 | 4 | 1.21 | 25 % |
| K_off_0p3 | P12_seed1 | 4 | 1.22 | 25 % |
| K_off_0p3 | P1_seed2 | 4 | 1.11 | 25 % |
| K_off_0p3 | P2_seed2 | 4 | 0.91 | 50 % |
| K_off_0p3 | P12_seed2 | 4 | 1.04 | 50 % |
| K_off_0p3 | P0A | 4 | 0.87 | 50 % |
| K_off_0p3 | P1A_seed0 | 4 | 1.01 | 50 % |
| K_off_0p3 | P2A_seed0 | 4 | 1.15 | 50 % |
| K_off_0p3 | P1A_seed1 | 4 | 1.16 | 25 % |
| K_off_0p3 | P2A_seed1 | 4 | 1.12 | 25 % |
| K_off_0p3 | P1A_seed2 | 4 | 0.97 | 50 % |
| K_off_0p3 | P2A_seed2 | 4 | 1.11 | 50 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P1_seed0 | 0 | — | — |
| K_off_0p1 | P2_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P1_seed1 | 0 | — | — |
| K_off_0p1 | P2_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P1_seed2 | 0 | — | — |
| K_off_0p1 | P2_seed2 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| K_off_0p1 | P0A | 0 | — | — |
| K_off_0p1 | P1A_seed0 | 0 | — | — |
| K_off_0p1 | P2A_seed0 | 0 | — | — |
| K_off_0p1 | P1A_seed1 | 0 | — | — |
| K_off_0p1 | P2A_seed1 | 0 | — | — |
| K_off_0p1 | P1A_seed2 | 0 | — | — |
| K_off_0p1 | P2A_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 3 | 1.12 | 0 % |
| n10_inband | P1_seed0 | 3 | 1.33 | 0 % |
| n10_inband | P2_seed0 | 3 | 1.36 | 0 % |
| n10_inband | P12_seed0 | 3 | 1.28 | 0 % |
| n10_inband | P1_seed1 | 3 | 1.44 | 0 % |
| n10_inband | P2_seed1 | 3 | 1.47 | 0 % |
| n10_inband | P12_seed1 | 3 | 1.36 | 0 % |
| n10_inband | P1_seed2 | 3 | 1.44 | 0 % |
| n10_inband | P2_seed2 | 3 | 1.39 | 0 % |
| n10_inband | P12_seed2 | 3 | 1.31 | 0 % |
| n10_inband | P0A | 3 | 1.04 | 33 % |
| n10_inband | P1A_seed0 | 3 | 1.31 | 0 % |
| n10_inband | P2A_seed0 | 3 | 1.28 | 0 % |
| n10_inband | P1A_seed1 | 3 | 1.36 | 0 % |
| n10_inband | P2A_seed1 | 3 | 1.28 | 0 % |
| n10_inband | P1A_seed2 | 3 | 1.31 | 0 % |
| n10_inband | P2A_seed2 | 3 | 1.28 | 33 % |
| n10_all | P3_oracle | 2 | 0.65 | 100 % |
| n10_all | P1_seed0 | 2 | 0.93 | 100 % |
| n10_all | P2_seed0 | 2 | 0.87 | 100 % |
| n10_all | P12_seed0 | 2 | 0.91 | 100 % |
| n10_all | P1_seed1 | 2 | 0.93 | 100 % |
| n10_all | P2_seed1 | 2 | 0.93 | 100 % |
| n10_all | P12_seed1 | 2 | 0.90 | 100 % |
| n10_all | P1_seed2 | 2 | 0.93 | 100 % |
| n10_all | P2_seed2 | 2 | 0.90 | 100 % |
| n10_all | P12_seed2 | 2 | 0.91 | 100 % |
| n10_all | P0A | 2 | 0.99 | 50 % |
| n10_all | P1A_seed0 | 2 | 0.93 | 100 % |
| n10_all | P2A_seed0 | 2 | 0.91 | 100 % |
| n10_all | P1A_seed1 | 2 | 0.90 | 100 % |
| n10_all | P2A_seed1 | 2 | 0.93 | 100 % |
| n10_all | P1A_seed2 | 2 | 0.92 | 100 % |
| n10_all | P2A_seed2 | 2 | 0.93 | 100 % |
