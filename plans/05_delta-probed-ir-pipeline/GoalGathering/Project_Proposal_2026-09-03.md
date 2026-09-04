# Probed coupled-cluster corrections to the harmonic force constants of polycyclic aromatic hydrocarbons: an infrared pipeline with a measured cost

**Master's capstone project proposal — plan 05**
Prepared for supervision review, 3 September 2026. Supersedes the plan-04 proposal of the
same date. Companion documents: this proposal summarises a frozen plan and explains *why* its
major decisions were taken; the binding technical documents (goal, ladder, tolerances,
opponents, gates, budget, mapping) live in the same folder and take precedence where they are
more specific. Two external reviews of this plan (a cold read and an adversarial domain
review, both on 3 September 2026) are in the folder with every finding and its closure; the
domain review's verdict was conditional, and §9 says on what.

---

## 1. Summary

Infrared band positions of polycyclic aromatic hydrocarbons (PAHs) underpin the interpretation
of the aromatic infrared bands JWST now resolves. The reference predictions — most prominently
the NASA Ames PAH IR Spectroscopic Database (PAHdb) — rest on scaled harmonic DFT, whose
systematic uncertainties its own current paper calls "currently unquantified" (Ricca et al.
2026). This project builds and tests one pipeline: any individual neutral aromatic molecule
in, an infrared absorption spectrum out, with the **harmonic force constants corrected to
coupled-cluster quality** and a measured error budget on every claimed band.

Plan 04, reviewed in the previous round, obtained its coupled-cluster anchor by learning a
per-molecule potential-energy surface from thousands of local coupled-cluster points. Its
domain review accepted the criterion and found the cost unaffordable at the sizes that matter.
Plan 05 keeps plan 04's criterion, opponents, laboratory scoreboards, gates and honesty rules
unchanged and replaces one thing: instead of learning a surface, it **probes the difference**
between the local coupled-cluster and DFT force constants — a small, smooth quantity — with a
hashed set of simultaneous multi-atom displacements, and recovers that difference by sparse
recovery in the DFT normal-mode basis. The number of coupled-cluster energies each molecule
needed is measured and reported beside its spectrum. Whether that number stops growing with
molecule size is a pre-registered measurement with a stated losing condition, not a claim.

The success criterion remains relative and measured: on small and medium PAHs the pipeline's
band positions are compared per band against named, version-frozen state-of-the-art
predictions under a pre-registered protocol; on the largest species the deliverable is a
spectrum with a labelled error budget and no accuracy claim. The project is as much about the
evaluation discipline — pre-registration, frozen baselines, mandatory null tests, fail-closed
reporting — as about the spectra themselves.

## 2. Why the coupled-cluster budget moves from the surface to the correction

Three facts, two of them measured in this project's own history and one from the literature,
drove the change.

First, the arithmetic of plan 04. Coronene has 102 vibrational coordinates; a learned surface
over them needs, by the source conversation's own estimate, of order 10⁴ local coupled-cluster
points — thousands of node-hours per molecule, on an allocation that does not yet exist. The
plan-04 domain review made this a blocking finding. No timed point has ever been run under any
plan, so this is an expectation, not a measurement; but every estimate points the same way.

Second, what a coupled-cluster anchor actually adds. Almost all of a PAH's potential-energy
surface is already described at DFT quality. The only new information the expensive method
supplies is the *difference* between the two surfaces, and near equilibrium that difference is
small and smooth. Paying coupled-cluster prices to relearn the DFT part is where plan 04's
cost went.

Third, where the difference pays. The hybrid quartic-force-field literature (Boese, Klopper &
Martin 2005; Bégué, Carbonnière & Pouchan 2005; and, on naphthalene, Esposito et al. 2024) puts
the coupled-cluster level in the **harmonic** constants and leaves cubic and quartic constants
at DFT level. Plan 04 had it the other way round. Plan 05 corrects the harmonic force
constants only — the object called Δ₂ in the technical documents — and lets DFT supply the
anharmonic constants. The domain review sharpened this further: energy-only probing cannot
produce the three-index cubic constants that PAH combination-band resonances need, so a
coupled-cluster anharmonic correction was not merely unnecessary but unbuildable with the
probes specified. It was removed from the promised set; a cheap probe of the diagonal cubic
correction remains, as a reported number that will show how much was given up.

