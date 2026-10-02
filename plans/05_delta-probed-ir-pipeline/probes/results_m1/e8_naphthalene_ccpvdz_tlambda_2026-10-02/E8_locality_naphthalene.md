# E8 — locality of the CCSD(T) − B3LYP correction, cc-pvdz (2026-10-02 02:19)

ΔH RMS (a.u.): CC − B3LYP 5.60e-03, proxy 3.17e-03. Internals: 93. Parameter-free projections of the minimum-norm internal correction.

| pattern | correction | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|
| (a) diagonal | CC − B3LYP | 0.68 | **0.67** | 15.67 | 33.88 (51.05) |
| (a) diagonal | proxy ωB97X − B3LYP | 0.77 | **1.05** | 17.06 | 10.14 (21.30) |
| (b) + atom-sharing pairs | CC − B3LYP | 0.15 | **0.72** | 7.37 | 7.14 (51.05) |
| (b) + atom-sharing pairs | proxy ωB97X − B3LYP | 0.65 | **0.90** | 14.25 | 7.44 (21.30) |
| (c) + ring bond-bond pairs | CC − B3LYP | 0.12 | **0.69** | 7.12 | 6.90 (51.05) |
| (c) + ring bond-bond pairs | proxy ωB97X − B3LYP | 0.35 | **0.52** | 7.13 | 4.27 (21.30) |

Exploratory: correlation of ΔF_CC and ΔF_proxy on pattern (c) 0.560; norm ratio CC/proxy 1.70.
**Verdict (pre-registered):** pattern (c) residual 0.12, ring coupling ratio 0.69 → **between**.
Total 1441 s.
