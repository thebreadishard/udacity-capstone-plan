# Module 05 — provenance and status (project notes)

## What was verified on 2026-09-12 (no download made)

| item | record | verified via |
|---|---|---|
| Hessian QM9 paper | Williams, N. J., Kabalan, L., Stojanovic, L., Zolyomi, V., & Pyzer-Knapp, E. O. (2025). *Scientific Data*, DOI 10.1038/s41597-024-04361-2 (arXiv:2408.08006, 15 Aug 2024) | Crossref, arXiv |
| Hessian QM9 data | figshare, DOI 10.6084/m9.figshare.26363959 (v4, **6,294,531,943 bytes ≈ 6.29 GB**); 41,645 molecules, ωB97x/6-31G* Hessians in vacuum, water, THF, toluene | DataCite |
| Fixture | `probes/results_dryrun/benzene/stageA_hessians.npz` (B3LYP → BHHLYP, 6-31G*, M = 30; `D2_direct_Q`), sha256 `f6e4d4b3…`; `benzene_quick` is the same tensor | local |

## Download done (2026-09-12, user's permission given in chat)

Figshare file 49271011 `hessian_qm9_DatasetDict.zip`, 6,281,831,499 bytes, md5 `f3e36130e5cc47021ab403767a19ddf7`
(matches the figshare record), sha256 `ce595041d718b2df…`; fetched detached (`data/hessian_qm9/fetch_hessian_qm9.ps1`,
resumable curl). The archive holds four splits (vacuum, thf, toluene, water; 9.47 GB unpacked); **only `vacuum/`
is extracted** (2.37 GB, five Arrow stream shards, read with pyarrow). Inventory printed by
`m05/inspect_hessian_qm9.py` → `out/HESSIAN_QM9_SUMMARY.md/.json`: **41,645 molecules**; fields energy, positions,
atomic_numbers, forces, frequencies (n×2), normal_modes, hessian (N,3,N,3; symmetric), label (`dsgdb9nsd_…`, the QM9
index); heavy atoms 1–9 (36,027 molecules with nine); **aromatic-like composition proxy (n_C ≥ 6, n_H ≤ n_C): 2,120
molecules (5.1 %)**, labels saved — an upper bound for the recomputed B3LYP subset, not its size. Units and
conventions of the fields are to be taken from the paper before use (not yet read; owed). The record metadata is
kept in `out/figshare_record_26363959.json`; the archive and shards stay out of git.

The corpus itself does not exist yet. Its remaining halves are owed as follows.

## Owed, and by whom

1. ~~The download~~ — done 2026-09-12 (above). **Paper read the same day** (arXiv 2408.08006 text, 7 pp.; methods,
   data records, Table 1): NWChem, ωB97X/6-31G*, geometries optimised in vacuum with NWChem defaults, **numerical
   Hessians by finite differences with 0.01 a.u. displacement** (their test: 0.005/0.01/0.02 a.u. changed
   frequencies by < 15 cm⁻¹ on average — the numerical noise floor of these Hessians, to be remembered when Δ₂
   labels are thresholded); SCF converged to 10⁻⁶ eV; only H, C, N, O (fluorine dropped); 41,645 of the 133,885 QM9
   molecules chosen by UMAP + farthest-point sampling. **Units (Table 1):** positions Å, energy eV, forces eV/Å,
   Hessian eV/Å², frequencies cm⁻¹, normal modes dimensionless (3N × 3N). The file's `frequencies` field is 3N × 2,
   not the paper's 3N × 1 — **checked 2026-09-12 by reconstruction**: mass-weighting the stored Hessian (eV/Å²,
   isotopic masses) and diagonalising reproduces column 0 to within 0.4 cm⁻¹ (e.g. 3563.6 vs 3563.3) and gives
   negative eigenvalues exactly where column 1 is non-zero (109.9, 80.0, 67.6 cm⁻¹ imaginary in the example), so
   **column 0 = real frequency, column 1 = magnitude of an imaginary frequency**. The translations and rotations are
   *not* projected out: the example's six lowest modes are three imaginary (68–110 cm⁻¹) and three small real
   (12–117 cm⁻¹), the signature of an unprojected numerical Hessian. Any Δ₂ built from these Hessians must project
   out translation and rotation first, and the ~15 cm⁻¹ displacement sensitivity the paper reports is the noise
   floor for its labels. Ring detection is done from geometry (`m05/ring_survey.py`, bonds from covalent radii, cycle
   basis of the bond graph, planarity 0.1 Å RMS), so no QM9-SMILES download is needed. **Result
   (`out/HESSIAN_QM9_RINGS.md`, 2026-09-12): 36,760 molecules (88 %) contain a ring, but only 66 (0.2 %) contain an
   all-carbon aromatic six-ring — benzene itself once — while 6,055 (14.5 %) contain a planar conjugated five- or
   six-ring of C/N/O (pyridine-, pyrrole-, furan-like included).** Ring sizes in the cycle basis: 3: 18,884; 4: 11,305;
   5: 17,388; 6: 8,900; 7: 4,222; 8: 2,137; 9: 556. **Consequence for the plan's "aromatic-heavy subset"
   (Capstone_Mapping §M05):** with at most nine heavy atoms and a UMAP/farthest-point selection, Hessian QM9 holds
   almost no benzene-ring chemistry; the realistic over-represented class is *conjugated and heteroaromatic rings*,
   and the PAH held-out set is even further off-distribution than the mapping assumed. This goes to the user as a
   decision input (subset definition: 66 all-carbon rings + the 6,055 conjugated rings, or the conjugated class alone);
   it changes no frozen text by itself.
