# Design note, 3 October 2026 — how a training pool is composed (the coverage rule)

*Decision 52 points here. Written 06:3x after the night's chains 28–30; the user: "Eigenlijk willen we goed zijn op alle families. Maar ik snap dat kosten
meetellen. Waar zullen we je rekenregel bewaren?" Every number below traces to a record file named in the table; the rule changes only through a dated
addendum with a new measurement.*

## The rule

1. **Coverage is per scaffold family.** A hold-out molecule is predicted well when its scaffold family (the ring skeleton, substituents aside) is in the
   training pool, and badly when it is not. Count beyond coverage adds nothing (620 molecules = 750 when the families are the same).
2. **A family is covered by a few dozen substituted children.** The first ≈ 30 buy three quarters of the gain; ≈ 60 buy nine tenths; beyond that nothing
   measurable. The children must be spread over substituents and positions (the measured 31 were a hash-ordered sample, i.e. mixed).
3. **Families help their neighbours a little.** Removing all three-ring and pyrene molecules worsened the never-seen fluorene and fluoranthene scaffolds
   by 0.06–0.10; chain 31 measures the within-three-ring neighbour effect (addendum below when read).
4. **Composition of a new pool:** breadth first — every scaffold family the pipeline must serve gets ≈ 30 mixed children; the families where the best
   accuracy is wanted get ≈ 60; then the next family, not more of the same. Seven of a family is noise (the pyrenes).
5. **Cost:** at the corpus route ≈ 1–3 h per molecule on a CPX62 (two runners), a family of 30 is a day, of 60 two days; one server-week covers three to
   six families. The aim stated by the user is good on *all* families; the order of families is therefore a cost decision, not the number per family.

## The evidence (carried recipe: pattern f, projected target, pattern + 0.3 kring + 0.1 K-diagonal, 3 × 64 sum body; three seeds each)

| chain | pool | (a) ratio | three-ring parents (phenanthrene / phenanthridine / biphenylene) | single-ring parents (benzene / biphenyl / benzonitrile) | (b) ratio | fluorene | fluoranthene | record |
|---|---|---|---|---|---|---|---|---|
| 28 control | first 620 of 750 | 0.229 | 0.15 / 0.16 / 0.15 | 0.06 / 0.24 / 0.10 | 0.349 | 0.30 | 0.37 | `out/E7_rungC_coverage_control620_2026-10-02.json` |
| 28 ablation | 750 − 130 (≥ 3 rings) = 620 | 0.373 | 0.48 / 0.52 / 0.34 | 0.11 / 0.23 / 0.13 | 0.411 | 0.40 | 0.41 | `…coverage_ablation620_2026-10-02.json` |
| 29 no-ring4 | 750 − 7 pyrenes = 743 | 0.221 | 0.15 (mean) | — | 0.354 | 0.29 | 0.39 | `…coverage_noring4_2026-10-02.json` |
| 29 no-ring3 | 750 − 123 three-ring = 627 | 0.369 | 0.46 / 0.49 / 0.41 | — | 0.418 | 0.40 | 0.43 | `…coverage_noring3_2026-10-02.json` |
| 30 keep25 | 31 of the 123 kept (658) | 0.249 | 0.18 / 0.18 / 0.29 | — | 0.351 | 0.31 | 0.37 | `…coverage_ring3keep25_2026-10-03.json` |
| 30 keep50 | 62 of the 123 kept (689) | 0.224 | 0.17 / 0.16 / 0.16 | — | 0.343 | 0.32 | 0.35 | `…coverage_ring3keep50_2026-10-03.json` |

Hold-out (a) = ten layer-A parents; hold-out (b) = 39 molecules on the fluorene and fluoranthene scaffolds, which the pool never contains. The three-ring
parents' own children are what the ablations remove. Registrations and outcome sections: `PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`
(amendments 17:2x, 22:0x, 01:1x, 04:1x and their outcomes).

## How the rule is used

- **Choosing the next pool:** `probes/rungC_error_map.py` names the weak and uncovered kinds from the latest records; the candidate list is then grouped by
  scaffold family and cut at ≈ 30 (or 60) mixed children per family, breadth first. The running 200 (`out/next_pool_candidates_2026-10-02.csv`) were chosen
  before this note; they fit it roughly (55 four-ring A2 rows across pyrene / fluoranthene-type parents, 8 three-ring, 137 fused two-ring B).
- **Reading a result:** a hold-out family's error is compared with how many of its children the pool holds before anything is concluded about the model.
- **Pricing a request** (module 08, the Spectrum Atlas): a molecule of an uncovered family is quoted as "its family first": ≈ 30 children at the corpus
  route, then the molecule.

## What would change the rule

- Chain 31 (neighbour coverage within the three-ring systems) decides whether a new family starts from its neighbours' level (then fewer than 30 may do
  while neighbours exist) or from zero.
- The 200's four-ring rows decide whether four-ring families behave like the three-ring one (the pyrenes at seven said nothing).
- A finer curve (≈ 45 kept) would locate the knee between 31 and 62; not worth a lane until a pool decision depends on it.
