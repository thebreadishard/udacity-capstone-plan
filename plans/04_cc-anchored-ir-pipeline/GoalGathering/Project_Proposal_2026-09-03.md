# Coupled-cluster-anchored anharmonic infrared spectra of polycyclic aromatic hydrocarbons

**Master's capstone project proposal**
Prepared for supervision review, 3 September 2026.
Companion documents: this proposal summarises a frozen plan; the binding technical documents
(ladder, tolerances, opponents, gates) live in the same folder and take precedence where they
are more specific.

---

## 1. Summary

Infrared band positions of polycyclic aromatic hydrocarbons (PAHs) underpin the interpretation
of the aromatic infrared bands that JWST now resolves in objects such as the Orion Bar. The
reference predictions used for this — most prominently the NASA Ames PAH IR Spectroscopic
Database (PAHdb) — rest on scaled harmonic DFT, and the current database paper states plainly
that the systematic uncertainties of its spectra "are currently unquantified" (Ricca et al.
2026). This project builds and tests one pipeline: any individual neutral aromatic molecule in,
an infrared absorption spectrum out, with the anharmonic part of the prediction anchored to
coupled-cluster quality electronic structure (DLPNO-CCSD(T)) rather than to DFT, and with a
measured error budget on every claimed band.

The success criterion is deliberately relative and measured, not absolute: on small and medium
PAHs, where laboratory spectra exist, the pipeline's band positions must be compared per band
against named, version-frozen state-of-the-art predictions under a pre-registered protocol; on
the largest species, where nothing exists beyond scaled harmonic B3LYP/4-31G, the deliverable
is a spectrum with a stated, honestly-labelled error budget — explicitly an extrapolation, with
no accuracy claim. The project is as much about the evaluation discipline (pre-registration,
frozen baselines, mandatory null tests, fail-closed reporting) as about the spectra themselves.

## 2. Background and motivation

The aromatic infrared bands at 3.3, 6.2, 7.7, 8.6, 11.2 and 12.7 µm are attributed to PAH
ensembles, and the 10–15 µm region in particular separates C–H out-of-plane bending modes by
adjacency class (solo, duo, trio, quartet hydrogens). Band positions therefore carry structural
information — but only at the accuracy the underlying molecular predictions support. The
practical resolution floor for astronomical claims is of order 10 cm⁻¹, since emission from a
temperature- and charge-distributed ensemble blurs anything finer; the question is whether the
theory is reliable even at that level, per molecule and per band family.

Preparatory work for this project (2026-08, scripted and reproducible from the repository
history) measured the error of the standard approach directly. Scaled harmonic B3LYP/6-31G*
with a single benzene-fitted scale factor, scored against argon-matrix laboratory bands from
PAHdb's experimental library, gives a mean absolute error of 7.1 cm⁻¹ on the quartet C–H
out-of-plane band across five 2–4-ring PAHs (worst case 15.6 cm⁻¹), and systematic errors of
−36 and −49 cm⁻¹ on the solo and duo classes. The same probes showed that the laboratory
quartet band itself spreads over 60 cm⁻¹ across those five species — wider than the computed
spread — so a lookup by adjacency class alone cannot work either. These are not literature
numbers; they were computed and scored within this project's own probe scripts, and they define
concretely what "better than the status quo" must mean per band family.

The motivation for a coupled-cluster anchor is that every currently available prediction line
shares the same ceiling: the electronic structure underneath is DFT, with an error that is
empirically patched (scale factors) rather than quantified. Where that patch is fitted — 25
gas-phase bands for PAHdb v4.00 — it works on average; what it costs per band, per molecule,
per size regime, no one has measured. That is the gap this project occupies.

## 3. State of the art

A survey pass (2026-09-02, every identifier verified against the primary source or flagged as
an open verification debt) maps the field as follows:

| Method front | Reaches | Keeper |
|---|---|---|
| Scaled harmonic DFT | C₃₈₆ | PAHdb theoretical v4.00 (Ricca et al. 2026): 10,749 species, B3LYP/6-31G* (4-31G above 200 C), three scale factors fitted to 25 gas-phase bands |
| Machine-learning MD, anharmonic (DFT teacher) | C₂₁₆ | Mai et al. 2025: 1,704 PAHdb species, several temperatures, linear scaling |
| Quartic force field / VPT2 anharmonic | C₁₈ / C₂₄ | PAHdb Anharmonic library v1.00 (45 spectra to C₁₈H₁₂); Mulas et al. 2018 (pyrene, coronene) |
| CC-quality vibrations | ~benzene / naphthalene | scattered literature; no PAH-scale product exists |

