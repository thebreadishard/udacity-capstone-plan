# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 22:34

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 3)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 3 | 0.19 | 100 % |
| K_off_0p3 | P12_seed0 | 3 | 0.53 | 67 % |
| K_off_0p3 | P12_seed1 | 3 | 0.69 | 67 % |
| K_off_0p3 | P12_seed2 | 3 | 0.65 | 67 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 1 | 0.36 | 100 % |
| n10_inband | P12_seed0 | 1 | 2.45 | 0 % |
| n10_inband | P12_seed1 | 1 | 2.18 | 0 % |
| n10_inband | P12_seed2 | 1 | 1.73 | 0 % |
| n10_all | P3_oracle | 1 | 0.09 | 100 % |
| n10_all | P12_seed0 | 1 | 0.62 | 100 % |
| n10_all | P12_seed1 | 1 | 0.67 | 100 % |
| n10_all | P12_seed2 | 1 | 0.62 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 4)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 4 | 0.42 | 100 % |
| K_off_0p3 | P12_seed0 | 4 | 0.68 | 75 % |
| K_off_0p3 | P12_seed1 | 4 | 0.60 | 75 % |
| K_off_0p3 | P12_seed2 | 4 | 0.76 | 75 % |
| K_off_0p1 | P3_oracle | 0 | — | — |
| K_off_0p1 | P12_seed0 | 0 | — | — |
| K_off_0p1 | P12_seed1 | 0 | — | — |
| K_off_0p1 | P12_seed2 | 0 | — | — |
| n10_inband | P3_oracle | 1 | 1.38 | 0 % |
| n10_inband | P12_seed0 | 1 | 1.38 | 0 % |
| n10_inband | P12_seed1 | 1 | 1.40 | 0 % |
| n10_inband | P12_seed2 | 1 | 1.40 | 0 % |
| n10_all | P3_oracle | 1 | 0.38 | 100 % |
| n10_all | P12_seed0 | 1 | 0.85 | 100 % |
| n10_all | P12_seed1 | 1 | 0.92 | 100 % |
| n10_all | P12_seed2 | 1 | 0.87 | 100 % |
