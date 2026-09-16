# X18 — type transfer of the internal-coordinate correction, benzene → naphthalene_sym (2026-09-16 07:19)

Source model: type-constrained least squares on the source (one constant per type), so source and target share the parameterisation; 29 types on benzene; source residual (type model, first order) RMS 38.53 cm⁻¹, max 84.42.

## Transfer to naphthalene_sym: 29 types on the target, 0 without a source constant (set to 0)

| family | modes | RMS error (cm⁻¹) | max | RMS zero rule | judged | passes 2.5 |
|---|---|---|---|---|---|---|
| CC-stretch | 9 | **17.82** | 38.90 | 41.22 | yes | NO |
| CH-ip-bend | 9 | **5.76** | 14.81 | 35.82 | — | NO |
| CH-oop | 15 | **64.48** | 85.15 | 64.48 | — | NO |
| CH-stretch | 8 | **0.27** | 0.60 | 25.11 | yes | yes |
| ring-ip | 7 | **6.42** | 11.92 | 22.02 | — | NO |

**Verdict (judged families): LOSE.**