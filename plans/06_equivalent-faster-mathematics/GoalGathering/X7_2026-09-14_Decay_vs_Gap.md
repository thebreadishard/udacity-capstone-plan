# X7 (run 2026-09-14 08:23) — the pair-energy decay length against the HOMO–LUMO gap, benzene → naphthalene → pyrene: **not lost, not confirmed**

*Pre-registered 12 September (Orientation §7; script header): for the three molecules, MP2/cc-pVDZ pair energies E_ij of Pipek–Mezey-localised valence occupied pairs against the distance of the orbital centroids; λ from a log-linear fit of the median |E_ij| per 0.5 Å shell beyond 1 Å (X3b's rule); the B3LYP/6-31G* HOMO–LUMO gap at the same geometry. The decay theorems (S1) predict a decay rate ∝ gap, i.e. λ·gap constant. **Losing condition, stated before the run: λ·gap varies by more than a factor 2 across the three.** Output `experiments/x7_decay_vs_gap.md/.json`; logs `x7_2026-09-14.log` (first run, invalid — see §3) and `x7_2026-09-14_rerun.log`.*

## 1. Result

| molecule | C | λ (Å) | B3LYP gap (eV) | HF gap (eV) | λ·gap_DFT | correlation beyond 3 Å | pair sum − E_corr (E_h) |
|---|---|---|---|---|---|---|---|
| benzene | 6 | 0.667 | 6.80 | 12.79 | 4.54 | 1.9 % | −2.6 × 10⁻¹⁵ |
| naphthalene | 10 | 0.702 | 4.83 | 10.23 | 3.39 | 3.8 % | 1.8 × 10⁻¹⁵ |
| pyrene | 16 | 0.750 | 3.84 | 8.67 | 2.88 | 5.5 % | 8.9 × 10⁻¹⁵ |

λ·gap max/min = **1.57** → the losing condition (> 2) is **not met**.

## 2. Reading

- **Not lost.** The rate-∝-gap statement survives its own falsification test: across a 44 % fall of the DFT gap the product λ·gap moves by a factor 1.57, under the pre-stated 2.
- **Not confirmed either.** Constant λ·gap would have λ rise by 77 % (6.80/3.84); it rises by 12 % (0.67 → 0.75 Å). The pair-energy decay length is, at this size range, nearly independent of the gap and of the molecule: ≈ 0.7 Å, a bond-fraction. The theorems give an upper bound on the decay rate's dependence on the gap; the data say the bound is far from tight here, and that the MP2 pair correlation is overwhelmingly nearest-neighbour: 2–6 % of the correlation energy lies beyond 3 Å.
- **Consistent with X6 and different from X9.** X6 (this morning) showed the ring-mode correlation curvature is whole-valence σ-dominated, not π; X7 says the same about the pair energies: short-ranged, σ-like. X9 and X12 measured a *different* object — the CC−DFT correction to the Hessian in the DFT–DFT stand-in — and found it longer-ranged than the mean field. The energy decays fast; its second derivative's difference between two methods does not have to, and X7 is not a test of X9.
- **For T3 (plan 06's gap conjecture):** the falsification did not fire, so T3 stays a conjecture with one more data point that neither supports nor contradicts its rate form; the 1 December review of the mathematics branch has it as "alive, weakly".

## 3. What went wrong first, and how the record stands

The first run (08:20) printed λ = 6.0 Å for benzene and −11.4 Å for naphthalene with pair sums 0.6–1.3 E_h off the MP2 correlation energy. Cause: the script rotated the canonical pair-energy *matrix* into the localised basis as if pair energies were bilinear in the occupied rotation; they are not (t2 and the integrals each carry two occupied indices). Fixed by rotating t2 and (ia|jb) to the localised occupied basis and forming E_ij there; the pair sum now equals E_corr to 10⁻¹⁵ E_h for all three molecules, which is the check that catches this class of error. A second, unrelated fix the same morning: pyscf 2.14's `mp.MP2` on a density-fitted mean field returns the DF variant whose integrals object carries `ovL`, not `ovov`; the conventional `RMP2` class is now forced. The invalid first log is kept beside the rerun.

## 4. Constants (from the run)

cc-pVDZ MP2, frozen core = number of carbons; Pipek–Mezey localisation of the valence occupied space; shells of 0.5 Å from 1.0 Å; far cut 3.0 Å; B3LYP/6-31G* gap at the same geometry; pyrene geometry from plan 02's stored B3LYP/6-31G* result (git 57a7910); benzene and naphthalene from plan 05's dry-run files.
