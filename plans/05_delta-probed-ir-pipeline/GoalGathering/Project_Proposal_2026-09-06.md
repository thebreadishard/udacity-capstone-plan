# Probed coupled-cluster corrections to the harmonic force constants of polycyclic aromatic hydrocarbons: an infrared pipeline with a measured cost

**Master's capstone project proposal — plan 05.** Prepared for supervision review; first version 6
September 2026 (the file name keeps that date), revised through 12 September 2026: the measurements, decisions and questions dated 8–12 September below were added after the 6-September
cold read, and a second cold read on 8 September — from the supervisor's own position — and its
closures of 10 September are on file. Earlier drafts (3 and 4 September) are in the repository's
history; this text supersedes them and stands on its own. Every number in it that describes this
project's own performance was printed by a script in the folder `probes/` and can be re-run, or is
arithmetic shown in place on such numbers; numbers from the literature are marked as such. A note
on provenance and on the terms used follows the summary.

---

## 1. Summary

Infrared band positions of polycyclic aromatic hydrocarbons (PAHs) underpin the interpretation of
the aromatic infrared bands JWST now resolves. The reference predictions — most prominently the
NASA Ames PAH IR Spectroscopic Database (PAHdb) — rest on scaled harmonic DFT, whose systematic
uncertainties the database's own current paper leaves unquantified (Ricca et al. 2026). This
project builds and tests one pipeline: any individual neutral aromatic molecule in, an infrared
absorption spectrum out, with the **harmonic force constants corrected by a local coupled-cluster
anchor, checked against canonical coupled cluster where affordable**, and a measured error budget
on every claimed band. The question behind it is whether a measured coupled-cluster correction,
licensed on the molecules where the truth is known, can mean anything for the PAHs where no truth
exists; benzene and naphthalene are the instruments of that question, not its goal.

**In a few sentences, for a reader who knows the field.** We want to show that the harmonic force
constants of a PAH can be corrected towards coupled-cluster quality with a handful of energies in a
frozen local-correlation space — no gradients, no full-molecule coupled-cluster calculation — and
that this correction can first be calibrated on benzene and naphthalene against the known truth, so
that every molecule on the ladder gets a complete anharmonic spectrum, positions, intensities and
shape as PAHdb delivers them, but with band positions that carry a measured coupled-cluster
correction and an error margin instead of a fitted scale factor, and a tested route to the large
PAHs for which no prediction above scale-factor level exists today (the test is decision 27, §6). Every piece of this exists
already, separately: Reiher and Neugebauer showed in 2003 that selected normal modes can be computed
without the full Hessian; Mata and Werner froze the local-correlation domains along a reaction path
in 2006 to keep local coupled cluster smooth; Allen and Schaefer's Concordant Mode Approach extracts
CCSD(T) force constants from a few energies in a DFT normal-mode basis for small molecules; Käser and Meuwly transfer-learn a cheaper method's surface to coupled-cluster quality from a few hundred coupled-cluster points on molecules of up to nine atoms; the supervisor's own
group built, with Mackie and later Esposito, the anharmonic-DFT front for PAHs up to eighteen
carbons; Pirali's naphthalene spectrum is what everyone calibrates on; and PAHdb, Mai and Bos supply
the scaled, simulated and ML-corrected DFT spectra for thousands of PAHs — what nobody has done is
to put these pieces together on a PAH: carry a frozen local coupled-cluster space along the modes,
recover the correction from energies alone, and measure an error margin per band (§3.1 and §14
carry the references and their reading status). And why the harmonic part rather than the
anharmonic one that PAH spectra are known for: because the only figure that exists on this ladder
— benzene, from the supervisor's own group (Esposito et al. 2024, Table S1) — puts the B3LYP/N07D
harmonic frequencies 5.45 cm⁻¹ from CCSD(T)-F12b on average, an error that passes one-to-one through
VPT2 into every fundamental, is systematic per band family rather than random, and is absorbed only
in its mean by a fitted scale factor; the anharmonic constants stay at DFT level exactly as in that
protocol, the Δ₂ = 0 null row of §7 separates what the coupled-cluster correction adds from what the
anharmonic step does, and whether the same is true at naphthalene, where no such figure exists, is
precisely what R1 measures per family (decision 28) — if the correction adds nothing there, the
answer is reported as such.

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

Seven measurements and three literature findings have been made since the plan was written,
between 5 and 12 September, all on the student's laptop. A
DFT-only rehearsal of the probing machinery (a difference between two DFT functionals standing in
for the coupled-cluster correction) recovered a full force-constant correction at benzene and
showed where the couplings really are. The frozen correlation spaces on which the whole design
rests were measured to be smooth: their energy scatters by 0.002–0.06 µE_h along a displaced mode,
where the same local-CC program re-selecting its spaces at every geometry scatters by 7–11 µE_h at
its default settings and 0.05–2.7 µE_h at tight ones. At the anchor basis the frozen object stays
as smooth; at the tight local-correlation thresholds it carried a frequency bias of up to 0.8 cm⁻¹
on the C–C stretch, and the same scan with the thresholds one decade tighter, finished on 12
September, brings that to +0.11 / −0.01 / +0.23 cm⁻¹ on the three modes with the smoothness unchanged
(§3.3) — the residual was local-correlation truncation, and the anchor runs at those thresholds. The cheap basis line printed the same day (SCF and MP2 at the same 27 points in larger bases, nineteen minutes) showed the anchor's remaining distance from its own basis-set limit to be an order of magnitude larger than that residual, and the anchor was redefined as a composite that carries the SCF and MP2 basis terms at under 1 % of the cost (decision 33). And the canonical coupled-cluster reference that
licenses the anchor was timed: it fits the laptop at benzene for the line that matters, and the
full canonical Hessian does not. The search found no gas-phase spectrum of known temperature for
chrysene or triphenylene in the 6–15 µm region, and for pyrene only a hot heat-pipe spectrum and
one cold band, which fixes what that rung can and cannot decide.

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
over DFT. On the pyrene-size and coronene rungs the pipeline's positions are compared per band
family against named, version-frozen state-of-the-art predictions under a pre-registered protocol,
wherever the laboratory can decide; on the largest species the deliverable is a spectrum with a
labelled error budget and no accuracy claim. The project is as much about the evaluation discipline —
pre-registration, frozen baselines, mandatory null tests, fail-closed reporting — as about the
spectra themselves.

### Provenance, reviews, and the words this document uses

