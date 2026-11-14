# Module 08 — Industry-Integrated AI Systems Synthesis: a spectrum with a stated accuracy and price, or an honest refusal

**Author:** Frederic Petrignani

**Status (3 November 2026 20:5x).** Built on 28 September after the user's decisions of §8 (`DESIGN_2026-09-27.md`; recorded in `PRE_REGISTRATION.md`): the request officer, certificate generator, replay worker, licence reader, measured price table and module-06 candidate draw in `m08/`, eight pre-registered scenarios plus three added cases (`scenarios/`, `run_scenarios.py`), the executed notebook `notebook/integrated_system.ipynb` and `Reflective_Synthesis_Paper.docx/.pdf`. Since 29 October (decision 64) the module also holds the **pipeline** it promised: one molecule in, as a SMILES or an xyz file, its infrared spectrum out with a certificate, on the laptop (`m08/pipeline.py`, version 0.9; the versions in `modules/PIPELINE.md`). Its show, a replay of 42 runs, is on the Spectrum Atlas at /pipeline/. The licence is decision 65's: a mode family is licensed where the carried ΔH network (v1.3) is within 3 cm⁻¹ on both hold-outs — ring-ip, CH-stretch and CH-oop; 'other' is not — read from the network's own evaluation records. What the pipeline still needs is `PIPELINE_BACKLOG.md`; the notebook and the paper still describe the licence of 28 September and are rewritten in the writing phase.

## What it is

*For readers without chemistry:* The integrated system turns a request — a molecule, how accurate the answer must be, a budget — into either a computed infrared spectrum with a stated accuracy and price, or a refusal that names the missing step. Its parts come from the earlier modules: the library of existing predictions (02), the laboratory numbers to score against (03), the trained correction (05) and the run steward that is allowed to start work (07). Terms are defined in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

