# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 19:49

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.22 | 100 % |
| K_off_0p3 | P12_seed0 | 5 | 0.74 | 100 % |
| K_off_0p3 | P12_seed1 | 5 | 0.79 | 100 % |
| K_off_0p3 | P12_seed2 | 5 | 0.74 | 100 % |
| K_off_0p1 | P3_oracle | 3 | 0.34 | 100 % |
| K_off_0p1 | P12_seed0 | 3 | 0.66 | 100 % |
| K_off_0p1 | P12_seed1 | 3 | 0.62 | 100 % |
| K_off_0p1 | P12_seed2 | 3 | 0.74 | 100 % |
| n10_inband | P3_oracle | 4 | 0.65 | 75 % |
| n10_inband | P12_seed0 | 4 | 1.62 | 0 % |
| n10_inband | P12_seed1 | 4 | 2.00 | 0 % |
| n10_inband | P12_seed2 | 4 | 2.08 | 0 % |
| n10_all | P3_oracle | 4 | 0.23 | 100 % |
| n10_all | P12_seed0 | 4 | 0.71 | 100 % |
| n10_all | P12_seed1 | 4 | 0.64 | 100 % |
| n10_all | P12_seed2 | 4 | 0.67 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.46 | 75 % |
| K_off_0p3 | P12_seed0 | 4 | 0.89 | 100 % |
| K_off_0p3 | P12_seed1 | 4 | 0.87 | 75 % |
| K_off_0p3 | P12_seed2 | 4 | 0.88 | 50 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 1 | 0.86 | 100 % |
| n10_inband | P12_seed0 | 1 | 1.48 | 0 % |
| n10_inband | P12_seed1 | 1 | 1.41 | 0 % |
| n10_inband | P12_seed2 | 1 | 1.48 | 0 % |
| n10_all | P3_oracle | 1 | 0.74 | 100 % |
| n10_all | P12_seed0 | 1 | 0.93 | 100 % |
| n10_all | P12_seed1 | 1 | 0.96 | 100 % |
| n10_all | P12_seed2 | 1 | 0.96 | 100 % |
