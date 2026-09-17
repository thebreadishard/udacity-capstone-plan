# Two questions behind the cost: what accuracy is actually needed, and how many expensive labels (17 September 2026)

*Desk work, no computation. Sources are the plan's own frozen ladder and the paper the transfer-learning
gate rests on (`Papers/Kaeser_Meuwly_2021_transfer_learning_CCSDT_JCTC17_3687.pdf`).*

## 1. The 0.5 cm⁻¹ is not the project's goal. It is one yardstick's own uncertainty.

Traced to its source (`Frozen_Ladder_and_Tolerances.md`, decision 21, the user, 2026-09-08): Pirali et
al. 2009 gives sixteen gas-phase naphthalene fundamentals at 300 K and **0.005 cm⁻¹ resolution**, with
the Q-branch head resolved from its hot-band sequences. The 0.5 cm⁻¹ is the **head-to-origin term** — an
upper bound on the gap between the band head that is measured and the band origin that is computed, read
off Pirali's Figs. 3–6 and *explicitly labelled as an upper bound until a digitised spectrum can measure
it*. It is the noise floor of the comparison, not a specification of the deliverable.

**It also applies to exactly one molecule.** Across the rest of the ladder the reference resolution is
an order of magnitude looser:

| reference class | resolution term |
|---|---|
| Pirali 2009, naphthalene, gas 300 K, resolved fundamental | **0.5 cm⁻¹** (head-to-origin, upper bound) |
| Maltseva 2016, 3 µm, jet-cooled | ~1 cm⁻¹, **C–H stretch family only** |
| free-electron-laser band lists | **5–17 cm⁻¹** from the stated bandwidth alone |
| PAHdb-anharmonic's own published protocol | stick spectrum convolved with **1 cm⁻¹ FWHM** |

So for every molecule except naphthalene, an error of a few cm⁻¹ cannot be distinguished from the best
available measurement. The tightest bar in the plan sits on the one molecule where labels are cheapest.

**What this licenses, and what it does not.** It licenses asking, per rung, what the *verifiable* bar is
rather than carrying 0.5 cm⁻¹ everywhere by habit. It does **not** license dropping the couplings at the
larger molecules, for one reason that has not been tested: couplings move **intensity**, not just
position. Fermi resonances in the 3 µm region redistribute band strength, and spectral *shape* — the
deliverable in the goal sentence — depends on intensities as much as on positions. Stage C's diagonal-
only column is a statement about positions only.

**Pre-registered test, no new energies:** take the naphthalene dry run's direct Δ₂, build the spectrum
with and without the off-diagonal block, convolve both at 1, 5 and 13 cm⁻¹ FWHM, and compare the
convolved shapes (not the stick positions). If dropping the couplings changes the convolved shape by
less than the reference can distinguish at 5–13 cm⁻¹, the diagonal-only route becomes a licensed rung
for the large molecules and the cost question changes character. If it does not, the couplings are
needed for shape and this note settles nothing about them.

*Threshold fixed 17 September 18:3x, before any result existed (the dipole run was at 14 of 103
displacements):* intensities are harmonic, from the B3LYP/6-31G* dipole gradient computed by
`probes/dipole_derivatives.py`, rotated by the eigenvectors of ω² + Δ^Q (full) and ω² + diag(Δ^Q)
(diagonal-only); the score is max |S_full − S_diag| as a fraction of S_full's peak, per window
(2950–3150, 1100–1650, 700–950 cm⁻¹); **PASS if that fraction is below 5 % in every window at both
5 and 13 cm⁻¹ FWHM**; the 1 cm⁻¹ row is reported, not scored. Script: `probes/shape_test_couplings.py`.
Caveat stated in advance: the plan's anharmonic intensity step is not applied; this is the harmonic
intensity redistribution by mode mixing, which is the part the couplings control.

