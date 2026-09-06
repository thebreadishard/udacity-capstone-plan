# Probed coupled-cluster corrections to the harmonic force constants of polycyclic aromatic hydrocarbons: an infrared pipeline with a measured cost

**Master's capstone project proposal — plan 05**
Prepared for supervision review. First written 3 September 2026; revised 4 September after four
review rounds and the student's first decisions; **rewritten as one document on 6 September 2026**
after the first measurements (the DFT-only dry run, the frozen-space probe, the feasibility
timings, a laboratory-source search) and the student's decisions 8–19. Earlier versions are in
the repository's history. Companion documents: this proposal summarises the plan and explains
*why* its decisions were taken; the binding technical documents (goal, ladder, tolerances,
opponents, gates, budget, mapping) live in the same folder and take precedence where they are more
specific. Eight external review passes (four cold reads and four adversarial domain reviews, 3–4
September) are in the folder with every finding and its closure; §9 says what they concluded and
where the review loop was closed. Every number in this proposal that describes this project's own
performance was printed by a script in the folder's `probes/` directory; numbers from the
literature are marked as such.

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

Plan 04, reviewed in the previous round, obtained its coupled-cluster anchor by learning a
per-molecule potential-energy surface from thousands of local coupled-cluster points. Its domain
review accepted the criterion and found the cost unaffordable at the sizes that matter. Plan 05
keeps plan 04's criterion, opponents, laboratory scoreboards, gates and honesty rules and replaces
one thing: instead of learning a surface, it **probes the difference** between the local
coupled-cluster and DFT force constants — a small, smooth quantity — with a hashed set of
simultaneous multi-atom displacements, and recovers that difference in the DFT normal-mode basis
under a prior that molecular symmetry supplies for free. The number of coupled-cluster energies
each molecule needed is measured and reported beside its spectrum. Whether that number stops
growing with molecule size is a pre-registered measurement with a stated losing condition, not a
claim.

Three things have been measured since the plan was written, all on the student's laptop, all in
the first week: the probing machinery recovers a full force-constant correction in a DFT-only
rehearsal; the frozen correlation spaces on which the whole design rests are smooth to a few
nano-hartree where the released local-CC code scatters by ten micro-hartree; and the canonical
coupled-cluster reference that licenses the anchor fits the laptop at benzene while the full
canonical Hessian does not. The pipeline outputs the whole spectral shape for every molecule —
position, intensity, drawn width — and the plan is explicit about which of those it scores and
which it promises: positions are promised and scored wherever a laboratory band exists;
intensities are scored on the two molecules where a calibrated gas-phase intensity exists
(benzene, naphthalene) and reported with their provenance everywhere else.

The success criterion remains relative and measured: on small and medium PAHs the pipeline's band
positions are compared per band against named, version-frozen state-of-the-art predictions under
a pre-registered protocol; on the largest species the deliverable is a spectrum with a labelled
error budget and no accuracy claim. The project is as much about the evaluation discipline —
pre-registration, frozen baselines, mandatory null tests, fail-closed reporting — as about the
spectra themselves.

## 2. Why the coupled-cluster budget moves from the surface to the correction

Three facts, two of them measured in this project's own history and one from the literature,
drove the change.

First, the arithmetic of plan 04. Coronene has 102 vibrational coordinates; a learned surface
over them needs, by the source conversation's own estimate, of order 10⁴ local coupled-cluster
points — thousands of node-hours per molecule, on an allocation that does not exist. The plan-04
domain review made this a blocking finding.

Second, what a coupled-cluster anchor actually adds. Almost all of a PAH's potential-energy
surface is already described at DFT quality. The only new information the expensive method
supplies is the *difference* between the two surfaces, and near equilibrium that difference is
small and smooth. Paying coupled-cluster prices to relearn the DFT part is where plan 04's cost
went.

Third, where the difference pays. The hybrid quartic-force-field literature (Boese, Klopper &
Martin 2005; Bégué, Carbonnière & Pouchan 2005; and, on naphthalene, Esposito et al. 2024) puts the
coupled-cluster level in the **harmonic** constants and leaves cubic and quartic constants at DFT
level. Plan 04 had it the other way round. Plan 05 corrects the harmonic force constants only —
the object called Δ₂ in the technical documents — and lets DFT supply the anharmonic constants.
The domain review sharpened this further: energy-only probing cannot produce the three-index
cubic constants that PAH combination-band resonances need, so a coupled-cluster anharmonic
correction was not merely unnecessary but unbuildable with the probes specified. It was removed
from the promised set; a cheap probe of the diagonal cubic correction remains, as a reported
number that will show how much was given up.

## 3. How the correction is recovered, and why in this form

### 3.1 Prior art and what is new

Two published methods recover a *full* Hessian from far fewer calculations than one per
coordinate by exploiting its structure: O1NumHess (Wang et al. 2025), which recovers a Hessian
from a number of gradients that saturates around a hundred for molecules of hundreds of atoms,
and compressed-sensing recovery in a cheap method's eigenbasis (Sanders, Andrade & Aspuru-Guzik
2015), which on anthracene needed 30 % of the Hessian columns and whose cost grew only
logarithmically across polyacenes of one to fifteen rings. Neither has been applied to a
coupled-cluster-minus-DFT difference.

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

