# Research note 2026-09-08 — P19: is the correction transferable per family across size? (the route from benzene to the beasts)

**Status.** A proposal for the user, not a decision. Nothing in the Ladder changes until it is
accepted; if accepted it enters as a dated note with a new gate (Q9) and the proposal's §6 is
rewritten from outlook to main route. Written after the user's statement of 2026-09-08: *the goal
is the very large PAHs; benzene is a tool, not a goal.*

## 1. Why this note exists

Plan 05 reaches the largest sizes (R4–R6) only as **reach** rungs: fragment-probed Δ₂ under a
measured licence, no accuracy claim, an expert-judgment datum where no laboratory truth exists
(Ladder §2, §3). That is honest, and it means the plan as written gives the large PAHs a
*demonstration*, not a *result*. The only route by which the accuracy rungs R0–R3 can hand
something to the large PAHs is the one the proposal keeps as an outlook (§6): if the correction Δ₂
is systematic per band family, a rule measured on small PAHs corrects a whole library of large
ones at almost no cost. Plan 04 tried a transfer of a *learned, motif-level* correction and it
failed its own transfer test; the Ladder therefore refuses "motif-transfer claims" (§6). P19 asks
a narrower, cheaper question that plan 04 never tested, and asks it under a pre-registered losing
condition — which is the only form in which a question the plan once refused may come back.

## 2. The quantity

In the dimensionless normal coordinates the probes use (E = ½ ω q², ω in E_h), the curvature of
the energy along DFT mode *i* is the frequency itself, so the diagonal element of the correction,
**Δ₂,ii = ω_CC,i − ω_DFT,i** along that mode, is to first order the frequency correction the
coupled-cluster anchor applies to mode *i* before the off-diagonal block re-mixes the modes. For a
scored band family F (Ladder §1: C–H out-of-plane, C–H in-plane, C–C stretch, C–H stretch …) and a
molecule M, define

- **δω_F(M)** = the mean of Δ₂,ii over the modes of family F in M (after the full recovery, the
  family's mean frequency shift including the off-diagonal re-mixing is reported beside it);
- **s_F(M)** = the spread (standard deviation) of those Δ₂,ii within the family in M.

Both are printed by the pipeline on every accuracy rung already; P19 adds no coupled-cluster
energy. Every number is in cm⁻¹ and comes from the same scripts that produce the scored spectrum.

## 3. The size sequence

R0 benzene (1 ring), R1 naphthalene (2), the anthracene locality probe (3, linear), R2 pyrene,
chrysene, triphenylene, tetracene (4 rings, three topologies), R3 coronene (7): **eight molecules,
five sizes, four topologies**, all of which the plan computes anyway. The anthracene probe exists
for the locality question (Q8); P19 uses its Δ₂ as one more point.

## 4. The rule and the test (form fixed now, numbers at the pilot note)

**The rule.** For each family F, a per-family constant **c_F**, and as a second candidate a
one-parameter size law **c_F + d_F/N_C** (N_C the number of carbons). Nothing else — no motif
terms, no learned model.

**The test.** Leave-one-molecule-out over the eight molecules: for every held-out molecule M of
R2 or R3, the rule fitted on the other seven predicts δω_F(M); the error |predicted − measured|
is the transfer error e_F(M).

**Winning condition (per family).** e_F(M) ≤ τ_F for every R2 and R3 molecule, **and**
s_F(M) ≤ τ_F on R2 and R3 (a family whose members disagree among themselves by more than the
margin is not a family for this purpose), where **τ_F is the family's beat margin** frozen in the
pilot note (Ladder §4). A family that wins is **transferable at the sizes measured**, with the
LOMO error as its error bar.

**Losing condition (per family).** Any R2/R3 molecule with e_F(M) > τ_F, or s_F(M) > τ_F on R2 or
R3: the family is **not transferable**; its rule is never applied above R3; the sentence is
pre-written.

**What is not tested and not claimed.** Transfer of spectra; transfer of off-diagonal blocks;
transfer beyond the largest size measured (coronene) except as the explicit extrapolation the
R6 check below tests; any statement about temperature, charge state or hydrogenation.

## 5. What passes to the large PAHs if a family wins

1. **A corrected library, shown with provenance.** Line A's scaled-harmonic positions for the
   family, shifted by c_F, with the LOMO error bar — for every PAHdb species, at no coupled-cluster
   cost. It is a *shown* product on R4–R6 (no laboratory truth there), scored only where a later
   measurement exists.
2. **A sharper R6.** The fragment-probed Δ₂ on the C₃₈₄H₄₈-class flake, which the plan already
   promises under the fragment licence, becomes a **direct check of the rule on one large PAH**:
   predicted c_F against the fragment-probed δω_F of the flake, per family. Today R6 carries no
   accuracy claim at all; under P19 it carries one falsifiable prediction per transferable family.
3. **A statement about the correction's size dependence** that the field does not have: whether
   the coupled-cluster correction to harmonic PAH frequencies is a per-family constant, a slow
   function of size, or a per-molecule quantity.

If no family wins, the large PAHs get nothing from the coupled-cluster arm, and the pipeline
reports that calibrated harmonic DFT with anharmonic DFT is, at this anchor and this size, as good
as the correction can make it — a result the field does not have either.

## 6. Why this is not plan 04's failed transfer

Plan 04 learned a correction on one ring motif and reused it on another; the learned object was
motif-specific and the test compared motifs. P19's object is a family-level constant across
*sizes* and *topologies*, fitted with two parameters at most, and its test is leave-one-molecule-
out with the losing condition written before any Δ₂ at R2 exists. Plan 04's measured failure is
the reason §4 states the losing condition first, and the reason the rule has no motif terms.

## 7. Cost and order

No new coupled-cluster energies: every Δ₂ used is one the ladder computes for its own scoring. The
anthracene probe is already budgeted for Q8. The test runs when R3 has printed and **before any R6
probe is submitted**; the R6 cluster request then carries the rule's prediction as the thing the
flake will check.

## 8. What changes in the documents if accepted (decision 27)

- **Ladder §6** — the refusal "no motif-transfer claim" stands; a sentence admits the per-family
  transfer *test* of this note as gate **Q9**, with its winning and losing conditions; the R6 row
  gains "and, for families that passed Q9, the check of the transferred rule"; §4 lists τ_F as the
  number Q9 reads from the pilot note.
- **Goal** — Q9 in the gate list and the glossary (δω_F, s_F, c_F, e_F).
- **Proposal §6** — from "outlook, not a promise" to the pre-registered test, with §4's
  conditions; §1 says in one sentence that the route from benzene to the large PAHs is this test.
- **Mapping** — Module 08's product includes the corrected library for the families that passed,
  with its provenance line.
- **Distilled plan** — Q9 row.
- **Frozen Lines** — none (line A stays the opponent; "line A + rule" is a product, not a line).

## 9. What it does not change

The anchor, its licence and its three lines (noise, bias, basis set — decisions 8–26); the
fragment licence; the intensities decision; the module chain; the refusal of learned spectrum
models. If P18 (composite anchor) is accepted later, Q9 uses whichever anchor the Ladder then
defines.
