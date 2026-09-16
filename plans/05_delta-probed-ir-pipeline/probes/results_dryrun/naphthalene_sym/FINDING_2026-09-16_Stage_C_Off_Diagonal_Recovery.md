# Stage C at naphthalene — the off-diagonal recovery does not reach its threshold, and the band-width rule is blind (16 September 2026, 15:45)

*Run: `dryrun_dft_delta_recovery.py --molecule naphthalene --symmetrised --stage C` on the stage B responses finished the same afternoon (712 patterns, 1,425 energies per arm, the symmetrised and irrep-projected stage A of 15 September). Stand-in correction Δ = H_BHHLYP − H_B3LYP at 6-31G*; deck amplitudes q_s = 1.0 with a second block at q₂ = 0.5. Report: `REPORT.md` in this folder; raw numbers `stageC_recovery.json`. Nothing here is a coupled-cluster statement.*

## What the run printed

**The off-diagonal criterion is never met.** The stopping rule of proposal §3.4 reads the held-out residual of the **off-diagonal** part, ρ_off. Its curve over the deck, from 98 to 1,082 energies:

| energies | 98 | 262 | 426 | 672 | 918 | 1,082 |
|---|---|---|---|---|---|---|
| ρ_off | 1.000 | 0.966 | 1.628 | 1.296 | 1.103 | 0.961 |

It does not fall; between 344 and 836 energies it is worse than no recovery at all (ρ_off > 1). **K_off at ρ_off ≤ 0.3: none, at any deck size.** At benzene the same rule reached its threshold at 210 off-diagonal energies.

**Why, in one line of arithmetic.** The held-out responses have RMS 198.22 µE_h, of which the off-diagonal part is **7.00 µE_h** (3.5 %). The model floor — the quartic contamination of a quadratic model at q_s = 1.0, measured here as ρ_dry = 0.0340 on the raw scale — is 0.0340 × 198.22 = **6.74 µE_h**. The contamination is the size of the signal. Subtracting the fitted diagonal quartic (Δ₄,iiii from the two amplitudes) does not help: the off-diagonal RMS after subtraction is 7.01 µE_h and ρ_off = 0.962, so what drowns the couplings is not the diagonal quartic but the cross terms a quadratic model cannot hold at unit amplitude.

**In band positions.** RMS frequency error of the recovered Δ₂ against the direct one, per family, in cm⁻¹:

| family | modes | full recovery | diagonal only |
|---|---|---|---|
| C–C stretch | 9 | 2.33 | 4.10 |
| C–H in-plane bend | 9 | 3.37 | 5.97 |
| C–H out-of-plane | 15 | 0.36 | 1.10 |
| C–H stretch | 8 | **2.89** | **0.03** |
| ring in-plane | 7 | 0.44 | 0.45 |

The recovery halves the error on three families, leaves 2.3–3.4 cm⁻¹ on the two in-plane skeleton families — at the level of the whole correction the project measures — and on the C–H stretches it is a hundred times *worse* than doing nothing: the fitted couplings inject error where the diagonal alone was already right to 0.03 cm⁻¹.

**The gradient route, on the same data, succeeds.** Mode G reaches the declared threshold at **96 gradients** with a model floor of 0.0019 and family errors of 0.05–0.21 cm⁻¹.

## A second, separate defect: the band-width rule reads a quantity a real molecule does not have, and stops at the first width that clears its tolerance

**Correction, 16 September 21:1x.** The first version of this section said the width w is chosen by the hold-out residual and that w = 25 wins because ρ is lowest there. That is wrong, and reading the selector itself (`dryrun_dft_delta_recovery.py`, the `w rule` block) gives a sharper defect than the one I described. ρ selects **λ** at fixed w; **w** is selected as the *smallest* candidate whose worst-family frequency RMS **against the direct Δ₂** clears τ₇ = 5.0 cm⁻¹. The table:

| w (cm⁻¹) | 25 | 50 | 100 | 200 | 400 |
|---|---|---|---|---|---|
| hold-out ρ | 0.034 | 0.034 | 0.034 | 0.040 | **0.048** |
| worst family RMS (cm⁻¹) | 3.37 | 3.36 | 3.36 | 3.36 | **0.82** |

w = 25 gives 3.37 cm⁻¹, which clears 5.0, so the search stops at the narrowest candidate and never reaches w = 400 at **0.82 cm⁻¹** — **four times better, left unclaimed**. Two independent faults, then. (i) The selector reads the direct Δ₂, which exists in this dry run and **does not exist on a real molecule** — the rule as written cannot be run in production at all. (ii) Its *smallest width that clears a tolerance* shape makes it stop at the first acceptable answer rather than the best available one; a tolerance is a floor, and this rule treats it as a target. The ρ column is a bystander: it is flat at 0.034 across w = 25–100 precisely because the off-diagonal part is 3.5 % of the response, so a residual on the full response could not have selected w either. This is the same class of blindness the plan already met once (decisions 8 and 12: a residual on the raw response read "done" while the couplings were unknown), now in the width rule rather than the stopping rule. It cannot be fixed by selecting on the family RMS, because on a real molecule the direct Δ₂ that defines it does not exist — a hold-out scored in cm⁻¹ rather than in µE_h is the direction, and it needs designing before it is used.

## What this does and does not say

- It is the **DFT stand-in**, not the coupled-cluster correction, at **one amplitude** and **one molecule**. The coupled-cluster Δ₂ may sit differently against the same quartic contamination, and nothing here measures that.
- It does not touch the **diagonal**: lever H (single-sided responses, decision 37) and the diagonal-first deck order of P27 are unaffected, and the diagonal-only column above is the quantity the per-family go/no-go reads.
- It does touch the **couplings**: the energies-only route to the off-diagonal elements, as the deck is designed today at q_s = 1.0, does not reach the plan's own threshold at naphthalene.

## The two tests this asks for (neither started; no psi4 beside the anchor run)

1. **Amplitude.** The contamination falls as q⁴ and the signal as q², so halving the amplitude should improve the ratio fourfold: predicted ρ_off ≈ 0.24 at q_s = 0.5, which would pass. Against it stands the noise floor: the off-diagonal signal itself falls to ≈ 1.75 µE_h, and the frozen spaces' own noise is ≈ 2 µE_h at benzene. The test is to repeat stage B's off-diagonal block at q_s = 0.5 (≈ 12 h of stand-in DFT on the laptop, after the anchor run) and read ρ_off. **Pre-registered prediction: ρ_off ≈ 0.24 ± 0.1 if contamination-dominated; ρ_off ≥ 0.8 if the noise floor dominates instead — in which case no amplitude window exists at naphthalene and the couplings need gradients.**
2. **The width rule.** Design a hold-out score in cm⁻¹ that does not use the direct Δ₂, and re-select w under it on this same data (desk work, no new energies).

Either way the finding belongs in the 26 September documents: it was produced by the plan's own stopping rule, on cheap stand-in data, before a single coupled-cluster energy was spent on couplings — which is what that rule is for.