## 3. How the correction is recovered, and why in this form

A force-constant correction that is short-ranged in real space has two exploitable
structures: it is sparse in an atom-local basis, and its blocks between distant atom groups
are of low rank. Two published methods exploit exactly these structures to recover a *full*
Hessian from far fewer calculations than one per coordinate: O1NumHess (Wang et al. 2025), which
recovers a Hessian from a number of gradients that saturates around a hundred for molecules of
hundreds of atoms, and compressed-sensing recovery in a cheap method's eigenbasis (Sanders,
Andrade & Aspuru-Guzik 2015), which on anthracene needed 30 % of the Hessian columns and whose
cost grew only logarithmically across polyacenes of one to fifteen rings. Neither has been
applied to a coupled-cluster-minus-DFT difference.

The domain review established that the *diagonal* part of this idea is not new: the Concordant
Mode Approach (Lahm et al. 2022; Kitzmiller et al. 2024) computes CCSD(T) force constants along
DFT normal modes from single-point energies and adds selected off-diagonal elements by a cheap
diagnostic. It is cited as prior art throughout the plan, and its own result — that
diagonal-only recovery fails on aromatic ring modes by up to ±28 cm⁻¹, because DFT and
coupled-cluster mode compositions differ there — is the strongest evidence for the plan's
design choices. What plan 05 proposes beyond CMA: local coupled cluster with frozen correlation
domains at PAH sizes; the off-diagonal block recovered by a **frequency-banded** sparse solve
from multi-mode patterns rather than one element at a time; the recovery licensed against
directly computed references; and the locality of the correction, and the number of
off-diagonal probes it needs, measured as a function of size.

Two further design choices follow from the reviews and are worth stating plainly. The probe
patterns are consumed in a hashed order fixed before any response exists, so the reported
probe count is a measurement and not a choice. And the coupled-cluster energies at displaced
geometries are computed with the local-correlation domains frozen at the equilibrium geometry,
because domain changes on displacement produce micro-hartree discontinuities — the same
mechanism Madriaga & Crawford (2025) showed destroys finite-difference field properties. The
domain review derived the noise floor this imposes (a per-point scatter below roughly
0.8 × tolerance × step², i.e. a few micro-hartree at practical steps) and noted that fixing PNO
dimensions did not remove the discontinuities in that study. Whether small nuclear
displacements behave better is unknown. It is therefore the **first measurement** the plan
makes at naphthalene, before anything else is committed, and the pipeline's promised mode
carries no accuracy claim at any size where that measurement fails.

## 4. Research questions

**Accuracy (benzene to coronene).** Can a per-molecule pipeline — DFT geometry, harmonic
Hessian and anharmonic constants, plus a probed coupled-cluster correction to the harmonic
force constants — produce band positions that measurably improve on scaled-harmonic DFT, on an
in-house ML-calibrated harmonic baseline, and, where its coverage overlaps, on DFT-teacher
machine-learning molecular dynamics, judged per band against laboratory spectra?

**Cost (every rung that ran).** How many coupled-cluster energies did that correction need per
molecule, and did the off-diagonal count stop growing between naphthalene, the pyrene-size
rung and coronene?

**Reach (C₃₈₄H₄₈-class).** Can the same pipeline produce a spectrum with a stated error budget
at a size where no anharmonic or coupled-cluster-quality prediction — and no laboratory
spectrum — exists? Here no "beat" is claimed. And here plan 05 is honest about a hard limit:
whole-molecule probing of a 432-atom molecule with energies only costs at least two energies
per vibrational mode — 2,580 coupled-cluster energies of a very large molecule — and is **not
promised**. The only route by which that cost stops depending on size is to probe the
correction on capped fragments of the flake, which uses a locality-verified electronic
correction obtained on one region for another. Whether that counts as the kind of transfer the
project forbids is a scope decision the student has not yet made (§10); the plan is written so
that either answer is honest.

