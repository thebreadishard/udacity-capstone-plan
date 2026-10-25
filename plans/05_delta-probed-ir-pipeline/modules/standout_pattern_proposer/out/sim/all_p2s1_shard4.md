# Pattern-proposer simulation — pool all, 2026-09-27 10:36

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 19 evaluation molecules.

## eval_parents (n 8; P0 reaches ρ_off ≤ 0.3 on 7)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 7 | 0.22 | 100 % |
| K_off_0p3 | P1_seed0 | 7 | 0.72 | 71 % |
| K_off_0p3 | P2_seed0 | 7 | 0.52 | 86 % |
| K_off_0p3 | P12_seed0 | 7 | 0.57 | 86 % |
| K_off_0p3 | P1_seed1 | 7 | 0.76 | 71 % |
| K_off_0p3 | P2_seed1 | 7 | 0.60 | 86 % |
| K_off_0p3 | P12_seed1 | 7 | 0.43 | 86 % |
| K_off_0p3 | P1_seed2 | 7 | 0.83 | 86 % |
| K_off_0p3 | P2_seed2 | 7 | 0.55 | 86 % |
| K_off_0p3 | P12_seed2 | 7 | 0.64 | 86 % |
| K_off_0p1 | P3_oracle | 5 | 0.39 | 100 % |
| K_off_0p1 | P1_seed0 | 5 | 0.71 | 80 % |
| K_off_0p1 | P2_seed0 | 5 | 0.71 | 80 % |
| K_off_0p1 | P12_seed0 | 5 | 0.65 | 80 % |
| K_off_0p1 | P1_seed1 | 5 | 0.80 | 80 % |
| K_off_0p1 | P2_seed1 | 5 | 0.79 | 80 % |
| K_off_0p1 | P12_seed1 | 5 | 0.67 | 80 % |
| K_off_0p1 | P1_seed2 | 5 | 0.79 | 80 % |
| K_off_0p1 | P2_seed2 | 5 | 0.76 | 80 % |
| K_off_0p1 | P12_seed2 | 5 | 0.65 | 80 % |
| n10_inband | P3_oracle | 7 | 0.85 | 71 % |
| n10_inband | P1_seed0 | 7 | 1.33 | 29 % |
| n10_inband | P2_seed0 | 7 | 1.08 | 29 % |
| n10_inband | P12_seed0 | 7 | 1.09 | 29 % |
| n10_inband | P1_seed1 | 7 | 1.36 | 14 % |
| n10_inband | P2_seed1 | 7 | 1.08 | 14 % |
| n10_inband | P12_seed1 | 7 | 1.13 | 29 % |
| n10_inband | P1_seed2 | 7 | 1.33 | 29 % |
| n10_inband | P2_seed2 | 7 | 1.09 | 29 % |
| n10_inband | P12_seed2 | 7 | 1.10 | 29 % |
| n10_all | P3_oracle | 7 | 0.41 | 100 % |
| n10_all | P1_seed0 | 7 | 0.73 | 86 % |
| n10_all | P2_seed0 | 7 | 0.75 | 86 % |
| n10_all | P12_seed0 | 7 | 0.73 | 86 % |
| n10_all | P1_seed1 | 7 | 0.83 | 86 % |
| n10_all | P2_seed1 | 7 | 0.75 | 86 % |
| n10_all | P12_seed1 | 7 | 0.65 | 86 % |
| n10_all | P1_seed2 | 7 | 0.91 | 86 % |
| n10_all | P2_seed2 | 7 | 0.79 | 100 % |
| n10_all | P12_seed2 | 7 | 0.67 | 86 % |

## eval (n 11; P0 reaches ρ_off ≤ 0.3 on 8)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 8 | 0.25 | 100 % |
| K_off_0p3 | P1_seed0 | 8 | 0.74 | 75 % |
| K_off_0p3 | P2_seed0 | 8 | 0.64 | 75 % |
| K_off_0p3 | P12_seed0 | 8 | 0.57 | 75 % |
| K_off_0p3 | P1_seed1 | 8 | 0.75 | 75 % |
| K_off_0p3 | P2_seed1 | 8 | 0.66 | 75 % |
| K_off_0p3 | P12_seed1 | 8 | 0.51 | 75 % |
| K_off_0p3 | P1_seed2 | 8 | 0.69 | 75 % |
| K_off_0p3 | P2_seed2 | 8 | 0.72 | 88 % |
| K_off_0p3 | P12_seed2 | 8 | 0.61 | 75 % |
| K_off_0p1 | P3_oracle | 4 | 0.63 | 100 % |
| K_off_0p1 | P1_seed0 | 4 | 1.02 | 25 % |
| K_off_0p1 | P2_seed0 | 4 | 0.89 | 75 % |
| K_off_0p1 | P12_seed0 | 4 | 0.93 | 75 % |
| K_off_0p1 | P1_seed1 | 4 | 1.01 | 25 % |
| K_off_0p1 | P2_seed1 | 4 | 0.94 | 75 % |
| K_off_0p1 | P12_seed1 | 4 | 0.95 | 75 % |
| K_off_0p1 | P1_seed2 | 4 | 0.99 | 50 % |
| K_off_0p1 | P2_seed2 | 4 | 0.97 | 50 % |
| K_off_0p1 | P12_seed2 | 4 | 0.94 | 75 % |
| n10_inband | P3_oracle | 7 | 1.24 | 29 % |
| n10_inband | P1_seed0 | 7 | 3.24 | 0 % |
| n10_inband | P2_seed0 | 7 | 3.18 | 0 % |
| n10_inband | P12_seed0 | 7 | 3.00 | 0 % |
| n10_inband | P1_seed1 | 7 | 3.29 | 0 % |
| n10_inband | P2_seed1 | 7 | 2.73 | 0 % |
| n10_inband | P12_seed1 | 7 | 3.00 | 0 % |
| n10_inband | P1_seed2 | 7 | 3.24 | 0 % |
| n10_inband | P2_seed2 | 7 | 3.35 | 0 % |
| n10_inband | P12_seed2 | 7 | 3.18 | 0 % |
| n10_all | P3_oracle | 7 | 0.46 | 100 % |
| n10_all | P1_seed0 | 7 | 0.97 | 71 % |
| n10_all | P2_seed0 | 7 | 0.91 | 57 % |
| n10_all | P12_seed0 | 7 | 0.95 | 57 % |
| n10_all | P1_seed1 | 7 | 0.97 | 71 % |
| n10_all | P2_seed1 | 7 | 0.93 | 71 % |
| n10_all | P12_seed1 | 7 | 0.95 | 86 % |
| n10_all | P1_seed2 | 7 | 0.98 | 57 % |
| n10_all | P2_seed2 | 7 | 0.95 | 71 % |
| n10_all | P12_seed2 | 7 | 0.95 | 71 % |