Three observations structure the plan. First, between C₁₈ and C₃₈₄ no anharmonic-beyond-DFT or
CC-anchored prediction exists at all; for the 101–386-carbon PAHdb size bin the only predictions
on Earth are scaled harmonic B3LYP/4-31G. Second, Mai et al.'s machine-learning approach is
impressive in scale and includes temperature, but by its authors' own description its accuracy
is "comparable to conventional quantum chemical calculations" — i.e. it inherits its DFT
teacher's ceiling; beating it on accuracy means beating that teacher, which is exactly what a
CC anchor is for. Third, Mulas et al. name the accuracy of the underlying quartic force field
as their own main limitation — again the electronic-structure level, not the vibrational
treatment.

Two further papers set bars rather than methods. Bos et al. (2025) show that machine-learned
DFT scale factors substantially improve on global scaling; this defines the cost bar — an
expensive anharmonic method must beat *ML-corrected* scaling, not merely raw scaling, or it has
not earned its cost, so we rebuild that class of baseline in-house and put it in every
comparison table. Tang et al. (2025) warn that harmonic-plus-scaling often already fits observed
band profiles; where anharmonicity and the CC anchor actually pay must therefore be shown per
band, not assumed.

These four lines (PAHdb v4.00; the anharmonic small-molecule front; Mai 2025; the ML-corrected
scaling baseline) are frozen by name and version as the opponents. After a comparison against a
line has been scored, that line may not be swapped or re-versioned; this is a deliberate
pre-registration measure.

## 4. Research questions

The plan keeps two questions strictly apart, because they support different claim types:

**Accuracy (small and medium PAHs, benzene to coronene).** Can a per-molecule pipeline —
equilibrium geometry, the best affordable Hessian, and a machine-learned anharmonic correction
trained on self-generated DLPNO-CCSD(T) points — produce infrared band positions that
measurably improve on scaled-harmonic DFT, on an in-house ML-calibrated harmonic baseline, and,
where its coverage overlaps, on DFT-teacher MLMD, judged per band against laboratory spectra?

**Reach (super-large PAHs, C₃₈₄H₄₈-class).** Can the same pipeline, unchanged, produce a
spectrum with a stated error budget at sizes where no anharmonic or CC-quality prediction — and
no laboratory spectrum — exists at all? Here no "beat" is claimed, because nothing could decide
it; the deliverable is a labelled theory-vs-theory comparison and an uncertainty statement that
is explicitly an extrapolation from the smaller, lab-scored rungs.

Embedded in the accuracy question is the methodological sub-question that doubles as the
project's controlled experiment: *what does the CC anchor itself buy?* This is answered by a
pre-registered comparison of Δ-learning (DFT surface plus a learned correction to DLPNO
anchors) against a direct fit to the DLPNO points alone, with identical splits, tuning budgets,
and at least three seeds per arm.

## 5. Approach

### 5.1 The pipeline, per molecule

1. **Geometry and harmonic Hessian** at a declared DFT level (B3LYP-class; basis frozen per
   size rung before any result exists). This yields harmonic frequencies and intensities and is
   the baseline every further step must improve on.
2. **Anharmonic correction.** A machine-learned potential energy surface is fitted to
   self-generated DLPNO-CCSD(T) single points, sampled along normal modes and short molecular
   dynamics trajectories. DLPNO-CCSD(T) (domain-based local pair natural orbital coupled
   cluster) is a controlled locality truncation of CCSD(T), usable at sizes where the canonical
   method is not. Spectra are then obtained through one of three resonance-explicit routes,
   chosen per rung and fixed in writing before any surface for that rung is fitted: GVPT2 with
   named resonance thresholds and a polyad cap; a dipole-autocorrelation MD route with C–H
   stretches labelled classical; or the C–H stretch excluded from scoring at that rung. Raw
   VPT2 without resonance treatment is forbidden on any promised molecule — Mulas et al. (2018)
   document exactly the Fermi-resonance breakdowns that make it unreliable for PAHs.
3. **Error budget.** Every claimed band carries a named, measured error source: the
   electronic-structure level, the surface fit RMSE, the sampling protocol, and — for
   matrix-isolation comparisons — the measured matrix–gas shift.

