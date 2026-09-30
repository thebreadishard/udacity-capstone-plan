# Pattern-proposer simulation — pool all, solver prior w 0 cm⁻¹, 2026-09-29 22:58

seeds [0, 1, 2], 60 checkpoints per curve, λ (1e-06, 1e-05), noise σ 0.0; 12 evaluation molecules; orderings P12,P3_oracle.

## eval_parents (n 5; P0 reaches ρ_off ≤ 0.3 on 3)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 3 | 0.31 | 100 % |
| K_off_0p3 | P12_seed0 | 3 | 0.52 | 100 % |
| K_off_0p3 | P12_seed1 | 3 | 0.62 | 100 % |
| K_off_0p3 | P12_seed2 | 3 | 0.72 | 100 % |
| K_off_0p1 | P3_oracle | 1 | 0.18 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 1.00 | 0 % |
| K_off_0p1 | P12_seed1 | 1 | 1.14 | 0 % |
| K_off_0p1 | P12_seed2 | 1 | 1.18 | 0 % |
| n10_inband | P3_oracle | 3 | 0.67 | 100 % |
| n10_inband | P12_seed0 | 3 | 1.10 | 33 % |
| n10_inband | P12_seed1 | 3 | 1.24 | 33 % |
| n10_inband | P12_seed2 | 3 | 1.10 | 33 % |
| n10_all | P3_oracle | 3 | 0.40 | 100 % |
| n10_all | P12_seed0 | 3 | 0.85 | 67 % |
| n10_all | P12_seed1 | 3 | 0.87 | 67 % |
| n10_all | P12_seed2 | 3 | 1.00 | 33 % |

## eval (n 7; P0 reaches ρ_off ≤ 0.3 on 5)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 5 | 0.67 | 80 % |
| K_off_0p3 | P12_seed0 | 5 | 0.89 | 60 % |
| K_off_0p3 | P12_seed1 | 5 | 0.98 | 60 % |
| K_off_0p3 | P12_seed2 | 5 | 0.93 | 60 % |
| K_off_0p1 | P3_oracle | 1 | 0.49 | 100 % |
| K_off_0p1 | P12_seed0 | 1 | 0.74 | 100 % |
| K_off_0p1 | P12_seed1 | 1 | 0.92 | 100 % |
| K_off_0p1 | P12_seed2 | 1 | 0.79 | 100 % |
| n10_inband | P3_oracle | 3 | 1.45 | 0 % |
| n10_inband | P12_seed0 | 3 | 2.36 | 0 % |
| n10_inband | P12_seed1 | 3 | 2.64 | 0 % |
| n10_inband | P12_seed2 | 3 | 2.82 | 0 % |
| n10_all | P3_oracle | 3 | 0.63 | 100 % |
| n10_all | P12_seed0 | 3 | 0.83 | 100 % |
| n10_all | P12_seed1 | 3 | 0.83 | 100 % |
| n10_all | P12_seed2 | 3 | 0.87 | 100 % |