2. **The recomputed B3LYP subset** — laptop compute with the plan's psi4 deck; benzene took 388 s on the
   laptop (dry run 2026-09-05), QM9 molecules are smaller (≤ 9 heavy atoms), so the ~1,000-molecule
   figure in the memory notes is an order of magnitude, not a plan number. **The subset size is fixed by
   a dated note** after the naphthalene dry run prints its Hessian timing and the machine is decided (P13).
   Not while an anchor job runs.
3. **The Zenodo release** of the corpus (Δ₂ tensors, labels, deck hashes) — the user; before the module's
   official start.
4. **Reading-2 fallback** — a second public Hessian source, to be searched and verified; none named.
5. **The label threshold θ** and the P3 effect size — pilot-note item 5 (RECIPE gives θ = 0.1 as candidate).
6. The notebook (`deep_learning.ipynb`), the report in the APA template with the nine prescribed sections,
   the three required sentences (Capstone_Mapping §M05), and the student's pass.

## What the smoke test showed (code path only, not a result)

Fixture benzene: 30 modes, 435 possible pairs, 10 positive pairs at θ = 0.1; baseline network
117,569 parameters; twenty steps on one molecule bring the weighted BCE from 1.36 to 0.58 in 0.3 s on
CPU; the implied pattern count at recall 0.9 is printed. None of this generalises; it proves that
tokens, labels, model, loss and the K-metric run end to end.

## Files

- `RECIPE.md`, `README.md`, `m05/build_corpus.py`, `m05/model.py`, `m05/smoke_test.py`, `requirements.txt`.
- `data/` is git-ignored (fixture corpus and smoke-test JSON are regenerated by the two commands in the README).

## Skeleton of the deliverables (2026-09-12, evening)

`notebook/make_notebook.py` writes `deep_learning.ipynb` in the rubric's order (load/preprocess · baseline Transformer · one
controlled comparison · training outputs · evaluation · example behaviour · summary). Cells marked FIXTURE run on the benzene
dry-run tensor (code path only); cells marked STUB raise until the corpus exists — the submitted notebook must not contain
them. `REPORT_OUTLINE.md` maps the nine required report sections to their number sources. Neither was executed or
filled: both wait for the corpus factory's timing test (after the anchor job) and the dated subset-size note.

## Dated status note, 2026-09-22 07:1x

The scaffold of 12 September is overtaken on four points, recorded here so that nobody reads the old status as current: the corpus
factory runs (layer A 39 molecules done; layer A2 = E6, 4 × 50 on Hetzner since 19 September, phase 1 ≈ 23 September); the E-series of
19 September moved the target from a per-mode support bit to the family block (diagonal plus couplings) after E4 showed the per-mode label
ill-posed and E1/E1b/E2/E5/E5b did not survive 45 molecules — the learning-curve rule (no verdict on tiny data) governs E6; the architecture
names the network the ΔH model (block head, pair head) and its PyTorch file supersedes `m05/model.py` when the module is written; the
anharmonic step of the spectrum pipeline is settled on analytic pyscf Hessians (decision 46). Still owed as listed above: the subset
decision on Hessian QM9 (66 all-carbon rings), the Zenodo release of the corpus (the user), the notebook and report in the rubric form.
Code that ships goes through the promotion gate of `QUALITY_POLICY.md` (decision 47).

## Dated note, 2026-09-22 11:4x — rubric-form deliverables prepared (no results)

