#!/usr/bin/env python
"""Runs the pre-registered scenarios of module 08 (PRE_REGISTRATION.md §5) end to end from repository data and writes the records:
`out/scenario_results_<date>.json`, the certificates (`out/certificates/`), the request ledger (`out/requests_ledger.csv`) and the cost-honesty
check (S7). S5 (catalogue consistency) runs the export's own builder when `--with-catalog` is given (RDKit over 11,321 rows, ≈ a minute).
Usage: python run_scenarios.py [--with-catalog] [--no-candidate]"""
import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))
from m08 import prices  # noqa: E402
from m08.catalog import REPO, Catalog  # noqa: E402
from m08.certify import certificate, write  # noqa: E402
from m08.officer import Request, decide  # noqa: E402
from m08.replay import execute_run_order  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

OUT = HERE / "out"


def judge(sc: dict, d, cert: dict | None, worker: dict | None) -> tuple[bool, list[str]]:
    e = sc["expected"]; notes = []
    ok = d.kind == e["kind"]
    if not ok:
        notes.append(f"kind {d.kind} ≠ {e['kind']}")
    if "rung_reached" in e and d.rung_reached != e["rung_reached"]:
        ok = False; notes.append(f"rung {d.rung_reached} ≠ {e['rung_reached']}")
    if "gate_contains" in e and (not d.gate_named or e["gate_contains"] not in d.gate_named):
        ok = False; notes.append(f"gate '{d.gate_named}' lacks '{e['gate_contains']}'")
    if "rule_ids_any" in e and not any(r in d.rule_ids for r in e["rule_ids_any"]):
        ok = False; notes.append(f"rules {d.rule_ids} lack {e['rule_ids_any']}")
    steps = [p.get("step") for p in d.price_lines]
    if "price_step" in e and e["price_step"] not in steps:
        ok = False; notes.append(f"price lines {steps} lack {e['price_step']}")
    if "price_steps" in e and not all(s in steps for s in e["price_steps"]):
        ok = False; notes.append(f"price lines {steps} lack {e['price_steps']}")
    if "reachable_contains" in e and not any(e["reachable_contains"] in r for r in d.reasons):
        ok = False; notes.append(f"no reason names '{e['reachable_contains']}'")
    if "gate_approved" in e and (d.gate or {}).get("approved") != e["gate_approved"]:
        ok = False; notes.append("gate verdict differs")
    if "forced_action" in e and ((d.gate or {}).get("forced_action") or {}).get("action") != e["forced_action"]:
        ok = False; notes.append("forced action differs")
    if "machine_touched" in e and (worker or {}).get("machine_touched", False) != e["machine_touched"]:
        ok = False; notes.append("worker touched a machine")
    if cert is not None:
        for k in e.get("certificate_has", []):
            if not cert.get(k):
                ok = False; notes.append(f"certificate lacks {k}")
        if e.get("provenance_resolves") and not all(x["exists"] for x in cert["provenance"]["evidence"]):
            ok = False; notes.append("an evidence path does not resolve")
        if e.get("some_family_wider_than_tolerance") and not any(a["wider_than_tolerance"] for a in cert["anchor_coverage"]):
            ok = False; notes.append("no family wider than its tolerance")
    return ok, notes


