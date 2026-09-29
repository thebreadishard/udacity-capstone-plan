# E8 — locality of the CCSD(T) − B3LYP correction, cc-pvdz (2026-09-29 20:57)

ΔH RMS (a.u.): CC − B3LYP 5.11e-03, proxy 3.48e-03. Internals: 54. Parameter-free projections of the minimum-norm internal correction.

| pattern | correction | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|
| (a) diagonal | CC − B3LYP | 0.55 | **0.90** | 16.80 | 25.55 (44.52) |
| (a) diagonal | proxy ωB97X − B3LYP | 0.78 | **0.95** | 18.78 | 11.55 (22.36) |
| (b) + atom-sharing pairs | CC − B3LYP | 0.13 | **0.77** | 12.25 | 9.41 (44.52) |
| (b) + atom-sharing pairs | proxy ωB97X − B3LYP | 0.58 | **0.67** | 14.09 | 7.35 (22.36) |
| (c) + ring bond-bond pairs | CC − B3LYP | 0.09 | **0.79** | 11.67 | 8.98 (44.52) |
| (c) + ring bond-bond pairs | proxy ωB97X − B3LYP | 0.06 | **0.15** | 2.91 | 2.20 (22.36) |

Exploratory: correlation of ΔF_CC and ΔF_proxy on pattern (c) 0.619; norm ratio CC/proxy 1.63.
**Verdict (pre-registered):** pattern (c) residual 0.09, ring coupling ratio 0.79 → **between**.
Total 436 s.
