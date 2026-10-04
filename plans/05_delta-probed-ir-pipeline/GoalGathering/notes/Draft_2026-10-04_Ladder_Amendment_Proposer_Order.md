# Draft, 4 October 2026 — a dated amendment of the Ladder: partial CC decks take the proposer's order (for the user's yes or no)

*Adopted 4 October 2026, 09:0x, as decision 58 (the user: "Akkoord met al je adviezen"); the amendment is in the Ladder §3 and the rehearsal is registered. The Ladder (`../Frozen_Ladder_and_Tolerances.md`) changes only by a dated amendment on the user's word. This draft answers the
question of 4 October 08:4x ("gebruiken we het geleerde uit de standout module in het eindproduct?") and TASKS item 21.*

## What the standout established

The pattern proposer orders the measurements of a partial coupled-cluster deck by what each pattern response teaches about the whole correction.
On real CC responses it was read twice: benzene (29 September) and naphthalene (4 October 02:5x). Under the band-free line, the registered line since the
amendment of 4 October 08:4x, the hand-feature scorer's order (P1) needs about half to a fifth of the energies the blind order needs
(naphthalene: P1/oracle 5.0, C1 and C2 passed). The learned representation (P2) has not beaten the hand-feature scorer at 175 training molecules; its
registered stages stand. The proposer's own verdict rule (pre-registration of 26 September): "S1 pass → the label plan's decks may take the P1 ordering
*before the hash*, announced as a dated amendment of the Ladder."

## Where it would enter the pipeline — and where not

- **Not in the trained network.** The end product (large PAH in, spectral shape out) contains nothing of the standout; the proposer is about *which
  calculations to run*, not about predicting.
- **Not in the anchors so far.** Every anchor (benzene, fluorobenzene, pyridine, naphthalene, anthracene) is a full symmetry-reduced finite-difference
  Hessian: all displacements, no deck to order.
- **In partial decks, when they come.** Beyond ≈ 26 atoms a full CCSD(T) Hessian is unaffordable on our machines (anthracene's 42 gradients take a
  CCX53 three days); the plan's route there is a partial deck of pattern responses with the recovery (§3 of the Ladder, the Q0 deck and its hash) and,
  for the local-CC question, the frozen-spaces route. There the order of the deck is exactly what the proposer provides.

## The amendment, as it would read (Ladder §3, beside the Q0-deck item)

**Dated amendment 2026-10-04 (decision ——; the standout's CC-level test, benzene 29 Sep and naphthalene 4 Oct, both passing the band-free line):**
a partial deck takes the order of the hand-feature pattern scorer (P1 of `modules/standout_pattern_proposer`, the version and its hash recorded in the
deck's manifest) *before* the deck's hash is taken and before any response exists; hold-out membership stays the seeded rule of item [05] and is drawn
after the ordering; the recovery and the stop rule are unchanged. A learned proposer (P2 or later) replaces P1 only after its registered stages beat
the hand-feature scorer on the proxy and on at least one CC molecule. Full Hessians, where affordable, are unchanged.

## What the user decides

1. Yes or no to the amendment above (with its decision number).
2. Whether the first partial deck — the first anchor beyond 26 atoms, or the LNO cell (b) read — is the first use, or whether a dry run on
   naphthalene's existing full Hessian (order the 30 symmetry-unique gradients by P1, recover after k of them, read the curve) comes first as a
   rehearsal. The rehearsal costs no new chemistry (the gradients exist) and gives the plan a number: how many of naphthalene's 30 gradients the
   recovery needs under P1's order to reach the anchor's own validation limits.

*My advice: yes to 1; the rehearsal of 2 first, registered with a line (recovery within the anchor's two-route limits after ≤ 60 % of the gradients),
because it turns the standout's result into a number the label plan can price.*
