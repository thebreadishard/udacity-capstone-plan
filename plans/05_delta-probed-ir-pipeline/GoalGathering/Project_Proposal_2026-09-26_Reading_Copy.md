# Probed coupled-cluster corrections to the harmonic force constants of polycyclic aromatic hydrocarbons: a label pipeline with a measured cost and a network licensed per band family

**Master's capstone project proposal — plan 05. Consolidated reading copy, 28 September 2026** (source
text of 6 September with the dated revisions of 8–16 September worked in; the dated original is kept
beside it as `Project_Proposal_2026-09-06.md`). This document is a Master's capstone project proposal in
the Udacity programme (nine modules with administrative deadlines, §12); the supervisor is asked to act
as the project's scientific supervisor in the sense of §13 — critical reader of the design and the
evaluation contract, sponsor of the cluster request, and the named expert for the reach rungs or the
person who nominates one [institution and role: to be confirmed by the student]. Earlier drafts (3 and 4
September) are in the repository's history; the 6 September text with its dated notes remains the
record, and the change log at the end of this copy lists, per section, what was merged and by which
dated decision. Every number in it that describes this project's own performance was printed by a
script in the folder `probes/` and can be re-run, or is arithmetic shown in place on such numbers;
numbers from the literature are marked as such. A note on provenance and on the terms used follows
the summary.

**How to read this in twenty minutes.**
1. §1 — what is built, what has been measured since 5 September, and the staged success criterion.
2. §13, items 1, 3, 5a–5c and 16 — what is asked of the supervisor.
3. §7 — the evaluation contract: opponents, null tests, licences, fail-closed reporting.
4. The change log at the end — what changed since the 6 September text, and by which decision.
5. Everything else (§2–§6, §8–§12, §14) is the supporting record, reachable from those four.

---

## 1. Summary

Infrared band positions of polycyclic aromatic hydrocarbons (PAHs) underpin the interpretation of
the aromatic infrared bands JWST now resolves. The reference predictions — most prominently the
NASA Ames PAH IR Spectroscopic Database (PAHdb) — rest on scaled harmonic DFT, whose systematic
uncertainties the database's own current paper does not report (Ricca et al. 2026). This project
builds and tests two coupled things. **Pipeline B, the label factory:** an individual aromatic
molecule in, a measured coupled-cluster correction to its harmonic force constants out — the
**harmonic force constants corrected by a local coupled-cluster anchor, checked against canonical
coupled cluster where affordable** — with an error budget on every claimed band; full decks on
benzene and naphthalene, thin decks above, the neutral molecules first and naphthalene⁺ as the first
cation rung (R1⁺, §5.2) under the condition stated there. **Pipeline A, the reach product:** a
network trained on pipeline B's labels that takes a PAH's DFT Hessian and returns the per-mode
correction with its per-family error budget, licensed or refused per band family by pre-registered
transfer tests, and returning DFT with the failure printed where a family fails (decision 36, 14
September; §3.5). The question behind both is whether a measured coupled-cluster correction,
licensed on the molecules where the truth is known, can mean anything for the PAHs where no truth
exists; benzene and naphthalene are the instruments of that question, not its goal.

**In a few sentences, for a reader who knows the field.** We want to show that the harmonic force
constants of a PAH can be corrected towards coupled-cluster quality without a canonical
coupled-cluster calculation of the molecule. A local coupled-cluster correlation space is built once
at the equilibrium geometry, frozen, and carried along the normal modes; the correction is then read
from a small number of local coupled-cluster quantities in that space — energies along single modes
for the diagonal of the correction (what probe B1 measures now), and gradients along symmetry-chosen
displacement patterns for the couplings between modes: two gradients per pattern plus one at the
reference geometry, 19 at naphthalene, a count that grows linearly with the number of modes while
the number of couplings grows with its square (§3.2, dated note of 17 September; §5.3). The
energies-only reading of the couplings was tested on naphthalene on 17 September and does not reach
the required accuracy at any push amplitude, which is why the couplings come from gradients and the
gradient code is built in-house (decision 43). That correction is calibrated first on benzene and
naphthalene against the known truth. Every molecule on the ladder then gets a complete anharmonic
spectrum — positions, intensities and shape as PAHdb delivers them — but with band positions that
carry a measured coupled-cluster correction and an error margin instead of a fitted scale factor.
The route to the large PAHs, for which no prediction above scale-factor level exists today, is the
network of pipeline A, and it is tested rather than assumed: the per-family test Q9 of decision 27
and the transfer tests T-1 and T-2 of §3.5 and §6.

Every piece of this exists already, separately. Reiher and Neugebauer showed in 2003 that selected
normal modes can be computed without the full Hessian. Mata and Werner wrote in 2006 that freezing local-correlation
domains at the reference structure is the standard remedy for numerical gradients and Hessians, and
merged domains along reaction paths to keep local coupled cluster smooth there too (Mata & Werner 2006,
read in full on 20 September; §3.1, §14). Allen and Schaefer's Concordant Mode Approach extracts CCSD(T) force constants from a few
energies in a DFT normal-mode basis for small molecules. Käser and Meuwly transfer-learn a cheaper
method's surface to coupled-cluster quality from a few hundred coupled-cluster points on molecules
of up to nine atoms. The NASA Ames group and the supervisor's co-authors built the anharmonic-DFT
front for PAHs up to eighteen carbons — Mackie et al. 2015 and 2016 with the supervisor as
co-author, Esposito et al. 2024 as the Ames group's work. Pirali's naphthalene spectrum is what
everyone calibrates on. PAHdb, Mai and Bos supply the scaled, simulated and ML-corrected DFT spectra
for thousands of PAHs. What nobody has done is to put these pieces together on a PAH: carry a frozen
local coupled-cluster space along the modes, recover the diagonal of the correction from energies
and its couplings from a linearly growing number of gradients in that space, and measure an error
margin per band (§3.1 and §14 carry the references and their reading status).

Why the harmonic part rather than the anharmonic one that PAH spectra are known for? Because the
only figure this project's search found on this ladder (the searches of 5–6 September, §3.1 and
§5.2) — benzene, from the Ames group's Esposito et al. 2024, Table S1 — puts the B3LYP/N07D harmonic frequencies 5.45 cm⁻¹ from CCSD(T)-F12b as a mean absolute
difference over the modes. That error passes one-to-one through VPT2 into every fundamental, is
systematic per band family rather than random, and is absorbed only in its mean by a fitted scale
factor. The 5.45 cm⁻¹ is a mean over families, not a bound on any single mode: §3.3 measures
per-mode basis terms of the same size or larger. The anharmonic constants stay at DFT level exactly
as in that protocol; the Δ₂ = 0 null row of §7 separates what the coupled-cluster correction adds
from what the anharmonic step does. Whether the same is true at naphthalene, where the search found
none, is precisely what R1 measures per family (decision 28) — if the correction adds nothing
there, the answer is reported as such.

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

The measurements and literature findings made since the plan was written, between 5 and 16
September and all on the student's laptop, are these. A DFT-only rehearsal of the probing machinery
(a difference between two DFT functionals standing in for the coupled-cluster correction) recovered
a full force-constant correction at benzene and showed where the couplings really are. The frozen
correlation spaces on which the whole design rests were measured to be smooth: their energy
scatters by 0.002–0.06 µE_h along a displaced mode, where the same local-CC program re-selecting its
spaces at every geometry (arm C of §3.3) scatters by 7–11 µE_h at its default settings and
0.9–2.7 µE_h at tight ones, and the intermediate arm B, which re-selects the fragment spaces on the
transported orbitals, by 0.05–1.2 µE_h at tight. At the anchor basis the frozen object stays as
smooth; at the tight local-correlation thresholds it carried a frequency bias of up to 0.8 cm⁻¹ on
the C–C stretch, and the same scan with the thresholds one decade tighter, finished on 12
September, brings that to +0.11 / −0.01 / +0.23 cm⁻¹ on the three modes with the smoothness
unchanged (§3.3) — the residual was local-correlation truncation, and the anchor runs at those
thresholds. The cheap basis line printed the same day (SCF and MP2 at the same 27 points in larger
bases, nineteen minutes) showed the anchor's remaining distance from its own basis-set limit to be
an order of magnitude larger than that residual, and the anchor was redefined as a composite that
carries the SCF and MP2 basis terms at under 1 % of the cost (decision 33). The canonical
coupled-cluster reference that licenses the anchor was timed: it fits the laptop at benzene for the
line that matters, and the full canonical Hessian does not. The naphthalene anchor energy was timed
on 14 September — 38.4 h at the anchor thresholds, a measured factor F = 3.34 over the 11.5 h at
tight — and the same energy in cc-pVDZ at tight thresholds on 15 September at 69 minutes (probe B1's
first cells, §3.5). The naphthalene DFT dry run of 15 September confirmed that one energy instead of
a ± pair suffices for every irrep-pure non-totally-symmetric pattern once the geometry is
symmetrised (decision 37), which takes the naphthalene deck from 474 to 291 energies. The first
cation energy was timed on 15 September: benzene⁺ costs 31 times the neutral with the installed
unrestricted code, which is why the cation rung carries a software condition (decision 41, §5.2).
And on 16 September the pre-registered test of a DFT-only rule for choosing which couplings to
measure lost at naphthalene, so that saving appears nowhere in this document (§3.5, §5.3). The
search found no gas-phase spectrum of known temperature for chrysene or triphenylene in the 6–15 µm
region, and for pyrene only a hot heat-pipe spectrum and one cold band, which fixes what that rung
can and cannot decide.

The pipeline outputs the whole spectral shape for every molecule — position, intensity, drawn
width — and the plan is explicit about which of those it scores and which it promises: positions
are promised and scored wherever a laboratory band can decide the comparison; intensities are
scored on the two molecules where a calibrated gas-phase intensity exists (benzene, naphthalene)
and reported with their provenance everywhere else; widths are drawn, not predicted.

The success criterion is measured and staged. On benzene the pipeline must **agree** with the
laboratory bands within the laboratory uncertainty combined with its own error budget — benzene
licenses the anchor and the recovery; nothing is "beaten" there, and the comparison with existing
predictions is printed without a claim (decision 28). On naphthalene agreement is required again
and, family by family, the question is put whether the coupled-cluster correction adds accuracy
over DFT. Above naphthalene the ladder is built ring by ring (decision 39): a three-ring rung —
anthracene and phenanthrene, the isomer test at equal size — on which the per-family go/no-go for
the size axis is read, then the pyrene class and coronene. On those rungs pipeline B measures
**thin decks** — the diagonal blocks per band family, tens to a few hundred coupled-cluster
energies per molecule — whose purpose is the pre-registered transfer test T-2: does the per-family
correction measured at benzene and naphthalene predict these molecules within the laboratory
margin? Full decks above naphthalene are out of reach on every route at the anchor's basis (§12);
whether a cheaper basis with a transferred increment changes that is a pre-registered probe (probe
B1, §3.5), not an assumption, and the laboratory rarely decides there (Module 03: the hot gas
records give 8.6–16 cm⁻¹ per family), so the plan says so rather than promising a comparison it
cannot score (decision 36). The thin decks themselves are not cheap at the anchor's basis: by the
duration table of §12 and its own exchange rate (the R1 H deck, 15–25 Snellius-days ↔
195,000–290,000 SBU, i.e. ≈ 12,000–13,000 SBU per Snellius-day on four thin nodes), the pyrene thin
deck (40–130 Snellius-days) is ≈ 0.5–1.7 million SBU and the coronene thin deck (180–1,200
Snellius-days) ≈ 2–16 million SBU — coronene alone above the 1,000,000 SBU of a Small Compute
application — so at cc-pVTZ they are beyond that application and enter the request of §13 item 5a
only if probe B1 wins, at roughly one tenth (the measured cc-pVDZ/cc-pVTZ ratio 9.9–10.0). On the largest species the deliverable is the network's prediction with
its per-family error budget, licensed or refused per family by the transfer tests, and no accuracy
claim beyond that budget. The project is as much about the evaluation discipline —
pre-registration, frozen baselines, mandatory null tests, fail-closed reporting — as about the
spectra themselves.

### Provenance, reviews, and the words this document uses

