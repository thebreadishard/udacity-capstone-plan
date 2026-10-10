"""The certificate: spectrum · spectral shape (heights where an APT exists, 10 Oct 2026) · per-band error budget · cost record · coverage ·
provenance, every number with its source, signed by release and commit. A rung not reached shows '—' and why. Written as JSON (the record)
and Markdown (the page)."""
from __future__ import annotations

import json
import math
import re
import subprocess
import time
from pathlib import Path

from . import prices
from . import spectrum as shape_mod
from .catalog import FAMILY_SOURCE, PLAN, REPO, RUNG_LABELS, Catalog, family
from .licence import state as licence_state
from .replay import replay_run

MODE_RE = re.compile(r"mode (\d+)[^0-9]{0,40}?(\d{3,4}\.\d) cm", re.I)


def commit_hash() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _rms(xs: list[float]) -> float | None:
    return round(math.sqrt(sum(x * x for x in xs) / len(xs)), 2) if xs else None


def anchor_coverage(evidence: list[str], u_band: dict[str, dict]) -> list[dict]:
    """What the anchor evidence files say per family. Two kinds of file exist today: a per-mode family reading (M3: 'mode 12, 785.3 cm⁻¹') and
    a diagonal-deck table with a family column and an 'ω′ − ω_CC' column (R0). The result is per family: covered or not, and, where the table
    gives it, the RMS of the composite's deviation from CCSD(T) against the laboratory tolerance — the honest failure case shows here."""
    per_family: dict[str, dict] = {}
    for rel in evidence:
        p = PLAN / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = MODE_RE.search(text)
        if m and "| mode | family |" not in text:
            fam = family(float(m.group(2)))
            per_family.setdefault(fam, dict(family=fam, evidence=[], modes=[]))
            per_family[fam]["evidence"].append(rel); per_family[fam]["modes"].append(dict(mode=int(m.group(1)), omega=float(m.group(2))))
            continue
        header = None
        for line in text.split("\n"):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] == "mode":
                header = cells; continue
            if header and len(cells) == len(header) and cells[0].isdigit():
                fam_raw = cells[header.index("family")]
                fam = {"CH-oop": "CH-oop (10.5-15 um; benzene nu11 at 673 included)", "ring-ip": "ring / CH-ip (9-10.5 um)", "CH-ip-bend": "CH-ip-bend (8.6 um)",
                       "CC-stretch": "CC-stretch (6.2 um)", "CH-stretch": "CH-stretch"}.get(fam_raw)
                if fam is None:                                          # e.g. ring-breathing-a1g, ring-ip-b1u: placed by their wavenumber
                    try:
                        fam = family(float(cells[header.index("ω B3LYP")]))
                    except (ValueError, KeyError):
                        continue
                try:
                    dev = float(cells[header.index("ω′ − ω_CC")].replace("−", "-"))
                except (ValueError, KeyError):
                    continue
                per_family.setdefault(fam, dict(family=fam, evidence=[], modes=[]))
                if rel not in per_family[fam]["evidence"]:
                    per_family[fam]["evidence"].append(rel)
                per_family[fam]["modes"].append(dict(mode=int(cells[0]), omega=float(cells[header.index("ω B3LYP")]), dev_vs_ccsdt=dev))
    out = []
    for fam, d in per_family.items():
        devs = [m["dev_vs_ccsdt"] for m in d["modes"] if "dev_vs_ccsdt" in m]
        tol = u_band.get(fam, {}).get("u_band")
        rms = _rms(devs)
        out.append(dict(family=fam, n_modes=len(d["modes"]), evidence=d["evidence"], rms_dev_vs_ccsdt=rms, u_band=tol,
                        wider_than_tolerance=(rms is not None and tol is not None and rms > tol),
                        reading=(f"composite vs CCSD(T): RMS {rms:.1f} cm⁻¹ against the laboratory tolerance {tol:.1f} — " + ("wider: not decidable at this rung, shown as such" if rms > tol else "within")
                                 if rms is not None and tol is not None else "a family reading exists (curvature at DZ and TZ); no per-mode deviation table")))
    return sorted(out, key=lambda r: r["family"])


