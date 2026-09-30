# Pattern-proposer simulation — pool all, merged 8 shards

seeds [0, 1, 2], 60 checkpoints per curve, λ [1e-06, 1e-05], noise σ 0.0; 97 evaluation molecules; 179.1 CPU-hours.

## eval_parents (n 41; P0 reaches ρ_off ≤ 0.3 on 35)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 35 | 0.33 | 91 % |
| K_off_0p3 | P12_seed0 | 35 | 0.68 | 77 % |
| K_off_0p3 | P12_seed1 | 35 | 0.69 | 80 % |
| K_off_0p3 | P12_seed2 | 35 | 0.69 | 80 % |
| K_off_0p1 | P3_oracle | 8 | 0.25 | 100 % |
| K_off_0p1 | P12_seed0 | 8 | 0.68 | 75 % |
| K_off_0p1 | P12_seed1 | 8 | 0.79 | 75 % |
| K_off_0p1 | P12_seed2 | 8 | 0.73 | 75 % |
| n10_inband | P3_oracle | 20 | 0.70 | 70 % |
| n10_inband | P12_seed0 | 20 | 1.83 | 20 % |
| n10_inband | P12_seed1 | 20 | 1.87 | 20 % |
| n10_inband | P12_seed2 | 20 | 2.04 | 15 % |
| n10_all | P3_oracle | 24 | 0.34 | 96 % |
| n10_all | P12_seed0 | 24 | 0.66 | 92 % |
| n10_all | P12_seed1 | 24 | 0.68 | 92 % |
| n10_all | P12_seed2 | 24 | 0.68 | 88 % |

## eval (n 56; P0 reaches ρ_off ≤ 0.3 on 35)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 35 | 0.50 | 77 % |
| K_off_0p3 | P12_seed0 | 35 | 0.88 | 66 % |
| K_off_0p3 | P12_seed1 | 35 | 0.89 | 57 % |
| K_off_0p3 | P12_seed2 | 35 | 0.92 | 57 % |
| K_off_0p1 | P3_oracle | 4 | 0.48 | 100 % |
| K_off_0p1 | P12_seed0 | 4 | 0.75 | 100 % |
| K_off_0p1 | P12_seed1 | 4 | 0.82 | 100 % |
| K_off_0p1 | P12_seed2 | 4 | 0.70 | 100 % |
| n10_inband | P3_oracle | 14 | 1.30 | 21 % |
| n10_inband | P12_seed0 | 14 | 2.35 | 0 % |
| n10_inband | P12_seed1 | 14 | 2.56 | 0 % |
| n10_inband | P12_seed2 | 14 | 2.33 | 0 % |
| n10_all | P3_oracle | 14 | 0.42 | 100 % |
| n10_all | P12_seed0 | 14 | 0.83 | 86 % |
| n10_all | P12_seed1 | 14 | 0.84 | 86 % |
| n10_all | P12_seed2 | 14 | 0.85 | 86 % |
