# Pattern-proposer simulation — pool all, 2026-09-27 10:56

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 19 evaluation molecules.

## eval_parents (n 8; P0 reaches ρ_off ≤ 0.3 on 8)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 8 | 0.28 | 100 % |
| K_off_0p3 | P1_seed0 | 8 | 0.73 | 75 % |
| K_off_0p3 | P2_seed0 | 8 | 0.64 | 75 % |
| K_off_0p3 | P12_seed0 | 8 | 0.74 | 75 % |
| K_off_0p3 | P1_seed1 | 8 | 0.88 | 62 % |
| K_off_0p3 | P2_seed1 | 8 | 0.63 | 62 % |
| K_off_0p3 | P12_seed1 | 8 | 0.71 | 75 % |
| K_off_0p3 | P1_seed2 | 8 | 0.73 | 88 % |
| K_off_0p3 | P2_seed2 | 8 | 0.64 | 62 % |
| K_off_0p3 | P12_seed2 | 8 | 0.68 | 88 % |
| K_off_0p1 | P3_oracle | 4 | 0.38 | 100 % |
| K_off_0p1 | P1_seed0 | 4 | 0.82 | 75 % |
| K_off_0p1 | P2_seed0 | 4 | 0.64 | 100 % |
| K_off_0p1 | P12_seed0 | 4 | 0.72 | 100 % |
| K_off_0p1 | P1_seed1 | 4 | 0.81 | 75 % |
| K_off_0p1 | P2_seed1 | 4 | 0.79 | 100 % |
| K_off_0p1 | P12_seed1 | 4 | 0.64 | 100 % |
| K_off_0p1 | P1_seed2 | 4 | 0.86 | 75 % |
| K_off_0p1 | P2_seed2 | 4 | 0.72 | 100 % |
| K_off_0p1 | P12_seed2 | 4 | 0.75 | 100 % |
| n10_inband | P3_oracle | 8 | 1.11 | 38 % |
| n10_inband | P1_seed0 | 8 | 1.58 | 12 % |
| n10_inband | P2_seed0 | 8 | 1.52 | 12 % |
| n10_inband | P12_seed0 | 8 | 1.58 | 12 % |
| n10_inband | P1_seed1 | 8 | 1.62 | 12 % |
| n10_inband | P2_seed1 | 8 | 1.58 | 12 % |
| n10_inband | P12_seed1 | 8 | 1.58 | 12 % |
| n10_inband | P1_seed2 | 8 | 1.56 | 12 % |
| n10_inband | P2_seed2 | 8 | 1.56 | 12 % |
| n10_inband | P12_seed2 | 8 | 1.57 | 12 % |
| n10_all | P3_oracle | 8 | 0.45 | 100 % |
| n10_all | P1_seed0 | 8 | 0.80 | 75 % |
| n10_all | P2_seed0 | 8 | 0.68 | 88 % |
| n10_all | P12_seed0 | 8 | 0.71 | 88 % |
| n10_all | P1_seed1 | 8 | 0.80 | 62 % |
| n10_all | P2_seed1 | 8 | 0.72 | 88 % |
| n10_all | P12_seed1 | 8 | 0.71 | 88 % |
| n10_all | P1_seed2 | 8 | 0.78 | 88 % |
| n10_all | P2_seed2 | 8 | 0.73 | 88 % |
| n10_all | P12_seed2 | 8 | 0.76 | 88 % |

## eval (n 11; P0 reaches ρ_off ≤ 0.3 on 10)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 10 | 0.48 | 100 % |
| K_off_0p3 | P1_seed0 | 10 | 1.02 | 50 % |
| K_off_0p3 | P2_seed0 | 10 | 0.93 | 60 % |
| K_off_0p3 | P12_seed0 | 10 | 1.01 | 50 % |
| K_off_0p3 | P1_seed1 | 10 | 1.11 | 40 % |
| K_off_0p3 | P2_seed1 | 10 | 0.88 | 70 % |
| K_off_0p3 | P12_seed1 | 10 | 0.92 | 60 % |
| K_off_0p3 | P1_seed2 | 10 | 1.05 | 40 % |
| K_off_0p3 | P2_seed2 | 10 | 0.90 | 70 % |
| K_off_0p3 | P12_seed2 | 10 | 0.88 | 70 % |
| K_off_0p1 | P3_oracle | 4 | 0.46 | 100 % |
| K_off_0p1 | P1_seed0 | 4 | 0.95 | 75 % |
| K_off_0p1 | P2_seed0 | 4 | 0.84 | 100 % |
| K_off_0p1 | P12_seed0 | 4 | 0.87 | 75 % |
| K_off_0p1 | P1_seed1 | 4 | 0.91 | 75 % |
| K_off_0p1 | P2_seed1 | 4 | 0.88 | 75 % |
| K_off_0p1 | P12_seed1 | 4 | 0.84 | 75 % |
| K_off_0p1 | P1_seed2 | 4 | 0.96 | 50 % |
| K_off_0p1 | P2_seed2 | 4 | 0.88 | 100 % |
| K_off_0p1 | P12_seed2 | 4 | 0.85 | 75 % |
| n10_inband | P3_oracle | 8 | 1.08 | 25 % |
| n10_inband | P1_seed0 | 8 | 1.84 | 25 % |
| n10_inband | P2_seed0 | 8 | 1.76 | 12 % |
| n10_inband | P12_seed0 | 8 | 1.79 | 25 % |
| n10_inband | P1_seed1 | 8 | 1.91 | 12 % |
| n10_inband | P2_seed1 | 8 | 1.70 | 12 % |
| n10_inband | P12_seed1 | 8 | 1.81 | 12 % |
| n10_inband | P1_seed2 | 8 | 1.94 | 12 % |
| n10_inband | P2_seed2 | 8 | 1.80 | 0 % |
| n10_inband | P12_seed2 | 8 | 1.87 | 25 % |
| n10_all | P3_oracle | 8 | 0.65 | 100 % |
| n10_all | P1_seed0 | 8 | 0.93 | 62 % |
| n10_all | P2_seed0 | 8 | 0.90 | 100 % |
| n10_all | P12_seed0 | 8 | 0.85 | 100 % |
| n10_all | P1_seed1 | 8 | 0.91 | 88 % |
| n10_all | P2_seed1 | 8 | 0.89 | 88 % |
| n10_all | P12_seed1 | 8 | 0.88 | 88 % |
| n10_all | P1_seed2 | 8 | 0.91 | 75 % |
| n10_all | P2_seed2 | 8 | 0.88 | 100 % |
| n10_all | P12_seed2 | 8 | 0.85 | 100 % |