Band positions are the scored quantity. Intensities are computed from dipole derivatives at the
declared level and reported with provenance, but they are not part of the success criterion:
matrix-isolation intensities are unreliable as a scoreboard, and preparatory work showed that
intensity-based band selection introduces its own failure modes. Positions are what the 10–15 µm
adjacency-class analysis actually consumes.

### 5.2 A size ladder with declared claim types

Molecules are ordered on a ladder, each rung with a stated purpose, pre-named opponents and a
pre-named laboratory scoreboard:

| Rung | Species | Type | Purpose |
|---|---|---|---|
| R0 | benzene | accuracy | end-to-end pilot; canonical CCSD(T) affordable (measured: single point ~20 s on the development laptop) |
| R1 | naphthalene | accuracy | the DLPNO-vs-canonical license check: measured harmonic-frequency deltas decide whether DLPNO anchors are trusted above this size |
| R2 | pyrene; tetracene, chrysene | accuracy | first territory beyond PAHdb's anharmonic front |
| R3 | coronene | accuracy | Mulas et al.'s molecule; largest PAH with a usable matrix spectrum in hand |
| R4–R5 | C₅₄–C₂₁₆ class | reach | no per-molecule laboratory truth; theory-vs-theory only |
| R6 | C₃₈₄H₄₈-class | reach | only scaled harmonic B3LYP/4-31G exists here; any physics beyond it is new |

The accuracy/reach split is the falsifiability backbone of the plan. On accuracy rungs the
claim "beat the line" is decidable and symmetric — losing is published with the same paired
table as winning. On reach rungs the word "beat" is forbidden, because no measurement exists to
decide it; what is delivered instead is the demonstration that the *same, unchanged* pipeline
that was scored honestly at three smaller tiers runs end-to-end at a size where nothing else
does, with its uncertainty statement labelled as an extrapolation. Reach rungs may not start
before R3 has been scored — where "scored" explicitly includes an honest loss or an
inconclusive outcome. Winning small is not a precondition for going large; scoring honestly is.

All rungs are neutral species. A laboratory spectrum of a cation never scores a neutral
prediction; cations are a natural extension but are out of scope for the promised set (§6).

### 5.3 Expectations per size tier

What success means differs by tier, and the four meanings chain into one argument:

1. **Small (R0–R1):** truth is known; the pipeline must *agree* with it within the stated
   margin. Beating the lines on benzene is secondary — the small rungs license and calibrate
   the method, they are not its destination.
2. **Medium (R2–R3):** approximate truth is known via empirically corrected calculations; the
   pipeline must land within its margin *natively*, without any generic scale factor. Matching
   what others need an empirical patch for, without the patch, is the medium-tier result. No
   scale factor is ever applied to anharmonic output.
3. **Large (R4–R5, bonus):** no sharp truth exists; the honest additional datum is named-expert
   judgment, with the expert and the exact question fixed in a dated note *before* any spectrum
   at that size exists — an opinion solicited after the numbers is a quote, not a datum.
4. **Super-large (R6):** earned trust. The claim cites the tier record exactly as it stands —
   including any inconclusive middles — and names what could and could not falsify the
   extrapolated uncertainty statement at that size.

## 6. What this project deliberately does not do, and why

**No transferable, train-once model across molecules.** Two reasons. First, the preparatory
probes measured the failure of structural transfer directly: the same adjacency class moves
56 cm⁻¹ between naphthalene and anthracene, and a controlled isomer series (tetracene,
chrysene, triphenylene — same formula, same ring count) showed that the "bay" correction is not
even approximately a constant. A motif atlas keyed on local structure carries a systematic
error several times the tolerance. Second, molecule-to-spectrum ML at scale already exists —
Mai et al. (2025) cover 1,704 species — and it is DFT-ceiling by construction. The niche that
is both open and defensible is per-molecule accuracy anchored above DFT, not another
transferable model. Each molecule therefore gets its own surface; if transfer is ever observed,
it is reported as a bonus observation, never promised.

**No full coupled-cluster potential energy surface, and no global quartic force field, for
large molecules.** Coronene has 102 vibrational coordinates; a full CC surface there is not a
matter of budget but of impossibility, and the cost measurements from the preparatory phase
(canonical CCSD(T) hits a memory wall near 110 basis functions on workstation hardware; a
DLPNO Hessian is thousands of single points) rule out the brute-force route. The pipeline's
design — best affordable harmonic Hessian plus a learned, sampled anharmonic correction —
follows the hybrid logic introduced by Boese, Klopper & Martin (2005) and is the only route
the arithmetic permits at PAH sizes.

