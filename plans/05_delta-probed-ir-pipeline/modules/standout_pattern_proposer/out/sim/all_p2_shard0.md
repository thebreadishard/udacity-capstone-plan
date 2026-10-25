# Pattern-proposer simulation — pool all, 2026-09-26 21:54

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 13 evaluation molecules.

## eval_parents (n 6; P0 reaches ρ_off ≤ 0.3 on 6)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 6 | 0.20 | 100 % |
| K_off_0p3 | P1_seed0 | 6 | 0.82 | 100 % |
| K_off_0p3 | P2_seed0 | 6 | 0.65 | 83 % |
| K_off_0p3 | P12_seed0 | 6 | 0.70 | 83 % |
| K_off_0p3 | P1_seed1 | 6 | 1.02 | 33 % |
| K_off_0p3 | P2_seed1 | 6 | 0.84 | 67 % |
| K_off_0p3 | P12_seed1 | 6 | 0.74 | 100 % |
| K_off_0p3 | P1_seed2 | 6 | 0.80 | 83 % |
| K_off_0p3 | P2_seed2 | 6 | 0.82 | 67 % |
| K_off_0p3 | P12_seed2 | 6 | 0.73 | 100 % |
| K_off_0p1 | P3_oracle | 5 | 0.47 | 100 % |
| K_off_0p1 | P1_seed0 | 5 | 0.80 | 100 % |
| K_off_0p1 | P2_seed0 | 5 | 0.86 | 80 % |
| K_off_0p1 | P12_seed0 | 5 | 0.81 | 100 % |
| K_off_0p1 | P1_seed1 | 5 | 0.84 | 100 % |
| K_off_0p1 | P2_seed1 | 5 | 0.87 | 60 % |
| K_off_0p1 | P12_seed1 | 5 | 0.83 | 100 % |
| K_off_0p1 | P1_seed2 | 5 | 0.84 | 100 % |
| K_off_0p1 | P2_seed2 | 5 | 0.90 | 80 % |
| K_off_0p1 | P12_seed2 | 5 | 0.79 | 100 % |
| n10_inband | P3_oracle | 6 | 0.55 | 83 % |
| n10_inband | P1_seed0 | 6 | 1.30 | 33 % |
| n10_inband | P2_seed0 | 6 | 1.42 | 17 % |
| n10_inband | P12_seed0 | 6 | 1.19 | 33 % |
| n10_inband | P1_seed1 | 6 | 1.32 | 33 % |
| n10_inband | P2_seed1 | 6 | 1.47 | 17 % |
| n10_inband | P12_seed1 | 6 | 1.25 | 33 % |
| n10_inband | P1_seed2 | 6 | 1.26 | 33 % |
| n10_inband | P2_seed2 | 6 | 1.31 | 33 % |
| n10_inband | P12_seed2 | 6 | 1.26 | 33 % |
| n10_all | P3_oracle | 6 | 0.44 | 100 % |
| n10_all | P1_seed0 | 6 | 0.77 | 100 % |
| n10_all | P2_seed0 | 6 | 0.78 | 100 % |
| n10_all | P12_seed0 | 6 | 0.79 | 100 % |
| n10_all | P1_seed1 | 6 | 0.80 | 100 % |
| n10_all | P2_seed1 | 6 | 0.85 | 83 % |
| n10_all | P12_seed1 | 6 | 0.81 | 100 % |
| n10_all | P1_seed2 | 6 | 0.81 | 100 % |
| n10_all | P2_seed2 | 6 | 0.80 | 100 % |
| n10_all | P12_seed2 | 6 | 0.77 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.28 | 100 % |
| K_off_0p3 | P1_seed0 | 4 | 0.62 | 100 % |
| K_off_0p3 | P2_seed0 | 4 | 0.66 | 100 % |
| K_off_0p3 | P12_seed0 | 4 | 0.59 | 100 % |
| K_off_0p3 | P1_seed1 | 4 | 0.66 | 100 % |
| K_off_0p3 | P2_seed1 | 4 | 0.83 | 100 % |
| K_off_0p3 | P12_seed1 | 4 | 0.64 | 100 % |
| K_off_0p3 | P1_seed2 | 4 | 0.59 | 100 % |
| K_off_0p3 | P2_seed2 | 4 | 0.68 | 100 % |
| K_off_0p3 | P12_seed2 | 4 | 0.57 | 100 % |
| K_off_0p1 | P3_oracle | 1 | 0.50 | 100 % |
| K_off_0p1 | P1_seed0 | 1 | 0.71 | 100 % |
| K_off_0p1 | P2_seed0 | 1 | 0.88 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.73 | 100 % |
| K_off_0p1 | P1_seed1 | 1 | 0.79 | 100 % |
| K_off_0p1 | P2_seed1 | 1 | 0.80 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.71 | 100 % |
| K_off_0p1 | P1_seed2 | 1 | 0.70 | 100 % |
| K_off_0p1 | P2_seed2 | 1 | 0.71 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.70 | 100 % |
| n10_inband | P3_oracle | 4 | 0.92 | 50 % |
| n10_inband | P1_seed0 | 4 | 1.20 | 25 % |
| n10_inband | P2_seed0 | 4 | 1.14 | 25 % |
| n10_inband | P12_seed0 | 4 | 1.14 | 25 % |
| n10_inband | P1_seed1 | 4 | 1.27 | 25 % |
| n10_inband | P2_seed1 | 4 | 1.16 | 25 % |
| n10_inband | P12_seed1 | 4 | 1.17 | 25 % |
| n10_inband | P1_seed2 | 4 | 1.17 | 25 % |
| n10_inband | P2_seed2 | 4 | 1.18 | 25 % |
| n10_inband | P12_seed2 | 4 | 1.06 | 50 % |
| n10_all | P3_oracle | 4 | 0.72 | 100 % |
| n10_all | P1_seed0 | 4 | 0.94 | 100 % |
| n10_all | P2_seed0 | 4 | 0.93 | 75 % |
| n10_all | P12_seed0 | 4 | 0.91 | 100 % |
| n10_all | P1_seed1 | 4 | 0.92 | 100 % |
| n10_all | P2_seed1 | 4 | 0.89 | 75 % |
| n10_all | P12_seed1 | 4 | 0.88 | 100 % |
| n10_all | P1_seed2 | 4 | 0.92 | 100 % |
| n10_all | P2_seed2 | 4 | 0.91 | 75 % |
| n10_all | P12_seed2 | 4 | 0.89 | 100 % |