### 3.2 The prior: symmetry, not a frequency band

The plan's first draft regularised the recovery with a frequency band: couplings between modes
close in frequency were left free, distant ones were penalised. The DFT-only rehearsal at benzene
(5 September; §8) showed that this is not where the structure is. The large off-diagonal elements
of the correction couple modes 170–450 cm⁻¹ apart — the strongest pair at 1186 and 1357 cm⁻¹ —
and every one of them lies within a single irreducible representation of the molecule's point
group. The band did not select them; the recovery worked because the two-mode patterns in the
deck isolated them and the fitted penalty was weak.

The prior is therefore now what symmetry gives for free (decision 11): couplings between modes of
**different** irreducible representations are fixed at zero — exact, not assumed — and couplings
within one representation are free whatever their frequency distance. A sparsity penalty remains
only for molecules whose point group leaves too many free elements to determine. This prior has
no parameters, cannot distort the truth on a symmetric molecule, and enters the probe deck after
the naphthalene rehearsal reproduces the direct DFT−DFT correction with it; until that rehearsal
has printed, the banded rule stands as the fallback. It also sets the honest cost expectation
(decision 13): without a prior the off-diagonal block costs about M(M−1)/2 energies for M modes —
the benzene rehearsal needed 388 energies for 435 unknowns, so sparsity as such saved nothing —
and with the symmetry prior naphthalene (D₂h, eight representations) has of order 120 free
couplings instead of 1,128. That difference is what puts the energy route at naphthalene inside
the laptop's budget rather than on a cluster.

### 3.3 Frozen correlation spaces — the object, now measured

The coupled-cluster energies at displaced geometries are computed with the local-correlation
spaces frozen at the equilibrium geometry and transported to each displaced geometry by
projection and orthonormalisation — nothing is re-localised or re-selected — because domain
changes on displacement produce micro-hartree discontinuities, the same mechanism Madriaga &
Crawford (2025) showed destroys finite-difference field properties even with fixed PNO dimensions.
The domain review derived the noise floor this imposes and made the smoothness of the frozen
space the first measurement of the plan. It has now been made (probe M1, 5–6 September, benzene,
cc-pVDZ): along three normal modes — totally symmetric, degenerate, and out-of-plane — at nine
displacements each, against canonical CCSD(T) on the same 27 geometries, the frozen-space energy
scatters about a smooth curve by **0.002–0.06 µE_h**, where the released code's energies, which
re-select their spaces at every geometry, scatter by 7–11 µE_h at its default thresholds and by
0.05–2.7 µE_h at tight ones. The frozen space carries a bias — it was chosen at equilibrium and
fits a displaced geometry slightly less well — and that bias is a clean quadratic in the
displacement, i.e. exactly a curvature bias: 5–28 cm⁻¹ on the bare local energy, **0.5–2.6 cm⁻¹**
with the local-correlation literature's standard second-order correction for the truncated space
at default thresholds, and **0.03–0.36 cm⁻¹** at tight thresholds. The object also reproduces the
reference energy exactly and reloads from file exactly, which is the property the pipeline
depends on. The same scan at the anchor basis (cc-pVTZ) is running as this is written; the basis
is larger, the frozen space is a smaller fraction of it, and the cc-pVDZ bias is a lower bound.
Two definitions were fixed by this measurement (decisions 14, 15): the transported orbital blocks
are semicanonicalised at each geometry — a rotation inside the frozen space that the impurity
solvers require, without which a first run read a spurious bias of up to 147 cm⁻¹ — and the
energy the pipeline probes is the composite local energy with the second-order correction.

### 3.4 The stopping rule and the probe count

The probe patterns are consumed in a hashed order fixed before any response exists, so the
reported probe count is a measurement and not a choice. The count K is the number of energies at
which the recovery's held-out residual first falls below a threshold, and the rehearsal changed
that threshold in two ways (decisions 8, 9, 12). The residual is computed on the **off-diagonal
part** of the responses: the diagonal correction is known after the first block of single-mode
patterns and dominates every response (97.6 % at benzene), so a residual on the raw response read
"done" while the couplings were still unknown. And the threshold carries a **model floor**: a
quadratic model cannot fit the quartic content of the surface below a printed residual, so at low
noise the old rule was unreachable and would have run every rung to its cap; the threshold is now
the larger of that floor and a multiple of the rung's own noise floor. The noise requirement for
the off-diagonal block is measured per rung from the off-diagonal signal (decision 10): at benzene
it is about 2 µE_h per energy, ten times stricter than the diagonal requirement, and the frozen
spaces meet it by two orders of magnitude; if a larger molecule did not, the plan says in advance
that the gradient route of §5.3 becomes load-bearing for the couplings.

## 4. Research questions

**Accuracy (benzene to coronene).** Can a per-molecule pipeline — DFT geometry, harmonic Hessian
and anharmonic constants, plus a probed coupled-cluster correction to the harmonic force
constants — produce band positions that measurably improve on scaled-harmonic DFT, on an
in-house ML-calibrated harmonic baseline, and, where its coverage overlaps, on DFT-teacher
machine-learning molecular dynamics, judged per band against laboratory spectra? And, on the two
molecules where the laboratory intensity is calibrated, do its anharmonic intensities improve on
the harmonic ones?

