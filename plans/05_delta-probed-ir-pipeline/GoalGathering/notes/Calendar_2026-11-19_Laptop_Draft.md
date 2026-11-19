# The laptop's calendar, 20 Nov 2026 – 28 Feb 2027 (draft for the user, TASKS 192)

**Fixed points:** paid compute stopped on 15 Nov, so the laptop is the only machine (13 GB for all runs together, one training
at a time). The supervisor meets us Wed 25 Nov, morning, and the laptop must be free then (TASKS 154). The Udacity modules
02–08 are to be finished in December (TASKS 20), and module 09 comes in 2027. The capstone is submitted between 1 Jan and
30 Jun 2027, aimed at ready by the end of February. There are no new CC anchors before July 2027 (decision 63).
**Every duration below is an estimate (est.)** unless it says measured. Memory figures are the run specs' `peak_gb`.

**Where the search stands (measured 19 Nov 19:15):** `v14_stage1` is at step 17 of 34 (c15, seed 0). Since the resume on
18 Nov, the eight trainings took 34.6 h, ≈ 4.3 h each, against the run spec's 2–3.5 h. At that pace the 16 seed-1 trainings
and read1 end **≈ Sun 22 Nov late evening, possibly Mon 23 Nov morning (est.)**, not the 21 Nov that row 270 assumed.

| week | laptop runs (est. duration, peak memory) | writing and desk work | the user's decisions |
|---|---|---|---|
| **Fri 20 – Sun 22 Nov** | v14 stage 1 continues (≈ 70 h left, 7.7 GB). It has room beside it for one small run (7.7 + ≤ 4 GB margin): the anharmonic step's first real run (TASKS 211, ≈ 0.5 h, 2.3 GB) once TASKS 255 is fixed | claims page for 25 Nov (TASKS 140); demo fixes (`demo-fixes` branch, rows 270/271); module 08's certificate strings → 'test set (a)/(b)' ready for the rebuild (TASKS 146) | whether stage 2 waits until after the meeting (proposed: yes) |
| **Mon 23 – Tue 24 Nov** | stage 1 ends; read1 writes stage 2 (minutes). Row 270's computed demo run (≈ 0.2–1 h, 7 GB). The demo rebuild and show regeneration (TASKS 146, < 1 h est.). **Stage 2 is not launched.** 24 Nov: the TASKS 154 check that nothing runs | demo rehearsal; the four claims with their numbers | the demo molecule menu for the supervisor (row 271) |
| **Wed 25 Nov (meeting)** | laptop idle in the morning. After the meeting: launch **stage 2** (best four + the control, seed 2: 5 trainings ≈ 22 h, 7.7 GB) | notes of the talk into the board | the funding and the PC (TASKS 191); papers D and C (30, 190); the missing anchors (82, 145); closed-access papers (144); runbook (93); large molecules: pieces or count (199/200) |
| **Thu 26 – Sun 29 Nov** | stage 2 ends ≈ Thu evening (est.). If its winner beats v1.4 by the registered route: a release retrain (≈ 7 h, 7.7 GB, `release_v14`), then product-error read and evals (≈ 1 h). Then TASKS 164's pyscf 2.15 checks on `~/qc215` (≈ 8 h, 9 GB, alone) | module 08 standalone content rewrite (TASKS 223); test-set renames in modules 06/08 (TASKS 262, after the user's answer) | **the cation fill's two run choices (TASKS 121)**, so the fill can start next week |
| **30 Nov – 6 Dec** | chain 42 arm D with six beside five, then the floor re-read (TASKS 49; duration unknown, to be read from chain 42's last run; 7.7 GB). The update to pyscf 2.15.1, between runs | module 08 snapshot build, `SUBMISSION.txt`, `make_module_repo.sh` dry run; module 02 rubric repo; my re-read of each module against its rubric | module 07's Vocareum key (early December); module 06's reproduction: confirm the 14 Nov run (exit 0) counts |
| **7 – 20 Dec** | **cation fill starts** (415 cations, ≈ 1,147 laptop h ≈ 48 days nonstop at 6 threads, peak ≈ 11.4 GB: it runs **alone**). Any other training pauses it | modules 06, 07, 08 final and pushed; module 09's slide outline (TASKS 189); paper D outline in the shape the talk gave | the GitHub pushes of the module repositories (yours) |
| **21 Dec – 3 Jan** | cation fill continues unattended under one alarm-only watchdog. No updates while it runs | holiday; light: the capstone report's skeleton | — |
| **4 – 17 Jan** | cation fill continues (≈ 60 % done est.) | capstone report: proxy proof, the four claims, the product (aromir) | aromir's tag / Hugging Face upload once its six criteria are green (TASKS 269, your word) |
| **18 – 31 Jan** | cation fill ends ≈ 24–31 Jan (est., if not paused). Then the merge and a retrain on the pool with cations (≈ 8 h for three seeds, 7.7 GB) and its reads | capstone report drafts; paper D draft | whether the cation network is carried (by the registered rule; a launch of a further run is yours) |
| **1 – 14 Feb** | the cations' reads (TASKS 257–259 design: ≈ 1–2 h each, est.); the MP2 QZ step (194) or other free-laptop checks if agreed | capstone report: full draft | the Zenodo deposit (TASKS 30) |
| **15 – 28 Feb** | reserve week for re-runs that reviews ask for; nothing long is started after ≈ 20 Feb | final read, submission package ready by 28 Feb | submit, or hold until spring |

**What does not fit on the laptop:** the neutral fill to 30 per cell (TASKS 85, ≈ 1,276 h est.) cannot run on top of the cation
fill before February. Doing both needs the PC or funded compute (TASKS 191: a decade of data ≈ €2,290 rented against ≈ €2,329
for the PC). That is the main question for 25 Nov.

**Checks to make before you agree to this:** (1) the stage-1 end time, re-estimated each day from the `done` lines in
`probes/results_m1/v14_stage1.log`. (2) Whether the cation fill can be paused and resumed (`resumable` in its run spec)
without losing the molecule in progress. (3) Chain 42's arm D duration.
