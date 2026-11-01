"""The engine check's run (TASKS 73; `GoalGathering/notes/PreRegistration_2026-11-01_Engine_Check.md`): the clean hold-out (a) on pyscf +
geomeTRIC geometries against the corpus's psi4 geometries, the network read on both, each against the analytic ωB97X Hessian at its own
geometry. The read is `probes/engine_check_read.py`.

    python probes/engine_check.py prepare <out>                       # Windows: the three folder sets and the ids
    python probes/engine_check.py prepare <out> --smoke               # water's start only (the smoke)
    python probes/engine_check.py optimise <folder> [--threads 6]     # WSL pyscf: geomeTRIC from start.json to geometry.json
    (then corpus/analytic_hessians.py <folder> --functionals b3lyp,wb97x --no-apt --grid 99,590, as the corpus's labels)
    python probes/engine_check.py evaluate <out> <route> <model> ...  # Windows: the network's error per family and seed

`prepare` writes, per molecule of `a8`: `check0/molecules/<id>` (the corpus folder as the licence's read loaded it: psi4's FD pair, the
analytic pair substituted), `psi4/molecules/<id>` (the corpus geometry and its analytic pair as an analytic-only folder) and
`pyscf/molecules/<id>/start.json` (the start the corpus's psi4 run began from, its `job.json`). Both compared routes are analytic-only
folders, so the loader labels each molecule's mode families from its own analytic B3LYP Hessian by the same path; check 0 proves on the
`check0` copies that `evaluate` reproduces the models' recorded `a8` read.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
import time
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
CORPUS = M05 / "corpus" / "molecules"
A8_IDS = M05 / "out" / "holdout_a_clean_2026-10-30.txt"
GRID = (99, 590)                     # the analytic Hessians' grid; the optimisation runs on it too
CONVERGENCE = {"convergence_set": "GAU_TIGHT", "maxsteps": 100}
ANALYTIC_ONLY = "analytic_only"      # learning_curve_layerA's label for a folder labelled by analytic Hessians alone
NOT_COPIED = ("psi4.out", "worker_stdout.txt")
EVAL_THREADS = 4                     # as the recorded a8 reads ran (probes/holdout_a_clean.sh): float32 sums follow the thread count
WATER = {"symbols": ["O", "H", "H"], "xyz_angstrom": [["O", 0.0, 0.0, 0.1173], ["H", 0.0, 0.7572, -0.4692], ["H", 0.0, -0.7572, -0.4692]],
         "masses_amu": [15.99491462, 1.00782503, 1.00782503]}


def a8_ids() -> list[str]:
    return [s.strip() for s in A8_IDS.read_text(encoding="utf-8").splitlines() if s.strip() and not s.startswith("#")]


def write_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    tmp.replace(path)


def manifest_rows(ids: list[str]) -> list[dict]:
    with open(CORPUS.parent / "manifest.csv", newline="", encoding="utf-8") as f:
        rows = {r["id"]: r for r in csv.DictReader(f)}
    return [rows[i] for i in ids]


def write_manifest(root: Path, rows: list[dict]) -> None:
    with open(root / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def prepare(out: Path, smoke: bool) -> None:
    """The folder sets; refuses an out folder that exists, so a prepared run is never overwritten."""
    if out.exists():
        raise SystemExit(f"{out} exists: a prepared run is never overwritten")
    if smoke:
        d = out / "smoke" / "molecules" / "water"
        d.mkdir(parents=True)
        write_json(d / "start.json", {"id": "water", "layer": "smoke", **WATER, "source": "textbook water, the smoke"})
        print(f"prepared the smoke in {d}")
        return
    ids = a8_ids()
    rows = manifest_rows(ids)
    for route in ("check0", "psi4", "pyscf"):
        (out / route / "molecules").mkdir(parents=True)
        write_manifest(out / route, rows)
    for i in ids:
        src = CORPUS / i
        shutil.copytree(src, out / "check0" / "molecules" / i, ignore=shutil.ignore_patterns(*NOT_COPIED))
        geometry = json.loads((src / "geometry.json").read_text(encoding="utf-8"))
        result = json.loads((src / "result.json").read_text(encoding="utf-8"))
        psi4 = out / "psi4" / "molecules" / i
        psi4.mkdir()
        shutil.copy2(src / "geometry.json", psi4 / "geometry.json")
        for name in ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"):
            shutil.copy2(src / name, psi4 / name)
        write_json(psi4 / "result.json", {"id": i, "layer": result["layer"], "labels": ANALYTIC_ONLY, "source": f"corpus {i}"})
        job = json.loads((src / "job.json").read_text(encoding="utf-8"))
        start = out / "pyscf" / "molecules" / i
        start.mkdir()
        write_json(start / "start.json", {"id": i, "layer": result["layer"], "symbols": geometry["symbols"],
                                          "xyz_angstrom": job["xyz_angstrom"], "masses_amu": geometry["masses_amu"],
                                          "source": f"corpus {i}/job.json (the psi4 run's start)"})
    (out / "ids.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    print(f"prepared {len(ids)} molecules in {out}")


def optimise(folder: Path, threads: int, max_memory: int) -> None:
    """geomeTRIC from start.json at the labels route's level (`analytic_hessians.labels_mol` / `labels_scf`, B3LYP, grid 99/590): writes
    geometry.json (bohr, the corpus's masses) and result.json (analytic-only, the optimisation's record). pyscf's log goes to pyscf.log."""
    sys.path[:0] = [str(M05 / "corpus"), str(PLAN / "probes")]
    import analytic_hessians as AH
    import numpy as np
    from library_log import PYSCF_LOG_NAME
    from pyscf import lib
    from pyscf.geomopt.geometric_solver import optimize

    if (folder / "geometry.json").exists():
        raise SystemExit(f"{folder}: geometry.json exists; an optimised folder is never redone")
    start = json.loads((folder / "start.json").read_text(encoding="utf-8"))
    lib.num_threads(threads)
    bohr = 1.0 / 0.529177210903
    geometry = {"symbols": start["symbols"], "coords_bohr": [[x * bohr for x in row[1:]] for row in start["xyz_angstrom"]]}
    steps = []
    t0 = time.time()
    with open(folder / PYSCF_LOG_NAME, "a", encoding="utf-8") as log:
        mf, _ = AH.labels_scf(AH.labels_mol(geometry, log, max_memory=max_memory), "b3lyp", GRID)
        mol_eq = optimize(mf, assert_convergence=True, callback=lambda env: steps.append(round(time.time() - t0, 1)), **CONVERGENCE)
        mf_eq, e_opt = AH.labels_scf(AH.labels_mol({"symbols": start["symbols"], "coords_bohr": mol_eq.atom_coords().tolist()}, log,
                                                   max_memory=max_memory), "b3lyp", GRID)
        g = mf_eq.nuc_grad_method().kernel()
    seconds = round(time.time() - t0, 1)
    write_json(folder / "geometry.json", {"symbols": start["symbols"], "coords_bohr": mol_eq.atom_coords().tolist(),
                                          "masses_amu": start["masses_amu"]})
    write_json(folder / "result.json", {"id": start["id"], "layer": start["layer"], "labels": ANALYTIC_ONLY,
                                        "optimisation": {"engine": "geomeTRIC via pyscf.geomopt.geometric_solver.optimize", **CONVERGENCE,
                                                         "functional": "b3lyp", "basis": "6-31g* (Cartesian d)", "grid": list(GRID),
                                                         "steps": len(steps), "seconds": seconds, "e_opt": float(e_opt),
                                                         "max_force_au": float(np.abs(g).max()), "start": start["source"]}})
    print(f"[engine check] {start['id']} optimised: {len(steps)} steps, {seconds} s, max |force| {np.abs(g).max():.1e} E_h/bohr", flush=True)