The user asked for preparatory desk work on the next module. Built and run end to end on the layer-A corpus (42 of 45 local molecules; three
skipped for an imaginary frequency at one level): `m05/build_release.py` → `data/corpus_release/layerA_2026-09-22.npz` (492 KB) with a manifest
that lists every input Hessian's SHA-256, the token layout and the target definition (K_ij in the B3LYP mode basis, RECIPE amendment of 19 Sep);
`m05/deltah_model.py` = the architecture sheet `GoalGathering/architecture/51_deltaH_model_pytorch.py` verbatim, refreshed and asserted identical by
`m05/sync_model.py` (forward pass checked: d_in 23, 135,875 parameters at two layers); `notebook/make_notebook.py` rewritten in the rubric's
structure (task type declared, load/inspect with samples and quality checks, baseline with the architecture shown and the design reasoning,
training with loss curves, the pre-registered one change 2 → 4 layers, evaluation per family against the zero and family-median rules and the
pair head against the resonance-denominator rule, a summary the builder fills from `results.json`); executed in quick mode (3 epochs, one seed,
two threads, ≈ 1 min) — `notebook/results.json` and the figures carry the quick flag and are not results; `make_summary.py` with the nine sections,
every number read from the result file and the manifest, four verified references, and a banner + no PDF whenever the results are quick.
`RUBRIC_CHECKLIST_2026-09-22.md` records the status per rubric item and the order of work when E6 lands. Open, unchanged: the Zenodo release
(the user), the Hessian QM9 subset decision, the full run, requirements from the environment of that run, promotion of the model to `src/dpir`.

**Dataset decision (the user, 22 September 17:2x: "begin met eigen corpus, daarna waarschijnlijk PC"):** the first full run of module 05 trains on the project's own corpus alone (layers A and A2, ≈ 240 molecules, both levels of theory on identical geometries). Hessian QM9 is not in that dataset — with at most nine heavy atoms and 66 all-carbon aromatic rings among 41,645 molecules it is off the plan's chemistry, and its labels would need the second level recomputed and carry ≈ 15 cm⁻¹ of numerical noise. It stays available as a pre-training source if the learning curve asks for more data; the first answer to such a demand is a layer A3 of the own corpus (200 more A2 candidates ≈ 3 days on four rented servers, ≈ € 75; the user leans towards buying the desktop PC for that and the M2 build). The E6 learning curve (≈ 23 September) is the arbiter, per the rule of no verdict on tiny data.

## Dated note, 2026-09-23 09:5x — the first full run (CCX53, fresh environment)

Release `data/corpus_release/layerA2_2026-09-23.npz` (224 molecules: 42 of layer A and 182 of layer A2, the 20 with an imaginary mode
skipped; 14607 modes; split by molecule 186/18/20). Executed on the rented CCX53
(`ubuntu-128gb-hel1-2`, 32 threads) in a fresh conda environment built from `requirements.txt` as frozen (torch 2.14.0+cpu, numpy 2.5.1) — that
execution is the fresh-environment check; the notebook ran top to bottom twice (the second pass fills the summary cell from the first pass's
`results.json`; both passes wrote identical numbers). 30 epochs, seeds [0, 1, 2], early stopping on the validation loss
(best epochs baseline [26, 29, 29], 4 layers [27, 29, 29]); parameters 135,939 and 235,907.

Test RMS in cm⁻¹, diagonal (band shift) / couplings inside the family block:

| model | CH-stretch | CH-oop | ring-ip | other |
|---|---|---|---|---|
| zero | 43.8 / 0.47 | 24.1 / 3.21 | 20.3 / 4.02 | 19.2 / 2.42 |
| family-median | 2.7 / 0.47 | 8.1 / 3.21 | 15.6 / 4.02 | 14.5 / 2.42 |
| baseline | 3.0 / 0.47 | 4.2 / 3.23 | 5.3 / 4.02 | 8.4 / 2.38 |
| 4 layers | 2.9 / 0.47 | 4.3 / 3.22 | 5.4 / 4.02 | 8.3 / 2.39 |

Pair head average precision: baseline 0.286, 4 layers 0.287, resonance rule 0.062.

Reading: the band shifts are learned — the model beats the family-median rule by a factor 2–3 on CH-oop, ring-in-plane and "other";
on the C–H stretches (shift nearly constant across the corpus) the median rule is as good. The couplings are not learned at this corpus
size: every family's coupling RMS equals the zero rule to two decimals, for both depths. The one controlled change (2 → 4 layers) makes
no difference beyond seed scatter. Best epochs of 26–29 out of 30 say the models were still improving; the epoch budget is a limitation
to name in the report, not a result. `requirements.txt` is now the `pip freeze` of the CCX53 environment. The E6 learning curve
(`m05/e6_learning_curve.py`, pre-registration of 19 September) runs on the same machine and answers whether the couplings are
data-limited; its outcome goes into the pre-registration file, not into this module's report.