*Reviews.* The plan was put through eight review passes on 3 and 4 September: four "cold reads"
by a reader who saw only the documents and a brief, and four adversarial domain reviews with
literature access. **These were performed by an AI assistant (Claude), each pass in a fresh
session that had not seen the author's reasoning; they are a disciplined self-review with an
outside vocabulary, not human peer review.** Every finding and its closure is on file in the
folder. This document itself was cold-read the same way on 6 September, on 8 September (by a
reader placed in the supervisor's position; 43 findings, four blocking, addressed on 10 September)
and on 16 September (two fresh readers, the proposal with its cover note and the Ladder; 25 ranked
stumbles, all accepted — decision 42; this reading copy implements the ones that concern the
proposal, and the change log at the end names them; a second reader the same day checked this copy
against those 25 and added 15, worked in under the change log's second heading).

*What was carried from plan 04.* The success criterion (per-band comparison against the best
existing prediction, decided by laboratory data); the baseline predictions ("opponents", §7); the
laboratory scoreboards; the leakage rules; the fail-closed reporting; the six-step size ladder;
the ban on scale factors on anharmonic output. Plans 01–03 preceded plan 04 and are referred to
once (§11, risk 7) for a lesson learned.

*Terms.* A **rung** is one step of the size ladder (§5.2). **Δ₂** is the correction to the
harmonic force-constant matrix, expressed in the DFT normal-mode basis; its **diagonal** entries
correct each mode's own frequency, its **off-diagonal** entries the couplings between modes. The
**energy route** obtains Δ₂ from coupled-cluster energies at displaced geometries; the **gradient
route**, if the side project of §5.3 delivers it, from gradients. The **deck** is the ordered list
of displacement patterns for a molecule; it is **hashed**, meaning its order is fixed by a seeded
function before any energy is computed, so nobody can reorder the patterns after seeing a result.
A **full deck** measures every symmetry-allowed coupling directly as a ± two-mode point; an **H
deck** is a full deck with decision 37 applied (one energy instead of a ± pair for every pattern
confined to a non-totally-symmetric irreducible representation); a **thin deck** is the single-mode
(diagonal) block only. **K** is the number of coupled-cluster energies a molecule needed; **K_off**
the part of it spent on the off-diagonal block. The **pilot note** is a dated document, written
before the first real coupled-cluster correction is computed, that fixes every tolerance, margin
and constant the evaluation uses. A **beat margin** is the pre-registered minimum per-band
improvement over the best opponent that counts as a win (used from naphthalene's families upward;
on benzene the test is agreement, decision 28). **τ₇** is the Ladder's tolerance within which a
recovered or predicted Δ₂ must agree with the directly computed one, per family. Numbered
**decisions** are the student's recorded choices (§10). The **licence rungs** are benzene and
naphthalene, the two rungs whose measurements license the anchor and the recovery for the rest of
the ladder. **Pipeline B** is the label factory and **pipeline A** the network (§3.5); **T-1** is
the transfer test benzene → naphthalene on the DFT stand-in correction and **T-2** the test in which
the thin decks above naphthalene are the hold-outs. **Module 05** is the deep-learning predictor of
where the correction has large couplings and **Module 06** the generative proposer of displacement
decks — both efficiency experiments on DFT-only corpora (§6, §12). The **campaign officer** (Module
07) is a rule-checking agent that reads the deck, the budget file and the pilot note, submits and
refuses computational jobs and report sentences by those rules, and never produces or edits a
scientific number. **Probe M1** is the frozen-space smoothness measurement of §3.3; **M2–M5** are
the milestones of the gradient side project of §5.3 and nothing else. **Probe B1** is the
pre-registered test of whether a cc-pVDZ deck with a transferred beyond-MP2 increment may replace
the cc-pVTZ deck (§3.5); the dated notes of 14–16 September call it "probe M3", and it is renamed
here, once, so that "M3" means only the gradient milestone. **F** is the measured cost factor of the
anchor thresholds over the tight thresholds (3.34 at naphthalene, §8); **c** the measured cost ratio
of a cation energy to the neutral's (§5.2); **g** the gradient-to-energy cost ratio of the side
project. The **(T) port** is the unrestricted compiled (T) kernel of decision 41 (§5.2). **P13, P18,
P24, P25, P26, P27** are the student's numbered proposals in the repository: P13 the choice of the
R1 machine (desktop or cluster; open), P18 the anchor as a composite with basis terms (adopted,
decision 33), P24 substitution probing (pre-registered, decision 34), P25 plan 06's DFT-only rule
for ranking which couplings to measure (its licence test lost on 16 September, §5.3), P26 the two
pipelines and the thin decks (adopted, decision 36), P27 the slow ladder priced on the measured
cc-pVDZ energy (open; its numbers are cited here as "proposed (P27, open)"). **Line D** is the row
the opponents table of §7 reserves for the 2026 machine-learning PAH-spectrum predictors once they
are read in full. **SBU** (system billing unit) is the unit in which Snellius compute time is
requested and charged, in practice one core-hour. **Levers G and H** are plan 06's cost-ladder names
for probe B1 and for decision 37 respectively. **X-numbers** (X8, X9, X16) are plan 06's numbered
desk experiments on DFT-only tensors, dated in the text where cited; **I-numbers** (I14) are ideas
in the mandate ledger of 13 September, I14 being the single-sided K rule that became decision 37;
**P10** is the research note behind decision 20 (per-mode calibration of the frozen-space bias not
needed); **probe 2a** occurs once, in the Module 03 row of §12, as the name of the scoreboard
measurement that row delivers; and "pilot prerequisite (f)" in decision 35 is the noise
measurement, item 7 of §7's list of inputs.

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
Martin 2005; Bégué, Carbonnière & Pouchan 2005 — both read in full, both on small molecules; there is
no PAH precedent) puts the coupled-cluster level in the **harmonic** constants and leaves cubic and
quartic constants at DFT level. Plan 04 had it the other way round. Plan 05 corrects the harmonic
force constants only — Δ₂ — and lets DFT supply the anharmonic constants. The domain review
sharpened this further: the probe set specified here — single- and paired-mode displacements at two
amplitudes — cannot produce the three-index cubic constants φ_ijk that PAH combination-band
resonances need (quartic force fields obtain them from energies at three-mode displacements, at
coupled-cluster cost ruled out above), so a coupled-cluster anharmonic correction was not merely
unnecessary but unbuildable with the probes specified. It was removed from the promised set. A cheap
by-product remains and is reported: the single-mode patterns are run at two amplitudes (§3.4), which
yields each mode's diagonal cubic correction for free — a number that will show how much was given
up, not a correction that is applied.

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
recovery fails on pyridine's ring modes by up to ±28 cm⁻¹ and leaves residuals up to 5 cm⁻¹ on
benzene, pyrrole and furan, because DFT and coupled-cluster mode compositions differ there — is the
strongest evidence for the plan's design choices. What plan 05 proposes beyond CMA: local coupled
cluster with frozen correlation spaces at PAH sizes; the off-diagonal block recovered from
multi-mode patterns by a **symmetry-blocked** solve of a *difference* Hessian, rather than one
element at a time; the recovery licensed against directly computed references; and the locality
of the correction, and the number of off-diagonal probes it needs, measured as a function of size.

**What is new, and what is not — stated plainly.** A literature search on 6 September 2026 (eight
queries; recorded in the working bibliography), extended on 8, 10 and 13 September as the paragraph
below the table records, found each ingredient of the plan in print and no work that combines them:

| Ingredient | Nearest published work | What plan 05 does differently |
|---|---|---|
| coupled-cluster force constants along DFT normal modes from energies; selected off-diagonals; symmetry-forbidden couplings zeroed in the full matrix | Concordant Mode Approach (Lahm et al. 2022; Kitzmiller et al. 2024; Olive Dornshuld et al. 2026 — reading (iv) below) | the target is the *difference* Δ₂, not the CC force constants; the off-diagonal block is recovered as a whole from multi-mode patterns, not element by element; symmetry used as the recovery prior rather than as a clean-up; local rather than canonical coupled cluster, at PAH sizes |
| recovering a Hessian from few measurements by exploiting its structure | compressed sensing in a cheap method's eigenbasis (Sanders et al. 2015); O1NumHess (Wang et al. 2025) | applied to a difference Hessian rather than a full one; the prior is the molecule's symmetry, parameter-free, instead of generic sparsity; the probe count is a measured, pre-registered quantity |
| correcting DFT towards CCSD(T) by learning the difference | Δ-machine learning of potential-energy surfaces: Käser, Boittier, Upadhyay & Meuwly 2021 and Lam, Abdul-Al & Allouche 2020 (reading (v) below); Qu et al. 2021 and Bowman et al. 2022 (local-CCSD(T) labels at 15 atoms; reading (ii) below) | nothing is learned per molecule at the licence rungs; the difference is measured, and the network of pipeline A is trained on those measured labels and licensed per family (§3.5, §6) |
| local-correlation spaces held fixed for numerical derivatives | the discontinuity problem, measured: steps of 0.1–1 mE_h, near equilibrium in conjugated systems (Russ & Crawford 2004, read in full 20 September; Madriaga & Crawford 2025); fixed PAO domains at the reference structure as the standard remedy for numerical gradients and Hessians, and domain merging along reaction paths (Mata & Werner 2006 §II, read in full 20 September); residual smoothing by bump functions, at the price of a doubled error (Subotnik & Head-Gordon 2005, read in full 20 September); fixed domains for DLPNO-MP2 numerical derivatives (ORCA) | **not the freezing** — freezing an atom-list domain is 2006 practice. LNO-type spaces (localised occupied orbitals and pair-density natural-orbital virtual subspaces) have no atom list to freeze; the plan transports them by projection to each displaced geometry, semicanonicalises them, measures the projection term and the reload error, and shows the finite-difference force constants smooth at the 10⁻⁸ E_h level against canonical CCSD(T) in cc-pVDZ and cc-pVTZ — no publication found that transports LNO spaces or prices that transport |
| scaled, ML-corrected or anharmonic DFT for PAH spectra | PAHdb v4.00 (Ricca et al. 2026); the PAHdb Anharmonic library v1.00 (Mackie et al. 2015, 2016; Esposito et al. 2024); Mulas et al. 2018; the ML-corrected scale factors of Bos et al. 2025 (marketed as Ethereal AI); the 2026 machine-learning predictors trained on DFT (line D, see below) | these are the opponents; the plan adds a measured coupled-cluster correction to the harmonic constants and an error budget per band, and leaves the anharmonic constants at DFT level as they do |
| selected high-level vibrations from a cheap guess, without the full Hessian | mode-tracking (Reiher & Neugebauer 2003, read in full: Davidson subspace iteration on gradient derivatives, cheap-method guess, CCSD(T) refinement named as the intended use) | the target is the correction to the whole force-constant matrix from energies, under a symmetry prior, with the probe count measured — not a set of converged eigenvectors |

*Readings behind the table (dated per item).* (i) **Mata & Werner 2006** (J. Chem. Phys. 125,
184110, DOI 10.1063/1.2364487; PDF from the supervisor, read in full 20 September with Russ & Crawford
2004 and Subotnik & Head-Gordon 2005 — `notes/Reading_Note_2026-09-20_Supervisor_PDFs_L1_Smoothness_and_Mackie.md`): §II states that fixed domains at the
reference structure are the standard remedy for numerical gradients and Hessians and that finite differences with
frozen domains reproduce the analytic gradient; the paper's own contribution is domain merging along reaction
paths. Two of its remarks are precedents the plan now cites: pseudocanonical blocks for (T0) among orbitals sharing
a domain (our semicanonicalisation), and testing the domain error at MP2 level before the expensive calculation
(our composite and M2's gate). The novelty claim of this row was reworded the same day (see the row). (ii)
**Two Δ-ML records added 13 September (Crossref-verified, abstracts only):** Qu, Houston, Conte,
Nandi & Bowman 2021, *J. Phys. Chem. Lett.* 12, 4902 — a Δ-ML correction of an MP2 surface of
15-atom acetylacetone from 2,151 *local* CCSD(T) energies, trained with as few as 430, the nearest
published cost logic to this plan's labels — and the perspective Bowman, Qu, Conte, Nandi, Houston &
Yu 2022, *J. Chem. Theory Comput.* 19, 1, which names local CCSD(T) as the only route to such labels
at 15 atoms. Why not a Δ-ML surface with local coupled cluster, as Qu et al. do: cost and object —
Qu et al. build a database of 2,151 local-CCSD(T) energies for a 15-atom molecule to learn a whole
surface, whereas this plan's naphthalene deck is 291 energies at 18 atoms (474 before decision 37)
and its thin transfer decks above naphthalene tens to a few hundred, because the promise (band
positions) needs only the harmonic constants and the molecule's symmetry selects the probes; the
price of that economy is that anharmonicity stays at DFT level (§6). (iii) **Line D, added 13
September (records Crossref-verified, abstracts read, all open access):** the group of line C
published in 2026 three machine-learning predictors of PAH infrared spectra trained on DFT — He, Mai
& Wang, *A&A* 708, A335 (charge-aware neural network, 12,599 species, four charge states, up to 150
carbons, "near-DFT accuracy"); Tang, He, Wang & Qiu, *MNRAS* 546, stag283 (graph neural networks,
best for 20–40 carbons); Liu, Wang & Qiu, *MNRAS* 549, stag893 (a transformer on molecular strings,
24,146 spectra) — and code for a machine-learning double-harmonic pipeline
(`zwAstroChem/ML-DH-PAH-IR`, July 2026, paper not yet found). These are the nearest existing "large
PAH in, spectrum out" products; they reproduce DFT, its errors included, and by their own abstracts
weaken at the largest molecules for lack of training data. They enter the opponents atlas as line D
once read in full (§7); this plan differs in the label (a measured coupled-cluster correction) and
in the error budget per band, and the network of pipeline A must be measured against them. (iv)
**Olive Dornshuld et al. 2026** (read in full): 17 intermolecular complexes, MP2 normal modes in a
heavy-augmented triple-zeta basis, CMA-2A converges with 3 % of the off-diagonals; its persistent
benzene outlier is one same-representation ring-deformation coupling, the same phenomenon our
rehearsal found. (v) **Käser, Boittier, Upadhyay & Meuwly 2021** (read in full 10 September):
262–632 CCSD(T) geometries with energies, gradients and dipoles, ≈ 5 % of an MP2 set, on 7–9-atom
molecules, harmonic MAE 0.1–1.1 cm⁻¹ against explicit CCSD(T), no aromatic; **Lam, Abdul-Al &
Allouche 2020** (read in full): B2PLYP harmonic part kept, cubic and quartic constants from a neural
network trained on 24N single points, 37 molecules including benzene and naphthalene, RMSD 21 cm⁻¹
against full B2PLYP — the harmonic part stays at DFT level.

The claim of novelty is therefore the combination and its measurement discipline, not any single
ingredient; the plan's own name for the object is "a symmetry-blocked recovery of a difference
Hessian with a frozen local-CC anchor".

### 3.2 The prior: symmetry, not a frequency band

The plan's first draft regularised the recovery with a frequency band: couplings between modes
close in frequency were left free, distant ones were penalised. The DFT-only rehearsal at benzene
(5 September; §8) showed that this is not where the structure is. In the rehearsal the
"correction" is a **surrogate**: the difference between two functionals, B3LYP and BHHLYP in the
6-31G* basis, chosen to bracket the amount of exact exchange; nothing coupled-cluster has been
computed yet, and every statement in this subsection is about that surrogate. Its large off-
diagonal elements couple modes 170–450 cm⁻¹ apart — the strongest pair at 1186 and 1357 cm⁻¹
(B3LYP/6-31G* harmonic values; both b₂u — the C–H in-plane bend and the Kekulé-type ring stretch)
— and every one of them lies within a single irreducible representation of the molecule's point
group. The band did not select them; the recovery worked because the two-mode patterns in the deck
isolated them and the fitted penalty was weak.

The prior is therefore now what symmetry gives for free (decision 11): couplings between modes of
**different** irreducible representations are fixed at zero — exact for the canonical surface,
measured for the frozen-space object (decision 23: a few forbidden pairs are fitted free at
benzene and naphthalene and their magnitude printed; in the DFT surrogate they sit at the
Hessians' noise, ≤ 2 µE_h against 424 µE_h for the largest allowed coupling) — and couplings
within one representation are free whatever their frequency distance. A sparsity penalty remains
only where the free-element count exceeds what the rung's probe cap can determine. This prior has
no parameters and cannot distort the canonical truth on a symmetric molecule. It entered the
benzene rehearsal on 10 September, on the same cached responses: every mode assigned in D₆h,
family errors equal to or better than the banded rule's, forbidden couplings at the Hessians'
noise. The naphthalene rehearsal repeats the test at 48 modes before the R1 deck is built: its
stage A — the two symmetrised, irrep-projected DFT Hessians and the direct stand-in Δ₂ — exists
since 15 September (§3.5), and on it the symmetry prior is exact to 0.004 cm⁻¹ with all 141
same-representation pairs kept (X16, 16 September); the recovery from the hashed deck is the part
decision 37 waits for, and until it reads the banded rule remains the fallback for that rung.

The prior also sets the cost expectation (decision 13). Without a prior the off-diagonal block
costs about M(M−1)/2 energies for M modes — the benzene rehearsal needed 388 off-diagonal energies
for 435 unknowns (§8), so sparsity as such saved nothing. Under the symmetry prior benzene has
**57** same-representation pairs: 54 under a strict D₆h assignment (2a₁g + a₂g + a₂u + 2b₁u + 2b₂g
+ 2b₂u + e₁g + 3e₁u + 4e₂g + 2e₂u), plus three from the accidentally degenerate a₁g/b₁u block at
1020 cm⁻¹, whose two DFT eigenvectors are mixed and carry both labels; 11 of the 57 lie within
blocks grouped as degenerate (ten true pairs and that one). The rerun on the same responses reached
the same threshold at **210** off-diagonal energies (10 September). With the symmetry prior
naphthalene has **141** same-representation couplings instead of 1,128 (the deck's own analysis;
the count is reproduced by the standard D₂h assignment of its 48 modes, 9a_g + 3b_1g + 4b_2g +
8b_3g + 4a_u + 8b_1u + 8b_2u + 4b_3u). The representation of each mode is determined by the deck's
own symmetry analysis in the molecule's **full** point group: DFT programs run in Abelian
subgroups (benzene in D₂h, where its degenerate modes split artificially — Esposito et al. 2024
note the same), and their labels would leave far more couplings free than symmetry does. Zeroing
symmetry-forbidden couplings is itself standard practice — the Concordant Mode Approach does it as
a clean-up of its full high-level matrix — what is new here is using it as the prior of a recovery
from few measurements.

The arithmetic rests on two measured per-energy times: 35 minutes for benzene in the anchor basis
at the tight thresholds (2,087 s; 76 minutes at the anchor's xtight thresholds, §8) and, for
naphthalene, **11.5 h per energy at 19.8 GB peak memory at the tight thresholds (11
September) and 38.4 h at the anchor thresholds (14 September; F = 3.34, peak 15.4 GB with pyscf's
out-of-core path)**. Two numbers describe the cost, with different roles. The **deck** at R1 is the
probing licence's reference (§5.1): 48 modes × 2 diagonal energies, the 48 second-amplitude points,
and every one of the 141 same-representation pairs measured directly as a ± two-mode point —
96 + 96 + 282 = **474 energies** as ± pairs, and **291 energies** as the H deck of decision 37
(one energy per irrep-pure non-totally-symmetric pattern; `probes/deck_counts_planar.py`), which
is the deck this document prices. At benzene's 35 minutes per energy the 474-energy deck is about
280 hours; at naphthalene's measured 38.4 h it is 474 × 38.4 h ≈ 18,200 laptop-hours ≈ 760 days,
and the 291-energy H deck 291 × 38.4 h ≈ 11,200 laptop-hours ≈ 466 days (by estimate 123–203 days
on the priced desktop and 15–25 days on four Snellius nodes, the 474-energy figures of
`probes/results_timing/DURATION_TABLE.md` — 198–330 and 25–41 days — scaled by 291/474). **K**,
what the stopping rule reports (K = 2M + K_off; the second amplitude sits outside it), is smaller:
96 diagonal energies plus between 0.9 and 2.0 energies per allowed coupling — 0.9 is the no-prior
benzene rate (388 for 435 unknowns), 2.0 is the cap at which every pair is simply measured; the
benzene rerun under the prior needed 3.7 per pair, but on a deck built for the banded rule in
which only 12 of the 57 allowed pairs had a two-mode pattern, which is why the R1 deck is built for
the prior — so K is of order 220–380 energies, against about 1,400 energies and 800+ hours without
the prior. By the 168-hour rule of §8 the R1 deck on the laptop would be 18,200 / 168 ≈ 108 weekly
batches as ± pairs and 11,200 / 168 ≈ 67 as the H deck: on the measured number R1 at the
anchor's basis is **cluster work**, or the work of a dedicated many-core machine; the choice is
P13, open and now decidable. If probe B1 licenses the cc-pVDZ deck (§3.5), the same H deck is
priced at 291 × 3.9 h ≈ 47 laptop-days (proposed, P27, open; the 3.9 h is the measured 69-minute
cc-pVDZ tight energy times F). A further thinning of the couplings by a DFT-only rule (P25) was
tested on 16 September and is not licensed (§5.3); the hashed order and the stopping rule remain the
only economy on the couplings. The prior is what brings the energy route at naphthalene within
reach at all; it does not make it cheap.

**Dated note, 17 September (third pass; the pricing above is kept as the record of the energy
route).** Two measurements this week change what the deck is. (1) The amplitude test pre-registered
on 16 September ran on all 616 off-diagonal patterns of the naphthalene DFT dry run at half amplitude:
against the full-amplitude block on identical patterns and an identical 493/123 split, ρ_off went
0.962 → 1.029 (w = 25), 1.127 → 1.179 (200), 0.820 → 0.819 (no band), while the signal fell by 3.99×
as q² requires. The residual scales with the signal — neither quartic contamination nor a noise floor
but an identifiability limit of the energies-only design at this size (1,128 unknowns, 493 rows).
**The energies-only route to the couplings has no amplitude window at naphthalene**; the diagonal is
untouched (`probes/results_dryrun/naphthalene_sym/FINDING_2026-09-16_…`, outcome section). (2) The
gradient route of plan 06 was counted, stress-tested and priced (X14, X20, X21, 17 September). On the
symmetry pattern — only same-irrep pairs couple, exact for a symmetric molecule and already secured by
decision 37 — **9 pattern products = 18 gradients recover every element of Δ₂, diagonal included, with
zero recovery error**; the coupled-cluster force at the DFT geometry that the odd part of the
single-mode pairs supplied above is one more gradient at the reference geometry, and c₀ and Δ₄ served
only the energy read. **The deck is therefore 2k + 1 = 19 gradients at naphthalene and no energies.**
Truncating to the pattern costs 0.0017 cm⁻¹ on the worst family; the substitution recovery damps
gradient noise (amplification 0.27, against 0.71 for the dense 96-gradient construction); the worst
family stays under 0.5 cm⁻¹ across the plan's whole σ_g grid (0.5–5 µE_h per unit q, 0.05–0.46 cm⁻¹).
The count grows linearly with the mode count while the pairs grow quadratically (6, 9, 12, 13, 15, 16,
18 products from benzene to pentacene; 23 for C2v phenanthrene), so the advantage grows with size.
The gradient-to-energy cost ratio for LNO-CCSD(T) itself, never measured before this week, is
**g = 6.04 at eight threads** on the full LNO-CCSD(T) energy (M2a cell 3, benzene, 6-31G, three
repeats, 22:31; an earlier reading of 5.71/7.19 the same day was taken on PySCFAD's (T)-increment
attribute and is superseded — the four-thread bound is now 7.6 by inference, not measurement; the
cc-pVDZ measurement does not fit this laptop, and RHF/MP2 read higher at the smaller basis, 3.41/3.73
against 2.84/3.20). Against the break-even of 291/18 = 16.2 the deck prices at **19 × (6.04–7.6) =
115–145 energy-equivalents, a saving of 2.5–2.0× on the 291-energy H deck**: at the anchor's
measured 38.4 h that is ≈ 184–232 laptop-days instead of 466, and, should probe B1 license cc-pVDZ, ≈
19–24 laptop-days instead of 47; at pentacene the saving is 4.8–3.8×. Three things stand between this
note and a deck: whether PySCFAD's shipped LNO (IAO auto-fragments) can stand in for the Pipek–Mezey
frozen spaces of §3.3 or an in-house gradient (M2) is needed; the quartic contamination of the
gradient-difference read at q = 1, measured so far only on the stand-in (mode G, 0.05–0.21 cm⁻¹ per
family); and probe B1's verdict, which sets the hours per energy that g multiplies. Plan 06's decision
rule was amended the same day so that branch C stays open on the measured g. *Late the same day, the
first of the three open items was settled by its pre-registered test (M2b, 23:27): PySCFAD's shipped
LNO does **not** compute this plan's response — at arm A's thresholds it differs from the frozen-space
value by 5.5, 8.2 and 26.4 µE_h on benzene's three probe modes against a bar of 6, and at its own
default thresholds the C–C stretch response comes out at half the frozen-space value. The gradient
engine must therefore be built on the frozen spaces of §3.3 (M2, two to three weeks), not borrowed; the
counting, the noise behaviour and the closure of the energies-only route are unaffected, and the g of
6.04 above is the borrowed engine's — M2's own is unmeasured.*

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
September; all numbers below are from the corrected run described in the last bullet of this
subsection):

- *Design.* Benzene, cc-pVDZ, three normal modes — the totally symmetric ring mode at 1020 cm⁻¹; a
  non-degenerate C–C stretch at 1357 cm⁻¹, which belongs to the same irreducible representation as
  the 1186 cm⁻¹ mode it couples to in §3.2; and one component of a degenerate C–H out-of-plane
  pair at 865 cm⁻¹ (B3LYP/6-31G* harmonic values; the degenerate partner sits at the same
  frequency) — at nine displacements each; three arms at every geometry: **A**, the frozen spaces
  transported from equilibrium; **B**, the equilibrium localised orbitals transported but the
  fragment spaces re-selected; **C**, everything re-selected (the program as released). Two
  settings of the program's truncation thresholds ("default" and "tight"; a third, one decade
  tighter — "xtight" — on 12 September). A canonical CCSD(T) energy at each of the 27 geometries as
  the truth line.
- *Smoothness.* Against that truth line, arm A's energy scatters about a smooth curve by
  **0.002–0.06 µE_h** on the three modes at either threshold setting; arm C by 7–11 µE_h at default
  and 0.9–2.7 µE_h at tight thresholds, arm B 0.05–1.2 µE_h at tight. The requirement the couplings
  impose (§3.4) is about 2 µE_h; arm A meets it by a factor of 30 to 1,000 depending on the mode.
- *Bias.* The frozen space was chosen at equilibrium and fits a displaced geometry slightly less
  well; that bias is a clean quadratic in the displacement, i.e. exactly a curvature bias, and it
  shrinks with the truncation threshold: 2.6–14 cm⁻¹ on the bare local energy at default
  thresholds; **0.25–1.3 cm⁻¹** on the composite energy — the local energy plus the standard
  second-order correction for the truncated space, [MP2(full) − MP2(local)], as pyscf-forge's own
  corrected energy defines it — at default thresholds; **0.015–0.18 cm⁻¹** on the composite at tight
  thresholds. The pipeline's anchor ran at tight thresholds until 12 September; it now runs one
  decade tighter (decision 20, below); the threshold-sensitivity line of §7 still decides, per rung,
  whether that is enough or extrapolation in the truncation thresholds is required.
- *Reload.* Arm A reproduces the equilibrium-geometry energy exactly and reloads its spaces from
  file exactly (to 10⁻⁴ µE_h), which is the property the pipeline depends on.
- *Arbitrariness made visible.* Two runs at the same displaced geometry landed the fresh localiser
  on different, symmetry-equivalent orbital sets (overlap between the two landings 0.67), while the
  transported set stayed put; on benzene the two landings cost nothing, on a molecule of lower
  symmetry they would not be equivalent. This is the effect the domain review asked about and the
  reason the plan transports rather than re-localises.
- *Anchor basis.* The same scan at cc-pVTZ, the basis the licence rungs use — the three arms at
  tight thresholds, 27 geometries, then its own canonical truth line — finished on 8 September
  (three arms 1.7–2.0 h per geometry, canonical 14–21 min; 58 h in all). The frozen object stays
  smooth (0.002–0.021 µE_h), but its composite frequency bias grows with the basis: +0.47 cm⁻¹ on
  the out-of-plane mode, +0.03 on the ring mode and +0.79 on the C–C stretch, against +0.07, +0.015
  and +0.18 at cc-pVDZ in the same order (all bias figures in this document were halved on 10
  September: a curvature difference in the dimensionless coordinate is twice the frequency shift,
  and earlier versions reported the curvature), with the smallest singular value of the transported
  virtual space against the fresh one being 0.36 at the out-of-plane endpoint, 0.66 on the ring
  mode and 0.57 on the C–C stretch — the bias is not a monotonic function of that overlap across the
  three modes, so the mechanism is not settled by this scan. The bias is a pure curvature term (the
  quartic coefficient is zero on every mode) and enters Δ₂ directly. What to do with it — record it
  as a measured floor, enlarge the frozen virtual space and re-measure, or calibrate it per mode
  where a canonical reference exists — was decided on 8 September: measure first.
- *The tighter thresholds (decision 20).* The same scan with the local-correlation thresholds one
  decade tighter (the frozen arm only; the other two arms and the truth line stand) started on the
  evening of 8 September, died with the terminal session after 5 of 27 geometries (which is why
  long runs now launch detached from the session), was resumed from its saved points on 11
  September at 05:16 and **finished on 12 September at 11:48** (27 points, about 75 minutes each for
  the frozen arm alone). **Result (read the same day; `probes/results_m1/XTIGHT_READIN.md`):** the
  composite frequency bias falls from +0.47 / +0.03 / +0.79 to **+0.11 / −0.01 / +0.23 cm⁻¹**
  (out-of-plane, ring, C–C stretch), the bare LNO bias from +16.3 / +1.8 / +5.3 to +2.1 / +0.2 /
  +0.8, and the smoothness stays at 0.003–0.044 µE_h — so the residual at the tight thresholds was
  local-correlation truncation, not transport, and **the anchor object runs at the tighter
  thresholds**. The cost record carries the factor: about 2 at benzene¹ and, at naphthalene, F =
  3.34 measured on 14 September (38.4 h per energy at the anchor thresholds against 11.5 h at tight,
  §8; the ratio carries the out-of-core memory path as well as the thresholds). Per-mode calibration
  is not needed (research note P10, decision 20).
- *The basis-set line, second input (decision 26 (ii), printed 12 September 12:13;
  `probes/results_m1/BASIS_LINE_scf_mp2.md`).* DF-RHF and DF-MP2 at the same 27 points in cc-pVQZ,
  DF-RHF in cc-pV5Z — 19 minutes in all. The SCF part of the curvature moves by +1.8 / −2.4 / −4.6
  cm⁻¹ from TZ to QZ and by +3.8 / −2.8 / −3.1 to 5Z (against +44 / −22 / −51 from DZ to TZ): nearly
  converged. The MP2 correlation part still moves by −1.0 / −2.4 / −8.0 cm⁻¹ from TZ to QZ (against
  +15 / −12 / −16 from DZ to TZ). **The anchor's distance from its own basis-set limit is therefore
  an order of magnitude larger than the frozen-space bias just measured** — the largest known term
  in Δ₂'s budget at benzene, and the cheapest to carry. **P18, decided the same day (decision 33):**
  the anchor energy per point is the existing composite plus [MP2/QZ − MP2/TZ] + [SCF/5Z − SCF/TZ],
  every term a difference of computed energies at one geometry, no fitted parameter, under 1 % of
  an LNO point in cost; the licence comparison is unaffected (the terms are common to arm and
  reference); the measured effect on benzene's three probed harmonic frequencies is +2.8 / −5.2 /
  −11.1 cm⁻¹ — per-mode terms of the size of, and on one mode twice, the 5.45 cm⁻¹ mean over
  families that Esposito et al. 2024 report for the whole DFT-to-CCSD(T) gap at benzene (§11), which
  is why they belong inside the anchor and not in a budget line; the CCSD(T)−MP2 remainder's basis
  change stays unmeasured until the canonical QZ line of the cluster request (research note, P18;
  Ladder §3). The local step stays at cc-pVTZ rather than cc-pVDZ plus the same composite because
  that remainder itself moved by about 5–8 cm⁻¹ from cc-pVDZ to cc-pVTZ on the probed modes
  (research note §2.2d) — a shift the composite cannot carry; whether a *transferred* beyond-MP2
  increment can carry it at naphthalene is what probe B1 tests (§3.5).
- *A definition fixed by the measurement.* The transported orbital blocks must be
  semicanonicalised at each geometry — a rotation inside the frozen space that the fragment
  solver's MP2 start and (T) step assume; a first run without that step read a spurious bias of up
  to 147 cm⁻¹ and is kept on file as the record of the error (decisions 14, 15).

¹ Bookkeeping of the benzene factor: 4,576 s per xtight frozen-arm point against ≈ 2,200 s per
tight frozen-arm point; the result file's "×0.7" compares with the tight scan's 6,441 s per point,
which ran arms B and C as well — arm A alone was 2,160 s at the reference point.

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
cubic term of §2 without fitting either. Since decision 37 (14 September, confirmed 15 September)
a pattern confined to a non-totally-symmetric irreducible representation is measured with one
energy instead of a ± pair — its odd part vanishes by symmetry, measured at ≤ 0.55 µE_h on
benzene's b₂u mode at tight and xtight, and at ≤ 0.001 µE_h on three naphthalene modes once the
geometry is symmetrised to ≤ 10⁻⁸ bohr and every mode is projected onto its irrep (the factory
geometry, symmetric only to 4–7 × 10⁻⁵ bohr, gave odd parts of 23–34 µE_h per unit displacement,
comparable to the response, which is why the symmetrisation is a hard prerequisite of stage A);
totally symmetric patterns and the noise witnesses keep their pairs.

The noise the couplings can tolerate is measured per rung from the off-diagonal signal (decision
10): at benzene the requirement is about 2 µE_h per energy, ten times stricter than the 19 µE_h
the diagonal alone would tolerate at a 5 cm⁻¹ tolerance, and the frozen spaces meet it (§3.3). If
a larger molecule did not, the plan says in advance what happens: the off-diagonal block for that
rung is reported at its noise-limited precision and carries no accuracy claim, and the gradient
route of §5.3 takes over the couplings if the side project has delivered it by then.

### 3.5 The two pipelines (decision 36, 14 September)

Pipeline B is the label factory: for a molecule it produces the measured coupled-cluster
correction with its error budget — full decks at R0–R1 (and R1⁺, §5.2), thin decks above.
Pipeline A is the product: a network trained on pipeline B's labels (pre-trained on the DFT–DFT
corpus of Module 05) that takes a PAH's DFT Hessian and returns the per-mode correction and its
per-family error budget, licensed per family by the transfer tests — T-1, benzene → naphthalene on
the DFT stand-in correction; T-2, with the thin decks above naphthalene as hold-outs — and, once
R1⁺ has run, per charge state as well. Pipeline A's reach is R4–R6; its truth is pipeline B's;
where a family fails the transfer test, pipeline A returns DFT with the failure printed.

The label budget that sets pipeline B's pace is measured, not asserted: 38.4 h per naphthalene
anchor energy at cc-pVTZ (14 September). Three pre-registered levers were named against it, each
licensed by its own test before it enters a deck; their state on 16 September:

- **Decision 37 (lever H), confirmed.** One energy per irrep-pure non-totally-symmetric pattern
  (§3.4): the naphthalene deck falls from 474 to 291 energies. Measured admissible on benzene (14
  September) and confirmed by the naphthalene DFT dry run on the symmetrised geometry (15
  September).
- **Probe B1 (lever G), launched 15 September evening; verdict expected ≈ 21–22 September.** Whether a cc-pVDZ deck plus a transferred beyond-MP2 increment
  reproduces the cc-pVTZ anchor's curvatures within the Ladder's tolerance — pre-registered 14
  September (`notes/PreRegistration_2026-09-14_M3_DZ_Anchored_Decks.md`, under its old name). It
  runs at tight thresholds in both bases on three naphthalene modes. Its cc-pVDZ cells finished on
  15 September at 13:43 — 69 minutes per energy at 1.7 GB, a factor 9.9–10.0 below the cc-pVTZ tight
  energy — and its cc-pVTZ cells were launched that evening (≈ 6 laptop-days); **the verdict is
  expected around 21–22 September** and this copy carries it as [probe B1 verdict on the cc-pVTZ
  cells: to be filled by the student on 25 September]. A win prices the naphthalene H deck at
  291 × 3.9 h ≈ 47 laptop-days (proposed, P27, open), returns full decks above naphthalene to the
  ladder as desktop or Snellius-weeks items, and — because the cc-pVDZ energy ran in 1.7 GB against
  19.8 GB at cc-pVTZ —
  puts every molecule up to coronene within the laptop's memory by estimate (P27 §3); a loss leaves
  R1 at cc-pVTZ on the cluster route and the thin decks above it.
- **Dated note, 20 September, 18:5x — probe B1's first family is read and lost.** The cc-pVTZ cells of the C–H out-of-plane mode (naphthalene mode 12, 785 cm⁻¹) completed at 18:43; the beyond-MP2 basis increment of its curvature moves DZ → TZ by −8.1 cm⁻¹ at naphthalene against +7.9 cm⁻¹ at benzene (16 cm⁻¹ apart, sign flipped; 15.1 cm⁻¹ in the alternative definition), beyond the pre-registered lose line of 5 cm⁻¹. For this family the anchor stays cc-pVTZ, the DZ pricing of P27 is not licensed, and the increment becomes the basis term of the error budget (decision 26). The components show why: at cc-pVDZ MP2 softens this out-of-plane mode from 861 (SCF) to 618 cm⁻¹, the known double-ζ out-of-plane pathology of MP2 for arenes, partly inherited by the local coupled-cluster arm; it grows with the arene and does not touch in-plane modes. The in-plane families (modes 22 and 31, ≈ 22 and 24 September) are still read per family. Source: `probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md`.
- **Dated note, 23 September, 10:0x — probe B1's second family is read and won.** The cc-pVTZ cells of the C–H in-plane bend mode (naphthalene mode 22, 1045.1 cm⁻¹) completed on 22 September 19:21; the beyond-MP2 increment of the curvature, DZ → TZ, is +1.2 cm⁻¹ against benzene's registered +1.0 cm⁻¹ (0.2 cm⁻¹ apart, same sign: win on this family by the registered rule; `probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md`). So the licence is per family, as §3.5 states it: the cc-pVDZ-anchored deck is licensed for the C–H in-plane bend family and closed for the C–H out-of-plane family; the third family (C–C stretch, mode 31, five points ≈ 26 September) fills the placeholder's last entry. The P27 pricing keeps its TZ numbers until then.
- **Dated note, 23 September, 15:2x — the couplings are learned once the target is local (decisions 49 and 50).** The pre-registered learning curve E6 showed that no mode-basis model learns the couplings of the correction matrix at 45, 100 or 175 corpus molecules (ratio to the zero rule 1.00, slopes 0.00 to −0.04): the target flips sign with an arbitrary mode-vector sign that no per-mode descriptor can see. Written as pairwise local terms in primitive internal coordinates — which a parameter-free projection showed to carry three quarters of the correction, most of it in the bond–bond interaction constants inside rings — the same 175 molecules teach the couplings: ring coupling ratio 0.43 on the layer-A hold-out and 0.47 on 39 molecules of two cores never seen in training, corrected frequencies within 4.7 / 5.1 cm⁻¹ against 23 for no correction (`GoalGathering/notes/PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md`; demonstration note of the same day). The one failing molecule was a corrupted target: benzene's corpus ωB97X finite-difference Hessian, wrong by 133 cm⁻¹ from psi4's default grid, found by an analytic second route and now guarded (decision 50). For §6's learned layer this fixes the representation: local pairwise force-constant terms, projected; the read-out is the corrected spectrum, not matrix elements. Whether the coupled-cluster correction lives in the same pattern is being measured (E8, benzene CCSD(T)/cc-pVDZ on a rented machine, read-out 24 September).
- **Dated note, 24 September, 04:3x — E8: the coupled-cluster correction is local in the same pattern, one bond further.** Benzene's CCSD(T)/cc-pVDZ Hessian (72 gradients on a rented machine, two-route checks passed): 92 % of the correction to B3LYP lies in the pairwise pattern of 23 September, 98 % once pairs two bonds apart are added, and only then are the ring couplings recovered (ratio 0.34; the DFT proxy's couplings are nearest-neighbour, 0.15). Verdict by the pre-registered rule: between — the residual criterion met with room, the coupling criterion only with the extended pattern. For §6 this fixes the target of the CC-trained layer: pairwise local terms up to two bonds apart. One molecule; naphthalene follows when authorised (E8 pre-registration, outcome sections).
- **Dated note, 24 September, 21:2x — probe B1's third family is read: between.** The anchor finished at 21:02 (fifteen cc-pVTZ points, eight laptop-days). The C–C stretch (naphthalene mode 31, 1410 cm⁻¹) gives a beyond-MP2 increment DZ → TZ of −1.9 cm⁻¹ against benzene's −6.0: 4.1 apart, same sign, between the 2.5 win margin and the 5 lose line. Closing tally lose / win / between: the DZ-anchored deck is licensed for the C–H in-plane bend family only; the other two stay TZ-anchored with their measured increments in the error budget. The basis step on this mode is large (−47.6 cm⁻¹) but almost all SCF and MP2, the terms the deck computes cheaply. (`notes/PreRegistration_2026-09-14_M3_DZ_Anchored_Decks.md`, outcome sections; `probes/results_m1/M3_TZ_MODE31_READING_2026-09-24.md`.)
- **Dated note, 25 September, 08:3x — how far the locality carries, and the proof-of-learning run.** Three pre-registered proxy tests (DFT–DFT ΔH, the 229-molecule release): E9 — a substituted molecule's correction rebuilt from its parent core's block plus the Hessian columns within two bonds of the substituent (a quarter of the columns) returns the corrected frequencies to 1.7 cm⁻¹ against 23 without correction, on 182 molecules (pass); E10 — that neighbourhood block measured once on the smallest host and transplanted: between (3.4–3.8 cm⁻¹), eleven of fifteen substituent types within the bars, the rotors (CH₃, OCH₃, SH, CONH₂) not; a size split — the pair model trained on ≤ 26 atoms predicts the 27–34-atom molecules at coupling ratio 0.59 against 0.36 within size (encouraging, at the edge). Against this, L2 priced one LNO-CCSD(T)/cc-pVDZ energy of a 25-atom molecule at the anchor's thresholds above nine hours on eight threads: for substituted molecules the label needs a cheaper correlation tier, to be licensed on benzene against canonical CCSD(T) before it labels anything (`notes/PreRegistration_2026-09-25_L2b_Cheaper_Label_Tier.md`). The proof that the network learns — the design's success criterion — is partial (diagonal yes; couplings yes on unseen scaffolds with a rising curve, flat on bare parents); the decisive learning curve is pre-registered and running since 25 September on the corpus's layer B (100 → 1,200 small molecules, hold-outs: bare parents, unseen scaffolds, larger molecules; `notes/PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md`). The framing for the conversation — labels as a growing asset over two horizons — is `notes/Note_2026-09-25_Growing_Asset_and_Proof_of_Learning.md`.
- **P25 (lever B), not licensed.** Plan 06's DFT-only rule for ranking which couplings to measure
  (the resonance denominator 1/|ω_i² − ω_j²|), which at benzene found the pairs that matter with 19
  of 47, was put to its pre-registered test on the naphthalene stand-in on 16 September and lost:
  reaching 0.5 cm⁻¹ needed 76 of the 141 eligible pairs where the rule allowed at most half (70.5)
  and at most 1.5 × the oracle's 33 (X16). The saving "couplings × 0.4" therefore appears in no
  affordability table of this document; the deck stays at 291 energies with levers G and H only.
