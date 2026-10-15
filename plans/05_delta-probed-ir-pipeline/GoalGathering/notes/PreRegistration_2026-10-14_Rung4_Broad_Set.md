# Rung 4 as a broad set — does the network hold a rung of new four-ring families, tested on a whole family it never saw? (registered 14 Oct 2026, 20:2x, before any rung-4 label exists)

*TASKS 61, step 1; design note `Design_2026-10-14_Rungs_4_5_Broad_Sets.md`. The user, 14 Oct evening: the ladder is climbed slowly (decision 39)
and 'een trede is … een zo groot mogelijke set van moleculen van die orde van grootte'; 'tetraceen akkoord' (the held-out family); 'Ja, begin
maar met 1 en 2' (the frozen list and this registration). Where it runs is the user's decision of 15 Oct; nothing here depends on the place.*

## Why

Rung 4 (four rings, 26–34 atoms) holds 84 finished molecules in two scaffold families, fluoranthene and pyrene; the five other closed-shell
four-ring benzenoids have no finished row. A climb to rung 5 tested on two families reads nothing about the rung. This test fills rung 4 with
four new families and asks whether the network then holds a fifth family of the same size that it never saw.

## Data (frozen now)

`probes/rung4_candidates.py` → `modules/05_support_predictor/out/rung4_candidates_2026-10-14.csv`, sha256
`cb854acef18d01768262e03527fe75dde78a75926130e2634e7d5df5d752694e` (tests `tests/test_rung4_candidates.py`, 6 passed): 150 rows, 30–34 atoms —
tetracene, chrysene, benz[a]anthracene, benzo[c]phenanthrene, triphenylene, each the parent plus 29 mono-substituted children (layer B's 15
substituents, substituents before positions). **Tetracene's 30 rows are the test family** (test_family = 1, never trained). The four training
families carry curve_rank 1..30 (parent first, then generation order), so every curve point below is a nested, breadth-first subset.

**Labels:** the analytic route of every layer since 5 Oct (`corpus/analytic_hessians.py`: B3LYP and ωB97X Hessians, route-C APT with the
residual check, the software stamp), geometry optimised by the corpus's own step. **Price** (labels server lane fit, measured to 307 basis
functions; rung 4's rows have 294–324): 1,214–1,243 lane-hours — on the CCX53 12.6–12.9 days, €259–266; on a CPX62 unmeasured, priced by its
first molecule. **Stop rule:** a molecule taking more than 1.5 × its fitted price (column lane_hours_hi) stops the batch for a re-price; a
failed or noisy molecule is re-run once by the route's retry and named; none is dropped silently.

## Trainings and read

- **Model:** chain 34's carried recipe (decision 55: `MODELS_STATUS.json`, status carried), `--use-analytic`, three seeds (0, 1, 2), decision
  51's early stopping with the best epoch reported (a best epoch within 10 % of the cap is re-run with a higher cap before the read).
- **Pool:** the corpus as it stands at the read — with pool 3 merged — plus the rung-4 training families at **k = 0, 10, 20, 30 rows per
  family** (ranks > k excluded by `--exclude-ids-file`, one file per k written from the frozen list); tetracene's 30 are in every exclude file.
  Hold-outs (a), (b) (frozen list of 8 Oct), (c) unchanged.
- **Read:** `probes/rungC_eval_saved.py <model> … --use-analytic --eval-ids-file tetracene=<the 30 ids>` (refuses a set that shares an id with
  training): per band family (CH-stretch, CH-oop, ring-ip, other) the corrected-ω rms on tetracene's rows and the ring-coupling ratio, seed mean ±
  SE over the three seeds, per k.

## Lines

