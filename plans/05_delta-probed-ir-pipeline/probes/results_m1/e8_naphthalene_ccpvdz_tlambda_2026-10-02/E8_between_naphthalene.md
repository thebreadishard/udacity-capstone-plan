# E8 between-branch — pattern extension and least-squares ceilings, cc-pvdz (2026-10-02 02:43)

Internals: 93 (19 bonds). mask = minimum-norm ΔF zeroed outside the pattern; fit = least-squares ΔF on the pattern.

| pattern | correction | read | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|---|
| (c) control (2125 pairs) | CC − B3LYP | mask | 0.12 | 0.69 | 7.12 | 6.90 (51.05) |
| (c) control (2125 pairs) | CC − B3LYP | fit | 0.01 | 0.05 | 0.41 | 1.09 (51.05) |
| (c) control (2125 pairs) | proxy ωB97X − B3LYP | mask | 0.35 | 0.52 | 7.13 | 4.27 (21.30) |
| (c) control (2125 pairs) | proxy ωB97X − B3LYP | fit | 0.11 | 0.14 | 1.80 | 1.97 (21.30) |
| (d) (c) + pairs two bonds apart (3297 pairs) | CC − B3LYP | mask | 0.07 | 0.45 | 3.96 | 2.81 (51.05) |
| (d) (c) + pairs two bonds apart (3297 pairs) | CC − B3LYP | fit | 0.00 | 0.01 | 0.34 | 0.36 (51.05) |
| (d) (c) + pairs two bonds apart (3297 pairs) | proxy ωB97X − B3LYP | mask | 0.30 | 0.42 | 6.43 | 3.68 (21.30) |
| (d) (c) + pairs two bonds apart (3297 pairs) | proxy ωB97X − B3LYP | fit | 0.04 | 0.08 | 0.95 | 1.10 (21.30) |
| (e) all pairs inside a ring (2143 pairs) | CC − B3LYP | mask | 0.12 | 0.68 | 7.15 | 6.92 (51.05) |
| (e) all pairs inside a ring (2143 pairs) | CC − B3LYP | fit | 0.01 | 0.05 | 0.41 | 1.09 (51.05) |
| (e) all pairs inside a ring (2143 pairs) | proxy ωB97X − B3LYP | mask | 0.35 | 0.52 | 7.23 | 4.32 (21.30) |
| (e) all pairs inside a ring (2143 pairs) | proxy ωB97X − B3LYP | fit | 0.11 | 0.14 | 1.80 | 1.97 (21.30) |
| (f) all pairs (4371 pairs) | CC − B3LYP | mask | 0.00 | 0.00 | 0.00 | 0.00 (51.05) |
| (f) all pairs (4371 pairs) | CC − B3LYP | fit | 0.00 | 0.00 | 0.00 | 0.00 (51.05) |
| (f) all pairs (4371 pairs) | proxy ωB97X − B3LYP | mask | 0.00 | 0.00 | 0.00 | 0.00 (21.30) |
| (f) all pairs (4371 pairs) | proxy ωB97X − B3LYP | fit | 0.00 | 0.00 | 0.00 | 0.00 (21.30) |

**Target pattern by the pre-registered rule (smallest with fit residual ≤ 0.35 and ring coupling ratio ≤ 0.5 on CC − B3LYP): (c) control.**
Total 1434 s.
