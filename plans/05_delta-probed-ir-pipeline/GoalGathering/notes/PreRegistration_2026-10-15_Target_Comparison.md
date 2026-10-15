# Pre-registration — the training target of the carried head: projected against ridge, read where the molecules are large

Registered 15 Oct 2026, 21:2x (the user, 21:1x: 'Registreer de doelvergelijking maar.'). The registration's read script (`probes/target_comparison_read.py`)
and its tests on synthetic records with the edge cases were written and run before this text was committed (the step agreed after two
faulty line designs this evening). No training of this comparison exists yet.

## Why

`PreRegistration_2026-10-15_Hybrid_Form_Floor.md` (outcome 15 Oct): pattern f can hold the correction — its least-squares floor at ≥ 24 atoms
is ring-ip 0.107 cm⁻¹ and a ring-coupling ratio of 0.017, flat with size — but the projected target the carried recipe trains loses
1.126 cm⁻¹ in ring-ip and a ratio of 0.122 there, growing with size (ring-ip 0.73 → 1.42 cm⁻¹ from 15–19 to ≥ 28 atoms). A network that
learned its target perfectly would still carry that loss. The recipe has a second target: the ridge-anchored least-squares target
(`--aux-target ls --ls-lam 1e-3`, `m05/rungC_targets.py`), whose bound is lower; on 1 Oct it trained *worse* at pool 750 (chain 10, one size),
so its learnability is the open question. This comparison asks it where the target loss is largest: on large molecules.

## Arms and settings

Two arms, identical but for the target: **P** = chain 34's carried recipe (`chain_runner.RECIPE_V11`, projected target), **R** = the same with
`--aux-target ls --ls-lam 1e-3`. Seeds 0, 1, 2 in every cell; decision 51's early stopping (a best epoch within 10 % of the cap is re-run with a
higher cap before the read).

- **Setting C (the question):** chain 39's control split — hold-out (s) = every pool molecule of ≥ 27 atoms, trained on all sizes below
  (`--size-test-min-atoms 27`), pool layers A, A2, B — at the full pool and at half of it (`--sizes`: half and all), for the still-learning rule.
- **Setting F (the guard):** the full pool as chain 34 trains it, read on hold-outs (a) and (b).

12 + 6 = 18 trainings. Price basis: chain 39's control trained 979–1,100 s per seed on the laptop (9 Oct, 868 molecules); the price is
re-measured on the merged corpus before the launch and written in the run spec.

**When:** after the labels server's analytic labels are fetched and merged into the corpus (TASKS row 'Analytic labels for the corpus', ≈ 24–29 Oct), so that both
arms train and are read on analytic labels — the target loss was measured on those; FD noise would blur the difference. Through
`tools/runspec.py` as a chain spec.

## Read-outs

From each training record's per-seed read-outs (`curve → per_seed → hold-out`): the ring-ip diagonal rms (`diag_rms["ring-ip"]`, cm⁻¹)
and the ring-coupling ratio, the two read-outs in which the target loss was found; the other families reported beside. Arms are compared
**paired by seed**: d = P − R per seed (positive = R better), mean and standard error over the three seeds.

## Lines

1. **R pays on large molecules (setting C, full pool, hold-out (s)):** mean d ≥ 0.5 cm⁻¹ in ring-ip (half the target loss measured at
   ≥ 24 atoms) or mean d ≥ 0.05 in the ring-coupling ratio, in either case with mean d > 2 SE.
2. **R costs nothing elsewhere (setting F, hold-outs (a) and (b)):** in every band family R's seed mean ≤ 1.10 × P's, and R's ring-coupling
   ratio ≤ P's + 0.03.

**Still learning (setting C):** if line 1 is missed, R's advantage is 'still growing' when d(full) > d(half) + 2·√(SE_full² + SE_half²) in
the read-out that missed. Then the miss is data-limited, not a verdict.

**What follows (registered now):**
- lines 1 and 2 met → R becomes the recipe candidate (decision 57's promotion checklist; a new carried version only through it); the
  chains still waiting to train (chain 43, rung 4's read) take the carried recipe as it stands when they start, so a promotion before
  their start is written into their specs, dated;
- line 1 met, line 2 missed → R is not adopted as is; the guard family is named and a combined target (R where it helps) is designed and
  registered;
- line 1 missed, still growing → data-limited: the comparison is repeated after the next data step (lever 5's labels or rung 4), same lines;
- line 1 missed, flat → the ridge target is not learnable enough at this size: the third target is registered — the read-out-metric target
  (the least-squares ΔF for the whole K that `probes/hybrid_form_floor.py` computes, anchored by a ridge toward the projected truth as
  `rungC_targets` anchors the LS target) — built and tested first.
- No scope-reducing fallback: a line is not read on a subset of (s) or of the families.

## My prediction (before any training)

R's bound advantage is about 1 cm⁻¹ on (s), and a network realises part of it: line 1 met in ring-ip with d ≈ 0.5–0.8 cm⁻¹, not in the
couplings (d ≈ 0.02–0.04); line 2 met. Less likely (one in three): flat, as chain 10 at 750 — then the third target.

## Outcome

(to be appended)

## Note (15 Oct 2026, 23:2x; before any training) — 'half' made precise

'Half of the pool' in setting C is `rungC_train --sizes half`, i.e. the first ⌊N/2⌋ molecules of the size-split pool in its hash order (the
trainer's own order for every pool size), N known only on the merged corpus. Spec: `probes/runs/chain44.json`. No line changes.
