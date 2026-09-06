# Probed coupled-cluster corrections to the harmonic force constants of polycyclic aromatic hydrocarbons: an infrared pipeline with a measured cost

**Master's capstone project proposal — plan 05.** Prepared for supervision review, 6 September
2026. Earlier drafts (3 and 4 September) are in the repository's history; this text supersedes
them and stands on its own. Every number in it that describes this project's own performance was
printed by a script in the folder `probes/` and can be re-run; numbers from the literature are
marked as such. A note on provenance and on the terms used follows the summary.

---

## 1. Summary

Infrared band positions of polycyclic aromatic hydrocarbons (PAHs) underpin the interpretation of
the aromatic infrared bands JWST now resolves. The reference predictions — most prominently the
NASA Ames PAH IR Spectroscopic Database (PAHdb) — rest on scaled harmonic DFT, whose systematic
uncertainties its own current paper calls "currently unquantified" (Ricca et al. 2026). This
project builds and tests one pipeline: any individual neutral aromatic molecule in, an infrared
absorption spectrum out, with the **harmonic force constants corrected by a local coupled-cluster
anchor, checked against canonical coupled cluster where affordable**, and a measured error budget
on every claimed band.

The previous plan (plan 04, discussed at the last supervision meeting) obtained its
coupled-cluster anchor by learning a per-molecule potential-energy surface from thousands of local
coupled-cluster points; its review accepted the criterion and found the cost unaffordable at the
sizes that matter. Plan 05 keeps that plan's success criterion, its baseline predictions, its
laboratory scoreboards and its reporting rules, and replaces one thing: instead of learning a
surface, it **probes the difference** between the local coupled-cluster and DFT force constants —
a small, smooth quantity — with a set of simultaneous multi-atom displacements taken in a
pre-fixed order, and recovers that difference in the DFT normal-mode basis under a prior that
molecular symmetry supplies for free. The number of coupled-cluster energies each molecule needed
is measured and reported beside its spectrum. Whether that number stops growing with molecule
size is a pre-registered measurement with a stated losing condition, not a claim.

Three measurements and one literature search have been made since the plan was written, all in
the first week, all on the student's laptop. A DFT-only rehearsal of the probing machinery (a
difference between two DFT functionals standing in for the coupled-cluster correction) recovered
a full force-constant correction at benzene and showed where the couplings really are. The frozen
correlation spaces on which the whole design rests were measured to be smooth: their energy
scatters by 0.002–0.06 µE_h along a displaced mode, where the same local-CC program re-selecting
its spaces at every geometry scatters by 7–11 µE_h at its default settings and 0.05–2.7 µE_h at
tight ones. And the canonical coupled-cluster reference that licenses the anchor was timed: it
fits the laptop at benzene for the line that matters, and the full canonical Hessian does not.
The search found no room-temperature gas-phase spectrum of the pyrene-size molecules in the
6–15 µm region, which fixes what that rung can and cannot decide.

The pipeline outputs the whole spectral shape for every molecule — position, intensity, drawn
width — and the plan is explicit about which of those it scores and which it promises: positions
are promised and scored wherever a laboratory band can decide the comparison; intensities are
scored on the two molecules where a calibrated gas-phase intensity exists (benzene, naphthalene)
and reported with their provenance everywhere else; widths are drawn, not predicted.

The success criterion is relative and measured: on small and medium PAHs the pipeline's band
positions are compared per band against named, version-frozen state-of-the-art predictions under
a pre-registered protocol; on the largest species the deliverable is a spectrum with a labelled
error budget and no accuracy claim. The project is as much about the evaluation discipline —
pre-registration, frozen baselines, mandatory null tests, fail-closed reporting — as about the
spectra themselves.

### Provenance, reviews, and the words this document uses

*Reviews.* The plan was put through eight review passes on 3 and 4 September: four "cold reads"
by a reader who saw only the documents and a brief, and four adversarial domain reviews with
literature access. **These were performed by an AI assistant (Claude), each pass in a fresh
session that had not seen the author's reasoning; they are a disciplined self-review with an
outside vocabulary, not human peer review.** Every finding and its closure is on file in the
folder. This document itself was cold-read the same way on 6 September before being sent.

*What was carried from plan 04.* The success criterion (per-band comparison against the best
existing prediction, decided by laboratory data); the baseline predictions ("opponents", §7); the
laboratory scoreboards; the leakage rules; the fail-closed reporting; the six-step size ladder;
the ban on scale factors on anharmonic output. Plans 01–03 preceded plan 04 and are referred to
once (§11, risk 7) for a lesson learned.

*Terms.* A **rung** is one step of the size ladder (§5.2). **Δ₂** is the correction to the
harmonic force-constant matrix, expressed in the DFT normal-mode basis; its **diagonal** entries
correct each mode's own frequency, its **off-diagonal** entries the couplings between modes. The
**energy route** obtains Δ₂ from coupled-cluster energies at displaced geometries; the
**gradient route**, if the side project of §5.3 delivers it, from gradients. The **deck** is the
ordered list of displacement patterns for a molecule; it is **hashed**, meaning its order is
fixed by a seeded function before any energy is computed, so nobody can reorder the patterns
after seeing a result. **K** is the number of coupled-cluster energies a molecule needed; **K_off**
the part of it spent on the off-diagonal block. The **pilot note** is a dated document, written
before the first real coupled-cluster correction is computed, that fixes every tolerance, margin
and constant the evaluation uses. A **beat margin** is the pre-registered minimum per-band
improvement over the best opponent that counts as a win. Numbered **decisions** are the student's
recorded choices (§10). The **campaign officer** (Module 07) is a rule-checking agent that reads
the deck, the budget file and the pilot note, submits and refuses computational jobs and report
sentences by those rules, and never produces or edits a scientific number.

## 2. Why the coupled-cluster budget moves from the surface to the correction

Three considerations, two from this project's own history and one from the literature, drove
the change.

First, the arithmetic of plan 04. Coronene has 102 vibrational coordinates; a learned surface
over them needs, by the estimate in the plan-04 design notes, of order 10⁴ local coupled-cluster
points — thousands of node-hours per molecule, on an allocation that does not exist. The plan-04
review made this a blocking finding.

Second, what a coupled-cluster anchor actually adds. Almost all of a PAH's potential-energy
surface is already described at DFT quality. The only new information the expensive method
supplies is the *difference* between the two surfaces, and near equilibrium that difference is
small and smooth. Paying coupled-cluster prices to relearn the DFT part is where plan 04's cost
went.

Third, where the difference pays. The hybrid quartic-force-field literature (Boese, Klopper &
Martin 2005; Bégué, Carbonnière & Pouchan 2005; and, on naphthalene, Esposito et al. 2024) puts the
coupled-cluster level in the **harmonic** constants and leaves cubic and quartic constants at DFT
level. Plan 04 had it the other way round. Plan 05 corrects the harmonic force constants only —
Δ₂ — and lets DFT supply the anharmonic constants. The domain review sharpened this further:
energy-only probing cannot produce the three-index cubic constants that PAH combination-band
resonances need, so a coupled-cluster anharmonic correction was not merely unnecessary but
unbuildable with the probes specified. It was removed from the promised set. A cheap by-product
remains and is reported: the single-mode patterns are run at two amplitudes (§3.4), which yields
each mode's diagonal cubic correction for free — a number that will show how much was given up,
not a correction that is applied.

## 3. How the correction is recovered, and why in this form

### 3.1 Prior art and what is new

