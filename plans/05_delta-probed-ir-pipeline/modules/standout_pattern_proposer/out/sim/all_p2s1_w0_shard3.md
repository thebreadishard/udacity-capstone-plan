# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 21:20

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.45 | 100 % |
| K_off_0p3 | P12_seed0 | 4 | 1.14 | 25 % |
| K_off_0p3 | P12_seed1 | 4 | 1.21 | 25 % |
| K_off_0p3 | P12_seed2 | 4 | 1.28 | 25 % |
| K_off_0p1 | P3_oracle | 1 | 0.34 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 1.14 | 0 % |
| K_off_0p1 | P12_seed1 | 1 | 1.14 | 0 % |
| K_off_0p1 | P12_seed2 | 1 | 1.24 | 0 % |
| n10_inband | P3_oracle | 3 | 0.62 | 67 % |
| n10_inband | P12_seed0 | 3 | 1.21 | 33 % |
| n10_inband | P12_seed1 | 3 | 1.47 | 33 % |
| n10_inband | P12_seed2 | 3 | 1.37 | 33 % |
| n10_all | P3_oracle | 4 | 0.35 | 100 % |
| n10_all | P12_seed0 | 4 | 0.76 | 75 % |
| n10_all | P12_seed1 | 4 | 0.73 | 75 % |
| n10_all | P12_seed2 | 4 | 0.75 | 75 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.64 | 75 % |
| K_off_0p3 | P12_seed0 | 4 | 0.97 | 50 % |
| K_off_0p3 | P12_seed1 | 4 | 1.11 | 25 % |
| K_off_0p3 | P12_seed2 | 4 | 1.09 | 50 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 1 | 1.33 | 0 % |
| n10_inband | P12_seed0 | 1 | 3.00 | 0 % |
| n10_inband | P12_seed1 | 1 | 3.00 | 0 % |
| n10_inband | P12_seed2 | 1 | 3.50 | 0 % |
| n10_all | P3_oracle | 1 | 0.53 | 100 % |
| n10_all | P12_seed0 | 1 | 0.85 | 100 % |
| n10_all | P12_seed1 | 1 | 0.85 | 100 % |
| n10_all | P12_seed2 | 1 | 0.89 | 100 % |
