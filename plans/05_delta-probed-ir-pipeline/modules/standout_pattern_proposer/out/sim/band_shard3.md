# Pattern-proposer simulation — pool band, 2026-09-26 10:07

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 1)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 1 | 0.09 | 100 % |
| K_off_0p3 | P1_seed0 | 1 | 1.00 | 0 % |
| K_off_0p3 | P1_seed1 | 1 | 0.96 | 100 % |
| K_off_0p3 | P1_seed2 | 1 | 0.98 | 100 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P1_seed0 | 0 | — | — |
| K_off_0p1 | P1_seed1 | 0 | — | — |
| K_off_0p1 | P1_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 1 | 0.98 | 100 % |
| n10_inband | P1_seed0 | 1 | 1.01 | 0 % |
| n10_inband | P1_seed1 | 1 | 0.98 | 100 % |
| n10_inband | P1_seed2 | 1 | 1.01 | 0 % |
| n10_all | P3_oracle | 0 | — | — |
| n10_all | P1_seed0 | 0 | — | — |
| n10_all | P1_seed1 | 0 | — | — |
| n10_all | P1_seed2 | 0 | — | — |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 0)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 0 | — | — |
| K_off_0p3 | P1_seed0 | 0 | — | — |
| K_off_0p3 | P1_seed1 | 0 | — | — |
| K_off_0p3 | P1_seed2 | 0 | — | — |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P1_seed0 | 0 | — | — |
| K_off_0p1 | P1_seed1 | 0 | — | — |
| K_off_0p1 | P1_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 0 | — | — |
| n10_inband | P1_seed0 | 0 | — | — |
| n10_inband | P1_seed1 | 0 | — | — |
| n10_inband | P1_seed2 | 0 | — | — |
| n10_all | P3_oracle | 0 | — | — |
| n10_all | P1_seed0 | 0 | — | — |
| n10_all | P1_seed1 | 0 | — | — |
| n10_all | P1_seed2 | 0 | — | — |
