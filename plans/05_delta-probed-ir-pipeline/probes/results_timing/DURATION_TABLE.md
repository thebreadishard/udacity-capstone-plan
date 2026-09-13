# Duration table — plan 05 through Module 08 (2026-09-13 11:23)

Naphthalene xtight factor F = 2.27 — PROVISIONAL: 16 of 24 fragments done, sum 17.4 h; remaining 8 at the observed mean 65 min -> total 26.0 h -> F = 2.27. Desktop = the hardware note's 16-core machine, 2.3-3.8 x the laptop (e, from the core count); Snellius = 4 thin nodes in parallel, each 4.6-7.7 x the laptop (e, Budget note). (m) measured, (e) estimated; every rule is in `probes/duration_table.py`.

| step | computation | days on laptop | days on desktop | days on Snellius (4 nodes) | status | note |
|---|---|---|---|---|---|---|
| R0 pilot (benzene) | 448 LNO-CCSD(T)/cc-pVTZ xtight energies at 76 min (m) | 23.6 | 6-10 | 0.8-1.3 | m |  |
| naphthalene DFT dry run, stage A | two psi4 Hessians (B3LYP, BHHLYP) at 6-31G* | 0.1-0.2 | 0.0-0.1 | 0.0-0.0 | e | B3LYP half exists (plan 02); psi4 runs on Windows, not on Snellius as installed |
| R1 smoothness sigma run (decision 35) | 10 naphthalene tight energies at 11.5 h (m) | 4.8 | 1.2-2.1 | 0.2-0.3 | m |  |
| M2a (gradient cost ratio g) | PySCFAD cells 0-4, benzene cc-pVDZ | 0.3 | 0.1-0.1 | 0.0-0.0 | e | laptop only (installed there); decides whether M2 is built |
| R1 deck (naphthalene) | 474 xtight energies at 26 h = 11.5 h x F, F = 2.27 (provisional) | 514.2 | 134-224 | 17-28 | m/F |  |
| R2 pyrene | deck ~936 energies (4M + 2E, E ~ M^2/2|G| = 324) at 5-10 x the naphthalene energy | does not fit | 1324-4414 | 166-552 | e | does not fit the laptop's 25 GB |
| R2 chrysene | deck ~2100 energies (4M + 2E, E ~ M^2/2|G| = 882) at 5-10 x the naphthalene energy | does not fit | 2971-9904 | 371-1238 | e | does not fit the laptop's 25 GB |
| R2 triphenylene | deck ~924 energies (4M + 2E, E ~ M^2/2|G| = 294) at 5-10 x the naphthalene energy | does not fit | 1307-4358 | 163-545 | e | does not fit the laptop's 25 GB |
| R2 tetracene | deck ~1218 energies (4M + 2E, E ~ M^2/2|G| = 441) at 5-10 x the naphthalene energy | does not fit | 1723-5744 | 215-718 | e | does not fit the laptop's 25 GB |
| R3 coronene | deck ~842 energies at 25-100 x the naphthalene energy (extrapolation) | does not fit | 5953-39688 | 744-4961 | e (extrapolated) | no measurement of any kind behind the factor |
| Module 05 corpus factory | 11321 B3LYP/6-31G* Hessians at 3-7 min (m, per Hessian) | 24-55 | 24-55 | 0.4-0.9 | m/e | same per-Hessian time on laptop and desktop (8 threads each; the laptop is busy with the anchor); Snellius: 4 nodes x 16 concurrent jobs assumed |
| Module 05 training | the Transformer on the corpus (CPU/GPU) | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| Module 06 generative proposer | DFT-only corpora, no coupled-cluster cost | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| Module 07 campaign officer | orchestration and cost record | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| Module 08 assembly | scoring R0-R3, no new energies | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| R6 fragment-probed C384H48 (if licensed) | 56 symmetry-unique fragments (Module 02) x an unmeasured per-fragment cost at that size | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |

**Totals of the estimable rows (days):** laptop 567-598 for what fits (R2-R3 do not: R2 pyrene, R2 chrysene, R2 triphenylene, R2 tetracene, R3 coronene); desktop 13445-64400; Snellius on 4 nodes 1678-8044. The R3 row alone is 5953-39688 desktop-days on an extrapolated factor; without R3 the desktop total is 7492-24712 days.

Open places: F (final when the xtight run ends; this table re-runs itself), g (M2a; when `results_m2a/` exists a gradient block is printed: R1 by 18 gradients = 18 g energy-equivalents, plan 06 X14). Levers not in the table: tight thresholds instead of xtight (÷ F, decision 20 reversed), P25 (deck ÷ ~1.6, after its licence test), gradients (M2).

## P26 block — thin decks and molecules per year

