# Sparse-probe count under the locality prior — 244 corpus molecules (2026-09-24)

m_d = free entries of ΔF on pattern (d) (bond-graph primitives: bonds, angles, dihedrals — an over-count of the non-redundant set, so p is an upper bound); p_d = ceil(m_d / 3N) probes by count; saving = 3N / p_d against plain finite differences (3N probes).

| size class (N atoms) | molecules | m_d / ΔH entries (median) | p_d (median, range) | 3N (median) | saving 3N / p_d (median, range) | bonds+angles only: p_d, saving (median) |
|---|---|---|---|---|---|---|
| 10–15 | 5 | 2.05 | 40 (38–55) | 42 | 0.9 (0.8–1.1) | 11, 3.3 |
| 16–20 | 26 | 2.08 | 54 (43–79) | 52 | 0.9 (0.8–1.1) | 14, 3.7 |
| 21–25 | 129 | 2.01 | 71 (47–92) | 69 | 1.0 (0.7–1.5) | 16, 4.3 |
| 26–30 | 84 | 1.87 | 76 (54–91) | 81 | 1.1 (0.9–1.4) | 17, 4.9 |

Linear fits over the 244 molecules: m_d ≈ 351.7 N − 3169; saving ≈ 0.011 N + 0.72.
Extrapolation by the fits (count only): N = 50 → saving 1.3; N = 100 → 1.9; N = 200 → 3.0.
Bonds + angles only (lower bound of the primitive set): saving ≈ 0.112 N + 1.76; N = 50 → 7.4; N = 100 → 13.0; N = 200 → 24.2.

Named molecules:

| molecule | N | 3N | primitives (with / without dihedrals) | m_c | m_d | p_c | p_d | saving_d | p_d, saving without dihedrals |
|---|---|---|---|---|---|---|---|---|---|
| carbazole+SH | 23 | 69 | 127 / 65 | 3196 | 5178 | 47 | 76 | 0.9 | 16, 4.3 |
| carbazole+SH | 23 | 69 | 127 / 65 | 3184 | 5144 | 47 | 75 | 0.9 | 16, 4.3 |
| carbazole+SH | 23 | 69 | 127 / 65 | 3198 | 5188 | 47 | 76 | 0.9 | 16, 4.3 |
| carbazole+SH | 23 | 69 | 127 / 65 | 3184 | 5146 | 47 | 75 | 0.9 | 16, 4.3 |
| biphenylene+CH3 | 23 | 69 | 129 / 67 | 3306 | 5234 | 48 | 76 | 0.9 | 17, 4.1 |
| naphthalene | 18 | 54 | 93 / 49 | 2101 | 3282 | 39 | 61 | 0.9 | 15, 3.6 |
| 1-naphthol | 19 | 57 | 97 / 51 | 2216 | 3497 | 39 | 62 | 0.9 | 15, 3.8 |
| phenanthrene | 24 | 72 | 132 / 68 | 3260 | 5363 | 46 | 75 | 1.0 | 17, 4.2 |
| benzene | 12 | 36 | 54 / 30 | 978 | 1365 | 28 | 38 | 0.9 | 11, 3.3 |
| anthracene | 24 | 72 | 132 / 68 | 3232 | 5271 | 45 | 74 | 1.0 | 16, 4.5 |
| 2-phenylpyridine | 21 | 63 | 104 / 56 | 2167 | 3326 | 35 | 53 | 1.2 | 14, 4.5 |
| pyrene | 26 | 78 | 153 / 77 | 4103 | 7014 | 53 | 90 | 0.9 | 19, 4.1 |
