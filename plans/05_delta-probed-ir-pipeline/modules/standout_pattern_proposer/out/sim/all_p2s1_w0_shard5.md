# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 19:21

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.33 | 80 % |
| K_off_0p3 | P12_seed0 | 5 | 0.62 | 100 % |
| K_off_0p3 | P12_seed1 | 5 | 0.64 | 100 % |
| K_off_0p3 | P12_seed2 | 5 | 0.69 | 100 % |
| K_off_0p1 | P3_oracle | 1 | 0.21 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.63 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.84 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.63 | 100 % |
| n10_inband | P3_oracle | 3 | 1.42 | 33 % |
| n10_inband | P12_seed0 | 3 | 2.17 | 0 % |
| n10_inband | P12_seed1 | 3 | 2.42 | 0 % |
| n10_inband | P12_seed2 | 3 | 2.67 | 0 % |
| n10_all | P3_oracle | 3 | 0.38 | 100 % |
| n10_all | P12_seed0 | 3 | 0.59 | 100 % |
| n10_all | P12_seed1 | 3 | 0.66 | 100 % |
| n10_all | P12_seed2 | 3 | 0.62 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 3)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 3 | 0.54 | 67 % |
| K_off_0p3 | P12_seed0 | 3 | 0.77 | 67 % |
| K_off_0p3 | P12_seed1 | 3 | 1.08 | 33 % |
| K_off_0p3 | P12_seed2 | 3 | 0.85 | 67 % |
| K_off_0p1 | P3_oracle | 1 | 0.48 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.75 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.80 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.70 | 100 % |
| n10_inband | P3_oracle | 1 | 1.25 | 0 % |
| n10_inband | P12_seed0 | 1 | 2.33 | 0 % |
| n10_inband | P12_seed1 | 1 | 2.58 | 0 % |
| n10_inband | P12_seed2 | 1 | 2.25 | 0 % |
| n10_all | P3_oracle | 1 | 0.39 | 100 % |
| n10_all | P12_seed0 | 1 | 0.83 | 100 % |
| n10_all | P12_seed1 | 1 | 0.67 | 100 % |
| n10_all | P12_seed2 | 1 | 0.83 | 100 % |