*Reviews.* The plan was put through eight review passes on 3 and 4 September: four "cold reads"
by a reader who saw only the documents and a brief, and four adversarial domain reviews with
literature access. **These were performed by an AI assistant (Claude), each pass in a fresh
session that had not seen the author's reasoning; they are a disciplined self-review with an
outside vocabulary, not human peer review.** Every finding and its closure is on file in the
folder. This document itself was cold-read the same way on 6 September and again on 8 September (the second
time by a reader placed in the supervisor's position); the 8-September findings — 43, four of them
blocking — were addressed on 10 September.

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
**K** is the number of coupled-cluster energies a molecule needed; **K_off** the part of it spent
on the off-diagonal block. The **pilot note** is a dated document, written before the first real
coupled-cluster correction is computed, that fixes every tolerance, margin and constant the
evaluation uses. A **beat margin** is the pre-registered minimum per-band improvement over the
best opponent that counts as a win (used from naphthalene's families upward; on benzene the test
is agreement, decision 28). Numbered **decisions** are the student's recorded choices (§10). The
**licence rungs** are benzene and naphthalene, the two rungs whose measurements license the anchor
and the recovery for the rest of the ladder. **Module 05** is the deep-learning predictor of where
the correction has large couplings and **Module 06** the generative proposer of displacement decks
— both efficiency experiments on DFT-only corpora (§6, §12). The **campaign officer** (Module 07)
is a rule-checking agent that reads the deck, the budget file and the pilot note, submits and
refuses computational jobs and report sentences by those rules, and never produces or edits a
scientific number.

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
no PAH precedent) puts the
coupled-cluster level in the **harmonic** constants and leaves cubic and quartic constants at DFT
level. Plan 04 had it the other way round. Plan 05 corrects the harmonic force constants only —
Δ₂ — and lets DFT supply the anharmonic constants. The domain review sharpened this further:
the probe set specified here — single- and paired-mode displacements at two amplitudes — cannot
produce the three-index cubic constants φ_ijk that PAH combination-band resonances need (quartic
force fields obtain them from energies at three-mode displacements, at coupled-cluster cost ruled out
above), so a coupled-cluster anharmonic correction was not merely unnecessary but unbuildable with
the probes specified. It was removed from the promised set. A cheap by-product
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
recovery fails on pyridine's ring modes by up to ±28 cm⁻¹ and leaves residuals up to 5 cm⁻¹ on
benzene, pyrrole and furan, because DFT and coupled-cluster mode compositions differ there — is the
strongest evidence for the plan's design choices. What plan 05
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
| coupled-cluster force constants along DFT normal modes from energies; selected off-diagonals; symmetry-forbidden couplings zeroed in the full matrix | Concordant Mode Approach (Lahm et al. 2022; Kitzmiller et al. 2024; Olive Dornshuld et al. 2026, read in full: 17 intermolecular complexes, MP2 normal modes in a heavy-augmented triple-zeta basis, CMA-2A converges with 3 % of the off-diagonals; its persistent benzene outlier is one same-representation ring-deformation coupling, the same phenomenon our rehearsal found) | the target is the *difference* Δ₂, not the CC force constants; the off-diagonal block is recovered as a whole from multi-mode patterns, not element by element; symmetry used as the recovery prior rather than as a clean-up; local rather than canonical coupled cluster, at PAH sizes |
| recovering a Hessian from few measurements by exploiting its structure | compressed sensing in a cheap method's eigenbasis (Sanders et al. 2015); O1NumHess (Wang et al. 2025) | applied to a difference Hessian rather than a full one; the prior is the molecule's symmetry, parameter-free, instead of generic sparsity; the probe count is a measured, pre-registered quantity |
| correcting DFT towards CCSD(T) by learning the difference | Δ-machine learning of potential-energy surfaces (transfer learning to CCSD(T), Käser, Boittier, Upadhyay & Meuwly 2021 — read in full 10 September: 262–632 CCSD(T) geometries with energies, gradients and dipoles, ≈ 5 % of an MP2 set, on 7–9-atom molecules, harmonic MAE 0.1–1.1 cm⁻¹ against explicit CCSD(T), no aromatic; and Lam, Abdul-Al & Allouche 2020 — read in full: B2PLYP harmonic part kept, cubic and quartic constants from a neural network trained on 24N single points, 37 molecules including benzene and naphthalene, RMSD 21 cm⁻¹ against full B2PLYP — the harmonic part stays at DFT level) | nothing is learned per molecule; the difference is measured; a learned model is a possible follow-up gated by the measured range (§6) |
| local-correlation spaces held fixed for numerical derivatives | **domain freezing and domain merging along a potential-energy surface (Mata & Werner 2006, J. Chem. Phys. 125, 184110, DOI 10.1063/1.2364487 — Crossref-verified 10 September, full text closed and asked of the supervisor; as described by Pinski & Neese 2019) — holding local-correlation domains fixed across geometries is 2006 prior art, found on 8 September after the first search missed it**; the discontinuity problem itself (Russ & Crawford 2004; Madriaga & Crawford 2025); residual smoothing (Subotnik & Head-Gordon 2005); fixed domains for DLPNO-MP2 numerical derivatives (ORCA) | frozen LNO-CCSD(T) fragment spaces transported by projection across displaced geometries, semicanonicalised, with the smoothness and bias measured against canonical CCSD(T) — no publication found that does this or measures it |
| scaled, ML-corrected or anharmonic DFT for PAH spectra | PAHdb v4.00 (Ricca et al. 2026); the PAHdb Anharmonic library v1.00 (Mackie et al. 2015, 2016; Esposito et al. 2024); Mulas et al. 2018; the ML-corrected scale factors of Bos et al. 2025 (marketed as Ethereal AI) | these are the opponents; the plan adds a measured coupled-cluster correction to the harmonic constants and an error budget per band, and leaves the anharmonic constants at DFT level as they do |
| selected high-level vibrations from a cheap guess, without the full Hessian | mode-tracking (Reiher & Neugebauer 2003, read in full: Davidson subspace iteration on gradient derivatives, cheap-method guess, CCSD(T) refinement named as the intended use) | the target is the correction to the whole force-constant matrix from energies, under a symmetry prior, with the probe count measured — not a set of converged eigenvectors |

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
noise; the naphthalene rehearsal repeats the test at 48 modes before the R1 deck is built, and
until then the banded rule remains the fallback for that rung. It also sets the cost expectation
(decision 13): without a prior the off-diagonal block costs about M(M−1)/2 energies for M modes —
the benzene rehearsal needed 388 off-diagonal energies for 435 unknowns (§8), so sparsity as such
saved nothing; under the symmetry prior benzene has **57** same-representation pairs — 54 under a
strict D₆h assignment (2a₁g + a₂g + a₂u + 2b₁u + 2b₂g + 2b₂u + e₁g + 3e₁u + 4e₂g + 2e₂u), plus
three from the accidentally degenerate a₁g/b₁u block at 1020 cm⁻¹, whose two DFT eigenvectors are
mixed and carry both labels; 11 of the 57 lie within blocks grouped as degenerate, ten true pairs
and that one and the rerun on the same responses reached the same threshold at **210** off-
diagonal energies (10 September) — and with the symmetry prior naphthalene has **141** same-
representation couplings instead of 1,128 (the deck's own analysis; the count is reproduced by the
standard D₂h assignment of its 48 modes, 9a_g + 3b_1g + 4b_2g + 8b_3g + 4a_u + 8b_1u + 8b_2u +
4b_3u). The representation of each mode is determined by the deck's own symmetry analysis in the
molecule's **full** point group: DFT programs run in Abelian subgroups (benzene in D₂h, where its
degenerate modes split artificially — Esposito et al. 2024 note the same), and their labels would
leave far more couplings free than symmetry does. Zeroing symmetry-forbidden couplings is itself
standard practice — the Concordant Mode Approach does it as a clean-up of its full high-level
matrix — what is new here is using it as the prior of a recovery from few measurements. The
arithmetic, at benzene's measured per-energy time of 35 minutes in the anchor basis (naphthalene's is longer: **measured 11 September, 11.5 h per energy at 19.8 GB peak memory on the laptop, against 35 minutes for benzene**). Two numbers, with different roles. The **deck**
at R1 is the probing licence's reference (§5.1): 48 modes × 2 diagonal energies, the 48 second-
amplitude points, and every one of the 141 same-representation pairs measured directly as a ± two-
mode point — 96 + 96 + 282 = **474 energies**, about 280 hours at benzene's 35 minutes per energy and **5,450 hours — 227 days — at naphthalene's measured 11.5 hours**, which is the figure §12 and P13 carry (measured at the tight local-correlation thresholds; the anchor now runs one decade tighter, decision 20, and the naphthalene energy at those thresholds was launched for timing on 12 September and is owed; the benzene factor suggests about twice, and its memory may exceed the laptop, in which case that timing is the first job of the machine P13 chooses). **K**, what the stopping rule
reports (K = 2M + K_off; the second amplitude sits outside it), is smaller: 96 diagonal energies
plus between 0.9 and 2.0 energies per allowed coupling — 0.9 is the no-prior benzene rate (388 for
435 unknowns), 2.0 is the cap at which every pair is simply measured; the benzene rerun under the
prior needed 3.7 per pair, but on a deck built for the banded rule in which only 12 of the 57
allowed pairs had a two-mode pattern, which is why the R1 deck is built for the prior — so K is of
order 220–380 energies, against about 1,400 energies and 800+ hours without the prior. By the 168-hour rule of §8 the R1 deck on the laptop would be thirty weekly batches: on the measured number R1 is **cluster work**, or the work of a dedicated many-core machine; the choice is P13, open and now decidable. The prior is what
brings the energy route at naphthalene within reach of this machine at all; it does not make it
cheap.

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

