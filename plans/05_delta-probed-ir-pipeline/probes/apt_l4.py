"""L4 of the refined-APT registration (TASKS 44; probes/results_m1/apt_refine_install_2026-10-12/REGISTRATION.md): a second route on a sample.

    select  the five molecules, by the registered rule, from the recompute's outputs and the unrefined files they replaced: the two with the
            largest APT change (max |refined − unrefined|, e), then the first, middle and last of the rest by sorted id. Written before any
            field-route number exists.
    read    per molecule, max |refined APT − field-route APT without grid response| against the line 1e-4 e (the derivative the analytic
            Hessian takes); the field route with grid response reported beside.

    python probes/apt_l4.py select --refined <recompute dir> --unrefined <fetched dir> --out <selection.tsv>
    python probes/apt_l4.py read --selection <selection.tsv> --refined <recompute dir> --field <dir of <id>_field.npz> --out <prefix>

APT files: <dir>/<id>/dipole_b3lyp_cphf.npz with key "apt" (3 × 3N); field files: apt_field_route.py's <id>_field.npz.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

APT_FILE = "dipole_b3lyp_cphf.npz"
LINE_E = 1e-4
N_LARGEST, N_SAMPLE = 2, 5


def apt(folder: Path) -> np.ndarray:
    with np.load(folder / APT_FILE) as z:
        return np.array(z["apt"], dtype=float)


def changes(refined: Path, unrefined: Path) -> dict[str, float]:
    """{id: max |refined − unrefined|} over the molecules the recompute wrote."""
    return {d.name: float(np.abs(apt(d) - apt(unrefined / d.name)).max()) for d in sorted(refined.iterdir()) if (d / APT_FILE).is_file()}


def select(change: dict[str, float]) -> list[tuple[str, str]]:
    """[(id, why)] by the registered rule; ties in the change broken by id so the choice is deterministic."""
    if len(change) < N_SAMPLE:
        raise SystemExit(f"{len(change)} recomputed molecules: the rule needs at least {N_SAMPLE}")
    largest = sorted(change, key=lambda i: (-change[i], i))[:N_LARGEST]
    rest = sorted(i for i in change if i not in largest)
    picks = [(i, f"largest change ({change[i]:.2e} e)") for i in largest]
    picks += [(rest[0], "first of the rest"), (rest[len(rest) // 2], "middle of the rest"), (rest[-1], "last of the rest")]
    return picks


def read(selection: list[str], refined: Path, field: Path) -> dict:
    rows = {}
    for i in selection:
        with np.load(field / f"{i}_field.npz") as z:
            no_gr, gr = np.array(z["apt_no_grid_response"]), np.array(z["apt_grid_response"])
        P = apt(refined / i)
        d0, d1 = float(np.abs(P - no_gr).max()), float(np.abs(P - gr).max())
        rows[i] = {"max_diff_no_grid_response_e": d0, "max_diff_grid_response_e": d1, "meets_line": bool(d0 <= LINE_E)}
    missed = [i for i, r in rows.items() if not r["meets_line"]]
    verdict = f"L4 fails on {', '.join(missed)}" if missed else "L4 passes"
    return {"verdict": verdict, "line_e": LINE_E, "molecules": rows}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--refined", type=Path, required=True)
    s.add_argument("--unrefined", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("read")
    r.add_argument("--selection", type=Path, required=True)
    r.add_argument("--refined", type=Path, required=True)
    r.add_argument("--field", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "select":
        picks = select(changes(a.refined, a.unrefined))
        a.out.write_text("# L4 selection (registered rule): id, why\n" + "".join(f"{i}\t{why}\n" for i, why in picks), encoding="utf-8", newline="\n")
        print("\n".join(f"{i}\t{why}" for i, why in picks))
        return 0
    ids = [ln.split("\t")[0] for ln in a.selection.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    res = read(ids, a.refined, a.field)
    Path(f"{a.out}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    lines = [f"# L4 — refined APT against the field route ({res['verdict']}; line {LINE_E:g} e)", "",
             "| molecule | max diff, no grid response (e) | max diff, grid response (e, beside) | line |", "|---|---|---|---|"]
    lines += [f"| {i} | {r['max_diff_no_grid_response_e']:.2e} | {r['max_diff_grid_response_e']:.2e} | {'meets' if r['meets_line'] else 'MISSES'} |"
              for i, r in res["molecules"].items()]
    Path(f"{a.out}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
