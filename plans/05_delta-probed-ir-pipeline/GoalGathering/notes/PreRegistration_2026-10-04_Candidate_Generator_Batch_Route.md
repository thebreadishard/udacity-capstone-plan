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