- *Design.* Benzene, cc-pVDZ, three normal modes — the totally symmetric ring mode at 1020 cm⁻¹; a
  non-degenerate C–C stretch at 1357 cm⁻¹, which belongs to the same irreducible representation as
  the 1186 cm⁻¹ mode it couples to in §3.2; and one component of a degenerate C–H out-of-plane
  pair at 865 cm⁻¹ (B3LYP/6-31G* harmonic values; the degenerate partner sits at the same
  frequency) — at nine displacements each; three arms at every geometry: **A**, the frozen spaces
  transported from equilibrium; **B**, the equilibrium localised orbitals transported but the
  fragment spaces re-selected; **C**, everything re-selected (the program as released). Two
  settings of the program's truncation thresholds ("default" and "tight"; a third, one decade
  tighter, on 12 September). A canonical CCSD(T)
  energy at each of the 27 geometries as the truth line. - *Smoothness.* Against that truth line,
  arm A's energy scatters about a smooth curve by **0.002–0.06 µE_h** on the three modes at either
  threshold setting; arm C by 7–11 µE_h at default and 0.9–2.7 µE_h at tight thresholds, arm B 0.05–1.2 µE_h at
  tight. The requirement the couplings impose (§3.4) is about 2 µE_h; arm A meets it by a factor
  of 30 to 1,000 depending on the mode. - *Bias.* The frozen space was chosen at equilibrium and
  fits a displaced geometry slightly less well; that bias is a clean quadratic in the
  displacement, i.e. exactly a curvature bias, and it shrinks with the truncation threshold:
  2.6–14 cm⁻¹ on the bare local energy at default thresholds; **0.25–1.3 cm⁻¹** on the composite
  energy — the local energy plus the standard second-order correction for the truncated space,
  [MP2(full) − MP2(local)], as pyscf-forge's own corrected energy defines it — at default
  thresholds; **0.015–0.18 cm⁻¹** on the composite at tight thresholds. The pipeline's anchor ran
  at tight thresholds until 12 September; it now runs one decade tighter (decision 20, below); the
  threshold-sensitivity line of §7 still decides, per rung, whether that is enough or extrapolation in
  the truncation thresholds is required. - *Reload.* Arm A reproduces
  the equilibrium-geometry energy exactly and reloads its spaces from file exactly (to 10⁻⁴ µE_h),
  which is the property the pipeline depends on. - *Arbitrariness made visible.* Two runs at the
  same displaced geometry landed the fresh localiser on different, symmetry-equivalent orbital
  sets (overlap between the two landings 0.67), while the transported set stayed put; on benzene
  the two landings cost nothing, on a molecule of lower symmetry they would not be equivalent.
  This is the effect the domain review asked about and the reason the plan transports rather than
  re-localises. - *Anchor basis.* The same scan at cc-pVTZ, the basis the licence rungs use — the
  three arms at tight thresholds, 27 geometries, then its own canonical truth line — finished on 8
  September (three arms 1.7–2.0 h per geometry, canonical 14–21 min; 58 h in all). The frozen
  object stays smooth (0.002–0.021 µE_h), but its composite frequency bias grows with the basis:
  +0.47 cm⁻¹ on the out-of-plane mode, +0.03 on the ring mode and +0.79 on the C–C stretch,
  against +0.07, +0.015 and +0.18 at cc-pVDZ in the same order (all bias figures in this document
  were halved on 10 September: a curvature difference in the dimensionless coordinate is twice the
  frequency shift, and earlier versions reported the curvature), with the smallest singular value
  of the transported virtual space against the fresh one being 0.36 at the out-of- plane endpoint,
  0.66 on the ring mode and 0.57 on the C–C stretch — the bias is not a monotonic function of that
  overlap across the three modes, so the mechanism is not settled by this scan. The bias is a pure
  curvature term (the quartic coefficient is zero on every mode) and enters Δ₂ directly. What to
  do with it — record it as a measured floor, enlarge the frozen virtual space and re-measure, or
  calibrate it per mode where a canonical reference exists — was decided on 8 September: measure
  first. The same scan with the local-correlation thresholds one decade tighter (the frozen arm
  only; the other two arms and the truth line stand) started that evening, died with the terminal
  session after 5 of 27 geometries (which is why long runs now launch detached from the session),
  was resumed from its saved points on 11 September at 05:16 and **finished on 12 September at 11:48**
  (27 points, about 75 minutes each for the frozen arm alone). **Result (decision 20, read the same
  day; `probes/results_m1/XTIGHT_READIN.md`):** the composite frequency bias falls from
  +0.47 / +0.03 / +0.79 to **+0.11 / −0.01 / +0.23 cm⁻¹** (out-of-plane, ring, C–C stretch), the
  bare LNO bias from +16.3 / +1.8 / +5.3 to +2.1 / +0.2 / +0.8, and the smoothness stays at
  0.003–0.044 µE_h — so the residual at the tight thresholds was local-correlation truncation, not
  transport, and **the anchor object runs at the tighter thresholds**; the cost record carries the
  factor, which at benzene is about 2 (4,576 s against ≈ 2,200 s per frozen-arm point; the result file's
  "×0.7" compares with the tight scan's 6,441 s per point, which ran arms B and C as well — arm A alone
  was 2,160 s at the reference point) and at
  naphthalene is owed as a timed energy before the R1 deck is priced (the 11.5 h of §8 is the tight
  figure). Per-mode calibration is not needed (research note P10, decision 20). - *The basis-set line,
  second input (decision 26 (ii), printed 12 September 12:13; `probes/results_m1/BASIS_LINE_scf_mp2.md`):*
  DF-RHF and DF-MP2 at the same 27 points in cc-pVQZ, DF-RHF in cc-pV5Z — 19 minutes in all. The
  SCF part of the curvature moves by +1.8 / −2.4 / −4.6 cm⁻¹ from TZ to QZ and by +3.8 / −2.8 / −3.1
  to 5Z (against +44 / −22 / −51 from DZ to TZ): nearly converged. The MP2 correlation part still
  moves by −1.0 / −2.4 / −8.0 cm⁻¹ from TZ to QZ (against +15 / −12 / −16 from DZ to TZ). **The
  anchor's distance from its own basis-set limit is therefore an order of magnitude larger than the
  frozen-space bias just measured** — the largest known term in Δ₂'s budget at benzene, and the
  cheapest to carry. **P18, decided the same day (decision 33):** the anchor energy per point is the
  existing composite plus [MP2/QZ − MP2/TZ] + [SCF/5Z − SCF/TZ], every term a difference of computed
  energies at one geometry, no fitted parameter, under 1 % of an LNO point in cost; the licence
  comparison is unaffected (the terms are common to arm and reference); the measured effect on
  benzene's three probed harmonic frequencies is +2.8 / −5.2 / −11.1 cm⁻¹ — terms of the size of the
  whole DFT-to-CCSD(T) gap of §11 (5.45 cm⁻¹ at benzene), which is why they belong inside the anchor
  and not in a budget line; the CCSD(T)−MP2 remainder's basis change stays unmeasured until the
  canonical QZ line of the cluster request (research note, P18; Ladder §3). The local step stays at
  cc-pVTZ rather than cc-pVDZ plus the same composite because that remainder itself moved by about
  5–8 cm⁻¹ from cc-pVDZ to cc-pVTZ on the probed modes (research note §2.2d) — a shift the composite
  cannot carry. - *A definition
  fixed by the measurement.* The transported orbital blocks must be semicanonicalised at each
  geometry — a rotation inside the frozen space that the fragment solver's MP2 start and (T) step
  assume; a first run without that step read a spurious bias of up to 147 cm⁻¹ and is kept on file
  as the record of the error (decisions 14, 15).

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
probing of a 432-atom molecule with energies only costs, under this protocol, four energies per
vibrational mode for the diagonal alone — 5,160 coupled-cluster energies of a very large molecule,
before a single coupling — and is not attempted. The only
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
   that is not yet chosen**; the DFT engine is psi4 1.11 (the rehearsal's Hessians ran there), the
   anchor is pyscf-forge's LNO-CCSD(T) in PySCF 2.14, and the VPT2 implementation is a pilot-note
   constant with its candidates recorded in the bibliography — the null row of §7 separates this
   pipeline's anharmonic step from the correction inside the pipeline, and is commensurate with
   line B only if the production level is B3LYP/N07D with a polyad treatment of the same kind,
   which is why §13 item 13 asks which level counts as the same footing. The level is fixed, from
   the opponents' levels and the anharmonic literature (the PAHdb-anharmonic standard is
   B3LYP/N07D with a 200 × 974 integration grid, Esposito et al. 2024; the CMA studies find basis
   quality to matter more than correlation level for the normal-mode basis; aug-cc-pVTZ is
   excluded for benzene-type rings by a documented linear-dependence artefact — the spurious 495i
   cm⁻¹ ring-puckering frequency reported by Olive Dornshuld et al. 2026), before the naphthalene
   rehearsal runs, so that the rehearsal constants the stopping rule uses (§3.4) and the noise-
   injected column of the pilot note are read at the production level; the benzene rehearsal so
   far used B3LYP/6-31G* against BHHLYP/6-31G*, and the Module-05 corpus factory computes both B3LYP and ωB97X (the QM9 layer is ωB97X as served). The choice is
   recorded in the pilot note with its reasons.
