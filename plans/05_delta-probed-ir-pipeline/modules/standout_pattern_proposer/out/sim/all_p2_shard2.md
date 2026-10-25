# Pattern-proposer simulation — pool all, 2026-09-26 22:26

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.44 | 80 % |
| K_off_0p3 | P1_seed0 | 5 | 0.66 | 80 % |
| K_off_0p3 | P2_seed0 | 5 | 0.68 | 60 % |
| K_off_0p3 | P12_seed0 | 5 | 0.62 | 80 % |
| K_off_0p3 | P1_seed1 | 5 | 0.68 | 80 % |
| K_off_0p3 | P2_seed1 | 5 | 0.79 | 80 % |
| K_off_0p3 | P12_seed1 | 5 | 0.65 | 80 % |
| K_off_0p3 | P1_seed2 | 5 | 0.65 | 80 % |
| K_off_0p3 | P2_seed2 | 5 | 0.68 | 80 % |
| K_off_0p3 | P12_seed2 | 5 | 0.59 | 80 % |
| K_off_0p1 | P3_oracle | 2 | 1.18 | 0 % |
| K_off_0p1 | P1_seed0 | 2 | 1.09 | 50 % |
| K_off_0p1 | P2_seed0 | 2 | 1.17 | 0 % |
| K_off_0p1 | P12_seed0 | 2 | 1.09 | 50 % |
| K_off_0p1 | P1_seed1 | 2 | 1.13 | 50 % |
| K_off_0p1 | P2_seed1 | 2 | 1.12 | 0 % |
| K_off_0p1 | P12_seed1 | 2 | 1.07 | 50 % |
| K_off_0p1 | P1_seed2 | 2 | 1.18 | 50 % |
| K_off_0p1 | P2_seed2 | 2 | 1.12 | 0 % |
| K_off_0p1 | P12_seed2 | 2 | 1.13 | 50 % |
| n10_inband | P3_oracle | 4 | 1.27 | 25 % |
| n10_inband | P1_seed0 | 4 | 2.31 | 0 % |
| n10_inband | P2_seed0 | 4 | 2.11 | 0 % |
| n10_inband | P12_seed0 | 4 | 2.28 | 0 % |
| n10_inband | P1_seed1 | 4 | 2.42 | 0 % |
| n10_inband | P2_seed1 | 4 | 2.30 | 0 % |
| n10_inband | P12_seed1 | 4 | 2.24 | 0 % |
| n10_inband | P1_seed2 | 4 | 2.08 | 0 % |
| n10_inband | P2_seed2 | 4 | 2.14 | 0 % |
| n10_inband | P12_seed2 | 4 | 2.31 | 0 % |
| n10_all | P3_oracle | 4 | 0.62 | 75 % |
| n10_all | P1_seed0 | 4 | 0.87 | 100 % |
| n10_all | P2_seed0 | 4 | 0.85 | 100 % |
| n10_all | P12_seed0 | 4 | 0.83 | 100 % |
| n10_all | P1_seed1 | 4 | 0.88 | 100 % |
| n10_all | P2_seed1 | 4 | 0.86 | 100 % |
| n10_all | P12_seed1 | 4 | 0.83 | 100 % |
| n10_all | P1_seed2 | 4 | 0.89 | 100 % |
| n10_all | P2_seed2 | 4 | 0.86 | 100 % |
| n10_all | P12_seed2 | 4 | 0.83 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 7)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 7 | 0.57 | 86 % |
| K_off_0p3 | P1_seed0 | 7 | 0.95 | 57 % |
| K_off_0p3 | P2_seed0 | 7 | 0.86 | 57 % |
| K_off_0p3 | P12_seed0 | 7 | 0.98 | 57 % |
| K_off_0p3 | P1_seed1 | 7 | 1.02 | 43 % |
| K_off_0p3 | P2_seed1 | 7 | 0.91 | 71 % |
| K_off_0p3 | P12_seed1 | 7 | 0.84 | 57 % |
| K_off_0p3 | P1_seed2 | 7 | 1.00 | 43 % |
| K_off_0p3 | P2_seed2 | 7 | 0.96 | 57 % |
| K_off_0p3 | P12_seed2 | 7 | 0.92 | 71 % |
| K_off_0p1 | P3_oracle | 4 | 0.55 | 100 % |
| K_off_0p1 | P1_seed0 | 4 | 0.94 | 100 % |
| K_off_0p1 | P2_seed0 | 4 | 0.91 | 100 % |
| K_off_0p1 | P12_seed0 | 4 | 0.85 | 75 % |
| K_off_0p1 | P1_seed1 | 4 | 0.86 | 50 % |
| K_off_0p1 | P2_seed1 | 4 | 0.83 | 100 % |
| K_off_0p1 | P12_seed1 | 4 | 0.79 | 100 % |
| K_off_0p1 | P1_seed2 | 4 | 0.94 | 100 % |
| K_off_0p1 | P2_seed2 | 4 | 0.89 | 75 % |
| K_off_0p1 | P12_seed2 | 4 | 0.84 | 75 % |
| n10_inband | P3_oracle | 5 | 0.73 | 60 % |
| n10_inband | P1_seed0 | 5 | 2.05 | 20 % |
| n10_inband | P2_seed0 | 5 | 1.52 | 20 % |
| n10_inband | P12_seed0 | 5 | 1.87 | 20 % |
| n10_inband | P1_seed1 | 5 | 1.71 | 20 % |
| n10_inband | P2_seed1 | 5 | 1.57 | 20 % |
| n10_inband | P12_seed1 | 5 | 1.71 | 20 % |
| n10_inband | P1_seed2 | 5 | 1.86 | 20 % |
| n10_inband | P2_seed2 | 5 | 1.67 | 40 % |
| n10_inband | P12_seed2 | 5 | 1.67 | 20 % |
| n10_all | P3_oracle | 4 | 0.53 | 100 % |
| n10_all | P1_seed0 | 4 | 0.95 | 50 % |
| n10_all | P2_seed0 | 4 | 0.91 | 100 % |
| n10_all | P12_seed0 | 4 | 0.87 | 100 % |
| n10_all | P1_seed1 | 4 | 0.83 | 75 % |
| n10_all | P2_seed1 | 4 | 0.89 | 100 % |
| n10_all | P12_seed1 | 4 | 0.86 | 100 % |
| n10_all | P1_seed2 | 4 | 0.84 | 75 % |
| n10_all | P2_seed2 | 4 | 0.85 | 100 % |
| n10_all | P12_seed2 | 4 | 0.78 | 100 % |