- **Dated bullet, 17 September — the gradient route (plan 06 branch C), now counted and priced.**
  The energies-only route to the couplings has no amplitude window at naphthalene (amplitude test,
  all 616 patterns, 17 September: ρ_off 0.962 → 1.029 while the signal fell 3.99×; §3.2, dated
  note). On the symmetry pattern 9 products = 18 gradients recover Δ₂ exactly, one more gradient
  supplies the geometry term, and c₀ and Δ₄ served only the energy read: **the deck becomes 19
  gradients and no energies**. With g = 6.04 measured for LNO-CCSD(T) (benzene, 6-31G, eight threads, full
  energy; 7.6 as an inferred bound) that is 115–145 energy-equivalents against the 291-energy H deck —
  2.5–2.0× — and the saving grows with size (4.8–3.8× at pentacene), because products grow linearly with the mode count
  while pairs grow quadratically. It enters no affordability table of this document yet: the transfer
  gate is M2a's rule, and the open items are named in §3.2 (PySCFAD's IAO-fragmented LNO against the
  Pipek–Mezey frozen spaces — settled the same night by M2b: it does not stand in, so the engine is
  built in-house (M2, two to three weeks); the quartic contamination of the gradient read at q = 1;
  probe B1).

## 4. Research questions

**Accuracy (benzene to coronene, and the first cation).** Can a per-molecule pipeline — DFT
geometry, harmonic Hessian and anharmonic constants, plus a probed coupled-cluster correction to
the harmonic force constants — produce band positions that measurably improve on scaled-harmonic
DFT (PAHdb), on an in-house calibrated-harmonic baseline, and, where its coverage overlaps, on the
published DFT-based machine-learning molecular dynamics of Mai et al. 2025, judged per band against
laboratory spectra? And, on the two molecules where the laboratory intensity is calibrated, do its
anharmonic intensities improve on the harmonic ones?

**Cost (every rung that ran), conditional on probe B1 above naphthalene.** How many
coupled-cluster energies did that correction need per molecule — benzene, naphthalene,
naphthalene⁺ and the three-ring rung, K and K_off printed beside each spectrum — and, *if probe B1
licenses the cc-pVDZ deck* so that full decks return to the pyrene-size rung and coronene, how did
the off-diagonal count grow between naphthalene, the pyrene-size rung and coronene, measured
against the number of couplings the molecule's symmetry leaves free? If probe B1 loses, the rungs
above naphthalene carry thin decks, K_off is measured at benzene, naphthalene and naphthalene⁺
only, no size sentence is earned above R1, and the cost records stand alone (§5.3).

**Reach (C₃₈₄H₄₈-class).** Can the labels of pipeline B, through the network of pipeline A,
produce a spectrum with a stated error budget at a size where no anharmonic or
coupled-cluster-quality prediction — and no laboratory spectrum — exists? Here no "beat" is
claimed, and the plan is explicit about a hard limit: whole-molecule probing of a 432-atom molecule
with energies only costs, under this protocol, four energies per vibrational mode for the diagonal
alone — 5,160 coupled-cluster energies of a very large molecule, before a single coupling — and is
not attempted. The only route by which that cost stops depending on size is to probe the
correction on capped fragments of the flake, which uses a locality-verified electronic correction
obtained on one region for another. The student ruled (decision 1) that this is not a scope
question but a method: if it works and the goal is reached with it, it is used; if the locality
measurement at the middle rungs says it does not, it is not. The largest species remains a promised
deliverable in this sense: the network's prediction licensed or refused per family, a
fragment-probed check where the four-part licence of §5.2 permits it, or the measured reason none
could be produced.

## 5. Approach

### 5.1 The pipeline, per molecule

