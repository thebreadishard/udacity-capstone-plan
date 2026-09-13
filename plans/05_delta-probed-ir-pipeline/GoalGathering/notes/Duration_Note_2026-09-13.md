# Duration note 2026-09-13 — how long every computation of plan 05 takes, through Module 08, per route (with two open places)

*Asked by the user on 13 September ("in welk document wordt het beste uitgelegd hoe lang het duurt"): no single document did. This note is that document. Every row is printed by `probes/duration_table.py` into `probes/results_timing/DURATION_TABLE.md` from measured prices (m) or labelled estimates (e); the script re-runs itself when the two open places fill. Nothing here changes the Budget or the Ladder; it reads them. The table is also the draft of the §12 table the user asked for in the proposal (step / computation / days on laptop / days on desktop / days on Snellius) — inserted there only after the column definitions below are confirmed.*

## 1. The two open places

- **F, the xtight/tight factor at naphthalene.** Measured tonight when the running xtight energy ends. **Provisional now: F = 2.33** (15 of 24 fragments in the checkpoint sum to 16.7 h, the remaining nine at the observed mean of 67 min give ≈ 26.8 h, against 11.5 h at tight). That is close to benzene's 2.1 and far below the P13 memo's model value of 3.6–4.7 — good news for the calendar if it holds through the large fragments still to come.
- **g, the gradient-to-energy cost ratio (M2a).** Not in the baseline table (energies only). When it exists the script prints a gradient block: the R1 deck by 18 gradients (plan 06 X14) = 18·g energy-equivalents.

## 2. Definitions the table uses (to be confirmed by the user)

- **Laptop:** this machine, 8 threads, one anchor job at a time, 25 GB ceiling; pyrene and larger do not fit.
- **Desktop:** the hardware note's 16-core machine (128 → 256 GB); speed 2.3–3.8 × the laptop, *an estimate from the core count, never timed* (P13 memo).
- **Snellius:** 4 thin nodes in parallel (a Small Compute application; decks are embarrassingly parallel over energies), each 4.6–7.7 × the laptop (Budget's Snellius note: 1.5–2.5 h wall per naphthalene tight energy). Node-days = 4 × the days shown.
- **Decks:** 4M + 2E energies (M modes, E same-irrep pairs); E measured at benzene (47) and naphthalene (141); estimated as M²/(2|G|) above (gives 144 at naphthalene). All coupled-cluster energies at the anchor's xtight thresholds (decision 20).
- **R2 price per energy:** 5–10 × naphthalene (Budget, unmeasured). **R3:** 25–100 × naphthalene — the author's extrapolation, no measurement of any kind behind it; the row is a placeholder for the pyrene timing that the Budget names as the cluster's first job.

## 3. The table (provisional F; from `DURATION_TABLE.md`)

| step | computation | days on laptop | days on desktop | days on Snellius (4 nodes) | status |
|---|---|---|---|---|---|
| R0 pilot (benzene) | 448 xtight energies at 76 min (m) | 23.6 | 6–10 | 0.8–1.3 | m |
| naphthalene DFT dry run, stage A | two psi4 Hessians | 0.1–0.2 | < 0.1 | — (psi4 on Windows) | e |
| R1 smoothness σ run (decision 35) | 10 tight energies at 11.5 h (m) | 4.8 | 1.2–2.1 | 0.2–0.3 | m |
| M2a (g) | PySCFAD cells 0–4, benzene cc-pVDZ | 0.3 | — | — | e |
| **R1 deck (naphthalene)** | 474 xtight energies at 11.5 h × F | **529** | **138–230** | **17–29** | m/F |
| R2 pyrene | ≈ 936 energies at 5–10 × naphthalene | does not fit | 1,360–4,540 | 170–570 | e |
| R2 chrysene | ≈ 2,100 energies (C2h: few symmetry savings) | does not fit | 3,060–10,180 | 380–1,270 | e |
| R2 triphenylene | ≈ 924 energies | does not fit | 1,340–4,480 | 170–560 | e |
| R2 tetracene | ≈ 1,218 energies | does not fit | 1,770–5,910 | 220–740 | e |
| R3 coronene | ≈ 842 energies at 25–100 × naphthalene | does not fit | 6,100–40,800 | 770–5,100 | e (extrapolated) |
| Module 05 corpus factory | 11,321 B3LYP Hessians at 3–7 min (m) | 24–55 (laptop busy) | 24–55 | 0.4–0.9 | m/e |
| Module 05 training, Module 06 proposer, Module 07 officer, Module 08 assembly | DFT-only corpora, orchestration, scoring | hours, not measured | hours | hours | not measured |
| R6 fragment-probed C₃₈₄H₄₈ (if licensed) | 56 symmetry-unique fragments (Module 02) × an unmeasured per-fragment cost | — | — | — | not estimable before R2–R3 fragment timings |

## 4. What the table says, read honestly

1. **R0 and R1 are within reach:** the pilot in three to four laptop-weeks; the R1 deck in five to eight months on the desktop or three to four weeks on four Snellius nodes, at the provisional F. That is the calendar the P13 memo already implied, now with a better F.
2. **R2 and R3 as written are out of reach on every route considered.** Four R2 molecules with full symmetry-prior decks at 5–10 × the naphthalene price are thousands of desktop-days and hundreds to more than a thousand days on four nodes each — tens of millions of SBU, a scale no Small Compute application covers; R3 with any plausible factor is worse. This is not new in kind (the Budget said "order 1–2 million SBU" for R2 and "several million" for R3), but the table makes the sum visible: **the decks, not the machines, are the problem above R1.** The Budget's own answer — family- and mode-selective scoring at R2–R3 instead of full decks — is what §12 must lean on, and the table should get a second version with those reduced decks once the pilot note fixes them.
3. **Where plan 06 bites.** The levers that change R2–R3 by orders of magnitude are exactly the ones on the ladder: P25 (deck ÷ ≈ 1.6, after its licence test), and gradients — under the symmetry prior a whole correction costs 2·(largest irrep block) gradients (X14: 18 at naphthalene; of order 20–40 at pyrene and coronene), against 900–2,100 energies. If g is small, R2–R3 move from "not feasible" to "cluster-weeks". That makes M2a tonight the most consequential measurement in the plan's calendar, more than F.
4. **The extrapolated R3 factor is a placeholder**, printed so that the row exists; the pyrene timing (the cluster's first job in the Budget's order) replaces it.

## 5. Questions for the user before the table enters the proposal §12

1. Desktop = the hardware note's machine with the core-count estimate, labelled (e) — acceptable, or leave the desktop column out until it is timed?
2. Snellius column as days on **4 nodes in parallel** (with node-days derivable), or as node-days on one node?
3. Keep the R3 row with the extrapolated factor (clearly labelled), or print "not estimable until the pyrene timing"?
4. Include the side project (M2a as a row; M2 as software weeks, not compute) and the Module 05–08 "hours" rows, or only the coupled-cluster steps?
5. Show a second table variant with the reduced R2–R3 decks (family- and mode-selective scoring) once the pilot note defines them — or wait for the pilot note?
