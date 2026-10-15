# Pre-registration — the rung-C architecture's floor: how much of the correction can the network's form hold, and how does that grow with size?

Registered 15 Oct 2026, 19:0x (the user, 19:0x: 'Ja, begin maar met de registratie. Let extra op codekwaliteit, ook van de Python.'). No number
of this test exists yet; the data list is frozen at the fetch, before the first computation.

## Why

The lowest odds of 15 Oct are the mandate (39 %) and the size line (50 %), and both sit on the size penalty: chain 39 read a ring-coupling
ratio 1.96× and a ring-in-plane diagonal 1.70× worse on molecules of ≥ 27 atoms. The levers bought so far for size are data (lever 5, rung 4,
the PC question at ≈ €2,290 per decade of data). They assume the error on large molecules is a learning error. Never tested: whether the
network's **form** can hold the correction of a large molecule at all. Rung C's head (`m05/rungC_equivariant.py`) writes

- an off-diagonal block ΔH_ij only for atom pairs within **5 Å**, zero beyond;
- each off-diagonal block **symmetric** (a registered restriction of 25 Sep);
- each diagonal block from the translational sum, ΔH_ii = −Σ_j ΔH_ij over the pairs it writes.

In a conjugated ring system force-constant changes can reach beyond 5 Å, and a larger molecule has more such pairs. If they matter, no amount
of data closes that part of the gap; a change of form does.

**What this test cannot answer, said before the numbers:** chain 39's ratio compares two networks of the *same* form (trained ≤ 20 atoms
against trained on every size below 27), read on the same molecules. A floor of the form is shared by both, so it cannot explain that ratio.
It measures the floor under every network of this form, and how the floor grows toward the mandate's sizes.

## Data (frozen at the fetch)

Every corpus molecule with the **analytic** pair (B3LYP and ωB97X, `hessian_{b3lyp,wb97x}_analytic.npz`): the labels server's
`/root/labels/molecules` (498 on 15 Oct 19:0x) and the 44 local folders, 534 together — by the manifest's atom count 5 below 10 atoms, 282 of
10–19, 242 of 20–29, 5 of ≥ 30. The id list and the sha256
of every fetched file are written at the fetch, before any floor is computed. FD-labelled molecules are left out: their noise reaches every
block, so a far block would mix signal and noise. Chain 39's hold-out (s) has 2 analytic molecules, so it is not the test set here; its
observed errors are quoted beside, for scale only (other molecules, FD truth).

## Method

