# Duration table — plan 05 through Module 08 (2026-09-13 10:27)

Naphthalene xtight factor F = 2.33 — PROVISIONAL: 15 of 24 fragments done, sum 16.7 h; remaining 9 at the observed mean 67 min -> total 26.8 h -> F = 2.33. Desktop = the hardware note's 16-core machine, 2.3-3.8 x the laptop (e, from the core count); Snellius = 4 thin nodes in parallel, each 4.6-7.7 x the laptop (e, Budget note). (m) measured, (e) estimated; every rule is in `probes/duration_table.py`.

| step | computation | days on laptop | days on desktop | days on Snellius (4 nodes) | status | note |
|---|---|---|---|---|---|---|
| R0 pilot (benzene) | 448 LNO-CCSD(T)/cc-pVTZ xtight energies at 76 min (m) | 23.6 | 6-10 | 0.8-1.3 | m |  |
| naphthalene DFT dry run, stage A | two psi4 Hessians (B3LYP, BHHLYP) at 6-31G* | 0.1-0.2 | 0.0-0.1 | 0.0-0.0 | e | B3LYP half exists (plan 02); psi4 runs on Windows, not on Snellius as installed |
| R1 smoothness sigma run (decision 35) | 10 naphthalene tight energies at 11.5 h (m) | 4.8 | 1.2-2.1 | 0.2-0.3 | m |  |
| M2a (gradient cost ratio g) | PySCFAD cells 0-4, benzene cc-pVDZ | 0.3 | 0.1-0.1 | 0.0-0.0 | e | laptop only (installed there); decides whether M2 is built |
| R1 deck (naphthalene) | 474 xtight energies at 27 h = 11.5 h x F, F = 2.33 (provisional) | 528.7 | 138-230 | 17-29 | m/F |  |
| R2 pyrene | deck ~936 energies (4M + 2E, E ~ M^2/2|G| = 324) at 5-10 x the naphthalene energy | does not fit | 1362-4539 | 170-567 | e | does not fit the laptop's 25 GB |
| R2 chrysene | deck ~2100 energies (4M + 2E, E ~ M^2/2|G| = 882) at 5-10 x the naphthalene energy | does not fit | 3055-10184 | 382-1273 | e | does not fit the laptop's 25 GB |
| R2 triphenylene | deck ~924 energies (4M + 2E, E ~ M^2/2|G| = 294) at 5-10 x the naphthalene energy | does not fit | 1344-4481 | 168-560 | e | does not fit the laptop's 25 GB |
| R2 tetracene | deck ~1218 energies (4M + 2E, E ~ M^2/2|G| = 441) at 5-10 x the naphthalene energy | does not fit | 1772-5907 | 221-738 | e | does not fit the laptop's 25 GB |
| R3 coronene | deck ~842 energies at 25-100 x the naphthalene energy (extrapolation) | does not fit | 6121-40807 | 765-5101 | e (extrapolated) | no measurement of any kind behind the factor |
| Module 05 corpus factory | 11321 B3LYP/6-31G* Hessians at 3-7 min (m, per Hessian) | 24-55 | 24-55 | 0.4-0.9 | m/e | same per-Hessian time on laptop and desktop (8 threads each; the laptop is busy with the anchor); Snellius: 4 nodes x 16 concurrent jobs assumed |
| Module 05 training | the Transformer on the corpus (CPU/GPU) | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| Module 06 generative proposer | DFT-only corpora, no coupled-cluster cost | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| Module 07 campaign officer | orchestration and cost record | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| Module 08 assembly | scoring R0-R3, no new energies | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |
| R6 fragment-probed C384H48 (if licensed) | 56 symmetry-unique fragments (Module 02) x an unmeasured per-fragment cost at that size | — | — | — | not measured | hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings |

**Totals of the estimable rows (days):** laptop 581-613 for what fits (R2-R3 do not: R2 pyrene, R2 chrysene, R2 triphenylene, R2 tetracene, R3 coronene); desktop 13823-66215; Snellius on 4 nodes 1725-8271. The R3 row alone is 6121-40807 desktop-days on an extrapolated factor; without R3 the desktop total is 7702-25407 days.

Open places: F (final when the xtight run ends; this table re-runs itself), g (M2a; when `results_m2a/` exists a gradient block is printed: R1 by 18 gradients = 18 g energy-equivalents, plan 06 X14). Levers not in the table: tight thresholds instead of xtight (÷ F, decision 20 reversed), P25 (deck ÷ ~1.6, after its licence test), gradients (M2).