**Cost (every rung that ran).** How many coupled-cluster energies did that correction need per
molecule, and did the off-diagonal count stop growing between naphthalene, the pyrene-size rung
and coronene — measured against the number of couplings the molecule's symmetry leaves free?

**Reach (C₃₈₄H₄₈-class).** Can the same pipeline produce a spectrum with a stated error budget at
a size where no anharmonic or coupled-cluster-quality prediction — and no laboratory spectrum —
exists? Here no "beat" is claimed. And here plan 05 is honest about a hard limit: whole-molecule
probing of a 432-atom molecule with energies only costs at least two energies per vibrational
mode — 2,580 coupled-cluster energies of a very large molecule — and is **not promised**. The
only route by which that cost stops depending on size is to probe the correction on capped
fragments of the flake, which uses a locality-verified electronic correction obtained on one
region for another. The student ruled (decision 1) that this is not a scope question but a
method: if it works and the goal is reached with it, it is used; if the locality measurement at
the middle rungs says it does not, it is not — and the goal, a pipeline that works up to the
largest species, stays in sight either way. The largest species remains a promised object in the
fragment-probed form.

## 5. Approach

### 5.1 The pipeline, per molecule

1. **Geometry, harmonic Hessian and dipole first and second derivatives** at a declared DFT
   level, analytic, on the student's laptop's CPU through coronene (it has no CUDA GPU; any GPU
   work is rented time); DFT cubic and semi-diagonal quartic constants for the scored band
   families and every mode the resonance search couples to them.
2. **Δ₂-probing.** A hashed, ordered set of displacement patterns; at each, the local
   coupled-cluster energy in the frozen spaces of §3.3 and the DFT energy; recovery of the
   correction in the DFT normal-mode basis under the symmetry prior of §3.2; the probe count K
   read by the stopping rule of §3.4. Three licences gate it: an anchor licence against frozen
   noise, bias and threshold formulas; a probing licence at benzene and naphthalene against
   directly computed reference corrections (including a canonical coupled-cluster reference, the
   only one independent of the space freezing); and a locality test computed on directly measured
   Hessian blocks — never on the recovered correction alone, which could certify the locality its
   own prior imposed. Modes that are infrared-inactive by symmetry are not dropped — their
   diagonal costs two energies each and their fundamentals reach the spectrum through
   resonances — but the coupling blocks made only of inactive modes are tested per rung in the
   DFT rehearsal and left out of the deck only where the scored positions do not move (decision
   19).
3. **Spectra** through the resonance-explicit routes plan 04 froze — second-order vibrational
   perturbation theory with explicit resonance treatment — with **no scale factor** on anharmonic
   output. Every spectrum carries positions, anharmonic intensities from the DFT dipole
   derivatives (the same physics PAHdb's intensities rest on, computed anharmonically rather than
   harmonically) and a drawn width at the resolution and temperature of the source it is compared
   with, each labelled with its provenance.
4. **Error budget** per band: DFT level, held-out residual, measured noise floor and
   space-freezing bias, the long-range share of the family's correction, and the matrix–gas shift
   where matrix data is used.

### 5.2 The size ladder (unchanged in species; claim types unchanged)

