# Pattern-proposer simulation — pool band, merged 3 shards

seeds [0, 1, 2], 60 checkpoints per curve, λ [1e-06, 1e-05], noise σ 0.0; 97 evaluation molecules; 19.6 CPU-hours.

## eval_parents (n 41; P0 reaches ρ_off ≤ 0.3 on 1)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 1 | 0.09 | 100 % |
| K_off_0p3 | P1_seed0 | 1 | 1.00 | 0 % |
| K_off_0p3 | P2_seed0 | 1 | 1.03 | 0 % |
| K_off_0p3 | P12_seed0 | 1 | 1.02 | 0 % |
| K_off_0p3 | P1_seed1 | 1 | 0.96 | 100 % |
| K_off_0p3 | P2_seed1 | 1 | 1.03 | 0 % |
| K_off_0p3 | P12_seed1 | 1 | 0.98 | 100 % |
| K_off_0p3 | P1_seed2 | 1 | 0.98 | 100 % |
| K_off_0p3 | P2_seed2 | 1 | 1.02 | 0 % |
| K_off_0p3 | P12_seed2 | 1 | 1.02 | 0 % |
| K_off_0p3 | P1A_seed0 | 1 | 0.98 | 100 % |
| K_off_0p3 | P2A_seed0 | 1 | 0.98 | 100 % |
| K_off_0p3 | P1A_seed1 | 1 | 0.34 | 100 % |
| K_off_0p3 | P2A_seed1 | 1 | 0.96 | 100 % |
| K_off_0p3 | P1A_seed2 | 1 | 0.96 | 100 % |
| K_off_0p3 | P2A_seed2 | 1 | 0.57 | 100 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P1_seed0 | 0 | — | — |
| K_off_0p1 | P2_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P1_seed1 | 0 | — | — |
| K_off_0p1 | P2_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P1_seed2 | 0 | — | — |
| K_off_0p1 | P2_seed2 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| K_off_0p1 | P1A_seed0 | 0 | — | — |
| K_off_0p1 | P2A_seed0 | 0 | — | — |
| K_off_0p1 | P1A_seed1 | 0 | — | — |
| K_off_0p1 | P2A_seed1 | 0 | — | — |
| K_off_0p1 | P1A_seed2 | 0 | — | — |
| K_off_0p1 | P2A_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 6 | 1.04 | 17 % |
| n10_inband | P1_seed0 | 6 | 1.03 | 17 % |
| n10_inband | P2_seed0 | 6 | 1.03 | 17 % |
| n10_inband | P12_seed0 | 6 | 1.02 | 17 % |
| n10_inband | P1_seed1 | 6 | 1.03 | 17 % |
| n10_inband | P2_seed1 | 6 | 1.04 | 17 % |
| n10_inband | P12_seed1 | 6 | 1.03 | 0 % |
| n10_inband | P1_seed2 | 6 | 1.03 | 0 % |
| n10_inband | P2_seed2 | 6 | 1.03 | 17 % |
| n10_inband | P12_seed2 | 6 | 1.03 | 17 % |
| n10_inband | P1A_seed0 | 5 | 1.02 | 20 % |
| n10_inband | P2A_seed0 | 5 | 1.00 | 40 % |
| n10_inband | P1A_seed1 | 5 | 1.04 | 40 % |
| n10_inband | P2A_seed1 | 5 | 1.02 | 40 % |
| n10_inband | P1A_seed2 | 5 | 1.02 | 40 % |
| n10_inband | P2A_seed2 | 6 | 1.00 | 50 % |
| n10_all | P3_oracle | 0 | — | — |
| n10_all | P1_seed0 | 0 | — | — |
| n10_all | P2_seed0 | 0 | — | — |
| n10_all | P12_seed0 | 0 | — | — |
| n10_all | P1_seed1 | 0 | — | — |
| n10_all | P2_seed1 | 0 | — | — |
| n10_all | P12_seed1 | 0 | — | — |
| n10_all | P1_seed2 | 0 | — | — |
| n10_all | P2_seed2 | 0 | — | — |
| n10_all | P12_seed2 | 0 | — | — |
| n10_all | P1A_seed0 | 0 | — | — |
| n10_all | P2A_seed0 | 0 | — | — |
| n10_all | P1A_seed1 | 0 | — | — |
| n10_all | P2A_seed1 | 0 | — | — |
| n10_all | P1A_seed2 | 0 | — | — |
| n10_all | P2A_seed2 | 0 | — | — |

