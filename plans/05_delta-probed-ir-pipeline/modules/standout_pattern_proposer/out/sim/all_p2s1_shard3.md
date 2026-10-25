# Pattern-proposer simulation — pool all, 2026-09-27 11:28

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 19 evaluation molecules.

## eval_parents (n 8; P0 reaches ρ_off ≤ 0.3 on 8)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 8 | 0.27 | 100 % |
| K_off_0p3 | P1_seed0 | 8 | 0.84 | 75 % |
| K_off_0p3 | P2_seed0 | 8 | 0.67 | 75 % |
| K_off_0p3 | P12_seed0 | 8 | 0.63 | 75 % |
| K_off_0p3 | P1_seed1 | 8 | 0.67 | 75 % |
| K_off_0p3 | P2_seed1 | 8 | 0.74 | 75 % |
| K_off_0p3 | P12_seed1 | 8 | 0.53 | 75 % |
| K_off_0p3 | P1_seed2 | 8 | 0.65 | 88 % |
| K_off_0p3 | P2_seed2 | 8 | 0.65 | 75 % |
| K_off_0p3 | P12_seed2 | 8 | 0.62 | 88 % |
| K_off_0p1 | P3_oracle | 4 | 0.47 | 100 % |
| K_off_0p1 | P1_seed0 | 4 | 0.71 | 75 % |
| K_off_0p1 | P2_seed0 | 4 | 0.70 | 75 % |
| K_off_0p1 | P12_seed0 | 4 | 0.65 | 75 % |
| K_off_0p1 | P1_seed1 | 4 | 0.76 | 75 % |
| K_off_0p1 | P2_seed1 | 4 | 0.65 | 75 % |
| K_off_0p1 | P12_seed1 | 4 | 0.66 | 75 % |
| K_off_0p1 | P1_seed2 | 4 | 0.74 | 75 % |
| K_off_0p1 | P2_seed2 | 4 | 0.68 | 75 % |
| K_off_0p1 | P12_seed2 | 4 | 0.67 | 75 % |
| n10_inband | P3_oracle | 6 | 0.70 | 67 % |
| n10_inband | P1_seed0 | 6 | 1.35 | 17 % |
| n10_inband | P2_seed0 | 6 | 1.55 | 17 % |
| n10_inband | P12_seed0 | 6 | 1.42 | 17 % |
| n10_inband | P1_seed1 | 6 | 1.37 | 17 % |
| n10_inband | P2_seed1 | 6 | 1.51 | 17 % |
| n10_inband | P12_seed1 | 6 | 1.36 | 17 % |
| n10_inband | P1_seed2 | 6 | 1.36 | 17 % |
| n10_inband | P2_seed2 | 6 | 1.51 | 17 % |
| n10_inband | P12_seed2 | 6 | 1.40 | 17 % |
| n10_all | P3_oracle | 6 | 0.45 | 100 % |
| n10_all | P1_seed0 | 6 | 0.82 | 67 % |
| n10_all | P2_seed0 | 6 | 0.76 | 83 % |
| n10_all | P12_seed0 | 6 | 0.71 | 67 % |
| n10_all | P1_seed1 | 6 | 0.86 | 67 % |
| n10_all | P2_seed1 | 6 | 0.82 | 83 % |
| n10_all | P12_seed1 | 6 | 0.76 | 67 % |
| n10_all | P1_seed2 | 6 | 0.85 | 67 % |
| n10_all | P2_seed2 | 6 | 0.74 | 83 % |
| n10_all | P12_seed2 | 6 | 0.76 | 67 % |

## eval (n 11; P0 reaches ρ_off ≤ 0.3 on 7)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 7 | 0.47 | 86 % |
| K_off_0p3 | P1_seed0 | 7 | 0.71 | 57 % |
| K_off_0p3 | P2_seed0 | 7 | 0.73 | 71 % |
| K_off_0p3 | P12_seed0 | 7 | 0.76 | 86 % |
| K_off_0p3 | P1_seed1 | 7 | 0.82 | 57 % |
| K_off_0p3 | P2_seed1 | 7 | 0.83 | 57 % |
| K_off_0p3 | P12_seed1 | 7 | 0.83 | 57 % |
| K_off_0p3 | P1_seed2 | 7 | 0.85 | 57 % |
| K_off_0p3 | P2_seed2 | 7 | 0.64 | 57 % |
| K_off_0p3 | P12_seed2 | 7 | 0.63 | 71 % |
| K_off_0p1 | P3_oracle | 1 | 0.55 | 100 % |
| K_off_0p1 | P1_seed0 | 1 | 0.75 | 100 % |
| K_off_0p1 | P2_seed0 | 1 | 0.71 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.75 | 100 % |
| K_off_0p1 | P1_seed1 | 1 | 0.76 | 100 % |
| K_off_0p1 | P2_seed1 | 1 | 0.73 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.71 | 100 % |
| K_off_0p1 | P1_seed2 | 1 | 0.71 | 100 % |
| K_off_0p1 | P2_seed2 | 1 | 0.73 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.75 | 100 % |
| n10_inband | P3_oracle | 4 | 1.33 | 25 % |
| n10_inband | P1_seed0 | 4 | 1.38 | 0 % |
| n10_inband | P2_seed0 | 4 | 1.27 | 25 % |
| n10_inband | P12_seed0 | 4 | 1.33 | 0 % |
| n10_inband | P1_seed1 | 4 | 1.37 | 0 % |
| n10_inband | P2_seed1 | 4 | 1.33 | 25 % |
| n10_inband | P12_seed1 | 4 | 1.34 | 0 % |
| n10_inband | P1_seed2 | 4 | 1.38 | 25 % |
| n10_inband | P2_seed2 | 4 | 1.26 | 25 % |
| n10_inband | P12_seed2 | 4 | 1.35 | 0 % |
| n10_all | P3_oracle | 3 | 0.78 | 100 % |
| n10_all | P1_seed0 | 3 | 0.97 | 67 % |
| n10_all | P2_seed0 | 3 | 0.93 | 100 % |
| n10_all | P12_seed0 | 3 | 0.95 | 100 % |
| n10_all | P1_seed1 | 3 | 0.97 | 67 % |
| n10_all | P2_seed1 | 3 | 0.93 | 100 % |
| n10_all | P12_seed1 | 3 | 0.95 | 100 % |
| n10_all | P1_seed2 | 3 | 0.99 | 67 % |
| n10_all | P2_seed2 | 3 | 0.97 | 100 % |
| n10_all | P12_seed2 | 3 | 0.95 | 100 % |