## 5. Approach

### 5.1 The pipeline, per molecule

1. **Geometry, harmonic Hessian and dipole derivatives** at a declared DFT level, analytic, on
   a GPU where the deck names one; DFT cubic and semi-diagonal quartic constants for the scored
   band families and every mode the resonance search couples to them.
2. **Δ₂-probing.** A hashed, ordered set of displacement patterns; at each, local coupled
   cluster and DFT with frozen domains; sparse recovery of the correction in the DFT
   normal-mode basis with a frequency-banded structural prior; the probe count K is the number
   at which a held-out residual first meets a target frozen before any coupled-cluster response
   exists. Three licences gate it: an anchor licence against frozen noise, bias and threshold
   formulas; a probing licence at benzene and naphthalene against directly computed reference
   corrections (including a canonical coupled-cluster reference, the only one independent of
   the domain freezing); and a locality test computed on directly measured Hessian blocks —
   never on the recovered correction alone, which could certify the locality its own prior
   imposed.
3. **Spectra** through the resonance-explicit routes plan 04 froze; no scale factor on
   anharmonic output.
4. **Error budget** per band: DFT level, held-out residual, measured noise floor and
   domain-freezing bias, the long-range share of the family's correction, and the matrix–gas
   shift where matrix data is used.

### 5.2 The size ladder (unchanged in species; claim types unchanged)

| Rung | Species | Type | What it licenses in plan 05 |
|---|---|---|---|
| R0 | benzene | accuracy | probing licence against local and canonical references; the DFT-only dry run |
| R1 | naphthalene | accuracy | the noise-floor measurement; the anchor licence; first locality read |
| R2 | pyrene, chrysene, triphenylene (gas-phase data), tetracene (matrix only) | accuracy | first off-diagonal-count ratio; direct-block locality probe; canonical diagonal check |
| R3 | coronene | accuracy | second ratio; the numeric size sentence is decided here |
| R4–R5 | C₅₄–C₂₁₆ class | reach (bonus) | expert-judgment datum; the learned-prior experiment |
| R6 | C₃₈₄H₄₈-class | reach | fragment-probed only, if the student decides fragments in; otherwise a refusal |

One change to R2 was forced by the project's own measurement: plan 04 had excluded
triphenylene as having no laboratory spectrum, but plan 04's NIST coverage probe found
gas-phase spectra for pyrene, chrysene and triphenylene and none for tetracene. Plan 05
scores triphenylene on its gas-phase families and gates tetracene fully. A per-family
decidability rule replaces plan 04's rung-level gate: a gas-scored family is decidable if the
measured spectral grid is finer than its beat margin; a matrix-scored family passes through the
matrix–gas gate or is pre-declared inconclusive.

### 5.3 Why the cost is reported and never described

The plan allows exactly two kinds of cost sentence. The **cost record** — probe count, mode,
prior, residual target, wall-clock per probe, the script that printed it — is promised for
every rung that ran. A **size sentence** is numeric only: how the off-diagonal count went from
naphthalene to coronene against how the mode count went. The adjectives "size-independent",
"O(1)" and "saturates" are forbidden everywhere, including this proposal. The reason is the
domain review's reading of the software landscape: no production code offers an analytic
nuclear gradient for local CCSD(T), so the gradient-based route on which an O(1) probe count
would rest is a bonus, not the plan. The promised route is energy-only, its diagonal part costs
two energies per mode by construction, and the honest question is whether the off-diagonal
part saturates. That question has a pre-registered losing condition and the plan reports
whichever answer it gets.

## 6. What this project deliberately does not do, and why

**No transferable, train-once spectrum model** (carried from plan 04; the measured failure of
motif transfer is the reason). Every molecule gets its own probed correction. The Module-05
deep-learning component predicts only *where* the correction is likely to have large
off-diagonal elements, is trained on a public DFT-vs-DFT Hessian corpus, and never enters a
promised rung.

