# Gate and niche test on `proposals_2026-10-04.csv` — 2026-10-04 13:26

30000 samples, 28309 distinct canonical SMILES. Manifest: 5318 molecules, 37 known fused aromatic ring systems (incl. the listed cores); PubChem set: 160972 molecules.

| stage (first failed) | distinct SMILES |
|---|---|
| parses | 3947 |
| neutral_closed_shell | 3 |
| elements | 0 |
| heavy_le_30 | 912 |
| fused_aromatic_2plus | 290 |
| not_in_manifest | 177 |
| new_ring_system | 15967 |
| **pass** | **7013** |

**New ring systems:** 881 distinct, of which 216 are themselves molecules of the PubChem set; 846 of the 7013 passing molecules are in the PubChem set.

| class | passing molecules | new ring systems |
|---|---|---|
| r2 N | 162 | 90 |
| r2 O | 3 | 5 |
| r2 mixed | 495 | 25 |
| r2 none | 1 | 4 |
| r3 N | 1166 | 243 |
| r3 O | 86 | 25 |
| r3 S | 7 | 8 |
| r3 mixed | 1788 | 95 |
| r3 none | 15 | 13 |
| r4+ N | 1358 | 198 |
| r4+ O | 94 | 27 |
| r4+ S | 17 | 14 |
| r4+ mixed | 1474 | 47 |
| r4+ none | 347 | 85 |

Frozen list `proposals_2026-10-04_gated.csv`, SHA-256 `69f25509e1c4e5a630672cb15bac1a200a31914e82cecc49f31ae41b21c3962b`.