**No new empirical scale factors.** ML-corrected scale factors are the cheap line (Bos et al.
2025) and serve as a baseline, not as the method: a scale factor is an unexplained empirical
patch, and the whole point of the CC anchor is to replace patching with quantified error. If a
harmonic fallback is ever used at a rung, it declares its factor and fit set openly and
competes under the same protocol.

**No light–matter dynamics, and no new emission model.** An earlier iteration of this plan
tried to co-own an electromagnetic propagation layer and failed review on timescale-separation
grounds; the lesson is kept. The scored product is the 0 K absorption spectrum against
laboratory data. Astrophysical emission after UV heating is handled by post-processing our
bands through the published NASA Ames cascade model — inherited machinery, honestly labelled;
our contribution is better input bands, not a new radiative model. Temperature-dependent band
shifts from MD on the fitted surface are a conditional bonus, pre-registered only after the
relevant laboratory references are pinned.

**No species identification in JWST spectra.** JWST motivates the work and frames the final
report, but claiming an identification would require population modelling, charge balance and
blend analysis far beyond a capstone's evidence. The deliverable is reliability-gated input
data for the people who do that work.

**No sub-tolerance accuracy language.** No claim finer than 10 cm⁻¹ is made in any astronomical
framing; a lab-facing claim may be finer only if the measurement uncertainty and the declared
controls (surface test RMSE, DLPNO-threshold sensitivity) both support it — and never on
matrix-isolation data, which carries its own shift.

## 7. Evaluation design

The evaluation contract is the part of this project most directly shaped by its review history,
and I would single it out for discussion.

**Frozen opponents and pre-registered comparisons.** The opponent lines are named and versioned
now, before any pipeline number exists. The comparison form is fixed: paired per-band absolute
error on identical laboratory bands, aggregated per band family, mean ± spread, at least three
seeds for every ML component. The exact band lists, windows, class assignments, and beat
margins are frozen in a dated pilot note written after the benzene pilot and a lab-scoreboard
re-read — but before any pipeline-vs-laboratory number exists for any molecule. Choosing
windows after seeing results is treated as the protocol violation it is.

**The matrix–gas decidability gate.** Most PAH laboratory spectra are argon-matrix data, which
carry a matrix shift of the same order as the improvements we are trying to measure (working
convention 15 cm⁻¹, to be replaced by a measured value). Before any medium-rung comparison is
scored, a per-band matrix-vs-gas shift table is produced for the families where both exist; a
family whose matrix–gas delta is not smaller than its beat margin is scored "pre-declared
inconclusive on matrix" — not beaten, not lost. A first coverage probe against the NIST WebBook
has already run: gas-phase IR exists for benzene, naphthalene, pyrene and chrysene, but not for
tetracene (solid only) or coronene — so this gate is not hypothetical; it will genuinely
declare some families undecidable, and the plan says so in advance rather than discovering it
after the numbers exist.

**Mandatory null tests.** Two null rows are required in every scored comparison, a lesson
learned twice in earlier plan reviews (gates that could not fail on garbage, and gates that a
do-nothing predictor passed). First, the Δ = 0 arm: the identical scoring script run with the
anharmonic correction switched off must *lose* the comparison, or the anharmonic claim is void
and the result is reported as "explained by the calibrated harmonic baseline" — a pre-written
sentence that cannot be negotiated afterwards. Second, a noise-input run must fail the sanity
gates. Given Tang et al.'s warning that scaled harmonics often already fit profiles, the Δ = 0
null is not a formality; it is where this project is most likely to be humbled, and the plan
treats that outcome as publishable.

**Anchor licensing by measurement, not trust.** DLPNO's locality thresholds are known to need
tightening for delocalised π systems (Sylvetsky et al. 2020 — a caveat established for
energies, not curvatures, which is precisely why it must be re-measured here). Before DLPNO
anchors may support any accuracy claim, three probes must print: DLPNO-vs-canonical harmonic
frequency deltas at the largest molecule where canonical CCSD(T) still runs; TightPNO-vs-
NormalPNO deltas at the license molecule and one medium-size spot check; and a smoothness probe
(second-difference noise along every promised normal mode, since local-truncation noise makes
the surface rough in exactly the way that corrupts force constants). If any delta approaches
the beat margin for a family, DLPNO anchors stop licensing accuracy language on that family,
and a declared hybrid fallback competes instead.

