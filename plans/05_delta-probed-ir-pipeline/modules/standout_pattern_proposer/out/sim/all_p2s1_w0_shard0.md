# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 21:55

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 13 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 6; P0 reaches ρ_off ≤ 0.3 on 6)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 6 | 0.26 | 100 % |
| K_off_0p3 | P12_seed0 | 6 | 0.66 | 83 % |
| K_off_0p3 | P12_seed1 | 6 | 0.60 | 83 % |
| K_off_0p3 | P12_seed2 | 6 | 0.73 | 83 % |
| K_off_0p1 | P3_oracle | 1 | 0.10 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.70 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.76 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.72 | 100 % |
| n10_inband | P3_oracle | 3 | 0.58 | 67 % |
| n10_inband | P12_seed0 | 3 | 2.25 | 0 % |
| n10_inband | P12_seed1 | 3 | 1.90 | 0 % |
| n10_inband | P12_seed2 | 3 | 2.40 | 0 % |
| n10_all | P3_oracle | 5 | 0.43 | 100 % |
| n10_all | P12_seed0 | 5 | 0.66 | 100 % |
| n10_all | P12_seed1 | 5 | 0.76 | 100 % |
| n10_all | P12_seed2 | 5 | 0.70 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.41 | 75 % |
| K_off_0p3 | P12_seed0 | 4 | 0.70 | 75 % |
| K_off_0p3 | P12_seed1 | 4 | 0.78 | 75 % |
| K_off_0p3 | P12_seed2 | 4 | 0.87 | 50 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 2 | 1.38 | 50 % |
| n10_inband | P12_seed0 | 2 | 2.73 | 0 % |
| n10_inband | P12_seed1 | 2 | 2.70 | 0 % |
| n10_inband | P12_seed2 | 2 | 2.62 | 0 % |
| n10_all | P3_oracle | 1 | 0.43 | 100 % |
| n10_all | P12_seed0 | 1 | 0.62 | 100 % |
| n10_all | P12_seed1 | 1 | 0.66 | 100 % |
| n10_all | P12_seed2 | 1 | 0.59 | 100 % |
