# Pre-registration, 4 October 2026, 11:3x — the candidate generator's batch route, steps (a) export and (b) gate with the niche test (TASKS row 22; the user: "Eens met je voorstel: de batchroute")

*Registered before any sample is drawn. The question: does module 06's candidate generator (v0.1 unconditioned, v0.2 conditioned; both `experimental`
in `modules/06_generative_candidates/MODELS.md`) propose enough new, computable ring skeletons to be a registered source for the corpus manifest? The
manifest's own enumeration (`corpus/build_manifest.py`) substitutes 19 listed cores and invents none, so "new core" is the only thing the generator can
add. This read decides whether step (c), a layer G in the manifest, is built; it prices nothing else.*

## Sample plan (step a, `m06/propose.py`)

- **Unconditioned, v0.1:** seeds 0 and 1 (the two checkpoints that exist; seed 2's checkpoint was never written), 10,000 samples each at temperature 1.0
  — the registered temperature of the 26 September read (validity 0.92, novelty 0.91, scaffold novelty 0.53 against the training set).
- **Conditioned, v0.2 (cond_seed0):** the four requests that name what pool 3 lacks — `<r3> <hnone>`, `<r4+> <hnone>`, `<r3> <hN>`, `<r4+> <hN>` —
  2,500 samples each at temperature 1.0 (obedience measured 26 Sep: 0.73–0.94 on these requests).
- Seeds fixed in the script (`seed * 7919 + chunk`, the module's own rule); the checkpoint hashes and the registry status in the output; the models are
  `experimental`, so the registry guard is passed with `--allow-any-model` and this note names that use.

## Gate (step b, `m06/gate.py`), in order, on the de-duplicated canonical SMILES

1. parses (RDKit); 2. neutral and closed shell (no formal charge on any atom, no radical electrons); 3. elements within C H N O S F Cl;
4. ≤ 30 heavy atoms; 5. at least two fused aromatic rings (`m06/evaluate.project_fit`); 6. not already in the manifest (canonical SMILES against every
manifest row with a SMILES, layers A, A2, B, P3, P3c); 7. **the niche test:** the Murcko scaffold is neither a listed core nor the scaffold of any
manifest row — a new ring skeleton, not a new substituent on a known one.
Columns, not gates: whether the molecule itself is in the frozen PubChem set (`data/pubchem_aromatics_2026-09-24.csv`; a known CID is a plausibility
flag), the ring class (2 / 3 / 4+ aromatic rings), the heteroatom class, and how many samples and which runs produced it.
Output: every sample with its stage (`out/proposals_<date>.csv`), the passing list sorted by (in PubChem set first, occurrences, SMILES) with its
SHA-256 (`out/proposals_<date>_gated.csv`), a summary json and md with the counts per stage, per run and per family.

## Predictions (on record)

Per 10,000 unconditioned samples: ≈ 9,200 parse; ≈ 8,000 pass stages 2–5 (project fit was 0.945 of the valid); ≈ 7,500 are not in the manifest
(the manifest holds 5,300 children of 19 cores against a 161,000-molecule prior); the niche test keeps 40–60 % of those. Across the 30,000 samples:
**2,000–6,000 distinct new scaffolds**, of which 10–30 % are themselves molecules of the PubChem set. The conditioned runs obey their request in
70–90 % of samples and give ≥ 50 distinct new scaffolds in each of the four classes. If the predictions are far off on the low side the cause is
expected to be the niche test: Murcko scaffolds of substituted systems with linkers count as "new" rarely, and most proposals re-use the 19 cores.

## Lines

- **≥ 300 distinct new scaffolds that are molecules of the PubChem set, or ≥ 1,000 distinct new scaffolds overall, with ≥ 20 in each of the four
  requested classes** → the generator is a registered source: step (c) is built (layer G, status pending, `source=generator v0.x <hash>`; the
  composition rule and the steward decide what is computed), the gated list is the frozen candidate list, PubChem-known scaffolds ranked first.
- **Fewer than 100 distinct new scaffolds** → not a source at this size; the generator stays 0.x; new cores enter the enumeration by hand.
- **In between** → a conditioned run at ten times the request sizes decides, registered as a dated amendment before it runs.

## Cost and place

Sampling ≈ 40,000 strings at 4 threads, of the order of an hour (10,000 took 540 s in the 26 September run); the gate, minutes. The run sits in the
laptop's afternoon queue (`probes/afternoon_1004.sh`) after chain 34c has released its threads; nothing of it touches the TZ run. Tests:
`tests/test_m06_gate.py` (every stage on hand-made molecules, determinism of the list and its hash, the loader of a run). Nothing in the manifest or
on the website changes before this read is on record.

*Dated amendment 4 October 11:4x, before the registered run (after the 250-sample smoke of the mechanics on seed 0 and one conditioned request):* the
niche test's object is the molecule's **largest fused aromatic ring system** (aromatic rings joined by shared atoms; substituents, linkers and side rings
removed; `m06/gate.py ring_system`), not the Murcko scaffold. The smoke showed why: Murcko scaffolds keep linkers and side rings, so 186 of the 195
molecules that reached stage 7 counted as "new" — a methyl-naphthalene with a phenyl linker is not a new ring skeleton. The ring-system test is the
stricter one; the predictions and the lines above now refer to **distinct new ring systems** with the same numbers (2,000–6,000 predicted; lines at
≥ 300 PubChem-known / ≥ 1,000 overall with ≥ 20 per requested class; < 100). The Murcko scaffold stays a column. The smoke's other numbers, for the
record and not as a read: 94 % parse (prediction 92 %), 11 of 250 above 30 heavy atoms, 4 without two fused aromatic rings, none already in the manifest.

## Outcome, 4 October 2026, 13:2x — the middle branch: 881 new ring systems, 216 of them PubChem molecules; a ten-fold conditioned run decides

Export 12:14–13:20 (`out/proposals_2026-10-04.{csv,json}`, 4 threads beside the TZ run): seed 0 10,000 samples in 1,313 s, seed 1 10,000 in 2,625 s,
cond_seed0 4 × 2,500 in 1,342 s; checkpoint hashes and the `experimental` status in the json. The gate's first run failed at the per-class table (a cut
aromatic fragment RDKit could not re-parse; `ring_system` now keeps an unsanitised canonical key and `ring_class` counts rings without aromaticity
perception for such a key; tests 5/5) and was re-run at 13:25 on the same export (`out/proposals_2026-10-04.md`, `_summary.json`, `_staged.csv`,
`_gated.csv` SHA-256 `69f25509e1c4…`).

| stage (first failed) | distinct SMILES | prediction |
|---|---|---|
| samples / distinct canonical | 30,000 / 28,309 | — |
| parses | 3,947 fail (86 % parse) | 92 % — the conditioned run parses 76 %, the unconditioned 92 % |
| neutral, closed shell | 3 | — |
| > 30 heavy atoms | 912 | — |
| fewer than two fused aromatic rings | 290 | — |
| already in the manifest | 177 (0.7 %) | ≈ 5 % |
| known ring system (the enumeration can make it) | 15,967 (69 % of those reaching the niche test) | 40–60 % kept → 31 % kept |
| **pass** | **7,013 molecules, 881 distinct new ring systems** | 2,000–6,000 systems |

Of the 881 systems, **216 are themselves molecules of the PubChem set** (25 %; predicted 10–30 %); 846 of the 7,013 passing molecules are PubChem
molecules. Per requested class (new systems): `<r3> <hN>` 243, `<r4+> <hN>` 198, `<r4+> <hnone>` 85, **`<r3> <hnone>` 13** — the hydrocarbon three-ring
skeletons are nearly all known already (the manifest's parents cover them); the generator's novelty is in the heteroatom systems.

**Lines.** ≥ 300 PubChem-known new systems: no (216). ≥ 1,000 new systems with ≥ 20 per class: no (881; `<r3> <hnone>` 13). < 100: no. **The middle
branch:** a conditioned run at ten times the request sizes decides, registered below before it runs. The prediction of 2,000–6,000 systems was too
high by a factor of two to seven: the niche test keeps 31 % rather than 40–60 %, because most proposals decorate a known skeleton.

*Dated amendment 4 October 13:3x (the ten-fold run, registered before it runs):* `cond_seed0` (v0.2), the same four requests at 25,000 samples each
(100,000 strings, ≈ 4 h at 4 threads), appended to today's export and gated together (`out/proposals_10x_2026-10-04.*`; the gate counts distinct
systems over the union, so today's 881 are included). Predictions: distinct new systems grow sub-linearly — 1,500–2,500 in the union, PubChem-known
350–600; `<r3> <hnone>` stays under 40. **Lines on the union, unchanged in their numbers:** ≥ 300 PubChem-known new systems or ≥ 1,000 overall with
≥ 20 in each of the four classes → a registered source (step c follows); otherwise not a source at this size, the generator stays 0.x. Runs tonight
after the notebook re-executions (`probes/batch_route_10x_1004.sh`, 4 threads beside the LNO cells' 12).

## Outcome of the ten-fold run, 5 October 2026, 19:0x — both lines met on the union: the generator is a registered source

`cond_seed0` × four requests × 25,000 (14:55–19:00, 4 threads; 100,000 strings, 75.6 % parse) appended to the 4 October export and gated on the union
(`out/proposals_10x_2026-10-04.{csv,md,_summary.json,_gated.csv}`, SHA-256 of the frozen list `a71f2283…`, gate 224 s). 130,000 samples, 96,469 distinct;
25,905 do not parse, 2,400 exceed 30 heavy atoms, 1,034 lack two fused aromatic rings, 259 are already in the manifest, 43,099 sit on a known ring
system; **23,769 pass, on 2,272 distinct new fused aromatic ring systems, 308 of which are themselves PubChem molecules** (1,655 of the passing
molecules are). Per requested class (new systems): `<r3> <hN>` 558, `<r4+> <hN>` 760, `<r4+> <hnone>` 426, `<r3> <hnone>` 25.

**Predictions.** 1,500–2,500 systems: 2,272, inside. PubChem-known 350–600: 308, below. `<r3> <hnone>` under 40: 25, inside — the hydrocarbon three-ring
skeletons are known already; the generator's novelty is in nitrogen systems and in four-ring and larger hydrocarbons (426).

**Lines.** ≥ 300 PubChem-known new systems → **met (308)**; ≥ 1,000 new systems with ≥ 20 in each of the four requested classes → **met (2,272; 25 / 426 /
558 / 760)**. The generator is a registered source for the corpus manifest. Step (c) follows, as registered, with one design choice made here before it is
built: **layer G holds one representative molecule per new ring system** — the most frequent passing molecule of that system, ties by SMILES — PubChem-known
systems first, then by the system's occurrence count (2,272 rows, not the 23,769 passing molecules; the enumeration can add substituents to a listed
system later, which is what a new *core* is for); status `pending`, note `source=generator v0.1+v0.2 <gated sha>`; hold-out membership by the seeded rule
when a pool draws from it; what is computed stays with the composition rule (decision 52) and the steward. Step (d), the Atlas: a `source` field
(enumeration / qm9 / generator) and a label, after (c). Version 1.0 for the generator at the first pool that carries its molecules.