**No coupled-cluster anharmonic correction** (§2). **No full coupled-cluster surface or global
quartic force field** (carried). **No new empirical scale factors** (carried; the ML-corrected
scaling baseline is an opponent, not the method). **No light–matter dynamics and no new
emission model** (carried; the published cascade model is inherited post-processing). **No
species identification in JWST spectra** (carried). **No sub-tolerance accuracy language**
(carried). **No whole-molecule probing at C₃₈₄H₄₈** (§4).

## 7. Evaluation design

The evaluation contract is inherited from plan 04 and was tightened by both reviews.

**Frozen opponents and pre-registered comparisons** (carried): named, versioned lines; paired
per-band absolute error on identical laboratory bands; band lists, windows and margins frozen
in a dated pilot note written before any pipeline-vs-laboratory number exists. Plan 05 adds a
rule about the pilot note's inputs: it is written with the laboratory side, the opponent side,
a DFT-only dry run of the probing machinery, the noise-floor measurement and single-point
timings in hand — and **nothing else**. The first coupled-cluster correction is computed after
the note is committed, so no residual target, probe cap, tolerance or margin can be shaped by
a result.

**Mandatory null tests** (carried, extended). The Δ=0 arm — DFT harmonic plus DFT anharmonic,
no coupled-cluster correction, scored by the same script on the same bands — must lose the
comparison on every family where "beat" is claimed, or the coupled-cluster claim for that
family is void and reported as explained by DFT-level anharmonicity. A noise-input run must
fail the sanity gates. New in plan 05: a **shuffled-probe null** — the probe responses randomly
permuted and fed to the same solver must fail the probing licence — and a **discriminability
clause** — the recovered correction must beat the zero correction against the reference by a
frozen factor. Both exist because a regularised recovery can be confidently wrong.

**Licensing by measurement** (carried, with frozen formulas). The plan-04 domain review noted
that its anchor gate could not breach because it had no threshold. Plan 05's anchor gate has
three formulas, each with its numbers filled in the pilot note: a noise line, a bias line
against a canonical reference, and a threshold-sensitivity line that, if breached, makes
complete-PNO-space extrapolation mandatory at double cost. The probing licence and the locality
test have their own tolerances, all bounded by the smallest beat margin.

**Leakage control** (carried): laboratory values never enter training, validation, stopping,
sampling or pattern design; the calibrated-harmonic baseline is the single declared exception,
evaluated leave-molecule-out.

**Fail-closed reporting** (carried): every rung that does not run, every family that is
undecidable, every gate that breaches has a pre-written sentence, and losing is published with
the same paired table as winning.

## 8. Feasibility and resources

Every cost in the plan is a measured slot reading "not run" until a script prints it. The
literature figures that motivated the design (a hundred-odd gradients for a full Hessian;
30 % of columns on anthracene; a few micro-hartree of local-correlation noise) are recorded as
motivation and are forbidden in any budget sentence.

The escalation path is unchanged in kind — the student's current laptop first (an 8-core
Ryzen 7 260 with integrated graphics and no CUDA-class GPU, so GPU work is rented time), then
a justified, probe-backed request for cluster or rented GPU time — but the first steps are cheaper and more decisive
than plan 04's. Before any pilot note is written: a DFT-only dry run of the whole probing
machinery at any size the laptop affords; a probe of which codes offer gradients at the anchor
level, with memory; one timed coupled-cluster point; and the naphthalene noise-floor
measurement (about thirty energies). After the note: the benzene probe batch and its references
(the only rung where a canonical coupled-cluster Hessian is certainly affordable); naphthalene;
an anthracene locality probe of about 130 energies as a dated bonus, because anthracene is the
first acene where DFT's delocalisation error is visible; then classification of the pyrene- and
coronene-size batches as laptop or cluster work by an arithmetic rule. The domain review priced
plan 05's own probes as cheaper than plan 04's first factory batch, and placed coronene's
energy-only count at a few hundred energies plus the unknown off-diagonal part — a factor
thirty to fifty below plan 04's asserted 10⁴, before that unknown is measured.

Human hours are logged and not capped. Laptop wall-clock carries checkpoints that force dated
decisions. Cluster node-hours and rented GPU-hours get no number until access, a timed probe
on the actual machine, and a per-rung cap exist in writing. The C₃₈₄H₄₈-class DFT Hessian is
itself a cluster object.