def certificate(row: dict, catalog: Catalog) -> dict:
    mol = catalog.molecule(row["id"])
    lic = licence_state()
    rung = int(row["rung"])
    ub = catalog.u_band(row["name"])
    freqs = {}
    budget = {}
    if mol:
        for fn in ("b3lyp", "wb97x"):
            vib = mol["frequencies_cm"][fn]["vibrational"]
            freqs[fn] = dict(n=len(vib), values_cm=[round(float(v), 1) for v in vib], n_imaginary=mol["n_imaginary"][fn],
                             source=f"website export molecules/{row['id']}.json ← corpus molecules/{row['id']}/ (deck {mol['ledger']['deck']})")
        fams: dict[str, list[float]] = {}
        for v in mol["frequencies_cm"]["b3lyp"]["vibrational"]:
            fams.setdefault(family(float(v)), []).append(float(v))
        for fam, vs in sorted(fams.items()):
            budget[fam] = dict(n_modes=len(vs), omega_range=[round(min(vs), 1), round(max(vs), 1)], u_band_lab=ub.get(fam, {}).get("u_band"),
                               u_band_source=ub.get(fam, {}).get("source"), ensemble_pm=None,
                               ensemble_note="— : no predicted correction is shown; " + lic["statement"].split(";")[0])
    shape = shape_mod.shape(row["id"], mol["frequencies_cm"]["b3lyp"]["vibrational"] if mol else None) if mol else dict(kind="none", reason="no cheap rung")
    if mol:
        shape["accuracy"] = shape_mod.measured_accuracy()
    coverage = anchor_coverage(row.get("evidence", []), ub) if rung >= 4 else []
    run = replay_run(mol) if mol else None
    cost = []
    if run:
        cost.append(dict(step="cheap rung (deck v1, both functionals)", **prices.price_of_run(float(run["seconds_total"]), run["machine"]),
                         breakdown_s=dict(optimise=run["seconds_optimise"], hessian_b3lyp=run["seconds_hessian_b3lyp"], hessian_wb97x=run["seconds_hessian_wb97x"]),
                         replayed_from=run["source"], replay=True))
    if rung >= 4:
        for step in (("anchor_m3_family_reading_naphthalene",) if row["name"] == "naphthalene" else ()):
            cost.append(dict(step="anchor family readings (M3, two families, laptop)", **{k: v for k, v in prices.step_price(step).items() if k not in ("step", "note")},
                             note="two families read (evidence files); hours per family from the M3 record; the E8 whole-molecule Hessian is computing (frozen 10, 28 Sep) and joins this record when read"))
        if row["name"] == "benzene":
            cost.append(dict(step="anchor: E8 CCSD(T)/cc-pVDZ Hessian (72 gradients, rented machine, 24 Sep 2026)", eur_ex_vat=None, hours=None, machine="CCX53",
                             source="probes/results_m1/e8_benzene_ccpvdz/E8_locality_benzene.md; the run's hours are not in a cost record yet — shown as not priced, not as €0"))
    prov = dict(release=row.get("releases", []), deck_hash=mol["ledger"]["deck"] if mol else None, commit=commit_hash(), export_built_utc=catalog.summary["built_utc"],
                export_sources_sha256=catalog.summary.get("sources"), evidence=[dict(path=e, exists=(PLAN / e).exists()) for e in row.get("evidence", [])],
                pre_registrations=["GoalGathering/notes/PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md", "modules/08_industry_synthesis/PRE_REGISTRATION.md"],
                family_rule=FAMILY_SOURCE, licence=dict(rule_source=lic["rule_source"], licensed_families=lic["licensed_families"], latest_reading=lic["latest_reading"]))
    ladder = {r: dict(label=RUNG_LABELS[r], reached=(r <= rung and r not in (2, 3)) or (r in (2, 3) and False),
                      note=("—: no family licensed" + ("; when licensed, heights only where an APT exists" if r == 3 else "") if r in (2, 3)
                            else ("" if r <= rung else "— not reached"))) for r in range(6)}
    return dict(kind="certificate", date=time.strftime("%Y-%m-%d %H:%M"), molecule=dict(id=row["id"], name=row["name"], smiles=row.get("smiles"), formula=row.get("formula"),
                layer=row.get("layer"), n_atoms=row.get("n_atoms"), flags=row.get("flags", [])),
                rung=dict(reached=rung, label=RUNG_LABELS[rung], ladder=ladder), spectrum=freqs, spectral_shape=shape, per_band_budget=budget,
                anchor_coverage=coverage,
                laboratory=catalog.lab_bands(row["name"]) if rung >= 5 else dict(n_bands=0, note="not validated against a laboratory record (rung < 5)"),
                cost_record=cost, provenance=prov,
                statement=(f"{row['name']}: rung {rung} ({RUNG_LABELS[rung]}). The cheap-level spectrum is served with the laboratory tolerance per family; no predicted "
                           "correction is shown because no family is licensed; the anchor coverage lists what coupled-cluster evidence exists and where it is wider than the tolerance."))


