# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 12:07

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.22 | 100 % |
| K_off_0p3 | P12_seed0 | 5 | 0.68 | 100 % |
| K_off_0p3 | P12_seed1 | 5 | 0.58 | 100 % |
| K_off_0p3 | P12_seed2 | 5 | 0.54 | 100 % |
| K_off_0p1 | P3_oracle | 1 | 0.29 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.63 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.65 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.63 | 100 % |
| n10_inband | P3_oracle | 2 | 0.88 | 100 % |
| n10_inband | P12_seed0 | 2 | 1.24 | 50 % |
| n10_inband | P12_seed1 | 2 | 1.22 | 50 % |
| n10_inband | P12_seed2 | 2 | 1.12 | 50 % |
| n10_all | P3_oracle | 2 | 0.41 | 100 % |
| n10_all | P12_seed0 | 2 | 0.63 | 100 % |
| n10_all | P12_seed1 | 2 | 0.60 | 100 % |
| n10_all | P12_seed2 | 2 | 0.63 | 100 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 6)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 6 | 0.38 | 83 % |
| K_off_0p3 | P12_seed0 | 6 | 0.96 | 50 % |
| K_off_0p3 | P12_seed1 | 6 | 1.02 | 50 % |
| K_off_0p3 | P12_seed2 | 6 | 0.95 | 50 % |
| K_off_0p1 | P3_oracle | 1 | 0.51 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.76 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.84 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.70 | 100 % |
| n10_inband | P3_oracle | 3 | 1.33 | 0 % |
| n10_inband | P12_seed0 | 3 | 2.62 | 0 % |
| n10_inband | P12_seed1 | 3 | 2.38 | 0 % |
| n10_inband | P12_seed2 | 3 | 2.25 | 0 % |
| n10_all | P3_oracle | 4 | 0.43 | 100 % |
| n10_all | P12_seed0 | 4 | 0.85 | 50 % |
| n10_all | P12_seed1 | 4 | 0.83 | 50 % |
| n10_all | P12_seed2 | 4 | 0.83 | 50 % |