def family_errors(molecules: Path, ids: list[str], models: list[Path]) -> dict[str, list[float]]:
    """The network's per-family error on `ids` for each model (seed), by the licence's read-out (`readouts(...)['diag_rms']`)."""
    sys.path[:0] = [str(M05 / "m05"), str(PLAN / "probes")]
    import rungC_train as RT
    from promotion_read import FAMILIES
    from rungC_equivariant import load_molecule

    out: dict[str, list[float]] = {f: [] for f in FAMILIES}
    for path in models:
        model, ck = RT.load_hybrid_model(path)
        cfg = RT.tensor_config(ck)
        mols, *_ = RT.load_corpus(str(molecules), True, log=lambda *_: None, settings=cfg.primitives)
        if missing := sorted(set(ids) - mols.keys()):
            raise ValueError(f"{molecules}: the loader did not take {missing}")
        tensors = {i: RT.molecule_tensors(i, load_molecule(molecules / i, use_analytic=True), mols[i], molecules / i, cfg,
                                          molecules.parent / "ls_targets") for i in ids}
        model.eval()
        r = RT.readouts(mols, ids, [i for i in ck["train_ids"] if i in mols], RT.predictor(model, tensors, mols))
        for f in FAMILIES:
            out[f].append(float(r["diag_rms"][f]))
    return out


