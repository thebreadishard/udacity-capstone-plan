# Pattern-proposer simulation — pool all, 2026-09-27 13:10

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 20 evaluation molecules.

## eval_parents (n 9; P0 reaches ρ_off ≤ 0.3 on 7)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 7 | 0.13 | 100 % |
| K_off_0p3 | P1_seed0 | 7 | 0.88 | 71 % |
| K_off_0p3 | P2_seed0 | 7 | 0.58 | 100 % |
| K_off_0p3 | P12_seed0 | 7 | 0.58 | 86 % |
| K_off_0p3 | P1_seed1 | 7 | 0.72 | 57 % |
| K_off_0p3 | P2_seed1 | 7 | 0.65 | 100 % |
| K_off_0p3 | P12_seed1 | 7 | 0.42 | 86 % |
| K_off_0p3 | P1_seed2 | 7 | 0.80 | 57 % |
| K_off_0p3 | P2_seed2 | 7 | 0.54 | 100 % |
| K_off_0p3 | P12_seed2 | 7 | 0.46 | 86 % |
| K_off_0p1 | P3_oracle | 6 | 0.24 | 83 % |
| K_off_0p1 | P1_seed0 | 6 | 0.90 | 100 % |
| K_off_0p1 | P2_seed0 | 6 | 0.72 | 100 % |
| K_off_0p1 | P12_seed0 | 6 | 0.66 | 100 % |
| K_off_0p1 | P1_seed1 | 6 | 0.84 | 100 % |
| K_off_0p1 | P2_seed1 | 6 | 0.78 | 83 % |
| K_off_0p1 | P12_seed1 | 6 | 0.76 | 100 % |
| K_off_0p1 | P1_seed2 | 6 | 0.87 | 83 % |
| K_off_0p1 | P2_seed2 | 6 | 0.77 | 100 % |
| K_off_0p1 | P12_seed2 | 6 | 0.69 | 100 % |
| n10_inband | P3_oracle | 7 | 0.55 | 86 % |
| n10_inband | P1_seed0 | 7 | 1.56 | 14 % |
| n10_inband | P2_seed0 | 7 | 1.36 | 14 % |
| n10_inband | P12_seed0 | 7 | 1.24 | 43 % |
| n10_inband | P1_seed1 | 7 | 1.68 | 14 % |
| n10_inband | P2_seed1 | 7 | 1.32 | 14 % |
| n10_inband | P12_seed1 | 7 | 1.32 | 14 % |
| n10_inband | P1_seed2 | 7 | 1.58 | 14 % |
| n10_inband | P2_seed2 | 7 | 1.40 | 14 % |
| n10_inband | P12_seed2 | 7 | 1.36 | 29 % |
| n10_all | P3_oracle | 8 | 0.22 | 100 % |
| n10_all | P1_seed0 | 8 | 0.78 | 88 % |
| n10_all | P2_seed0 | 8 | 0.67 | 88 % |
| n10_all | P12_seed0 | 8 | 0.67 | 100 % |
| n10_all | P1_seed1 | 8 | 0.76 | 88 % |
| n10_all | P2_seed1 | 8 | 0.76 | 100 % |
| n10_all | P12_seed1 | 8 | 0.69 | 100 % |
| n10_all | P1_seed2 | 8 | 0.84 | 88 % |
| n10_all | P2_seed2 | 8 | 0.75 | 100 % |
| n10_all | P12_seed2 | 8 | 0.70 | 100 % |

## eval (n 11; P0 reaches ρ_off ≤ 0.3 on 9)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 9 | 0.53 | 89 % |
| K_off_0p3 | P1_seed0 | 9 | 0.96 | 56 % |
| K_off_0p3 | P2_seed0 | 9 | 0.89 | 67 % |
| K_off_0p3 | P12_seed0 | 9 | 0.80 | 67 % |
| K_off_0p3 | P1_seed1 | 9 | 1.04 | 44 % |
| K_off_0p3 | P2_seed1 | 9 | 0.88 | 67 % |
| K_off_0p3 | P12_seed1 | 9 | 0.83 | 56 % |
| K_off_0p3 | P1_seed2 | 9 | 0.91 | 56 % |
| K_off_0p3 | P2_seed2 | 9 | 0.83 | 67 % |
| K_off_0p3 | P12_seed2 | 9 | 0.85 | 78 % |
| K_off_0p1 | P3_oracle | 3 | 0.47 | 100 % |
| K_off_0p1 | P1_seed0 | 3 | 0.78 | 100 % |
| K_off_0p1 | P2_seed0 | 3 | 0.78 | 100 % |
| K_off_0p1 | P12_seed0 | 3 | 0.78 | 100 % |
| K_off_0p1 | P1_seed1 | 3 | 0.75 | 67 % |
| K_off_0p1 | P2_seed1 | 3 | 0.78 | 100 % |
| K_off_0p1 | P12_seed1 | 3 | 0.76 | 100 % |
| K_off_0p1 | P1_seed2 | 3 | 0.73 | 100 % |
| K_off_0p1 | P2_seed2 | 3 | 0.76 | 100 % |
| K_off_0p1 | P12_seed2 | 3 | 0.70 | 100 % |
| n10_inband | P3_oracle | 7 | 1.03 | 43 % |
| n10_inband | P1_seed0 | 7 | 1.33 | 0 % |
| n10_inband | P2_seed0 | 7 | 1.36 | 0 % |
| n10_inband | P12_seed0 | 7 | 1.28 | 0 % |
| n10_inband | P1_seed1 | 7 | 1.44 | 0 % |
| n10_inband | P2_seed1 | 7 | 1.36 | 0 % |
| n10_inband | P12_seed1 | 7 | 1.28 | 0 % |
| n10_inband | P1_seed2 | 7 | 1.44 | 0 % |
| n10_inband | P2_seed2 | 7 | 1.19 | 0 % |
| n10_inband | P12_seed2 | 7 | 1.24 | 0 % |
| n10_all | P3_oracle | 6 | 0.66 | 100 % |
| n10_all | P1_seed0 | 6 | 0.95 | 83 % |
| n10_all | P2_seed0 | 6 | 0.86 | 83 % |
| n10_all | P12_seed0 | 6 | 0.85 | 83 % |
| n10_all | P1_seed1 | 6 | 0.96 | 67 % |
| n10_all | P2_seed1 | 6 | 0.86 | 83 % |
| n10_all | P12_seed1 | 6 | 0.86 | 83 % |
| n10_all | P1_seed2 | 6 | 0.91 | 67 % |
| n10_all | P2_seed2 | 6 | 0.85 | 100 % |
| n10_all | P12_seed2 | 6 | 0.86 | 100 % |
