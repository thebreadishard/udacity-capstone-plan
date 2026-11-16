"""Did geomeTRIC converge on the engine check's eight pyscf-route geometries (TASKS 228)?

`engine_check.py optimise` of 2-3 Nov 2026 called pyscf's `geometric_solver.optimize`, which drops the convergence flag, so the run never
learned the outcome. What it left per molecule: `result.json` (`steps`, `max_force_au` = the largest Cartesian component of a gradient
recomputed at the final geometry) and `step.log`, the run's stdout with geomeTRIC's own lines. This reads the last `Step` line of each
`step.log` (displacement rms/max in Angstrom, gradient rms/max in E_h/bohr over per-atom norms, energy change in E_h) against the
GAU_TIGHT set the run asked for, and whether geomeTRIC's `Converged! =D` line follows it.

    python convergence_read.py <engine check folder>/pyscf/molecules [--out <folder>]

The criteria, from the geomeTRIC 1.1.1 the run used (WSL `~/qc05/lib/python3.12/site-packages/geometric`):
`params.py:192` `'GAU_TIGHT': [1e-6, 1e-5, 1.5e-5, 4e-5, 6e-5]` in the order energy, grms, gmax, drms, dmax (`params.py:185`);
`optimize.py:879-883` compares each with `<`; `optimize.py:917` requires all five (`criteria_met`).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

GAU_TIGHT = {"energy": 1e-6, "grms": 1e-5, "gmax": 1.5e-5, "drms": 4e-5, "dmax": 6e-5}
ANSI = re.compile(r"\x1b\[[0-9;]*m")
NUMBER = r"([-+]?\d\.\d+e[-+]\d+)"
STEP = re.compile(rf"Step\s+(\d+) : Displace = {NUMBER}/{NUMBER} \(rms/max\).*Grad = {NUMBER}/{NUMBER} \(rms/max\) "
                  rf"E \(change\) = [-+]?\d+\.\d+ \({NUMBER}\)")
CONVERGED_LINE = "Converged! =D"
FAILED_LINE = "failed to converge"


def read_molecule(folder: Path) -> dict[str, object]:
    """One molecule's stored convergence numbers and the verdict they allow."""
    stored = json.loads((folder / "result.json").read_text(encoding="utf-8"))["optimisation"]
    row: dict[str, object] = {"id": folder.name, "steps": stored["steps"], "maxsteps": stored["maxsteps"],
                              "convergence_set": stored["convergence_set"], "max_force_au": stored["max_force_au"]}
    log = folder / "step.log"
    if not log.is_file():
        return row | {"verdict": "cannot be told", "missing": "step.log (geomeTRIC's lines)"}
    lines = [ANSI.sub("", s) for s in log.read_text(encoding="utf-8", errors="replace").splitlines()]
    steps = [(k, m) for k, s in enumerate(lines) if (m := STEP.search(s))]
    if not steps:
        return row | {"verdict": "cannot be told", "missing": "a geomeTRIC Step line in step.log"}
    at, last = steps[-1]
    drms, dmax, grms, gmax, de = (float(x) for x in last.groups()[1:])
    values = {"energy": abs(de), "grms": grms, "gmax": gmax, "drms": drms, "dmax": dmax}
    met = {k: values[k] < GAU_TIGHT[k] for k in GAU_TIGHT}
    said_converged = sum(CONVERGED_LINE in s for s in lines)
    converged_after_last = any(CONVERGED_LINE in s for s in lines[at + 1:])
    said_failed = sum(FAILED_LINE in s.lower() for s in lines)
    row |= {"last_step": int(last.group(1)), "last_step_values": values, "criteria_met": met,
            "converged_lines": said_converged, "failed_lines": said_failed}
    if all(met.values()) and said_converged == 1 and converged_after_last and not said_failed:
        return row | {"verdict": "converged"}
    if said_failed or not said_converged:
        return row | {"verdict": "not converged"}
    return row | {"verdict": "cannot be told", "missing": "agreement between the last Step line and geomeTRIC's Converged line"}


def table(rows: list[dict[str, object]]) -> str:
    """The eight rows as a Markdown table."""
    head = ("| molecule | steps (cap) | last step | abs dE (E_h) | grms | gmax (E_h/bohr) | drms | dmax (Angstrom) | "
            "geomeTRIC line | stored max_force_au | verdict |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    limit = (f"| GAU_TIGHT, each `<` | | | {GAU_TIGHT['energy']:.1e} | {GAU_TIGHT['grms']:.1e} | {GAU_TIGHT['gmax']:.1e} | "
             f"{GAU_TIGHT['drms']:.1e} | {GAU_TIGHT['dmax']:.1e} | | | |\n")
    body = ""
    for r in rows:
        v = r.get("last_step_values")
        cells = [f"{v[k]:.3e}" for k in GAU_TIGHT] if isinstance(v, dict) else ["-"] * 5
        said = "Converged! =D" if r.get("converged_lines") else ("failed" if r.get("failed_lines") else "-")
        verdict = str(r["verdict"]) + (f" (missing: {r['missing']})" if "missing" in r else "")
        body += (f"| {r['id']} | {r['steps']} ({r['maxsteps']}) | {r.get('last_step', '-')} | " + " | ".join(cells)
                 + f" | {said} | {float(str(r['max_force_au'])):.3e} | {verdict} |\n")
    return head + limit + body


def plan_relative(path: Path) -> str:
    """`path` from the plan folder on (the folder above its last `probes` part), so the record names no checkout."""
    parts = path.resolve().parts
    if "probes" not in parts:
        raise SystemExit(f"{path}: not under a plan folder's probes/")
    return "/".join(parts[len(parts) - 1 - parts[::-1].index("probes"):])


def main() -> None:
    ap = argparse.ArgumentParser(description="Read the engine check's stored geomeTRIC convergence numbers.")
    ap.add_argument("molecules", type=Path, help="<engine check folder>/pyscf/molecules")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    folders = sorted(p for p in a.molecules.iterdir() if (p / "result.json").is_file())
    if not folders:
        raise SystemExit(f"{a.molecules}: no molecule folder with a result.json")
    rows = [read_molecule(f) for f in folders]
    text = table(rows)
    for name, content in (("convergence_read.json", json.dumps({"criteria": GAU_TIGHT, "source": plan_relative(a.molecules), "rows": rows}, indent=1)),
                          ("convergence_read.md", text)):
        tmp = a.out / (name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(a.out / name)
    print(text)
    print({v: sum(r["verdict"] == v for r in rows) for v in ("converged", "not converged", "cannot be told")})


if __name__ == "__main__":
    main()