1. **Rung 4 holds** (decision 39's go/no-go, its 2.5 cm⁻¹): at k = 30, every band family's corrected-ω rms on the tetracene family ≤ 2.5 cm⁻¹
   (seed mean). → Step 2 (rung 5) may be proposed, priced and registered.
2. **Reported beside, no line:** the transfer without rung-4 data, e(k = 0) per family, and q₄ = ring-coupling ratio at k = 0 / at k = 30 (how
   much the rung's own data buys; chain 39 read q = 1.96 for size alone).

## Learning curve (the 'still learning' rule)

e(k) = the per-family corrected-ω rms on tetracene, seed mean, SE over seeds. **'Still learning'** for a family: e(30) < e(10) − 2·√(SE₁₀² +
SE₃₀²) and e(30) < e(20).
- **Line 1 missed for a family while it is still learning: not failed — data-limited.** Next, registered now: the four training families to
  60 rows each (decision 52's 'finish'), the next 30 per family by the same generator (`family_children` with quota 59, the 30 frozen rows kept
  as the first 30), priced from that list on the same fit, put to the user with its price; the read repeated at k = 60.
- **Missed with a flat curve:** no verdict at 30. The search first — is the miss one family? one C–H adjacency class (tetracene's four solo
  hydrogens on its inner rings are a class that rung 3 has only in anthracene)? a feature the model lacks (adjacency class as input) or a
  model-class question? Each candidate read on the same split; only a curve that stays flat after the search reads as 'rung 4 does not transfer
  to a new family of its size', and the next idea is registered then. The goal stays.
- **No scope-reducing fallback:** the test family is not swapped, a family that cannot be computed is re-priced and the read waits for it, and a
  miss is never narrowed to the families that passed.

## Before the read (tools, not run yet)

Pool 3 merged (`tools/fetch_corpus_shards.sh … merge`, after both runners end); the rung-4 rows appended to the manifest
(`rung4_candidates.py --write-manifest`, which moves the five parents' layer-G twins) after the user picks the place; the k exclude files
written from the frozen CSV by a small script with a test; one chain spec in `probes/runs/` (chain_runner), dry-run before it starts.

## My prediction (before any label)

e(0) misses 2.5 cm⁻¹ in CH-oop on tetracene (solo hydrogens, rare below rung 4) and meets it in CH-stretch; at k = 30 ring-ip and CH-stretch
meet the line, CH-oop does not but is still learning, so the most likely outcome is 'data-limited → 60 per family'. q₄ between 1.3 and 2.

## Note (15 Oct 2026, 00:1x, before any rung-4 label) — where chain 39's size penalty sits; exploratory

No line and no prediction above changes. `probes/size_penalty_per_family.py` on chain 39's two records
(`probes/results_m1/size_penalty_2026-10-15/chain39_per_family.md`), hold-out (s) of ≥ 27 atoms, size run ≤ 20 atoms against the control
of every size below 27, ratio of seed means (range from the seed extremes): ring-coupling ratio 1.96 (1.76–2.18), ring-ip diagonal **1.70
(1.57–1.87)**, 'other' 1.34 (1.16–1.54), CH-stretch 1.27 (1.05–1.48), CH-oop 1.33 (0.85–2.04, not resolved from 1). The size penalty sits in
the ring in-plane physics — the modes delocalised over fused rings — which is what a rung of new four-ring families feeds. My registered
prediction named CH-oop as the likely miss at k = 30; on this evidence ring-ip is at least as likely. Recorded so that the read can say which.

## Place (15 Oct 2026, 08:1x; the user: 'Trede 4 draait op de CCX53 na hefboom 5')

The labels server (CCX53), after lever 5. Nothing above changes. Armed: `probes/labels_batch_ccx53.sh` (lever 5's runner pattern with the
batch and its wait condition as arguments) in /root/labels/rung4 waits for '=== (L5) all done', then optimises the 150 (psi4, corpus deck,
no Hessians; jobs from `probes/rung4_jobs.py`, start geometry `run_corpus.start_geometry`) and labels them (analytic_hessians.py), four lanes
× 8 threads. The test family is held out structurally: `corpus/holdout_rung4_test.txt` (30 ids) is read by `E6.splits`, as hold-out (c).

## Outcome

*(empty until the read)*