**Outcome, 17 September 19:1x — FAIL, split by region.** Dipole gradient from `dipole_derivatives.py`
(103 displacements, 2,705 s; the FINDIF Hessian reproduces stage A's H_low to 7.5e-5 E_h/bohr²). A
first pass used the experimental 3 µm window (2950–3150), which is empty at unscaled B3LYP/6-31G*
positions (the C–H stretches sit at 3190–3240); the window was moved to 3150–3300 and an empty-window
guard added before any verdict was recorded (ledger 19:06). Bands matched by eigenvector overlap, not
by sorted index, so shifts and intensity changes below are physical, not relabelling.

| window (harmonic positions) | bands | max shift | max intensity change (strong bands) | weakest overlap | 1 cm⁻¹ | **5 cm⁻¹** | **13 cm⁻¹** |
|---|---|---|---|---|---|---|---|
| C–H stretch, 3150–3300 | 8 | 0.01 | 11.5 % | 1.00 | 2.6 % | **1.6 %** | **1.4 %** |
| 6–9 µm, 1100–1650 | 13 | 21.4 cm⁻¹ | 28.1 % | 0.83 (band at 1182) | 95.6 % | **31.6 %** | **18.5 %** |
| C–H out-of-plane, 700–950 | 6 | 2.0 cm⁻¹ | 4.1 % | 0.99 | 76.7 % | **20.1 %** | **9.5 %** |

**Reading.** In the C–H stretch region the couplings do nothing the references can see (1.6 % and
1.4 % against the 5 % bar): there the diagonal-only route is licensed on shape, consistent with stage
C's 0.03 cm⁻¹ diagonal-only error for that family. In the fingerprint region they do a great deal: a
band at 1182 cm⁻¹ keeps only 83 % of its identity after mixing, positions move by up to 21 cm⁻¹ and
strong bands change intensity by up to 28 %, so the convolved shapes differ by 32 % of the peak at
5 cm⁻¹ and still 18.5 % at 13 cm⁻¹ — three to six times the bar, at the resolution of the loosest
reference on the ladder. The C–H out-of-plane region fails at 5 (20 %) and only just at 13 (9.5 %).
**Consequence for section 1 above: the looser tolerances above naphthalene do not rescue the
diagonal-only route.** Mode mixing moves intensity by tens of percent in the 6–9 µm region, and no
reference resolution hides that. The couplings are needed for spectral shape wherever the fingerprint
region matters — which for astronomical PAH bands (6.2, 7.7, 8.6, 11.2 µm) is everywhere except the
3 µm family. The only economy this test licenses is a **diagonal-only C–H stretch family**; the rest
goes to the gradient route. Caveats as pre-stated: DFT stand-in Δ₂, harmonic intensities, one molecule.

## 2. How many expensive labels the network needs: still unmeasured, and the literature is weaker than the plan implies

The architecture (ledger, §4 item 3) is the Käser/Bowman form: **pre-train on a cheap proxy of the
correction, fine-tune on the coupled-cluster labels**. The open number is how many CC labels the
fine-tuning needs.

**Why it cannot be measured today.** The proxy corpus is **6 of 11,321 molecules done** (layer A: 39
pending at ~1 h each). There is no pre-training set, so there is no fine-tuning curve to draw. The PAHdb
anharmonic library offers 45 species, but only **10** of them carry a matching entry in the theoretical
library, and at a different level of theory (B3LYP/N07D against RB3LYP) — too few, and not
method-consistent.

**What the cited paper actually shows.** Käser & Meuwly 2021 transfer-learn H₂CO from MP2 to CCSD(T)-F12
using **188 data points** (151 original plus 37 VPT2 geometries), tested on 3,450 held-out structures,
and reproduce the harmonic frequencies to within 0.3 cm⁻¹ (MAE 0.1). Two readings follow.

- **Encouraging on scale.** 188 high-level points per molecule is the same order as this plan's deck:
  291 energies, or 96 energies plus 18 gradients under the pattern-product route. Per molecule, the plan
  is buying roughly what the reference method needed.
- **Discouraging on ambition.** Those 188 points lift **one molecule's** potential surface. The datasets
  in that paper are generated per molecule and the results are reported per molecule. Plan 05 wants a
  network that generalises **across chemical space** — large PAH in, spectrum out — from a handful of
  expensive molecules. That is a stronger claim than the cited work demonstrates, and the plan's own
  predecessor already flagged this gate as "the one most likely to fail silently", noting that Käser
  reports VPT2 outliers up to 150 cm⁻¹ from surfaces whose energies and forces looked acceptable.

**Consequence.** The gap between "labels are affordable" (this week's work) and "enough labels to
generalise" (untested) is the largest remaining unknown in the plan, larger now than the cost questions
that have dominated the week. It is not answerable before the proxy corpus exists: **39 pending layer-A
molecules, about 40 hours of compute**, which is the cheapest path to the first real learning curve and
should be scheduled as such.
