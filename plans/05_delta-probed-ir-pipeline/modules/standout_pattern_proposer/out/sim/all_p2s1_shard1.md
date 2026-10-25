# Pattern-proposer simulation — pool all, 2026-09-27 12:28

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 20 evaluation molecules.

## eval_parents (n 8; P0 reaches ρ_off ≤ 0.3 on 8)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 8 | 0.36 | 88 % |
| K_off_0p3 | P1_seed0 | 8 | 0.80 | 62 % |
| K_off_0p3 | P2_seed0 | 8 | 0.79 | 62 % |
| K_off_0p3 | P12_seed0 | 8 | 0.79 | 62 % |
| K_off_0p3 | P1_seed1 | 8 | 0.87 | 62 % |
| K_off_0p3 | P2_seed1 | 8 | 0.81 | 50 % |
| K_off_0p3 | P12_seed1 | 8 | 0.78 | 62 % |
| K_off_0p3 | P1_seed2 | 8 | 0.91 | 50 % |
| K_off_0p3 | P2_seed2 | 8 | 0.89 | 50 % |
| K_off_0p3 | P12_seed2 | 8 | 0.76 | 62 % |
| K_off_0p1 | P3_oracle | 6 | 0.77 | 67 % |
| K_off_0p1 | P1_seed0 | 6 | 1.01 | 50 % |
| K_off_0p1 | P2_seed0 | 6 | 1.00 | 50 % |
| K_off_0p1 | P12_seed0 | 6 | 0.86 | 67 % |
| K_off_0p1 | P1_seed1 | 6 | 0.95 | 67 % |
| K_off_0p1 | P2_seed1 | 6 | 0.90 | 67 % |
| K_off_0p1 | P12_seed1 | 6 | 0.96 | 50 % |
| K_off_0p1 | P1_seed2 | 6 | 1.04 | 33 % |
| K_off_0p1 | P2_seed2 | 6 | 0.88 | 83 % |
| K_off_0p1 | P12_seed2 | 6 | 0.93 | 50 % |
| n10_inband | P3_oracle | 7 | 0.67 | 57 % |
| n10_inband | P1_seed0 | 7 | 1.33 | 29 % |
| n10_inband | P2_seed0 | 7 | 1.38 | 43 % |
| n10_inband | P12_seed0 | 7 | 1.24 | 43 % |
| n10_inband | P1_seed1 | 7 | 1.41 | 29 % |
| n10_inband | P2_seed1 | 7 | 1.24 | 29 % |
| n10_inband | P12_seed1 | 7 | 1.17 | 43 % |
| n10_inband | P1_seed2 | 7 | 1.33 | 14 % |
| n10_inband | P2_seed2 | 7 | 1.38 | 43 % |
| n10_inband | P12_seed2 | 7 | 1.21 | 43 % |
| n10_all | P3_oracle | 7 | 0.51 | 86 % |
| n10_all | P1_seed0 | 7 | 0.94 | 86 % |
| n10_all | P2_seed0 | 7 | 0.84 | 100 % |
| n10_all | P12_seed0 | 7 | 0.86 | 100 % |
| n10_all | P1_seed1 | 7 | 0.93 | 86 % |
| n10_all | P2_seed1 | 7 | 0.84 | 86 % |
| n10_all | P12_seed1 | 7 | 0.84 | 86 % |
| n10_all | P1_seed2 | 7 | 0.96 | 71 % |
| n10_all | P2_seed2 | 7 | 0.84 | 100 % |
| n10_all | P12_seed2 | 7 | 0.84 | 100 % |

## eval (n 12; P0 reaches ρ_off ≤ 0.3 on 9)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 9 | 0.27 | 100 % |
| K_off_0p3 | P1_seed0 | 9 | 0.77 | 78 % |
| K_off_0p3 | P2_seed0 | 9 | 0.56 | 78 % |
| K_off_0p3 | P12_seed0 | 9 | 0.59 | 78 % |
| K_off_0p3 | P1_seed1 | 9 | 0.89 | 56 % |
| K_off_0p3 | P2_seed1 | 9 | 0.73 | 78 % |
| K_off_0p3 | P12_seed1 | 9 | 0.55 | 67 % |
| K_off_0p3 | P1_seed2 | 9 | 0.73 | 67 % |
| K_off_0p3 | P2_seed2 | 9 | 0.68 | 78 % |
| K_off_0p3 | P12_seed2 | 9 | 0.57 | 78 % |
| K_off_0p1 | P3_oracle | 6 | 0.50 | 100 % |
| K_off_0p1 | P1_seed0 | 6 | 0.88 | 83 % |
| K_off_0p1 | P2_seed0 | 6 | 0.86 | 83 % |
| K_off_0p1 | P12_seed0 | 6 | 0.75 | 83 % |
| K_off_0p1 | P1_seed1 | 6 | 0.86 | 67 % |
| K_off_0p1 | P2_seed1 | 6 | 0.84 | 67 % |
| K_off_0p1 | P12_seed1 | 6 | 0.79 | 67 % |
| K_off_0p1 | P1_seed2 | 6 | 0.84 | 83 % |
| K_off_0p1 | P2_seed2 | 6 | 0.81 | 83 % |
| K_off_0p1 | P12_seed2 | 6 | 0.70 | 83 % |
| n10_inband | P3_oracle | 9 | 0.91 | 67 % |
| n10_inband | P1_seed0 | 9 | 1.44 | 22 % |
| n10_inband | P2_seed0 | 9 | 1.31 | 22 % |
| n10_inband | P12_seed0 | 9 | 1.38 | 22 % |
| n10_inband | P1_seed1 | 9 | 1.47 | 22 % |
| n10_inband | P2_seed1 | 9 | 1.28 | 11 % |
| n10_inband | P12_seed1 | 9 | 1.41 | 22 % |
| n10_inband | P1_seed2 | 9 | 1.44 | 22 % |
| n10_inband | P2_seed2 | 9 | 1.34 | 22 % |
| n10_inband | P12_seed2 | 9 | 1.41 | 33 % |
| n10_all | P3_oracle | 8 | 0.51 | 100 % |
| n10_all | P1_seed0 | 8 | 0.86 | 75 % |
| n10_all | P2_seed0 | 8 | 0.75 | 100 % |
| n10_all | P12_seed0 | 8 | 0.76 | 100 % |
| n10_all | P1_seed1 | 8 | 0.88 | 75 % |
| n10_all | P2_seed1 | 8 | 0.78 | 100 % |
| n10_all | P12_seed1 | 8 | 0.75 | 100 % |
| n10_all | P1_seed2 | 8 | 0.82 | 75 % |
| n10_all | P2_seed2 | 8 | 0.81 | 100 % |
| n10_all | P12_seed2 | 8 | 0.82 | 100 % |