## 9. Review status and the conditions on the green light

The cold read (Round 7, Pass A) found ten blocking and eleven non-blocking issues, all
addressed the same day; the domain reviewer confirmed the patches held. The domain review
(Round 7, Pass B) returned a **conditional verdict**: a green light for the benzene–naphthalene
measurement programme once six blocking items were written in, and no green light for the
promised set *as it was then worded* — which promised a coupled-cluster anharmonic correction
the probes could not build, hung its cost question on a gradient that does not exist in
production codes, and treated the largest species as a whole-molecule object. All six items are
now written into the frozen documents in the form the reviewer specified; the re-worded
promised set — harmonic correction only, energy-only probing as the promised route, the
largest species dependent on the fragment decision — is the set the reviewer described as "not
a mistake relative to plan 04". Whether to adopt that re-worded set is the student's decision
(§10), and this proposal is written for it. The reviewer's own words on the cheapest
measurements that would settle whether the plan is a mistake are the first five owed probes.

## 10. Decisions the student has not yet made

Listed here because a supervisor's view on them is more useful before than after.

1. **Fragment probing at the largest sizes** — in or out. It decides whether the project's
   final deliverable at C₃₈₄H₄₈-class size is a spectrum or an explicit refusal. Both are
   honest outcomes under the plan; only one reaches the territory the project exists for.
2. **The Module-05 target** — a Transformer predicting the support of the correction on a
   public DFT-vs-DFT Hessian corpus, never used on a promised rung. If that is judged too far
   from the science, the module becomes a demonstration and is defended as one.
3. ~~The R2 scored set~~ — decided 4 September 2026: triphenylene is scored on its gas-phase
   families; tetracene is matrix-only and gated.
4. **Adoption of the re-worded promised set** of §9.
5. ~~Whether to remove the plan-04 folder~~ — decided 4 September 2026: every plan version stays
   in the repository as a read-only record, so a reader can follow the whole history.

## 11. Risks

1. **Frozen-domain energies are not smooth enough for energy-only probing.** The published
   analogue (field derivatives) failed even with fixed PNO dimensions. Response: the first
   measurement of the plan, at naphthalene, before anything else; a promised mode that carries
   no accuracy claim where it fails; gradient-based and extrapolated routes as labelled
   fallbacks.
2. **The correction is not near-diagonal in the DFT mode basis on aromatic ring modes.** The
   Concordant Mode Approach's own result says it is not. Response: the banded prior, the
   dry-run calibration on a functional pair that brackets exact exchange, the diagonal-only and
   full recoveries printed side by side at benzene and naphthalene.
3. **The correction is not local, or is local for C–H modes and not for the delocalised C–C
   families the astronomy needs.** Response: locality measured on directly computed blocks per
   family, the anthracene probe, and a pre-registered per-family losing condition that
   withdraws the reach story for exactly those families.
4. **The coupled-cluster harmonic correction does not beat calibrated harmonics.** The
   opponents' fitted scale factors already absorb the mean of a ~5 cm⁻¹ harmonic difference;
   what remains to buy is the per-family scatter. Response: the expected-effect line is written
   into the pilot note before any result, and losing is publishable.
5. **Laboratory decidability** (carried): the per-family rule pre-declares undecidable
   families inconclusive; gas-phase or jet-cooled sources beyond PAHdb and the NIST WebBook
   would enlarge the decidable set.

## 12. Fit to the capstone programme

Each module is mapped onto a load-bearing pipeline artifact: the opponent atlas; the
laboratory scoreboard with the measured matrix tolerance and gas grids; the calibrated-harmonic
baseline; the campaign officer that enforces the budget rules and the two permitted cost
sentences; and the assembled pipeline with its scored ladder and cost records. Two modules —
the deep-learning support predictor and the generative pattern proposer — are honest efficiency
experiments on the off-diagonal probe count, run on DFT-only corpora at zero coupled-cluster
cost and kept off the promised path; the mapping says so rather than pretending otherwise, and
the first of them is one of the decisions in §10. Module deadlines are administrative facts; a
module may ship an honest fail-closed state to meet its date, and the science continues past it.

