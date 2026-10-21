# Design — the few-anchor transfer checked on a second correction (21 Oct 2026, 06:5x; the user's item 2 of 06:3x; desk, no run)

## The question

Set three's diagnosis (`Diagnosis_2026-10-21_Set_Three_Read.md`, exploratory) found that fine-tuning the whole head on a few CC anchors
halves the held-out error, where the last layer alone could not even fit the anchors. That finding rests on eleven anchors, and the
protocol was chosen on them. The open question is general: **does a base model that learned one correction move to a different
correction from about ten labelled molecules, and does the whole head do it better than the last layer?** Read on hundreds of held-out
molecules, not eleven, it gives the T3 transfer a test the CC anchors cannot give before July 2027 (decision 63).

## What exists, and what does not

The corpus has two levels per molecule, B3LYP and ωB97X with 6-31G* at the same geometry (job.json). 1230 molecules have both
Hessians; 601 have both as analytic labels (counted 21 Oct from the per-molecule files). **There is no third level.** The base models
(chain 34) learned ωB97X − B3LYP. A second correction therefore has to be computed: some level T, giving T − B3LYP at the B3LYP
geometry.

## The analogue

| CC case | proxy check |
|---|---|
| low level B3LYP | B3LYP (corpus) |
| proxy correction the base learned: ωB97X − B3LYP | the same; chain 34's models unchanged |
| target correction: CCSD(T) − B3LYP on 11 anchors | T − B3LYP on k fine-tune molecules |
| leave-one-out on the anchors | read on every molecule with a T label outside the fine-tune set |

Arms, the same as set three: no fine-tune (the base as it stands), last layer at λ = 1 (the registered protocol), the head at λ = 0, the
whole head (`--head-all`); the zero rule beside them. Along k (for example 2, 5, 10, 20), with subsets and the three seeds, so the
learning curve is read and not one point.

## What makes the check informative

The CC correction runs against the proxy in the out-of-plane families (alignment c = −0.59 in the diagnosis' decomposition). If T − B3LYP
were nearly parallel to ωB97X − B3LYP, any fine-tune would pass and the check would prove nothing. So the alignment of T − B3LYP with the
proxy, per family, is measured on the first molecules **before** the lines are registered, and a T is chosen whose out-of-plane alignment
is far from +1.

Two candidates for T:

- **(X) GFN2-xTB** at the B3LYP geometry. Its tool exists (`probes/xtb_hessians_for_qff.py`, xtb 6.7.1 in WSL). It is cheap, and its
  correction is far from the proxy's, so it is a hard case. Two drawbacks: it is not a DFT, and at a geometry that is not its own minimum
  its Hessian carries a gradient term. On 19 Oct a naphthalene-sized Hessian took about 70 s at `--acc 0.01`, with jobs running in
  parallel; one molecule is timed alone before pricing.
- **(D) a third DFT** (for example PBE0 or TPSSh, 6-31G*, pyscf analytic Hessians). This is the faithful 'two DFTs' version. Cost: a
  24-atom corpus molecule took 2816 s for the B3LYP analytic Hessian and 3433 s for ωB97X (its `analytic_check.json`). A few hundred
  molecules therefore take days of laptop time; small molecules cost less. Timed on one molecule before pricing.

## Order, and what waits for the user

1. The laptop is first set three's whole-head repeat (running since 06:40), then the cation restart (P3-2). The labels' larger half
   (24–29 Oct) has priority. Nothing here runs beside them.
2. On the laptop when it is free: time one molecule for X and one for D, and measure the per-family alignment of each with the proxy on
   about ten molecules. This is a measurement, not a read.
3. Then the user chooses T and the number of molecules (cost against alignment). The lines are registered after that and before any
   fine-tune: the error of each arm against the zero rule and against the base on the held-out molecules, per family, with the
   learning-curve rule.

No paid compute (decision 63, spending pause).