## Dated note, 2026-09-23 14:4x — follow-up cells (section 7) after the user's decision ("pas maar aan... in vervolg-cellen in plaats van in vervangende")

The notebook gained a section 7 and was executed a third time, top to bottom, on the CCX53 (same environment; 16 threads). Sections 1–6 are unchanged in
source; their numbers moved within seed/thread scatter against the first two executions (ring-in-plane baseline 5.46 against 5.32 before; C–H out-of-plane
4.05 against 4.20) — this third execution is the deliverable, and `results.json` is its record. Section 7 shows, in this order: (7.1) the second-route check
of benzene (pyscf analytic vs the corpus psi4 finite-difference ωB97X Hessian: max disagreement 132 cm⁻¹, |ΔH| 2.1e-02 a.u.) and the corpus-wide
screen (`data/second_route/corpus_screen_2026-09-23.json`: 244 molecules, median max shift 48 cm⁻¹, 1 above 100); (7.2) the baseline retrained with the identical
protocol on the corrected release `layerA2_2026-09-23b.npz` (built with `m05/build_release.py --prefer-analytic`, benzene's Hessians from `corpus/analytic_hessians.py`;
benzene is in the **train** split): ring-in-plane 5.58 against 20.3 for the zero rule, C–H out-of-plane 3.98 against 24.1, pair AP
0.285; (7.3) the pre-registered E6/E7 curves side by side (mode-basis couplings at the zero rule at every size; local pairwise target
0.43 / 0.47 at 175 molecules, corrected frequencies 4.7 / 5.1 cm⁻¹); (7.4) what was learned. `results_followup.json` is the record of section 7 and feeds the
report's addendum (`make_summary.py`). The model of sections 2–5 stays the module's pre-registered baseline; the pairwise local target is the design
of the next version. Files added: `data/second_route/*.json`, `data/corpus_release/layerA2_2026-09-23b.*`, `corpus/analytic_hessians.py`, the screen in
`corpus/check_results.py`.

## Dated note 2026-09-24 13:2x — section 8 follow-up cells added (not yet executed)

`notebook/make_notebook.py` gained section 8 (five markdown cells, four code cells) after section 7, leaving sections 1–7 as run: 8.1 the twenty
imaginary-mode molecules read along the analytic second route (`data/second_route/imaginary_second_route_2026-09-24.json`: 5 healed, 15 genuine);
8.2 the baseline retrained with the identical protocol on release `layerA2_2026-09-24` (229 molecules; env `M05_RELEASE_FOLLOWUP2`); 8.3 E8's
reading of benzene's CCSD(T)/cc-pVDZ correction with the E7 projections (`probes/results_m1/e8_benzene_ccpvdz/E8_locality_benzene.json`,
`E8_between_benzene.json`); 8.4 what was learned. `make_summary.py` writes "Addendum 2" from `notebook/results_followup2.json` when it exists. The
scratch build (`--no-execute`) validates: 39 cells, every new code cell compiles. **Execution pending** until a 32-core machine is free of E8
(the CCX53 runs naphthalene until ≈ 26–27 September); the committed `deep_learning.ipynb`, `results.json`, report and PDF are still the 23 September
third execution.

## Dated note 2026-09-24 14:4x — section 8 executed append-only (CCX53, m05 env, 4 threads, 12:15–12:27 UTC)

`notebook/execute_section8.py`: a fresh kernel ran the setup cells (2, 4, 8, 10) and the *definitions* of cells 12 and 17, then the four new code
cells (29, 32, 35, 38); the outputs of cells 0–26 are the ones saved on 23 September (code cells verified identical to the generator; markdown kept as
run). Method and cell indices are in the notebook metadata (`append_only_execution`). Environment as on 23 September: `M05_RELEASE=layerA2_2026-09-23`,
plus `M05_RELEASE_FOLLOWUP2=layerA2_2026-09-24` by default. Results: `notebook/results_followup2.json` — 229 molecules, the five healed molecules all fall
into the training split by the sha rule (test set unchanged: 20 molecules), test RMS of the band shifts (diagonal) ring-in-plane 5.39 cm⁻¹ against 20.34
for the zero rule (section 3: 5.32; 7.2 on 224: 5.46), C–H out-of-plane 3.95, C–H stretch 2.63, other 8.50; pair-head average precision 0.290 (v1 0.287,
224: 0.285). E8 table read from `probes/results_m1/e8_benzene_ccpvdz/`. Report rebuilt with Addendum 2 (`make_summary.py`, docx and PDF, Word on the
laptop as before). No error cells; 39 cells.