Two published methods recover a *full* Hessian from far fewer calculations than one per
coordinate by exploiting its structure: O1NumHess (Wang et al. 2025), which recovers a Hessian
from a number of gradients that levels off near a hundred in the authors' data for molecules of
hundreds of atoms, and compressed-sensing recovery in a cheap method's eigenbasis (Sanders,
Andrade & Aspuru-Guzik 2015), which on anthracene needed 30 % of the Hessian columns and whose
cost grew only logarithmically across polyacenes of one to fifteen rings. Neither has been
applied to a coupled-cluster-minus-DFT difference.

The domain review established that the *diagonal* part of this idea is not new: the Concordant
Mode Approach (Lahm et al. 2022; Kitzmiller et al. 2024) computes CCSD(T) force constants along
DFT normal modes from single-point energies and adds selected off-diagonal elements by a cheap
diagnostic. It is cited as prior art throughout the plan, and its own result — that diagonal-only
recovery fails on aromatic ring modes by up to ±28 cm⁻¹, because DFT and coupled-cluster mode
compositions differ there — is the strongest evidence for the plan's design choices. What plan 05
proposes beyond CMA: local coupled cluster with frozen correlation spaces at PAH sizes; the
off-diagonal block recovered from multi-mode patterns by a **symmetry-blocked** solve of a
*difference* Hessian, rather than one element at a time; the recovery licensed against directly
computed references; and the locality of the correction, and the number of off-diagonal probes it
needs, measured as a function of size.

**What is new, and what is not — stated plainly.** A literature search on 6 September 2026 (eight
queries; recorded in the working bibliography) found each ingredient of the plan in print and no
work that combines them:

| Ingredient | Nearest published work | What plan 05 does differently |
|---|---|---|
| coupled-cluster force constants along DFT normal modes from energies; selected off-diagonals; symmetry-forbidden couplings zeroed in the full matrix | Concordant Mode Approach (Lahm et al. 2022; Kitzmiller et al. 2024; Olive Dornshuld et al. 2026, read in full: 17 intermolecular complexes, MP2/haTZ modes, CMA-2A converges with 3 % of the off-diagonals; its persistent benzene outlier is one same-representation ring-deformation coupling, the same phenomenon our rehearsal found) | the target is the *difference* Δ₂, not the CC force constants; the off-diagonal block is recovered as a whole from multi-mode patterns, not element by element; symmetry used as the recovery prior rather than as a clean-up; local rather than canonical coupled cluster, at PAH sizes |
| recovering a Hessian from few measurements by exploiting its structure | compressed sensing in a cheap method's eigenbasis (Sanders et al. 2015); O1NumHess (Wang et al. 2025) | applied to a difference Hessian rather than a full one; the prior is the molecule's symmetry, parameter-free, instead of generic sparsity; the probe count is a measured, pre-registered quantity |
| correcting DFT towards CCSD(T) by learning the difference | Δ-machine learning of potential-energy surfaces (e.g. Bowman and co-workers, 2024; transfer learning to CCSD(T), Käser & Meuwly 2021) | nothing is learned per molecule; the difference is measured; a learned model is a possible follow-up gated by the measured range (§6) |
| local-correlation spaces held fixed for numerical derivatives | fixed domains for DLPNO-MP2 numerical derivatives (ORCA); the discontinuity problem itself (Madriaga & Crawford 2025) | frozen LNO-CCSD(T) fragment spaces transported by projection across displaced geometries, semicanonicalised, with the smoothness and bias measured against canonical CCSD(T) — no publication found that does this or measures it |
| scaled or ML-corrected harmonic DFT for PAH spectra | PAHdb (Ricca et al. 2026); Ethereal AI (Bos et al. 2025) | these are the opponents; the plan adds a measured coupled-cluster correction and an error budget per band |

The claim of novelty is therefore the combination and its measurement discipline, not any single
ingredient; the plan's own name for the object is "a symmetry-blocked recovery of a difference
Hessian with a frozen local-CC anchor".

### 3.2 The prior: symmetry, not a frequency band

The plan's first draft regularised the recovery with a frequency band: couplings between modes
close in frequency were left free, distant ones were penalised. The DFT-only rehearsal at benzene
(5 September; §8) showed that this is not where the structure is. In the rehearsal the
"correction" is a **surrogate**: the difference between two functionals, B3LYP and BHHLYP in the
6-31G* basis, chosen to bracket the amount of exact exchange; nothing coupled-cluster has been
computed yet, and every statement in this subsection is about that surrogate. Its large
off-diagonal elements couple modes 170–450 cm⁻¹ apart — the strongest pair at 1186 and 1357 cm⁻¹
(B3LYP/6-31G* harmonic values) — and every one of them lies within a single irreducible
representation of the molecule's point group. The band did not select them; the recovery worked
because the two-mode patterns in the deck isolated them and the fitted penalty was weak.

