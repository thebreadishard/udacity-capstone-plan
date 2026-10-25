# Pattern-proposer simulation — pool all, 2026-09-26 23:22

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.27 | 100 % |
| K_off_0p3 | P1_seed0 | 4 | 1.07 | 25 % |
| K_off_0p3 | P2_seed0 | 4 | 1.04 | 50 % |
| K_off_0p3 | P12_seed0 | 4 | 0.81 | 75 % |
| K_off_0p3 | P1_seed1 | 4 | 0.93 | 50 % |
| K_off_0p3 | P2_seed1 | 4 | 0.99 | 50 % |
| K_off_0p3 | P12_seed1 | 4 | 0.98 | 50 % |
| K_off_0p3 | P1_seed2 | 4 | 0.85 | 75 % |
| K_off_0p3 | P2_seed2 | 4 | 1.00 | 50 % |
| K_off_0p3 | P12_seed2 | 4 | 0.96 | 75 % |
| K_off_0p1 | P3_oracle | 2 | 0.29 | 100 % |
| K_off_0p1 | P1_seed0 | 2 | 0.88 | 50 % |
| K_off_0p1 | P2_seed0 | 2 | 0.85 | 50 % |
| K_off_0p1 | P12_seed0 | 2 | 0.86 | 50 % |
| K_off_0p1 | P1_seed1 | 2 | 0.82 | 50 % |
| K_off_0p1 | P2_seed1 | 2 | 0.84 | 50 % |
| K_off_0p1 | P12_seed1 | 2 | 0.84 | 50 % |
| K_off_0p1 | P1_seed2 | 2 | 0.88 | 50 % |
| K_off_0p1 | P2_seed2 | 2 | 0.86 | 50 % |
| K_off_0p1 | P12_seed2 | 2 | 0.88 | 50 % |
| n10_inband | P3_oracle | 3 | 1.17 | 33 % |
| n10_inband | P1_seed0 | 3 | 2.44 | 0 % |
| n10_inband | P2_seed0 | 3 | 2.72 | 0 % |
| n10_inband | P12_seed0 | 3 | 2.50 | 0 % |
| n10_inband | P1_seed1 | 3 | 2.67 | 0 % |
| n10_inband | P2_seed1 | 3 | 2.33 | 0 % |
| n10_inband | P12_seed1 | 3 | 2.39 | 0 % |
| n10_inband | P1_seed2 | 3 | 2.44 | 0 % |
| n10_inband | P2_seed2 | 3 | 2.28 | 33 % |
| n10_inband | P12_seed2 | 3 | 2.22 | 0 % |
| n10_all | P3_oracle | 3 | 0.41 | 100 % |
| n10_all | P1_seed0 | 3 | 0.98 | 67 % |
| n10_all | P2_seed0 | 3 | 0.94 | 67 % |
| n10_all | P12_seed0 | 3 | 0.90 | 67 % |
| n10_all | P1_seed1 | 3 | 1.00 | 33 % |
| n10_all | P2_seed1 | 3 | 0.88 | 67 % |
| n10_all | P12_seed1 | 3 | 0.90 | 67 % |
| n10_all | P1_seed2 | 3 | 0.98 | 67 % |
| n10_all | P2_seed2 | 3 | 0.90 | 67 % |
| n10_all | P12_seed2 | 3 | 0.90 | 67 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 6)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 6 | 0.50 | 83 % |
| K_off_0p3 | P1_seed0 | 6 | 1.16 | 50 % |
| K_off_0p3 | P2_seed0 | 6 | 1.07 | 50 % |
| K_off_0p3 | P12_seed0 | 6 | 1.05 | 50 % |
| K_off_0p3 | P1_seed1 | 6 | 1.23 | 50 % |
| K_off_0p3 | P2_seed1 | 6 | 1.09 | 50 % |
| K_off_0p3 | P12_seed1 | 6 | 1.05 | 50 % |
| K_off_0p3 | P1_seed2 | 6 | 1.11 | 50 % |
| K_off_0p3 | P2_seed2 | 6 | 1.03 | 50 % |
| K_off_0p3 | P12_seed2 | 6 | 1.04 | 50 % |
| K_off_0p1 | P3_oracle | 3 | 0.47 | 100 % |
| K_off_0p1 | P1_seed0 | 3 | 1.05 | 33 % |
| K_off_0p1 | P2_seed0 | 3 | 1.05 | 33 % |
| K_off_0p1 | P12_seed0 | 3 | 0.97 | 67 % |
| K_off_0p1 | P1_seed1 | 3 | 1.00 | 33 % |
| K_off_0p1 | P2_seed1 | 3 | 1.12 | 33 % |
| K_off_0p1 | P12_seed1 | 3 | 1.12 | 33 % |
| K_off_0p1 | P1_seed2 | 3 | 0.95 | 67 % |
| K_off_0p1 | P2_seed2 | 3 | 0.93 | 67 % |
| K_off_0p1 | P12_seed2 | 3 | 0.93 | 67 % |
| n10_inband | P3_oracle | 6 | 1.44 | 17 % |
| n10_inband | P1_seed0 | 6 | 2.58 | 0 % |
| n10_inband | P2_seed0 | 6 | 2.83 | 0 % |
| n10_inband | P12_seed0 | 6 | 2.60 | 0 % |
| n10_inband | P1_seed1 | 6 | 2.64 | 0 % |
| n10_inband | P2_seed1 | 6 | 2.44 | 0 % |
| n10_inband | P12_seed1 | 6 | 2.57 | 0 % |
| n10_inband | P1_seed2 | 6 | 2.71 | 0 % |
| n10_inband | P2_seed2 | 6 | 2.65 | 0 % |
| n10_inband | P12_seed2 | 6 | 2.65 | 0 % |
| n10_all | P3_oracle | 5 | 0.71 | 100 % |
| n10_all | P1_seed0 | 5 | 0.95 | 60 % |
| n10_all | P2_seed0 | 5 | 0.95 | 80 % |
| n10_all | P12_seed0 | 5 | 0.95 | 100 % |
| n10_all | P1_seed1 | 5 | 0.97 | 60 % |
| n10_all | P2_seed1 | 5 | 0.93 | 100 % |
| n10_all | P12_seed1 | 5 | 0.93 | 100 % |
| n10_all | P1_seed2 | 5 | 0.95 | 60 % |
| n10_all | P2_seed2 | 5 | 0.93 | 100 % |
| n10_all | P12_seed2 | 5 | 0.95 | 100 % |
