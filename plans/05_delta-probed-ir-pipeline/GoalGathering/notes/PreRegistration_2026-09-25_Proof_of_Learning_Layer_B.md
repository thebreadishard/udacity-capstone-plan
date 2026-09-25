# Pre-registration 2026-09-25, 07:0x — the proof that the network learns: the layer-B learning curve (the user: "Ja, doe de laag B run")

**Question (fixed).** Does the local ΔH model keep improving with data, on hold-outs that stand for the mandate's direction (bare cores, unseen
scaffolds, larger molecules), or does it plateau above the label noise? This is the user's success criterion for the design ("het bewijs dát het
netwerk leert is het allerbelangrijkste"). Written before any layer-B molecule is finished.

**Data (fixed).** Corpus layer B as defined on 12 September (`corpus/DESIGN_2026-09-12.md`, `build_manifest.py`): 4,353 mono- and di-substituted
aromatic and heteroaromatic molecules of 8–26 atoms in the hashed manifest order; deck v1 unchanged; computed as five shards on CPX62s
(`run_corpus.py --layer B --shard i/5`, shards 0 and 1 started 25 September on hel1-18 and hel1-21; 2–4 join as machines free up). Molecules with an
imaginary mode in either functional are excluded as in E6/E7, and the second-route screen of the corpus README applies before any table is read.
The learning-curve **training sets are the first 100 / 300 / 600 / 1,200 admitted layer-B molecules in the hashed order**, whichever shard
computed them; a table is read only when every molecule of its prefix is done or excluded (a missing one that is still pending blocks the table).
Layers A and A2 are **not** in the training pool of this test (they are the hold-outs); a second, secondary curve adds the A2 pool to each
training set and is reported beside the first.

**Hold-outs (fixed, disjoint from the training sets):**
- (a) **bare parents:** the layer-A molecules without a substituent (the 14 cores of A2 and the other layer-A aromatics), admitted ones only;
- (b) **unseen scaffolds:** E6's two scaffold cores and all their A2 derivatives (`E6.splits`), as in E7 rung B;
- (c) **larger than any training molecule:** the admitted A2 molecules with more atoms than the largest molecule in the training set at hand
  (layer B tops at 26 atoms; A2 runs to 30–34) — the size-extrapolation hold-out.

**Model (fixed for this test).** E7 rung B's pair model (`m05/e7_rungB_pairs.py`: MLP 2 × 128 on pair features, three seeds, plus the
gradient-boosted check) — the floor. When the equivariant ΔH model of the 23 September decision exists, the identical table is rerun with it;
that rerun is a separate dated section, not a replacement.

**Read-outs (fixed; E6/E7):** corrected-frequency RMS (same-family blocks) and ring coupling ratio to the zero rule on each hold-out at each
training size; ΔH residual ratio; the slope of log(ratio) against log(n) per hold-out; the second-route noise floor of the labels (analytic vs
finite-difference Hessians, per-mode RMS on the molecules that have both) printed beside the curve.

**Reading (fixed before any number):**
- **Pass ("the network learns"):** on all three hold-outs the corrected-frequency RMS and the ring coupling ratio decrease monotonically over
  100 → 300 → 600 → 1,200 (seed means; a single non-monotone step smaller than the seed spread does not break monotonicity), with a slope of at
  least a factor 1.5 per decade of data on (a) and (c), and any plateau no higher than three times the second-route noise floor.
- **Fail:** flat (slope worse than a factor 1.15 per decade) on (a) or on (c) — the model does not learn what the mandate needs from more data
  of this kind; the next step is then the model (equivariant, more capacity) or the data kind (bare cores, larger molecules in the pool), not
  more of the same.
- **Between:** anything else; the per-hold-out slopes say which direction is short of data and which of model.
- Intermediate tables (at 300, at 600) are read and recorded as they come but carry no verdict; the verdict is at 1,200.

**Not registered:** family breakdowns, the secondary curve's reading, and anything read from the equivariant rerun.

**Cost.** ≈ 1,700 CPX62-hours for the first 1,200 (≈ €400); the rest of layer B continues afterwards as corpus work. The tables themselves are
minutes on the laptop or a CPX62.

**Consequence of a pass.** The design's central claim is demonstrated on the proxy at the scale the corpus allows; the proposal of 28 September
cites the 300-table (if it exists by then) as the first point of a curve whose reading rule is on record here.