| Rung | Species | Type | What it licenses in plan 05 |
|---|---|---|---|
| R0 | benzene | accuracy | probing licence against local and canonical references; intensity scored (NIST Quantitative IR series) |
| R1 | naphthalene | accuracy | the noise-floor measurement; the anchor licence; first locality read; intensity scored (PNNL quantitative vapour-phase record, 25 °C, 0.1 cm⁻¹) |
| R2 | pyrene, chrysene, triphenylene (gas-phase data — hot-vapour GC-IR spectra at 8 cm⁻¹, so the C–C families are expected undecidable on this source), tetracene (matrix, plus a jet-cooled band list) | accuracy | first off-diagonal-count ratio; direct-block locality probe; canonical diagonal check |
| R3 | coronene (matrix, plus five jet-cooled 6–15 µm bands) | accuracy | second ratio; the numeric size sentence is decided here |
| R4–R5 | C₅₄–C₂₁₆ class | reach (bonus as spectra; the R4 fragment checks promised conditional on cluster access) | expert-judgment datum; the first rungs where the learned prior, if it earned its licence at R2–R3, may carry the recovery; the fragment-vs-whole comparison on a molecule larger than coronene and the fragment-radius convergence test |
| R6 | C₃₈₄H₄₈-class | reach | fragment-probed only, under a four-part measured licence (locality at R2–R3; coronene probed in fragments reproducing coronene probed whole; the same on a larger molecule where the cluster allows; a fragment-radius convergence test on the flake's own interior); otherwise a per-family or full refusal |

A per-family decidability rule replaces plan 04's rung-level gate: a gas-scored family is
decidable if the scoreboard's **measured band-centre uncertainty** — instrument resolution,
centroid precision and a temperature term — is smaller than its beat margin; a matrix-scored
family passes through the matrix–gas gate or is pre-declared inconclusive. Benzene and
naphthalene are scored unconditionally on room-temperature cell spectra (the NIST Quantitative
series; the PNNL record), with the hot NIST WebBook entries as labelled extra columns. For the
pyrene-size rung, an exhaustive search on 5 September found no room-temperature gas-phase spectrum
of pyrene, chrysene or triphenylene in the 6–15 µm region; it found jet-cooled band lists for
tetracene (Lemmens et al. 2019) and coronene (Lemmens, Rijs & Buma 2021) and one rotationally
resolved cold pyrene band, all now named as labelled cold columns. The C–C stretching families at
R2 are therefore expected to be undecidable by construction, the plan says so before any number
exists, and the student has decided to sign off the scoreboard module with that expected result
rather than wait for a source that may not exist (§13 still asks).

### 5.3 Why the cost is reported and never described; the gradient side project

The plan allows exactly two kinds of cost sentence. The **cost record** — probe count, mode,
prior, noise floor and stopping threshold, wall-clock per probe, the script that printed it — is
promised for every rung that ran. A **size sentence** is numeric only: how the off-diagonal count
went from naphthalene to coronene against how the mode count went and against the free-element
count symmetry leaves. The adjectives "size-independent", "O(1)" and "saturates" are forbidden
everywhere, including this proposal. Any favourable size sentence is expected, if at all, to come
from the prior — symmetry or learned — and not from sparsity as such.

The domain review's reading of the software landscape stands: no production code offers an
analytic nuclear gradient for local CCSD(T), and the project's own measurement shows why the
canonical one is no substitute (a canonical CCSD(T) gradient of benzene costs about fifty
energies and 13.9 GB already at cc-pVDZ; §8). The student's response was not to accept that as a
limit but to build it: a pre-registered **side project** extends the open PySCFAD
implementation of LNO-CCSD(T) gradients by automatic differentiation — demonstrated by its
authors to about 29 atoms — to frozen correlation spaces and PAH sizes. Two arguments, to be
tested by its first milestones, make this engineering rather than new theory: on a surface with
frozen spaces an automatic-differentiation gradient with fixed spaces is the derivative of the
surface actually probed, so the response terms that make general local-CC gradients hard should
not arise; and the fragment structure of the local method should let the memory of reverse-mode
differentiation scale with the largest fragment rather than the molecule. The one physics
question the review put first — whether the frozen space is a smooth function of the nuclei on
the six-fold-symmetric molecules, where a re-localised orbital set would be arbitrary — is
answered for benzene by probe M1 (§3.3), which also showed the arbitrariness directly: two runs
landed the fresh localiser on different, symmetry-equivalent orbital sets at the same geometry,
while the transported set stayed put. The side project has four milestones with printed pass
conditions, its own budget line, a twelve-week checkpoint and a kill criterion. If it succeeds,
the gradient route runs in addition to the energy route on the rungs it licenses — each rung then
carries two cost records — and the size question is also answered on the gradient count; if it
fails, the energy route remains the guaranteed route.

## 6. What this project deliberately does not do, and why

**No transferable, train-once spectrum model** (carried from plan 04; the measured failure of
motif transfer is the reason). Every molecule gets its own probed correction. The Module-05
deep-learning component predicts only *where* the correction is likely to have large
off-diagonal elements, is trained on a public DFT-vs-DFT Hessian corpus, and enters a promised
rung only after a licence: its saving demonstrated on that corpus against the symmetry prior's
free-element count, and its result checked prior-free at that rung. The student ruled more
generally that a rule inherited from an earlier plan carries no authority of its own — knowledge
transfer is allowed wherever a gate shows it makes the pipeline succeed.

**No coupled-cluster anharmonic correction** (§2). **No coupled-cluster correction to
intensities**: the intensities are DFT-level and say so; whether the frozen-space object removes
the discontinuity Madriaga & Crawford found in local-CC field derivatives is a measured question
(the dipole probe M1-μ, owed after the cc-pVTZ scan), and only a printed result can turn it into a
proposal. **No predicted band widths**: widths are drawn at the source's resolution and
temperature and labelled as presentation. **No full coupled-cluster surface or global quartic
force field** (carried). **No new empirical scale factors** (carried; the ML-corrected scaling
baseline is an opponent, not the method). **No light–matter dynamics and no new emission model**
(carried; the published cascade model is inherited post-processing). **No species identification
in JWST spectra** (carried). **No sub-tolerance accuracy language** (carried). **No
whole-molecule probing at C₃₈₄H₄₈** (§4).

## 7. Evaluation design

**What is scored, what is shown.** Band **positions** are the promised quantity and are scored
on every rung where a laboratory band passes the decidability rule. **Intensities** are shown
for every molecule with their provenance and are **scored on benzene and naphthalene** — the two
rungs with calibrated gas-phase intensities — as a second, separately reported quantity: the
integrated band intensity of each scored band, the pipeline's anharmonic value against the
scaled-harmonic baseline's harmonic value and against PAHdb's where it reports one, with the
source's stated intensity uncertainty as tolerance (decision 18). Elsewhere the intensities stand
beside PAHdb's computed ones as a comparison, not a verdict: both are DFT, and no scoreboard
exists. Matrix intensities never score.

**Frozen opponents and pre-registered comparisons** (carried): named, versioned lines; paired
per-band absolute error on identical laboratory bands; band lists, windows and margins frozen in
a dated pilot note written before any pipeline-vs-laboratory number exists. The pilot note is
written with seven inputs in hand — the laboratory side with its measured band uncertainties,
the opponent side, the DFT-only rehearsal with its noise-injected column, the frozen-space probe,
the canonical feasibility probe, a run/no-run gradient check at equilibrium, and the naphthalene
noise-floor measurement with its fits sealed — and **nothing else**. Four of the seven exist
today. The first coupled-cluster correction is computed after the note is committed, so no
stopping constant, probe cap, tolerance or margin can be shaped by a result; the raw displaced
energies of the frozen-space probe are sealed for the same reason, and this proposal quotes only
differences between methods.

**Mandatory null tests** (carried, extended). The Δ=0 arm — DFT harmonic plus DFT anharmonic, no
coupled-cluster correction, scored by the same script on the same bands — must lose the comparison
on every family where "beat" is claimed, or the coupled-cluster claim for that family is void and
reported as explained by DFT-level anharmonicity. A noise-input run must fail the sanity gates.
New in plan 05: a **shuffled-probe null** — the probe responses randomly permuted and fed to the
same solver must fail the probing licence — and a **discriminability clause** — the recovered
correction must beat the zero correction against the reference by a frozen factor. Both exist
because a regularised recovery can be confidently wrong.

**Licensing by measurement** (carried, with frozen formulas). The anchor gate has three formulas,
each with its numbers filled in the pilot note: a noise line, a bias line against a canonical
reference (judged on the composite energy of §3.3), and a threshold-sensitivity line that, if
breached, makes complete-PNO-space extrapolation mandatory at double cost. The probing licence
and the locality test have their own tolerances, all bounded by the smallest beat margin.

**Leakage control** (carried): laboratory values never enter training, validation, stopping,
sampling or pattern design; the calibrated-harmonic baseline is the single declared exception,
evaluated leave-molecule-out.

**Fail-closed reporting** (carried): every rung that does not run, every family that is
undecidable, every gate that breaches has a pre-written sentence, and losing is published with the
same paired table as winning.

## 8. Feasibility and resources — what has been measured

Every cost in the plan is a measured slot reading "not run" until a script prints it. The
literature figures that motivated the design (a hundred-odd gradients for a full Hessian; 30 % of
columns on anthracene; a few micro-hartree of local-correlation noise) are recorded as motivation
and are forbidden in any budget sentence. The following were printed between 5 and 6 September on
the student's laptop (an 8-core Ryzen 7 260, 31 GB, no CUDA GPU; the anchor code runs in a Linux
subsystem given 22 GB; the machine is dedicated to the project and available around the clock).

