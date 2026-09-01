# Frozen ladder and tolerances — Plan 03

**Frozen date.** 2026-08-29.  
**Contradiction pass.** 2026-09-01. **Round-5 Pass A pass.** 2026-09-01 (second block below). Open OR-choices are now single defaults. Change only under Distilled Plan §4 with a dated note, committed *before* the affected quantity is measured. A later probe may force a §4 deviation; it may not reopen an OR, silently or otherwise, without that note.

## Contradiction pass 2026-09-01

These were mutually inconsistent in the 2026-08-29 draft. The 2026-09-01 default is the left-hand choice in each row. A later probe may force a §4 deviation; it may not reopen the OR without one.

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
| Effort “hours-to-days”, asserted | Caps live in [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md). No wall-clock is typed by hand. |
| P2 “200 teacher steps or 1 fs” | **P2 = 200 teacher steps.** 1 fs is a bonus report if it fits the teacher cap, not a second gate. |
| Learner \(k\) undeclared | **\(k=1\)**. |
| Conservation penalty “allowed” | **Off** until a dated pre-training note turns it on. |
| Kernel 3 or 5 | Default **3×3×3**. 5×5×5 is the Module 05 comparison axis, and promoting it to the thesis object after 3×3×3 is scored is a §4 deviation. |

## Round-5 Pass A pass 2026-09-01

Second correction block, from the first cold read of this plan
([Professor_Review_2026-09-01_Round5_PassA.md](Professor_Review_2026-09-01_Round5_PassA.md)). Same rule: these are now defaults, not open choices.

| Was | Now |
|---|---|
| State described as “twelve channels” while enumerating eleven | **11 channels.** The count is `len(grid_spec.CHANNEL_ORDER)`, and it is hashed into Q0. |
| Refinement “\(h(r)\sim a_0/Z\)” — which is \(1.0\,a_0\) at hydrogen, coarser than the outer grid | **\(h(r)\sim 0.20\,a_0/Z\)**, capped at the outer spacing. Refinement now refines on every promised rung. |
| P4 baseline periodic (`np.roll`), so \(N\) was conserved to round-off by construction and P0 passed on random noise | **Non-periodic**, matching the frozen finite box. P0 on the baseline is now a test that can fail. |
| Baseline Maxwell = forward Euler at \(c\,\Delta t/h = 34.26\) (59× the 3-D limit \(1/\sqrt{3}\)); reached NaN inside the P2 horizon | **Leapfrog + CFL sub-cycling**, 119 Maxwell sub-steps per teacher step. The teacher \(\Delta t\) and spacing are unchanged. |
| P0 on H₂O listed as a “Gate” here and as “report” in Distilled §7.2 | **Report only.** There is no numerical P0 gate on water. |
| P3 defined as a bare zero-shot measurement in the Goal and as “beat the baseline” here | **Both, always reported together.** See Distilled §7.2. |
| “Octopus (Andrade et al. 2020 family)” | **Tancogne-Dejean et al., J. Chem. Phys. 152, 124119 (2020)**, DOI 10.1063/1.5142502 (bibliography item 1). Andrade is a coauthor; “Andrade et al.” is a different 2015 paper. |

Teacher code for every promised rung: **Octopus** — Tancogne-Dejean et al., *J. Chem. Phys.* **152**, 124119 (2020), DOI 10.1063/1.5142502; bibliography item 1. (Do not write “Andrade et al. 2020”: he is a coauthor, and that string belongs to a different paper.) Input decks are hashed. NWChem is not the teacher. The dated freeze of remaining OR-choices is [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md).

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
| Spatial family | Real-space Cartesian, nuclear-refined by the rule \(h(r)\sim 0.20\,a_0/Z\) near nuclei, \(h\) capped at the outer spacing | No, except §4 probe-forced |
| Nominal outer spacing | \(0.20\,a_0\) (hash of generator + this number + box is Q0, Module 05) | No |
| \(\Delta t\) | Teacher \(0.05\) au. Learner \(k=1\) unless a dated note sets another integer \(k\) **before** training | Declare \(k\) before training |
| Box | Molecule + \(\ge 6\,a_0\) vacuum + absorbing rim if ionising. Finite, therefore **non-periodic**: learner padding and the P4 baseline match the rim | Hash |
| Plus channel | Frozen point nuclei; they source \(\mathbf{E}\) only. Do not deposit dynamical \(\rho_+\) and point charges in the same run | No |
| \(\mathbf{E},\mathbf{B}\) | Teacher Maxwell–TDDFT, hashed with the deck. Independent dynamical channels | Poisson reconstruction only under §4 |
| \(\mathbf{B}\) drop | Forbidden until a probe prints that \(\mathbf{B}\) is numerically zero on the ladder | §4 |

## Tests and tolerances (frozen before training)

| Test | Quantity | Gate (H₂) | H₂O transfer |
|---|---|---|---|
| P0 fixed point | \(\lvert N(t)-N(0)\rvert / N(0)\) after \(T_0=200\) field-free steps | \(< 10^{-3}\) | \(< 5\times 10^{-3}\), **report only** |
| P1 one-step | relative \(L^2\) on \(\rho_-\) | default \(< 5\times 10^{-3}\); 8 h pilot may only tighten | report only |
| P2 rollout | same, after \(T = 200\) teacher steps (\(k=1\); \(\approx 0.24\) fs) | \(< 5\times 10^{-2}\) or fail-closed | report only |
| P3 transfer | P1-style on H₂O, zero-shot | — | no numerical gate; report the error **and** the comparison — beat the linear baseline or say inconclusive |
| P4 baseline | learned vs linear stencil | declared \(\Delta\) in relative \(L^2\), 3 seeds | same |

Energy drift is reported. It is not a hidden extra gate. If P0 fails, P2 is not interpreted.

The frozen linear stencil is [`probes/linear_stencil.py`](../probes/linear_stencil.py): non-periodic, leapfrog Maxwell, CFL sub-cycled. Editing it after Q0 is a §4 deviation — it is the object P3 and P4 are scored against.

## Effect size

P4 effect size: Cohen-style difference of paired relative \(L^2\) across seeds. Pre-register “small / medium” after the 8 h pilot, in a committed dated note, and before any H₂ test or H₂O window is scored. The pilot runs on the train/validation slice only (Distilled §6.2), so the threshold is not set after seeing the comparison it governs.

## Split files

- Train windows and test windows are disjoint in **time**, then hashed.
- A second split by **kick protocol** (linear-response kick vs resonant pulse vs field-free) is hashed.
- H₂O is never in the H₂ training hash.