def to_markdown(c: dict) -> str:
    m = c["molecule"]; r = c["rung"]
    L = [f"# Certificate — {m['name']} ({m['id']}), rung {r['reached']} · {r['label']} — {c['date']}", "", c["statement"], "",
         "## Ladder", "", "| rung | label | status |", "|---|---|---|"]
    for k, v in r["ladder"].items():
        L.append(f"| {k} | {v['label']} | {'reached' if v['reached'] else v['note']} |")
    L += ["", "## Spectrum (cheap rung; harmonic, cm⁻¹)", ""]
    for fn, s in c["spectrum"].items():
        L.append(f"- **{fn}**: {s['n']} vibrational modes, {s['n_imaginary']} imaginary; source {s['source']}")
    L += _shape_markdown(c.get("spectral_shape", {}))
    L += ["", "## Per-band error budget", "", "| family | modes | ω range | laboratory tolerance u_band (cm⁻¹) | ensemble ± | source |", "|---|---|---|---|---|---|"]
    for fam, b in c["per_band_budget"].items():
        L.append(f"| {fam} | {b['n_modes']} | {b['omega_range'][0]}–{b['omega_range'][1]} | {b['u_band_lab']} | — | {b['u_band_source']} |")
    if c["per_band_budget"]:
        L.append(""); L.append("*Ensemble ±:* " + next(iter(c["per_band_budget"].values()))["ensemble_note"] + ".")
    if c["anchor_coverage"]:
        L += ["", "## Anchor coverage (coupled-cluster evidence)", "", "| family | modes read | RMS vs CCSD(T) | u_band | reading | evidence |", "|---|---|---|---|---|---|"]
        for a in c["anchor_coverage"]:
            L.append(f"| {a['family']} | {a['n_modes']} | {a['rms_dev_vs_ccsdt'] if a['rms_dev_vs_ccsdt'] is not None else '—'} | {a['u_band']} | {a['reading']} | {'; '.join(a['evidence'])} |")
    if c["laboratory"].get("n_bands"):
        lab = c["laboratory"]
        L += ["", f"## Laboratory record (rung 5): {lab['n_bands']} bands in {len(lab['records'])} record(s) — {lab['source']}"]
    L += ["", "## Cost record", "", "| step | machine | hours | € ex VAT | source |", "|---|---|---|---|---|"]
    for k in c["cost_record"]:
        L.append(f"| {k['step']} | {k.get('machine')} | {k.get('hours') if k.get('hours') is not None else '—'} | {format(k['eur_ex_vat'], '.2f') if k.get('eur_ex_vat') is not None else 'not priced'} | {k.get('source')} |")
    p = c["provenance"]
    L += ["", "## Provenance", "", f"- releases: {', '.join(p['release']) or '—'}; deck {p['deck_hash']}; commit {p['commit']}; export built {p['export_built_utc']}",
          "- evidence: " + ("; ".join(f"{e['path']} ({'exists' if e['exists'] else 'MISSING'})" for e in p["evidence"]) or "—"),
          f"- licence: {len(p['licence']['licensed_families'])} families licensed ({p['licence']['rule_source']})", f"- family rule: {p['family_rule']}", ""]
    return "\n".join(L)


def _shape_markdown(s: dict) -> list[str]:
    """The spectrum as astronomers read it: the strongest bands, and how well that shape is known (TASKS 39)."""
    L = ["", "## Spectral shape (cheap rung; positions and heights)", ""]
    if s.get("kind") != "positions and heights":
        return L + [f"Positions only: {s.get('reason', '—')}."]
    top = sorted(s["sticks"], key=lambda x: -x["km_mol"])[:8]
    L += [f"{s['n_ir_active']} infrared-active bands of {len(s['sticks'])} modes (the others have height zero and are not drawn); "
          f"{s['broadening']['lineshape']} FWHM {s['broadening']['fwhm_cm']:g} cm⁻¹. APT {s['apt_source']}; Hessian {s['hessian_source']}; "
          f"largest difference to the listed positions {s['max_dev_from_listed_cm']} cm⁻¹.", "",
          "| band (cm⁻¹) | height (km/mol) | family |", "|---|---|---|"]
    L += [f"| {b['omega_cm']} | {b['km_mol']} | {family(b['omega_cm'])} |" for b in sorted(top, key=lambda x: x['omega_cm'])]
    a = s.get("accuracy")
    if a:
        L += ["", "**How well the shape is known** (measured; 'corrected' is the learned correction, not served until a family is licensed):", "",
              "| level | spectrum overlap, cheap → corrected | height error, cheap → corrected | records |", "|---|---|---|---|"]
        for k in ("proxy", "cc"):
            x = a[k]
            L.append(f"| {x['level']} | {x['cheap']['spectrum_overlap']} → {x['corrected']['spectrum_overlap']} | "
                     f"{x['cheap']['intensity_error']} → {x['corrected']['intensity_error']} | {'; '.join(x['sources'])} |")
        L += ["", f"*Overlap:* {a['definitions']['spectrum_overlap']}. *Height error:* {a['definitions']['intensity_error']}. *Benzene:* {a['cc']['note']}. "
              f"*Open:* {a['open'][0]}."]
    return L


def write(c: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"certificate_{c['molecule']['name'].replace(' ', '_')}_{c['molecule']['id']}"
    pj = out_dir / f"{stem}.json"; pm = out_dir / f"{stem}.md"
    json.dump(c, open(pj, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    pm.write_text(to_markdown(c), encoding="utf-8", newline="\n")
    return pj, pm
