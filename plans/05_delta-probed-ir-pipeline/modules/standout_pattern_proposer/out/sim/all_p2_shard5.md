# Pattern-proposer simulation — pool all, 2026-09-26 19:50

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.33 | 100 % |
| K_off_0p3 | P1_seed0 | 5 | 0.67 | 100 % |
| K_off_0p3 | P2_seed0 | 5 | 0.74 | 60 % |
| K_off_0p3 | P12_seed0 | 5 | 0.67 | 100 % |
| K_off_0p3 | P1_seed1 | 5 | 0.62 | 100 % |
| K_off_0p3 | P2_seed1 | 5 | 0.53 | 80 % |
| K_off_0p3 | P12_seed1 | 5 | 0.59 | 100 % |
| K_off_0p3 | P1_seed2 | 5 | 0.63 | 100 % |
| K_off_0p3 | P2_seed2 | 5 | 0.52 | 100 % |
| K_off_0p3 | P12_seed2 | 5 | 0.53 | 100 % |
| K_off_0p1 | P3_oracle | 4 | 0.38 | 75 % |
| K_off_0p1 | P1_seed0 | 4 | 0.80 | 75 % |
| K_off_0p1 | P2_seed0 | 4 | 0.84 | 100 % |
| K_off_0p1 | P12_seed0 | 4 | 0.77 | 75 % |
| K_off_0p1 | P1_seed1 | 4 | 0.81 | 75 % |
| K_off_0p1 | P2_seed1 | 4 | 0.84 | 100 % |
| K_off_0p1 | P12_seed1 | 4 | 0.77 | 100 % |
| K_off_0p1 | P1_seed2 | 4 | 0.75 | 75 % |
| K_off_0p1 | P2_seed2 | 4 | 0.87 | 100 % |
| K_off_0p1 | P12_seed2 | 4 | 0.75 | 75 % |
| n10_inband | P3_oracle | 5 | 0.85 | 60 % |
| n10_inband | P1_seed0 | 5 | 1.84 | 20 % |
| n10_inband | P2_seed0 | 5 | 1.58 | 20 % |
| n10_inband | P12_seed0 | 5 | 1.47 | 20 % |
| n10_inband | P1_seed1 | 5 | 1.68 | 0 % |
| n10_inband | P2_seed1 | 5 | 1.56 | 20 % |
| n10_inband | P12_seed1 | 5 | 1.68 | 20 % |
| n10_inband | P1_seed2 | 5 | 1.58 | 20 % |
| n10_inband | P2_seed2 | 5 | 1.56 | 20 % |
| n10_inband | P12_seed2 | 5 | 1.63 | 20 % |
| n10_all | P3_oracle | 5 | 0.43 | 100 % |
| n10_all | P1_seed0 | 5 | 0.82 | 100 % |
| n10_all | P2_seed0 | 5 | 0.71 | 100 % |
| n10_all | P12_seed0 | 5 | 0.73 | 100 % |
| n10_all | P1_seed1 | 5 | 0.85 | 100 % |
| n10_all | P2_seed1 | 5 | 0.78 | 100 % |
| n10_all | P12_seed1 | 5 | 0.73 | 100 % |
| n10_all | P1_seed2 | 5 | 0.80 | 100 % |
| n10_all | P2_seed2 | 5 | 0.73 | 100 % |
| n10_all | P12_seed2 | 5 | 0.70 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 7)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 7 | 0.41 | 100 % |
| K_off_0p3 | P1_seed0 | 7 | 0.71 | 71 % |
| K_off_0p3 | P2_seed0 | 7 | 0.71 | 100 % |
| K_off_0p3 | P12_seed0 | 7 | 0.59 | 100 % |
| K_off_0p3 | P1_seed1 | 7 | 0.73 | 71 % |
| K_off_0p3 | P2_seed1 | 7 | 0.64 | 100 % |
| K_off_0p3 | P12_seed1 | 7 | 0.55 | 86 % |
| K_off_0p3 | P1_seed2 | 7 | 0.76 | 71 % |
| K_off_0p3 | P2_seed2 | 7 | 0.62 | 86 % |
| K_off_0p3 | P12_seed2 | 7 | 0.65 | 71 % |
| K_off_0p1 | P3_oracle | 2 | 0.52 | 100 % |
| K_off_0p1 | P1_seed0 | 2 | 0.79 | 100 % |
| K_off_0p1 | P2_seed0 | 2 | 0.78 | 100 % |
| K_off_0p1 | P12_seed0 | 2 | 0.73 | 100 % |
| K_off_0p1 | P1_seed1 | 2 | 0.79 | 100 % |
| K_off_0p1 | P2_seed1 | 2 | 0.76 | 100 % |
| K_off_0p1 | P12_seed1 | 2 | 0.76 | 100 % |
| K_off_0p1 | P1_seed2 | 2 | 0.73 | 100 % |
| K_off_0p1 | P2_seed2 | 2 | 0.70 | 100 % |
| K_off_0p1 | P12_seed2 | 2 | 0.71 | 100 % |
| n10_inband | P3_oracle | 4 | 0.97 | 50 % |
| n10_inband | P1_seed0 | 4 | 1.21 | 0 % |
| n10_inband | P2_seed0 | 4 | 1.20 | 25 % |
| n10_inband | P12_seed0 | 4 | 1.17 | 0 % |
| n10_inband | P1_seed1 | 4 | 1.19 | 0 % |
| n10_inband | P2_seed1 | 4 | 1.13 | 25 % |
| n10_inband | P12_seed1 | 4 | 1.22 | 0 % |
| n10_inband | P1_seed2 | 4 | 1.19 | 25 % |
| n10_inband | P2_seed2 | 4 | 1.17 | 25 % |
| n10_inband | P12_seed2 | 4 | 1.16 | 0 % |
| n10_all | P3_oracle | 4 | 0.71 | 100 % |
| n10_all | P1_seed0 | 4 | 0.99 | 50 % |
| n10_all | P2_seed0 | 4 | 0.90 | 50 % |
| n10_all | P12_seed0 | 4 | 0.93 | 75 % |
| n10_all | P1_seed1 | 4 | 0.99 | 50 % |
| n10_all | P2_seed1 | 4 | 0.88 | 100 % |
| n10_all | P12_seed1 | 4 | 0.92 | 100 % |
| n10_all | P1_seed2 | 4 | 1.00 | 25 % |
| n10_all | P2_seed2 | 4 | 0.86 | 75 % |
| n10_all | P12_seed2 | 4 | 0.91 | 100 % |
