# X6 (run 2026-09-14 08:18) — the π-CAS share of the correlation curvature along benzene's probed modes: **lost**

*Pre-registered 12 September (Orientation §7; script header): along the three M1 benzene modes and the same nine-point q grid at cc-pVDZ, compare the curvature of E_CAS(6,6) − E_HF (the π-valence active space, AVAS on the carbon 2p_z functions) with the curvature of E_MP2 − E_HF, the cheapest unsealed proxy for the correlation energy; share = a₂(CAS)/a₂(MP2) from even degree-4 fits. **Losing condition, stated before the run: a π-CAS share below ½ on the C–C stretch mode closes S3 (a π-space DMRG anchor for long acenes) as an anchor route.** Output `experiments/x6_pi_cas_share_cc-pvdz.md/.json`, log `x6_2026-09-14.log`; the sealed CC − DFT comparison (`--sealed`) waits for the pilot note as designed.*

## Result

| mode | family | ω (cm⁻¹) | a₂ MP2 (µE_h) | a₂ π-CAS (µE_h) | **share** | Δω MP2 / π-CAS (cm⁻¹) | fit RMS MP2 / CAS (µE_h) |
|---|---|---|---|---|---|---|---|
| 18 | C–C stretch | 1357 | 1133.8 | 102.1 | **0.09** | 248.8 / 22.4 | 0.39 / 0.19 |
| 6 | C–H out-of-plane | 865 | −627.2 | 298.9 | **−0.48** | −137.7 / 65.6 | 0.04 / 0.02 |
| 12 | C–H in-plane bend | 1020 | −99.4 | −46.2 | 0.47 | −21.8 / −10.2 | **2,506 / 1,388** (fit not trustworthy: the curve is not an even quartic on this grid — the mode is one component of a degenerate pair, and the CAS/MP2 energies along it are not smooth at the 10³ µE_h level; printed, not read) |

**Verdict under the pre-stated condition: LOST.** On the C–C stretch the π-valence CAS(6,6) carries 9 % of the MP2 correlation curvature; on the C–H out-of-plane mode it carries −48 %, i.e. the π-space curvature has the *opposite sign* to the full correlation curvature. The correlation correction to benzene's ring-mode force constants is not a π-space quantity; it lives predominantly in the σ–π and σ dynamic correlation that a π active space excludes by construction.

## What it closes and what it does not

- **Closes (plan 06 direction S3, the "solve the π cloud exactly" route; reflection lead E's gate):** a π-active-space solver (DMRG or otherwise) embedded in a DFT σ frame cannot be the label generator for the ring-mode corrections, because the quantity to be labelled is not in that space. The mathematics branch of plan 06 loses one of its two anchor candidates; the decision rule's 1 December review has one item fewer.
- **Confirms X17 from the other side:** X17 found the correction terminates one bond out in internal coordinates but cannot be split into σ and π blocks for the out-of-plane family; X6 says even the diagonal ring-mode curvature is mostly not π. Both point at dynamic correlation of the whole valence shell, which is exactly what local coupled cluster computes and what a small active space cannot.
- **Does not close:** the *use* of MP2 as a proxy (idea I1 in the mandate ledger) — MP2 is the *reference* here, not the tested object; the sealed CC − DFT comparison at the pilot note, which will say how well MP2's curvature tracks the coupled-cluster one; and lead A (a better functional), which X6 does not touch.
- **Caveat on the proxy:** MP2 − HF is not CC − DFT. A share of 9 % against MP2 could differ against CCSD(T); the pre-registered `--sealed` rerun at the pilot note decides whether the verdict stands against the anchor itself. Nothing in the σ-dominance is expected to reverse, since (T) and CCSD add dynamic correlation of the same kind, not π-static correlation.

## Consequences recorded

- Plan 06 Orientation §7 / decision rule: S3 closed by its own losing condition on 14 September; branch M keeps T3 (the gap-decay conjecture, X7 running) and the Lean-checked recovery theorems.
- Mandate ledger: lead E's status becomes "gate fired negative"; obstacle 3's proxy question shifts entirely to lead A's test (double hybrid, MP2) — the label generator for large PAHs is local CC or a learned residual, not a π solver.