## eval (n 56; P0 reaches ρ_off ≤ 0.3 on 3)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 3 | 0.89 | 100 % |
| K_off_0p3 | P1_seed0 | 3 | 0.98 | 67 % |
| K_off_0p3 | P2_seed0 | 3 | 1.00 | 33 % |
| K_off_0p3 | P12_seed0 | 3 | 1.00 | 33 % |
| K_off_0p3 | P1_seed1 | 3 | 0.98 | 67 % |
| K_off_0p3 | P2_seed1 | 2 | 0.96 | 100 % |
| K_off_0p3 | P12_seed1 | 3 | 0.98 | 67 % |
| K_off_0p3 | P1_seed2 | 3 | 1.00 | 33 % |
| K_off_0p3 | P2_seed2 | 2 | 0.98 | 50 % |
| K_off_0p3 | P12_seed2 | 3 | 0.98 | 67 % |
| K_off_0p3 | P1A_seed0 | 2 | 0.69 | 100 % |
| K_off_0p3 | P2A_seed0 | 3 | 0.98 | 100 % |
| K_off_0p3 | P1A_seed1 | 3 | 0.97 | 100 % |
| K_off_0p3 | P2A_seed1 | 2 | 0.82 | 100 % |
| K_off_0p3 | P1A_seed2 | 3 | 0.97 | 67 % |
| K_off_0p3 | P2A_seed2 | 2 | 0.89 | 100 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P1_seed0 | 0 | — | — |
| K_off_0p1 | P2_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P1_seed1 | 0 | — | — |
| K_off_0p1 | P2_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P1_seed2 | 0 | — | — |
| K_off_0p1 | P2_seed2 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| K_off_0p1 | P1A_seed0 | 0 | — | — |
| K_off_0p1 | P2A_seed0 | 0 | — | — |
| K_off_0p1 | P1A_seed1 | 0 | — | — |
| K_off_0p1 | P2A_seed1 | 0 | — | — |
| K_off_0p1 | P1A_seed2 | 0 | — | — |
| K_off_0p1 | P2A_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 8 | 1.02 | 12 % |
| n10_inband | P1_seed0 | 8 | 1.03 | 12 % |
| n10_inband | P2_seed0 | 8 | 1.01 | 25 % |
| n10_inband | P12_seed0 | 8 | 1.02 | 0 % |
| n10_inband | P1_seed1 | 8 | 1.02 | 0 % |
| n10_inband | P2_seed1 | 8 | 1.03 | 0 % |
| n10_inband | P12_seed1 | 8 | 1.03 | 12 % |
| n10_inband | P1_seed2 | 8 | 1.03 | 0 % |
| n10_inband | P2_seed2 | 8 | 1.02 | 0 % |
| n10_inband | P12_seed2 | 8 | 1.01 | 12 % |
| n10_inband | P1A_seed0 | 8 | 0.99 | 50 % |
| n10_inband | P2A_seed0 | 8 | 1.01 | 38 % |
| n10_inband | P1A_seed1 | 8 | 1.00 | 38 % |
| n10_inband | P2A_seed1 | 8 | 1.00 | 25 % |
| n10_inband | P1A_seed2 | 8 | 1.01 | 25 % |
| n10_inband | P2A_seed2 | 8 | 1.01 | 38 % |
| n10_all | P3_oracle | 0 | — | — |
| n10_all | P1_seed0 | 0 | — | — |
| n10_all | P2_seed0 | 0 | — | — |
| n10_all | P12_seed0 | 0 | — | — |
| n10_all | P1_seed1 | 0 | — | — |
| n10_all | P2_seed1 | 0 | — | — |
| n10_all | P12_seed1 | 0 | — | — |
| n10_all | P1_seed2 | 0 | — | — |
| n10_all | P2_seed2 | 0 | — | — |
| n10_all | P12_seed2 | 0 | — | — |
| n10_all | P1A_seed0 | 0 | — | — |
| n10_all | P2A_seed0 | 0 | — | — |
| n10_all | P1A_seed1 | 0 | — | — |
| n10_all | P2A_seed1 | 0 | — | — |
| n10_all | P1A_seed2 | 0 | — | — |
| n10_all | P2A_seed2 | 0 | — | — |
