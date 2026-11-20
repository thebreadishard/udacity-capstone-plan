# Module 08 — Industry-Integrated AI Systems Synthesis: a spectrum with a stated accuracy and price, or an honest refusal

**Author:** Frederic Petrignani

**Status (20 November 2026).** The module has two parts. The first, built on 28 September, is a **request service**: a request officer, a certificate generator, a replay worker, a licence reader and a measured price table in `m08/`, with eight pre-registered scenarios plus three added cases (`scenarios/`, `run_scenarios.py`). The second, since 29 October (decision 64), is the **pipeline** the service points to: one molecule in, as a SMILES or an xyz file, its corrected infrared spectrum out with a certificate, computed on a laptop (`m08/pipeline.py`, version 0.15). The notebook `notebook/integrated_system.ipynb` runs the scenarios' evidence end to end and shows one stored pipeline run; `Reflective_Synthesis_Paper.pdf` is the paper.

**What is proven, and at which level.** The correction is a neural network (module 05's ΔH network, version 1.4). It is trained on the difference between two DFT functionals, B3LYP and ωB97X, and tested on whether it reproduces the second from the first on molecules it never saw. That is a proxy proof: nothing is claimed at the coupled-cluster level, and no new coupled-cluster reference calculation is made before July 2027 (decision 63). A family of vibrations is **licensed** when the error of the corrected band positions is within 3 cm⁻¹ on both test sets — test set (a), unseen molecules, and test set (b), molecules of held-out scaffolds (decision 65). For version 1.4 all four families are licensed: ring-ip 1.17 / 1.22, CH-stretch 0.80 / 1.67, CH-oop 1.86 / 1.26 and 'other' 2.38 / 2.10 cm⁻¹ on (a) / (b). Two of them rest on few molecules on test set (a), and the licence says so with their intervals (CH-oop 0.93–3.2 cm⁻¹, 'other' 1.45–3.19 cm⁻¹). The error is measured on *measurement networks*, which never saw the test sets; the printed spectrum is made by *release networks* of the same recipe, trained on all data (decision 66). The code and the records call the test sets "hold-out (a)" and "hold-out (b)"; the words mean the same.

## What it is

*For readers without chemistry:* The integrated system turns a request — a molecule, how accurate the answer must be, a budget — into either a computed infrared spectrum with a stated accuracy and price, or a refusal that names the missing step. Its parts come from the earlier modules: the library of existing predictions (02), the laboratory numbers to score against (03), the trained correction (05) and the run steward that is allowed to start work (07). Terms are defined in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

The public **Spectrum Atlas** (built 23–24 September) is the integrated artifact's front; this module adds the part that makes it a
service: a **request officer** that answers a request (molecule, target rung, budget, free text) with a **certificate**, a **refusal naming the gate and the
cap, the price of each missing step and the rung the budget does reach**, or a **run order** that cannot start without module 07's gate. The ladder — listed · cheap level done ·
correction predicted · spectrum predicted · anchored · validated — is on every output; a rung not reached shows "—" and why. The two predicted rungs are empty in the catalogue because a catalogue record is the cheap level: the corrected spectrum is computed per molecule by the pipeline.

Since 10 October the certificate also carries the **spectral shape** as astronomers read it: band positions *and* heights (double-harmonic
intensities from the molecule's dipole derivatives, `m08/spectrum.py`), Lorentzian-broadened, with its accuracy read from the network's evaluation records.
For version 1.4 the correction lifts the spectrum overlap from 0.277 to 0.977 on test set (a) (8 molecules) and from 0.366 to 0.975 on test set (b) (the 31 molecules with dipole derivatives), and lowers the height error from 0.227 to 0.109 and from 0.511 to 0.216. These are comparisons against ωB97X, the proxy; no coupled-cluster comparison was made for this version. The pipeline computes every molecule's dipole derivatives, so its certificate always carries heights; a catalogue certificate carries them where the corpus holds the molecule's dipole derivatives, and otherwise shows positions only and says why. Notebook §3.6.

Four earlier modules are load-bearing in code: **03** (the laboratory tolerance u_band per family = the certificate's error budget; the family rule is copied from module 03's script), **05** (the ΔH network the pipeline's step 4 runs, and its evaluation records, from which `m08/accuracy.py` reads the measured error and `m08/licence.py` the licence of decision 65; the error comes from the measurement networks and the spectrum from the release networks, decision 66), **06** (the candidate of scenario S3: in the plan's repository it is drawn from the trained SMILES model at a fixed seed; the submitted repository carries no weights, and S3 runs on a fixed candidate with `--no-candidate`), **07** (a run order is a `Proposal` in the steward's schema, judged by the steward's gate with its default rule table, `rules_v2.json`, 41 rules). Modules 02 (the library of existing predictions) and 04 (the calibrated-harmonic reading) are part of the story the paper tells, but no code here reads their output. The standout proposer's plan line is shown as a labelled proxy only (decision 3).

## The pipeline (decision 64)

Six steps, each named in the record: (1) the start geometry from the canonical SMILES (RDKit ETKDG + MMFF) or the xyz given, in one atom order; (2) the B3LYP/6-31G* optimisation in psi4, after which the bonds are checked: an optimised geometry that is no longer the molecule admitted is refused before the next step; (3) pyscf's analytic B3LYP Hessian and dipole derivatives; (4) the ΔH network's correction: the mean of the release networks' seeds, with each seed kept; (5) the double-harmonic spectrum, Lorentzian-broadened, with the B3LYP spectrum scaled by PAHdb's 6-31G* factors beside it as the baseline only, and then the molecule's **own spread**: the networks correct the same molecule again turned, mirrored and with its atoms listed in other orders, and each band's spread is the furthest it lay from the printed position; (6) the anharmonic step, off unless asked for (next section). The certificate (`m08/live_certificate.py`) marks every band. A band is licensed only if its family is licensed *and* its own spread is within 3 cm⁻¹ in every presentation tried — a sample, not a bound. The corrected positions are printed either way. The certificate also says whether the networks have seen the molecule (`m08/seen.py`).

Steps 2–3 come from the corpus where it holds the molecule as these steps compute it (`m08/reuse.py`); the run time is estimated before a run (`m08/runtime.py`). The pipeline takes one neutral, closed-shell molecule with an aromatic ring, made of the elements the networks trained on; anything else is refused before any computation, with the reason. A molecule outside the sizes the networks trained on, or with a kind of charged atom or a size of aromatic ring no training molecule has, is computed and printed, and no band of it is licensed. Positions are harmonic unless step 6 ran, and the correction moves B3LYP toward the DFT proxy the networks were trained on (ωB97X/6-31G*); nothing is claimed at the coupled-cluster level. The versions are in the plan repository's `modules/PIPELINE.md`; the pipeline's show on the Spectrum Atlas (/pipeline/) replays runs of network version 1.3, which are records in the plan repository and not part of this submission.

## The anharmonic step: what we tried, what we learned, and what the certificate may say

*For readers without chemistry:* a molecule's infrared spectrum is a list of frequencies at which it absorbs light. The usual way to
compute one treats every chemical bond as an ideal spring, which is called the **harmonic** picture. Real bonds are not ideal springs
— they soften as they stretch — so a real band sits a little below the harmonic one. That difference is the **anharmonic shift**,
a few to a few tens of wavenumbers (cm⁻¹), and this module's certificate is only as good as its handling of it.

The pipeline's spectrum is ν = ω(the network's corrected stiffness) + Δ_anh (the anharmonic shift). The network is module 05's; this
section is the story of the second term, because the path to it is a better lesson than the result. In the pipeline it is
step 6, added in version 0.11: off unless a run asks for it with `--anharmonic-minutes`.

**Step one: how cheaply can the shift be computed?** (S1, registered 13 October.) The shift needs a second, more expensive kind of
calculation. We registered two candidate levels before measuring, one cheap (G) and one cheaper still (B), and asked how far each
lands from a trusted reference. G came within **0.19 cm⁻¹ on average and 0.34 at worst**; B missed by **3.16 and 7.51**, which
was predicted and is why the prediction was written first. G it is. The saving against the trusted route was real but smaller than
hoped: the five molecules of the shape test cost about **€2,715** at the trusted level and **€1,300** at G, a factor 2.1.

**Step two: does a bigger basis set change the answer?** (S1-TZ, October.) It does not enough to pay for itself, and G was kept
(the user, 30 October).

**Step three: can the shift be learned instead of computed?** (S2 and S2b.) For 30 to 60-atom molecules even G is expensive, so we
asked whether a small model can predict the shift from cheap features. The reads are per **family** of vibrations — the ring
breathing in the plane, the hydrogens flapping out of the plane, the rest — because the families behave differently. On the relabelled
sets (12 November) the learning curves said: **CH-oop 5.06 and flat** (more data will not help), **ring-ip 3.02 and still learning**
(about 36 more scaffolds would reach the line), **'other' 3.25** but needing some 1,607 scaffolds, which nobody will pay for.

**Step four: the diagnosis.** (13 November.) One family's error was absurd — 41.18 cm⁻¹ — and the cause was not the model. The
reference method itself, second-order perturbation theory, is out of its domain for a handful of strongly anharmonic out-of-plane
modes; its arithmetic divides by a difference that goes to zero. We registered a measure of that breakdown before re-reading, marked
the modes it catches (8 of 2,028 in the labels we have), and read again: **'other' fell from 41.18 to 3.84**, and a control that
keeps the marked modes reproduced the first read exactly. So the model was never the problem there; the labels were.

**Step five: the verdict, and what a certificate may say.** A rule registered on 4 November — before either read — said which
route each family may use, with a line at 3 cm⁻¹. Read on 13 November it licensed **no anharmonic step in any family**: the best
model lands at 3.37 (ring-ip), 3.84 ('other') and 8.38 (CH-oop), and coronene carries nearly every failure where tetracene alone
would pass two. The honest consequence is in the certificate: **no band's position is claimed to 3 cm⁻¹**.

But refusing the step is not the same as printing the harmonic position, and the harmonic position is worse: over the same modes it
is wrong by **26.23 cm⁻¹ in ring-ip, 8.20 in 'other' and 12.48 in CH-oop**. A registration of 14 November separates the two
questions. What the certificate **prints** is the best estimate we have — the anharmonic step with the family's measured error
beside it — and what it **licenses** stays what the rule of 4 November says, which is nothing. A mode the domain measure marks gets
no step at all and says so.

**What is not done, said plainly.** The C–H stretches, the strongest bands in the spectrum, have no measured error bar at all: the
reads work in a window that stops below them, so under the same rule they are printed harmonic — and that is where the harmonic
error is largest, about −170 cm⁻¹. The read that would fix it is registered and not yet run. A hindered methyl group's policy is
designed and not built. Whether more training scaffolds are bought for the in-plane ring family is a decision, not a measurement.
And the corpus holds no molecule shaped like coronene, which is precisely the shape that fails here.

The notes behind this section: `GoalGathering/notes/Design_2026-10-13_Spectral_Shape_Anharmonic_Step.md`,
`PreRegistration_2026-10-14_S2_Anharmonic_Shift.md`, `PreRegistration_2026-11-04_Anharmonic_Route_Rule.md`,
`Design_2026-11-13_VPT2_Domain_Marks.md`, `PreRegistration_2026-11-14_Printed_Band_Position.md`, and the reads they name.

## How to run

In the submitted repository. It reads its frozen `snapshot/`; no other folder is needed, and nothing touches a machine:

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute notebook/integrated_system.ipynb --output executed.ipynb   # the notebook, from stored records
python run_scenarios.py --no-candidate     # the scenarios again: S1–S4 and S8, and the cost check S7; S3 on a fixed candidate
```

`--no-candidate` is needed there because the fresh candidate of S3 is drawn from module 06's trained model, whose weights are not in this repository. S5 (`--with-catalog`) rebuilds the website export and S6 needs the built site and a browser; both belong to the plan's repository, and S6's status is read from the record of its run (`out/s6_accessibility_2026-10-11.json`). The pipeline itself needs psi4, pyscf and the networks' weights, so it does not run from this repository either; the notebook shows a stored run of it. The tests in `tests/` are the module's own and run in the plan's repository, where the corpus and module 05's code are.

In the plan's repository (from `plans/05_delta-probed-ir-pipeline`):

```bash
python modules/08_industry_synthesis/run_scenarios.py --with-catalog     # S1–S4, S8 end to end; S7; S5 (the export builder, ≈ a minute)
python -m pytest modules/08_industry_synthesis/tests tests/test_m08_*.py -q   # the module's and the pipeline's tests, no machine
cd modules/08_industry_synthesis && python -m m08.pipeline --name benzene --smiles c1ccccc1 --out <folder> --threads 6
                                                                          # the pipeline; CORPUS_QC_PYTHON names the psi4 env
python modules/08_industry_synthesis/notebook/make_notebook.py            # writes and executes integrated_system.ipynb (needs a run of run_scenarios.py first)
python modules/08_industry_synthesis/make_summary.py                      # the paper from notebook/results.json; refuses outside 1,500–2,000 words
cd modules/08_industry_synthesis && python -m m08.make_snapshot           # freezes what the scenarios and the notebook read into snapshot/
```

Environment: Python 3.14 with torch, rdkit, pydantic and nbclient (`requirements.txt` is its `pip freeze`).

Inputs. In the submitted repository everything the module reads from outside its own folder lies under `snapshot/`, at the path it has in the plan's repository; `snapshot/MANIFEST.json` lists every file with its size, its sha256 and the plan commit it was frozen from. That is: the website export (the catalogue, its summary and the molecule records the scenarios open), module 03's tolerance table and laboratory band table, module 05's corpus manifest, anchor registry, model registry and the evaluation records of the carried network (under `out/v14/`), the evidence files the certificates cite, and one stored pipeline run. `steward/` is module 07's package with its rule table. Outputs: `out/certificates/*.json|.md`, `out/requests_ledger.csv`, `out/scenario_results_<date>.json`.

## Decisions (the user, 28 September 2026)

1 replay worker, not live · 2 Cloudflare Pages when live · 3 the standout's plan line labelled proxy, in the "estimated" column only · 4 module-06
candidates: intake only · 5 build now. `PRE_REGISTRATION.md` carries them with the date.

Decisions 1 and 2 are of their date. The worker is still a replay, and no live worker or hosted officer is promised any more: under the proxy proof there is no coupled-cluster job to launch, and a new molecule is served by running the pipeline on a laptop. `DESIGN_2026-09-27.md` is the design as it was written on 27 September; its live worker, sign-in and hosting sections describe that design, not this build.

## Files

- `notebook/integrated_system.ipynb` — the problem, the system, the scenarios run end to end, the failure case, a stored pipeline run, the evaluation.
- `notebook/results.json`, `notebook/figures/` — the notebook's numbers and figures; the paper is built from them.
- `Reflective_Synthesis_Paper.pdf` — the reflective synthesis paper in the Udacity APA 7 template.
- `m08/` — the code: `officer.py` (the decision), `certify.py` (the catalogue certificate), `licence.py` and `accuracy.py` (the licence and the measured error, read from the network's records), `prices.py` (the measured price table), `catalog.py`, `replay.py`, `candidates.py`, `spectrum.py`, `stored_run.py`; the pipeline: `pipeline.py`, `live_certificate.py`, `own_spread.py`, `domain.py`, `molecule.py`, `seen.py`, `reuse.py`, `runtime.py`, `anharmonic.py`, `positions.py`, `progress.py`; the standalone form: `paths.py`, `make_snapshot.py`.
- `scenarios/` — the pre-registered scenarios with their dated amendments; `run_scenarios.py` — the runner; `out/` — its records: the results, the certificates, the request ledger and the record of S6.
- `tests/` — the module's tests.
- `snapshot/` — the frozen files the module reads from the rest of the project, with `MANIFEST.json`; `steward/` — module 07's gate, rules and schema.
- `PRE_REGISTRATION.md` (the frozen scenarios and pass lines, the decisions, the outcome and its dated addenda) · `PROVENANCE.md` · `DESIGN_2026-09-27.md` (the design of 27 September).
- `requirements.txt` · `SUBMISSION.txt` (what this repository holds).

The scripts that build the notebook and the paper, the pipeline's tests, the rubric checklist, the standalone plan, the pipeline's backlog and build note, and the records of the pipeline show stay in the plan's repository, in the module's folder
[`modules/08_industry_synthesis`](https://github.com/thebreadishard/udacity-capstone-plan/tree/master/plans/05_delta-probed-ir-pipeline/modules/08_industry_synthesis).

## Repository

Submitted as the public repository `udacity-industry-ai-synthesis` (its default branch `main` is the one the review reads). Its commit history
is this module's own, carried over from the plan's repository [udacity-capstone-plan](https://github.com/thebreadishard/udacity-capstone-plan),
where the module lives as `plans/05_delta-probed-ir-pipeline/modules/08_industry_synthesis/`. The last commit on `main` keeps only the files
listed in `SUBMISSION.txt`.
