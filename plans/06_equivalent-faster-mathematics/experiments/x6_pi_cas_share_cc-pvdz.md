# X6 — π-CAS(6,6) share of the correlation curvature along the probed benzene modes (cc-pvdz, 2026-09-14 08:18)

Even degree-4 fits in q of E_corr(MP2) and E_corr(CAS(6,6) via AVAS on C 2pz) − both relative to the same RHF; a2 is the curvature coefficient (µE_h per q²), Δω = a2 in cm⁻¹ the frequency shift it implies (M1's convention). Share = a2(CAS)/a2(MP2).

| mode | family | ω (cm⁻¹) | a2 MP2 (µE_h) | a2 π-CAS (µE_h) | **share** | Δω MP2 / π-CAS (cm⁻¹) | rms fit MP2 / CAS (µE_h) |
|---|---|---|---|---|---|---|---|
| 12 | CH-ip-bend | 1020 | -99.42 | -46.24 | **0.47** | -21.82 / -10.15 | 2506.317 / 1388.338 |
| 18 | CC-stretch | 1357 | 1133.77 | 102.14 | **0.09** | 248.83 / 22.42 | 0.389 / 0.194 |
| 6 | CH-oop | 865 | -627.20 | 298.90 | **-0.48** | -137.65 / 65.60 | 0.037 / 0.020 |

Losing condition (pre-stated): pi-CAS share of the MP2 correlation curvature < 0.5 on the C-C stretch mode. The sealed CC − DFT comparison waits for the pilot note.

Constants: {"basis_default": "cc-pvdz", "npts_default": 9, "q_range": [-1.0, 1.0], "active_space": [6, 6], "avas_labels": ["C 2pz"], "avas_threshold": 0.2, "fit_degree": 4, "losing_condition": "pi-CAS share of the MP2 correlation curvature < 0.5 on the C-C stretch mode"}