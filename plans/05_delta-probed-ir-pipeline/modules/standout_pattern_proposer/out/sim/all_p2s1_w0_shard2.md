# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 22:38

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.82 | 50 % |
| K_off_0p3 | P12_seed0 | 4 | 1.09 | 25 % |
| K_off_0p3 | P12_seed1 | 4 | 1.07 | 50 % |
| K_off_0p3 | P12_seed2 | 4 | 1.07 | 50 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 1 | 1.10 | 0 % |
| n10_inband | P12_seed0 | 1 | 0.96 | 100 % |
| n10_inband | P12_seed1 | 1 | 0.92 | 100 % |
| n10_inband | P12_seed2 | 1 | 1.00 | 0 % |
| n10_all | P3_oracle | 2 | 0.67 | 50 % |
| n10_all | P12_seed0 | 2 | 0.82 | 100 % |
| n10_all | P12_seed1 | 2 | 0.80 | 100 % |
| n10_all | P12_seed2 | 2 | 0.88 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.61 | 60 % |
| K_off_0p3 | P12_seed0 | 5 | 0.93 | 60 % |
| K_off_0p3 | P12_seed1 | 5 | 0.89 | 60 % |
| K_off_0p3 | P12_seed2 | 5 | 0.93 | 60 % |
| K_off_0p1 | P3_oracle | 1 | 0.45 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.96 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.75 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.62 | 100 % |
| n10_inband | P3_oracle | 2 | 0.98 | 50 % |
| n10_inband | P12_seed0 | 2 | 2.20 | 0 % |
| n10_inband | P12_seed1 | 2 | 2.48 | 0 % |
| n10_inband | P12_seed2 | 2 | 2.28 | 0 % |
| n10_all | P3_oracle | 2 | 0.41 | 100 % |
| n10_all | P12_seed0 | 2 | 0.75 | 100 % |
| n10_all | P12_seed1 | 2 | 0.78 | 100 % |
| n10_all | P12_seed2 | 2 | 0.72 | 100 % |