The prior is therefore now what symmetry gives for free (decision 11): couplings between modes of
**different** irreducible representations are fixed at zero — exact, not assumed — and couplings
within one representation are free whatever their frequency distance. A sparsity penalty remains
only where the free-element count exceeds what the rung's probe cap can determine. This prior has
no parameters, cannot distort the truth on a symmetric molecule, and enters the deck after the
naphthalene rehearsal reproduces the direct surrogate correction with it; until that rehearsal has
printed, the banded rule stands as the fallback. It also sets the cost expectation (decision 13):
without a prior the off-diagonal block costs about M(M−1)/2 energies for M modes — the benzene
rehearsal needed 388 off-diagonal energies for 435 unknowns (§8), so sparsity as such saved
nothing — and with the symmetry prior naphthalene has **141** same-representation couplings
instead of 1,128 (from the textbook D₂h assignment of its 48 modes, 9a_g + 3b_1g + 4b_2g + 8b_3g +
4a_u + 8b_1u + 8b_2u + 4b_3u). The representation of each mode is determined by the deck's own
symmetry analysis in the molecule's **full** point group: DFT programs run in Abelian subgroups
(benzene in D₂h, where its degenerate modes split artificially — Esposito et al. 2024 note the
same), and their labels would leave far more couplings free than symmetry does. Zeroing
symmetry-forbidden couplings is itself standard practice — the Concordant Mode Approach does it
as a clean-up of its full high-level matrix — what is new here is using it as the prior of a
recovery from few measurements. The arithmetic, at benzene's measured per-energy time of 35 minutes in the anchor basis
(naphthalene's will be longer and is measured before the note): 48 modes × 4 diagonal energies
plus about 0.9 energies per allowed coupling plus the held-out fraction is of order 350–400
energies, i.e. 200–250 hours — a few weeks of unattended laptop time, classified by the 168-hour
rule of §8 once the naphthalene time is known — against about 1,400 energies and 800+ hours
without the prior. The prior is what brings the energy route at naphthalene within reach of this
machine at all; it does not make it cheap.

### 3.3 Frozen correlation spaces — the object, now measured

The local coupled-cluster program is **LNO-CCSD(T) as implemented in pyscf-forge 1.1.1 on PySCF
2.14.0** (local natural orbitals; one fragment per localised occupied orbital; a CCSD(T) solve in
each fragment's truncated orbital space). At displaced geometries the plan computes its energies
with those fragment spaces **frozen at the equilibrium geometry** and transported to each
displaced geometry by projection and orthonormalisation — nothing is re-localised or re-selected —
because space changes on displacement produce micro-hartree discontinuities, the same mechanism
Madriaga & Crawford (2025) showed destroys finite-difference field properties even with fixed
PNO dimensions. The domain review made the smoothness of the frozen space the first measurement
of the plan. It has now been made (probe M1, the plan's first numbered measurement, 5–6
September; all numbers below are from the corrected run described at the end of this
subsection):

- *Design.* Benzene, cc-pVDZ, three normal modes — the totally symmetric ring mode at 1020 cm⁻¹;
  a non-degenerate C–C stretch at 1357 cm⁻¹, which belongs to the same irreducible representation
  as the 1186 cm⁻¹ mode it couples to in §3.2; and one component of a degenerate C–H out-of-plane
  pair at 865 cm⁻¹ (B3LYP/6-31G* harmonic values; the degenerate partner sits at the same
  frequency) — at nine displacements each; three arms at every geometry:
  **A**, the frozen spaces transported from equilibrium; **B**, the equilibrium localised orbitals
  transported but the fragment spaces re-selected; **C**, everything re-selected (the program as
  released). Two settings of the program's truncation thresholds ("default" and "tight"). A
  canonical CCSD(T) energy at each of the 27 geometries as the truth line.
- *Smoothness.* Against that truth line, arm A's energy scatters about a smooth curve by
  **0.002–0.06 µE_h** on the three modes at either threshold setting; arm C by 7–11 µE_h at
  default and 0.05–2.7 µE_h at tight thresholds, arm B in between. The requirement the couplings
  impose (§3.4) is about 2 µE_h; arm A meets it by a factor of 30 to 1,000 depending on the mode.
- *Bias.* The frozen space was chosen at equilibrium and fits a displaced geometry slightly less
  well; that bias is a clean quadratic in the displacement, i.e. exactly a curvature bias, and it
  shrinks with the truncation threshold: 5–28 cm⁻¹ on the bare local energy at default
  thresholds; **0.5–2.6 cm⁻¹** on the composite energy — the local energy plus the standard
  second-order correction for the truncated space, [MP2(full) − MP2(local)] — at default
  thresholds; **0.03–0.36 cm⁻¹** on the composite at tight thresholds. The pipeline's anchor runs
  at tight thresholds; the threshold-sensitivity line of §7 decides, per rung, whether that is
  enough or extrapolation in the truncation thresholds is required.
- *Reload.* Arm A reproduces the equilibrium-geometry energy exactly and reloads its spaces from
  file exactly (to 10⁻⁴ µE_h), which is the property the pipeline depends on.
- *Arbitrariness made visible.* Two runs at the same displaced geometry landed the fresh
  localiser on different, symmetry-equivalent orbital sets (overlap between the two landings
  0.67), while the transported set stayed put; on benzene the two landings cost nothing, on a
  molecule of lower symmetry they would not be equivalent. This is the effect the domain review
  asked about and the reason the plan transports rather than re-localises.
- *Anchor basis.* The same scan at cc-pVTZ, the basis the licence rungs use — the three arms at
  tight thresholds, 27 geometries, then the canonical truth line — is running as this is written
  (about two hours per geometry for the three arms; results Tuesday 8 September). The basis is larger and
  the frozen space a smaller fraction of it; the cc-pVDZ bias is expected to be a lower bound, and
  the scan will say.
- *A definition fixed by the measurement.* The transported orbital blocks must be
  semicanonicalised at each geometry — a rotation inside the frozen space that the fragment
  solver's MP2 start and (T) step assume; a first run without that step read a spurious bias of
  up to 147 cm⁻¹ and is kept on file as the record of the error (decisions 14, 15).

### 3.4 The stopping rule and the probe count

The deck is consumed in its hashed order, so the reported probe count K is a measurement and not
a choice. K is the number of energies at which the recovery's **held-out residual** first falls
below a threshold; the residual is the root-mean-square difference between the responses that
were withheld from the fit and the responses the recovered Δ₂ predicts for them, divided by the
root-mean-square of the withheld responses — dimensionless, 1 for no recovery, 0 for a perfect
one. The rehearsal changed that threshold in two ways (decisions 8, 9, 12),
**before any real coupled-cluster response exists**, so nothing was tuned on a result the rule
will later judge. The residual is computed on the **off-diagonal part** of the responses: the
diagonal correction is known after the first block of single-mode patterns and dominates every
response (97.6 % of the response's root-mean-square at benzene), so a residual on the raw response
read "done" while the couplings were still unknown. And the threshold carries a **model floor**:
a quadratic model cannot fit the quartic content of the surface below a printed residual (0.20 on
the off-diagonal scale at benzene), so at low noise the old rule was unreachable and would have
run every rung to its probe cap; the threshold is now the larger of that floor and a multiple of
the rung's own measured noise, the multiple fixed in the pilot note. The single-mode patterns are
run at two amplitudes; the pair identifies the shared reference energy's offset and the diagonal
cubic term of §2 without fitting either.

The noise the couplings can tolerate is measured per rung from the off-diagonal signal (decision
10): at benzene the requirement is about 2 µE_h per energy, ten times stricter than the 19 µE_h
the diagonal alone would tolerate at a 5 cm⁻¹ tolerance, and the frozen spaces meet it (§3.3). If
a larger molecule did not, the plan says in advance what happens: the off-diagonal block for that
rung is reported at its noise-limited precision and carries no accuracy claim, and the gradient
route of §5.3 takes over the couplings if the side project has delivered it by then.

## 4. Research questions

**Accuracy (benzene to coronene).** Can a per-molecule pipeline — DFT geometry, harmonic Hessian
and anharmonic constants, plus a probed coupled-cluster correction to the harmonic force
constants — produce band positions that measurably improve on scaled-harmonic DFT (PAHdb), on an
in-house calibrated-harmonic baseline, and, where its coverage overlaps, on the published
DFT-based machine-learning molecular dynamics of Mai et al. 2025, judged per band against
laboratory spectra? And, on the two molecules where the laboratory intensity is calibrated, do its
anharmonic intensities improve on the harmonic ones?

**Cost (every rung that ran).** How many coupled-cluster energies did that correction need per
molecule, and how did the off-diagonal count grow between naphthalene, the pyrene-size rung and
coronene — measured against the number of couplings the molecule's symmetry leaves free?

**Reach (C₃₈₄H₄₈-class).** Can the same pipeline produce a spectrum with a stated error budget at
a size where no anharmonic or coupled-cluster-quality prediction — and no laboratory spectrum —
exists? Here no "beat" is claimed, and the plan is explicit about a hard limit: whole-molecule
probing of a 432-atom molecule with energies only costs at least two energies per vibrational
mode — 2,580 coupled-cluster energies of a very large molecule — and is not attempted. The only
route by which that cost stops depending on size is to probe the correction on capped fragments
of the flake, which uses a locality-verified electronic correction obtained on one region for
another. The student ruled (decision 1) that this is not a scope question but a method: if it
works and the goal is reached with it, it is used; if the locality measurement at the middle
rungs says it does not, it is not. The largest species remains a promised deliverable in this
sense: a fragment-probed spectrum, or the measured reason none could be produced.

## 5. Approach

### 5.1 The pipeline, per molecule

1. **Geometry, harmonic Hessian and dipole first and second derivatives** at the pipeline's DFT
   level, analytic, on the student's laptop's CPU through coronene (it has no CUDA GPU; any GPU
   work is rented time); DFT cubic and semi-diagonal quartic constants for the scored band
   families and every mode the resonance search couples to them. **The production DFT level
   (functional, dispersion correction, basis set, integration grid) is a pre-registered constant
   that is not yet chosen**: it is fixed, from the opponents' levels and the anharmonic
   literature (the PAHdb-anharmonic standard is B3LYP/N07D with a 200 × 974 integration grid,
   Esposito et al. 2024; the CMA studies find basis quality to matter more than correlation level
   for the normal-mode basis; aug-cc-pVTZ is excluded for benzene-type rings by a documented
   linear-dependence artefact), before the naphthalene rehearsal runs, so that the rehearsal constants the stopping
   rule uses (§3.4) and the noise-injected column of the pilot note are read at the production
   level; the benzene rehearsal so far used B3LYP/6-31G* against BHHLYP/6-31G*, and the Module-05
   corpus uses B3LYP. The choice is recorded in the pilot note with its reasons.
2. **Δ₂-probing.** The deck of displacement patterns; at each, the composite local
   coupled-cluster energy in the frozen spaces of §3.3 and the DFT energy; recovery of Δ₂ in the
   DFT normal-mode basis under the symmetry prior of §3.2; K read by the stopping rule of §3.4.
   Three licences gate it: an **anchor licence** against the noise, bias and threshold-sensitivity
   formulas fixed in the pilot note (§7); a **probing licence** at benzene and naphthalene against directly computed reference
   corrections (at benzene including a canonical coupled-cluster reference, the only one
   independent of the space freezing); and a **locality test** computed on directly measured
   Hessian blocks — never on the recovered correction alone, which could certify the locality its
   own prior imposed. Modes that are infrared-inactive by symmetry are not dropped — their
   diagonal is cheap and their fundamentals reach the spectrum through
   resonances — but the coupling blocks made only of inactive modes are tested per rung in the
   DFT rehearsal and left out of the deck only where the scored positions do not move (decision
   19). (Each mode's diagonal costs four energies: a ± pair at each of two amplitudes, §3.4.)
3. **Spectra** by second-order vibrational perturbation theory with explicit resonance
   treatment (GVPT2; the implementation is pinned in the pilot note as a pre-registered constant,
   with named resonance thresholds and a polyad cap; from the pyrene-size rung upward the
   anharmonic constants are built in reduced dimensionality — Hessians differentiated only along
   the scored modes and the partners a dimensionless coupling indicator and the Darling–Dennison
   test select, after Fusè et al. 2024, whose thresholds are pilot-note candidates — on the DFT anharmonic
   constants and the Δ₂-corrected harmonic part, plus a first-order geometry term: the corrected
   surface's own minimum shifts slightly from the DFT one, and that shift is applied and printed
   on every scored band); **no scale factor** on anharmonic output. Every spectrum carries
   positions, anharmonic intensities from the DFT dipole derivatives (the same physics PAHdb's
   intensities rest on, computed anharmonically rather than harmonically) and a drawn width at
   the resolution and temperature of the source it is compared with, each labelled with its
   provenance.
4. **Error budget** per band: DFT level, held-out residual, measured noise and space-freezing
   bias, the share of the family's correction that comes from couplings beyond the locality
   test's radius, and the matrix–gas shift where matrix data is used.

### 5.2 The size ladder (species and claim types unchanged from plan 04)

| Rung | Species | Type | What it licenses in plan 05 |
|---|---|---|---|
| R0 | benzene | accuracy | probing licence against local and canonical references; the anchor's bias line (canonical reference); intensity scored |
| R1 | naphthalene | accuracy | the noise measurement; the anchor licence closes; first locality read; intensity scored |
| R2 | pyrene, chrysene, triphenylene, tetracene | accuracy (C–H families; C–C families expected undecidable on the existing gas data, see below) | first off-diagonal-count ratio; direct-block locality probe; a canonical diagonal check at pyrene (expected cluster work; classified by the rule of §8, and skipped with a printed sentence if no cluster time exists) |
| R3 | coronene | accuracy | second ratio; the numeric size sentence is decided here |
| R4–R5 | C₅₄–C₂₁₆ class | reach; the R4 fragment checks conditional on cluster access | expert-judgment datum (§13.5); the first rungs where the learned prior, if it earned its licence at R2–R3, may carry the recovery; the fragment-vs-whole comparison on a molecule larger than coronene and the fragment-radius convergence test |
| R6 | C₃₈₄H₄₈-class | reach | fragment-probed only, under a four-part measured licence (locality at R2–R3; coronene probed in fragments reproducing coronene probed whole; the same on a larger molecule where the cluster allows; a fragment-radius convergence test on the flake's own interior); otherwise a per-family or full refusal |

*Laboratory sources per rung.* Benzene: the NIST Quantitative Infrared Database cell spectra (Chu
et al. 1999), with calibrated intensities. Naphthalene: the PNNL quantitative vapour-phase record
at 25 °C and 0.1 cm⁻¹ (Schneider et al. 2024, in the database described by Sharpe et al. 2004),
with calibrated intensities; the hot NIST WebBook entries as labelled extra columns; Pirali et al.
2009 and Joblin et al. 1995 for the temperature term. Pyrene, chrysene, triphenylene: NIST WebBook hot-vapour GC-IR
spectra at 8 cm⁻¹ without concentration data. Tetracene: matrix isolation, plus a jet-cooled band
list (Lemmens et al. 2019). Coronene: matrix isolation, plus five jet-cooled 6–15 µm bands
(Lemmens, Rijs & Buma 2021).

A per-family decidability rule replaces plan 04's rung-level gate: a gas-scored family is
decidable if the scoreboard's **measured band-centre uncertainty** — instrument resolution,
centroid precision and a temperature term — is smaller than its beat margin; a matrix-scored
family passes through the matrix–gas gate or is pre-declared inconclusive. Benzene and
naphthalene are therefore scored unconditionally on room-temperature cell spectra. For the
pyrene-size rung, a systematic search on 5 September (NIST WebBook, the PNNL database, PAHdb's
experimental library, and journal searches on jet-cooled and cell spectroscopy of each species)
found no room-temperature gas-phase spectrum of pyrene, chrysene or triphenylene in the 6–15 µm
region; it found the two jet-cooled lists above and one rotationally resolved cold pyrene band
(Brumfield, Stewart & McCall 2012), all now named as labelled cold columns. The C–C stretching
families at R2 are therefore expected to be undecidable by construction (they carry the largest
temperature shifts and the smallest beat margins, so the unknown vapour temperature swamps them;
the strong, isolated C–H out-of-plane bands shift least and keep a usable margin); the plan says so
before
any number exists, and the student has decided to sign off the scoreboard module with that
expected result rather than wait for a source that may not exist (decision 3, addition of 5
September). §13 still asks.

### 5.3 Why the cost is reported in numbers and never in adjectives; the gradient side project

The plan allows exactly two kinds of cost sentence. The **cost record** — K and K_off, route,
prior, measured noise and stopping threshold, wall-clock per probe, the script that printed it —
is promised for every rung that ran. A **size sentence** is numeric only: how K_off went from
naphthalene to coronene against how the mode count went and against the free-element count
symmetry leaves. The adjectives "size-independent", "O(1)" and "saturates" are forbidden in any
sentence about this project's own cost. **The losing condition of the size question:** if K_off
grows from naphthalene to coronene at least as fast as the count of symmetry-allowed couplings,
no size sentence is earned and the cost records stand alone. Any favourable size sentence is
expected, if at all, to come from the prior — symmetry or learned — and not from sparsity as
such.

The domain review's reading of the software landscape stands: no production code offers an
analytic nuclear gradient for local CCSD(T), and the project's own measurement shows why the
canonical one is no substitute (§8). The student's response was not to accept that as a limit
but to build it: a pre-registered **side project** extends the open PySCFAD implementation of
LNO-CCSD(T) gradients by automatic differentiation (Zhang et al. 2024; demonstrated by its
authors to about 29 atoms) to frozen correlation spaces and PAH sizes. Two arguments, to be tested
by its first milestone, make this engineering rather than new theory: on a surface with frozen
spaces an automatic-differentiation gradient with fixed spaces is the derivative of the surface
actually probed, so the response terms that make general local-CC gradients hard should not
arise; and the fragment structure of the local method should let the memory of reverse-mode
differentiation scale with the largest fragment rather than the molecule. The side project's
terms are frozen now (its milestones are numbered M2–M5 in the technical documents, continuing the
plan's numbering after probe M1; they are unrelated objects and are named here by molecule):

- **M2** (benzene, cc-pVTZ; laptop): the engine version pinned and printed; the
  automatic-differentiation gradient with the frozen-space projection inside the differentiated
  graph agrees component-wise with central finite differences of the re-projected frozen-space
  energy; its smoothness along the same modes as probe M1 printed; the projection term of the
  gradient measured. Passing M2 licenses the gradient route at benzene.
- **M3** (naphthalene, cc-pVTZ; laptop): the same correctness, smoothness and projection-term
  printouts, plus wall-clock per gradient
  and peak memory within the laptop's ceiling. Passing M3 licenses the gradient route at
  naphthalene.
- **M4** (pyrene) and **M5** (coronene), each nine gradients per probed mode: run/no-run,
  correctness against finite differences, noise, memory and wall-clock, and the batch classified
  as laptop or cluster work by the budget's arithmetic rule. Expected cluster-conditional.
- **Kill criterion.** The side project stops, by dated note, if M3 is not reached within twelve
  calendar weeks of the pilot note's commit date, or if M2's correctness check fails after the
  gradient and the finite-difference reference have each been re-derived once. Its hours are
  booked to a separate budget line and reviewed every four weeks against the pipeline's own
  infrastructure hours; if they exceed them, a written review is mandatory before another hour is
  logged. A stopped side project is reported with its last printed milestone.

If it succeeds, the gradient route runs in addition to the energy route on the rungs it licenses
— each rung then carries two cost records — and the size question is also answered on the
gradient count; if it fails, the energy route remains the guaranteed route.

## 6. What this project deliberately does not do, and why

**No transferable, train-once spectrum model.** Plan 04's attempt to learn a correction on one
ring motif and reuse it on another failed its own transfer test, and that measured failure is the
reason every molecule gets its own probed correction. The Module-05 deep-learning component
predicts only *where* the correction is likely to have large off-diagonal elements, is trained on
a public DFT-vs-DFT Hessian corpus, and enters a promised rung only after a licence: its saving
demonstrated on that corpus against the symmetry prior's free-element count, and its result
checked prior-free at that rung. The student ruled more generally that a rule inherited from an
earlier plan carries no authority of its own — knowledge transfer is allowed wherever a gate shows
it makes the pipeline succeed.

**What would follow from success (outlook, not a promise).** Plan 05 builds no transferable model,
for the measured reason above. But it produces the two things such a model would need. It measures
the *range* of the correction — whether a block of Δ₂ between two atoms is fixed by their local
environment or by the whole molecule — at the pyrene and coronene rungs, and that measurement
decides in advance whether a transferable model of Δ₂ can exist at all. And every rung delivers Δ₂
itself, hundreds of atom-pair blocks per molecule, thousands more from the fragment probing at the
top of the ladder: training data for a model that would predict the correction from local
structure, the classical Δ-learning target — a small, smooth difference, not the potential-energy
surface plan 04 tried to learn. If the range measured at R3 is short, a dated follow-up proposal
would put such a model through the same licence as the Module-05 prior — checked against the probed
Δ₂ on a middle rung before it is trusted on a higher one — and a new PAH would then need only its
DFT steps and a sampled coupled-cluster check instead of the full probe count. If the range is long,
no such model exists, and the pipeline remains a per-molecule measurement. Either outcome is a
result; neither is claimed here.

**No promised coupled-cluster anharmonic correction** (§2; the diagonal cubic by-product is
reported, not applied). **No coupled-cluster correction to intensities** (§7). **No predicted band
widths** (§7). **No full coupled-cluster surface or global quartic force field.** **No new
empirical scale factors** (the in-house calibrated-harmonic baseline is an opponent, not the
method). **No light–matter dynamics and no new emission model** (the emission cascade model of
Mulas et al. 2018 is inherited post-processing where an emission spectrum is drawn). **No species
identification in JWST spectra.** **No sub-tolerance accuracy language.** **No whole-molecule
probing at C₃₈₄H₄₈** (§4).

## 7. Evaluation design

**What is scored, what is shown.** Band **positions** are the promised quantity and are scored
on every rung where a laboratory band passes the decidability rule. **Intensities** are shown for
every molecule with their provenance and are **scored on benzene and naphthalene** — the two rungs
with calibrated gas-phase intensities — as a second, separately reported quantity: the integrated
band intensity of each scored band, the pipeline's anharmonic value against the
calibrated-harmonic baseline's harmonic value and against PAHdb's where it reports one, with the
source's stated intensity uncertainty as tolerance (decision 18). Elsewhere the intensities stand
beside PAHdb's computed ones as a comparison, not a verdict: both are DFT, and no scoreboard
exists. Matrix intensities never score. No coupled-cluster correction to intensities is promised:
Madriaga & Crawford's objection to local-CC field derivatives stands, and whether the frozen-space
object removes it is a measured question — a dipole companion to probe M1 (**M1-μ**: the frozen
spaces' dipole moment along the same modes against canonical CCSD(T)), owed after the cc-pVTZ scan
— and only a printed result can turn it into a proposal. Band **widths** are drawn at the source's
resolution and temperature and labelled as presentation.

**Opponents (frozen baselines), named and versioned:**

| Line | What it is | Version / reference | Where it competes |
|---|---|---|---|
| A | PAHdb computed library: scaled-harmonic DFT | v4.00; Ricca et al. 2026 | every rung |
| B | anharmonic DFT quartic force field for pyrene and coronene | Mulas et al. 2018 | R2, R3 where present |
| C | machine-learning molecular dynamics trained on DFT, temperature-dependent, to C₂₁₆ | Mai et al. 2025 (MNRAS 541, 3073) | where coverage overlaps; theory-vs-theory on reach rungs |
| in-house | the **calibrated-harmonic baseline** (Module 04): a per-band ML correction to scaled-harmonic DFT, trained leave-molecule-out on laboratory residuals, after the ML-corrected-scaling approach of Bos et al. 2025 | built in this project, frozen before scoring | every accuracy rung |

**Frozen comparisons and the pilot note.** Paired per-band absolute error on identical laboratory
bands; band lists, windows and margins frozen in the pilot note, which is written with seven
inputs in hand and **nothing else**:

1. the laboratory side with its measured band uncertainties — owed (the scoreboard re-read);
2. the opponent side — exists (versions named above);
3. the DFT-only rehearsal with its noise-injected column — exists for benzene (5 September);
   naphthalene owed;
4. the frozen-space probe M1 — exists (5–6 September; cc-pVTZ scan running);
5. the canonical feasibility probe — exists (5 September);
6. a run/no-run check of which local-CC codes produce an analytic gradient at the anchor level
   at the equilibrium geometry, with memory — owed;
7. the naphthalene noise measurement (four modes × nine points × two arms — arm A, frozen
   spaces, and arm B, re-selected spaces on the transported orbitals — = 72 energies; the noise
   is the scatter about a smooth fit, no canonical line existing at naphthalene) with its fitted
   coefficients sealed — owed.

The first real coupled-cluster correction is computed after the note is committed, so no stopping
constant, probe cap, tolerance or margin can be shaped by a result; the raw displaced energies of
probe M1 are sealed for the same reason, and this proposal quotes only differences between
methods.

**Mandatory null tests.** The Δ=0 arm — DFT harmonic plus DFT anharmonic, no coupled-cluster
correction, scored by the same script on the same bands — must lose the comparison on every family
where "beat" is claimed, or the coupled-cluster claim for that family is void and reported as
explained by DFT-level anharmonicity. A noise-input run must fail the sanity gates. New in plan
05: a **shuffled-probe null** — the probe responses randomly permuted and fed to the same solver
must fail the probing licence — and a **discriminability clause** — the recovered correction must
beat the zero correction against the reference by a factor frozen in the pilot note. Both exist
because a regularised recovery can be confidently wrong.

**Licensing by measurement.** The anchor gate has three formulas, each with its numbers filled in
the pilot note: a noise line, a bias line against the canonical reference (judged on the composite
energy of §3.3), and a threshold-sensitivity line — the frequency change between the program's
tight and default truncation thresholds — that, if breached, makes extrapolation in the LNO
truncation thresholds (the analogue, for this program, of the complete-PNO-space extrapolation of
Altun et al. 2021, who measured the local error on acenes growing linearly with ring count and
reduced it four- to five-fold by extrapolation) mandatory at double cost. The probing licence and the locality
test have their own tolerances, all bounded by the smallest beat margin.

**Leakage control.** Laboratory values never enter training, validation, stopping, sampling or
pattern design; the calibrated-harmonic baseline is the single declared exception, evaluated
leave-molecule-out.

**Fail-closed reporting.** Every rung that does not run, every family that is undecidable, every
gate that breaches has a pre-written sentence, and losing is published with the same paired table
as winning.

## 8. Feasibility and resources — what has been measured

Every cost in the plan is a measured slot reading "not run" until a script prints it. The
literature figures that motivated the design (a hundred-odd gradients for a full Hessian; 30 % of
columns on anthracene; a few micro-hartree of local-correlation noise) are recorded as motivation
and are forbidden in any budget sentence. The following were printed between 5 and 6 September on
the student's laptop (an 8-core Ryzen 7 260, 31 GB, no CUDA GPU; the anchor code runs in a Linux
subsystem given 22 GB; the machine is dedicated to the project and available around the clock).

- **The DFT-only rehearsal (benzene; B3LYP vs BHHLYP, 6-31G*).** The deck: 30 single-mode
  patterns, 184 two-mode patterns and 120 multi-mode patterns, each run as a ± pair (two
  energies), i.e. 334 pairs or 668 energies, of which 61 pairs (122 energies) were held out of
  every fit; plus the 30 single-mode patterns at a second amplitude (60 energies) and the
  reference geometry — **729 energies per functional**, 2 h 30 min. Of the 546 training energies
  the recovery reached its off-diagonal threshold at 448, of which the first 60 (the single-mode
  block) fix the diagonal: **K = 448 energies, K_off = 388 energies for 435 off-diagonal
  unknowns**. (K counts the energies consumed until the rule stopped; the 122 held-out energies
  are computed as well and are reported beside K as the hold-out fraction, never inside it.)
  Energy route:
  per-family errors of the full recovery ≤ 0.43 cm⁻¹ against 7 cm⁻¹ for the diagonal-only
  recovery; gradient route: the same from 60 gradients.
- **Probe M1** (§3.3): two threshold settings × 27 geometries × three arms, plus 27 canonical
  CCSD(T) points; 5–10 minutes per geometry at cc-pVDZ. The cc-pVTZ scan takes about two hours per
  geometry and 2.5 days in all.
- **The canonical reference.** Canonical CCSD(T) energy of benzene: 27 s at cc-pVDZ, **755 s and
  7.3 GB at cc-pVTZ**. Local LNO-CCSD(T) energy at cc-pVTZ: 2,087 s (locality pays only at larger
  molecules). The anchor's bias line — 61 canonical energies along benzene's 30 modes — is
  therefore about 13 hours and **fits the laptop**; the full canonical reference Hessian by
  energies (1 + 2·30 + 4·435 = 1,801 energies, about 378 hours) **does not**, and neither does the
  gradient branch: a canonical CCSD(T) gradient of benzene costs 1,399 s and 13.9 GB at cc-pVDZ —
  about fifty energies — and at cc-pVTZ it did not complete within the 22 GB ceiling (its memory
  scales roughly with the fourth power of the basis size, (264/114)⁴ ≈ 30, i.e. hundreds of GB). The full canonical Hessian at benzene is cluster work; the probing licence was written
  to test the recovery without it. **The canonical reference at benzene therefore consists of**
  the 61-energy diagonal line (the anchor's bias line) and the canonical two-mode points of
  decision 16 for the off-diagonal bias; the probing licence's full-matrix comparison is against
  the directly computed local-CC reference with the same frozen spaces.
- **The Module-05 corpus.** A B3LYP Hessian of a QM9-size molecule takes 3–7 minutes here, so the
  aromatic-heavy subset of order a thousand molecules is three days of laptop time.

Still owed before the pilot note (§7's list): the naphthalene rehearsal, which also admits or
refuses the symmetry prior; the scoreboard re-read with its measured band uncertainties; the
gradient run/no-run check; and the naphthalene noise measurement. After the note: the benzene
probe batch and its references, including canonical two-mode points from which the frozen
spaces' off-diagonal bias is read (decision 16); naphthalene; an anthracene direct-coupling probe
as a dated bonus (the plan's own reason: anthracene is the smallest acene where the plan expects
DFT's delocalisation error to begin to show in the C–C families; a reason, not a citation); then
classification of the pyrene- and coronene-size batches as laptop or cluster work by an
arithmetic rule (168 hours of wall-clock per batch is the line). The domain review priced plan
05's own probes as cheaper than plan 04's first batch of surface-learning points, and the
measurements so far agree.

Human hours are logged and not capped. Laptop wall-clock carries checkpoints that force dated
decisions. Cluster node-hours and rented GPU-hours get no number until access, a timed probe on
the actual machine, and a per-rung cap exist in writing. The C₃₈₄H₄₈-class DFT Hessian is itself
a cluster object.

## 9. Review status

Four review rounds — each a cold read and an adversarial domain review, performed as described
after §1 — were run on 3 and 4 September. The first domain review returned a **conditional
verdict**: a green light for the benzene–naphthalene measurement programme once six blocking items
were written in, and no green light for the promised set *as it was then worded*, which promised
a coupled-cluster anharmonic correction the probes could not build, hung its cost question on a
gradient that does not exist in production codes, and treated the largest species as a
whole-molecule object. The student's decisions of 4 September (§10, items 1–7) re-worded the set;
the second domain review then gave a green light for the pre-pilot-note programme and the benzene
and naphthalene rungs once four items were written into the specification (a reproducible
estimator for the noise gate; a noise-aware stopping rule; an absolute agreement metric for the
locality couplings; a feasibility probe for the canonical reference) and withheld it for the
pyrene and coronene rungs on two points — the fragment licence and the gas-phase decidability of
the C–C families — both closed in the specification the same day. The third and fourth rounds
re-read those closures (seventeen of eighteen held; the exception was re-patched and re-read in the
fourth round; then twelve of twelve) and changed the design in seven
places, all in the text: paired displacements so that the coupled-cluster force at the DFT
geometry cancels; frozen spaces transported by projection rather than re-localised; only benzene
scored unconditionally until the room-temperature naphthalene source was found; noise injected
per energy in the rehearsal; the shared reference energy's offset identified from a second
displacement amplitude (§3.4); the first-order geometry term on every scored band (§5.1); and the
PNNL naphthalene source itself.

The review loop was **closed on 4 September** after a consistency check of the last revision (19
cross-references, all mechanical). Since then the plan's text changes only by dated notes that
name a measurement or a decision; the decisions of 5–6 September (§10, items 8–19) are such notes.
Items 8–16 and 19 were made on the DFT-only rehearsal, the frozen-space probe and the timings —
before any coupled-cluster response of the real correction exists, so none of the rules the
evaluation depends on was shaped by a result it will judge; items 17 and 18 are tooling and scope
choices. The remaining risk is retired by
measurements, not by further reading; §8 lists the first of them.

## 10. Decisions the student made (all closed; a supervisor's objection would reopen any of them)

**Principle, 4 September 2026.** A rule inherited from an earlier plan carries no authority of its
own; knowledge transfer is allowed wherever a gate shows it makes the pipeline succeed.

**4 September 2026.**
1. Fragment probing at the largest sizes is a permitted method, used if the locality measurement
   at the middle rungs licenses it; the C₃₈₄H₄₈-class deliverable is a fragment-probed spectrum,
   or the measured reason it could not be produced.
2. Every plan version stays in the repository as a read-only record.
3. The R2 scored set: triphenylene is scored on its gas-phase families; tetracene is matrix-only
   and gated (a jet-cooled band list added since as a cold column). *Addition, 5 September:* the
   R2 C–C families are signed off as expected-undecidable after the source search (§5.2).
4. The Module-05 target: a Transformer predicting the support of the correction, trained on an
   aromatic-heavy subset of the public Hessian QM9 set (Williams et al. 2024) with recomputed
   B3LYP Hessians; success is the measured saving and the per-rung licence, not accuracy.
5. The re-worded promised set: the harmonic-only correction; the energy route as the guaranteed
   route but not as a limit, the gradient route built in the side project.
6. The development machine: the student's current laptop; a replacement only if a probe shows it
   necessary.
7. No earlier coursework overlaps with this project. An unsubmitted draft that used the QM9 set
   has been renamed so that the Module-05 corpus cannot be mistaken for re-used work.

**5–6 September 2026, after the first measurements.**
8. The stopping rule reads the off-diagonal residual.
9. Its threshold carries the model floor.
10. The off-diagonal noise requirement is measured per rung; if exceeded, the couplings are
    reported at noise-limited precision and the gradient route takes them over where it exists.
11. The structural prior is the symmetry prior, entering the deck after the naphthalene rehearsal.
12. The rehearsal's former fixed reading threshold is retired; the stopping constant is calibrated
    on the off-diagonal residual.
13. The energy route is budgeted at M(M−1)/2 energies where no prior bites and at the symmetry
    prior's free-element count where it applies; the learned prior is measured against that count.
14. The frozen-space object's transported blocks are semicanonicalised at each geometry.
15. The energy the object reports is the composite local-CCSD(T) + [MP2(full) − MP2(local)].
16. The cc-pVTZ frozen-space scan with its canonical truth line runs (started 6 September); the
    benzene probe batch includes canonical two-mode points for the off-diagonal bias.
17. Module 07's campaign officer runs on LangGraph (admissible through the programme's
    LangChain/LangGraph elective) with the Anthropic API as model endpoint, model id logged.
18. Intensities are scored on benzene and naphthalene as a second quantity; positions remain the
    primary claim; no coupled-cluster intensity correction is promised; the dipole probe M1-μ
    decides whether one can be proposed; widths are drawn, not predicted.
19. Coupling blocks made only of infrared-inactive modes are tested per rung and dropped only
    where the scored positions do not move.

## 11. Risks

1. **Frozen-space energies are not smooth enough for energy-only probing.** Measured at benzene in
   cc-pVDZ: they are, by a factor of 30 to 1,000 (§3.3). Remaining exposure: the anchor basis (scan
   running) and larger molecules (the naphthalene noise measurement). Response where a measurement
   fails: no accuracy claim for the couplings at that size; the gradient route where the side
   project has delivered it.
2. **The correction is not near-diagonal in the DFT mode basis on aromatic ring modes.** Measured
   at benzene on the DFT surrogate: it is not, and the couplings follow symmetry, not frequency.
   Response: the symmetry prior; the rehearsal on a functional pair that brackets exact exchange;
   the diagonal-only and full recoveries printed side by side at benzene and naphthalene.
3. **The correction is not local, or is local for C–H modes and not for the delocalised C–C
   families the astronomy needs.** Response: locality measured on directly computed blocks per
   family, the anthracene probe, and a pre-registered per-family losing condition that withdraws
   the reach story for exactly those families.
4. **The coupled-cluster harmonic correction does not beat calibrated harmonics.** The opponents'
   fitted scale factors already absorb the mean of a harmonic difference that Esposito et al. 2024
   (§14) measured for benzene: B3LYP/N07D against CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies,
   mean absolute difference 5.45 cm⁻¹ (their Table S1; benzene only, read in full 6 September);
   what remains to buy is the per-family scatter. Response: the expected-effect line is
   written into the pilot note before any result, and losing is publishable.
5. **Laboratory decidability.** The per-family rule pre-declares undecidable families
   inconclusive. The pyrene-size rung's C–C families are in that class on every source the search
   found; the cold jet-cooled lists for tetracene and coronene are scored as labelled columns.
   Only a new gas-phase source changes this (§13).
6. **Off-diagonal probing is expensive without a prior.** Measured: 0.9 energies per unknown at
   benzene. Response: the symmetry prior (decision 11) with its per-rung free-element count printed
   beside the probe count; the learned prior of Module 05 measured against the same count; the
   168-hour rule classifies any rung the prior does not rescue as cluster work rather than
   quietly overrunning.
7. **The side project becomes a time sink** — the failure mode that ended plan 01, which spent
   two-thirds of its hours on infrastructure. Response: the terms of §5.3 (separate budget line,
   twelve-week kill criterion, four-weekly review).
8. **Operational.** The first week produced two lost runs (a memory ceiling set too high; a
   machine switched off with a job running). Both are now rules in the budget document: a memory
   ceiling with headroom for the host, one anchor job at a time, every long run announced with
   its end time and written out point by point so an interruption costs one point.

## 12. Fit to the capstone programme

Each module of the programme is mapped onto a load-bearing pipeline artifact: the opponent atlas
(Module 02); the laboratory scoreboard with the measured band-centre uncertainties and, for benzene
and naphthalene, the calibrated intensities (Module 03); the calibrated-harmonic baseline (Module
04); the campaign officer that enforces the budget rules and the two permitted cost sentences
(Module 07; see the terms after §1); and the assembled pipeline with its scored ladder and cost
records (Module 08). Module 01 (foundations) maps to no pipeline artifact. Two
modules — the deep-learning support predictor (Module 05) and the generative pattern proposer
(Module 06) — are efficiency experiments on the off-diagonal probe count, run on DFT-only corpora
at zero coupled-cluster cost and measured against the symmetry prior's free-element count; the
deep-learning model is measured on the accuracy rungs and, if it earns its licence there, becomes
load-bearing on the reach rungs — the mapping says exactly that rather than pretending otherwise.
Module deadlines are administrative facts; a module may ship a fail-closed state to meet its
date, and the science continues past it.

## 13. What is asked of the supervisor

1. A critical reading of §2–§3 (why the coupled-cluster budget moves to the harmonic correction,
   why it is recovered by probing under a symmetry prior, and what the first measurements say) and
   of §7 (the evaluation contract, with the opponents now named) — the places where the plan's
   discipline either holds or does not.
2. A view on the fragment-probing route to the largest sizes (§4) and on the Module-05 target
   (§10, item 4), both decided by the student as methods subject to measurement — a supervisor's
   objection would reopen either — and on the side project of §5.3, whose milestones, kill
   criterion and budget terms are stated there.
3. **Laboratory sources.** Gas-phase or jet-cooled spectra of pyrene, chrysene and triphenylene
   **in the 6–15 µm region** at better than 8 cm⁻¹ resolution and known temperature would make the
   C–C families at the pyrene-size rung decidable. The 5 September search found none at room
   temperature; a source the supervisor knows of that the search missed would enlarge the
   decidable set, and the plan is written so that it can be added before, never after, a comparison
   is scored.
4. A view on the intensity question (§7): positions are the promise, intensities are scored where
   a calibrated gas-phase measurement exists and reported elsewhere, and a coupled-cluster
   correction to intensities is a measured question rather than a promise. If the supervisor wants
   intensities carried further, the dipole probe M1-μ is the measurement that would license it.
5. When the naphthalene measurements justify it: sponsorship of a cluster-time request sized by
   the timed probes, and, at the large-rung stage, serving as or nominating the named expert whose
   pre-registered judgment is the datum where no laboratory truth exists (the "expert-judgment
   datum" of §5.2).
6. Whether the supervisor sees the outlook of §6 as a reason to widen the corpus of measured
   molecules beyond the ladder, at cluster cost, once R3 has printed the range of the correction.

## 14. References

Verification status is tracked per item in the working bibliography of this folder; every
identifier is re-verified against the primary source before it appears in any scored document.

Cited in this proposal (verified by Crossref, arXiv or full text on 2–5 September 2026 unless
marked otherwise; author initials are given only where the working bibliography records them):

- Altun, A., Ghosh, S., Riplinger, C., Neese, F., Bistoni, G. 2021, J. Phys. Chem. A 125, 9932.
  DOI 10.1021/acs.jpca.1c09106. (Local-approximation error grows with acene length; CPS
  extrapolation.)
- Bégué, D., Carbonnière, P., Pouchan, C. 2005, J. Phys. Chem. A 109, 4611.
  DOI 10.1021/jp0406114. (Hybrid CC-quadratic / DFT-anharmonic force field.)
- Boese, Klopper & Martin 2005, Mol. Phys. 103, 863. DOI 10.1080/00268970512331339369. (Origin
  of the hybrid split: coupled-cluster harmonics, cheap anharmonics.)
- Bos et al. 2025, ACS Omega 10, 62282. DOI 10.1021/acsomega.5c10225. (ML-corrected DFT
  scaling; the approach the in-house calibrated-harmonic baseline reproduces.)
- Brumfield, Stewart & McCall 2012, J. Phys. Chem. Lett. 3, 1985.
  DOI 10.1021/jz300769k. (One rotationally resolved cold band of pyrene near 8.5 µm; Crossref
  record; content at abstract grade.)
- Chu, Guenther, Rhoderick & Lafferty 1999, J. Res. Natl. Inst. Stand.
  Technol. 104, 59. DOI 10.6028/jres.104.004. (The NIST Quantitative Infrared Database; Crossref
  record; read by the scoreboard module before any uncertainty is printed.)
- Esposito, V. J., Fortenberry, R. C., Boersma, C., Allamandola, L. J. 2024, J. Chem. Phys. 160,
  211101. DOI 10.1063/5.0208597. (C–H overtone spectra of benzene and naphthalene; the
  PAHdb-anharmonic protocol; B3LYP/N07D vs CCSD(T)-F12b benzene harmonics, MAD 5.45 cm⁻¹.)
- Fusè, M., Mazzeo, G., Longhi, G., Abbate, S., Yang, Q., Bloino, J. 2024, Spectrochim. Acta A
  311, 123969. DOI 10.1016/j.saa.2024.123969. (Reduced-dimensionality VPT2 for large molecules.)
- Olive Dornshuld, L. N., Lahm, M. E., Kitzmiller, N. L., Allen, W. D., Schaefer, H. F. 2026,
  J. Phys. Chem. A 130, 3249. DOI 10.1021/acs.jpca.6c00689. (CMA for intermolecular vibrations.)
- Joblin, Boissel, Léger, d'Hendecourt & Défourneau 1995, Astron. Astrophys.
  299, 835. (PAH band shifts with temperature; reference known, not yet opened.)
- Kitzmiller, N. L., Lahm, M. E., Olive Dornshuld, L. N., Jin, J., Allen, W. D., Schaefer, H. F.
  2024, J. Chem. Theory Comput. 20, 10886. DOI 10.1021/acs.jctc.4c01240. (CMA-2.)
- Lahm, M. E., Kitzmiller, N. L., Mull, H. F., Allen, W. D., Schaefer, H. F. 2022, J. Am. Chem.
  Soc. 144, 23271. DOI 10.1021/jacs.2c11158. (Concordant Mode Approach.)
- Lemmens, Rap, Thunnissen, Mackie, Candian, Tielens, Rijs & Buma 2019, Astron. Astrophys. 628, A130.
  DOI 10.1051/0004-6361/201935631. (Jet-cooled mid-infrared band list of tetracene.)
- Lemmens, Rijs & Buma 2021, Astrophys. J. 923, 238.
  DOI 10.3847/1538-4357/ac2f9d. (Jet-cooled far- and mid-infrared spectra of coronene and larger
  PAHs.)
- Madriaga, J. P., Crawford, T. D. 2025, J. Phys. Chem. A 129, 10014.
  DOI 10.1021/acs.jpca.5c05210. (PNO discontinuities in finite-difference properties.)
- Mai et al. 2025, Mon. Not. R. Astron. Soc. 541, 3073; arXiv:2503.05120. (Opponent line C:
  DFT-trained machine-learning molecular dynamics of PAHs to C₂₁₆.)
- Mulas, Falvo, Cassam-Chenaï & Joblin 2018, J. Chem. Phys. 149, 144102.
  DOI 10.1063/1.5050087. (Opponent line B: anharmonic DFT quartic force fields of pyrene and
  coronene; the emission cascade model.)
- Pirali, Vervloet, Mulas, Malloci & Joblin 2009, Phys. Chem. Chem. Phys. 11,
  3443. DOI 10.1039/b814037e. (Naphthalene hot-band spectroscopy; the temperature term.)
- Ricca, Boersma, Maragkoudakis, Roser, Shannon, Allamandola & Bauschlicher 2026, Astrophys. J. Suppl. Ser. 282, 7. DOI 10.3847/1538-4365/ae1c38.
  (PAHdb v4.00, opponent line A; the "currently unquantified" quotation.)
- Sanders, J. N., Andrade, X., Aspuru-Guzik, A. 2015, ACS Cent. Sci. 1, 24. DOI 10.1021/oc5000404.
  (Compressed-sensing Hessians; polyacenes.)
- Schneider, Baker, Scharko, Blake, Tonkyn, Forland & Johnson 2024, J. Quant. Spectrosc. Radiat. Transfer 323, 109045.
  DOI 10.1016/j.jqsrt.2024.109045. (Quantitative vapour-phase spectra of solids, naphthalene among
  them, 25 °C, 0.1 cm⁻¹; Crossref record; read by the scoreboard module.)
- Sharpe, Johnson, Sams, Chu, Rhoderick & Johnson 2004,
  Appl. Spectrosc. 58, 1452. DOI 10.1366/0003702042641281. (The PNNL gas-phase quantitative IR
  database.)
- Wang, B., Luo, S., Wang, Z., Liu, W. 2025, J. Chem. Theory Comput. 21, 10893.
  DOI 10.1021/acs.jctc.5c01354. (O1NumHess.)
- Williams, N. J., Kabalan, L., Stojanovic, L., Zolyomi, V., Pyzer-Knapp, E. O. 2024,
  arXiv:2408.08006. (Hessian QM9.)
- Zhang, X., et al. 2024, arXiv:2404.03129. (Automatic-differentiation gradients for local coupled
  cluster, PySCFAD.)

Other plan-04 sources carried in the working bibliography and used by the modules (matrix
scoreboards, the DLPNO caveats): Bauschlicher et al. 2018; Chen, Li & Li 2026; Hudgins & Sandford 1998; Käser & Meuwly 2021; Lam, Abdul-Al &
Allouche 2020; Mattioda et al. 2020; Sylvetsky et al. 2020; Tang et al. 2025; NIST CCCBDB; Zapata
Trujillo & McKemmish 2022.
