# E8 between-branch — pattern extension and least-squares ceilings, cc-pvdz (2026-09-24 02:30)

Internals: 54 (12 bonds). mask = minimum-norm ΔF zeroed outside the pattern; fit = least-squares ΔF on the pattern.

| pattern | correction | read | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|---|
| (c) control (978 pairs) | CC − B3LYP | mask | 0.08 | 0.80 | 8.39 | 6.22 (37.95) |
| (c) control (978 pairs) | CC − B3LYP | fit | 0.00 | 0.01 | 0.11 | 0.13 (37.95) |
| (c) control (978 pairs) | proxy ωB97X − B3LYP | mask | 0.06 | 0.15 | 2.91 | 2.20 (22.36) |
| (c) control (978 pairs) | proxy ωB97X − B3LYP | fit | 0.00 | 0.00 | 0.02 | 0.07 (22.36) |
| (d) (c) + pairs two bonds apart (1365 pairs) | CC − B3LYP | mask | 0.02 | 0.34 | 5.95 | 4.07 (37.95) |
| (d) (c) + pairs two bonds apart (1365 pairs) | CC − B3LYP | fit | 0.00 | 0.00 | 0.02 | 0.06 (37.95) |
| (d) (c) + pairs two bonds apart (1365 pairs) | proxy ωB97X − B3LYP | mask | 0.04 | 0.17 | 2.91 | 1.91 (22.36) |
| (d) (c) + pairs two bonds apart (1365 pairs) | proxy ωB97X − B3LYP | fit | 0.00 | 0.00 | 0.01 | 0.03 (22.36) |
| (e) all pairs inside a ring (984 pairs) | CC − B3LYP | mask | 0.08 | 0.80 | 8.39 | 6.22 (37.95) |
| (e) all pairs inside a ring (984 pairs) | CC − B3LYP | fit | 0.00 | 0.01 | 0.11 | 0.13 (37.95) |
| (e) all pairs inside a ring (984 pairs) | proxy ωB97X − B3LYP | mask | 0.06 | 0.15 | 2.91 | 2.20 (22.36) |
| (e) all pairs inside a ring (984 pairs) | proxy ωB97X − B3LYP | fit | 0.00 | 0.00 | 0.02 | 0.07 (22.36) |
| (f) all pairs (1485 pairs) | CC − B3LYP | mask | 0.00 | 0.00 | 0.00 | 0.00 (37.95) |
| (f) all pairs (1485 pairs) | CC − B3LYP | fit | 0.00 | 0.00 | 0.00 | 0.00 (37.95) |
| (f) all pairs (1485 pairs) | proxy ωB97X − B3LYP | mask | 0.00 | 0.00 | 0.00 | 0.00 (22.36) |
| (f) all pairs (1485 pairs) | proxy ωB97X − B3LYP | fit | 0.00 | 0.00 | 0.00 | 0.00 (22.36) |

**Target pattern by the pre-registered rule (smallest with fit residual ≤ 0.35 and ring coupling ratio ≤ 0.5 on CC − B3LYP): (c) control.**
Total 358 s.
