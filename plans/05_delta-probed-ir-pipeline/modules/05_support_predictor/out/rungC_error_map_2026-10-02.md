# Error map of the pattern-f hybrid records (2026-10-02 06:54)

15 records (largest size each: [100, 175, 449, 750]), per-molecule errors averaged over seeds and records; pool of 750 molecules. Kind = aromatic rings, fusion, ring heteroatoms, substituent elements (rdkit on the manifest SMILES).

| kind | hold-out n (sets) | pool count | ring-coupling ratio | ω rms (cm⁻¹) | ΔH residual | worst molecules (ratio) |
|---|---|---|---|---|---|---|
| 4ar-fused|carbo|sub:CF | 2 (b) | 1 | 0.43 | 4.7 | 0.36 | fluoranthene+CF3 0.44, fluoranthene+CF3 0.43 |
| 4ar-fused|carbo|sub:CNO | 1 (b) | 0 | 0.42 | 4.8 | 0.33 | fluoranthene+CONH2 0.42 |
| 4ar-fused|carbo|sub:CN | 3 (b) | 0 | 0.40 | 4.9 | 0.32 | fluoranthene+CN 0.42, fluoranthene+CN 0.40, fluoranthene+CN 0.39 |
| 4ar-fused|carbo|sub:C | 6 (b) | 0 | 0.40 | 5.4 | 0.30 | fluoranthene+vinyl 0.43, fluoranthene+CH3 0.43, fluoranthene+CH3 0.42 |
| 4ar-fused|carbo|sub:S | 1 (b) | 0 | 0.40 | 5.0 | 0.32 | fluoranthene+SH 0.40 |
| 4ar-fused|carbo|sub:N | 2 (b) | 0 | 0.39 | 4.6 | 0.30 | fluoranthene+NH2 0.42, fluoranthene+NH2 0.37 |
| 4ar-fused|carbo|sub:CO | 2 (b) | 3 | 0.39 | 4.9 | 0.31 | fluoranthene+COOH 0.40, fluoranthene+OCH3 0.38 |
| 2ar-fused|carbo|sub:CNO | 1 (b) | 83 | 0.39 | 7.5 | 0.27 | fluorene+CONH2 0.39 |
| 4ar-fused|carbo|sub:O | 1 (b) | 1 | 0.38 | 5.2 | 0.31 | fluoranthene+OH 0.38 |
| 2ar|carbo|sub:CO | 1 (a) | 2 | 0.37 | 5.3 | 0.25 | benzophenone 0.37 |
| 2ar-fused|carbo|sub:CN | 1 (b) | 24 | 0.36 | 5.2 | 0.26 | fluorene+CN 0.36 |
| 4ar-fused|carbo|sub:Cl | 1 (b) | 0 | 0.34 | 4.0 | 0.27 | fluoranthene+Cl 0.34 |
| 4ar-fused|carbo|sub:none | 1 (a) | 1 | 0.34 | 4.0 | 0.26 | fluoranthene 0.34 |
| 2ar-fused|carbo|sub:N | 3 (b) | 1 | 0.33 | 4.9 | 0.22 | fluorene+NH2 0.37, fluorene+NH2 0.32, fluorene+NH2 0.30 |
| 2ar-fused|carbo|sub:NO | 1 (b) | 4 | 0.33 | 5.9 | 0.24 | fluorene+NO2 0.33 |
| 2ar-fused|carbo|sub:C | 5 (b) | 25 | 0.32 | 5.4 | 0.22 | fluorene+CH3 0.37, fluorene+ethynyl 0.32, fluorene+vinyl 0.32 |
| 2ar-fused|carbo|sub:CO | 3 (ab) | 85 | 0.32 | 5.2 | 0.22 | fluorene+COOH 0.37, fluorene+OCH3 0.36, 2-naphthoic_acid 0.22 |
| 2ar-fused|carbo|sub:Cl | 3 (b) | 3 | 0.32 | 4.9 | 0.22 | fluorene+Cl 0.33, fluorene+Cl 0.32, fluorene+Cl 0.30 |
| 2ar-fused|carbo|sub:CF | 1 (b) | 17 | 0.30 | 4.7 | 0.23 | fluorene+CF3 0.30 |
| 2ar-fused|carbo|sub:F | 2 (b) | 2 | 0.29 | 4.3 | 0.20 | fluorene+F 0.30, fluorene+F 0.28 |
| 2ar-fused|carbo|sub:S | 1 (b) | 2 | 0.28 | 6.3 | 0.20 | fluorene+SH 0.28 |
| 2ar-fused|carbo|sub:none | 1 (a) | 4 | 0.28 | 4.4 | 0.19 | fluorene 0.28 |
| 2ar|carbo|sub:none | 1 (a) | 0 | 0.24 | 4.1 | 0.16 | biphenyl 0.24 |
| 3ar-fused|ring-N|sub:none | 1 (a) | 3 | 0.20 | 3.1 | 0.15 | phenanthridine 0.20 |
| 3ar-fused|carbo|sub:none | 2 (a) | 1 | 0.20 | 4.9 | 0.19 | phenanthrene 0.21, biphenylene 0.18 |
| 1ar|carbo|sub:CN | 1 (a) | 0 | 0.14 | 3.9 | 0.14 | benzonitrile 0.14 |
| 1ar|carbo|sub:none | 1 (a) | 0 | 0.11 | 4.7 | 0.13 | benzene 0.11 |

Median kind ratio 0.33; weak kinds (≥ median): 14; uncovered kinds (pool < 8): 22.
Next-pool candidates: 200 of 4410 pending rows of layers A2,B,C with ≤ 19 heavy atoms, by reason: weak+uncovered 68, weak 60, uncovered 40, new-kind 32 → `next_pool_candidates_2026-10-02.csv`.
