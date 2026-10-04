# Pre-registration, 4 October 2026, 09:1x — the proposer's order rehearsed on naphthalene's existing CC gradients (decision 58, the user: "Akkoord met al je adviezen")

*Registered before anything is built or read. Decision 58 (4 Oct 09:0x) puts the standout's hand-feature scorer in charge of the order of partial
coupled-cluster decks, before the hash. This rehearsal turns that rule into a price on a case where the full answer already exists: how many of
naphthalene's 30 symmetry-unique CCSD(T)/cc-pVDZ gradients does an anchor need when the carried network fills in the rest?*

## The object

`probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/`: the 30 symmetry-unique displacement pairs (60 gradients) of the (T)-lambda-corrected
anchor, its assembled Hessian `hessian_ccsd_t.npz` (the truth of this rehearsal), its two-route limits (FD asymmetry, symmetry consistency, energy route)
and the analytic B3LYP low level of the same geometry. The carried network of decision 57 (chain 34's three seeds) predicts the Cartesian correction
ΔH for naphthalene as a hold-out (a) molecule.

## The hybrid anchor after k gradients

For an ordered list of the 30 displacements, the hybrid Hessian after the first k is: the measured CC rows (and, by symmetry, their orbit images) for
those k coordinates, the network's predicted rows for the others, symmetrised, translations and rotations projected out. Read-out per k: the rms
difference of the corrected frequencies (hybrid against the full anchor) per family (ring-ip, CH-stretch, CH-oop, other) and the ring-coupling ratio of
the hybrid's ΔH against the anchor's. Three orders:

- **P1** — the standout's hand-feature scorer (the version and hash of `modules/standout_pattern_proposer` recorded in the output), adapted to
  displacements: a displacement's score is the sum of the scorer's scores over the pattern pairs that contain its coordinate (the adapter is a
  dozen lines, written and tested on benzene's 12 displacements before naphthalene is touched); ties by the seeded rule.
- **blind** — the symmetry-unique index order the probe uses today (the order in which the anchor was actually computed).
- **oracle** — descending true |ΔH_CC − ΔH_network| row norm (the ceiling, impossible in practice).

Noise is already in the gradients; no synthetic noise is added. One run per order (deterministic); the network's three seeds give the spread.

## Predictions (on record)

The hybrid at k = 0 is the network alone: naphthalene's chain-34 hold-out numbers (in-plane ω ≈ 2 cm⁻¹, other ≈ 3–4, ratio ≈ 0.2). P1 reaches the
anchor's own limits — rms ≤ 1 cm⁻¹ in every family and ratio ≤ 0.05 — at 40–60 % of the gradients; blind at 70–90 %; the oracle at 20–40 %. The
C–H stretch family is the first to be done under every order (it is local), the ring modes the last.

## Lines

- **P1 reaches the limits at ≤ 60 % of the gradients and earlier than blind by ≥ 15 points** → the deck route is priced at that fraction for the label
  plan (an anchor beyond 26 atoms costs that share of a full Hessian), and the Ladder amendment of decision 58 applies to displacement decks as well
  as pattern decks.
- **P1 reaches the limits but not earlier than blind (within 15 points)** → the scorer does not transfer from pattern pairs to displacements; decision 58
  stays for pattern decks only, and displacement decks keep the blind order until a displacement scorer is registered.
- **No order reaches the limits before 90 %** → the network's predicted rows are not good enough to carry an anchor; the deck route needs the
  recovery (the standout's own, on pattern responses) rather than network rows, and that is registered separately before any large anchor.

## Cost and place

No new chemistry: the gradients, the Hessian and the network exist. The adapter, the assembly and the read-out are one probe (`probes/anchor_deck_rehearsal.py`),
two threads, minutes per order; built after the lay-reader passes of 4 October, run on the laptop when the TZ run is done (the network's prediction
needs the torch environment the host cannot spare beside the TZ run's VM today). Nothing in the Ladder changes until the read is on record.

*Dated note 4 October 09:2x (while building, before any read):* two details fixed in `probes/anchor_deck_rehearsal.py`. (1) The adapter: the scorer scores
pairs of normal modes, so a Cartesian displacement k is scored as s_k = Σ_{i<j} S_ij (V_ki² + V_kj²) with V the mass-weighted normal modes of the
analytic B3LYP Hessian — each mode pair weighed by the displacement's share in its two modes; scorer seeds 0–2 averaged, the checkpoint hashes in the
output. (2) The smoke molecule is pyridine, not benzene: benzene's per-displacement gradients were never copied from its server (the fetch audit of
3 Oct), pyridine's 21 are local. The smoke runs with `--no-network` (the B3LYP Hessian alone fills the unmeasured rows) to test the mechanics; that
column is a baseline beside the registered hybrid, not a line.

## Outcome, 4 October 2026, 09:2x–09:3x (`modules/05_support_predictor/out/deck_rehearsal_naphthalene_c34_2026-10-04.{md,json}`; the pyridine smoke beside it)

Run beside the TZ run and chain 34c rather than after them (two threads, about a minute per molecule; the host's free memory held). Chain 34's three
carried seeds filled the unmeasured rows; the probe was amended before the read with a per-read-out first-k table (the verdict table and the
curves are unchanged by it).

**Third line.** No order reaches the anchor's limits before the last gradient: P1, blind and oracle all at 15 / 15 (100 %). The k = 0 column, the
prediction alone, is naphthalene's T3 'network as is' read of 2 October within 1 cm⁻¹ (ring-ip 20.4, CH-stretch 54.5, CH-oop 94.2, other 75.1, ratio
1.00; T3: 20.9, 55.2, 93.6, 74.3, 0.99). At the CC level and without fine-tuning the network's correction is as far from the anchor as no correction
at all, and worse than B3LYP alone out of plane (CH-oop 94 against 76 under the zero rule). Rows that good cannot carry an anchor: a family's rms
drops below 1 cm⁻¹ only when every row that family lives on has been measured.

**The prediction on record was wrong, and the mistake is in the registration:** it put the k = 0 column at the chain-34 hold-out numbers (≈ 2–4 cm⁻¹).
Those are read against the corpus's high level; the CC correction is a different object, and the T3 read of 2 October had the 'network as is'
column at ratio 0.99 on record. The registration should have cited it.

**What the split shows (the per-read-out table in the output; not a registered line):** P1 does transfer from pattern pairs to displacements. Under
P1 the in-plane read-outs close first — ring-ip ≤ 1 cm⁻¹ and ratio ≤ 0.05 at k = 9 (60 %), CH-stretch at k = 10 (67 %) — against k = 13 and 14
under the blind order (87 %, 93 %): 27 points earlier. CH-oop and 'other' close at 15 / 15 under every order: P1 ranks the ten in-plane
displacements before the five out-of-plane ones, and the network's out-of-plane rows are worse than B3LYP's. The 'oracle' (largest true row error
first) measures the out-of-plane carbon rows first and is last on the in-plane read-outs; at k = 9 blind and oracle have measured the same nine
carbon rows. A row-norm oracle is not the read-out oracle — a design note for any next registration.

**Consequences.** (1) The deck route is not priced: with today's network an anchor is a full symmetry-reduced deck. The Ladder amendment of
decision 58 stands for pattern decks and for the *order* of any displacement deck that is partial for another reason; it says nothing about stopping
early. (2) The route re-enters when the CC-level transfer itself (T3, dossier question 5: anchors as the lever) is within a few cm⁻¹ out of plane;
a hybrid with fine-tuned rows (T3's 'head tuned' column, ratio 0.25, CH-oop 34) is a new registration, not a rerun, and today's numbers say it would
not reach 1 cm⁻¹ either. (3) The in-plane lead of P1 (≥ 15 points over blind on ring-ip and CH-stretch) is the candidate line for that registration.
