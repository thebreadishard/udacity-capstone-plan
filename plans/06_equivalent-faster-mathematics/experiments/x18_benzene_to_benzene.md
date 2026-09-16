# X18 — type transfer of the internal-coordinate correction, benzene → benzene (2026-09-16 07:19)

Source model: type-constrained least squares on the source (one constant per type), so source and target share the parameterisation; 29 types on benzene; source residual (type model, first order) RMS 38.53 cm⁻¹, max 84.42.

## Transfer to benzene: 29 types on the target, 0 without a source constant (set to 0)

| family | modes | RMS error (cm⁻¹) | max | RMS zero rule | judged | passes 2.5 |
|---|---|---|---|---|---|---|
| CC-stretch | 6 | **0.01** | 0.02 | 48.46 | yes | yes |
| CH-ip-bend | 7 | **0.02** | 0.04 | 34.69 | — | yes |
| CH-oop | 9 | **70.35** | 84.42 | 70.35 | — | NO |
| CH-stretch | 6 | **0.05** | 0.07 | 25.11 | yes | yes |
| ring-ip | 2 | **0.03** | 0.03 | 23.07 | — | yes |

**Verdict (judged families): PASS.**

Self-test: source = target — the transfer reproduces the type-constrained source fit; the error printed is the type model's own residual, not a transfer error.