"""Build the frozen mini-corpus of the rung-C trainer's regression pin (TASKS 72, 16 Oct 2026).

The pin first ran on the live corpus, whose first five pool molecules and class scales move whenever molecules are merged into it (chain 40
merged 64 five-ring molecules at 11:32 and the pin went red without a code change). This copies a fixed, rule-chosen set of molecules —
only the files the trainer reads — into `tests/data/rungC_pin_corpus/`, with a manifest of their names and a sha256 per file, so the pin
reads the same bytes on every machine, CI included.

The rule, each pick in sha1 order of the id, from folders with geometry, result and both FD Hessians, layers A / A2 / B, no imaginary mode,
none in hold-out (c) or rung 4's test family:
    A    8 molecules: the first 4 with the analytic pair, then the first 4 without;
    A2   3 molecules from each of the first 3 cores (sha1 order of the core name) that have at least 3 molecules of ≤ 24 atoms;
    B    the first 10 of ≤ 22 atoms;
    APT  then layer-B molecules with a passed dipole file (≤ 22 atoms) until at least 4 of the set have one.
`excluded` = the first two pool molecules of the set by E6's split rule, for the chainlike case's excluded-ids file; `size_min_atoms` = the
atom count of the third-largest pool molecule, the chainlike case's size threshold (the queued chains' 27–28 atoms do not occur in a set
this small, so the switch is exercised at the set's own scale).

    python tests/data/make_rungC_pin_corpus.py [--corpus modules/05_support_predictor/corpus]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "rungC_pin_corpus"
FILES = ("geometry.json", "result.json", "hessian_b3lyp.npz", "hessian_wb97x.npz", "hessian_b3lyp_analytic.npz",
         "hessian_wb97x_analytic.npz", "dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz")
LAYERS = ("A", "A2", "B")


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {ln.split()[0] for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}


def apt_passed(d: Path) -> bool:
    for name in ("dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz"):
        if (d / name).exists():
            with np.load(d / name) as z:
                return bool(z["passed"])
    return False


def candidates(corpus: Path) -> list[dict]:
    """Every admissible molecule with what the rule needs to know about it."""
    names = {}
    with open(corpus / "manifest.csv", newline="", encoding="utf-8") as f:
        names = {r["id"]: r["name"] for r in csv.DictReader(f)}
    excluded = frozen_ids(corpus / "holdout_c.txt") | frozen_ids(corpus / "holdout_rung4_test.txt")
    out = []
    for d in sorted(p for p in (corpus / "molecules").iterdir() if p.is_dir()):
        if d.name in excluded or not all((d / f).exists() for f in FILES[:4]):
            continue
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        layer = r.get("layer", "A2" if d.name.startswith("A2_") else "A")
        if layer not in LAYERS or r.get("n_imaginary_b3lyp", 0) or r.get("n_imaginary_wb97x", 0):
            continue
        n_atoms = len(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["symbols"])
        out.append({"id": d.name, "dir": d, "layer": layer, "name": names.get(d.name, d.name), "core": names.get(d.name, d.name).split("+")[0],
                    "atoms": n_atoms, "analytic": all((d / f).exists() for f in FILES[4:6]), "apt": apt_passed(d)})
    return sorted(out, key=lambda m: sha1(m["id"]))


def choose(mols: list[dict]) -> list[dict]:
    """The rule of the module docstring."""
    a = [m for m in mols if m["layer"] == "A"]
    picks = [m for m in a if m["analytic"]][:4] + [m for m in a if not m["analytic"]][:4]
    a2 = [m for m in mols if m["layer"] == "A2" and m["atoms"] <= 24]
    by_core: dict[str, list[dict]] = {}
    for m in a2:
        by_core.setdefault(m["core"], []).append(m)
    cores = sorted((c for c, ms in by_core.items() if len(ms) >= 3), key=sha1)[:3]
    picks += [m for c in cores for m in by_core[c][:3]]
    picks += [m for m in mols if m["layer"] == "B" and m["atoms"] <= 22][:10]
    chosen = {m["id"] for m in picks}
    # the APT additions come from layer B only: an A2 molecule of another core would add a core and could move hold-out (b), an A molecule
    # would move hold-out (a)'s quarter
    chosen = {m["id"] for m in picks}
    for m in mols:
        if sum(p["apt"] for p in picks) >= 4:
            break
        if m["apt"] and m["layer"] == "B" and m["atoms"] <= 22 and m["id"] not in chosen:
            picks.append(m)
            chosen.add(m["id"])
    return sorted(picks, key=lambda m: sha1(m["id"]))


def pool_of(picks: list[dict]) -> list[str]:
    """E6's split on the set: hold-out (a) = the first quarter of layer A, (b) = the A2 molecules of the first two cores; the rest is the pool."""
    a = sorted((m["id"] for m in picks if m["layer"] == "A"), key=sha1)
    test_a = set(a[: max(1, math.ceil(0.25 * len(a)))])
    cores = sorted({m["core"] for m in picks if m["layer"] == "A2"}, key=sha1)[:2]
    test_b = {m["id"] for m in picks if m["layer"] == "A2" and m["core"] in cores}
    return sorted((m["id"] for m in picks if m["id"] not in test_a | test_b), key=sha1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", type=Path, default=PLAN / "modules" / "05_support_predictor" / "corpus")
    a = ap.parse_args()
    picks = choose(candidates(a.corpus))
    if OUT.exists():
        shutil.rmtree(OUT)
    files = {}
    for m in picks:
        dst = OUT / "molecules" / m["id"]
        dst.mkdir(parents=True)
        for name in FILES:
            if (m["dir"] / name).exists():
                shutil.copy2(m["dir"] / name, dst / name)
                files[f"{m['id']}/{name}"] = sha256(dst / name)
    with open(OUT / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name"])
        w.writerows([m["id"], m["name"]] for m in picks)
    pool = pool_of(picks)
    atoms = {m["id"]: m["atoms"] for m in picks}
    size_min = sorted((atoms[i] for i in pool), reverse=True)[2]
    record = {"rule": "tests/data/make_rungC_pin_corpus.py docstring", "source": str(a.corpus.relative_to(PLAN)), "excluded": pool[:2],
              "size_min_atoms": size_min, "molecules": [{k: m[k] for k in ("id", "layer", "name", "atoms", "analytic", "apt")} for m in picks],
              "sha256": files}
    (OUT / "pin_corpus.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"{len(picks)} molecules ({', '.join(f'{x} {sum(m['layer'] == x for m in picks)}' for x in LAYERS)}), {len(files)} files, "
          f"{size / 1e6:.1f} MB; analytic {sum(m['analytic'] for m in picks)}, APT {sum(m['apt'] for m in picks)}; pool {len(pool)}, "
          f"excluded {pool[:2]}, size hold-out ≥ {size_min} atoms: {sum(atoms[i] >= size_min for i in pool)} pool molecules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
