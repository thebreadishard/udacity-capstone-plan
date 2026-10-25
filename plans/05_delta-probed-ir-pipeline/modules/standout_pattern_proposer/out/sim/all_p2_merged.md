# Pattern-proposer simulation — pool all, merged 8 shards

seeds [0, 1, 2], 60 checkpoints per curve, λ [1e-06, 1e-05], noise σ 0.0; 97 evaluation molecules; 68.6 CPU-hours.

## eval_parents (n 41; P0 reaches ρ_off ≤ 0.3 on 38)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 38 | 0.25 | 97 % |
| K_off_0p3 | P1_seed0 | 38 | 0.76 | 71 % |
| K_off_0p3 | P2_seed0 | 38 | 0.70 | 71 % |
| K_off_0p3 | P12_seed0 | 38 | 0.70 | 79 % |
| K_off_0p3 | P1_seed1 | 38 | 0.78 | 66 % |
| K_off_0p3 | P2_seed1 | 38 | 0.80 | 66 % |
| K_off_0p3 | P12_seed1 | 38 | 0.71 | 76 % |
| K_off_0p3 | P1_seed2 | 38 | 0.77 | 74 % |
| K_off_0p3 | P2_seed2 | 38 | 0.74 | 74 % |
| K_off_0p3 | P12_seed2 | 38 | 0.73 | 82 % |
| K_off_0p1 | P3_oracle | 25 | 0.46 | 88 % |
| K_off_0p1 | P1_seed0 | 25 | 0.90 | 76 % |
| K_off_0p1 | P2_seed0 | 25 | 0.86 | 76 % |
| K_off_0p1 | P12_seed0 | 25 | 0.81 | 76 % |
| K_off_0p1 | P1_seed1 | 25 | 0.86 | 80 % |
| K_off_0p1 | P2_seed1 | 25 | 0.84 | 76 % |
| K_off_0p1 | P12_seed1 | 25 | 0.82 | 88 % |
| K_off_0p1 | P1_seed2 | 25 | 0.84 | 68 % |
| K_off_0p1 | P2_seed2 | 25 | 0.86 | 72 % |
| K_off_0p1 | P12_seed2 | 25 | 0.82 | 76 % |
| n10_inband | P3_oracle | 35 | 0.80 | 63 % |
| n10_inband | P1_seed0 | 35 | 1.43 | 20 % |
| n10_inband | P2_seed0 | 35 | 1.49 | 17 % |
| n10_inband | P12_seed0 | 35 | 1.38 | 20 % |
| n10_inband | P1_seed1 | 35 | 1.52 | 17 % |
| n10_inband | P2_seed1 | 35 | 1.48 | 20 % |
| n10_inband | P12_seed1 | 35 | 1.38 | 23 % |
| n10_inband | P1_seed2 | 35 | 1.50 | 17 % |
| n10_inband | P2_seed2 | 35 | 1.33 | 23 % |
| n10_inband | P12_seed2 | 35 | 1.37 | 23 % |
| n10_all | P3_oracle | 36 | 0.43 | 97 % |
| n10_all | P1_seed0 | 36 | 0.81 | 81 % |
| n10_all | P2_seed0 | 36 | 0.81 | 92 % |
| n10_all | P12_seed0 | 36 | 0.79 | 86 % |
| n10_all | P1_seed1 | 36 | 0.82 | 78 % |
| n10_all | P2_seed1 | 36 | 0.85 | 86 % |
| n10_all | P12_seed1 | 36 | 0.79 | 83 % |
| n10_all | P1_seed2 | 36 | 0.84 | 81 % |
| n10_all | P2_seed2 | 36 | 0.81 | 89 % |
| n10_all | P12_seed2 | 36 | 0.77 | 86 % |

## eval (n 56; P0 reaches ρ_off ≤ 0.3 on 43)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 43 | 0.38 | 95 % |
| K_off_0p3 | P1_seed0 | 43 | 0.80 | 63 % |
| K_off_0p3 | P2_seed0 | 43 | 0.79 | 65 % |
| K_off_0p3 | P12_seed0 | 43 | 0.76 | 74 % |
| K_off_0p3 | P1_seed1 | 43 | 0.88 | 53 % |
| K_off_0p3 | P2_seed1 | 43 | 0.84 | 70 % |
| K_off_0p3 | P12_seed1 | 43 | 0.76 | 63 % |
| K_off_0p3 | P1_seed2 | 43 | 0.83 | 58 % |
| K_off_0p3 | P2_seed2 | 43 | 0.71 | 67 % |
| K_off_0p3 | P12_seed2 | 43 | 0.65 | 67 % |
| K_off_0p1 | P3_oracle | 18 | 0.52 | 100 % |
| K_off_0p1 | P1_seed0 | 18 | 0.93 | 72 % |
| K_off_0p1 | P2_seed0 | 18 | 0.89 | 78 % |
| K_off_0p1 | P12_seed0 | 18 | 0.85 | 72 % |
| K_off_0p1 | P1_seed1 | 18 | 0.90 | 61 % |
| K_off_0p1 | P2_seed1 | 18 | 0.89 | 78 % |
| K_off_0p1 | P12_seed1 | 18 | 0.88 | 78 % |
| K_off_0p1 | P1_seed2 | 18 | 0.94 | 72 % |
| K_off_0p1 | P2_seed2 | 18 | 0.89 | 83 % |
| K_off_0p1 | P12_seed2 | 18 | 0.83 | 78 % |
| n10_inband | P3_oracle | 35 | 1.08 | 40 % |
| n10_inband | P1_seed0 | 35 | 1.72 | 11 % |
| n10_inband | P2_seed0 | 35 | 1.52 | 11 % |
| n10_inband | P12_seed0 | 35 | 1.52 | 11 % |
| n10_inband | P1_seed1 | 35 | 1.69 | 9 % |
| n10_inband | P2_seed1 | 35 | 1.46 | 9 % |
| n10_inband | P12_seed1 | 35 | 1.51 | 11 % |
| n10_inband | P1_seed2 | 35 | 1.60 | 11 % |
| n10_inband | P2_seed2 | 35 | 1.38 | 14 % |
| n10_inband | P12_seed2 | 35 | 1.44 | 14 % |
| n10_all | P3_oracle | 32 | 0.57 | 100 % |
| n10_all | P1_seed0 | 32 | 0.94 | 72 % |
| n10_all | P2_seed0 | 32 | 0.91 | 84 % |
| n10_all | P12_seed0 | 32 | 0.89 | 94 % |
| n10_all | P1_seed1 | 32 | 0.94 | 75 % |
| n10_all | P2_seed1 | 32 | 0.89 | 91 % |
| n10_all | P12_seed1 | 32 | 0.87 | 94 % |
| n10_all | P1_seed2 | 32 | 0.92 | 69 % |
| n10_all | P2_seed2 | 32 | 0.88 | 88 % |
| n10_all | P12_seed2 | 32 | 0.83 | 94 % |
