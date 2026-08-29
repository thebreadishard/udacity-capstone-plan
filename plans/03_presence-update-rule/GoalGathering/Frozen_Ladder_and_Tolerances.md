# Frozen ladder and tolerances — Plan 03

**Frozen date.** 2026-08-29.  
Change only under Distilled Plan §4 with a dated note.

## Molecule ladder

| Rung | System | Teacher | Role | Module 08 status |
|---|---|---|---|---|
| 0 | H atom | Analytic 1-e / exact grid TDSE | Sanity, P0, current identity | Required diagnostic |
| 1 | H₂ | Declared: 2-e exact *or* RT-TDDFT; if TDDFT, name functional + grid | Train + P0–P2 | **Promised** |
| 2 | H₂O | RT-TDDFT, same grid family as H₂ | P3 transfer | **Promised** |
| 3 | Small hydrides (optional) | Same teacher family | Robustness | Bonus |
| 4 | C₃₈₄H₄₈ | — | Scale story | Horizon 12 only |

If rung 1 teacher cannot be produced inside the 80 h grid+teacher cap, **stop**. Report the cap. Do not invent a coarser physics to keep the brand.

## Time and grid (frozen)

| Quantity | Frozen choice | May change? |
|---|---|---|
| Spatial family | Real-space Cartesian, nuclear-refined by the rule \(h(r)\sim a_0/Z\) near nuclei, \(h\) capped outside | No, except §4 probe-forced |
| Nominal outer spacing | 0.15–0.25 \(a_0\) (exact number hashed in Module 02) | No |
| \(\Delta t\) | \(\le 0.05\) au for teacher; learner may take \(k\Delta t\) if declared | Declare \(k\) before training |
| Box | Molecule + \(\ge 6\,a_0\) vacuum + absorbing rim if ionising | Hash |
| Plus channel | Nuclear charge deposited on grid *or* frozen point charges contributing only to \(\mathbf{E}\) | Declare one; do not mix mid-study |

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