**Leakage control.** Laboratory values never enter the pipeline's training, validation,
stopping, or sampling decisions; the pipeline's spectra meet laboratory data only inside the
frozen comparison scripts. The one declared exception is the in-house calibrated-harmonic
baseline, which trains on lab residuals by design, is evaluated strictly leave-molecule-out,
and appears only as an opponent column and as the empirical layer of the reach-rung error
budget — never inside the pipeline.

**Fail-closed reporting.** Every rung that does not run is reported with the named cap,
precondition, or missing binary that stopped it. Losing a scored comparison is published with
the same paired table as winning. Inconclusive is a publishable outcome throughout.

## 8. Feasibility and resources

The plan is built on measured, not estimated, costs wherever a measurement exists. On the
development laptop (8-core Ryzen, 32 GB): a B3LYP/6-31G* Hessian runs in ~3 minutes for
benzene, ~3 hours for coronene; canonical CCSD(T) single points run in ~20 s for benzene and
hit a memory wall shortly above it — which is the measured, not assumed, justification for
DLPNO at every larger size. The source-conversation estimate for a full medium-rung anchor set
(~10⁴ DLPNO points for coronene, i.e. thousands of node-hours) is the class of cost that
motivates the escalation structure below.

Compute is tracked in three declared budgets. Human hours are logged but not capped — no
deadline is a scientific gate. Laptop wall-clock carries checkpoints (168 h per rung pilot)
that force dated decisions — continue knowingly, reroute to the cluster, or stop — but never
silently kill a rung, and never permit ducking under a checkpoint by quietly coarsening the
basis or loosening DLPNO thresholds. Cluster node-hours get no number until three preconditions
exist: written access, a timed single-point probe on the actual machine, and a dated per-rung
cap derived from that probe. Reach rungs are explicitly conditional on that third budget; if
the allocation never materialises, R6 is reported fail-closed rather than silently dropped.

The intended escalation path is: everything through the benzene and naphthalene rungs on local
hardware (proving the pipeline end-to-end before any allocation is requested), then a
justified, probe-backed request for cluster time for the anchor-point production runs of the
medium rungs and the single reach demonstration. This is the main practical point on which
supervision input is requested.

## 9. Risks

The three risks the plan considers most serious, with their declared responses:

1. **DLPNO surface roughness erases the CC advantage.** The local truncation makes the surface
   noisy at exactly the scale of the force constants; fit and sampling error may then swallow
   the DFT-to-CC gain. Response: the Q6 smoothness and threshold-delta probes are a hard stop
   condition, and the outcome "the anchor does not pay at this size, measured thus" is a
   reportable result, not a failure mode to hide.
2. **The anharmonic correction does not beat calibrated harmonics.** Tang et al. suggest this
   is a live possibility. Response: the mandatory Δ = 0 null row makes this outcome explicit
   and publishable, and the Δ-vs-direct experiment still answers a real methods question
   either way.
3. **Laboratory decidability is worse than hoped.** The gas-phase coverage probe already shows
   tetracene and coronene lack gas-phase IR. Response: the matrix–gas gate pre-declares these
   inconclusive rather than letting matrix-shifted comparisons masquerade as decisions;
   supervision advice on additional gas-phase or jet-cooled sources would directly enlarge the
   decidable set.

## 10. Fit to the capstone programme

The degree programme requires eight graded modules (exploratory data analysis, statistics,
applied ML, deep learning, generative methods, agentic workflows, synthesis). Each module is
mapped onto a load-bearing pipeline artifact — the opponent-line atlas parsed from PAHdb v4.00;
the laboratory scoreboard and the matrix-vs-gas shift test; the calibrated-harmonic baseline;
the Δ-learning-vs-direct experiment; label-efficient geometry sampling; a campaign-management
agent that enforces the budget preconditions and emits the certificate-or-refusal; and the
assembled pipeline with the scored ladder. The mapping rule is that no module may invent
busywork: if a rubric cannot be served by something the pipeline genuinely needs, the conflict
is escalated, not papered over. Module deadlines are administrative facts; a module may ship an
honest fail-closed state to meet its date, and the science continues past it.