def cost_honesty(certs: list[dict]) -> dict:
    """S7: every priced line of every certificate names a machine in the price table and a source; every € equals hours × the list price."""
    checked = traced = 0; misses = []
    for c in certs:
        for k in c["cost_record"]:
            checked += 1
            if k.get("eur_ex_vat") is None:
                if k.get("source"):
                    traced += 1
                else:
                    misses.append((c["molecule"]["name"], k["step"], "unpriced line without a source"))
                continue
            cls = k.get("machine_class") or k.get("machine")
            price = prices.MACHINES.get(cls, {}).get("eur_per_hour")
            if price is None or not k.get("source"):
                misses.append((c["molecule"]["name"], k["step"], "no price class or source")); continue
            if abs(round(k["hours"] * price, 2) - k["eur_ex_vat"]) > 0.011:
                misses.append((c["molecule"]["name"], k["step"], f"€ {k['eur_ex_vat']} ≠ {k['hours']} h × {price}")); continue
            traced += 1
    return dict(lines_checked=checked, lines_traced=traced, fraction=(traced / checked if checked else None), misses=misses)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--with-catalog", action="store_true", help="also run S5: website/export/build_catalog.py (≈ a minute)")
    ap.add_argument("--no-candidate", action="store_true", help="S3 with a fixed SMILES instead of a fresh module-06 draw (tests)")
    a = ap.parse_args(argv)
    S = json.load(open(HERE / "scenarios" / "scenarios.json", encoding="utf-8"))
    cat = Catalog()
    OUT.mkdir(exist_ok=True); (OUT / "certificates").mkdir(exist_ok=True)
    results = []; certs = []; ledger_rows = []
    candidate = None
    for sc in S["scenarios"]:
        req = dict(sc["request"])
        if req["molecule"].startswith("<module-06"):
            if a.no_candidate:
                candidate = dict(smiles="c1ccc2c(c1)ccc1c2ccc2cc3ccccc3cc12", source="fixed test candidate (no module-06 draw)")
            else:
                from m08.candidates import draw_candidate
                candidate = draw_candidate()
            req["molecule"] = candidate["smiles"]
        d = decide(Request(**req), cat)
        cert = worker = None
        if d.kind == "certificate":
            cert = certificate(cat.find(req["molecule"]), cat); pj, pm = write(cert, OUT / "certificates"); certs.append(cert)
        if d.kind == "run_order":
            worker = execute_run_order(d.model_dump(), cat)
        ok, notes = judge(sc, d, cert, worker)
        ledger_rows.append(dict(date=d.date, scenario=sc["id"], molecule=d.name or req["molecule"], kind=d.kind, gate=d.gate_named or "", rules=" ".join(d.rule_ids), line=d.ledger_line))
        results.append(dict(id=sc["id"], title=sc["title"], request=req, decision=d.model_dump(), certificate_files=[str(p.relative_to(HERE)).replace("\\", "/") for p in ((pj, pm) if cert else ())],
                            worker=worker, candidate=candidate if sc["id"] == "S3" else None, prediction=sc["prediction"], passed=ok, notes=notes))
        print(f"{sc['id']}: {'pass' if ok else 'FAIL'} — {d.kind}" + (f" ({d.gate_named})" if d.gate_named else "") + (f"  notes: {notes}" if notes else ""))
    with open(OUT / "requests_ledger.csv", "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ledger_rows[0].keys()))
        if fh.tell() == 0:
            w.writeheader()
        w.writerows(ledger_rows)
    mech = {"S7": cost_honesty(certs)}
    print(f"S7: {mech['S7']['lines_traced']}/{mech['S7']['lines_checked']} cost lines trace to a run log or the price table" + (f"; misses {mech['S7']['misses']}" if mech["S7"]["misses"] else ""))
    if a.with_catalog:
        t0 = time.time()
        r = subprocess.run([sys.executable, str(REPO / "website" / "export" / "build_catalog.py")], capture_output=True, text=True, check=False)
        summ = {}
        if "{" in r.stdout:
            try:
                summ = json.loads(r.stdout[r.stdout.find("{"):])
            except json.JSONDecodeError:
                summ = {}
        mech["S5"] = dict(exit_code=r.returncode, seconds=round(time.time() - t0), problems=summ.get("problems"), n_molecules=summ.get("n_molecules"), stderr_tail=r.stderr[-400:])
        print(f"S5: build_catalog.py exit {r.returncode}, problems {summ.get('problems')}")
    mech["S6"] = dict(status="not run in this build: needs the built site and axe (website backlog rows 8–9)")
    rec = dict(date=time.strftime("%Y-%m-%d %H:%M"), frozen=S["frozen"], n_pass=sum(r["passed"] for r in results), n_scenarios=len(results), results=results, mechanical=mech,
               licence=cert["provenance"]["licence"] if certs else None, provenance=provenance())
    p = OUT / f"scenario_results_{time.strftime('%Y-%m-%d')}.json"
    json.dump(rec, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{rec['n_pass']}/{rec['n_scenarios']} scenarios pass; written {p.relative_to(HERE)}")
    return 0 if rec["n_pass"] == rec["n_scenarios"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