- **The DFT-only rehearsal (benzene).** The difference between two functionals stood in for the
  correction. 334 displacement pairs, 2 h 30 min. Energy mode recovers the full off-diagonal
  block with per-family errors ≤ 0.43 cm⁻¹ against 7 cm⁻¹ for the diagonal-only recovery;
  gradient mode does the same from 60 gradients. The measured off-diagonal count, 388 energies
  for 435 unknowns, is what §3.2's cost expectation rests on.
- **The frozen-space probe (benzene, cc-pVDZ, two threshold settings, 27 geometries each,
  with a canonical CCSD(T) truth line).** Results in §3.3. Cost: 5–10 minutes per geometry for
  all three arms; the cc-pVTZ scan now running takes about two hours per geometry and 2.5 days in
  all.
- **The canonical reference.** One canonical CCSD(T) energy of benzene at cc-pVTZ: 755 s, 7.3 GB.
  One local LNO-CCSD(T) energy at the same basis: 2,087 s (locality pays only at larger
  molecules). The anchor's bias line — 61 canonical energies along benzene's 30 modes — is
  therefore about 13 hours and **fits the laptop**; the full canonical reference Hessian by
  energies, 1,801 energies or about 378 hours, **does not**, and neither does the gradient
  branch: a canonical CCSD(T) gradient costs 1,399 s and 13.9 GB at cc-pVDZ, about fifty energies,
  and exceeded the memory the laptop can give at cc-pVTZ. The full canonical Hessian at benzene
  is cluster work; the plan already said what the probing licence tests without it.
- **The Module-05 corpus.** A B3LYP Hessian of a QM9-size molecule takes 3–7 minutes here, so the
  aromatic-heavy subset of order a thousand molecules is three days of laptop time.

Still owed before the pilot note: the naphthalene DFT rehearsal (which also admits or refuses the
symmetry prior), the scoreboard re-read with its measured band uncertainties, the run/no-run
gradient check, and the naphthalene noise-floor measurement (72 energies). After the note: the
benzene probe batch and its references, including canonical two-mode points from which the
frozen spaces' off-diagonal bias is read (decision 16); naphthalene; an anthracene
direct-coupling probe as a dated bonus, because anthracene is the first acene where DFT's
delocalisation error is visible; then classification of the pyrene- and coronene-size batches as
laptop or cluster work by an arithmetic rule (168 hours of wall-clock per batch is the line). The
domain review priced plan 05's own probes as cheaper than plan 04's first factory batch, and the
measurements so far agree.

