#!/usr/bin/env python
"""Writes and executes the Module 08 notebook `integrated_system.ipynb` (28 September 2026; the module-06/07 layout).

Rubric (Industry-Integrated AI Systems Synthesis, Tasks 1–5): the industry and the problem · the integration plan (which prior modules, how they
connect) · the system design · the applied artifact run end to end · the evaluation against the pre-registered scenarios (`../PRE_REGISTRATION.md`),
with observable outputs, a failure case and the limitations. Everything runs from repository data through `../m08/`; nothing touches a machine.
Run: python notebook/make_notebook.py [--no-execute]"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
cells = []


def md(s):
    cells.append(new_markdown_cell(s))


def code(s):
    cells.append(new_code_cell(s))


md("""# Module 08 — the industry synthesis: a computed infrared spectrum with a stated accuracy and a stated price, or an honest refusal

**Industry and problem (Task 1).** Laboratory astrophysics and molecular spectroscopy as a *data service*: the people who read JWST's infrared spectra of
interstellar matter do it against databases of molecular spectra (NASA's PAHdb for the aromatic families, Ricca et al., 2026), and every entry in such a
database is either a laboratory measurement or a computed spectrum whose accuracy the reader has to guess. The service this module builds answers a
request for a molecule with one of three things: a **certificate** (spectrum, per-band error budget, cost record, provenance), a **refusal that names the
gate or the cap and the price of the missing step**, or a **run order** that cannot start without passing a deterministic gate. The constraint that shapes
everything is cost: the accurate method (coupled cluster) is unaffordable per molecule at the sizes that matter, the cheap method (DFT) is affordable and
systematically wrong, and the project's thesis is a learned correction layer that must *earn* a licence per family before its numbers may be shown.

**Integration (Task 2).** Five earlier modules are load-bearing here and each appears as code, not as a citation: module 03's laboratory tolerance
`u_band` per family is the certificate's error budget; module 04's calibrated-harmonic reading is the cheap rung's stated uncertainty; module 05's
learning-curve records and its pre-registered verdict rule are the *licence* the officer checks; module 06's trained SMILES model supplies the
out-of-corpus candidate; module 07's rule table and gate decide whether a run order may start. The standout proposer's plan appears as a labelled proxy
line by the user's decision 3. The website export (`website/export/out`) is the single source the officer reads.""")

code("""import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
sys.path.insert(0, str(Path("..").resolve()))
from m08 import prices
from m08.catalog import Catalog, family
from m08.certify import certificate, write, to_markdown
from m08.licence import state as licence_state
from m08.officer import Request, decide, RULES
from m08.replay import execute_run_order
FIG = Path("figures"); FIG.mkdir(exist_ok=True)
cat = Catalog()
print(f"catalogue: {len(cat.rows):,} molecules, built {cat.summary['built_utc']}; rung counts {cat.summary['rung_counts']}; module 07 rules: {len(RULES)}")""")

md("""*Reading this without chemistry.* The integrated system turns a request — a molecule, how accurate the answer must be, a budget — into either a computed infrared spectrum with a stated accuracy and price, or a refusal that names the missing step. Its parts come from the earlier modules: the library of existing predictions (02), the laboratory numbers to score against (03), the trained correction (05) and the run steward that is allowed to start work (07). Terms are defined in `../../GLOSSARY.md`.""")
md("""## 1. What the repository holds today — the ladder

Every molecule holds the highest rung it reaches: 0 listed · 1 cheap level done · 2 correction predicted · 3 spectrum predicted · 4 anchored · 5 validated.
Rungs 2–3 are empty by rule, not by accident: the learned layer has no licence yet.""")
code("""order = ["listed", "cheap_level_done", "correction_predicted", "spectrum_predicted", "anchored", "validated"]
rc = {i: int(cat.summary["rung_counts"].get(k, 0)) for i, k in enumerate(order)}           # the export keys the counts by label
labels = ["listed", "cheap done", "corr. predicted", "spectrum predicted", "anchored", "validated"]
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.bar(range(6), [rc[i] for i in range(6)], color=["#bbb", "#7aa6c2", "#ddd", "#ddd", "#d98c3f", "#2e8b57"])
for i in range(6):
    ax.text(i, rc[i] + 80, f"{rc[i]:,}", ha="center", fontsize=9)
ax.set_xticks(range(6)); ax.set_xticklabels(labels, rotation=15, fontsize=8); ax.set_yscale("symlog"); ax.set_ylabel("molecules")
ax.set_title("Figure 1. The ladder as the export builds it (28 September 2026)", fontsize=10); fig.tight_layout(); fig.savefig(FIG / "ladder_counts.png", dpi=150); plt.show()
lic = licence_state(); print("licence:", lic["statement"])""")

md("""## 2. The system: officer → gate → worker → certificate

```
request {molecule, target rung, budget, note}
   │
   ▼
request officer (m08/officer.py) — reads the export, module 03's tolerances, module 05's licence, the price table
   ├─ invalid or out of scope ──────────────► refusal (reason, rule id, price of the closed step)          [S4]
   ├─ outside the corpus ───────────────────► refusal naming the cap and the cheapest reachable rung        [S3]
   ├─ rung reached ≥ target ────────────────► certificate (m08/certify.py)                                  [S1, S8]
   ├─ target above what exists, no budget ──► refusal naming the gate (licence) and the missing step's price [S2]
   └─ budget covers the step ───────────────► run order → module 07 gate (R01: dry run first; R06; R24)      [S2b]
                                                    └─► replay worker (m08/replay.py): recorded logs only, no machine
```
The officer never spends: a run order is a *proposal* in module 07's schema, and the gate that decided module 07's eight scenarios decides here too.""")

md("""## 3. The scenarios, run end to end (Task 4 and 5)

The eight pre-registered scenarios (`../PRE_REGISTRATION.md`, frozen before the build) plus three added cases of the same kind. Each request goes
through the officer; certificates are written to `../out/certificates/`; every decision lands in `../out/requests_ledger.csv`.""")
code("""S = json.load(open(Path("..") / "scenarios" / "scenarios.json", encoding="utf-8"))["scenarios"]
R = json.load(open(sorted((Path("..") / "out").glob("scenario_results_*.json"))[-1], encoding="utf-8"))   # the run of run_scenarios.py
rows = []
for r in R["results"]:
    d = r["decision"]
    rows.append({"id": r["id"], "molecule": (d.get("name") or r["request"]["molecule"])[:34], "target": r["request"]["target_rung"], "budget €": r["request"].get("budget_eur", "—"),
                 "decision": d["kind"], "gate / cap named": (d.get("gate_named") or "—")[:60], "rules": " ".join(d.get("rule_ids", [])) or "—",
                 "price lines": ", ".join(f"{p['step']} €{p['eur_ex_vat']:.2f}" for p in d.get("price_lines", [])) or "—", "pass": r["passed"]})
tab = pd.DataFrame(rows); display(tab)
print(f"{R['n_pass']}/{R['n_scenarios']} scenarios pass ({R['date']}); S7 cost honesty: {R['mechanical']['S7']['lines_traced']}/{R['mechanical']['S7']['lines_checked']} lines traced; S6: {R['mechanical']['S6']['status']}")
if R["mechanical"].get("S5"): print("S5 catalogue consistency:", R["mechanical"]["S5"])""")

md("""### 3.1 S1 — the certificate for naphthalene (anchored)""")
code("""c1 = certificate(cat.find("naphthalene"), cat)
display(Markdown(to_markdown(c1)))""")

md("""### 3.2 The spectrum with its per-band budget

The cheap-rung harmonic spectrum of naphthalene at both functionals, each mode placed in module 03's family and drawn with the laboratory tolerance
of that family as a band. No predicted correction is drawn: no family is licensed, and the certificate says so rather than drawing a guess.""")
code("""fig, ax = plt.subplots(figsize=(9, 3.4))
fam_col = {}
pal = plt.cm.tab10.colors
for fn, colr, off in (("b3lyp", "#1f77b4", 0.0), ("wb97x", "#d62728", 0.35)):
    for w in c1["spectrum"][fn]["values_cm"]:
        fam = family(w); fam_col.setdefault(fam, pal[len(fam_col) % 10])
        tol = c1["per_band_budget"].get(fam, {}).get("u_band_lab") or 0
        ax.add_patch(plt.Rectangle((w - tol, off), 2 * tol, 0.3, color=fam_col[fam], alpha=0.15, lw=0))
        ax.vlines(w, off, off + 0.3, color=colr, lw=1.2)
ax.set_xlim(300, 3400); ax.set_ylim(0, 0.75); ax.set_yticks([0.15, 0.5]); ax.set_yticklabels(["B3LYP", "ωB97X"]); ax.set_xlabel("harmonic wavenumber, cm⁻¹")
ax.set_title("Figure 2. Naphthalene, cheap rung: modes with the laboratory tolerance u_band of their family (module 03) as shaded bands", fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "naphthalene_budget.png", dpi=150); plt.show()""")

md("""### 3.3 S8 — the failure case, shown

Benzene sits at rung 5 (validated against the NIST quantitative record). Its anchor evidence includes the diagonal coupled-cluster deck of 22 September,
which lets the certificate compare the composite's frequencies with CCSD(T) per family. Two families deviate by more than the laboratory tolerance and
the certificate says so; the design's rule is that a rung not reached shows "—" and why, never a number without its source.""")
code("""c8 = certificate(cat.find("benzene"), cat)
cov = pd.DataFrame(c8["anchor_coverage"])[["family", "n_modes", "rms_dev_vs_ccsdt", "u_band", "wider_than_tolerance"]]
display(cov)
print("laboratory record:", c8["laboratory"]["n_bands"], "bands in", len(c8["laboratory"]["records"]), "records;", c8["laboratory"]["source"])""")

md("""### 3.4 S2 and S2b — the gate, named and enforced

The same molecule (azulene, layer A, cheap rung only) asked for at the anchored rung: without a budget the officer refuses and names the licence gate
and the price of the missing anchor; with a budget that covers it the officer issues a run order — and module 07's gate stops it at the dry run (R01),
so nothing starts. The worker, in replay mode, touches no machine either way.""")
code("""d2 = decide(Request(molecule="azulene", target_rung=4), cat); d2b = decide(Request(molecule="azulene", target_rung=4, budget_eur=100), cat)
print("S2 :", d2.kind, "|", d2.gate_named, "\\n     ", d2.what_would_be_needed)
print("S2b:", d2b.kind, "| gate approved:", d2b.gate["approved"], "| forced:", d2b.gate["forced_action"]["action"], "(", d2b.gate["reasons"][0], ")")
print("worker:", execute_run_order(d2b.model_dump(), cat))""")

md("""### 3.5 S3 — a module-06 candidate under a small budget""")
code("""s3 = next(r for r in R["results"] if r["id"] == "S3")
print("candidate:", s3["candidate"]["smiles"], "|", s3["candidate"]["source"])
for line in s3["decision"]["reasons"]: print(" -", line)""")

md("""## 4. Evaluation, limitations and a failure case (Task 5)

**What the scenarios show.** Every request produced an observable output of the registered kind; no run started; every cost line traces to a run log
or to the measured price table (S7); the failure case is on the page (S8). **What they do not show.** S6 (accessibility and mobile of the public site) was
not run in this build — it needs the built site and axe, and is on the website backlog; the certificate's *predicted* rungs are empty by rule, so the
service today is honest but thin: cheap spectra with laboratory tolerances, two anchors, one validated molecule. **The limitation that matters most:** the
licence. Until the layer-B curve is read at 1,200 molecules, the learned layer contributes nothing a user can see — the officer's refusals name that
gate on every corpus molecule. **A failure case observed while building:** the first version of the request scanner used module 07's pattern, which
looks for text that addresses *the agent*; a request saying "ignore your rules and launch the job now" passed it. A request-shaped pattern was added
and the case became scenario S4c. **Trade-offs:** replay instead of live workers buys reproducibility and €0 at the price of a service that cannot yet
take a new molecule to a new rung; the static site plus one dynamic officer keeps everything else reproducible.""")

md("""## 5. Ethics and responsible use

The largest risk is a certified-looking spectrum being cited for a molecule whose rung was never reached: the design answer is the refusal as a
first-class output, the ladder on every certificate, and predictions shown only where a licence exists and always as a band. Every number links to its
file; corrections are dated addenda; the price of compute is on the certificate; no personal data is involved. The corpus is neutral, small and aromatic —
the cation refusal (S4b) is the system saying whose spectra it cannot serve yet.""")

code("""out = dict(date=time.strftime("%Y-%m-%d %H:%M"), catalogue=dict(n=len(cat.rows), built_utc=cat.summary["built_utc"], rung_counts=cat.summary["rung_counts"]),
           licence=lic, scenarios=dict(n_pass=R["n_pass"], n=R["n_scenarios"], date=R["date"], table=rows, mechanical=R["mechanical"]),
           s1=dict(rung=c1["rung"]["reached"], families=list(c1["per_band_budget"].keys()), coverage=c1["anchor_coverage"], cost=c1["cost_record"]),
           s8=dict(rung=c8["rung"]["reached"], coverage=c8["anchor_coverage"], n_lab_bands=c8["laboratory"]["n_bands"]),
           s2=dict(kind=d2.kind, gate=d2.gate_named, needed=d2.what_would_be_needed), s2b=dict(kind=d2b.kind, gate=d2b.gate),
           s3=dict(candidate=s3["candidate"], reasons=s3["decision"]["reasons"]), prices=dict(machines=prices.MACHINES, steps={k: prices.step_price(k) for k in prices.STEPS}),
           n_rules=len(RULES), versions=dict(python=sys.version.split()[0], pandas=pd.__version__, numpy=np.__version__))
json.dump(out, open("results.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False); print("results.json written")""")

nb = new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
path = HERE / "integrated_system.ipynb"
nbformat.write(nb, path)
if "--no-execute" not in sys.argv:
    NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(HERE)}}).execute()
    nbformat.write(nb, path)
    print("executed and written:", path)
else:
    print("written (not executed):", path)