Decks per molecule: full = 4M + 2E; diagonal = 2M; diagonal + P25 couplings = 2M + 2·0.40·E (plan 06 X10 at benzene: 19 of 47 eligible pairs; the naphthalene repeat decides); gradients = 2k with k ≈ 1.5·M/|G| (k ~ 1.5 M/|G| (naphthalene: 48/8*1.5 = 9 = X14)), costing 2k·g energies. Desktop year = 365 days at 2.3-3.8× the laptop; Snellius small allocation 100,000 SBU ≈ 33 node-days at 4.6-7.7× the laptop per node. Molecules per year = (desktop-days + Snellius node-days converted) / days per molecule.

| class | deck | energies (or energy-equivalents) | days per molecule, desktop | **molecules per year (desktop + small Snellius)** | status |
|---|---|---|---|---|---|
| benzene-class (M=30, |G|=24, E=47 m) | full 4M + 2E | 214 | 2.9-4.9 | **82.3-160.7** | m/F |
| benzene-class (M=30, |G|=24, E=47 m) | diagonal 2M | 60 | 0.8-1.4 | **293.5-573.2** | m/F |
| benzene-class (M=30, |G|=24, E=47 m) | diagonal + P25 couplings | 98 | 1.3-2.2 | **179.7-350.9** | m/F |
| benzene-class (M=30, |G|=24, E=47 m) | gradients 2k = 4, g = 3 | 12 | 0.2-0.3 | **1467.4-2866.0** | m/F |
| benzene-class (M=30, |G|=24, E=47 m) | gradients 2k = 4, g = 5 | 20 | 0.3-0.5 | **880.4-1719.6** | m/F |
| benzene-class (M=30, |G|=24, E=47 m) | gradients 2k = 4, g = 10 | 40 | 0.6-0.9 | **440.2-859.8** | m/F |
| benzene-class (M=30, |G|=24, E=47 m) | gradients 2k = 4, g = 20 | 80 | 1.1-1.8 | **220.1-429.9** | m/F |
| naphthalene-class (M=48, E=141 m) | full 4M + 2E | 474 | 134.1-223.6 | **1.8-3.5** | m/F |
| naphthalene-class (M=48, E=141 m) | diagonal 2M | 96 | 27.2-45.3 | **8.9-17.4** | m/F |
| naphthalene-class (M=48, E=141 m) | diagonal + P25 couplings | 210 | 59.4-99.0 | **4.1-8.0** | m/F |
| naphthalene-class (M=48, E=141 m) | gradients 2k = 18, g = 3 | 54 | 15.3-25.5 | **15.9-31.0** | m/F |
| naphthalene-class (M=48, E=141 m) | gradients 2k = 18, g = 5 | 90 | 25.5-42.4 | **9.5-18.6** | m/F |
| naphthalene-class (M=48, E=141 m) | gradients 2k = 18, g = 10 | 180 | 50.9-84.9 | **4.8-9.3** | m/F |
| naphthalene-class (M=48, E=141 m) | gradients 2k = 18, g = 20 | 360 | 101.9-169.8 | **2.4-4.6** | m/F |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | full 4M + 2E | 936 | 1324.3-4414.5 | **0.1-0.4** | e |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | diagonal 2M | 144 | 203.7-679.1 | **0.6-2.3** | e |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | diagonal + P25 couplings | 406 | 574.4-1914.6 | **0.2-0.8** | e |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | gradients 2k = 28, g = 3 | 84 | 118.9-396.2 | **1.0-4.0** | e |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | gradients 2k = 28, g = 5 | 140 | 198.1-660.3 | **0.6-2.4** | e |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | gradients 2k = 28, g = 10 | 280 | 396.2-1320.6 | **0.3-1.2** | e |
| pyrene-class (M=72, E~324 e, energy 5-10x naphthalene e) | gradients 2k = 28, g = 20 | 560 | 792.3-2641.1 | **0.2-0.6** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | full 4M + 2E | 842 | 5953.2-39687.7 | **0.0-0.1** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | diagonal 2M | 204 | 1443.2-9621.3 | **0.0-0.3** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | diagonal + P25 couplings | 379 | 2683.0-17886.3 | **0.0-0.2** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | gradients 2k = 12, g = 3 | 36 | 254.7-1697.9 | **0.2-1.9** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | gradients 2k = 12, g = 5 | 60 | 424.5-2829.8 | **0.1-1.1** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | gradients 2k = 12, g = 10 | 120 | 848.9-5659.6 | **0.1-0.6** | e |
| coronene-class (M=102, E~217 e, energy 25-100x naphthalene e) | gradients 2k = 12, g = 20 | 240 | 1697.9-11319.1 | **0.0-0.3** | e |

Reading: a training set of tens of PAHs per year exists only on the gradient rows with small g, or on the diagonal rows for the smallest classes; the full-deck rows are the truth-rung cost, not a factory. Pyrene- and coronene-class rows rest on the unmeasured energy factors and are brackets.