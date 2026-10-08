# Error map of the pattern-f hybrid records (2026-10-08 09:21)

1 records (largest size each: [750]), per-molecule errors averaged over seeds and records; pool of 750 molecules. Kind = aromatic rings, fusion, ring heteroatoms, substituent elements (rdkit on the manifest SMILES).

| kind | hold-out n (sets) | pool count | ring-coupling ratio | ω rms (cm⁻¹) | ΔH residual | worst molecules (ratio) |
|---|---|---|---|---|---|---|
| 4ar-fused|carbo|sub:CF | 2 (b) | 1 | 0.40 | 2.7 | 0.31 | fluoranthene+CF3 0.40, fluoranthene+CF3 0.39 |
| 4ar-fused|carbo|sub:CNO | 1 (b) | 0 | 0.39 | 3.5 | 0.31 | fluoranthene+CONH2 0.39 |
| 4ar-fused|carbo|sub:S | 1 (b) | 0 | 0.36 | 3.4 | 0.29 | fluoranthene+SH 0.36 |
| 4ar-fused|carbo|sub:N | 2 (b) | 0 | 0.36 | 2.8 | 0.27 | fluoranthene+NH2 0.38, fluoranthene+NH2 0.34 |
| 4ar-fused|carbo|sub:C | 6 (b) | 0 | 0.35 | 4.1 | 0.27 | fluoranthene+CH3 0.38, fluoranthene+CH3 0.38, fluoranthene+vinyl 0.36 |
| 4ar-fused|carbo|sub:CN | 3 (b) | 0 | 0.35 | 3.0 | 0.28 | fluoranthene+CN 0.36, fluoranthene+CN 0.36, fluoranthene+CN 0.33 |
| 2ar|carbo|sub:CO | 1 (a) | 2 | 0.34 | 3.0 | 0.19 | benzophenone 0.34 |
| 4ar-fused|carbo|sub:O | 1 (b) | 1 | 0.34 | 3.0 | 0.27 | fluoranthene+OH 0.34 |
| 4ar-fused|carbo|sub:CO | 2 (b) | 3 | 0.33 | 2.9 | 0.27 | fluoranthene+COOH 0.34, fluoranthene+OCH3 0.32 |
| 2ar-fused|carbo|sub:CN | 1 (b) | 24 | 0.33 | 3.2 | 0.22 | fluorene+CN 0.33 |
| 2ar-fused|carbo|sub:CNO | 1 (b) | 83 | 0.32 | 4.5 | 0.19 | fluorene+CONH2 0.32 |
| 4ar-fused|carbo|sub:Cl | 1 (b) | 0 | 0.30 | 2.9 | 0.25 | fluoranthene+Cl 0.30 |
| 4ar-fused|carbo|sub:none | 1 (a) | 1 | 0.30 | 3.0 | 0.23 | fluoranthene 0.30 |
| 2ar-fused|carbo|sub:C | 5 (b) | 25 | 0.28 | 3.7 | 0.17 | fluorene+ethynyl 0.31, fluorene+CH3 0.30, fluorene+CH3 0.28 |
| 2ar-fused|carbo|sub:N | 3 (b) | 1 | 0.28 | 3.1 | 0.17 | fluorene+NH2 0.32, fluorene+NH2 0.26, fluorene+NH2 0.26 |
| 2ar-fused|carbo|sub:F | 2 (b) | 2 | 0.27 | 2.9 | 0.17 | fluorene+F 0.28, fluorene+F 0.26 |
| 2ar-fused|carbo|sub:Cl | 3 (b) | 3 | 0.27 | 3.0 | 0.17 | fluorene+Cl 0.28, fluorene+Cl 0.27, fluorene+Cl 0.26 |
| 2ar-fused|carbo|sub:none | 1 (a) | 4 | 0.27 | 3.4 | 0.16 | fluorene 0.27 |
| 2ar-fused|carbo|sub:NO | 1 (b) | 4 | 0.27 | 4.0 | 0.18 | fluorene+NO2 0.27 |
| 2ar-fused|carbo|sub:CF | 1 (b) | 17 | 0.26 | 3.1 | 0.18 | fluorene+CF3 0.26 |
| 2ar-fused|carbo|sub:S | 1 (b) | 2 | 0.26 | 4.6 | 0.17 | fluorene+SH 0.26 |
| 2ar-fused|carbo|sub:CO | 3 (ab) | 85 | 0.24 | 2.4 | 0.15 | fluorene+COOH 0.32, fluorene+OCH3 0.31, 2-naphthoic_acid 0.11 |
| 2ar|carbo|sub:none | 1 (a) | 0 | 0.20 | 2.2 | 0.14 | biphenyl 0.20 |
| 3ar-fused|carbo|sub:none | 2 (a) | 1 | 0.16 | 2.1 | 0.12 | phenanthrene 0.16, biphenylene 0.15 |
| 3ar-fused|ring-N|sub:none | 1 (a) | 3 | 0.15 | 1.7 | 0.11 | phenanthridine 0.15 |
| 1ar|carbo|sub:CN | 1 (a) | 0 | 0.09 | 2.2 | 0.09 | benzonitrile 0.09 |
| 1ar|carbo|sub:none | 1 (a) | 0 | 0.07 | 2.1 | 0.04 | benzene 0.07 |

Median kind ratio 0.28; weak kinds (≥ median): 14; uncovered kinds (pool < 8): 22.
Next-pool candidates: 200 of 4210 pending rows of layers A2,B,C with ≤ 19 heavy atoms, by reason: weak+uncovered 19, weak 60, uncovered 36, new-kind 85 → `next_pool_candidates_2026-10-08.csv`.