## 13. What is asked of the supervisor

1. A critical reading of §2–§3 (why the coupled-cluster budget moves to the harmonic
   correction, and why it is recovered by probing) and of §7 (the evaluation contract) — the
   places where the plan's honesty either holds or does not.
2. A view on the two decisions in §10 that shape the deliverable: fragment probing at the
   largest sizes, and the Module-05 target.
3. Advice on laboratory sources: gas-phase or jet-cooled spectra for tetracene- and
   coronene-class species would directly enlarge the decidable set.
4. When the naphthalene measurements justify it: sponsorship of a cluster-time request sized
   by the timed probes, and, at the large-rung stage, serving as or nominating the named expert
   whose pre-registered judgment is the honest datum where no laboratory truth exists.

## 14. References

Verification status is tracked per item in the working bibliography of this folder; every
identifier is re-verified against the primary source before it appears in any scored document.
New to plan 05, all verified by Crossref, arXiv or full text on 3 September 2026:

- Altun, A., Ghosh, S., Riplinger, C., Neese, F., Bistoni, G. 2021, J. Phys. Chem. A 125,
  9932. DOI 10.1021/acs.jpca.1c09106. (Local-approximation error grows with acene length;
  CPS extrapolation.)
- Bégué, D., Carbonnière, P., Pouchan, C. 2005, J. Phys. Chem. A 109, 4611.
  DOI 10.1021/jp0406114. (Hybrid CC-quadratic / DFT-anharmonic force field.)
- Esposito, V. J., Fortenberry, R. C., Boersma, C., Allamandola, L. J. 2024, J. Chem. Phys.
  160, 211101. DOI 10.1063/5.0208597. (CCSD(T)-F12b harmonics with a DFT QFF on naphthalene.)
- Kitzmiller, N. L., Lahm, M. E., Olive Dornshuld, L. N., Jin, J., Allen, W. D., Schaefer,
  H. F. 2024, J. Chem. Theory Comput. 20, 10886. DOI 10.1021/acs.jctc.4c01240. (CMA-2.)
- Lahm, M. E., Kitzmiller, N. L., Mull, H. F., Allen, W. D., Schaefer, H. F. 2022, J. Am. Chem.
  Soc. 144, 23271. DOI 10.1021/jacs.2c11158. (Concordant Mode Approach.)
- Madriaga, J. P., Crawford, T. D. 2025, J. Phys. Chem. A 129, 10014.
  DOI 10.1021/acs.jpca.5c05210. (PNO discontinuities in finite-difference properties.)
- Sanders, J. N., Andrade, X., Aspuru-Guzik, A. 2015, ACS Cent. Sci. 1, 24.
  DOI 10.1021/oc5000404. (Compressed-sensing Hessians; polyacenes.)
- Wang, B., Luo, S., Wang, Z., Liu, W. 2025, J. Chem. Theory Comput. 21, 10893.
  DOI 10.1021/acs.jctc.5c01354. (O1NumHess.)
- Williams, N. J., Kabalan, L., Stojanovic, L., Zolyomi, V., Pyzer-Knapp, E. O. 2024,
  arXiv:2408.08006. (Hessian QM9.)
- Zhang, X., et al. 2024, arXiv:2404.03129. (Automatic-differentiation gradients for local
  coupled cluster, PySCFAD.)

Carried from plan 04 (verification status as recorded there): Bauschlicher et al. 2018;
Boese, Klopper & Martin 2005; Bos et al. 2025; Chen, Li & Li 2026; Hudgins & Sandford 1998;
Käser & Meuwly 2021; Lam, Abdul-Al & Allouche 2020; Mai et al. 2025; Mattioda et al. 2020;
Mulas, Falvo, Cassam-Chenaï & Joblin 2018; Ricca et al. 2026; Sylvetsky et al. 2020; Tang et
al. 2025; NIST CCCBDB; Zapata Trujillo & McKemmish 2022.