1. **Geometry, harmonic Hessian and dipole first and second derivatives** at the pipeline's DFT
   level, analytic, on the student's laptop's CPU through coronene (it has no CUDA GPU; any GPU
   work is rented time); DFT cubic and semi-diagonal quartic constants for the scored band
   families and every mode the resonance search couples to them. **The production DFT level
   (functional, dispersion correction, basis set, integration grid) is a pre-registered constant
   that is not yet chosen**; the DFT engine is psi4 1.11 (the rehearsal's Hessians ran there), the
   anchor is pyscf-forge's LNO-CCSD(T) in PySCF 2.14, and the VPT2 implementation is a pilot-note
   constant with its candidates recorded in the bibliography — the null row of §7 separates this
   pipeline's anharmonic step from the correction inside the pipeline, and is commensurate with
   line B only if the production level is B3LYP/N07D with a polyad treatment of the same kind,
   which is why §13 item 13 asks which level counts as the same footing. The level is fixed, from
   the opponents' levels and the anharmonic literature (the PAHdb-anharmonic standard is
   B3LYP/N07D with a 200 × 974 integration grid, Esposito et al. 2024; the CMA studies find basis
   quality to matter more than correlation level for the normal-mode basis; aug-cc-pVTZ is set
   aside for benzene-type rings on one reported linear-dependence artefact — the spurious 495i
   cm⁻¹ ring-puckering frequency of Olive Dornshuld et al. 2026 — until a run shows it absent for
   the ladder's molecules), before the naphthalene rehearsal's recovery runs, so that the
   rehearsal constants the stopping rule uses (§3.4) and the noise-injected column of the pilot
   note are read at the production level; the benzene rehearsal so far used B3LYP/6-31G* against
   BHHLYP/6-31G*, the naphthalene dry run the same pair on a symmetrised geometry, and the Module-05
   corpus factory computes both B3LYP and ωB97X (the QM9 layer is ωB97X as served). The geometry
   is symmetrised to ≤ 10⁻⁸ bohr and every mode projected onto its irreducible representation
   before any single-sided energy (decision 37's hard prerequisite, §3.4). The choice is recorded
   in the pilot note with its reasons.
2. **Δ₂-probing.** The deck of displacement patterns; at each, the composite local coupled-cluster
   energy in the frozen spaces of §3.3 and the DFT energy; recovery of Δ₂ in the DFT normal-mode
   basis under the symmetry prior of §3.2; K read by the stopping rule of §3.4. Three licences
   gate it: an **anchor licence** against the noise, bias, basis-set and threshold-sensitivity
   formulas fixed in the pilot note (§7); a **probing licence** at benzene and naphthalene against
   directly computed reference corrections — at naphthalene the reference is the full deck itself,
   every same-representation pair measured directly, against which the recovery from the hashed
   prefix is judged; at benzene it includes a canonical coupled-cluster reference, the only one
   independent of the space freezing; and a **locality test** computed on directly measured Hessian
   blocks — never on the recovered correction alone, which could certify the locality its own prior
   imposed. Modes that are infrared-inactive by symmetry are not dropped — their diagonal is cheap
   and their fundamentals reach the spectrum through resonances — but the coupling blocks made only
   of inactive modes are tested per rung in the DFT rehearsal and left out of the deck only where
   the scored positions do not move (decision 19). (Each mode's diagonal costs two energies inside
   K — a ± pair, or under decision 37 one energy per amplitude for a non-totally-symmetric mode —
   and the second-amplitude points that sit outside K and yield the cubic by-product, §3.4.)
3. **Spectra** by second-order vibrational perturbation theory with explicit resonance treatment
   (GVPT2; the implementation is pinned in the pilot note as a pre-registered constant, with named
   resonance thresholds and a polyad cap; from the pyrene-size rung upward the anharmonic
   constants are built in reduced dimensionality — Hessians differentiated only along the scored
   modes and the partners a dimensionless coupling indicator and the Darling–Dennison test select,
   after Fusè et al. 2024, whose thresholds are pilot-note candidates — on the DFT anharmonic
   constants and the Δ₂-corrected harmonic part, plus a first-order geometry term: the corrected
   surface's own minimum shifts slightly from the DFT one, by the coupled-cluster force at the DFT
   geometry — the odd part of the totally symmetric single-mode ± pairs whose even part gives the
   diagonal, so it costs nothing extra — divided by the corrected curvature, and that shift is
   applied and printed on every scored band); **no scale factor** on anharmonic output. Every
   spectrum carries positions, anharmonic intensities from the DFT dipole derivatives (the same
   physics PAHdb's intensities rest on, computed anharmonically rather than harmonically) and a
   drawn width at the resolution and temperature of the source it is compared with, each labelled
   with its provenance.
4. **Error budget** per band: DFT level, held-out residual, measured noise and space-freezing
   bias, the anchor's **basis-set line** (decision 26: the measured cc-pVDZ → cc-pVTZ change of
   the canonical curvature, +67 / −33 / −73 cm⁻¹ on benzene's three probed modes, two thirds of it
   at the SCF level; the literature distance of CCSD(T)/cc-pVTZ from the basis-set limit once
   read; a canonical cc-pVQZ diagonal line in the cluster request — the 5.45 cm⁻¹ expected-effect
   figure of §11 is a mean absolute difference over benzene's modes at a near-complete basis: it
   bounds what this anchor can buy *on average over families*, not per mode, since the per-mode
   basis terms of §3.3, +2.8 / −5.2 / −11.1 cm⁻¹, exceed it on one mode) — of which the SCF and MP2
   parts are carried inside the anchor since decision 33 (§3.3), leaving the basis change of the
   CCSD(T) − MP2 remainder as the open budget term —, the share of the family's correction that
   comes from couplings beyond the locality test's radius, and the matrix–gas shift where matrix
   data is used.

### 5.2 The size ladder (species and claim types of plan 04; the cation rungs and the three-ring rung added by decisions 39, 41 and 42)

| Rung | Species | Type | Deck | What it licenses in plan 05 |
|---|---|---|---|---|
| R0 | benzene | agreement (decision 28): within the laboratory uncertainty plus the pipeline's own budget; the opponents are printed, not claimed | full, cc-pVTZ at the anchor thresholds; priced at the rehearsal's 448 energies (§8) | probing licence against local and canonical references; the anchor's bias and basis-set lines (canonical reference); intensities scored for agreement |
| R0⁺ | benzene⁺ | timing point, and a deck decision | one cc-pVDZ energy at the D₂h minimum, ⟨S²⟩ and T₁ printed — **measured 15 September: c = 31.0** (below) | the cation cost ratio c; whether benzene⁺ gets a deck at all is a written decision to take with the supervisor, because its D₆h ground state is Jahn–Teller active and a static deck about one D₂h minimum does not describe the observable spectrum without a vibronic treatment this pipeline does not contain (P27 §5, open) |
| R1 | naphthalene | agreement, plus the per-family question whether the correction adds accuracy over DFT | the H deck of decision 37: 291 energies (114 in the diagonal block); cc-pVTZ at the anchor thresholds on the cluster route, or cc-pVDZ if probe B1 licenses it | the noise measurement (decision 35, §7); the anchor licence closes; first locality read; intensities scored for agreement; the first transfer datum |
| R1⁺ | naphthalene⁺ | agreement (its gas-phase and matrix columns are named before Module 03 prints them, under the no-swap rule; none is named here from memory), plus the charge-state transfer datum | the neutral's H deck (291 energies; the diagonal block of 114 as the fallback), the same point group and frozen-space machinery; **condition: the unrestricted (T) port of decision 41** | whether the network may be licensed per charge state; the first cation label of pipeline B |
| three-ring rung (decision 39) | anthracene and phenanthrene — the isomer test at equal size | transfer: the per-family go/no-go for the size axis, read as the transfer 2 → 3 within 2.5 cm⁻¹ for both isomers, together with the price curve over three sizes | full decks in cc-pVDZ if probe B1 licenses the basis, thin decks otherwise (decision 39); P27 proposes diagonal-first H decks at the tight thresholds, 156 + 178 = 334 energies, with one xtight energy per isomer as the printed bias check, and counts the full decks at 818 and 1,432 energies — phenanthrene, C₂v rather than D₂h, allows 584 same-representation pairs against anthracene's 277 (proposed, P27, open) | the go/no-go per band family; the exponent that prices the rungs above; the anchor diagnostics per molecule (T₁, the (T) share, the largest LNO domain; for cations ⟨S²⟩) printed from here on (decision 39) |
| R2 | pyrene, chrysene, triphenylene, tetracene | accuracy for the C–H out-of-plane families (hot gas, decidable by margin); the C–H stretch family is scored on the jet-cooled 3 µm column only once a scoring rule for its resonance polyads is agreed (§13 item 8) and is not counted as promised until then (decision 25); C–C families expected undecidable on the existing gas data, see below | thin decks (the diagonal blocks, ≈ 170 energies for pyrene as an H diagonal deck, P27) unless probe B1 returns full decks; P27 proposes that chrysene and triphenylene leave the coupled-cluster ladder and serve as network hold-outs at DFT level, their gas-phase columns being undecidable by construction (proposed, P27, open) | the first off-diagonal-count ratio *if probe B1 licensed full decks*; direct-block locality probe; a canonical diagonal check at pyrene (scaled from the measured benzene point: 620 against 264 basis functions at cc-pVTZ, N⁷ time and N⁴ memory give roughly 400 × 755 s ≈ 80 h and 30 × 7.3 GB ≈ 220 GB per energy, for 2 × 72 + 1 = 145 energies — cluster work by two orders of magnitude, classified by the rule of §8, and skipped with a printed sentence if no cluster time exists) |
| R3 | coronene | accuracy on the cold column (decision 24), transfer | thin deck (204 energies as the diagonal block, `DURATION_TABLE.md`) unless probe B1 returns the full deck | the second ratio and the numeric size sentence *only if probe B1 licensed full decks*; otherwise the cost record stands alone |
| R4–R5 | C₅₄–C₂₁₆ class | reach; the R4 fragment checks conditional on cluster access | none (network rungs) | expert-judgment datum (§13, item 5c); the first rungs where the learned prior, if it earned its licence at the accuracy rungs, may carry the recovery; the fragment-vs-whole comparison on a molecule larger than coronene and the fragment-radius convergence test |
| R6 | C₃₈₄H₄₈-class | reach | fragment-probed only | under a four-part measured licence (locality at the accuracy rungs; coronene probed in fragments reproducing coronene probed whole; the same on a larger molecule where the cluster allows; a fragment-radius convergence test on the flake's own interior); otherwise a per-family or full refusal |

*The order above naphthalene (decision 39, 14 September).* The ladder is built slowly, ring by
ring, with ions: the three-ring isomer pair first, then pyrene and tetracene (the peri main axis
and the acene stress branch, so that a family which transfers for one topology and not the other
is licensed per topology rather than refused), then a five-ring pair (perylene or pentacene) only
after the four-ring rung and only if the per-family transfer 3 → 4 held. The go/no-go per band
family is read after the three-ring rung — by P27's pricing 35–70 laptop-days or 9–30 desktop-days
after naphthalene for the diagonal-first decks (estimates on the measured cc-pVDZ energy; proposed,
P27, open) — instead of at the pyrene thin decks of March 2027; the extra months of the rungs above
are finishing work after that decision, not its precondition. Decision 39's "≈ 2–3 desktop-weeks"
for the three-ring rung holds only for diagonal-first decks at the tight thresholds; the full decks
of both isomers (2,250 energies; 1,514 as H decks) are 160–320 laptop-days at tight even as H decks
(P27 §4). The acenes are the stress branch because long acenes are expected to reach the region
where a single-reference anchor becomes doubtful; the T₁ diagnostic printed per molecule marks it,
and the threshold's source is Crossref-verified before the pilot note fixes it (P27 §4).

*The cation rungs (decisions 39, 41, 42).* The cations are the gap the affordability collection had
to close, and they enter where it is cheapest: naphthalene⁺ first, because its D₂h ground state is
non-degenerate and its deck, point group and frozen-space machinery are the neutral's; benzene⁺ as
the timing molecule. The price was measured on 15 September (`probes/results_m4/`, quiet machine):
the benzene neutral LNO-CCSD(T) energy at cc-pVDZ tight took 164 s, benzene⁺ at the same geometry
with the installed unrestricted code (`ULNOCCSD_T`, 15 + 14 spin-fragments, 4.2 GB, UHF ⟨S²⟩ 0.870
after one stability round) 5,096 s — **c = 31.0**. Of those 5,096 s the unrestricted CCSD alone
took 1,264 s (c_UCCSD = 7.7), so the (T) kernel — a NumPy reference implementation in the installed
code, not the compiled kernel of the restricted path — is 3,832 s, 75 % of the cost. With c = 31 no
cation deck fits the laptop (the R1⁺ H deck ≈ 1,460 laptop-days at xtight, ≈ 430 at tight; the
diagonal H deck ≈ 170 at tight) and on the desktop only the diagonal deck at tight (45–75 days)
would. **Decision 41 (15 September) answers this with own software:** an unrestricted compiled (T)
kernel for the LNO fragment energies, PySCF's compiled restricted kernel as the model, with its
acceptance tests fixed now — the benzene⁺ energy equal to the NumPy kernel's to 10⁻⁸ E_h on the
same fragments; time ≤ 1.5 × the restricted compiled (T) for the neutral; the shipped CH₃ comparison
against canonical UCCSD(T) unchanged — expected to bring c to ≈ 8–9 (the UCCSD's 7.7 plus a compiled
(T) of the restricted kind's cost), the R1⁺ diagonal H deck to ≈ 45 laptop-days at tight and the
full H deck to ≈ 115 (desktop 30–50). It is desk work of one to two weeks in the private part of the
repository (Software Changes Ledger row 13), starts after this proposal is safe, never displaces the
probe B1 cells, and nothing is sent upstream without the student's word. R1⁺ runs after R1 and
after the port passes its tests; if the port fails, R1⁺ falls back to its diagonal deck at tight on
the desktop or lapses with a printed sentence.

*Laboratory sources per rung.* Benzene: the NIST Quantitative Infrared Database cell spectra (Chu
et al. 1999), with calibrated intensities. Naphthalene: the PNNL quantitative vapour-phase record
at 0.112 cm⁻¹ and 25 or 50 °C — the methods state 25 °C, the introduction and the figure caption
50 °C; the record header decides — (Schneider et al. 2024, in the database described by Sharpe et
al. 2004), with calibrated intensities; Pirali et al. 2009's sixteen fundamentals at 0.005 cm⁻¹,
read at the Q-branch head with the hot bands resolved away, as a second labelled column (scored
with no temperature shift and a 0.5 cm⁻¹ head-to-origin term, since the fundamental is read
directly — decision 21); the hot NIST WebBook entries as labelled extra columns; Pirali et al.
2009 and Joblin et al. 1995 for the temperature term. Naphthalene⁺: gas-phase and matrix spectra
exist and are named before Module 03 prints its columns, under the no-swap rule (P27 §5). Pyrene,
chrysene, triphenylene: NIST WebBook hot-vapour GC-IR spectra at 8 cm⁻¹ without concentration data,
and, for the C–H stretch family only, the jet-cooled 3 µm IR–UV ion-dip spectra of Maltseva et al.
2016 as a labelled cold column. Tetracene: matrix isolation, plus a jet-cooled band list (Lemmens
et al. 2019). Coronene: matrix isolation, six jet-cooled 6–15 µm bands (Lemmens, Rijs & Buma 2021)
as the primary cold column, and the 770 K heat-pipe spectrum of Joblin et al. 1994 with the slopes
of Joblin et al. 1995 as the labelled hot column (decision 24). Chu 1999, Schneider 2024, Pirali
2009, Joblin 1994 and 1995, Lemmens 2019 and 2021, Mattioda 2020 and Brumfield 2012 were read in
full (6 and 8 September) and their conditions transcribed; Maltseva 2016 is held at abstract grade
and its band tables are asked for (§13, item 8) (bibliography, "Readings of 2026-09-06 —
laboratory sources"). Three readings changed numbers, not rules: the benzene intensities are not
certified where water, CO and CO₂ absorb (1325–1900, 2050–2225, 2295–2385 and 3550–3950 cm⁻¹), so
the intensity score at benzene excludes the C–C band near 1480 cm⁻¹; the hot-band slopes of Joblin
et al. 1995 replace the earlier recalled floor (the largest measured 6–15 µm slope is 0.044 cm⁻¹
K⁻¹, coronene's 6.2 µm band), and their model gives the room-temperature term per family; and the
jet-cooled coronene bands at 7.7 and 8.8 µm lie 10–19 cm⁻¹ from where the hot spectra of Joblin et
al. 1994 and the slopes of Joblin et al. 1995 put a cold band. The jet-cooled band is the pipeline's
most direct 0 K observable, so it is the primary cold column with the laser bandwidth as its
uncertainty; the hot-extrapolated position is a second, labelled column, and a family is called
inconclusive only if the two disagree on the verdict (decision 24).

A per-family decidability rule replaces plan 04's rung-level gate: a gas-scored family is
decidable if the scoreboard's **measured band-centre uncertainty** — instrument resolution,
centroid precision and a temperature term — is smaller than its beat margin; a matrix-scored
family passes through the matrix–gas gate or is pre-declared inconclusive. Benzene and
naphthalene are therefore scored unconditionally on room-temperature cell spectra; the first
benzene scoreboard was printed on 10 September from the NIST Quantitative IR record at 0.125 cm⁻¹
(four IR-active fundamentals, integrated intensities agreeing between two records of the series to
≤ 1.3 %), and on it the temperature term is the pipeline's own computed 296 K shift with ±30 %
(decision 29), so the laboratory side of the R0 agreement test is a few tenths of a cm⁻¹, not the
2.6 cm⁻¹ a generic floor would give. For the pyrene-size rung, a systematic search on 5 September
(NIST WebBook, the PNNL database, PAHdb's experimental library, and journal searches on jet-cooled
and cell spectroscopy of each species) found no gas-phase spectrum of known temperature for
chrysene or triphenylene in the 6–15 µm region; for pyrene it found the hot heat-pipe spectrum of
Joblin et al. 1994 at 570 K (with the 8.5 and 12 µm slopes of Joblin et al. 1995 — the same
two-column treatment as coronene's applies), the jet-cooled 3 µm list of Maltseva et al. 2016 and
one rotationally resolved cold band (Brumfield, Stewart & McCall 2012, read in full: origin
1184.0356 cm⁻¹, T_vib ≤ 111 K), all now named as labelled columns. The C–C stretching families at
R2 are therefore expected to be undecidable by construction (they carry the largest temperature
shifts and the smallest beat margins, so the GC-IR entries' unknown vapour temperature swamps
them; the strong, isolated C–H out-of-plane bands shift least and keep a usable margin); the plan
says so before any number exists, and the student has decided to sign off the scoreboard module
with that expected result rather than wait for a source that may not exist (decision 3, addition
of 5 September). §13 still asks.

### 5.3 Why the cost is reported in numbers and never in adjectives; the gradient side project

The plan allows exactly two kinds of cost sentence. The **cost record** — K and K_off, route,
prior, measured noise and stopping threshold, wall-clock per probe, the script that printed it —
is promised for every rung that ran. A **size sentence** is numeric only: how K_off went from
naphthalene to coronene against how the mode count went and against the free-element count
symmetry leaves. The adjectives "size-independent", "O(1)" and "saturates" are forbidden in any
sentence about this project's own cost. **The losing condition of the size question:** if K_off
grows from naphthalene to coronene at least as fast as the count of symmetry-allowed couplings,
no size sentence is earned and the cost records stand alone. **The size question is now
conditional on probe B1 (§3.5):** only if the cc-pVDZ deck is licensed do full decks — and with
them K_off — exist above naphthalene; with thin decks there the size sentence is not attempted, and
what the ladder measures instead is the per-family transfer of the diagonal correction (T-2 and
the go/no-go of §5.2). Any favourable size sentence is expected, if at all, to come from the prior
— symmetry or learned — and not from sparsity as such.

The domain review's reading of the software landscape stands as a reading of the codes'
documentation, to be confirmed by the run/no-run check of §8: no production code offers an
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
terms are frozen now (its milestones are numbered M2–M5, continuing the plan's numbering after
probe M1; they are unrelated objects and are named here by molecule; the basis probe of §3.5 is
"probe B1", not an M-number):

- **M2** (benzene; laptop): the engine version pinned and printed; the
  automatic-differentiation gradient with the frozen-space projection inside the differentiated
  graph agrees component-wise with central finite differences of the re-projected frozen-space
  energy; its smoothness along the same modes as probe M1 printed; the projection term of the
  gradient measured. M2 runs first at cc-pVDZ, where the canonical analytic gradient fitted the
  laptop (13.9 GB, §8), because at benzene every fragment spans the whole molecule and the
  memory argument above gives no relief there; the cc-pVTZ repeat is M3's first item, and a
  failure at cc-pVTZ that is memory-only (correctness and smoothness passed at cc-pVDZ) is
  recorded as such and does not by itself trigger the kill criterion (cold read of 8 September,
  finding 22). Passing M2 licenses the gradient route at benzene. *State on 16 September:* M2's
  first cells (M2a, the gradient cost ratio g at benzene cc-pVDZ) ran on 14 September; g is
  unmeasurable on the laptop at the coupled-cluster level (X16, 16 September), so M2's
  coupled-cluster cells wait for a machine with more memory.
- **M3** (benzene at cc-pVTZ, then naphthalene at cc-pVTZ; laptop): the same correctness,
  smoothness and projection-term printouts, plus wall-clock per gradient
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
gradient count; if it fails, the energy route remains the fallback, at the deck cost of §3.2.

*The related idea plan 06 ("equivalent, faster mathematics").* That plan fed two things into this
one: substitution probing (P24, pre-registered as a second measurement layer, decision 34) and the
DFT-only rule for ranking which couplings to measure (P25). P25's pre-registered licence test on
the naphthalene stand-in lost on 16 September (76 of 141 eligible pairs needed for 0.5 cm⁻¹, against
at most 70.5 and at most 1.5 × the oracle's 33; §3.5), so lever B is not licensed and appears in no
table here. With g unmeasurable on the laptop at the coupled-cluster level (14 September) and P25
not licensed, both closing conditions of plan 06's cost branch hold, and under its own decision rule
that branch closes at the 15 October review. What survives from it for this plan: the symmetry
prior's nine Hessian–vector products, which recover naphthalene's 141-pair block exactly on the
stand-in tensor (X16) and matter only if a gradient becomes available on a larger machine; and the
locality readings X8 and X9, which at two rings confirm what benzene showed (zeroing Δ₂'s atom-pair
blocks beyond bond-graph distance 4 still moves a band by 10.5 cm⁻¹, beyond 5 by 5.4, beyond 6 by
0.4).

## 6. What this project deliberately does not do, and why

**No train-once motif transfer; a network licensed per family instead.** Plan 04's attempt to
learn a correction on one ring motif and reuse it on another failed its own transfer test. That
measured failure is why every molecule on the licence rungs gets its own probed correction, and
why the network of pipeline A is promised only as a *licensed* predictor: trained on pipeline B's
measured labels, tested per band family by T-1, T-2 and Q9 with the losing condition written
first, and refused per family — returning DFT with the failure printed — where a test fails
(decision 36, 14 September). Its accuracy claim on R4–R6 is the grounded error budget, not a beat;
its losing condition per family (τ_F, P26 memo §6) is its licence; and the two measured conditions
that gated it when it was still a follow-up (decision 32, 12 September; superseded by decision 36,
see the change log) remain the gates of that licence: the range of the correction at the accuracy
rungs, now read from the thin decks' transfer test T-2, and the Q10 coverage table below. The
Module-05 deep-learning component predicts only *where* the correction is likely to have large
off-diagonal elements, is trained on a public-plus-own DFT-vs-DFT Hessian corpus (§8, §10 item 4),
and enters a promised rung only after a licence: its saving demonstrated on that corpus against
the symmetry prior's free-element count, and its result checked prior-free at that rung. The
student ruled more generally that a rule inherited from an earlier plan carries no authority of
its own — knowledge transfer is allowed wherever a gate shows it makes the pipeline succeed.

**The pre-registered route to the large PAHs (decision 27, 10 September).** Between the accuracy
rungs and the largest sizes stands one test, gate Q9, written before any correction at pyrene size
exists. For each band family — the C–H out-of-plane bands per hydrogen-adjacency class, the C–H
in-plane bends, the C–C stretches, the C–H stretches — the per-mode diagonal correction δω_F is
already printed on every accuracy rung; Q9 asks whether it is a per-family constant c_F (the
per-family constant of this test, not the cation cost ratio c of §5.2), or at most a
one-parameter size law c_F + d_F/N_C, across benzene, naphthalene, anthracene, the four R2
species and coronene: eight molecules, six sizes (C₆, C₁₀, C₁₄, C₁₆, C₁₈, C₂₄), four topologies, no
coupled-cluster energy beyond those the ladder computes. Q9's anthracene point depends on the
anthracene deck running — under decision 39 anthracene is the three-ring rung of §5.2, so the point
exists if that rung runs, and phenanthrene adds a second C₁₄ molecule to the test; if P27's
proposal to move chrysene and triphenylene to DFT-level hold-outs is adopted, the molecule list
follows the ladder as run (proposed, P27, open). The test is leave-one-molecule-out; a family wins
only if the transfer error is within its beat margin τ_F on every R2 and R3 molecule and the
family's members agree among themselves to the same margin; a family that loses is never applied
above coronene, and that sentence is written now. A family that wins gives the large PAHs
something the coupled-cluster arm cannot otherwise reach: line A's positions for that family
shifted by c_F with the held-out error as their error bar, shown with provenance because no truth
exists there, and one falsifiable prediction per family that the fragment-probed C₃₈₄H₄₈ flake then
checks. Expectations are recorded as expectations: transfer is plausible for the C–H stretch and
the out-of-plane classes, doubtful for the delocalised C–C families. This is not plan 04's motif
transfer — two parameters at most, across sizes, with the losing condition first.

**The calibration check (decision 31, 10 September).** Small errors are not enough for a data
generator; the error bars must be true. For every scored band on R0–R3 the pipeline prints whether
the laboratory value lies inside k·u_total (k = 1, 2), with u_total the laboratory uncertainty
combined with the per-band budget, and reports the coverage per rung, per family and overall
against the nominal 68 % / 95 %; the pass thresholds are fixed in the pilot note before any
pipeline-vs-lab number exists, and a budget that falls short is declared incomplete and its deficit
reported — it is never widened afterwards to reach the nominal. That table, not the mean error, is
what would let a reader trust the pipeline's bands as training labels.

**What the network is trained on, and what decides whether it can exist.** Pipeline B produces
the two things pipeline A needs. It measures the *range* of the correction — whether a block of Δ₂
between two atoms is fixed by their local environment or by the whole molecule — on the directly
measured blocks of the full decks at R0, R1 and R1⁺ and, above naphthalene, through the thin
decks' transfer test T-2; that measurement decides whether a transferable model of Δ₂ can exist at
all. And every rung delivers Δ₂ itself, hundreds of atom-pair blocks per molecule, thousands more
from the fragment probing at the top of the ladder: training data for a model that predicts the
correction from local structure, the classical Δ-learning target — a small, smooth difference, not
the potential-energy surface plan 04 tried to learn. If the range is short, the network is trained
and licensed per family as §3.5 says, and a new PAH then needs only its DFT steps and a sampled
coupled-cluster check instead of the full probe count. If the range is long, no such model exists,
pipeline A returns DFT with that sentence printed for every family, and the pipeline remains a
per-molecule measurement. Either outcome is a result; neither is claimed here.

**No promised coupled-cluster anharmonic correction** (§2; the diagonal cubic by-product is
reported, not applied). **No coupled-cluster correction to intensities** (§7). **No predicted band
widths** (§7). **No full coupled-cluster surface or global quartic force field.** **No new
empirical scale factors** (the in-house calibrated-harmonic baseline is an opponent, not the
method). **No light–matter dynamics and no new emission model** (the emission cascade model of
Mulas et al. 2018 is inherited post-processing where an emission spectrum is drawn). **No species
identification in JWST spectra.** **No sub-tolerance accuracy language.** **No whole-molecule
probing at C₃₈₄H₄₈** (§4). **No vibronic treatment**: benzene⁺'s Jahn–Teller surface is outside the
pipeline, which is why R0⁺ is a timing point and not a deck until decided otherwise (§5.2).

## 7. Evaluation design

**What is scored, what is shown.** Band **positions** are the promised quantity and are scored on
every rung where a laboratory band passes the decidability rule. On benzene the score is
**agreement**: |predicted − laboratory| within the laboratory uncertainty combined with the
pipeline's own budget, per band; the paired comparison with the opponents is printed there and
claims nothing (decision 28). From naphthalene upward the paired comparison carries the claim.
**Intensities** are shown for every molecule with their provenance and are **scored on benzene and
naphthalene** — the two rungs with calibrated gas-phase intensities — as a second, separately
reported quantity: the integrated band intensity of each scored band, the pipeline's anharmonic
value against the calibrated-harmonic baseline's harmonic value and against PAHdb's where it
reports one, with the source's stated intensity uncertainty as tolerance (decision 18). Elsewhere
the intensities stand beside PAHdb's computed ones as a comparison, not a verdict: both are DFT,
and no scoreboard exists. Matrix intensities never score. No coupled-cluster correction to
intensities is promised: Madriaga & Crawford's objection to local-CC field derivatives stands, and
whether the frozen-space object removes it is a measured question — a dipole companion to probe M1
(**M1-μ**: the frozen spaces' dipole moment along the same modes against canonical CCSD(T)), owed,
scheduled after the R1 timings and before the pilot note — and only a printed result can turn it
into a proposal. Band **widths** are drawn at the source's resolution and temperature and labelled
as presentation.

**Dated note, 19 September (third-pass follow-up; the desk note `notes/Desk_2026-09-17_Tolerance_and_Label_Count.md` and the shape test of 17 September).** Two measured facts sharpen how the scores above are read. (1) **The tolerance is the reference's, per family, not a single number.** The 0.5 cm⁻¹ that appears in this document is Pirali 2009's head-to-origin term for naphthalene's resolved fundamentals (decision 21), an upper bound for one molecule; the other scoring columns resolve ~1 cm⁻¹ (Maltseva 2016, C–H stretch only) and 5–17 cm⁻¹ (the free-electron-laser band lists above naphthalene). No family is therefore held to 0.5 cm⁻¹ anywhere but naphthalene, and a per-family licence is granted against the margin of the column that scores it. (2) **Where the couplings are needed is now measured on the spectrum's shape.** With the naphthalene stand-in's correction applied once with and once without its off-diagonal block, blurred to 5 and 13 cm⁻¹ (the FEL resolutions) and compared as normalised spectra: the C–H stretch window differs by 1.6 % / 1.4 % of the peak (the diagonal alone suffices there), the 6–9 µm window by 31.6 % / 18.5 % (one band keeps only 0.83 of its identity, positions move up to 21.4 cm⁻¹, strong-band intensities up to 28 %), the C–H out-of-plane window by 20.1 % / 9.5 %. So the couplings — recovered from gradients since 17–18 September (§1, §3.2 note, §5.3) — are required for every family that scores in the fingerprint and out-of-plane regions, and the C–H stretch family may be served diagonal-only, which the per-family design allows and the licence test will decide. Neither fact changes what is scored; both change what "within tolerance" means per family.

**Opponents (frozen baselines), named and versioned:**

| Line | What it is | Version / reference | Where it competes |
|---|---|---|---|
| A | PAHdb computed library: scaled-harmonic DFT | v4.00; Ricca et al. 2026 | every rung except R0 — the library as served (parsed 10 September: 10,749 species) has **no benzene entry**, so line A's column at R0 — where the comparison is printed and claims nothing (decision 28) — is empty by construction; C₃₈₄H₄₈ is present (uid 617) |
| B | anharmonic DFT quartic force fields: the **PAHdb Anharmonic library v1.00** (45 spectra, C₆H₆ to C₁₈H₁₂; B3LYP/N07D quartic force fields, VPT2 with symmetry-based resonance polyads in SPECTRO — the protocol of Mackie et al. 2015, 2016 and Esposito et al. 2024) and, for pyrene and coronene, Mulas et al. 2018 (B97-1) | v1.00 (1 July 2026); Mackie et al. 2015, 2016; Mulas et al. 2018 | every accuracy rung where a species is present (R0–R2 from the library, R2–R3 from Mulas) — as served (parsed 10 September): benzene, naphthalene, pyrene and tetracene on the ladder; chrysene, triphenylene and coronene absent |
| C | machine-learning molecular dynamics trained on DFT, temperature-dependent, to C₂₁₆ | Mai et al. 2025 (MNRAS 541, 3073) | where coverage overlaps; theory-vs-theory on reach rungs |
| D (reserved) | the 2026 machine-learning predictors of PAH spectra trained on DFT, from the group of line C: He, Mai & Wang 2026; Tang, He, Wang & Qiu 2026; Liu, Wang & Qiu 2026 (§3.1) | records Crossref-verified, abstracts read (13 September); enters the atlas once read in full | theory-vs-theory on the reach rungs — the nearest existing "large PAH in, spectrum out" products, against which pipeline A's network is measured |
| in-house | the **calibrated-harmonic baseline** (Module 04): a per-band ML correction to scaled-harmonic DFT, trained leave-molecule-out on laboratory residuals, after the ML-corrected-scaling approach of Bos et al. 2025 | built in this project, frozen before scoring | every accuracy rung |

**What the in-house baseline is, after Module 04 measured it (12–16 September).** On the matrix-scored library the calibrated correction does not beat the library as served: leave-one-molecule-out MAE 6.49 cm⁻¹ for the best model against 6.40 cm⁻¹ for the served scaled-harmonic values, R² ≤ 0.01. On that data it *is* line A rather than an independent opponent. It stays in the table as a column, labelled equal to line A within the noise, so that the scoreboard is complete and the reader can see that the Bos-type correction adds nothing there; it is not counted as a second, independent baseline beaten.

Line B is compared on **stick positions per band family**, nothing else: its authors' choices — as
stated in the two 2024 papers held and read (Esposito et al. 2024, J. Chem. Phys. and MNRAS
Letters): the 200 cm⁻¹ resonance window, the exclusion of modes below 300 cm⁻¹ from the VPT2, the
line profile — are not scored against (whether every one of the library's 45 spectra follows that
protocol, and what the 2015/2016 founding papers fixed, is asked in §13, items 11 and 15), and
where this pipeline's anharmonic step differs from that protocol the difference is separated from
the coupled-cluster correction by the Δ₂ = 0 null row below, which runs this pipeline's own
anharmonic step without the correction. The question put to line B is therefore not whether its
anharmonic treatment is right, but whether a measured coupled-cluster correction to the harmonic
constants adds accuracy on top of an anharmonic DFT treatment of the same kind.

**The supervisor's dual role, on record.** The supervisor is a co-author of the 2015 and 2016 papers
behind line B (Mackie et al.) and of the jet-cooled 3 µm spectra named as an R2 column (Maltseva et
al. 2016); the 2024 papers of line B's protocol (Esposito et al.) are the NASA Ames group's. The
protections are the ones already written — the frozen version, the pre-registered margins, the
Δ₂ = 0 null row, the leakage rules, the fail-closed reporting — and the supervisor's role on line B is
advisory on protocol facts (§13, items 11–15), never on margins or verdicts.

**Frozen comparisons and the pilot note.** Paired per-band absolute error on identical laboratory
bands; band lists, windows and margins frozen in the pilot note, which is written with seven
inputs in hand and **nothing else**:

1. the laboratory side with its measured band uncertainties — **printed for benzene (10 September,
   two NIST records) and for naphthalene's resolved fundamentals (11 September, Pirali 2009, u_band
   0.50–0.71 cm⁻¹)**; the PNNL naphthalene record and the R2/R3 columns owed;
2. the opponent side — exists (versions named above; line D pending its full read);
3. the DFT-only rehearsal with its noise-injected column — exists for benzene (5 September; the
   symmetry prior 10 September); for naphthalene the symmetrised stage A exists (15 September,
   §3.4) and the recovery from the hashed deck is owed;
4. the frozen-space probe M1 — exists (5–8 September; cc-pVDZ and cc-pVTZ scans with canonical
   truth lines; the xtight frozen arm, 27 points, and the DF-RHF/DF-MP2 QZ/5Z line on 12 September);
   probe B1's cc-pVDZ cells exist (15 September) and its cc-pVTZ cells decide (§3.5);
5. the canonical feasibility probe — exists (5 September);
6. a run/no-run check of which local-CC codes produce an analytic gradient at the anchor level
   at the equilibrium geometry, with memory — owed; the side project's own first cells (M2a, 14
   September) left g unmeasurable on the laptop at the coupled-cluster level (§5.3);
7. the naphthalene noise measurement, sized by **decision 35 (12 September)**: σ of the frozen
   object at the **tight** thresholds along **one mode** — the family with the largest σ at benzene,
   the C–C stretch — at **nine points**, ≈ 10 tight energies at 11.5 h, 4.8 laptop-days; the noise is
   the scatter about a smooth fit, no canonical line existing at naphthalene, with its fitted
   coefficients sealed. σ(tight) stands in for σ(xtight) with a label, justified at benzene, where σ
   did not change between the two settings (0.003–0.044 µE_h at both) while the bias did — and the
   bias is not a pilot input; σ(xtight) at R1 is re-measured on the first machine that can afford
   it (P13), and the pilot note's item 8 is re-read then if it differs. The run is queued after
   probe B1's cells (decision 38) and is cited in this copy as running, with its pre-registration
   (decision 40).

The first real coupled-cluster correction is computed after the note is committed, so no stopping
constant, probe cap, tolerance or margin can be shaped by a result; the raw displaced energies of
probe M1 are hash-committed for the same reason — the files are readable in the repository, the
SHA-256 sidecar proves they were not altered, and the author has undertaken not to open them before
the pilot note; "sealed" elsewhere in the plan means exactly this. What the hash-commitment protects
is the probing licence's off-diagonal responses and the R1 fit coefficients; the anchor licence's
noise and bias lines have their *form* fixed in the Ladder (σ_E ≤ 0.82·τ·q_s²; the bias line on
the composite energy), M1 supplies only the measured σ and bias read against them, and the pilot
note may not move the form — so quoting M1's summary statistics here shapes nothing. This proposal
quotes differences between methods and continuity diagnostics, never an absolute energy.

**Mandatory null tests.** The Δ=0 arm — DFT harmonic plus DFT anharmonic, no coupled-cluster
correction, scored by the same script on the same bands — must lose the comparison on every family
where "beat" is claimed, or the coupled-cluster claim for that family is void and reported as
explained by DFT-level anharmonicity. A noise-input run must fail the sanity gates. New in plan
05: a **shuffled-probe null** — the probe responses randomly permuted and fed to the same solver
must fail the probing licence — and a **discriminability clause** — the recovered correction must
beat the zero correction against the reference by a factor frozen in the pilot note. Both exist
because a regularised recovery can be confidently wrong.

**Licensing by measurement.** The anchor gate has four formulas, each with its numbers filled in
the pilot note: a noise line, a bias line against the canonical reference (judged on the composite
energy of §3.3), the basis-set line of decision 26, and a threshold-sensitivity line — the
frequency change between two of the program's truncation-threshold settings; the 6 September text
named tight against default, and with the anchor now at the thresholds one decade tighter than
tight (decision 20) the pair the line compares is the anchor's own setting, xtight [10⁻⁷, 10⁻⁸], against tight
[10⁻⁶, 10⁻⁷] one decade looser: the line is the difference of the two decks' curvatures per mode,
measured at benzene as +0.47 / +0.03 / +0.79 cm⁻¹ (tight) against +0.11 / −0.01 / +0.23 (xtight) — that, if breached, makes extrapolation
in the LNO truncation thresholds (the analogue, for this program, of the complete-PNO-space
extrapolation of Altun et al. 2021, who measured the local error on acenes growing linearly with
ring count and reduced it four- to five-fold by extrapolation) mandatory at double cost. The
probing licence and the locality test have their own tolerances, all bounded by the smallest beat
margin.

**Leakage control.** Laboratory values never enter training, validation, stopping, sampling or
pattern design; the calibrated-harmonic baseline is the single declared exception, evaluated
leave-molecule-out.

**Fail-closed reporting.** Every rung that does not run, every family that is undecidable, every
gate that breaches has a pre-written sentence, and losing is published with the same paired table
as winning.

**Dated note, 21 September (evaluation follow-up; the user: "Zet het principe in de fabriek").** The error budget gains a measured noise term with a fixed method: every derived quantity — a curvature from displaced energies, a coupling from a pattern, an anharmonic constant from displaced Hessians — is computed by two independent routes or checked against a symmetry partner, and the difference is the noise term of that quantity. The rule comes from a measurement of 20–21 September on benzene: the semi-diagonal quartic constants that a VPT2 package derived from psi4 Hessians differed between their two finite-difference routes by a median of 22 cm⁻¹ and up to 1,265 cm⁻¹ while the package reported no inconsistency (`probes/results_vpt2/qff_benzene_2026-09-21.md`); the cause is that psi4 has no analytic B3LYP Hessian, so those Hessians are themselves finite differences, and the package's default step is too small for that input. In the label factory this is the step "Consistentiecontrole" that feeds the error budget (architecture sheet 4); in the spectrum pipeline the anharmonic constants carry their route difference (sheet 8). Nothing in the coupled-cluster labels is affected: their curvatures come from energies, not from differentiated Hessians; the harmonic DFT Hessians of the corpus and the factory are one finite difference and accurate to ≈ 0.1 cm⁻¹. *Follow-up the same evening:* the diagnosis was tested as two pre-registered predictions (`probes/results_vpt2/PREREGISTRATION_2026-09-21_FD_noise_demonstration.md`): with the same psi4 Hessians at step 0.20 the route disagreement fell to a median of 2.3 cm⁻¹ (maximum 110.1), and with analytic pyscf Hessians at the same 61 geometries and step 0.05 to 0.1 cm⁻¹ (maximum 0.9 once the analysis basis inside exactly degenerate pairs is aligned with the displacements; 46.8 before that fix of the diagnostic); the benzene fundamentals became physical in both (ring breathing −17.3 and −28.0 cm⁻¹ against −216.9 before; the three test bands 850.6, 1004.4, 1324.1 cm⁻¹ with analytic Hessians against the gas-phase origins 847.1, 993.1, 1309.4 of Goodman, Ozkabak & Thakur 1991 (the Shimanouchi values 849, 992, 1310 were used until 22 September; the two papers arrived that morning)). Decision 46: the anharmonic step of the spectrum pipeline runs on analytic Hessians wherever psi4 has none (sheet 8: "VPT2 (pyVPT2 on pyscf Hessians)"); the step size follows from a third run at 0.10. *22 September:* the third run (step 0.10) reproduced the bands to 0.1 cm⁻¹, so the step is 0.10; and against Miani et al. 2000 (B3LYP/TZ2P, own anharmonic force field) our anharmonic shifts agree to a median of 4.3 cm⁻¹ over the 20 modes (`probes/results_vpt2/benzene_benchmark_2026-09-22.md`), so the residual +11 cm⁻¹ on the breathing mode is the 6-31G* harmonic, which the ΔH correction addresses. *22 September, evening (decision 48):* the R0 diagonal deck (44 coupled-cluster energies along the 20 benzene modes, `probes/results_m1/R0_TABLE_2026-09-28.md`) showed that a corrected harmonic frequency is the curvature at the cheap geometry *plus* a geometry term — the first-order shift towards the high-level minimum, predictable from one high-level gradient and the cheap cubic constants (validated on Hartree–Fock for six modes to about 10 %; C–H stretches against CCSD(T): MAE 52 → 14 cm⁻¹). The term is now a fixed step of the label factory and the spectrum pipeline (sheets 4 and 8); the table for the 28th shows all twenty modes with curvature, geometry term, sum and literature CCSD(T), two out-of-plane rows still open.

## 8. Feasibility and resources — what has been measured

Every cost in the plan is a measured slot reading "not run" until a script prints it. The
literature figures that motivated the design (a hundred-odd gradients for a full Hessian; 30 % of
columns on anthracene; a few micro-hartree of local-correlation noise) are recorded as motivation
and are forbidden in any budget sentence. The following were printed between 5 and 16 September on
the student's laptop (an 8-core Ryzen 7 260, 31 GB, no CUDA GPU; the anchor code runs in a Linux
subsystem given 22 GB until 12 September and **25 GB** since, Windows keeping about 6 GB; the
machine is dedicated to the project and available around the clock).

**What "fits the laptop" means, once for the whole document.** A computation fits the laptop when
(i) its peak memory stays under the Linux subsystem's ceiling — 25 GB since 12 September — and
(ii) its wall-clock is run as weekly batches of at most **168 hours**, each ending in a dated
checkpoint decision; the arithmetic rule of this section classifies a batch as cluster work when
its weekly-batch count is such that it displaces the queue rather than joining it. By these tests:
the anchor's 61-energy canonical bias line (13–21 h) fits; the R0 pilot (448 energies × 76 min ≈
567 h, 3.4 weekly batches, 24 days) fits and runs first; the R1 deck at the anchor's basis (67
weekly batches as the H deck, 108 as ± pairs, §3.2) is cluster work; pyrene at cc-pVTZ fails the
memory test outright; and the full canonical benzene Hessian by energies (1,801 energies, ≈ 378 h,
2.3 weekly batches) would pass both tests but is not run. The reason is what the pilot has to
license: the frozen-space local method is the only arm that reaches naphthalene and above, so its
probing licence has to be earned on its own energies, with the canonical bias line of §3.3 as the
truth against which they are read. A canonical Hessian at benzene would test the truth, not the
instrument, and licenses nothing above the molecule it is computed on. The probing licence was written
to test the recovery without it — the 6 September text called it "cluster work", and the change log
records the re-reading.

- **The DFT-only rehearsal (benzene; B3LYP vs BHHLYP, 6-31G*).** The deck: 30 single-mode
  patterns, 184 two-mode patterns and 120 multi-mode patterns, each run as a ± pair (two
  energies), i.e. 334 pairs or 668 energies, of which 61 pairs (122 energies) were held out of
  every fit; plus the 30 single-mode patterns at a second amplitude (60 energies) and the
  reference geometry — **729 energies per functional**, 2 h 30 min. Of the 546 training energies
  the recovery reached its off-diagonal threshold at 448, of which the first 60 (the single-mode
  block) fix the diagonal: **K = 448 energies, K_off = 388 energies for 435 off-diagonal
  unknowns**. (K counts the energies consumed until the rule stopped; the 122 held-out energies
  are computed as well and are reported beside K as the hold-out fraction, never inside it.)
  Energy route: per-family errors of the full recovery ≤ 0.43 cm⁻¹ against 7 cm⁻¹ for the
  diagonal-only recovery; gradient route: the same from 60 gradients. Under the symmetry prior
  (rerun 10 September, same responses) the threshold was reached at 210 off-diagonal energies,
  K = 60 + 210 = 270, on a deck built for the banded rule (§3.2). **The R0 pilot is nevertheless
  priced at 448 energies** — the measured K before the prior — as the conservative figure; the R0
  deck is built for the prior and is expected to stop earlier, and the pilot's printed K replaces
  the price.
- **The naphthalene DFT dry run (stage A, 15 September; `probes/results_dryrun/naphthalene_sym/`).**
  The two functionals' Hessians on a geometry symmetrised to D₂h and every mode projected onto its
  irreducible representation; the factory geometry (`symmetry c1`, symmetric only to 4–7 × 10⁻⁵
  bohr) carried odd parts of up to +30.9 µE_h at unit displacement along nominally
  non-totally-symmetric modes through a 10⁻⁴ admixture, the symmetrised modes ≤ 0.001 µE_h on the
  three modes tested (12 / 22 / 31) in both functionals — decision 37's prerequisite met (§3.4).
  The recovery from the hashed deck (stage B) is owed.
- **Probe M1** (§3.3): two threshold settings × 27 geometries × three arms, plus 27 canonical
  CCSD(T) points; 5–10 minutes per geometry at cc-pVDZ. The cc-pVTZ scan takes about two hours per
  geometry and 2.5 days in all; the xtight frozen arm alone 27 points at about 75 minutes each
  (12 September), and the DF-RHF/DF-MP2 cc-pVQZ and DF-RHF cc-pV5Z line 19 minutes for 54 points.
- **Probe B1** (§3.5): the naphthalene frozen arm at tight thresholds along three modes in cc-pVDZ
  — fifteen geometries, 14 September 17:51 to 15 September 13:43, **69 minutes per energy at 1.7 GB,
  a factor 9.9–10.0 below the cc-pVTZ tight energy** — and the same cells in cc-pVTZ, launched 15
  September evening, ≈ 6 laptop-days.
- **The canonical reference.** Canonical CCSD(T) energy of benzene: 27 s at cc-pVDZ, **755 s and
  7.3 GB at cc-pVTZ** on the idle laptop at the equilibrium geometry (850–1,270 s at the displaced
  geometries of the scan, with the laptop in use). Local LNO-CCSD(T) energy at cc-pVTZ: 2,087 s for
  benzene (locality pays only at larger molecules) and **41,375 s — 11.5 hours — for naphthalene at
  tight thresholds, 24 fragments, peak memory 19.8 GB against the then 22 GB ceiling (11
  September)**, and **138,305 s — 38.4 hours of fragment solves — at the anchor thresholds
  [10⁻⁷, 10⁻⁸], peak 15.4 GB with the out-of-core path, finished 14 September (F = 3.34)**; pyrene
  will not fit this laptop's memory at cc-pVTZ. The anchor's bias line — 61 canonical energies
  along benzene's 30 modes — is therefore 13–21 hours and **fits the laptop**; the full canonical
  reference Hessian by energies (1 + 2·30 + 4·435 = 1,801 energies, about 378 hours) is not run
  here (above), and the gradient branch does not fit: a canonical CCSD(T) gradient of benzene costs
  1,399 s and 13.9 GB at cc-pVDZ — about fifty energies — and at cc-pVTZ it did not complete within
  the 22 GB ceiling (its memory scales roughly with the fourth power of the basis size,
  (264/114)⁴ ≈ 30, i.e. hundreds of GB). **The canonical reference at benzene therefore consists
  of** the 61-energy diagonal line (the anchor's bias line) and the canonical two-mode points of
  decision 16 for the off-diagonal bias; the probing licence's full-matrix comparison is against
  the directly computed local-CC reference with the same frozen spaces.
- **The cation energy (M4, 15 September; `probes/results_m4/`).** Benzene neutral LNO-CCSD(T) at
  cc-pVDZ tight 164 s; benzene⁺ with the installed unrestricted code 5,096 s (UCCSD 1,264 s, the
  NumPy (T) kernel 3,832 s), 4.2 GB — **c = 31.0**, the number behind decision 41 (§5.2).
- **The Module-05 corpus.** A B3LYP Hessian of a QM9-size molecule takes 3–7 minutes here, so the
  conjugated QM9 subset (6,055 molecules, B3LYP side only) is about three weeks of laptop time; the
  own aromatic layers prepared on 12 September (45 + 868 + 4,353 candidates, both functionals, up
  to 34 atoms; naphthalene 13 minutes and pyrene 54 minutes per Hessian here) were priced by the
  five-molecule timing test of 14 September at 177 laptop-days for layers A + A′ + B (P27 §7, citing
  the Timing Note) — the factory runs start-and-stop and never beside an anchor job, and on one
  machine it displaces the anchor day for day, which is the strongest single argument for a second
  machine or for running it elsewhere (§12, Module 05 row; `modules/05_support_predictor/corpus/`).

Still owed before the pilot note (§7's list): the naphthalene rehearsal's recovery from the hashed
deck, which also admits or refuses the symmetry prior at 48 modes; the scoreboard re-read with its
measured band uncertainties; the gradient run/no-run check; and the naphthalene noise measurement
of decision 35 (running, §7). After the note: the benzene probe batch and its references,
including canonical two-mode points from which the frozen spaces' off-diagonal bias is read
(decision 16); naphthalene; the three-ring rung, whose anthracene deck is also the direct-coupling
probe the 6 September text carried as a dated bonus (the plan's own reason: anthracene is the
smallest acene where the plan expects DFT's delocalisation error to begin to show in the C–C
families; a reason, not a citation); then classification of the pyrene- and coronene-size batches
as laptop or cluster work by the arithmetic rule above. The domain review priced plan 05's own
probes as cheaper than plan 04's first batch of surface-learning points, and the measurements so
far agree.

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
re-read those closures (the re-checks of the earlier closures held with one exception, re-patched
and re-read in the fourth round; the counts are in the review files) and changed the design in
seven places, all in the text: paired displacements so that the coupled-cluster force at the DFT
geometry cancels; frozen spaces transported by projection rather than re-localised; only benzene
scored unconditionally until the room-temperature naphthalene source was found; noise injected
per energy in the rehearsal; the shared reference energy's offset identified from a second
displacement amplitude (§3.4); the first-order geometry term on every scored band (§5.1); and the
PNNL naphthalene source itself.

The review loop was **closed on 4 September** after a consistency check of the last revision (19
cross-references, all mechanical). Since then the plan's text changes only by dated notes that
name a measurement or a decision; the decisions of 5–16 September (§10, items 8–42) are such notes.
Items 8–16 and 19 were made on the DFT-only rehearsal, the frozen-space probe and the timings —
before any coupled-cluster response of the real correction exists, so none of the rules the
evaluation depends on was shaped by a result it will judge; items 17 and 18 are tooling and scope
choices; items 20–34 are readings of measurements (20, 26, 33), laboratory-source rules (21, 24,
25, 29, 30) and pre-registrations (27, 28, 31, 32, 34); items 35–42 (12–16 September) are the sizing
of the noise run (35), the adoption of the two pipelines (36), the single-sided K rule (37), the
anchor's thresholds and the machine order (38), the slow ladder with ions (39), the proposal date
(40), the (T) port (41) and the cold reads of 16 September with this reading copy (42) — all made
before any coupled-cluster response of the real correction exists. The three cold reads of this
document (6, 8 and 16 September) are described after §1. The remaining risk is retired by
measurements, not by further reading; §8 lists the first of them.

## 10. Decisions the student made (items 1–42; all closed unless marked open; a supervisor's objection would reopen any of them)

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
   aromatic-heavy subset of the public Hessian QM9 set (Williams et al. 2025) with recomputed
   B3LYP Hessians; success is the measured saving and the per-rung licence, not accuracy.
   *Addition, 12 September:* Hessian QM9 holds 66 all-carbon aromatics and 6,055 conjugated rings
   (measured), so the corpus is Hessian QM9 **plus an own four-layer aromatic corpus** (45 / 868 /
   4,353 / 6,055 candidates, §8; the number actually computed is fixed by a dated note after the
   five-molecule timing test).
5. The re-worded promised set: the harmonic-only correction; the energy route as the guaranteed
   route but not as a limit, the gradient route built in the side project.
6. The development machine: the student's current laptop; a replacement only if a probe shows it
   necessary.
7. No earlier coursework overlaps with this project. An unsubmitted draft that used the QM9 set
   has been renamed so that the Module-05 corpus cannot be mistaken for re-used work.

**5–8 September 2026, after the first measurements.**
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
15. The energy the object reports is the composite local-CCSD(T) + [MP2(full) − MP2(local)] (extended by
    the two basis terms of item 33).
16. The cc-pVTZ frozen-space scan with its canonical truth line ran (6–8 September; result in §3.3);
    the benzene probe batch includes canonical two-mode points for the off-diagonal bias.
17. Module 07's campaign officer runs on LangGraph (admissible through the programme's
    LangChain/LangGraph elective) with the Anthropic API as model endpoint, model id logged.
18. Intensities are scored on benzene and naphthalene as a second quantity; positions remain the
    primary claim; no coupled-cluster intensity correction is promised; the dipole probe M1-μ
    decides whether one can be proposed; widths are drawn, not predicted.
19. Coupling blocks made only of infrared-inactive modes are tested per rung and dropped only
    where the scored positions do not move.

**8–10 September 2026, after the anchor-basis scan, the laboratory readings and the second cold read.**

20. The anchor-basis curvature bias of the frozen arm (§3.3) is **measured against a larger frozen
    space before anything else is decided**: the same benzene scan at thresholds one decade tighter,
    frozen arm only, against the existing cc-pVTZ truth line (started 8 September; died with its
    session after 5 of 27 points; resumed 11 September; **finished 12 September: composite bias
    +0.11 / −0.01 / +0.23 cm⁻¹ against +0.47 / +0.03 / +0.79 at tight, smoothness unchanged — the
    anchor runs at the tighter thresholds, cost factor ≈ 2 at benzene and F = 3.34 at naphthalene,
    measured 14 September**).
21. A room-temperature source whose fundamental is resolved from its hot bands (Pirali et al. 2009,
    sixteen naphthalene bands at 0.005 cm⁻¹) is scored with no temperature shift and a 0.5 cm⁻¹
    head-to-origin term; other room-temperature sources keep the floor.
22. The benzene rehearsal is rerun under the symmetry prior (done 10 September; §3.2).
23. The symmetry-forbidden couplings of the frozen-space object are measured as a null (a few pairs
    fitted free) rather than assumed zero (§3.2).
24. The jet-cooled coronene bands are the primary cold column with the laser bandwidth as their
    uncertainty; the hot-extrapolated position is a second, labelled column; a family is inconclusive
    only when the two disagree on the verdict (§5.2).
25. The R2 C–H stretch family on the jet-cooled 3 µm column is shown, not promised, until a scoring
    rule for its resonance polyads is agreed (§5.2, §13 item 8).
26. A **basis-set line** enters the anchor licence and the per-band budget: the measured cc-pVDZ →
    cc-pVTZ change of the canonical curvature (§3.3), the literature distance of CCSD(T)/cc-pVTZ from
    the basis-set limit for benzene once read, and a canonical cc-pVQZ diagonal line in the cluster
    request; the expected-effect line bounds the family mean at the anchor's level, not any single
    mode (§5.1). *Input (ii) printed 12 September:* the cheap TZ → QZ/5Z line shows the SCF part
    nearly converged (2–5 cm⁻¹) and the MP2 correlation part still moving by 1–8 cm⁻¹ — see P18 in
    §3.3.
27. **The per-family transferability test Q9** (parked 8 September, unparked 10 September): the
    route from the accuracy rungs to the large PAHs is a pre-registered leave-one-molecule-out test
    of the diagonal correction per band family across benzene–coronene plus anthracene, with the
    losing condition written first (§6; research note of 8 September); it runs after R3 and before
    any R6 probe; no coupled-cluster energies beyond the ladder's own.
28. **The criterion per rung** (§1, §5.2, §7): benzene is an agreement rung, naphthalene agreement
    plus the per-family question whether the correction adds accuracy, "beat" from there upward.
29. **The temperature term on the room-temperature licence rungs** (10 September, after the first
    benzene scoreboard print): the 0 → 296 K shift per scored band is computed from the pipeline's
    own DFT anharmonic constants and applied as a correction carrying ±30 % of itself, in place of a
    floor of 2.55 cm⁻¹ that would otherwise be the whole of the laboratory uncertainty on the
    0.125 cm⁻¹ benzene record; pre-registered, printed before any coupled-cluster number exists.
30. **Line A is the PAHdb library as served** (10 September): its stored v3.00 scale factors; the
    v4.00 paper's refit is printed beside it as a labelled column and claims nothing (§7).
31. **The calibration check of the error budget, Q10** (10 September): coverage of the laboratory
    bands inside k·u_total, per rung, family and overall, thresholds fixed in the pilot note; a short
    budget is reported as incomplete, never widened (§6).
32. **The network as named stand-out work, outside the sequence** (12 September; **superseded 14
    September by item 36**, which makes the network the reach product): a model trained on the
    pipeline's own Δ₂ blocks and certified bands, gated by the measured range at the accuracy rungs
    and the Q10 coverage table, with its losing condition pre-written — the two gates survive as
    the licence's gates (§6); the sequence still ends at Module 09.
33. **The anchor as a composite with basis corrections** (12 September, P18): the anchor energy per
    point is the local-CC energy at the tighter thresholds plus the existing [MP2(full) − MP2(LNO)]
    term plus [MP2/QZ − MP2/TZ] + [SCF/5Z − SCF/TZ], every term a difference of computed energies at
    one geometry, no fitted parameter, under 1 % of an LNO point in cost; named by the basis line of
    the same day (§3.3); the licence comparison is unaffected; the CCSD(T)−MP2 remainder's basis
    change stays the open term of decision 26 (Ladder §3 words added).
34. **Substitution probing pre-registered as a second measurement layer** (12 September, P24, from the idea
    plan 06): the R0 pilot gains one measured Hessian–vector product and one pre-registered comparison of a
    six-product reconstruction of Δ₂ (Powell & Toint's triangular substitution, verified exact and noise-tolerant
    on the dry-run tensor) against the deck's Δ₂; winning condition: agreement within the R0 noise budget *and*
    fewer energies than the deck; losing condition: either fails. Priced honestly: with energies only a product
    costs ≈ 4M energies, so the layer pays only if the side project delivers gradients; nothing else in the plan
    changes until the comparison is won. (On naphthalene's stand-in the symmetry prior's nine products recover
    the 141-pair block exactly, X16, 16 September; g is unmeasurable on the laptop at the coupled-cluster level,
    so the layer waits for a larger machine, §5.3.)

**12–16 September 2026, after the naphthalene timings, the basis probe and the third cold read.**

35. **The R1 noise measurement sized** (12 September): a 27-point xtight scan at naphthalene would
    be ≈ 50 laptop-days (≈ 2 days per energy), so pilot prerequisite (f) is met by σ at the **tight**
    thresholds, **nine points, one mode** (the family with the largest σ at benzene, the C–C
    stretch), ≈ 10 energies at 11.5 h ≈ 4.8 laptop-days; σ(tight) stands in for σ(xtight) with a
    label, justified at benzene, where σ was 0.003–0.044 µE_h at both settings while the bias
    changed; σ(xtight) at R1 is re-measured on the first machine that can afford it (P13) and the
    pilot note's item 8 re-read then (§7 item 7).
36. **P26 adopted with one change** (14 September): the network is the reach product and pipeline B
    the label factory; thin decks above naphthalene; every sentence "no machine can pay a full deck
    above naphthalene" qualified "at the anchor's basis", with probe B1 (then called "probe M3") as
    the measurement that could return full decks to the ladder; the Snellius request sized both
    ways (§1, §3.5, §6, §12, §13 item 5).
37. **I14 adopted as a dated amendment of the K rule** (14 September; confirmed 15 September): one
    energy per irrep-pure non-totally-symmetric pattern, a pair per totally symmetric pattern and
    per noise witness; measured admissible at tight and xtight on benzene's b₂u mode. Hard
    prerequisite added 15 September: the geometry symmetrised to ≤ 10⁻⁸ bohr and every pattern
    projected onto its irrep before any single-sided energy — confirmed the same day by the
    naphthalene dry run (§3.4, §8). The naphthalene deck is 291 energies (§3.2).
38. **The anchor's thresholds and the machine order after M2a** (14 September): (a) the anchor stays
    at xtight (bias +0.11 / −0.01 / +0.23 cm⁻¹ at benzene; 38 h per naphthalene energy at cc-pVTZ,
    ≈ 3.3 h estimated at cc-pVDZ if probe B1 wins); probe B1 itself runs at tight in both bases, as
    pre-registered. (b) The σ-run of item 35 did not start that night. (c) Order after M2a: probe
    B1's cc-pVDZ cells (≈ 13 laptop-hours), then its cc-pVTZ cells (≈ 6 laptop-days), then the σ-run
    (4.8 laptop-days); B1's own ± pairs along non-totally-symmetric modes give a first σ estimate on
    the way. The naphthalene DFT dry run, the benzene VPT2 run (≈ 3 h) and the parked app update
    take the gap between B1's cells; no psi4 beside a WSL anchor job.
39. **The ladder is built slowly, ring by ring, with ions** (14 September evening): the three-ring
    rung (anthracene and phenanthrene, the isomer test at equal size) between naphthalene and the
    pyrene class, full decks in cc-pVDZ if probe B1 licenses the basis and thin decks otherwise; the
    four-ring rung (pyrene, tetracene) full if B1 wins, thin otherwise; a five-ring rung (perylene
    or pentacene) only after it and only if the per-family transfer 3 → 4 held; cations at the two
    smallest rungs (benzene⁺, naphthalene⁺) by unrestricted local CC after a smoke test and one timed
    energy; the go/no-go per band family read after the three-ring rung; the peri series as the main
    axis, the acenes as the stress branch with the anchor's diagnostics printed; the reach product
    and the shape objective unchanged (§5.2).
40. **The proposal goes to the supervisor on 26 September 2026** (14 September evening; *moved to 28 September 2026 by decision 44 on 18 September, when the cc-pVTZ cells' end date became 27 September*): by then
    measured — probe B1's cc-pVDZ cells (15 September), its cc-pVTZ cells (≈ 21 September, the
    decisive number for the label budget and the Snellius paragraph), the naphthalene dry run with
    the P25 and I14 licences (15–16 September), the benzene VPT2 calibration (15 September), one
    timed benzene⁺ energy (15 September), the corpus price (done); running on the day: the σ-run of
    item 35, cited as running with its pre-registration. The rungs above naphthalene and everything
    on the desktop are written as the plan, not as results; the pilot note stays a later document
    (§12).
41. **The unrestricted (T) port** (15 September evening): the measured cation price (c = 31.0 at
    benzene, cc-pVDZ tight; the NumPy (T) kernel 75 % of it) is answered with own software — an
    unrestricted compiled (T) kernel for the LNO fragment energies, PySCF's compiled restricted
    kernel as the model — with acceptance tests fixed now: the benzene⁺ energy equal to the NumPy
    kernel's to 10⁻⁸ E_h on the same fragments; time ≤ 1.5 × the restricted compiled (T) for the
    neutral; the shipped CH₃ comparison against canonical UCCSD(T) unchanged. Expected c ≈ 8–9;
    Software Changes Ledger row 13; desk work of one to two weeks in the private part of the
    repository, starting after the 26 September proposal work is safe, never displacing probe B1's
    cells; nothing sent upstream without the student's word (§5.2).
42. **The cold reads of 16 September and what is done with them** (16 September morning): (1) this
    consolidated reading copy for 26 September — the dated revisions worked into one voice with a
    change log at the end; the 6 September original stays as the record; (2) the misattribution of
    Esposito et al. 2024 to the supervisor's group corrected at once by dated note in the original;
    (3) §13 item 5 split into three numbered asks with a one-line derivation of the SBU figure on
    the decision-37 deck; (4) the cations enter explicitly as rung R1⁺ with the (T) port as its
    condition, in place of the orphan "and charge state"; (5) plan 06's annex gets an opening
    paragraph with its four outcomes and one question to the supervisor; (6) the remaining stumbles
    of both reports worked into the copy and the annex without further questions. Dispositions are
    written under each report.

## 11. Risks

1. **Frozen-space energies are not smooth enough for energy-only probing.** Measured at benzene in
   cc-pVDZ: they are, by a factor of 30 to 1,000 (§3.3). Remaining exposure: the anchor basis —
   measured 8 September: smooth (0.002–0.021 µE_h) with a frequency bias of +0.47 / +0.03 / +0.79
   cm⁻¹ (out-of-plane, ring, C–C stretch) at tight thresholds, **+0.11 / −0.01 / +0.23 cm⁻¹ at the
   thresholds one decade tighter (12 September; decision 20 closed: the anchor runs there, at about
   twice the per-point cost at benzene and 3.34 times at naphthalene)** — and larger molecules (the
   naphthalene noise measurement of decision 35, running). Response where a measurement fails: no
   accuracy claim for the couplings at that size; the gradient route where the side project has
   delivered it.
2. **The correction is not near-diagonal in the DFT mode basis on aromatic ring modes.** Measured
   at benzene on the DFT surrogate: it is not, and the couplings follow symmetry, not frequency.
   Response: the symmetry prior; the rehearsal on a functional pair that brackets exact exchange;
   the diagonal-only and full recoveries printed side by side at benzene and naphthalene.
3. **The correction is not local, or is local for C–H modes and not for the delocalised C–C
   families the astronomy needs.** Response: locality measured on directly computed blocks per
   family, the three-ring rung, and a pre-registered per-family losing condition that withdraws
   the reach story for exactly those families. (On the naphthalene stand-in, zeroing Δ₂'s atom-pair
   blocks beyond bond-graph distance 4 still moves a band by 10.5 cm⁻¹, beyond 6 by 0.4 — X16, §5.3.)
4. **The coupled-cluster harmonic correction does not beat calibrated harmonics.** The opponents'
   fitted scale factors absorb the signed mean of the harmonic difference; the mean absolute
   difference that Esposito et al. 2024 (§14; the NASA Ames group) measured for benzene —
   B3LYP/N07D against CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies, 5.45 cm⁻¹ (their Table S1;
   benzene only, read in full 6 September) — is a mean over the modes, not a per-mode bound (§5.1);
   what remains to buy is the per-family scatter. Response: the expected-effect line is written into
   the pilot note before any result, and losing is publishable.
5. **Laboratory decidability.** The per-family rule pre-declares undecidable families
   inconclusive. The pyrene-size rung's C–C families are in that class on every source the search
   found; the cold jet-cooled lists for tetracene and coronene are scored as labelled columns.
   Only a new gas-phase source or measurement changes this (§13, item 3).
6. **Off-diagonal probing is expensive without a prior.** Measured: 0.9 energies per unknown at
   benzene without a prior (388 for 435); under the symmetry prior 210 for 57 allowed pairs on a
   deck not built for it, with 2.0 per pair the cap on a deck that is (§3.2); a DFT-only rule for
   thinning the couplings further (P25) lost its licence test at naphthalene (§3.5). Response: the
   symmetry prior (decision 11) with its per-rung free-element count printed beside the probe
   count; the single-sided patterns of decision 37; the learned prior of Module 05 measured against
   the same count; the 168-hour rule classifies any rung the prior does not rescue as cluster work
   rather than quietly overrunning.
7. **The side project becomes a time sink** — the failure mode that ended plan 01, which spent
   two-thirds of its hours on infrastructure. Response: the terms of §5.3 (separate budget line,
   twelve-week kill criterion, four-weekly review); the (T) port of decision 41 is bounded the same
   way (one to two weeks of desk work, acceptance tests fixed first, Software Changes Ledger row).
8. **Operational.** The first week produced two lost runs (a memory ceiling set too high; a
   machine switched off with a job running). Both are now rules in the budget document: a memory
   ceiling with headroom for the host, one anchor job at a time, every long run announced with
   its end time and written out point by point so an interruption costs one point.
9. **Probe B1 loses.** Then the naphthalene deck stays at cc-pVTZ — 291 energies at 38.4 h, cluster
   work by the rule of §8 — full decks above naphthalene stay out of reach on every route, the
   size question of §4 is not attempted, and the rungs above naphthalene carry thin decks only.
   Response: written in advance (§3.5, §4, §5.3, §12); the cluster request is sized for the
   cc-pVTZ deck (§13, item 5a).
10. **The cation price.** Measured 15 September: c = 31.0 with the installed unrestricted code,
    which fits no cation deck on the laptop (§5.2). Response: the (T) port of decision 41 with its
    acceptance tests; if it fails, R1⁺ falls back to its diagonal deck at tight on the desktop or
    lapses with a printed sentence.

## 12. Fit to the capstone programme

Each module of the programme is mapped onto a load-bearing pipeline artifact: the opponent atlas
(Module 02); the laboratory scoreboard with the measured band-centre uncertainties and, for benzene
and naphthalene, the calibrated intensities (Module 03); the calibrated-harmonic baseline (Module
04); the campaign officer that enforces the budget rules and the two permitted cost sentences
(Module 07; see the terms after §1); and the assembled pipeline with its scored ladder and cost
records (Module 08). Module 01 (foundations) maps to no pipeline artifact. Two modules — the
deep-learning support predictor (Module 05) and the generative pattern proposer (Module 06; it
proposes decks on DFT-only corpora *before* hashing — a proposed deck is hashed like any other and
never reordered after an energy exists) — are efficiency experiments on the off-diagonal probe
count, run on DFT-only corpora at zero coupled-cluster cost and measured against the symmetry
prior's free-element count; the deep-learning model is measured on the accuracy rungs and, if it
earns its licence there, becomes load-bearing on the reach rungs as the network of pipeline A —
the mapping says exactly that rather than pretending otherwise. Module deadlines are administrative
facts; a module may ship a fail-closed state to meet its date, and the science continues past it.

**Calendar (set 10 September 2026 from the first week's measured pace; re-read on 14–16 September
against decisions 38–41; each date means "delivered in full or in its fail-closed state").** The
pace-setting quantities are the laptop's serial compute (one anchor job at a time; a benzene
cc-pVTZ scan is two days, one naphthalene LNO-CCSD(T) energy **11.5 hours at tight thresholds (11
September) and 38.4 hours at the anchor thresholds (14 September), 15–20 GB peak memory; 69
minutes at cc-pVDZ tight (15 September)**), the student's evenings and weekends for decisions, and
the supervisor's reading time around this proposal and around the cluster request (one to two
weeks each assumed). The first week also showed that each measurement brought one correction with
it (semicanonicalisation, the frozen-core count in the timing probe, the factor 2, the basis set;
in the second week the geometry symmetrisation and the cation kernel); one round back per module
is budgeted, not hoped away.

| Milestone / module | Content | Date | What sets the pace |
|---|---|---|---|
| Module 02 — opponent atlas | PAHdb v4.00 and Anharmonic v1.00, Mai 2025, the Bos-type baseline, read in and version-frozen — **first version complete 10 September** (parser, tables, notebook, report; the student's own pass before submission); line D added once read in full | 25 Sep 2026 | data engineering, no compute |
| Proposal to the supervisor | this reading copy with its cover note, after probe B1's cc-pVTZ cells (verdict ≈ 27 September, measured 18 September at 16.6 h per energy; the 14 September calendar had ≈ 21–22 September) and the third cold read (decision 40; moved by decision 44; the 10 September calendar had Monday 14 September) | 28 Sep 2026 | the student's work |
| Module 03 — scoreboard and u_band | probe 2a, the laboratory columns, decidability per family — **scaffolded in the Udacity rubric form on 11 September** (`modules/03_lab_scoreboard/`: a pre-registered matrix–gas test committed before the join, 63 pairs of naphthalene, anthracene, pyrene and chrysene against the WebBook GC-IRD records; six families reject a zero offset, median +3.3 to +5.9 cm⁻¹ matrix above hot gas; the u_band columns on these records, the PNNL and cold columns and the naphthalene⁺ columns still owed) | 2 Oct 2026 | the student's work; the supervisor's answers to §13 items 7–10 |
| Pilot-note inputs | the naphthalene rehearsal's recovery (stage A done 15 September), the R0 pilot, the canonical two-mode points, and the naphthalene noise run of decision 35 (≈ 10 tight energies, 4.8 laptop-days, queued after probe B1's cells — decision 38 — and running on 26 September) | 23 Oct 2026 | laptop, one anchor job at a time: the R0 pilot (benzene, 448 energies at ≈ 76 min per xtight energy, 24 days), the canonical two-mode points (14–21 min each), the σ-run |
| Pilot note | every frozen number, band lists, margins; the threshold-sensitivity pair (§7) | 30 Oct 2026 | the student's work after the measurements |
| Module 04 — calibrated-harmonic baseline | ML correction to scale factors, leave-molecule-out — **scaffolded in the rubric form on 12 September** (`modules/04_calibrated_harmonic/`: recipe committed before training; 2,477 matrix↔computed pairs of 83 molecules; leave-one-molecule-out MAE 6.49 cm⁻¹ for the library as served against 6.40 for the best model, R² ≤ 0.01 — on this table the calibrated baseline *is* line A; the Zenodo release of the table and the pilot note's adoption of the recipe still owed) | 30 Oct 2026 | in parallel with the compute |
| Module 05 — Δ₂-support predictor | the DFT-vs-DFT Hessian corpus and the network — **scaffolded 12 September** (`modules/05_support_predictor/`: recipe, the Transformer in PyTorch, smoke test on the benzene dry-run tensor). **Hessian QM9 downloaded and verified the same day** (41,645 molecules, ωB97X/6-31G* numerical Hessians; paper read for units and conventions). **Measured: it holds only 66 molecules with an all-carbon aromatic six-ring and 6,055 with a planar conjugated five- or six-ring** — the "aromatic-heavy QM9 subset" of the mapping is really a conjugated/heteroaromatic subset. **Prepared in response: a resumable corpus factory** (`modules/05_support_predictor/corpus/`) with four layers — 45 ladder-adjacent aromatics of 12–30 atoms as a size bridge, 868 mono-substituted three- and four-ring cores that turn the bridge into a distribution, 4,353 substituted aromatic and heteroaromatic cores as the class, and the 6,055 conjugated QM9 molecules — computed with the plan's two functionals at 6-31G*, start-and-stop, in a fixed order so every stop leaves a reproducible subset. The five-molecule timing test of 14 September priced layers A + A′ + B at 177 laptop-days (§8); the number actually computed is fixed by a dated note; the corpus is published with a DOI before the module starts (reading 1). No result | 20 Nov 2026 | the corpus costs DFT compute and competes with the anchor day for day on one machine (measured per molecule: a QM9-size molecule 3–7 min per Hessian, naphthalene 13 min, pyrene 54 min) |
| Cluster request | sponsored by the supervisor, sized by the measured anchor energy on the 291-energy deck (§13, item 5a: ≈ 195,000–290,000 SBU, estimate); its first job one timed energy on the node; re-sized before submission if probe B1 licenses cc-pVDZ | 4 Dec 2026 | the supervisor and the request's lead time; the hinge of the two scenarios below |
| R1 probe batch and scoring | the first real coupled-cluster correction, naphthalene: the 291-energy H deck | 11 Dec 2026 is the start on the machine P13 chooses; on the cluster route the batch itself follows the allocation's lead time; on the cc-pVDZ route P27 puts its end at mid-December on the laptop alone or late November with the desktop (proposed, open) | **not the laptop at cc-pVTZ (466 days for the H deck at 38.4 h; §3.2): four Snellius nodes in 15–25 days or the desktop of the hardware note in 123–203 days, both estimates from the 474-energy figures of the duration table scaled by 291/474; the desktop is a priced configuration, not a purchase, and would be the student's own; at cc-pVDZ, if probe B1 wins, the laptop in ≈ 47 days (P27, open)** — P13 open |
| R0⁺ / R1⁺ | the (T) port (decision 41: one to two weeks of desk work after 26 September, acceptance tests first), then naphthalene⁺'s H deck after R1 | after R1; the date follows the port's tests and P13 | c-dependent: with the port ≈ 45 laptop-days for the diagonal H deck at tight and ≈ 115 for the full H deck (desktop 30–50), P27 §5 with decision 41 (estimates until the port is timed) |
| Module 06 — generative pattern proposer | the efficiency experiment on K_off | 18 Dec 2026 | the student's work |
| Q9 pre-registration — families per adjacency class, τ_F, the two rules, the LOMO protocol (decision 27) | written before any correction above naphthalene exists | 15 Jan 2027 | no compute |
| Module 07 — campaign officer | LangGraph, the Anthropic API, the cost record | 15 Jan 2027 | the student's work |
| Three-ring rung and the go/no-go | anthracene and phenanthrene, diagonal-first decks; the per-family go/no-go read from both diagonal blocks (decision 39) | by P27's calendar February–April 2027 on the laptop alone, December 2026–January 2027 with the desktop (proposed, open); in both cases before Module 08 | the machine of P13; 334 energies at 2.5–5 h each (estimate) |
| R2 and R3 | pyrene class and coronene, thin decks (full only if probe B1 licensed them); then Q9 evaluated per family and the Q10 coverage table printed for R0–R3 | after the three-ring go/no-go: February–April 2027 on the laptop alone, December 2026–January 2027 with a desktop (P27, open) | **cluster access**; without it these rungs lapse |
| Module 08 — the pipeline assembled and scored | R0–R1 and R1⁺, the thin decks, the network licensed or refused per family, fragment-probed R6 where licensed | 16 Apr 2027 | everything above |
| Module 09 — defence | | 21 May 2027 | |

**Durations per route, through Module 08 (the table drawn up on 13 September; printed by
`probes/duration_table.py` into `probes/results_timing/DURATION_TABLE.md`, reprinted 14 September
with the measured anchor factor F = 3.34; rows marked "this copy" are arithmetic on that table's
figures shown in §3.2 or in the row).** Laptop = measured where marked (m); **desktop = an estimate
from the core count of the priced but unbought workstation, 2.3–3.8 × the laptop, never timed**;
Snellius = four thin nodes in parallel, an estimate from the laptop's core-hours with a factor 2 for
parallel inefficiency, to be replaced by one timed energy on the actual node. Rows marked (e) rest
on unmeasured per-energy factors and are brackets; the R3 row is kept, labelled, because it prices
the claim as the Ladder states it.

| step | computation | days on laptop | days on desktop (estimate) | days on Snellius (4 nodes) | status |
|---|---|---|---|---|---|
| R0 pilot (benzene) | 448 LNO-CCSD(T)/cc-pVTZ xtight energies at 76 min | 24 | 6–10 | 0.8–1.3 | m |
| naphthalene DFT dry run (stage A) | two psi4 Hessians at 6-31G* on the symmetrised geometry | done 15 September | — | — (psi4 not on Snellius) | m |
| R1 smoothness σ (decision 35) | 10 naphthalene tight energies at 11.5 h | 4.8 | 1.2–2.1 | 0.2–0.3 | m per energy; **not started** — queued behind probe B1's cc-pVTZ cells (decision 38) |
| probe B1 (basis probe) | 15 cc-pVDZ + 15 cc-pVTZ tight energies on three modes | 0.6 (cc-pVDZ, done) + ≈ 6 (cc-pVTZ) | — | — | m; verdict ≈ 21–22 Sep |
| M2a, the gradient cost ratio g | PySCFAD cells 0–4, benzene cc-pVDZ | ran 14 September | — | — | g unmeasurable on the laptop at the coupled-cluster level |
| R1 deck (naphthalene), 474 energies as ± pairs | 474 xtight energies at 38 h (11.5 h × F, F = 3.34 measured) | 759 | 198–330 | 25–41 | m |
| **R1 H deck (decision 37)** | 291 xtight energies at 38.4 h = 11,174 h | **466** | **123–203** | **15–25** | m; this copy (291/474 of the row above) |
| R1 diagonal H deck only (thin) | 114 energies × 38.4 h = 4,378 h | 182 | 48–79 | 6–10 | m; this copy (the 6 September table had 96 energies, 154 days) |
| R1 deck, couplings thinned by P25 | 210 energies | — | — | — | **not licensed (16 September)**; row struck |
| R1 H deck at cc-pVDZ xtight | 291 energies at 3.9 h (69 min × F) | 47 | 12–20 | — | e; conditional on probe B1 (proposed, P27, open) |
| R1 by gradients (side project M2) | 18 gradients = 18·g energies | — | — | — | g unmeasurable on the laptop at the coupled-cluster level; a larger machine |
| three-ring rung, diagonal-first H decks at tight cc-pVDZ | 156 + 178 = 334 energies at 2.5–5 h | 35–70 | 9–30 | ≈ 3–10 (6,000–20,000 SBU) | e; conditional on probe B1 (proposed, P27, open) |
| anharmonic step, benzene — finite-difference DFT Hessians (psi4 1.10.2) | pyVPT2 at B3LYP/6-31G*: ≈ 4,100 gradient evaluations | 0.4–0.5 (10–11 h at 8 threads) | 0.1–0.2 | — (psi4 not on Snellius) | **m** 15–16 September (the run was interrupted at 68 % by a system restart; a checkpoint layer now exists, so a restart costs one task) |
| anharmonic step with analytic Hessians (psi4 1.11) — benzene / naphthalene | 2M + 1 Hessians: 61 / 97, at the factory's measured 195 s (benzene) and 707 s (naphthalene) per B3LYP/6-31G* Hessian | 0.14 (3 h) / 0.8 (19 h) | < 0.1 / 0.2–0.3 | — | **m** per-Hessian time; the counts are arithmetic |
| anharmonic step with analytic Hessians — pyrene / coronene | 145 / 205 Hessians at the timing note's fitted t ∝ N_atoms^3.33 (six molecules, 14 September) | ≈ 4 / ≈ 17 | 1–2 / 4–7 | — | e (the fit, not a run) |
| the DFT Hessian of the largest reach species, C₃₈₄H₄₈ (432 atoms) | one B3LYP/6-31G* Hessian by the same fit | ≈ 330 | 87–143 | — | e; a desktop or cluster object, as §5.1 says of it |
| three-ring rung, full H decks at tight cc-pVDZ | 499 + 1,015 = 1,514 energies | 160–320 | — | — | e; not what the go/no-go needs (P27 §4) |
| R2 pyrene, full deck | 952 energies (P27's count; the 13 September table had 936) at 5–10 × the naphthalene energy | does not fit (memory, cc-pVTZ) | 1,950–6,500 | 240–810 | e |
| R2 pyrene, thin decks (diagonal / gradients) | 144 energies / 28 gradients (170 as an H diagonal deck, P27) | does not fit at cc-pVTZ | 300–1,000 / 120–400 | 40–130 / 15–50 | e |
| R2 chrysene, triphenylene, tetracene, full decks | ≈ 2,100 / 924 / 1,248 energies (tetracene per P27; 1,218 in the 13 September table) at 5–10 × naphthalene | does not fit | 1,900–14,600 each | 240–1,830 each | e; P27 proposes chrysene and triphenylene as DFT-level hold-outs (open) |
| R3 coronene, full deck | ≈ 842 energies at 25–100 × the naphthalene energy | does not fit | 8,800–58,600 | 1,100–7,300 | e (extrapolated; no measurement behind the factor) |
| R3 coronene, thin decks (diagonal / gradients) | 204 energies / 12 gradients | does not fit | 1,400–9,600 / 250–1,700 | 180–1,200 / 30–210 | e |
| Module 05 corpus factory | 11,321 B3LYP/6-31G* Hessians at 3–7 min; layers A + A′ + B priced at 177 laptop-days (14 September) | 24–55 (QM9 layer) | 24–55 | 0.4–0.9 | m/e |
| Modules 05–08 (training, proposer, officer, assembly) | no new coupled-cluster energies | hours | hours | hours | not measured |
| R6 fragment-probed C₃₈₄H₄₈ (if licensed) | 56 symmetry-unique fragments × an unmeasured per-fragment cost | — | — | — | not measured |

What the table says: R0 and R1 are within reach — R0 on the laptop in weeks, R1 as the 291-energy
H deck on four Snellius nodes in two to four weeks or on the desktop in four to seven months at the
anchor's basis, or on the laptop in about seven weeks at cc-pVDZ if probe B1 licenses it; **every
full deck above naphthalene is out of reach on every route at the anchor's basis**, by the decks,
not the machines — probe B1 is the measurement that could return them (a win would put a full
pyrene deck at Snellius-weeks and, by P27's estimate, the three-ring rung's diagonal-first decks at
35–70 laptop-days), and until it reads the plan promises thin decks above naphthalene (decision
36). The levers the table carries are the tight/xtight choice (÷ 3.3; the accuracy side measured
at benzene: 0.47 / 0.03 / 0.79 → 0.11 / −0.01 / 0.23 cm⁻¹ — decision 38 keeps the anchor at xtight
for R1's agreement claim, and P27 proposes tight for the transfer rungs, whose threshold is 2.5
cm⁻¹, open), the single-sided patterns of decision 37 (474 → 291, confirmed) and the cc-pVDZ deck of
probe B1 (÷ 10 per energy, verdict pending); the DFT-only thinning of the couplings (P25) is not a
lever (§3.5), and g is not measurable on the laptop.

**Two scenarios follow from the one hinge, cluster access (decision 36; re-read against decision
39).** **With a small cluster allocation** the programme ends at the defence of 21 May 2027 with R1
full, R1⁺ under the (T) port, the three-ring go/no-go read, the rungs above it thin (the transfer
tests) or full where probe B1 licensed them, and the network licensed or refused per family.
**Without it** R1 runs on the desktop (or on the laptop at cc-pVDZ, if probe B1 wins) or stops at
the pilot, the network is trained on R0–R1 (and R1⁺) plus the corpus, its reach claim thinner and
honest; the defence date stays 21 May 2027, and the end of March 2027 is the date by which this
scenario's compute must have finished for Module 08 on 16 April (the 6 September text wrote that
"the defense can be held at the end of March 2027" in this scenario; the reading adopted here is
flagged in the change log). By P27's calendar the go/no-go on the size axis falls in February–April
2027 on the laptop alone and in December 2026–January 2027 with the desktop; in both scenarios it
precedes Module 08 (proposed, P27, open). The hinge is December: a cluster request not submitted
before the winter break puts the project in the second scenario. The critical path is the laptop's
compute until the end of October, the student's decisions in the evenings, and the supervisor's
reading time at the two points named.

**The serial sum, one anchor job at a time (arithmetic on the table above; the machine runs one
job, so the days add).** Between 26 September 2026 and Module 08 on 16 April 2027 there are about
200 laptop-days. *Without a cluster and with probe B1 winning:* the R0 pilot 24, the smoothness run
4.8, probe B1's cc-pVTZ cells 6, the R1 H deck at cc-pVDZ 47, and the three-ring diagonal decks
35–70 — together **117–152 days**, which fits, but leaves 48–83 days for everything else. R1⁺ (the
cation deck, only with the (T) port of item 41) and the corpus factory of Module 05 do not both fit
in what remains: one of the two moves to a second machine or lapses, and the plan says which at the
three-ring go/no-go rather than promising both here. *Without a cluster and with probe B1 losing:*
the R1 H deck is 466 laptop-days on its own, so R1 moves to the desktop or the deck stops at the
pilot, as the scenario above states. *With a small allocation:* R1 runs on the nodes (15–25
node-days), the laptop keeps 24 + 4.8 + 6 + 35–70 = **70–105 days** and has room for R1⁺ or the
corpus, not both. The anharmonic step of each ladder molecule (the rows above: 3 h at benzene, 19 h
at naphthalene, 4 and 17 days at pyrene and coronene) is counted inside the rung that needs it.

## 13. What is asked of the supervisor

1. A critical reading of §2–§3 (why the coupled-cluster budget moves to the harmonic correction,
   why it is recovered by probing under a symmetry prior, and what the first measurements say) and
   of §7 (the evaluation contract, with the opponents now named) — the places where the plan's
   discipline either holds or does not.
2. A view on the fragment-probing route to the largest sizes (§4) and on the Module-05 target
   (§10, item 4), both decided by the student as methods subject to measurement — a supervisor's
   objection would reopen either — and on the side project of §5.3, whose milestones, kill
   criterion and budget terms are stated there.
3. **Laboratory sources — or one measurement** (revised 13 September; the 6 September wording asked
   only for a source). Module 03 finds no gas-phase source that makes the C–C families at the
   pyrene rung decidable at the plan's 5 cm⁻¹ promise: the hot records give u_band 8.6–16 cm⁻¹ per
   family (8 cm⁻¹ resolution plus the temperature term), the jet-cooled free-electron-laser band
   lists ≥ 5–17 cm⁻¹ from their stated bandwidth alone; only naphthalene (Pirali et al. 2009; ν46
   origin to 10⁻⁶ cm⁻¹, Albert et al. 2011, Pirali et al. 2013) and one pyrene band (ν68, Brumfield
   et al. 2012) are resolved. **One cold, resolved measurement of pyrene — one strong band per
   family at 6.2, 7.7, 8.6 and 11–13 µm, band centres tabulated to ≤ 1 cm⁻¹ — would make the rung
   decidable.** The instrument class that reaches this is the one behind the single resolved pyrene
   band the plan already cites: the jet-cooled, rotationally resolved measurement of Brumfield,
   Stewart & McCall 2012 (origin 1184.035595(20) cm⁻¹, T_vib ≤ 111 K), not a free-electron-laser
   band list. A source the supervisor knows of, or an instrument of that class in the supervisor's
   network that could take such a request, is what this item asks for — by whatever cold method the
   supervisor judges feasible, the instrument class being the supervisor's to weigh and not the
   student's. What the scoreboard needs is centroid precision on the band centre, not the
   instrument's bandwidth: item 7 below leaves the bandwidth-to-centre question open, and a resolved
   measurement settles it for the bands it covers. Without such a number the corrections of §12 can
   be produced at this rung but not scored. The student pre-registers the scoreboard rows before any such number arrives; laboratory
   data are added before, never after, a comparison is scored
   (`notes/Ask_Note_2026-09-13_Lead_G_Cold_Measurement.md`).
4. A view on the intensity question (§7): positions are the promise, intensities are scored where
   a calibrated gas-phase measurement exists and reported elsewhere, and a coupled-cluster
   correction to intensities is a measured question rather than a promise. If the supervisor wants
   intensities carried further, the dipole probe M1-μ is the measurement that would license it.
5. **Three asks that the 6 September text bundled into one sentence**, now that the naphthalene
   measurement justifies them (38.4 hours per energy on the laptop at the anchor thresholds,
   measured 14 September; the 291-energy H deck is ≈ 11,200 laptop-hours):
   - **5a. Sponsorship of a Snellius Small Compute application.** Sized by the measured anchor
     energy on the decision-37 deck: the Compute Budget's Snellius estimate is 200–300 SBU per
     naphthalene energy at the tight thresholds; the anchor runs at xtight, which costs 3.34 × tight
     (measured); the deck is 291 energies; so 291 × 3.34 × 200–300 ≈ **195,000–290,000 SBU** for the
     naphthalene deck at cc-pVTZ — an estimate until one energy is timed on the node, which is the
     application's first job — inside a Small Compute application (up to 1,000,000 SBU). The 6
     September figure of 330,000–500,000 SBU was the same arithmetic on the 474-energy deck. If
     probe B1 licenses the cc-pVDZ deck the figure falls by about an order of magnitude (the 14
     September estimate for the 474-energy cc-pVDZ deck was ≈ 30,000–45,000 SBU; × 291/474 ≈
     18,000–28,000) and the request is re-sized before submission. To it come the thin decks of the
     rungs above naphthalene (tens of thousands of SBU each), the canonical cc-pVQZ diagonal line of
     decision 26, and, if the three-ring go/no-go is a go, the four-ring decks (pyrene and
     tetracene, ≈ 170 + 200 diagonal energies at 3.5–10 h each, estimate) as the allocation's second
     job (proposed, P27, open).
   - **5b. A machine in the supervisor's own network.** Whether a suitable many-core machine exists
     there for the R1 deck or the cation and three-ring decks — the desktop route of P13 without the
     purchase.
   - **5c. The named expert.** At the large-rung stage, serving as or nominating the named expert
     whose pre-registered judgment is the datum where no laboratory truth exists (the
     "expert-judgment datum" of §5.2).
6. Whether the supervisor sees the network of §6 as a reason to widen the corpus of measured
   molecules beyond the ladder, at cluster cost, once the three-ring rung has printed the range of
   the correction.

**Questions the student will bring to the first meeting** (collected 8 September; each is a
number or a source the plan would use, none changes a rule by itself):

*On the laboratory side.*

7. For the jet-cooled band lists of Lemmens et al. 2019 and 2021, the free-electron-laser bandwidth
   per measurement rather than the "0.5–1 % of the frequency" of the papers — it is the resolution
   term of the cold columns — and whether the 10–19 cm⁻¹ disagreement between the cold coronene
   bands at 7.7 and 8.8 µm and the hot spectra of Joblin et al. 1994 with their temperature slopes
   has a known cause.
8. For Maltseva et al. 2016, the band tables and laser bandwidth of the 3 µm spectra of pyrene,
   chrysene and triphenylene, and whether the assigned features can be scored as fundamentals given
   the Fermi-resonance polyads in that region.
9. For Pirali et al. 2009, whether the offset between the Q-branch head and the band origin of the
   c-type naphthalene bands is known better than the 0.5 cm⁻¹ upper bound adopted here (decision
   21).
10. The temperature of the PNNL naphthalene record (25 °C in the methods of Schneider et al. 2024,
    50 °C in its figure caption) — asked only if the record's own metadata file does not settle it.

*On the PAHdb Anharmonic library (line B).*

11. Whether all 45 spectra of version 1.00 were computed with the protocol stated in the two 2024 papers read (J. Chem. Phys. 160, 211101; MNRAS Lett. 531, L87)
    (B3LYP/N07D, the 200 × 974 grid, SPECTRO with symmetry-based resonance polyads, a 200 cm⁻¹
    window, modes below 300 cm⁻¹ excluded), or with per-species deviations the plan should record;
    and which of those choices the 2015 and 2016 founding papers fixed.
12. Whether stick lists (positions and intensities) of the library are downloadable, and which
    line profile the library applies — the plan scores positions and integrated intensities, so the
    profile matters only for the figures.
13. Whether the comparison of §7 — stick positions per family, with the Δ₂ = 0 null row
    separating this pipeline's anharmonic treatment from the coupled-cluster correction — is, in the
    supervisor's judgment, the fair way to put a coupled-cluster harmonic correction next to the
    supervisor's method; and
    which DFT level the supervisor would regard as the "same footing" for the pipeline's production constant
    (§5.1, not yet chosen).
14. Whether a coupled-cluster harmonic reference for naphthalene exists in the supervisor's group's work or
    elsewhere: the expected-effect line of the evaluation has a literature figure for benzene only
    (5.45 cm⁻¹, Esposito et al. 2024, a mean over the modes) and none at R1.
15. Whether excluding modes below 300 cm⁻¹ from the VPT2 in that protocol drops their couplings
    to the 6–15 µm fundamentals entirely, or only their own bands — relevant to how the Δ₂ = 0 null
    row of this pipeline, which keeps them, is read against line B.

*On the ladder and the programme.*

16. Whether the scope of the promise — a coupled-cluster correction to the harmonic constants
    only, no coupled-cluster anharmonic correction, intensities scored on benzene and naphthalene
    only, the network licensed per family — is one the supervisor would sign, or whether the
    supervisor wants any of the three measured questions of §6–§7 (M1-μ, the diagonal cubic
    by-product, the learned prior) promoted before the pilot note.
17. The asks 5a–5c above in concrete form when the time comes: the size of the cluster-time
    request the supervisor would sponsor, whether a machine exists in the supervisor's network, and
    who serves as the named expert for the reach rungs.
18. On the cations (added 16 September; P27 §5, open): which gas-phase and matrix spectra of
    naphthalene⁺ the supervisor would regard as the scoring columns for R1⁺ (named before Module 03
    prints them, under the no-swap rule), and whether benzene⁺ — Jahn–Teller active, a static deck
    about one D₂h minimum not describing the observable spectrum without a vibronic treatment —
    should get a deck at all or remain the timing point.

## 14. References

Verification status is tracked per item in the working bibliography of this folder; every
identifier is re-verified against the primary source before it appears in any scored document.

Cited in this proposal (verified by Crossref, arXiv or full text on 2–6 September 2026 unless
marked otherwise; author initials are given only where a held PDF's first page shows them):

- Altun, A., Ghosh, S., Riplinger, C., Neese, F., Bistoni, G. 2021, J. Phys. Chem. A 125, 9932.
  DOI 10.1021/acs.jpca.1c09106. (Local-approximation error grows with acene length; CPS
  extrapolation.)
- Bégué, Carbonnière & Pouchan 2005, J. Phys. Chem. A 109, 4611.
  DOI 10.1021/jp0406114. (Hybrid CC-quadratic / DFT-anharmonic force field.)
- Boese, Klopper & Martin 2005, Mol. Phys. 103, 863. DOI 10.1080/00268970512331339369. (Origin
  of the hybrid split: coupled-cluster harmonics, cheap anharmonics.)
- Bos et al. 2025, ACS Omega 10, 62282. DOI 10.1021/acsomega.5c10225. (ML-corrected DFT
  scaling; the approach the in-house calibrated-harmonic baseline reproduces.)
- Brumfield, Stewart & McCall 2012, J. Phys. Chem. Lett. 3, 1985.
  DOI 10.1021/jz300769k. (One rotationally resolved cold band of pyrene near 8.5 µm; read in full 8
  September: band origin 1184.035595(20) cm⁻¹, T_rot ≈ 23 K, T_vib ≤ 111 K.)
- Chu, Guenther, Rhoderick & Lafferty 1999, J. Res. Natl. Inst. Stand.
  Technol. 104, 59. DOI 10.6028/jres.104.004. (The NIST Quantitative Infrared Database; read in full
  2026-09-06 from the NIST PDF: 296 K, 760 Torr N₂, 0.12 cm⁻¹, intensities 3.3 % at k = 2, not
  certified in the water, CO and CO₂ regions.)
- Esposito, V. J., Fortenberry, R. C., Boersma, C., Allamandola, L. J. 2024, J. Chem. Phys. 160,
  211101. DOI 10.1063/5.0208597. (NASA Ames group. C–H overtone spectra of benzene and naphthalene;
  the PAHdb-anharmonic protocol; B3LYP/N07D vs CCSD(T)-F12b benzene harmonics, MAD 5.45 cm⁻¹.)
- Esposito, V. J., Fortenberry, R. C., Boersma, C., Maragkoudakis, A., Allamandola, L. J. 2024,
  MNRAS Lett. 531, L87. DOI 10.1093/mnrasl/slae037. (NASA Ames group. CN stretches of cyano-PAHs;
  the second statement of the PAHdb-anharmonic protocol, 1 cm⁻¹ Gaussian profile; CC BY, read in
  full 8 September.)
- Fusè, M., Mazzeo, G., Longhi, G., Abbate, S., Yang, Q., Bloino, J. 2024, Spectrochim. Acta A
  311, 123969. DOI 10.1016/j.saa.2024.123969. (Reduced-dimensionality VPT2 for large molecules.)
- Olive Dornshuld, L. N., Lahm, M. E., Kitzmiller, N. L., Allen, W. D., Schaefer, H. F. 2026,
  J. Phys. Chem. A 130, 3249. DOI 10.1021/acs.jpca.6c00689. (CMA for intermolecular vibrations.)
- Joblin, Boissel, Léger, d'Hendecourt & Défourneau 1995, Astron. Astrophys.
  299, 835. (PAH band shifts with temperature; read in full 2026-09-06 from the ADS scan; Tables 1–2
  transcribed in the bibliography.)
- Joblin, d'Hendecourt, Léger & Défourneau 1994, Astron. Astrophys. 281, 923. (Gas-phase, solid and
  Ne-matrix PAH spectra 3–20 µm, the hot spectra of the coronene cross-check; read in full 2026-09-06
  from the ADS scan.)
- Käser, Boittier, Upadhyay & Meuwly 2021, J. Chem. Theory Comput. 17, 3687–3699. DOI 10.1021/acs.jctc.1c00249 (journal record Crossref-verified 13 September; read in full 10 September from the held arXiv manuscript, arXiv:2103.05491). (Transfer learning to CCSD(T) anharmonic frequencies — the Δ-learning precedent of §3.1.)
- Qu, Houston, Conte, Nandi & Bowman 2021, J. Phys. Chem. Lett. 12, 4902–4909. DOI 10.1021/acs.jpclett.1c01142. (Δ-ML from local CCSD(T) energies at 15 atoms — added to §3.1 on 13 September; Crossref-verified record, abstract only.)
- Bowman, Qu, Conte, Nandi, Houston & Yu 2022, J. Chem. Theory Comput. 19, 1–17. DOI 10.1021/acs.jctc.2c01034. (Perspective on Δ-ML surfaces — added to §3.1 on 13 September; Crossref-verified record, abstract only.)
- Kitzmiller, N. L., Lahm, M. E., Olive Dornshuld, L. N., Jin, J., Allen, W. D., Schaefer, H. F.
  2024, J. Chem. Theory Comput. 20, 10886. DOI 10.1021/acs.jctc.4c01240. (CMA-2.)
- Lahm, Kitzmiller, Mull, Allen & Schaefer 2022, J. Am. Chem.
  Soc. 144, 23271. DOI 10.1021/jacs.2c11158. (Concordant Mode Approach.)
- Lemmens, Rap, Thunnissen, Mackie, Candian, Tielens, Rijs & Buma 2019, Astron. Astrophys. 628, A130.
  DOI 10.1051/0004-6361/201935631. (Jet-cooled mid-infrared band list of tetracene.)
- Lemmens, Rijs & Buma 2021, Astrophys. J. 923, 238.
  DOI 10.3847/1538-4357/ac2f9d. (Jet-cooled far- and mid-infrared spectra of coronene and larger
  PAHs.)
- Mackie, Candian, Huang, Maltseva, Petrignani, Oomens, Buma, Lee & Tielens 2015, J. Chem. Phys.
  143, 224314. DOI 10.1063/1.4936779. (Opponent line B: the anharmonic quartic-force-field protocol
  of the PAHdb Anharmonic library — naphthalene, anthracene, tetracene; the supervisor is a
  co-author; Crossref record, 8 September; PDF asked of the supervisor.)
- Mackie, Candian, Huang, Maltseva, Petrignani, Oomens, Mattioda, Buma, Lee & Tielens 2016,
  J. Chem. Phys. 145, 084313. DOI 10.1063/1.4961438. (Opponent line B: benz[a]anthracene,
  chrysene, phenanthrene, pyrene, triphenylene; the supervisor is a co-author; Crossref record, 8
  September; PDF asked of the supervisor.)
- Madriaga, J. P., Crawford, T. D. 2025, J. Phys. Chem. A 129, 10014.
  DOI 10.1021/acs.jpca.5c05210. (PNO discontinuities in finite-difference properties.)
- Mai et al. 2025, Mon. Not. R. Astron. Soc. 541, 3073; arXiv:2503.05120. (Opponent line C:
  DFT-trained machine-learning molecular dynamics of PAHs to C₂₁₆.)
- Maltseva, Petrignani, Candian, Mackie, Huang, Lee, Tielens, Oomens & Buma 2016, Astrophys. J.
  831, 58. DOI 10.3847/0004-637x/831/1/58. (Jet-cooled 3 µm spectra of pyrene, chrysene and
  triphenylene among others — the C–H stretch cold column at R2; the supervisor is a co-author;
  Crossref record; abstract grade.)
- Mata & Werner 2006, J. Chem. Phys. 125, 184110. DOI 10.1063/1.2364487. ("Calculation of smooth potential energy surfaces using local electron correlation methods" — the 2006 prior art of §3.1; Crossref-verified 10 September; closed access, asked of the supervisor, not read; its content is cited here as described by Pinski & Neese 2019.)
- Mulas, Falvo, Cassam-Chenaï & Joblin 2018, J. Chem. Phys. 149, 144102.
  DOI 10.1063/1.5050087. (Opponent line B: anharmonic DFT quartic force fields of pyrene and
  coronene; the emission cascade model.)
- Pinski & Neese 2018, J. Chem. Phys. 148, 031101; 2019, J. Chem. Phys. 150, 164102. (The
  DLPNO-MP2 analytic gradient; PNO-relaxation constraints; the continuous degeneracy of localised
  orbitals in symmetric molecules; discontinuities of local-correlation surfaces and their known
  remedies; read 8 September.)
- Pirali, Vervloet, Mulas, Malloci & Joblin 2009, Phys. Chem. Chem. Phys. 11,
  3443. DOI 10.1039/b814037e. (Naphthalene hot-band spectroscopy; the temperature term.)
- Reiher & Neugebauer 2003, J. Chem. Phys. 118, 1634. DOI 10.1063/1.1523908. (Mode-tracking; read in
  full 8 September.)
- Ricca, Boersma, Maragkoudakis, Roser, Shannon, Allamandola & Bauschlicher 2026, Astrophys. J. Suppl. Ser. 282, 7. DOI 10.3847/1538-4365/ae1c38.
  (PAHdb v4.00, opponent line A; the paper does not report the systematic uncertainties of the
  scaled-harmonic library — the reading behind §1.)
- Russ & Crawford 2004, J. Chem. Phys. 121, 691. DOI 10.1063/1.1759322. ("Potential energy surface discontinuities in local correlation methods"; Crossref-verified 10 September; closed access, asked of the supervisor, not read.)
- Sanders, J. N., Andrade, X., Aspuru-Guzik, A. 2015, ACS Cent. Sci. 1, 24. DOI 10.1021/oc5000404.
  (Compressed-sensing Hessians; polyacenes.)
- Schneider, Baker, Scharko, Blake, Tonkyn, Forland & Johnson 2024, J. Quant. Spectrosc. Radiat. Transfer 323, 109045.
  DOI 10.1016/j.jqsrt.2024.109045. (Quantitative vapour-phase spectra of solids, naphthalene among
  them; 25 °C in the methods, 50 °C in the introduction and the Fig. 6 caption; 0.112 cm⁻¹; ±8 % at
  2σ; read in full 2026-09-06 from the OSTI author manuscript.)
- Sharpe, Johnson, Sams, Chu, Rhoderick & Johnson 2004,
  Appl. Spectrosc. 58, 1452. DOI 10.1366/0003702042641281. (The PNNL gas-phase quantitative IR
  database.)
- Subotnik & Head-Gordon 2005, J. Chem. Phys. 123, 064108. DOI 10.1063/1.2000252. ("A local correlation model that yields intrinsically smooth potential-energy surfaces"; Crossref-verified 10 September; closed access, asked of the supervisor, not read.)
- Wang, Luo, Wang & Liu 2025, J. Chem. Theory Comput. 21, 10893.
  DOI 10.1021/acs.jctc.5c01354. (O1NumHess.)
- Williams, N. J., Kabalan, L., Stojanovic, L., Zolyomi, V., Pyzer-Knapp, E. O. 2025, Scientific Data 12,
  DOI 10.1038/s41597-024-04361-2 (arXiv:2408.08006). (Hessian QM9; data: figshare, DOI 10.6084/m9.figshare.26363959,
  v4, CC0 — downloaded and inventoried 12 September 2026.)
- Zhang, X., et al. 2024, J. Chem. Phys. 161, 014109; arXiv:2404.03129. (Automatic-differentiation gradients for local coupled
  cluster, PySCFAD.)

Line D (§3.1, §7; records Crossref-verified 13 September, abstracts read, not yet in the atlas): He,
Mai & Wang 2026, A&A 708, A335; Tang, He, Wang & Qiu 2026, MNRAS 546, stag283; Liu, Wang & Qiu
2026, MNRAS 549, stag893.

Other plan-04 sources carried in the working bibliography and used by the modules (matrix
scoreboards, the DLPNO caveats): Bauschlicher et al. 2018; Chen, Li & Li 2026; Hudgins & Sandford 1998; Lam, Abdul-Al &
Allouche 2020; Mattioda et al. 2020; Sylvetsky et al. 2020; Tang et al. 2025; NIST CCCBDB; Zapata
Trujillo & McKemmish 2022.

---

## Change log against the 6 September text

### Second pass, 16 September (cold read 2)

*The second cold read of this copy (`notes/ColdRead_2026-09-16b_Reading_Copy.md`) checked the 25 items
of the first against it (19 resolved, 5 partly, 1 not applicable) and reported 15 new stumbles. What
this pass changed, in its numbering:*

- **B1 (§1, §12, §13 item 5a).** The thin decks above naphthalene repriced from this copy's own
  duration table at its own exchange rate: at cc-pVTZ the pyrene thin deck is ≈ 0.5–1.7 M SBU and the
  coronene thin deck ≈ 2–16 M SBU, so they lie beyond a Small Compute application and enter the
  request only if probe B1 wins, at roughly one tenth (the measured cc-pVDZ/cc-pVTZ ratio 9.9–10.0);
  the R6 four-part licence, which needs coronene probed whole, hangs on the same condition.
- **B2 (§5.2, §12).** The per-energy factors above naphthalene given their assumption: fragment count
  (15 at benzene, 24 at naphthalene, 37 at pyrene, 54 at coronene) times a per-fragment cost that grew
  14-fold from benzene to naphthalene at cc-pVDZ tight (12 s → 173 s, measured); the low end assumes
  the per-fragment cost saturates, the high end that it keeps growing, and the ring-by-ring ladder
  measures which. Both marked (e).
- **B3 (§12).** A serial sum added per scenario: the laptop runs one anchor job at a time, so the days
  add, and the sum is set against the ≈ 200 days to Module 08 with the items that then do not fit named.
- **B4 (§12, duration table).** Four rows for the anharmonic step: benzene measured with
  finite-difference DFT Hessians (≈ 4,100 gradient evaluations, 10–11 laptop-hours at 8 threads,
  15–16 September, interrupted at 68 % by a system restart, a checkpoint layer written since); the
  analytic-Hessian route at benzene and naphthalene (61 and 97 Hessians at the measured 195 s and
  707 s); pyrene and coronene from the timing note's fitted scaling (e); and the single C₃₈₄H₄₈
  Hessian at ≈ 330 laptop-days (e).
- **B6 (§12).** The smoothness run's status corrected from "running" to not started, queued behind
  probe B1's cc-pVTZ cells; the three bracketed markers stay and name the student and 25 September.
- **B7 (§12).** R2 and R3 dated after the three-ring go/no-go instead of 12 March 2027; the December
  start of R1 labelled by route.
- **B8 (§1).** "The only figure that exists on this ladder" → "the only figure this project's search
  found", the search named.
- **B9 (§13 item 3).** The measurement asked for by whatever cold method the supervisor judges
  feasible; the comparison with the cost of a cluster request dropped; centroid precision named as the
  need rather than instrument bandwidth.
- **B10 (header).** A five-line reading map added.
- **B11 (§1 Terms).** The X- and I-numbers, P10 and probe 2a defined.
- **B12 (§7).** One paragraph on what the in-house calibrated-harmonic baseline is after Module 04's
  leave-one-molecule-out measurement (6.49 against 6.40 cm⁻¹, R² ≤ 0.01): on that data it is line A,
  and it stays as a labelled column rather than as a second baseline beaten.
- **B14 (throughout).** Arithmetic pass: 1.7 GB for the naphthalene cc-pVDZ peak, 3.9 h for the xtight
  cc-pVDZ estimate, 35 min for the benzene tight energy against 76 min at xtight, and the 69 min per
  cc-pVDZ energy stated as the frozen arm's time.
- **B15 (§8).** One sentence on what the LNO pilot licenses that a canonical benzene Hessian cannot.
- **A14, A20, A23.** The two long table cells of §3.1 split; the reading status of Russ & Crawford 2004
  and Subotnik & Head-Gordon 2005 marked where they are cited for the mechanism; the
  threshold-sensitivity line's bracket replaced by the two settings it compares (xtight [10⁻⁷, 10⁻⁸]
  against tight [10⁻⁶, 10⁻⁷]) with the measured biases.
- **Left for the student, 25 September.** B5 (read Maltseva et al. 2016, on arXiv as 1609.09325, and
  delete its request in §13 item 11; the Mackie 2015/2016 papers are not on arXiv, so that request
  stands); B13's remaining "this copy" asides in the duration table's status column; the closing
  suggestion of the cold read, to cut the review-history paragraph of §1 to one disclosure sentence;
  and the three bracketed markers.



Each bullet names the change and the dated decision or cold-read item (CR n = item n of
`notes/ColdRead_2026-09-16_Proposal_and_Cover_Note.md`, disposition of decision 42) it implements.
Numbers that are arithmetic on the sources are shown in place in the body.

- **Title.** "an infrared pipeline with a measured cost" → "a label pipeline with a measured cost and a network licensed per band family", so that the title, §1 and §6 speak with one voice on what is promised (decision 36; CR 1).
- **Header / status line.** Status line replaced by "consolidated reading copy, 26 September 2026 (source text of 6 September with the dated revisions of 8–16 September worked in; the dated original is kept beside it)" (CR 22); one sentence added naming the programme (Udacity — the source names it only through "the Udacity rubric form" and "the programme's elective") and the role asked of the supervisor as inferred from §13; institution and role marked [to be confirmed by the student] because the source is silent on both (CR 10; decision 42).
- **§1.** Rewritten as one voice: pipeline B the label factory, pipeline A the network as the reach product, licensed per family (decision 36; CR 1). The two ≈ 200-word sentences broken into shorter ones without loss of content or citations (CR 14). Esposito et al. 2024 attributed to the NASA Ames group in both places; the supervisor's co-authorship placed on Mackie et al. 2015/2016 and Maltseva et al. 2016 (dated correction of 16 September in the original; decision 42; CR 2). Mata & Werner 2006 marked "full text not read; known through Pinski & Neese 2019" at first use (CR 20). Ricca et al. 2026 softened from "leaves unquantified" to "does not report" (CR 19). The 5.45 cm⁻¹ figure qualified as a mean absolute difference over modes, not a per-mode bound (CR 17). The measurements paragraph extended to 16 September (naphthalene 38.4 h and F = 3.34, the 69-minute cc-pVDZ energy, decision 37's confirmation, the cation timing c = 31, the P25 loss); arm C (0.9–2.7 µE_h) and arm B (0.05–1.2 µE_h) named separately (CR 24). "Neutral" restriction replaced by the cation rung R1⁺ (decision 42 (4); CR 18). Probe "M3" renamed probe B1 (CR 8). The three-ring rung of decision 39 named in the staged criterion. The provenance paragraph records the 16 September cold read.
- **§1 Terms.** Added: full / H / thin deck, τ₇, pipeline A/B, T-1/T-2, probe B1 and the M-numbers' scope, F, c, g, the (T) port, P13/P18/P24/P25/P26/P27 with their status, line D, SBU, levers G and H (CR 9). Q6–Q8 and η₈ do not occur in the proposal and were not added.
- **§2.** Unchanged in substance; one broken line join repaired.
- **§3.1.** Dated insertions (Mata & Werner's reading status, the Qu/Bowman records and the "why not Δ-ML" paragraph, the line-D papers) moved out of the table cells into a paragraph below the table (CR 14); the "474 energies" in that paragraph updated to 291 with 474 kept as the pre-decision-37 count (decision 37); the third row's last cell now says the network is trained on the measured labels (decision 36).
- **§3.2.** The two broken sentences repaired: the "11 of the 57 … and the rerun" fragment and the "The arithmetic, at benzene's … Two numbers, with different roles" fragment re-read as prose (CR 16). The naphthalene rehearsal's state given as of 16 September (stage A symmetrised, the symmetry prior exact on the stand-in per X16, the recovery owed) — the source's "repeats the test … before the R1 deck is built" kept as the rule. The deck priced at 291 energies (decision 37) beside the 474 as ± pairs; "thirty weekly batches" recomputed at 38.4 h: 108 batches as ± pairs, 67 as the H deck (CR 11). Desktop and Snellius figures for the 291-energy deck are the duration table's 474-energy figures × 291/474 (arithmetic shown). The cc-pVDZ price 47 laptop-days cited as proposed (P27, open). P25 stated as not licensed (16 September, X16).
- **§3.3.** The bullet list restored (Design, Smoothness, Bias, Reload, Arbitrariness, Anchor basis, Tighter thresholds, Basis-set line, Definition) and the "×0.7" cost-factor bookkeeping moved to footnote 1 (CR 15). Decision 20's "naphthalene factor owed" replaced by the measured F = 3.34 of 14 September (CR, smaller items). The comparison of the basis terms (+2.8 / −5.2 / −11.1 cm⁻¹) with the 5.45 cm⁻¹ figure reworded as per-mode terms against a family mean (CR 17). One sentence added pointing to probe B1 as the test of a transferred beyond-MP2 increment.
- **§3.4.** Decision 37 (single-sided energies for irrep-pure non-totally-symmetric patterns; the symmetrisation prerequisite with its measured odd parts) added as a dated amendment of the K rule (decision 37, README).
- **§3.5.** Rewritten from the 14 September insertion into one voice; the three levers given their 16 September state: decision 37 confirmed; probe B1 (renamed from "probe M3", CR 8) running, cc-pVDZ cells done 15 September (69 min, 1.7 GB, ratio 9.9–10.0), cc-pVTZ cells pending — verdict marked [to be filled]; P25 not licensed (X16, 16 September) and struck as a saving everywhere. "Licensed per family and charge state" made true by R1⁺ (CR 18; decision 42 (4)).
- **§4.** The Cost question restated as conditional on probe B1 above naphthalene, with the thin-deck case spelled out (CR 5; decision 36). The Reach question rewritten with the network as the route and the deliverable stated as licensed-or-refused per family (decision 36).
- **§5.1.** Item 1: aug-cc-pVTZ's exclusion softened to "set aside … on one reported artefact until a run shows it absent" (CR, smaller items); the symmetrisation prerequisite of decision 37 added; the naphthalene dry run named. Item 2: the diagonal cost under decision 37 noted. Item 3: the geometry term's odd part attributed to the totally symmetric ± pairs (the coupled-cluster force at a symmetric geometry is totally symmetric — the same fact decision 37 rests on; a wording change, flagged here). Item 4: the "upper bound" reading of 5.45 cm⁻¹ replaced by "bounds the family mean, not any single mode" (CR 17).
- **§5.2.** Table gains a Deck column, the rows R0⁺ (timing point; the Jahn–Teller deck decision open, P27 §5) and R1⁺ (naphthalene⁺, the neutral's H deck, condition: the (T) port — decision 41; decision 42 (4)), and the three-ring rung of decision 39; R2/R3's "first off-diagonal-count ratio" and "size sentence decided here" made conditional on probe B1 (CR 5). P27's deck counts (818 / 1,432 / 952 / 1,248, the 334-energy diagonal-first design, 35–70 laptop-days, the isomer rule, chrysene and triphenylene as hold-outs) cited as proposed (P27, open). Two paragraphs added: the order above naphthalene (decision 39) and the cation rungs with the measured c = 31.0, its UCCSD/(T) split and decision 41's port and acceptance tests (P27 §5; README decisions 39, 41). Laboratory sources: a sentence for naphthalene⁺'s columns (P27 §5). The R4–R5 expert datum now points to §13 item 5c.
- **§5.3.** The losing condition of the size question made conditional on probe B1 (CR 5). The side project's M2 state on 16 September added (g unmeasurable on the laptop at the coupled-cluster level, X16). A closing paragraph on plan 06: P25's licence test lost on 16 September (76 of 141 pairs against ≤ 70.5 and ≤ 1.5 × 33), lever B not licensed, the cost branch closing at the 15 October review under its own rule, the nine-product and locality results kept (X16).
- **§6.** The bold "No transferable, train-once spectrum model" paragraph rewritten as "No train-once motif transfer; a network licensed per family instead" (decision 36; CR 1). The 14 September "network as the reach product" insertion merged into it; the decision 32 paragraph ("named follow-up, outside the sequence", 12 September) removed from the body — its history: the network was first named stand-out work outside the module sequence, gated by the range at R2–R3 and the Q10 coverage table, not in the promised set; decision 36 (14 September) made it the reach product and kept those two gates as the licence's gates (§10 item 32 records the supersession). The outlook paragraph ("Plan 05 builds no transferable model") rewritten as "What the network is trained on" (decision 36). Q9's count corrected to six sizes (C₆, C₁₀, C₁₄, C₁₆, C₁₈, C₂₄) and its dependence on the anthracene deck stated (CR 25); c_F disambiguated from the cation ratio c. "No vibronic treatment" added to the not-done list (P27 §5).
- **§7.** Opponents table: line D row added as reserved pending the full read (CR 9). The dual-role paragraph names Mackie and Maltseva and places Esposito with Ames (CR 2). Pilot-note inputs: item 3 (naphthalene stage A exists, recovery owed), item 4 (probe B1 cells), item 6 (M2a) updated; item 7 sized by decision 35 — one mode, nine points, ≈ 10 tight energies, 4.8 laptop-days, σ(tight) standing in for σ(xtight) with the benzene justification — replacing the four-mode, two-arm, 72-energy version (CR 13; decision 35). The threshold-sensitivity line: the source's "tight vs default" pair is stale after decision 20 and no source names the new pair — marked [to be fixed in the pilot note] (CR 23).
- **§8.** "Fits the laptop" defined once (memory under the 25 GB ceiling; wall-clock in 168-hour weekly batches with dated checkpoints; the arithmetic rule for cluster work) and applied to the bias line, the R0 pilot, the R1 deck, pyrene and the canonical benzene Hessian — the last re-read as "would pass both tests but is not run because the licence does not need it", where the source said "does not [fit]" at 378 h while pricing the 567-h R0 pilot as laptop work (CR 11; flagged as a resolution of an inconsistency, source lines 814–815 vs 1082). The subsystem ceiling given as 22 GB until 12 September and 25 GB since (Compute Budget, 12 September note; P27 §3). The R0 pilot's pricing at 448 energies explained against the symmetry-prior rerun's K = 60 + 210 = 270 (CR 12). Added bullets: the naphthalene DFT dry run (decision 37's confirmation), probe B1's cc-pVDZ cells, the cation timing (M4, 15 September); the corpus priced at 177 laptop-days for layers A + A′ + B (P27 §7, citing the 14 September Timing Note). "Still owed" list updated; the anthracene "dated bonus" folded into the three-ring rung (decision 39).
- **§9.** Decision count 8–34 → 8–42 with a one-line summary of items 35–42; the third cold read named.
- **§10.** Heading "(all closed)" → "(items 1–42; all closed unless marked open …)"; item 20's "naphthalene factor owed" replaced by F = 3.34 (CR 4, smaller items); item 26's "upper bound" wording aligned with §5.1; item 27's "no new coupled-cluster energies" aligned with the ladder; item 32 marked superseded by item 36; item 34 given X16's nine-product result; items 35–42 added with their dates from the README's decision record (CR 4; decision 42).
- **§11.** Risk 1: the naphthalene factor and the running noise run; risk 3: X16's locality numbers; risk 4: 5.45 cm⁻¹ as a mean over modes and Esposito as Ames (CR 2, 17); risk 5: "or measurement"; risk 6: P25's loss and decision 37; risk 7: the (T) port bounded the same way; risks 9 (probe B1 loses) and 10 (the cation price) added — both restate measured facts and written responses, no new claim.
- **§12.** Mapping paragraph: the Module-05 model's reach role tied to pipeline A. Calendar re-read against decisions 38–41: the proposal row moved to 26 September (decision 40; the source's "sent as a scheduled e-mail for Monday 14 September" dropped as superseded); the pilot-note-inputs row's stale sentence on a 72-energy noise run "not deliverable by 23 October" deleted (CR 13; decision 35); the cluster-request row placed before the R1 row and the two dates exchanged (request 4 Dec 2026, R1 start 11 Dec 2026 — the source had R1 4 Dec, request 11 Dec; CR 7) with the R1 row labelled by route; an R0⁺/R1⁺ row and a three-ring-rung row added (decisions 39, 41; P27's dates marked proposed, open). Duration table: "schatting" → "estimate" and "the table the student was asked for" → "the table drawn up" (CR, smaller items); the 474-energy R1 row kept and a 291-energy H-deck row added with the arithmetic (decision 37); the diagonal-only row recomputed at 114 energies (P27's H diagonal deck) with the source's 96 noted; the "+ P25" row struck as not licensed (16 September); the gradient rows marked "g unmeasurable on the laptop"; probe B1, M2a and the dry run given their 16 September status; cc-pVDZ rows for R1 and the three-ring rung added as proposed (P27, open); pyrene 952 and tetracene 1,248 noted against the table's 936 and 1,218 (P27 §2). Scenario paragraph: one defence date per scenario — 21 May 2027 in both, with the end of March 2027 read as the date by which the second scenario's compute must have finished for Module 08; the source's sentence "the defense can be held at the end of March 2027" (source line 1101) against the table's 21 May 2027 (source line 1076) could not be resolved from the source alone, so both dates are stated and this reading is flagged (CR 7). P27's go/no-go calendar added as proposed.
- **§13.** Item 3: the instrument class named as the one behind Brumfield, Stewart & McCall 2012's rotationally resolved cold band (CR 21). Item 5 split into 5a (Small Compute sponsorship, with the one-line SBU derivation 291 × 3.34 × 200–300 ≈ 195,000–290,000 SBU, inside ≤ 1,000,000 SBU, an estimate until one energy is timed on the node; the cc-pVDZ re-sizing; P27's second job as proposed), 5b (a machine in the supervisor's network) and 5c (the named expert) (CR 3; decision 42 (3)). Item 6: "R3" → "the three-ring rung" (decision 39). Item 14: the 5.45 cm⁻¹ qualified. Item 16: the network's licence added to the scope sentence (decision 36). Item 17: refers to 5a–5c. Item 18 added on the cation columns and the benzene⁺ deck decision (P27 §5, open; decision 42 (4)).
- **§14.** Esposito et al. 2024 (both entries) marked NASA Ames group; Mackie 2015/2016 and Maltseva 2016 marked as the supervisor's co-authored papers (CR 2); Ricca et al. 2026's annotation softened to "does not report" (CR 19); Mata & Werner 2006's annotation says its content is cited as described by Pinski & Neese 2019 (CR 20); the line-D records listed separately as not yet in the atlas.
- **Third pass, 17 September (dated notes only; no frozen sentence rewritten).** §3.2: a dated note after the pricing paragraph records the amplitude test's outcome on all 616 patterns (FAIL — the energies-only coupling route has no amplitude window at naphthalene; the diagonal is untouched) and the gradient route as counted, stress-tested and priced this week (X14/X20/X21: 2k + 1 = 19 gradients at naphthalene, exact; g = 6.04 for LNO-CCSD(T) at 6-31G on the full energy, 7.6 inferred; 2.5–2.0× on the H deck, 4.8–3.8× at pentacene — corrected 22:31 from a first reading taken on the (T)-increment attribute), with the three open items named. §7: the lever list gains a dated fourth bullet pointing to that note. Plan 06's decision rule carries the matching dated amendment (branch C stays open on the measured g). The 0.5 cm⁻¹ of decision 21 was traced to its source the same day (the head-to-origin term of Pirali 2009, an upper bound, one molecule; 5–17 cm⁻¹ elsewhere on the ladder) — recorded in `notes/Desk_2026-09-17_Tolerance_and_Label_Count.md`, not yet folded into §4's error budget.
- **Date change, 18 September (decision 44).** The conversation with the supervisor moves from 26 to 28 September 2026: stage 0 of probe B1's cc-pVTZ cells passed on 18 September 04:28, but one TZ tight energy costs 16.6 h, so the third mode and the report land ≈ 27 September. Header, decision 40 and the §12 calendar row carry the new date; the filename is kept so that the ledger's and the blog's links stay valid.
- **Fourth pass, 18 September (the user: "Herschrijf alinea 2 en de slotzin van alinea 3"; two frozen passages of §1 rewritten, the first rewrite of frozen text since 6 September).** §1, the "In a few sentences" paragraph: "a handful of energies … no gradients" replaced by the measured route — energies along single modes for the diagonal, gradients along symmetry-chosen patterns for the couplings (2 per pattern + 1, 19 at naphthalene), with the amplitude test of 17 September and decision 43 named as the reason; "no full-molecule coupled-cluster calculation" replaced by "without a canonical coupled-cluster calculation of the molecule", since the LNO energies are whole-molecule calculations. §1, the closing sentence of the prior-art paragraph: "recover the correction from energies alone" replaced by the diagonal-from-energies, couplings-from-gradients statement. Nothing else in §1 touched.
- **19 September (dated note only).** §7, after the opening paragraph: the tolerance is the scoring column's, per family (0.5 cm⁻¹ is Pirali's naphthalene term; 1 cm⁻¹ Maltseva, C–H stretch; 5–17 cm⁻¹ FEL), and the shape test of 17 September fixes where the couplings are needed (fingerprint and out-of-plane windows) and where the diagonal suffices (C–H stretch). No frozen sentence rewritten.
- **Not changed, on purpose.** The 5,160-energy whole-molecule figure of §4 (four energies per mode × 1,290 modes); the Ladder's ≥ 2,580 counts two per mode (the cold read's smaller item concerns the Ladder, which is not this copy's job). The cover note and the Ladder are not touched.
- **Markers left in this copy.** (1) Header: "[institution and role: to be confirmed by the student]". (2) §3.5: "[probe B1 verdict: read family by family — lose (C–H out-of-plane, 20 September), win (C–H in-plane bend, 23 September), between (C–C stretch, 24 September); the dated notes below]" (expected ≈ 21–22 September; decision 40 dated it ≈ 21 September, the brief for this copy ≈ 22 September). (3) §7: "[the two LNO threshold settings that define the threshold-sensitivity line: to be fixed in the pilot note]".

### Follow-up, 20 September evening (the supervisor's PDFs)

- §1 and §3.1: the prior-art sentence and row on fixed local-correlation spaces rewritten after Mata & Werner 2006, Russ & Crawford 2004 and Subotnik & Head-Gordon 2005 were read in full (PDFs received 20 September 18:05). Freezing domains for numerical Hessians is named as 2006 practice; the plan's claim is the transport of LNO-type spaces with the projection term measured. Reading note `notes/Reading_Note_2026-09-20_Supervisor_PDFs_L1_Smoothness_and_Mackie.md`. Line B's accuracy numbers from Mackie 2015/2016 are in `Frozen_Lines_to_Beat.md` §3 (dated line 2026-09-20); the pyVPT2 polyad check is recorded in the reading note §5. No number of this copy changes.

- **25 September 08:3x (dated notes only).** §3.5: probe B1's third family (between; closing tally lose / win / between) and the 25 September note on E9, E10, the size split, L2 and the layer-B proof-of-learning run; the §3.5 marker replaced by the verdict line. Nothing frozen rewritten.
