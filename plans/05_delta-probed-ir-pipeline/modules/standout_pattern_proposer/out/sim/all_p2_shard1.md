# Pattern-proposer simulation — pool all, 2026-09-26 16:22

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.22 | 100 % |
| K_off_0p3 | P1_seed0 | 5 | 0.88 | 60 % |
| K_off_0p3 | P2_seed0 | 5 | 0.83 | 80 % |
| K_off_0p3 | P12_seed0 | 5 | 0.84 | 80 % |
| K_off_0p3 | P1_seed1 | 5 | 0.72 | 80 % |
| K_off_0p3 | P2_seed1 | 5 | 0.74 | 60 % |
| K_off_0p3 | P12_seed1 | 5 | 0.87 | 80 % |
| K_off_0p3 | P1_seed2 | 5 | 0.80 | 80 % |
| K_off_0p3 | P2_seed2 | 5 | 0.78 | 80 % |
| K_off_0p3 | P12_seed2 | 5 | 0.78 | 80 % |
| K_off_0p1 | P3_oracle | 2 | 0.30 | 100 % |
| K_off_0p1 | P1_seed0 | 2 | 0.75 | 100 % |
| K_off_0p1 | P2_seed0 | 2 | 0.71 | 100 % |
| K_off_0p1 | P12_seed0 | 2 | 0.70 | 100 % |
| K_off_0p1 | P1_seed1 | 2 | 0.73 | 100 % |
| K_off_0p1 | P2_seed1 | 2 | 0.75 | 100 % |
| K_off_0p1 | P12_seed1 | 2 | 0.69 | 100 % |
| K_off_0p1 | P1_seed2 | 2 | 0.73 | 100 % |
| K_off_0p1 | P2_seed2 | 2 | 0.72 | 100 % |
| K_off_0p1 | P12_seed2 | 2 | 0.73 | 100 % |
| n10_inband | P3_oracle | 4 | 0.84 | 50 % |
| n10_inband | P1_seed0 | 4 | 1.25 | 25 % |
| n10_inband | P2_seed0 | 4 | 1.33 | 25 % |
| n10_inband | P12_seed0 | 4 | 1.33 | 25 % |
| n10_inband | P1_seed1 | 4 | 1.33 | 25 % |
| n10_inband | P2_seed1 | 4 | 1.41 | 25 % |
| n10_inband | P12_seed1 | 4 | 1.35 | 25 % |
| n10_inband | P1_seed2 | 4 | 1.22 | 25 % |
| n10_inband | P2_seed2 | 4 | 1.26 | 25 % |
| n10_inband | P12_seed2 | 4 | 1.27 | 25 % |
| n10_all | P3_oracle | 4 | 0.43 | 100 % |
| n10_all | P1_seed0 | 4 | 0.83 | 75 % |
| n10_all | P2_seed0 | 4 | 0.78 | 75 % |
| n10_all | P12_seed0 | 4 | 0.75 | 75 % |
| n10_all | P1_seed1 | 4 | 0.85 | 75 % |
| n10_all | P2_seed1 | 4 | 0.80 | 75 % |
| n10_all | P12_seed1 | 4 | 0.76 | 75 % |
| n10_all | P1_seed2 | 4 | 0.82 | 75 % |
| n10_all | P2_seed2 | 4 | 0.79 | 75 % |
| n10_all | P12_seed2 | 4 | 0.78 | 75 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 6)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 6 | 0.34 | 100 % |
| K_off_0p3 | P1_seed0 | 6 | 0.84 | 67 % |
| K_off_0p3 | P2_seed0 | 6 | 0.82 | 83 % |
| K_off_0p3 | P12_seed0 | 6 | 0.83 | 100 % |
| K_off_0p3 | P1_seed1 | 6 | 1.02 | 33 % |
| K_off_0p3 | P2_seed1 | 6 | 0.76 | 83 % |
| K_off_0p3 | P12_seed1 | 6 | 0.68 | 67 % |
| K_off_0p3 | P1_seed2 | 6 | 0.93 | 67 % |
| K_off_0p3 | P2_seed2 | 6 | 0.66 | 83 % |
| K_off_0p3 | P12_seed2 | 6 | 0.59 | 83 % |
| K_off_0p1 | P3_oracle | 4 | 0.44 | 100 % |
| K_off_0p1 | P1_seed0 | 4 | 0.82 | 75 % |
| K_off_0p1 | P2_seed0 | 4 | 0.71 | 75 % |
| K_off_0p1 | P12_seed0 | 4 | 0.74 | 75 % |
| K_off_0p1 | P1_seed1 | 4 | 0.82 | 75 % |
| K_off_0p1 | P2_seed1 | 4 | 0.81 | 75 % |
| K_off_0p1 | P12_seed1 | 4 | 0.78 | 75 % |
| K_off_0p1 | P1_seed2 | 4 | 0.81 | 75 % |
| K_off_0p1 | P2_seed2 | 4 | 0.70 | 75 % |
| K_off_0p1 | P12_seed2 | 4 | 0.60 | 75 % |
| n10_inband | P3_oracle | 6 | 0.90 | 67 % |
| n10_inband | P1_seed0 | 6 | 1.66 | 17 % |
| n10_inband | P2_seed0 | 6 | 1.50 | 0 % |
| n10_inband | P12_seed0 | 6 | 1.54 | 17 % |
| n10_inband | P1_seed1 | 6 | 1.66 | 17 % |
| n10_inband | P2_seed1 | 6 | 1.41 | 0 % |
| n10_inband | P12_seed1 | 6 | 1.44 | 17 % |
| n10_inband | P1_seed2 | 6 | 1.58 | 17 % |
| n10_inband | P2_seed2 | 6 | 1.47 | 17 % |
| n10_inband | P12_seed2 | 6 | 1.27 | 17 % |
| n10_all | P3_oracle | 6 | 0.45 | 100 % |
| n10_all | P1_seed0 | 6 | 0.83 | 83 % |
| n10_all | P2_seed0 | 6 | 0.69 | 100 % |
| n10_all | P12_seed0 | 6 | 0.67 | 100 % |
| n10_all | P1_seed1 | 6 | 0.81 | 83 % |
| n10_all | P2_seed1 | 6 | 0.73 | 83 % |
| n10_all | P12_seed1 | 6 | 0.68 | 83 % |
| n10_all | P1_seed2 | 6 | 0.73 | 83 % |
| n10_all | P2_seed2 | 6 | 0.66 | 83 % |
| n10_all | P12_seed2 | 6 | 0.64 | 83 % |
