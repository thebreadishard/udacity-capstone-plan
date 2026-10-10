# Module 08 — Industry-Integrated AI Systems Synthesis: a spectrum with a stated accuracy and price, or an honest refusal

**Status (10 October 2026).** Built in one evening on 28 September after the user's decisions of §8 (`DESIGN_2026-09-27.md`; recorded in `PRE_REGISTRATION.md`): `m08/` (request officer, certificate generator, replay worker, licence reader, measured price table, module-06 candidate draw), `scenarios/scenarios.json` (eight pre-registered scenarios plus three added cases), `run_scenarios.py` (8/8 pass; S7 cost honesty 4/4; S5 catalogue consistency exit 0), `tests/` (9 green), the executed notebook `notebook/integrated_system.ipynb` with `results.json` and three figures, `Reflective_Synthesis_Paper.docx/.pdf` (1,852 words), `requirements.txt`, `PROVENANCE.md`, `RUBRIC_CHECKLIST_2026-09-28.md`. Since then: the Spectrum Atlas (the module's integrated artifact, `website/`) was republished on 2 October with 843 computed molecules and four coupled-cluster Hessians as anchored evidence, and the user's first pass on a real phone (3 October) found search, molecule page and the 3D view in order — the manual half of S6; the axe run of S6 still needs the built site. Decision 52 (3 October) added the pricing rule the Atlas will quote for an uncovered family — 'its family first', ≈ 30 molecules at the cheap level before anything is promised — which the price table here does not yet carry (a design input, not a code change so far).

## What it is

*For readers without chemistry:* The integrated system turns a request — a molecule, how accurate the answer must be, a budget — into either a computed infrared spectrum with a stated accuracy and price, or a refusal that names the missing step. Its parts come from the earlier modules: the library of existing predictions (02), the laboratory numbers to score against (03), the trained correction (05) and the run steward that is allowed to start work (07). Terms are defined in [`../GLOSSARY.md`](../GLOSSARY.md).

The public **Spectrum Atlas** (built 23–24 September, `website/`) is the integrated artifact's front; this module adds the part that makes it a
service: a **request officer** that answers a request (molecule, target rung, budget, free text) with a **certificate**, a **refusal naming the gate or the
cap and the price of the missing step**, or a **run order** that cannot start without module 07's gate. The ladder — listed · cheap level done ·
correction predicted · spectrum predicted · anchored · validated — is on every output; a rung not reached shows "—" and why.
Since 10 October the certificate also carries the **spectral shape** as astronomers read it: band positions *and* heights (double-harmonic
intensities from the molecule's dipole derivatives, `m08/spectrum.py`), Lorentzian-broadened, with its accuracy read from module 05's records —
at the proxy level the learned correction lifts the spectrum overlap from 0.27 to 0.97 and halves the height error (0.30 → 0.13); against
CCSD(T) on benzene the overlap goes from 0.26 to 0.59. Heights appear only where dipole derivatives exist (ten molecules today); every other
certificate shows positions only and says why. Notebook §3.6.

Five earlier modules are load-bearing in code: **03** (the laboratory tolerance u_band per family = the certificate's error budget; the family rule is
copied from module 03's script), **04** (the calibrated-harmonic reading behind the cheap rung), **05** (the licence: the proof-of-learning
pre-registration's rule and the latest layer-B table — no family licensed until the verdict at 1,200 molecules), **06** (the out-of-corpus candidate is
drawn from the trained SMILES model at a fixed seed), **07** (a run order is a `Proposal` in the steward's schema, judged by the steward's gate with its
32-rule table). The standout proposer's plan line is shown as a labelled proxy only (decision 3).

## How to run

```bash
python modules/08_industry_synthesis/run_scenarios.py --with-catalog     # S1–S4, S8 end to end; S7; S5 (the export builder, ≈ seconds)
python -m pytest modules/08_industry_synthesis/tests -q                   # 8 tests, no network, no machine
python modules/08_industry_synthesis/notebook/make_notebook.py            # writes and executes integrated_system.ipynb (needs a run of run_scenarios.py first)
python modules/08_industry_synthesis/make_summary.py                      # the paper from notebook/results.json; refuses outside 1,500–2,000 words
```

Environment: the system Python 3.14 with torch, rdkit, pydantic, nbclient, python-docx (`requirements.txt` is its `pip freeze`); Word for the PDF.
Inputs: `website/export/out` (built by `website/export/build_catalog.py`), `modules/03_lab_scoreboard/out/u_band_by_record_family.csv` and
`notebook/bands_lab.csv`, `modules/05_support_predictor/out/E7_rungB_layerB_2026-09-27.md`, `modules/06_generative_candidates/notebook/out/seed0/`,
`modules/07_agentic_workflows/rules/rules_v1.json` and `steward/`. Outputs: `out/certificates/*.json|.md`, `out/requests_ledger.csv`,
`out/scenario_results_<date>.json`.

## Decisions (the user, 28 September 2026)

1 replay worker, not live · 2 Cloudflare Pages when live · 3 the standout's plan line labelled proxy, in the "estimated" column only · 4 module-06
candidates: intake only · 5 build now. The design note's §8 carries them with the date.

## Files

`DESIGN_2026-09-27.md` (Tasks 1–7 as designed) · `PRE_REGISTRATION.md` (frozen scenarios and pass lines, decisions, outcome) · `m08/` · `scenarios/` ·
`run_scenarios.py` · `tests/test_m08.py` · `notebook/make_notebook.py` → `integrated_system.ipynb`, `results.json`, `figures/` · `make_summary.py` →
`Reflective_Synthesis_Paper.docx/.pdf` · `requirements.txt` · `PROVENANCE.md` · `RUBRIC_CHECKLIST_2026-09-28.md` · `out/`.