def check0(out: Path, ids: list[str], models: list[Path], records: list[Path]) -> float:
    """The largest |difference| between `family_errors` on the check0 copies and the models' recorded `a8` read (same order of seeds)."""
    sys.path.insert(0, str(PLAN / "probes"))
    from promotion_read import FAMILIES

    mine = family_errors(out / "check0" / "molecules", ids, models)
    worst = 0.0
    for k, rec_path in enumerate(records):
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        if Path(rec["model"]).name != models[k].name:
            raise ValueError(f"{rec_path} is the read of {rec['model']}, not of {models[k]}")
        for f in FAMILIES:
            worst = max(worst, abs(mine[f][k] - float(rec["a8"]["diag_rms"][f])))
    return worst


def evaluate(out: Path, route: str, models: list[Path], records: list[Path], threads: int = EVAL_THREADS) -> None:
    """`<out>/<route>.json` for `engine_check_read.py`; the psi4 route runs check 0 first (`records`: the models' a8 reads)."""
    import torch

    torch.set_num_threads(threads)
    if route not in ("psi4", "pyscf"):
        raise SystemExit(f"route {route!r}: psi4 or pyscf")
    if route == "psi4" and len(records) != len(models):
        raise SystemExit("the psi4 route needs one recorded a8 read per model (--records) for check 0")
    ids = (out / "ids.txt").read_text(encoding="utf-8").split()
    rec = {"route": route, "models": [p.name for p in models], "molecules": ids, "threads": threads,
           "family_errors": family_errors(out / route / "molecules", ids, models)}
    if route == "psi4":
        worst = check0(out, ids, models, records)
        rec["check0"] = {"max_abs_difference": worst if math.isfinite(worst) else None, "records": [p.name for p in records]}
        print(f"[engine check] check 0: max |difference| against the recorded a8 read {worst:.2e} cm-1", flush=True)
    write_json(out / f"{route}.json", rec)
    print(f"[engine check] wrote {out / f'{route}.json'}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("out", type=Path)
    p.add_argument("--smoke", action="store_true")
    o = sub.add_parser("optimise")
    o.add_argument("folder", type=Path)
    o.add_argument("--threads", type=int, default=6)
    o.add_argument("--max-memory", type=int, default=4000, help="pyscf's max_memory in MB (below the run's cap)")
    e = sub.add_parser("evaluate")
    e.add_argument("out", type=Path)
    e.add_argument("route")
    e.add_argument("models", nargs="+", type=Path)
    e.add_argument("--records", nargs="*", type=Path, default=[], help="the models' recorded a8 reads, in the models' order (psi4 route)")
    e.add_argument("--threads", type=int, default=EVAL_THREADS, help="torch's threads (the recorded reads' count by default)")
    a = ap.parse_args()
    if a.action == "prepare":
        prepare(a.out, a.smoke)
    elif a.action == "optimise":
        optimise(a.folder, a.threads, a.max_memory)
    else:
        evaluate(a.out, a.route, a.models, a.records, a.threads)


if __name__ == "__main__":
    main()