The public **Spectrum Atlas** (built 23–24 September, `website/`) is the integrated artifact's front; this module adds the part that makes it a
service: a **request officer** that answers a request (molecule, target rung, budget, free text) with a **certificate**, a **refusal naming the gate and the
cap, the price of each missing step and the rung the budget does reach**, or a **run order** that cannot start without module 07's gate. The ladder — listed · cheap level done ·
correction predicted · spectrum predicted · anchored · validated — is on every output; a rung not reached shows "—" and why.
Since 10 October the certificate also carries the **spectral shape** as astronomers read it: band positions *and* heights (double-harmonic
intensities from the molecule's dipole derivatives, `m08/spectrum.py`), Lorentzian-broadened, with its accuracy read from module 05's records —
at the proxy level the learned correction lifts the spectrum overlap from 0.27 to 0.97 and halves the height error (0.30 → 0.13); against
CCSD(T) on benzene the overlap goes from 0.26 to 0.37. The pipeline computes every molecule's dipole derivatives, so its certificate always carries heights; a catalogue certificate carries them where the corpus holds the molecule's dipole derivatives, and otherwise shows positions only and says why. Notebook §3.6.

Four earlier modules are load-bearing in code: **03** (the laboratory tolerance u_band per family = the certificate's error budget; the family rule is copied from module 03's script), **05** (the ΔH network the pipeline's step 4 runs, and its evaluation records, from which `m08/accuracy.py` reads the measured error and `m08/licence.py` the licence of decision 65), **06** (the out-of-corpus candidate is drawn from the trained SMILES model at a fixed seed), **07** (a run order is a `Proposal` in the steward's schema, judged by the steward's gate with its default rule table, `rules_v2.json`, 41 rules). Modules 02 (the library of existing predictions) and 04 (the calibrated-harmonic reading) are part of the story the paper tells, but no code here reads their output. The standout proposer's plan line is shown as a labelled proxy only (decision 3).

## The pipeline (decision 64)

Six steps, each named in the record: (1) the start geometry from the canonical SMILES (RDKit ETKDG + MMFF) or the xyz given, in one atom order; (2) the B3LYP/6-31G* optimisation in psi4; (3) pyscf's analytic B3LYP Hessian and dipole derivatives; (4) the ΔH network's correction, the mean of its three seeds with each seed kept; (5) the double-harmonic spectrum, Lorentzian-broadened; (6) the certificate (`m08/live_certificate.py`), which marks every band by its family's licence and says whether the network has seen the molecule (`m08/seen.py`). Steps 2–3 come from the corpus where it holds the molecule as these steps compute it (`m08/reuse.py`); the run time is estimated before a run (`m08/runtime.py`); a molecule outside what the network trained on — charged, open-shell, other elements — is refused before any computation, with the reason. Positions are harmonic, and the correction moves B3LYP toward the DFT proxy the network was trained on (ωB97X/6-31G*); nothing is claimed at the coupled-cluster level.

## The anharmonic step: what we tried, what we learned, and what the certificate may say

*For readers without chemistry:* a molecule's infrared spectrum is a list of frequencies at which it absorbs light. The usual way to
compute one treats every chemical bond as an ideal spring, which is called the **harmonic** picture. Real bonds are not ideal springs
— they soften as they stretch — so a real band sits a little below the harmonic one. That difference is the **anharmonic shift**,
a few to a few tens of wavenumbers (cm⁻¹), and this module's certificate is only as good as its handling of it.

The pipeline's spectrum is ν = ω(the network's corrected stiffness) + Δ_anh (the anharmonic shift). The network is module 05's; this
section is the story of the second term, because the path to it is a better lesson than the result.

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

```bash
python modules/08_industry_synthesis/run_scenarios.py --with-catalog     # S1–S4, S8 end to end; S7; S5 (the export builder, ≈ seconds)
python -m pytest modules/08_industry_synthesis/tests tests/test_m08_*.py -q   # the module's and the pipeline's tests, no machine
cd modules/08_industry_synthesis && python -m m08.pipeline --name benzene --smiles c1ccccc1 --out <folder> --threads 6
                                                                          # the pipeline; CORPUS_QC_PYTHON names the psi4 env
python modules/08_industry_synthesis/notebook/make_notebook.py            # writes and executes integrated_system.ipynb (needs a run of run_scenarios.py first)
python modules/08_industry_synthesis/make_summary.py                      # the paper from notebook/results.json; refuses outside 1,500–2,000 words
```

Environment: the system Python 3.14 with torch, rdkit, pydantic, nbclient, python-docx (`requirements.txt` is its `pip freeze`); Word for the PDF.
Inputs: `website/export/out` (built by `website/export/build_catalog.py`), `modules/03_lab_scoreboard/out/u_band_by_record_family.csv` and
`notebook/bands_lab.csv`, the carried ΔH network's evaluation records in `modules/05_support_predictor/out/` (`m08/accuracy.py`), `modules/06_generative_candidates/notebook/out/seed0/`,
`modules/07_agentic_workflows/rules/rules_v2.json` and `steward/`. Outputs: `out/certificates/*.json|.md`, `out/requests_ledger.csv`,
`out/scenario_results_<date>.json`.

## Decisions (the user, 28 September 2026)

1 replay worker, not live · 2 Cloudflare Pages when live · 3 the standout's plan line labelled proxy, in the "estimated" column only · 4 module-06
candidates: intake only · 5 build now. The design note's §8 carries them with the date.

## Files

`DESIGN_2026-09-27.md` (Tasks 1–7 as designed) · `PRE_REGISTRATION.md` (frozen scenarios and pass lines, decisions, outcome) · `m08/` · `scenarios/` ·
`run_scenarios.py` · `tests/test_m08.py` · `notebook/make_notebook.py` → `integrated_system.ipynb`, `results.json`, `figures/` · `make_summary.py` →
`Reflective_Synthesis_Paper.docx/.pdf` · `requirements.txt` · `PROVENANCE.md` · `RUBRIC_CHECKLIST_2026-09-28.md` · `out/`.
