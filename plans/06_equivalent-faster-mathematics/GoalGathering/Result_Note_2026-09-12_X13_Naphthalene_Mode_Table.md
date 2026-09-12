# Result note 2026-09-12 (evening) — X13: naphthalene's DFT mode table, its 141 symmetry-allowed pairs (= plan 05's 282 R1 off-diagonal energies), and the DFT-only ranking pre-tabulated for P25's licence test

*Script `experiments/x13_naphthalene_mode_table.py`; tables `x13_naphthalene_mode_table.md` / `.json`. Input: plan 02's B3LYP/6-31G* naphthalene Hessian (git `57a7910`, extracted by the script), at the geometry plan 05's dry run will use (identical within 5 × 10⁻⁴ bohr, checked earlier tonight). Direction S4; groundwork for the naphthalene repeat of X10. Every number from the file.*

## 1. What was built

The 48 normal modes (the six smallest |λ| dropped) in the inertial frame, each with its frequency, its D2h irreducible representation (character ⟨v|Rv⟩ under the eight operations; axis convention: x the long axis, y the short in-plane axis, z the plane normal — labels B1/B2/B3 follow that convention) and the dry run's family label (`assign_families` of `dryrun_dft_delta_recovery.py`, reproduced unchanged). No imaginary modes; four modes have characters off ±1 by more than 10⁻³ (all still uniquely assignable), none unassigned.

| | count |
|---|---|
| modes | 48 (Ag 9, B1g 8, B2g 3, B3g 4, Au 4, B1u 4, B2u 8, B3u 8) |
| families | CC-stretch 9, CH-ip-bend 9, CH-oop 15, CH-stretch 8, ring-ip 7 |
| off-diagonal pairs | 1,128 |
| **same-irrep (eligible) pairs** | **141 (12.5 %)** |
| eligible pairs within a factor 10 / 100 of the top resonance denominator | 64 / 141 |

## 2. Two things the table settles now

- **Plan 05's R1 deck is cross-checked.** The proposal (§3.2) prices the R1 deck at 96 + 96 + 282 energies; 282 = 2 × 141, the deck's two-mode pattern price for exactly the eligible pairs found here from the modes' symmetry alone. The number was derived independently on 6 September; tonight's table reproduces it from the stored Hessian.
- **The licence test of draft P25 has its table in advance.** The DFT-only ranking of X10 over the 141 pairs is printed (top of the list: the near-degenerate C–H stretch pairs at 3176/3194 and 3174/3193 cm⁻¹, then C–H in-plane bends at 1184/1244, C–H out-of-plane pairs at 900/994 and 785/900). When the BHHLYP half of the dry run exists, the repeat of X10 ranks these pairs and reads how many the DFT rule needs for 0.5 cm⁻¹ — against a table it did not choose. The rule's selectivity is already visible: 64 of 141 pairs sit within a factor 10 of the top denominator, so a rule that needs "about half" would be close to its losing condition; the correction's magnitudes decide.

## 3. Side products

- **For Module 03:** this is the naphthalene DFT mode-vector family table the scoreboard was waiting for ("family labels by DFT mode vector once the naphthalene dry run exists"), from the B3LYP side; the BHHLYP side does not change families.
- **For the pilot note's prerequisite (a):** the B3LYP half of the naphthalene dry run exists; the machine queue's item 5 is the BHHLYP Hessian only.
- **Benzene cross-check not clean:** plan 02's benzene Hessian is not D6h-symmetric (its E-pair members are split by up to 23 cm⁻¹, e.g. 620.6/643.2), so the D2h character analysis flags 23 of 30 modes there and the count (35 eligible of 435) is not comparable with the dry run's 57 same-irrep pairs (from the symmetrised dry-run modes). The naphthalene file has no such defect (no degeneracies to split, four mildly off-integer characters). Plan 02's benzene and naphthalene files are therefore of different quality; only the naphthalene one is used further.

## 4. What changes

Nothing in plan 05's frozen text. Ledger S4: X13 done (groundwork); P25's licence test now has its pre-registered pair table. Plan 05 README: the 282-energy cross-check and the Module 03 family table noted in the dated line of 12 September.
