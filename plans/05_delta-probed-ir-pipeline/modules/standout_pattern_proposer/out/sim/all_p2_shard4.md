# Pattern-proposer simulation — pool all, 2026-09-26 22:01

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.19 | 100 % |
| K_off_0p3 | P1_seed0 | 4 | 0.93 | 50 % |
| K_off_0p3 | P2_seed0 | 4 | 0.64 | 75 % |
| K_off_0p3 | P12_seed0 | 4 | 0.86 | 50 % |
| K_off_0p3 | P1_seed1 | 4 | 0.93 | 50 % |
| K_off_0p3 | P2_seed1 | 4 | 0.88 | 50 % |
| K_off_0p3 | P12_seed1 | 4 | 0.95 | 50 % |
| K_off_0p3 | P1_seed2 | 4 | 0.97 | 50 % |
| K_off_0p3 | P2_seed2 | 4 | 0.83 | 50 % |
| K_off_0p3 | P12_seed2 | 4 | 0.90 | 50 % |
| K_off_0p1 | P3_oracle | 2 | 0.69 | 100 % |
| K_off_0p1 | P1_seed0 | 2 | 0.84 | 100 % |
| K_off_0p1 | P2_seed0 | 2 | 0.71 | 100 % |
| K_off_0p1 | P12_seed0 | 2 | 0.77 | 100 % |
| K_off_0p1 | P1_seed1 | 2 | 0.83 | 100 % |
| K_off_0p1 | P2_seed1 | 2 | 0.78 | 100 % |
| K_off_0p1 | P12_seed1 | 2 | 0.72 | 100 % |
| K_off_0p1 | P1_seed2 | 2 | 0.89 | 50 % |
| K_off_0p1 | P2_seed2 | 2 | 0.81 | 100 % |
| K_off_0p1 | P12_seed2 | 2 | 0.79 | 100 % |
| n10_inband | P3_oracle | 4 | 0.73 | 75 % |
| n10_inband | P1_seed0 | 4 | 1.47 | 0 % |
| n10_inband | P2_seed0 | 4 | 1.54 | 0 % |
| n10_inband | P12_seed0 | 4 | 1.40 | 0 % |
| n10_inband | P1_seed1 | 4 | 1.59 | 0 % |
| n10_inband | P2_seed1 | 4 | 1.69 | 0 % |
| n10_inband | P12_seed1 | 4 | 1.54 | 0 % |
| n10_inband | P1_seed2 | 4 | 1.56 | 0 % |
| n10_inband | P2_seed2 | 4 | 1.49 | 0 % |
| n10_inband | P12_seed2 | 4 | 1.42 | 0 % |
| n10_all | P3_oracle | 4 | 0.35 | 100 % |
| n10_all | P1_seed0 | 4 | 0.98 | 50 % |
| n10_all | P2_seed0 | 4 | 0.88 | 75 % |
| n10_all | P12_seed0 | 4 | 0.87 | 75 % |
| n10_all | P1_seed1 | 4 | 0.98 | 50 % |
| n10_all | P2_seed1 | 4 | 0.93 | 75 % |
| n10_all | P12_seed1 | 4 | 0.91 | 50 % |
| n10_all | P1_seed2 | 4 | 1.01 | 25 % |
| n10_all | P2_seed2 | 4 | 0.88 | 75 % |
| n10_all | P12_seed2 | 4 | 0.88 | 75 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.54 | 100 % |
| K_off_0p3 | P1_seed0 | 4 | 1.02 | 50 % |
| K_off_0p3 | P2_seed0 | 4 | 1.19 | 50 % |
| K_off_0p3 | P12_seed0 | 4 | 0.96 | 50 % |
| K_off_0p3 | P1_seed1 | 4 | 0.99 | 50 % |
| K_off_0p3 | P2_seed1 | 4 | 0.93 | 50 % |
| K_off_0p3 | P12_seed1 | 4 | 0.89 | 50 % |
| K_off_0p3 | P1_seed2 | 4 | 0.97 | 50 % |
| K_off_0p3 | P2_seed2 | 4 | 0.84 | 50 % |
| K_off_0p3 | P12_seed2 | 4 | 0.89 | 50 % |
| K_off_0p1 | P3_oracle | 2 | 0.62 | 100 % |
| K_off_0p1 | P1_seed0 | 2 | 0.93 | 100 % |
| K_off_0p1 | P2_seed0 | 2 | 1.00 | 50 % |
| K_off_0p1 | P12_seed0 | 2 | 0.92 | 100 % |
| K_off_0p1 | P1_seed1 | 2 | 0.94 | 100 % |
| K_off_0p1 | P2_seed1 | 2 | 0.96 | 100 % |
| K_off_0p1 | P12_seed1 | 2 | 0.90 | 100 % |
| K_off_0p1 | P1_seed2 | 2 | 1.00 | 50 % |
| K_off_0p1 | P2_seed2 | 2 | 0.91 | 100 % |
| K_off_0p1 | P12_seed2 | 2 | 0.88 | 100 % |
| n10_inband | P3_oracle | 4 | 1.42 | 25 % |
| n10_inband | P1_seed0 | 4 | 2.36 | 25 % |
| n10_inband | P2_seed0 | 4 | 2.51 | 25 % |
| n10_inband | P12_seed0 | 4 | 2.16 | 25 % |
| n10_inband | P1_seed1 | 4 | 2.39 | 0 % |
| n10_inband | P2_seed1 | 4 | 2.53 | 0 % |
| n10_inband | P12_seed1 | 4 | 2.40 | 25 % |
| n10_inband | P1_seed2 | 4 | 2.49 | 0 % |
| n10_inband | P2_seed2 | 4 | 2.26 | 0 % |
| n10_inband | P12_seed2 | 4 | 2.24 | 25 % |
| n10_all | P3_oracle | 4 | 0.59 | 100 % |
| n10_all | P1_seed0 | 4 | 0.87 | 75 % |
| n10_all | P2_seed0 | 4 | 0.87 | 75 % |
| n10_all | P12_seed0 | 4 | 0.85 | 75 % |
| n10_all | P1_seed1 | 4 | 0.87 | 75 % |
| n10_all | P2_seed1 | 4 | 0.86 | 75 % |
| n10_all | P12_seed1 | 4 | 0.83 | 75 % |
| n10_all | P1_seed2 | 4 | 0.90 | 75 % |
| n10_all | P2_seed2 | 4 | 0.88 | 75 % |
| n10_all | P12_seed2 | 4 | 0.82 | 75 % |
