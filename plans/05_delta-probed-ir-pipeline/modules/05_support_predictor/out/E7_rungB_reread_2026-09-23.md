# E7 / rung B re-read with second-route Hessians (post-hoc, 23 September 2026)

Analytic Hessians substituted for: benzene (A_8448043181)

| molecule of hold-out (a) | ratio before | ratio after | ring diag before / after | corrected ω before / after (zero) | ΔH residual before / after |
|---|---|---|---|---|---|
| biphenyl | 0.35 | **0.35** | 6.5 / 6.5 | 6.1 / 6.1 (23.8) | 0.25 / 0.25 |
| benzene * | 0.99 | **0.25** | 42.5 / 4.1 | 34.1 / 5.4 (25.0) | 0.71 / 0.20 |
| fluorene | 0.38 | **0.38** | 6.0 / 6.0 | 6.2 / 6.2 (23.7) | 0.29 / 0.29 |
| phenanthrene | 0.50 | **0.50** | 6.2 / 6.2 | 6.3 / 6.3 (22.9) | 0.38 / 0.38 |
| fluoranthene | 0.52 | **0.52** | 7.2 / 7.2 | 6.5 / 6.5 (22.3) | 0.42 / 0.42 |
| 2-naphthoic_acid | 0.58 | **0.58** | 5.4 / 5.4 | 7.0 / 7.0 (23.2) | 0.39 / 0.39 |
| benzophenone | 0.35 | **0.35** | 5.8 / 5.8 | 5.9 / 5.9 (23.3) | 0.25 / 0.25 |
| benzonitrile | 0.29 | **0.29** | 4.5 / 4.5 | 6.3 / 6.3 (24.5) | 0.28 / 0.28 |
| phenanthridine | 0.54 | **0.54** | 5.4 / 5.4 | 5.4 / 5.4 (22.2) | 0.39 / 0.39 |
| biphenylene | 0.41 | **0.41** | 7.7 / 7.7 | 7.2 / 7.2 (23.6) | 0.35 / 0.35 |

| aggregate | before | after |
|---|---|---|
| (a) GBT: ratio / ring diag / corrected ω | 0.82 / 11.8 / 10.0 | **0.46** / 6.1 / 6.3 |
| (a) MLP: ratio / ring diag / corrected ω | 0.81 / 11.3 / 9.3 | **0.43** / 4.5 / 4.8 |
| (b) GBT: ratio / ring diag / corrected ω | 0.49 / 6.4 / 6.7 | **0.49** / 6.4 / 6.7 |
| (b) MLP: ratio / ring diag / corrected ω | 0.47 / 4.6 / 5.1 | **0.47** / 4.6 / 5.1 |

\* = analytic second-route Hessians substituted.
Total 562 s.