Per molecule, from the raw analytic Hessians (`H_raw`) and the low level's normal modes, K = the mode-basis correction exactly as
`coupling_matrix` builds it (cm⁻¹, diagonal = first-order frequency shift). The **oracle of the form** ΔH⁽ᶠ⁾ keeps the true ΔH_ij for pairs
within the cutoff, takes each block's symmetric part, zeroes the rest, and rebuilds every diagonal block from the sum rule. Its error in modes,
K⁽ᶠ⁾ − K, is the floor: what a network of this form would still miss if it learned every block it can write perfectly. Three variants
attribute the floor: **form** (all three restrictions), **cutoff only** (blocks kept whole), **symmetry only** (no cutoff). Read-outs per band
family (CH-stretch, CH-oop, ring-ip, other; the assignment rung C's read-outs use): the rms of the diagonal error, pooled over modes. Beside:
the ring-coupling floor (rms of the ring family's off-diagonal error over the rms of its true couplings), and the form floor at cutoffs 4, 5,
6, 8 and 10 Å.

Invariant checked in the tests before any read: with no restriction the oracle returns K exactly (to 1e-8 cm⁻¹), and the raw and the projected
Hessians give the same K in the vibrational block.

## Lines

1. **The form costs now:** the pooled form floor (5 Å) on the molecules of ≥ 25 atoms is ≥ 1.0 cm⁻¹ in a band family. (If fewer than 30
   molecules have ≥ 25 atoms, the bound is lowered one atom at a time until 30 are in; the bound used is reported.) 1.0 takes 16 % of
   the 2.5 cm⁻¹ line's variance budget before any learning error.
2. **The form costs at the mandate's size:** a power law fitted to the per-molecule form floor against the atom count (molecules of ≥ 10
   atoms, least squares in log–log), evaluated at 60 atoms, is ≥ 1.25 cm⁻¹ in a band family (half the line). The point estimate decides; a
   bootstrap over molecules (1,000 resamples, seed 0) gives its interval beside. Sixty atoms lies beyond the data: line 2 is a forecast and is
   **re-read on lever 5's large-PAH labels (34–60 atoms, TASKS 49) and layer T when they are fetched**, with this script and these lines,
   registered now.

**What follows (registered now):**
- line 1 or 2 met in a family → a model change is registered before more data is bought for size: the pair cutoff raised to the distance
  where the floor of that family falls below 0.5 cm⁻¹ (from the sweep), with or without the symmetric-block restriction as the attribution says,
  trained on chain 34's recipe at one pool size and read against chain 34 on hold-outs (a) and (b);
- neither met → the form is not the limit at these sizes; the size levers stay with data, and the PC question is put with that sentence.
- No scope-reducing fallback: a family that meets a line is not argued away by the others that do not.

## Limits

- The floor of truncation is not a strict lower bound: a network can partly compensate a missing far block through the blocks it writes. It is
  the floor of perfect local learning, the natural reading of 'what the form can hold'.
- The ωB97X − B3LYP difference is the proxy target, not CC − DFT. The CC anchors' correction is read the same way once the method is shown
  to work (beside, later, on the anchors with analytic DFT pairs).

## My prediction (before any number)

The form floor is small next to the observed errors at these sizes: ring-ip 0.3–0.8 cm⁻¹ on ≥ 25 atoms (line 1 not met), CH-stretch and
CH-oop below 0.3; the cutoff dominates the symmetry restriction; the power-law exponent ≈ 1, giving 0.6–1.5 cm⁻¹ at 60 atoms — line 2 the
open one.

## Outcome (15 Oct 2026, 19:2x)

Read with `probes/architecture_floor.py` on the frozen 534 (`probes/results_m1/arch_floor_2026-10-15/`: `inputs.tsv`, `floor.md`,
`floor.json`); line 1's bound came out at 24 atoms (30 molecules). Invariants before the read: an unrestricted oracle returns the correction
to 1e-12; raw and projected Hessians give the same K to 1.7e-8 cm⁻¹ over all 534.

| family | line 1 (≥ 1.0) | line 2 at 60 atoms (≥ 1.25) | cutoff only | symmetry only |
|---|---|---|---|---|
| CH-stretch | 0.70 | **1.39** (0.98–1.89) | 0.05 | 0.70 |
| CH-oop | 0.90 | **4.00** (1.49–13.4) | 0.90 | 0.00 |
| ring-ip | **5.58** | **5.62** (4.11–7.58) | 1.49 | 5.41 |
| other | **10.03** | **7.89** (5.81–10.70) | 3.01 | 9.68 |

By the registered procedure both lines are met (line 1 in ring-ip and other, line 2 in all four families). **The read does not carry the
meaning the registration gave it.** The registration called the projection oracle 'the floor of perfect local learning' and said it was not
a strict bound; the numbers show it is not a floor at all. Chain 39's control network — this very form — reads ring-ip 3.78 and other 5.09
on molecules of ≥ 27 atoms, against FD truth that adds noise; the 'floor' here is 5.6 and 10.0. A floor cannot sit above what a network of
the form already reaches. The reason is in the read-out: the per-family numbers are the *diagonal of K in the mode basis*, a few hundred
numbers per molecule, while the form writes thousands of block entries. A network compensates a block it cannot write (an antisymmetric part,
a pair beyond 5 Å) through the blocks it can, so the element-wise projection overstates what is lost — by far the most for the symmetric-block
restriction, which carries nearly all of the 'floor' (symmetry only 5.41 of 5.58 in ring-ip).

**What stands:** the cutoff part is small in ring-ip (1.49 by projection, also an overstatement) and in CH-stretch, and in CH-oop it falls
steeply with the cutoff (0.90 at 5 Å, 0.08 at 8 Å) — the one pattern that reads as a real reach effect. **What does not:** a floor, and
therefore line 2's forecast for 60 atoms.

**What follows (a departure from the registered consequence, with its reason):** the registration said 'a line met → a model change is
registered before more data is bought for size'. That consequence assumed the numbers were a floor. On this evidence alone no model change is
justified. The question remains open and is answered directly, not by a better bound: a registered training comparison on chain 34's recipe
at one pool size — the head as it is, the head with non-symmetric pair blocks, the head with an 8 Å pair cutoff — read against chain 34 on
hold-outs (a), (b) and the size hold-out. To be registered before it runs; it needs laptop time that the current jobs hold until about the end
of October. Until then the size levers stay with data, and the PC question is put without a claim either way about the architecture.

My prediction (small floors, line 1 not met) was wrong in its numbers and right in its conclusion, for a reason I had not foreseen: the
measure, not the network, was the problem.