Human hours are logged and not capped. Laptop wall-clock carries checkpoints that force dated
decisions. Cluster node-hours and rented GPU-hours get no number until access, a timed probe on
the actual machine, and a per-rung cap exist in writing. The C₃₈₄H₄₈-class DFT Hessian is itself
a cluster object.

## 9. Review status

Four review rounds — each a cold read by a fresh reader and an adversarial domain review with
literature access — were run on 3 and 4 September. The first domain review returned a
**conditional verdict**: a green light for the benzene–naphthalene measurement programme once six
blocking items were written in, and no green light for the promised set *as it was then worded*,
which promised a coupled-cluster anharmonic correction the probes could not build, hung its cost
question on a gradient that does not exist in production codes, and treated the largest species
as a whole-molecule object. The student's decisions of 4 September (§10, items 1–7) re-worded the
set; the second domain review then gave a green light for the pre-pilot-note programme and the
benzene and naphthalene rungs once four in-spec items were written in (a reproducible estimator
for the noise gate; a noise-aware stopping rule; an absolute agreement metric for the locality
couplings; a feasibility probe for the canonical reference) and withheld it for the pyrene and
coronene rungs on two points — the fragment licence and the gas-phase decidability of the C–C
families — both closed in spec the same day. The third and fourth rounds re-read those closures
(seventeen of eighteen held, then twelve of twelve) and changed the design in seven places, all in
the text: paired displacements so that the coupled-cluster force at the DFT geometry cancels;
frozen spaces transported by projection rather than re-localised; only benzene scored
unconditionally until the room-temperature naphthalene source was found; noise injected per
energy in the rehearsal; the shared reference energy's offset identified from a second
displacement amplitude; a first-order geometry term on every scored band; and the PNNL naphthalene
source itself.

The review loop was **closed on 4 September** after a seam check of the last patch (19 seams, all
mechanical). The plan's text has been frozen since; it changes only by dated notes naming a
measurement or a decision, and the ladder document carries every such note. The remaining risk
is retired by measurements, not by further reading; §8 lists the first of them.

## 10. Decisions the student made (all closed; a supervisor's objection would reopen any of them)

**4 September 2026.**
1. Fragment probing at the largest sizes is a permitted method, used if the locality measurement
   at the middle rungs licenses it; the C₃₈₄H₄₈-class deliverable is a fragment-probed spectrum,
   or the measured reason it could not be produced.
2. Every plan version stays in the repository as a read-only record.
3. The R2 scored set: triphenylene is scored on its gas-phase families; tetracene is matrix-only
   and gated (a jet-cooled band list added since as a cold column).
4. The Module-05 target: a Transformer predicting the support of the correction, trained on an
   aromatic-heavy subset of the public Hessian QM9 set with recomputed B3LYP Hessians; success is
   the measured saving and the per-rung licence, not accuracy.
5. The re-worded promised set: the harmonic-only correction; the energy route as the guaranteed
   route but not as a limit, the gradient route built in the side project.
6. The development machine: the student's current laptop; a replacement only if a probe shows it
   necessary.
7. Nothing has been submitted to the programme; an unsubmitted draft on QM9 is renamed so the
   Module-05 corpus carries no reuse exposure.

**5–6 September 2026, after the first measurements.**
8. The stopping rule reads the off-diagonal residual.
9. Its threshold carries the model floor.
10. The off-diagonal noise requirement is measured per rung; if exceeded, the gradient route is
    load-bearing for the couplings.
11. The structural prior is the symmetry prior, entering the deck after the naphthalene rehearsal.
12. The rehearsal's former fixed reading threshold is retired; the stopping constant is calibrated
    on the off-diagonal residual.
13. Mode E is budgeted at M(M−1)/2 energies where no prior bites and at the symmetry prior's
    free-element count where it applies; the learned prior is measured against that count.
14. The frozen-space object's transported blocks are semicanonicalised at each geometry.
15. The energy the object reports is the composite local-CCSD(T) + [MP2(full) − MP2(local)].
16. The cc-pVTZ frozen-space scan with its canonical truth line runs (started 6 September); the
    benzene probe batch includes canonical two-mode points for the off-diagonal bias.
17. Module 07's agent runs on LangGraph (admissible through the programme's LangChain/LangGraph
    elective) with the Anthropic API as model endpoint, model id logged.
18. Intensities are scored on benzene and naphthalene as a second quantity; positions remain the
    primary claim; no coupled-cluster intensity correction is promised; the dipole probe M1-μ
    decides whether one can be proposed; widths are drawn, not predicted.
19. Coupling blocks made only of infrared-inactive modes are tested per rung and dropped only
    where the scored positions do not move.

## 11. Risks

1. **Frozen-space energies are not smooth enough for energy-only probing.** Measured at benzene in
   cc-pVDZ: they are, by two orders of magnitude (§3.3). Remaining exposure: the anchor basis
   (scan running) and larger molecules (the naphthalene noise-floor measurement); a promised mode
   that carries no accuracy claim where the measurement fails; the gradient route as the labelled
   fallback for the couplings (decision 10).
