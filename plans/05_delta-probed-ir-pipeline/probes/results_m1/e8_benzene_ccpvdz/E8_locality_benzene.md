# E8 — locality of the CCSD(T) − B3LYP correction, cc-pvdz (2026-09-24 02:19)

ΔH RMS (a.u.): CC − B3LYP 4.98e-03, proxy 3.48e-03. Internals: 54. Parameter-free projections of the minimum-norm internal correction.

| pattern | correction | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|
| (a) diagonal | CC − B3LYP | 0.54 | **1.08** | 16.00 | 19.22 (37.95) |
| (a) diagonal | proxy ωB97X − B3LYP | 0.78 | **0.95** | 18.78 | 11.55 (22.36) |
| (b) + atom-sharing pairs | CC − B3LYP | 0.27 | **0.93** | 11.88 | 8.37 (37.95) |
| (b) + atom-sharing pairs | proxy ωB97X − B3LYP | 0.58 | **0.67** | 14.09 | 7.35 (22.36) |
| (c) + ring bond-bond pairs | CC − B3LYP | 0.08 | **0.80** | 8.39 | 6.22 (37.95) |
| (c) + ring bond-bond pairs | proxy ωB97X − B3LYP | 0.06 | **0.15** | 2.91 | 2.20 (22.36) |

Exploratory: correlation of ΔF_CC and ΔF_proxy on pattern (c) 0.780; norm ratio CC/proxy 1.61.
**Verdict (pre-registered):** pattern (c) residual 0.08, ring coupling ratio 0.80 → **between**.
Total 358 s.