2. **Δ₂-probing.** The deck of displacement patterns; at each, the composite local coupled-cluster
   energy in the frozen spaces of §3.3 and the DFT energy; recovery of Δ₂ in the DFT normal-mode
   basis under the symmetry prior of §3.2; K read by the stopping rule of §3.4. Three licences
   gate it: an **anchor licence** against the noise, bias, basis-set and threshold-sensitivity
   formulas fixed in the pilot note (§7); a **probing licence** at benzene and naphthalene against
   directly computed reference corrections — at naphthalene the reference is the full deck itself,
   every same-representation pair measured directly as a ± two-mode point, against which the
   recovery from the hashed prefix is judged; at benzene it includes a canonical coupled-cluster
   reference, the only one independent of the space freezing; and a **locality test** computed on
   directly measured Hessian blocks — never on the recovered correction alone, which could certify
   the locality its own prior imposed. Modes that are infrared-inactive by symmetry are not
   dropped — their diagonal is cheap and their fundamentals reach the spectrum through resonances
   — but the coupling blocks made only of inactive modes are tested per rung in the DFT rehearsal
   and left out of the deck only where the scored positions do not move (decision 19). (Each
   mode's diagonal costs two energies inside K — a ± pair — and two more at the second amplitude
   that sit outside K and yield the cubic by- product, §3.4.)
3. **Spectra** by second-order vibrational perturbation theory with explicit resonance treatment
   (GVPT2; the implementation is pinned in the pilot note as a pre-registered constant, with named
   resonance thresholds and a polyad cap; from the pyrene-size rung upward the anharmonic
   constants are built in reduced dimensionality — Hessians differentiated only along the scored
   modes and the partners a dimensionless coupling indicator and the Darling–Dennison test select,
   after Fusè et al. 2024, whose thresholds are pilot-note candidates — on the DFT anharmonic
   constants and the Δ₂-corrected harmonic part, plus a first- order geometry term: the corrected
   surface's own minimum shifts slightly from the DFT one, by the coupled-cluster force at the DFT
   geometry — the odd part of the same single-mode ± pairs whose even part gives the diagonal, so
   it costs nothing extra — divided by the corrected curvature, and that shift is applied and
   printed on every scored band); **no scale factor** on anharmonic output. Every spectrum carries
   positions, anharmonic intensities from the DFT dipole derivatives (the same physics PAHdb's
   intensities rest on, computed anharmonically rather than harmonically) and a drawn width at the
   resolution and temperature of the source it is compared with, each labelled with its
   provenance.
4. **Error budget** per band: DFT level, held-out residual, measured noise and space-freezing
   bias, the anchor's **basis-set line** (decision 26: the measured cc-pVDZ → cc-pVTZ change of
   the canonical curvature, +67 / −33 / −73 cm⁻¹ on benzene's three probed modes, two thirds of it
   at the SCF level; the literature distance of CCSD(T)/cc-pVTZ from the basis-set limit once
   read; a canonical cc-pVQZ diagonal line in the cluster request — the 5.45 cm⁻¹ expected-effect
   figure of §11 is at a near-complete basis and is therefore an upper bound on what this anchor
   can buy) — of which the SCF and MP2 parts are carried inside the anchor since decision 33 (§3.3),
   leaving the basis change of the CCSD(T) − MP2 remainder as the open budget term —, the share of
   the family's correction that comes from couplings beyond the locality
   test's radius, and the matrix–gas shift where matrix data is used.

### 5.2 The size ladder (species and claim types unchanged from plan 04)