2. **The correction is not near-diagonal in the DFT mode basis on aromatic ring modes.** Measured
   at benzene: it is not, and the couplings follow symmetry, not frequency. Response: the symmetry
   prior; the rehearsal on a functional pair that brackets exact exchange; the diagonal-only and
   full recoveries printed side by side at benzene and naphthalene.
3. **The correction is not local, or is local for C–H modes and not for the delocalised C–C
   families the astronomy needs.** Response: locality measured on directly computed blocks per
   family, the anthracene probe, and a pre-registered per-family losing condition that withdraws
   the reach story for exactly those families.
4. **The coupled-cluster harmonic correction does not beat calibrated harmonics.** The opponents'
   fitted scale factors already absorb the mean of a harmonic difference that one naphthalene study
   puts near 5 cm⁻¹ (carried at snippet grade until the full text is read); what remains to buy is
   the per-family scatter. Response: the expected-effect line is written into the pilot note
   before any result, and losing is publishable.
5. **Laboratory decidability.** The per-family rule pre-declares undecidable families
   inconclusive. The pyrene-size rung's C–C families are in that class on every source found by an
   exhaustive search; the cold jet-cooled lists for tetracene and coronene are scored as labelled
   columns. Only a new gas-phase source changes this (§13).
6. **Off-diagonal probing is expensive without a prior.** Measured: 0.9 energies per unknown at
   benzene. Response: the symmetry prior (decision 11) with its per-rung free-element count printed
   beside the probe count; the learned prior of Module 05 measured against the same count; the
   168-hour rule classifies any rung the prior does not rescue as cluster work rather than
   quietly overrunning.
7. **The side project becomes a time sink** — the failure mode that ended plan 01. Response: its
   own budget line, a twelve-week checkpoint, a kill criterion frozen in advance, and a four-weekly
   alarm that forces a written review if its hours outgrow the pipeline's infrastructure bucket.
8. **Operational.** The first week produced two lost runs (a memory ceiling set too high; a
   machine switched off with a job running). Both are now rules in the budget document: a memory
   ceiling with headroom for the host, one anchor job at a time, every long run announced with
   its end time and written out point by point so an interruption costs one point.

## 12. Fit to the capstone programme

Each module is mapped onto a load-bearing pipeline artifact: the opponent atlas (Module 02); the
laboratory scoreboard with the measured band-centre uncertainties and, for benzene and
naphthalene, the calibrated intensities (Module 03); the calibrated-harmonic baseline (Module
04); the campaign officer that enforces the budget rules and the two permitted cost sentences,
built on LangGraph with the Anthropic API and every refusal logged (Module 07); and the assembled
pipeline with its scored ladder and cost records (Module 08). Two modules — the deep-learning
support predictor (Module 05) and the generative pattern proposer (Module 06) — are honest
efficiency experiments on the off-diagonal probe count, run on DFT-only corpora at zero
coupled-cluster cost and measured against the symmetry prior's free-element count; the
deep-learning model is measured on the accuracy rungs and, if it earns its licence there, becomes
load-bearing on the reach rungs — the mapping says exactly that rather than pretending otherwise.
Module deadlines are administrative facts; a module may ship an honest fail-closed state to meet
its date, and the science continues past it.

## 13. What is asked of the supervisor

1. A critical reading of §2–§3 (why the coupled-cluster budget moves to the harmonic correction,
   why it is recovered by probing under a symmetry prior, and what the first measurements say) and
   of §7 (the evaluation contract) — the places where the plan's honesty either holds or does not.
2. A view on the fragment-probing route to the largest sizes (§4) and on the Module-05 target
   (§10, item 4), both decided by the student as methods subject to measurement — a supervisor's
   objection would reopen either — and on the side project of §5.3, which is where the plan's
   ambition and its main time risk both sit.
3. **Laboratory sources.** Gas-phase or jet-cooled spectra of pyrene, chrysene and triphenylene
   **in the 6–15 µm region** at better than 8 cm⁻¹ resolution and known temperature would make the
   C–C families at the pyrene-size rung decidable. An exhaustive search on 5 September found none
   at room temperature (it found the tetracene and coronene jet-cooled lists now in the plan and one
   cold pyrene band); a source the supervisor knows of that the search missed would enlarge the
   decidable set, and the plan is written so that it can be added before, never after, a comparison
   is scored.
4. A view on the intensity question (§7): positions are the promise, intensities are scored where
   a calibrated gas-phase measurement exists and reported elsewhere, and a coupled-cluster
   correction to intensities is a measured question rather than a promise. If the supervisor wants
   intensities carried further, the dipole probe M1-μ is the measurement that would license it.
5. When the naphthalene measurements justify it: sponsorship of a cluster-time request sized by
   the timed probes, and, at the large-rung stage, serving as or nominating the named expert whose
   pre-registered judgment is the honest datum where no laboratory truth exists.

## 14. References

Verification status is tracked per item in the working bibliography of this folder; every
identifier is re-verified against the primary source before it appears in any scored document.
New to plan 05, verified by Crossref, arXiv or full text on 3 September 2026:

