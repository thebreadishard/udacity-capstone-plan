# Module 08 — Industry-Integrated AI Systems Synthesis: a spectrum with a stated accuracy and price, or an honest refusal

**Author:** Frederic Petrignani

**Status (3 November 2026 20:5x).** Built on 28 September after the user's decisions of §8 (`DESIGN_2026-09-27.md`; recorded in `PRE_REGISTRATION.md`): the request officer, certificate generator, replay worker, licence reader, measured price table and module-06 candidate draw in `m08/`, eight pre-registered scenarios plus three added cases (`scenarios/`, `run_scenarios.py`), the executed notebook `notebook/integrated_system.ipynb` and `Reflective_Synthesis_Paper.docx/.pdf`. Since 29 October (decision 64) the module also holds the **pipeline** it promised: one molecule in, as a SMILES or an xyz file, its infrared spectrum out with a certificate, on the laptop (`m08/pipeline.py`, version 0.9; the versions in `modules/PIPELINE.md`). Its show, a replay of 42 runs, is on the Spectrum Atlas at /pipeline/. The licence is decision 65's: a mode family is licensed where the carried ΔH network (v1.3) is within 3 cm⁻¹ on both hold-outs — ring-ip, CH-stretch and CH-oop; 'other' is not — read from the network's own evaluation records. What the pipeline still needs is `PIPELINE_BACKLOG.md`; the notebook and the paper still describe the licence of 28 September and are rewritten in the writing phase.

## What it is

*For readers without chemistry:* The integrated system turns a request — a molecule, how accurate the answer must be, a budget — into either a computed infrared spectrum with a stated accuracy and price, or a refusal that names the missing step. Its parts come from the earlier modules: the library of existing predictions (02), the laboratory numbers to score against (03), the trained correction (05) and the run steward that is allowed to start work (07). Terms are defined in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

The public **Spectrum Atlas** (built 23–24 September, `website/`) is the integrated artifact's front; this module adds the part that makes it a
service: a **request officer** that answers a request (molecule, target rung, budget, free text) with a **certificate**, a **refusal naming the gate or the
cap and the price of the missing step**, or a **run order** that cannot start without module 07's gate. The ladder — listed · cheap level done ·
correction predicted · spectrum predicted · anchored · validated — is on every output; a rung not reached shows "—" and why.
Since 10 October the certificate also carries the **spectral shape** as astronomers read it: band positions *and* heights (double-harmonic
intensities from the molecule's dipole derivatives, `m08/spectrum.py`), Lorentzian-broadened, with its accuracy read from module 05's records —
at the proxy level the learned correction lifts the spectrum overlap from 0.27 to 0.97 and halves the height error (0.30 → 0.13); against
CCSD(T) on benzene the overlap goes from 0.26 to 0.37. The pipeline computes every molecule's dipole derivatives, so its certificate always carries heights; a catalogue certificate carries them where the corpus holds the molecule's dipole derivatives, and otherwise shows positions only and says why. Notebook §3.6.

Four earlier modules are load-bearing in code: **03** (the laboratory tolerance u_band per family = the certificate's error budget; the family rule is copied from module 03's script), **05** (the ΔH network the pipeline's step 4 runs, and its evaluation records, from which `m08/accuracy.py` reads the measured error and `m08/licence.py` the licence of decision 65), **06** (the out-of-corpus candidate is drawn from the trained SMILES model at a fixed seed), **07** (a run order is a `Proposal` in the steward's schema, judged by the steward's gate with its default rule table, `rules_v2.json`, 41 rules). Modules 02 (the library of existing predictions) and 04 (the calibrated-harmonic reading) are part of the story the paper tells, but no code here reads their output. The standout proposer's plan line is shown as a labelled proxy only (decision 3).

## The pipeline (decision 64)

Six steps, each named in the record: (1) the start geometry from the canonical SMILES (RDKit ETKDG + MMFF) or the xyz given, in one atom order; (2) the B3LYP/6-31G* optimisation in psi4; (3) pyscf's analytic B3LYP Hessian and dipole derivatives; (4) the ΔH network's correction, the mean of its three seeds with each seed kept; (5) the double-harmonic spectrum, Lorentzian-broadened; (6) the certificate (`m08/live_certificate.py`), which marks every band by its family's licence and says whether the network has seen the molecule (`m08/seen.py`). Steps 2–3 come from the corpus where it holds the molecule as these steps compute it (`m08/reuse.py`); the run time is estimated before a run (`m08/runtime.py`); a molecule outside what the network trained on — charged, open-shell, other elements — is refused before any computation, with the reason. Positions are harmonic, and the correction moves B3LYP toward the DFT proxy the network was trained on (ωB97X/6-31G*); nothing is claimed at the coupled-cluster level.

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