| Rung | Species | Type | What it licenses in plan 05 |
|---|---|---|---|
| R0 | benzene | agreement (decision 28): within the laboratory uncertainty plus the pipeline's own budget; the opponents are printed, not claimed | probing licence against local and canonical references; the anchor's bias and basis-set lines (canonical reference); intensities scored for agreement |
| R1 | naphthalene | agreement, plus the per-family question whether the correction adds accuracy over DFT | the noise measurement; the anchor licence closes; first locality read; intensities scored for agreement |
| R2 | pyrene, chrysene, triphenylene, tetracene | accuracy for the C–H out-of-plane families (hot gas, decidable by margin); the C–H stretch family is scored on the jet-cooled 3 µm column only once a scoring rule for its resonance polyads is agreed (§13 item 8) and is not counted as promised until then (decision 25); C–C families expected undecidable on the existing gas data, see below | first off-diagonal-count ratio; direct-block locality probe; a canonical diagonal check at pyrene (scaled from the measured benzene point: 620 against 264 basis functions at cc-pVTZ, N⁷ time and N⁴ memory give roughly 400 × 755 s ≈ 80 h and 30 × 7.3 GB ≈ 220 GB per energy, for 2 × 72 + 1 = 145 energies — cluster work by two orders of magnitude, classified by the rule of §8, and skipped with a printed sentence if no cluster time exists) |
| R3 | coronene | accuracy | second ratio; the numeric size sentence is decided here |
| R4–R5 | C₅₄–C₂₁₆ class | reach; the R4 fragment checks conditional on cluster access | expert-judgment datum (§13, item 5); the first rungs where the learned prior, if it earned its licence at R2–R3, may carry the recovery; the fragment-vs-whole comparison on a molecule larger than coronene and the fragment-radius convergence test |
| R6 | C₃₈₄H₄₈-class | reach | fragment-probed only, under a four-part measured licence (locality at R2–R3; coronene probed in fragments reproducing coronene probed whole; the same on a larger molecule where the cluster allows; a fragment-radius convergence test on the flake's own interior); otherwise a per-family or full refusal |

*Laboratory sources per rung.* Benzene: the NIST Quantitative Infrared Database cell spectra (Chu
et al. 1999), with calibrated intensities. Naphthalene: the PNNL quantitative vapour-phase record
at 0.112 cm⁻¹ and 25 or 50 °C — the methods state 25 °C, the introduction and the figure caption
50 °C; the record header decides — (Schneider et al. 2024, in the database described by Sharpe et
al. 2004), with calibrated intensities; Pirali et al. 2009's sixteen fundamentals at 0.005 cm⁻¹,
read at the Q-branch head with the hot bands resolved away, as a second labelled column (scored
with no temperature shift and a 0.5 cm⁻¹ head-to-origin term, since the fundamental is read
directly — decision 21); the hot NIST WebBook entries as labelled extra columns; Pirali et al.
2009 and Joblin et al. 1995 for the temperature term. Pyrene, chrysene, triphenylene: NIST WebBook
hot-vapour GC-IR spectra at 8 cm⁻¹ without concentration data, and, for the C–H stretch family
only, the jet-cooled 3 µm IR–UV ion-dip spectra of Maltseva et al. 2016 as a labelled cold column.
Tetracene: matrix isolation, plus a jet-cooled band list (Lemmens et al. 2019). Coronene: matrix
isolation, six jet-cooled 6–15 µm bands (Lemmens, Rijs & Buma 2021) as the primary cold column,
and the 770 K heat-pipe spectrum of Joblin et al. 1994 with the slopes of Joblin et al. 1995 as
the labelled hot column (decision 24). Chu 1999, Schneider 2024, Pirali 2009, Joblin 1994 and
1995, Lemmens 2019 and 2021, Mattioda 2020 and Brumfield 2012 were read in full (6 and 8
September) and their conditions transcribed; Maltseva 2016 is held at abstract grade and its band
tables are asked for (§13, item 8) (bibliography, "Readings of 2026-09-06 — laboratory sources").
Three readings changed numbers, not rules: the benzene intensities are not certified where water,
CO and CO₂ absorb (1325–1900, 2050–2225, 2295–2385 and 3550–3950 cm⁻¹), so the intensity score at
benzene excludes the C–C band near 1480 cm⁻¹; the hot-band slopes of Joblin et al. 1995 replace
the earlier recalled floor (the largest measured 6–15 µm slope is 0.044 cm⁻¹ K⁻¹, coronene's 6.2
µm band), and their model gives the room-temperature term per family; and the jet-cooled coronene
bands at 7.7 and 8.8 µm lie 10–19 cm⁻¹ from where the hot spectra of Joblin et al. 1994 and the
slopes of Joblin et al. 1995 put a cold band. The jet-cooled band is the pipeline's most direct 0
K observable, so it is the primary cold column with the laser bandwidth as its uncertainty; the
hot-extrapolated position is a second, labelled column, and a family is called inconclusive only
if the two disagree on the verdict (decision 24).

A per-family decidability rule replaces plan 04's rung-level gate: a gas-scored family is
decidable if the scoreboard's **measured band-centre uncertainty** — instrument resolution,
centroid precision and a temperature term — is smaller than its beat margin; a matrix-scored
family passes through the matrix–gas gate or is pre-declared inconclusive. Benzene and
naphthalene are therefore scored unconditionally on room-temperature cell spectra; the first
benzene scoreboard was printed on 10 September from the NIST Quantitative IR record at 0.125 cm⁻¹
(four IR-active fundamentals, integrated intensities agreeing between two records of the series to
≤ 1.3 %), and on it the temperature term is the pipeline's own computed 296 K shift with ±30 %
(decision 29), so the laboratory side of the R0 agreement test is a few tenths of a cm⁻¹, not the
2.6 cm⁻¹ a generic floor would give. For the
pyrene-size rung, a systematic search on 5 September (NIST WebBook, the PNNL database, PAHdb's
experimental library, and journal searches on jet-cooled and cell spectroscopy of each species)
found no gas-phase spectrum of known temperature for chrysene or triphenylene in the 6–15 µm
region; for pyrene it found the hot heat-pipe spectrum of Joblin et al. 1994 at 570 K (with the
8.5 and 12 µm slopes of Joblin et al. 1995 — the same two-column treatment as coronene's applies),
the jet-cooled 3 µm list of Maltseva et al. 2016 and one rotationally resolved cold band (Brumfield, Stewart & McCall
2012, read in full: origin 1184.0356 cm⁻¹, T_vib ≤ 111 K), all now named as labelled columns. The C–C stretching
families at R2 are therefore expected to be undecidable by construction (they carry the largest
temperature shifts and the smallest beat margins, so the GC-IR entries' unknown vapour temperature swamps them;
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
terms are frozen now (its milestones are numbered M2–M5 in the technical documents, continuing the
plan's numbering after probe M1; they are unrelated objects and are named here by molecule):

- **M2** (benzene; laptop): the engine version pinned and printed; the
  automatic-differentiation gradient with the frozen-space projection inside the differentiated
  graph agrees component-wise with central finite differences of the re-projected frozen-space
  energy; its smoothness along the same modes as probe M1 printed; the projection term of the
  gradient measured. M2 runs first at cc-pVDZ, where the canonical analytic gradient fitted the
  laptop (13.9 GB, §8), because at benzene every fragment spans the whole molecule and the
  memory argument above gives no relief there; the cc-pVTZ repeat is M3's first item, and a
  failure at cc-pVTZ that is memory-only (correctness and smoothness passed at cc-pVDZ) is
  recorded as such and does not by itself trigger the kill criterion (cold read of 8 September,
  finding 22). Passing M2 licenses the gradient route at benzene.
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

## 6. What this project deliberately does not do, and why

**No transferable, train-once spectrum model.** Plan 04's attempt to learn a correction on one
ring motif and reuse it on another failed its own transfer test, and that measured failure is the
reason every molecule gets its own probed correction. The Module-05 deep-learning component
predicts only *where* the correction is likely to have large off-diagonal elements, is trained on
a public-plus-own DFT-vs-DFT Hessian corpus (§8, §10 item 4), and enters a promised rung only after a licence: its saving
demonstrated on that corpus against the symmetry prior's free-element count, and its result
checked prior-free at that rung. The student ruled more generally that a rule inherited from an
earlier plan carries no authority of its own — knowledge transfer is allowed wherever a gate shows
it makes the pipeline succeed.

**The pre-registered route to the large PAHs (decision 27, 10 September).** Between the accuracy
rungs and the largest sizes stands one test, gate Q9, written before any correction at pyrene size
exists. For each band family — the C–H out-of-plane bands per hydrogen-adjacency class, the C–H
in-plane bends, the C–C stretches, the C–H stretches — the per-mode diagonal correction δω_F is
already printed on every accuracy rung; Q9 asks whether it is a per-family constant c_F, or at most
a one-parameter size law c_F + d_F/N_C, across benzene, naphthalene, anthracene, the four R2
species and coronene: eight molecules, five sizes, four topologies, no new coupled-cluster energy.
The test is leave-one-molecule-out; a family wins only if the transfer error is within its beat
margin τ_F on every R2 and R3 molecule and the family's members agree among themselves to the same
margin; a family that loses is never applied above coronene, and that sentence is written now. A
family that wins gives the large PAHs something the coupled-cluster arm cannot otherwise reach:
line A's positions for that family shifted by c_F with the held-out error as their error bar, shown
with provenance because no truth exists there, and one falsifiable prediction per family that the
fragment-probed C₃₈₄H₄₈ flake then checks. Expectations are recorded as expectations: transfer is
plausible for the C–H stretch and the out-of-plane classes, doubtful for the delocalised C–C
families. This is not plan 04's motif transfer — two parameters at most, across sizes, with the
losing condition first.

**The calibration check (decision 31, 10 September).** Small errors are not enough for a data
generator; the error bars must be true. For every scored band on R0–R3 the pipeline prints whether
the laboratory value lies inside k·u_total (k = 1, 2), with u_total the laboratory uncertainty
combined with the per-band budget, and reports the coverage per rung, per family and overall
against the nominal 68 % / 95 %; the pass thresholds are fixed in the pilot note before any
pipeline-vs-lab number exists, and a budget that falls short is declared incomplete and its deficit
reported — it is never widened afterwards to reach the nominal. That table, not the mean error, is
what would let a reader trust the pipeline's bands as training labels.

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

**Named follow-up, outside the sequence (decision 32, 12 September): the network as stand-out work.**
The student names the model of the previous paragraph as the project's stand-out ambition — a network
trained on the pipeline's own output, the Δ₂ blocks and certified band positions, to predict the
correction for a new PAH from its DFT steps alone — and places it deliberately **outside the module
sequence**, which still ends at Module 09 (the degree's rubrics carry no stand-out criterion in
version 1.5.1; the label is the student's). It is not in the promised set and not in §1. It becomes a
dated follow-up proposal only if two measured conditions hold: (i) the range of the correction
measured at R2–R3 is short enough that a transferable model can exist at all, and (ii) the Q10 coverage
table above (decision 31) is in order for the families the model would be trained on, so that the pipeline's bands
qualify as training labels. Its losing condition is written now: on a middle rung the network's
prediction must agree with the probed Δ₂ per family within τ₇, as the Module-05 prior must, before it
is trusted on a higher one; if it does not, the pipeline remains a per-molecule measurement and the
follow-up is closed with that sentence. The Module-05 corpus factory (§10, item 4; the dated note in
the mapping) and the Q9 transferability test (decision 27) are the two instruments that would feed
it; nothing else is built for it before the conditions are met.

**No promised coupled-cluster anharmonic correction** (§2; the diagonal cubic by-product is
reported, not applied). **No coupled-cluster correction to intensities** (§7). **No predicted band
widths** (§7). **No full coupled-cluster surface or global quartic force field.** **No new
empirical scale factors** (the in-house calibrated-harmonic baseline is an opponent, not the
method). **No light–matter dynamics and no new emission model** (the emission cascade model of
Mulas et al. 2018 is inherited post-processing where an emission spectrum is drawn). **No species
identification in JWST spectra.** **No sub-tolerance accuracy language.** **No whole-molecule
probing at C₃₈₄H₄₈** (§4).

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

**Opponents (frozen baselines), named and versioned:**

| Line | What it is | Version / reference | Where it competes |
|---|---|---|---|
| A | PAHdb computed library: scaled-harmonic DFT | v4.00; Ricca et al. 2026 | every rung except R0 — the library as served (parsed 10 September: 10,749 species) has **no benzene entry**, so line A's column at R0 — where the comparison is printed and claims nothing (decision 28) — is empty by construction; C₃₈₄H₄₈ is present (uid 617) |
| B | anharmonic DFT quartic force fields: the **PAHdb Anharmonic library v1.00** (45 spectra, C₆H₆ to C₁₈H₁₂; B3LYP/N07D quartic force fields, VPT2 with symmetry-based resonance polyads in SPECTRO — the protocol of Mackie et al. 2015, 2016 and Esposito et al. 2024) and, for pyrene and coronene, Mulas et al. 2018 (B97-1) | v1.00 (1 July 2026); Mackie et al. 2015, 2016; Mulas et al. 2018 | every accuracy rung where a species is present (R0–R2 from the library, R2–R3 from Mulas) — as served (parsed 10 September): benzene, naphthalene, pyrene and tetracene on the ladder; chrysene, triphenylene and coronene absent |
| C | machine-learning molecular dynamics trained on DFT, temperature-dependent, to C₂₁₆ | Mai et al. 2025 (MNRAS 541, 3073) | where coverage overlaps; theory-vs-theory on reach rungs |
| in-house | the **calibrated-harmonic baseline** (Module 04): a per-band ML correction to scaled-harmonic DFT, trained leave-molecule-out on laboratory residuals, after the ML-corrected-scaling approach of Bos et al. 2025 | built in this project, frozen before scoring | every accuracy rung |

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

**A conflict of interest, on record.** The supervisor is a co-author of the 2015 and 2016 papers
behind line B and of the jet-cooled 3 µm spectra named as an R2 column (Maltseva et al. 2016). The
protections are the ones already written — the frozen version, the pre-registered margins, the
Δ₂ = 0 null row, the leakage rules, the fail-closed reporting — and the supervisor's role on line B is
advisory on protocol facts (§13, items 11–15), never on margins or verdicts.

**Frozen comparisons and the pilot note.** Paired per-band absolute error on identical laboratory
bands; band lists, windows and margins frozen in the pilot note, which is written with seven
inputs in hand and **nothing else**:

1. the laboratory side with its measured band uncertainties — **printed for benzene (10 September, two NIST records) and for naphthalene's resolved fundamentals (11 September, Pirali 2009, u_band 0.50–0.71 cm⁻¹)**; the PNNL naphthalene record and the R2/R3 columns owed;
2. the opponent side — exists (versions named above);
3. the DFT-only rehearsal with its noise-injected column — exists for benzene (5 September);
   naphthalene owed;
4. the frozen-space probe M1 — exists (5–8 September; cc-pVDZ and cc-pVTZ scans with canonical truth lines; the xtight frozen arm, 27 points, and the DF-RHF/DF-MP2 QZ/5Z line on 12 September);
5. the canonical feasibility probe — exists (5 September);
6. a run/no-run check of which local-CC codes produce an analytic gradient at the anchor level
   at the equilibrium geometry, with memory — owed;
7. the naphthalene noise measurement (four modes × nine points × two arms — arm A, frozen
   spaces, and arm B, re-selected spaces on the transported orbitals — = 72 energies; the noise
   is the scatter about a smooth fit, no canonical line existing at naphthalene) with its fitted
   coefficients sealed — owed.

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
frequency change between the program's tight and default truncation thresholds — that, if
breached, makes extrapolation in the LNO truncation thresholds (the analogue, for this program, of
the complete-PNO-space extrapolation of Altun et al. 2021, who measured the local error on acenes
growing linearly with ring count and reduced it four- to five-fold by extrapolation) mandatory at
double cost. The probing licence and the locality test have their own tolerances, all bounded by
the smallest beat margin.

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
and are forbidden in any budget sentence. The following were printed between 5 and 12 September on
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
  geometry and 2.5 days in all; the xtight frozen arm alone 27 points at about 75 minutes each
  (12 September), and the DF-RHF/DF-MP2 cc-pVQZ and DF-RHF cc-pV5Z line 19 minutes for 54 points.
- **The canonical reference.** Canonical CCSD(T) energy of benzene: 27 s at cc-pVDZ, **755 s and
  7.3 GB at cc-pVTZ** on the idle laptop at the equilibrium geometry (850–1,270 s at the displaced
  geometries of the scan, with the laptop in use). Local LNO-CCSD(T) energy at cc-pVTZ: 2,087 s for benzene (locality pays only at larger molecules) and **41,375 s — 11.5 hours — for naphthalene at tight thresholds, 24 fragments, peak memory 19.8 GB against the laptop's 22 GB ceiling (11 September)**; pyrene will not fit this laptop's memory. The anchor's bias line — 61 canonical energies along benzene's 30 modes — is
  therefore 13–21 hours and **fits the laptop**; the full canonical reference Hessian by
  energies (1 + 2·30 + 4·435 = 1,801 energies, about 378 hours) **does not**, and neither does the
  gradient branch: a canonical CCSD(T) gradient of benzene costs 1,399 s and 13.9 GB at cc-pVDZ —
  about fifty energies — and at cc-pVTZ it did not complete within the 22 GB ceiling (its memory
  scales roughly with the fourth power of the basis size, (264/114)⁴ ≈ 30, i.e. hundreds of GB). The full canonical Hessian at benzene is cluster work; the probing licence was written
  to test the recovery without it. **The canonical reference at benzene therefore consists of**
  the 61-energy diagonal line (the anchor's bias line) and the canonical two-mode points of
  decision 16 for the off-diagonal bias; the probing licence's full-matrix comparison is against
  the directly computed local-CC reference with the same frozen spaces.
- **The Module-05 corpus.** A B3LYP Hessian of a QM9-size molecule takes 3–7 minutes here, so the
  conjugated QM9 subset (6,055 molecules, B3LYP side only) is about three weeks of laptop time; the own
  aromatic layers prepared on 12 September (45 + 868 + 4,353 candidates, both functionals, up to 34
  atoms; naphthalene 13 minutes and pyrene 54 minutes per Hessian here) are priced by a five-molecule
  timing test before any size is committed — the factory runs start-and-stop and never beside an anchor
  job (§12, Module 05 row; `modules/05_support_predictor/corpus/`).

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
re-read those closures (the re-checks of the earlier closures held with one exception, re-patched and re-read in the
fourth round; the counts are in the review files) and changed the design in seven
places, all in the text: paired displacements so that the coupled-cluster force at the DFT
geometry cancels; frozen spaces transported by projection rather than re-localised; only benzene
scored unconditionally until the room-temperature naphthalene source was found; noise injected
per energy in the rehearsal; the shared reference energy's offset identified from a second
displacement amplitude (§3.4); the first-order geometry term on every scored band (§5.1); and the
PNNL naphthalene source itself.

The review loop was **closed on 4 September** after a consistency check of the last revision (19
cross-references, all mechanical). Since then the plan's text changes only by dated notes that
name a measurement or a decision; the decisions of 5–12 September (§10, items 8–34) are such notes.
Items 8–16 and 19 were made on the DFT-only rehearsal, the frozen-space probe and the timings —
before any coupled-cluster response of the real correction exists, so none of the rules the
evaluation depends on was shaped by a result it will judge; items 17 and 18 are tooling and scope
choices; items 20–34 are readings of measurements (20, 26, 33), laboratory-source rules (21, 24,
25, 29, 30) and pre-registrations (27, 28, 31, 32, 34), all made before any coupled-cluster response of
the real correction exists. The remaining risk is retired by
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
    anchor runs at the tighter thresholds, cost factor ≈ 2 at benzene, naphthalene factor owed**).
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
    request; the expected-effect line is an upper bound at the anchor's level. *Input (ii) printed 12
    September:* the cheap TZ → QZ/5Z line shows the SCF part nearly converged (2–5 cm⁻¹) and the MP2
    correlation part still moving by 1–8 cm⁻¹ — see P18 in §3.3.
27. **The per-family transferability test Q9** (parked 8 September, unparked 10 September): the
    route from the accuracy rungs to the large PAHs is a pre-registered leave-one-molecule-out test
    of the diagonal correction per band family across benzene–coronene plus anthracene, with the
    losing condition written first (§6; research note of 8 September); it runs after R3 and before
    any R6 probe; no new coupled-cluster energies.
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
32. **The network as named stand-out work, outside the sequence** (12 September): a model trained on
    the pipeline's own Δ₂ blocks and certified bands is the project's stand-out ambition, gated by the
    measured range at R2–R3 and the Q10 coverage table, with its losing condition pre-written; not in
    the promised set, not a Module 10 — the sequence ends at Module 09 (§6).
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
    changes until the comparison is won.

## 11. Risks

1. **Frozen-space energies are not smooth enough for energy-only probing.** Measured at benzene in
   cc-pVDZ: they are, by a factor of 30 to 1,000 (§3.3). Remaining exposure: the anchor basis — measured 8 September: smooth (0.002–0.021 µE_h) with a
   frequency bias of +0.47 / +0.03 / +0.79 cm⁻¹ (out-of-plane, ring, C–C stretch) at tight
   thresholds, **+0.11 / −0.01 / +0.23 cm⁻¹ at the thresholds one decade tighter (12 September;
   decision 20 closed: the anchor runs there, at about twice the per-point cost)**
   — and larger molecules (the naphthalene noise measurement). Response where a measurement
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
   fitted scale factors absorb the signed mean of the harmonic difference; the mean absolute
   difference that Esposito et al. 2024 (§14) measured for benzene: B3LYP/N07D against CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies,
   mean absolute difference 5.45 cm⁻¹ (their Table S1; benzene only, read in full 6 September);
   what remains to buy is the per-family scatter. Response: the expected-effect line is
   written into the pilot note before any result, and losing is publishable.
5. **Laboratory decidability.** The per-family rule pre-declares undecidable families
   inconclusive. The pyrene-size rung's C–C families are in that class on every source the search
   found; the cold jet-cooled lists for tetracene and coronene are scored as labelled columns.
   Only a new gas-phase source changes this (§13).
6. **Off-diagonal probing is expensive without a prior.** Measured: 0.9 energies per unknown at
   benzene without a prior (388 for 435); under the symmetry prior 210 for 57 allowed pairs on a
   deck not built for it, with 2.0 per pair the cap on a deck that is (§3.2). Response: the symmetry prior (decision 11) with its per-rung free-element count printed
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
(Module 06; it proposes decks on DFT-only corpora *before* hashing — a proposed deck is hashed like
any other and never reordered after an energy exists) — are efficiency experiments on the off-diagonal probe count, run on DFT-only corpora
at zero coupled-cluster cost and measured against the symmetry prior's free-element count; the
deep-learning model is measured on the accuracy rungs and, if it earns its licence there, becomes
load-bearing on the reach rungs — the mapping says exactly that rather than pretending otherwise.
Module deadlines are administrative facts; a module may ship a fail-closed state to meet its
date, and the science continues past it.

**Calendar (set 10 September 2026, from the first week's measured pace; the first date is the
Monday the proposal is sent, every date after it is a Friday, and each means "delivered in full or in its fail-closed state").** The pace-setting quantities are the
laptop's serial compute (one anchor job at a time; a benzene cc-pVTZ scan is two days, one naphthalene LNO-CCSD(T) energy **11.5 hours, measured 11 September, at 19.8 GB peak memory**), the student's evenings and weekends for
decisions, and the supervisor's reading time around this proposal and around the cluster request
(one to two weeks each assumed). The first week also showed that each measurement brought one
correction with it (semicanonicalisation, the frozen-core count in the timing probe, the factor 2,
the basis set); one round
back per module is budgeted, not hoped away.

| Milestone / module | Content | Date | What sets the pace |
|---|---|---|---|
| Proposal to the supervisor | after the tighter-threshold scan, the basis line and the cold-read round — **sent as a scheduled e-mail for Monday 14 September, 08:00** | 14 Sep 2026 | the student's work |
| Module 02 — opponent atlas | PAHdb v4.00 and Anharmonic v1.00, Mai 2025, the Bos-type baseline, read in and version-frozen — **first version complete 10 September** (parser, tables, notebook, report; the student's own pass before submission) | 25 Sep 2026 | data engineering, no compute |
| Module 03 — scoreboard and u_band | probe 2a, the laboratory columns, decidability per family — **scaffolded in the Udacity rubric form on 11 September** (`modules/03_lab_scoreboard/`: a pre-registered matrix–gas test committed before the join, 63 pairs of naphthalene, anthracene, pyrene and chrysene against the WebBook GC-IRD records; six families reject a zero offset, median +3.3 to +5.9 cm⁻¹ matrix above hot gas; the u_band columns on these records, the PNNL and cold columns still owed) | 2 Oct 2026 | the student's work; the supervisor's answers to §13 items 7–10 |
| Pilot-note inputs | naphthalene dry run, R0 pilot, canonical two-mode points — and the naphthalene noise run | 23 Oct 2026 for the laptop part; the noise run with the R1 machine (P13) | **laptop for the DFT dry run, the R0 pilot (benzene, ≈ 75 min per xtight energy) and the canonical two-mode points (14–21 min each). Repriced 12 September from the 11 September timing (the row had been set on 10 September, before it): the naphthalene noise run of §7 item 7 is 72 energies × 11.5 h = 828 h ≈ 35 days at tight thresholds, about twice that at the anchor's xtight thresholds — not deliverable by 23 October on the laptop; it goes with the machine P13 chooses and its date follows that decision** |
| Pilot note | every frozen number, band lists, margins | 30 Oct 2026 | the student's work after the measurements |
| Module 04 — calibrated-harmonic baseline | ML correction to scale factors, leave-molecule-out — **scaffolded in the rubric form on 12 September** (`modules/04_calibrated_harmonic/`: recipe committed before training; 2,477 matrix↔computed pairs of 83 molecules; leave-one-molecule-out MAE 6.49 cm⁻¹ for the library as served against 6.40 for the best model, R² ≤ 0.01 — on this table the calibrated baseline *is* line A; the Zenodo release of the table and the pilot note's adoption of the recipe still owed) | 30 Oct 2026 | in parallel with the compute |
| Module 05 — Δ₂-support predictor | the DFT-vs-DFT Hessian corpus and the network — **scaffolded 12 September** (`modules/05_support_predictor/`: recipe, the Transformer in PyTorch, smoke test on the benzene dry-run tensor). **Hessian QM9 downloaded and verified the same day** (41,645 molecules, ωB97X/6-31G* numerical Hessians; paper read for units and conventions). **Measured: it holds only 66 molecules with an all-carbon aromatic six-ring and 6,055 with a planar conjugated five- or six-ring** — the "aromatic-heavy QM9 subset" of the mapping is really a conjugated/heteroaromatic subset. **Prepared in response (no compute yet): a resumable corpus factory** (`modules/05_support_predictor/corpus/`) with four layers — 45 ladder-adjacent aromatics of 12–30 atoms as a size bridge, 868 mono-substituted three- and four-ring cores that turn the bridge into a distribution (added the same day on the student's decision), 4,353 substituted aromatic and heteroaromatic cores as the class, and the 6,055 conjugated QM9 molecules — computed with the plan's two functionals at 6-31G* on this laptop, the desktop or a cluster, start-and-stop, in a fixed order so every stop leaves a reproducible subset. The number actually computed is fixed by a dated note after a five-molecule timing test; the corpus is published with a DOI before the module starts (reading 1). No result | 20 Nov 2026 | the corpus costs DFT compute and competes with R1 (measured per molecule: a QM9-size molecule 3–7 min per Hessian, naphthalene 13 min, pyrene 54 min) |
| R1 probe batch and scoring | the first real coupled-cluster correction, naphthalene | 4 Dec 2026 | **not the laptop (227 days at the measured 11.5 h per energy): the desktop of the hardware note in two to three months — an estimate from the core count, not a timing; nearer four with the corpus factory beside it; the desktop is a priced configuration, not a purchase, and would be the student's own — or the cluster** (P13, open) |
| Cluster request | sponsored by the supervisor, sized by the R1 timings | 11 Dec 2026 | the supervisor and the request's lead time |
| Module 06 — generative pattern proposer | the efficiency experiment on K_off | 18 Dec 2026 | the student's work |
| Q9 pre-registration — families per adjacency class, τ_F, the two rules, the LOMO protocol (decision 27) | written before any R2 correction exists | 15 Jan 2027 | no compute |
| Module 07 — campaign officer | LangGraph, the Anthropic API, the cost record | 15 Jan 2027 | the student's work |
| R2 and R3 | pyrene class and coronene; then Q9 evaluated per family and the Q10 coverage table printed for R0–R3 | 12 Mar 2027 | **cluster access**; without it these rungs lapse |
| Module 08 — the pipeline assembled and scored | R0–R3, fragment-probed R6 where licensed | 16 Apr 2027 | everything above |
| Module 09 — defense | | 21 May 2027 | |

Two scenarios follow from the one hinge, cluster access. **With the cluster** the programme ends in
May 2027, eight months from now. **Without it** R2 and R3 lapse, Module 08 scores R0–R1 and the
laboratory side, and the defense can be held at the end of March 2027 — thinner, and honest. The
hinge is December: a cluster request not submitted before the winter break puts the project in the
second scenario. The critical path is the laptop's compute until the end of October, the student's
decisions in the evenings, and the supervisor's reading time at the two points named.

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
   C–C families at the pyrene-size rung decidable. The 5 September search found none of known
   temperature; a source the supervisor knows of that the search missed would enlarge the
   decidable set, and the plan is written so that it can be added before, never after, a comparison
   is scored.
4. A view on the intensity question (§7): positions are the promise, intensities are scored where
   a calibrated gas-phase measurement exists and reported elsewhere, and a coupled-cluster
   correction to intensities is a measured question rather than a promise. If the supervisor wants
   intensities carried further, the dipole probe M1-μ is the measurement that would license it.
5. The naphthalene measurement now justifies it (11.5 hours per energy on the laptop at the tight thresholds, more at the anchor's tighter ones; the R1 deck of
   474 energies is 5,450 laptop-hours): sponsorship of a cluster-time request sized by the timed
   probes, including whether a suitable machine exists within the supervisor's own network, and, at the large-rung stage, serving as or nominating the named expert whose
   pre-registered judgment is the datum where no laboratory truth exists (the "expert-judgment
   datum" of §5.2).
6. Whether the supervisor sees the outlook of §6 as a reason to widen the corpus of measured
   molecules beyond the ladder, at cluster cost, once R3 has printed the range of the correction.

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
    (5.45 cm⁻¹, Esposito et al. 2024) and none at R1.
15. Whether excluding modes below 300 cm⁻¹ from the VPT2 in that protocol drops their couplings
    to the 6–15 µm fundamentals entirely, or only their own bands — relevant to how the Δ₂ = 0 null
    row of this pipeline, which keeps them, is read against line B.

*On the ladder and the programme.*

16. Whether the scope of the promise — a coupled-cluster correction to the harmonic constants
    only, no coupled-cluster anharmonic correction, intensities scored on benzene and naphthalene
    only — is one the supervisor would sign, or whether the supervisor wants any of the three measured questions of
    §6–§7 (M1-μ, the diagonal cubic by-product, the learned prior) promoted before the pilot note.
17. The two asks of item 5 above in concrete form when the time comes: the size of a cluster-time
    request the supervisor would sponsor, and who serves as the named expert for the reach rungs.

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
  211101. DOI 10.1063/5.0208597. (C–H overtone spectra of benzene and naphthalene; the
  PAHdb-anharmonic protocol; B3LYP/N07D vs CCSD(T)-F12b benzene harmonics, MAD 5.45 cm⁻¹.)
- Esposito, V. J., Fortenberry, R. C., Boersma, C., Maragkoudakis, A., Allamandola, L. J. 2024,
  MNRAS Lett. 531, L87. DOI 10.1093/mnrasl/slae037. (CN stretches of cyano-PAHs; the second
  statement of the PAHdb-anharmonic protocol, 1 cm⁻¹ Gaussian profile; CC BY, read in full 8
  September.)
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
- Käser, Boittier, Upadhyay & Meuwly 2021, J. Chem. Theory Comput. 17, 3687 (per the held arXiv manuscript, arXiv:2103.05491, read in full 10 September; journal record not verified against the journal). (Transfer learning to CCSD(T) anharmonic frequencies — the Δ-learning precedent of §3.1.)
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
  of the PAHdb Anharmonic library — naphthalene, anthracene, tetracene; Crossref record, 8
  September; PDF asked of the supervisor.)
- Mackie, Candian, Huang, Maltseva, Petrignani, Oomens, Mattioda, Buma, Lee & Tielens 2016,
  J. Chem. Phys. 145, 084313. DOI 10.1063/1.4961438. (Opponent line B: benz[a]anthracene,
  chrysene, phenanthrene, pyrene, triphenylene; Crossref record, 8 September; PDF asked of the
  supervisor.)
- Madriaga, J. P., Crawford, T. D. 2025, J. Phys. Chem. A 129, 10014.
  DOI 10.1021/acs.jpca.5c05210. (PNO discontinuities in finite-difference properties.)
- Mai et al. 2025, Mon. Not. R. Astron. Soc. 541, 3073; arXiv:2503.05120. (Opponent line C:
  DFT-trained machine-learning molecular dynamics of PAHs to C₂₁₆.)
- Maltseva, Petrignani, Candian, Mackie, Huang, Lee, Tielens, Oomens & Buma 2016, Astrophys. J.
  831, 58. DOI 10.3847/0004-637x/831/1/58. (Jet-cooled 3 µm spectra of pyrene, chrysene and
  triphenylene among others — the C–H stretch cold column at R2; Crossref record; abstract grade.)
- Mata & Werner 2006, J. Chem. Phys. 125, 184110. DOI 10.1063/1.2364487. ("Calculation of smooth potential energy surfaces using local electron correlation methods" — the 2006 prior art of §3.1; Crossref-verified 10 September; closed access, asked of the supervisor, not read.)
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
  (PAHdb v4.00, opponent line A; the statement that its systematic uncertainties are unquantified.)
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

Other plan-04 sources carried in the working bibliography and used by the modules (matrix
scoreboards, the DLPNO caveats): Bauschlicher et al. 2018; Chen, Li & Li 2026; Hudgins & Sandford 1998; Lam, Abdul-Al &
Allouche 2020; Mattioda et al. 2020; Sylvetsky et al. 2020; Tang et al. 2025; NIST CCCBDB; Zapata
Trujillo & McKemmish 2022.