- Altun, A., Ghosh, S., Riplinger, C., Neese, F., Bistoni, G. 2021, J. Phys. Chem. A 125, 9932.
  DOI 10.1021/acs.jpca.1c09106. (Local-approximation error grows with acene length; CPS
  extrapolation.)
- Bégué, D., Carbonnière, P., Pouchan, C. 2005, J. Phys. Chem. A 109, 4611.
  DOI 10.1021/jp0406114. (Hybrid CC-quadratic / DFT-anharmonic force field.)
- Esposito, V. J., Fortenberry, R. C., Boersma, C., Allamandola, L. J. 2024, J. Chem. Phys. 160,
  211101. DOI 10.1063/5.0208597. (CCSD(T)-F12b harmonics with a DFT QFF on naphthalene.)
- Kitzmiller, N. L., Lahm, M. E., Olive Dornshuld, L. N., Jin, J., Allen, W. D., Schaefer, H. F.
  2024, J. Chem. Theory Comput. 20, 10886. DOI 10.1021/acs.jctc.4c01240. (CMA-2.)
- Lahm, M. E., Kitzmiller, N. L., Mull, H. F., Allen, W. D., Schaefer, H. F. 2022, J. Am. Chem.
  Soc. 144, 23271. DOI 10.1021/jacs.2c11158. (Concordant Mode Approach.)
- Madriaga, J. P., Crawford, T. D. 2025, J. Phys. Chem. A 129, 10014.
  DOI 10.1021/acs.jpca.5c05210. (PNO discontinuities in finite-difference properties.)
- Sanders, J. N., Andrade, X., Aspuru-Guzik, A. 2015, ACS Cent. Sci. 1, 24. DOI 10.1021/oc5000404.
  (Compressed-sensing Hessians; polyacenes.)
- Wang, B., Luo, S., Wang, Z., Liu, W. 2025, J. Chem. Theory Comput. 21, 10893.
  DOI 10.1021/acs.jctc.5c01354. (O1NumHess.)
- Williams, N. J., Kabalan, L., Stojanovic, L., Zolyomi, V., Pyzer-Knapp, E. O. 2024,
  arXiv:2408.08006. (Hessian QM9.)
- Zhang, X., et al. 2024, arXiv:2404.03129. (Automatic-differentiation gradients for local coupled
  cluster, PySCFAD.)

Laboratory sources named on 4–5 September 2026 (Crossref records verified; full texts are read by
the scoreboard module before any band uncertainty is printed, and are marked so in the working
bibliography):

- Chu, P. M., Guenther, F. R., Rhoderick, G. C., Lafferty, W. J. 1999, J. Res. Natl. Inst. Stand.
  Technol. 104, 59. DOI 10.6028/jres.104.004. (The NIST Quantitative Infrared Database — the
  benzene cell spectra and their conditions.)
- Schneider, S., et al. 2024, J. Quant. Spectrosc. Radiat. Transfer 323, 109045.
  DOI 10.1016/j.jqsrt.2024.109045. (Quantitative vapour-phase spectra of solids, naphthalene among
  them, 25 °C, 0.1 cm⁻¹.)
- Sharpe, S. W., Johnson, T. J., Sams, R. L., Chu, P. M., Rhoderick, G. C., Johnson, P. A. 2004,
  Appl. Spectrosc. 58, 1452. DOI 10.1366/0003702042641281. (The PNNL gas-phase quantitative IR
  database.)
- Pirali, O., Vervloet, M., Mulas, G., Malloci, G., Joblin, C. 2009, Phys. Chem. Chem. Phys. 11,
  3443. DOI 10.1039/b814037e. (Naphthalene hot-band spectroscopy; the temperature term.)
- Joblin, C., Boissel, P., Léger, A., d'Hendecourt, L., Défourneau, D. 1995, Astron. Astrophys.
  299, 835. (PAH band shifts with temperature; reference known, not yet opened.)
- Lemmens, A. K., et al. 2019, Astron. Astrophys. 628, A130. DOI 10.1051/0004-6361/201935631.
  (Jet-cooled mid-infrared band list of tetracene.)
- Lemmens, A. K., Rijs, A. M., Buma, W. J. 2021, Astrophys. J. 923, 238.
  DOI 10.3847/1538-4357/ac2f9d. (Jet-cooled far- and mid-infrared spectra of coronene and larger
  PAHs.)
- Brumfield, B. E., Stewart, J. T., McCall, B. J. 2012, J. Phys. Chem. Lett. 3, 1985.
  DOI 10.1021/jz300769k. (One rotationally resolved cold band of pyrene near 8.5 µm.)

Carried from plan 04 (verification status as recorded there): Bauschlicher et al. 2018; Boese,
Klopper & Martin 2005; Bos et al. 2025; Chen, Li & Li 2026; Hudgins & Sandford 1998; Käser &
Meuwly 2021; Lam, Abdul-Al & Allouche 2020; Mai et al. 2025; Mattioda et al. 2020; Mulas, Falvo,
Cassam-Chenaï & Joblin 2018; Ricca et al. 2026; Sylvetsky et al. 2020; Tang et al. 2025; NIST
CCCBDB; Zapata Trujillo & McKemmish 2022.