## 11. What is asked of the supervisor

1. A critical reading of this proposal, in particular the evaluation contract (§7) and the
   accuracy/reach split (§5.2) — the two places where the plan's honesty either holds or does
   not.
2. Advice on laboratory sources: gas-phase or jet-cooled spectra for tetracene- and
   coronene-class species beyond PAHdb and the NIST WebBook would directly enlarge the set of
   decidable comparisons.
3. When the local pilots justify it: sponsorship of a cluster-time request, sized by the timed
   probes described in §8.
4. Optionally, at the large-rung stage: serving as, or nominating, the named expert whose
   pre-registered judgment is the honest datum for sizes where no laboratory truth exists.

## 12. References

Verification status is tracked per item in the working bibliography; identifiers below are
re-verified against the primary source before appearing in any scored document.

- Bauschlicher, C. W., Ricca, A., Boersma, C., Allamandola, L. J. 2018, ApJS 234, 32.
  DOI 10.3847/1538-4365/aaa019. (PAHdb v3.00 scale factors.)
- Boese, A. D., Klopper, W., Martin, J. M. L. 2005, Mol. Phys. 103, 863.
  DOI 10.1080/00268970512331339369. (Origin of the hybrid harmonic-anchor + cheaper-anharmonic
  split.)
- Bos et al. 2025, "Ethereal AI: Infrared Spectra of PAHs with Machine Learning DFT
  Scaling Factors", ACS Omega 10(50), 62282. DOI 10.1021/acsomega.5c10225. (The cheap line /
  cost bar.)
- Chen, Li & Li 2026, A&A, arXiv:2607.20015. (Cascade emission machinery template.)
- Hudgins, D. M., Sandford, S. A. 1998, J. Phys. Chem. A 102, 329. DOI 10.1021/jp9834816.
  (Matrix-isolation source behind PAHdb experimental entries.)
- Käser, S., Meuwly, M. 2021, arXiv:2103.05491; Käser, S., et al. 2021, arXiv:2109.08407.
  (Δ-learning precedent: of order 10² high-level points suffice for transfer to CC quality.)
- Lam, Abdul-Al & Allouche 2020, JCTC. DOI 10.1021/acs.jctc.9b00964.
  (Closest method precedent — QM harmonic + ML anharmonic corrections, 37 molecules,
  RMSD 21–23 cm⁻¹; cited so tolerances are not quietly relaxed to match it.)
- Mai, Wang, Pan, Schörghuber, Kovács, Carrete & Madsen 2025, MNRAS 541, 3073;
  arXiv:2503.05120. (Line C — MLMD anharmonic to C₂₁₆.)
- Mattioda, A. L., et al. 2020, ApJS 251, 22. DOI 10.3847/1538-4365/abc2c8. (PAHdb laboratory
  spectra.)
- Mulas, G., Falvo, C., Cassam-Chenaï, P., Joblin, C. 2018, JCP 149, 144102.
  DOI 10.1063/1.5050087. (Line B — anharmonic DFT-QFF for pyrene and coronene; names its own
  QFF-accuracy limit; documents the VPT2 resonance breakdowns.)
- Ricca, A., Boersma, C., Maragkoudakis, A., Roser, J. E., Shannon, M. J., Allamandola, L. J.,
  Bauschlicher, C. W. 2026, ApJS 282, 7. DOI 10.3847/1538-4365/ae1c38. (Line A — PAHdb v4.00;
  the "currently unquantified" systematics statement.)
- Sylvetsky, N., Banerjee, A., Alonso, M., Martin, J. M. L. 2020, JCTC 16, 3641;
  arXiv:2001.08641. (DLPNO threshold caveat on delocalised π — established for energies, hence
  the in-house curvature probes.)
- Tang et al. 2025, JCP 163, 044304; arXiv:2504.11898. (IRMPD standard for cationic
  pyrene; the harmonic-plus-scaling-often-suffices warning.)
- NIST CCCBDB, SRD 101, Release 22 (2022), ed. R. D. Johnson III. DOI 10.18434/T47C7Z.
  (Verified fallback vibrational database.)
- Zapata Trujillo, J. C., McKemmish, L. K. 2022, J. Phys. Chem. A 126(25), 4100.
  DOI 10.1021/acs.jpca.2c01438. (VIBFREQ1295, second fallback database.)
