# Frozen ladder and tolerances — Plan 03

**Frozen date.** 2026-08-29.  
**Contradiction pass.** 2026-09-01. Open OR-choices below are now single defaults. Change only under Distilled Plan §4 with a dated note.

## Contradiction pass 2026-09-01

These were mutually inconsistent in the 2026-08-29 draft. The 2026-09-01 default is the left-hand choice in each row. A later probe may force a §4 deviation; it may not silently reopen the OR.

| Was | Now |
|---|---|
| Plan called “complete as a plan” in the patch table | **Draft.** Completeness waits on a review. |
| H₂ teacher: 2-e exact *or* RT-TDDFT | **RT-TDDFT in Octopus**, ALDA, same grid family as H₂O. Exact 2-e is Horizon 10 / H-atom diagnostic only. |
| \(\mathbf{E},\mathbf{B}\): teacher Maxwell *or* Poisson reconstruction | **Teacher Maxwell–TDDFT.** \(\mathbf{E}\) and \(\mathbf{B}\) are dynamical channels, not a Poisson reconstruction of \(\rho\). Poisson is forbidden mid-study. |
| Plus channel: \(\rho_+\) on grid *or* point charges | **Frozen point nuclei.** They contribute to \(\mathbf{E}\) only. \(\rho_+\) on the grid is a bookkeeping channel of zeros plus optional nuclear smearing diagnostic, not a second dynamical species. |
| Outer spacing “0.15–0.25 \(a_0\), hashed in Module 02” | **0.20 \(a_0\)** outer spacing. Hash of generator + spacing + box lives in **Module 05 / Q0**, not Module 02. Module 02 is a public QM9 table and never sees a cube. |
| Distilled §4 “changing the grid after Module 02 is a deviation” | Changing the grid after **Q0 is hashed** is a deviation. Q0 is a Module 05 scientific-corpus gate. |
| P1 gate after an 8 h pilot; Module 08 had no number until then | Module 08 may quote the **default** P1 target \(< 5\times 10^{-3}\) relative \(L^2\) on \(\rho_-\) until a dated pilot note replaces it. The 8 h pilot may only **tighten**, never loosen, without a §4 note. |
| P3 “no numerical gate” | Still no absolute gate. Headline is **beat the frozen linear stencil or say inconclusive**. That is the P4 language on water, not a secret extra number. |
| Effort “hours-to-days”, asserted | Still asserted until `probes/` print a number. The 80 h grid+teacher cap stays. Do not type a wall-clock into markdown by hand. |

Teacher code for every promised rung: **Octopus** (Andrade et al. 2020 family). Input decks are hashed. NWChem is not the teacher.

## Molecule ladder

| Rung | System | Teacher | Role | Module 08 status |
|---|---|---|---|---|
| 0 | H atom | Analytic 1-e / exact grid TDSE | Sanity, P0, current identity | Required diagnostic |
| 1 | H₂ | Octopus RT-TDDFT, ALDA, frozen grid | Train + P0–P2 | **Promised** |
| 2 | H₂O | Octopus RT-TDDFT, ALDA, same grid family | P3 transfer | **Promised** |
| 3 | Small hydrides (optional) | Same teacher family | Robustness | Bonus |
| 4 | C₃₈₄H₄₈ | — | Scale story | Horizon 12 only |

If rung 1 teacher cannot be produced inside the 80 h grid+teacher cap, **stop**. Report the cap. Do not invent a coarser physics to keep the brand.

## Time and grid (frozen)

| Quantity | Frozen choice | May change? |
|---|---|---|
| Spatial family | Real-space Cartesian, nuclear-refined by the rule \(h(r)\sim a_0/Z\) near nuclei, \(h\) capped outside | No, except §4 probe-forced |
| Nominal outer spacing | \(0.20\,a_0\) (hash of generator + this number + box is Q0, Module 05) | No |
| \(\Delta t\) | Teacher \(0.05\) au. Learner \(k=1\) unless a dated note sets another integer \(k\) **before** training | Declare \(k\) before training |
| Box | Molecule + \(\ge 6\,a_0\) vacuum + absorbing rim if ionising | Hash |
| Plus channel | Frozen point nuclei; they source \(\mathbf{E}\) only. Do not deposit dynamical \(\rho_+\) and point charges in the same run | No |
| \(\mathbf{E},\mathbf{B}\) | Teacher Maxwell–TDDFT, hashed with the deck. Independent dynamical channels | Poisson reconstruction only under §4 |
| \(\mathbf{B}\) drop | Forbidden until a probe prints that \(\mathbf{B}\) is numerically zero on the ladder | §4 |

## Tests and tolerances (frozen before training)

| Test | Quantity | Gate (H₂) | Gate (H₂O transfer) |
|---|---|---|---|
| P0 fixed point | \(\lvert N(t)-N(0)\rvert / N(0)\) after \(T_0\) | \(< 10^{-3}\) | \(< 5\times 10^{-3}\) |
| P1 one-step | relative \(L^2\) on \(\rho_-\) | pre-register after a 8 h pilot; default target \(< 5\times 10^{-3}\) | report only |
| P2 rollout | same, after \(T = 200\) teacher steps or 1 fs, whichever is declared | \(< 5\times 10^{-2}\) or fail-closed | report only |
| P3 transfer | P1-style on H₂O, zero-shot | — | no numerical gate; beat linear baseline or say inconclusive |
| P4 baseline | learned vs linear stencil | declared \(\Delta\) in relative \(L^2\), 3 seeds | same |

Energy drift is reported. It is not a hidden extra gate. If P0 fails, P2 is not interpreted.

## Effect size

P4 effect size: Cohen-style difference of paired relative \(L^2\) across seeds. Pre-register “small / medium” after the 8 h pilot, not after the test.

## Split files

- Train windows and test windows are disjoint in **time**, then hashed.
- A second split by **kick protocol** (linear-response kick vs resonant pulse vs field-free) is hashed.
- H₂O is never in the H₂ training hash.
