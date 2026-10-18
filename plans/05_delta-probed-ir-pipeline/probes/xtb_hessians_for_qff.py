"""GFN2-xTB optimisation and Hessians for a quartic force field (18 Oct 2026; S2 amendment 4) — the xtb counterpart of
pyscf_hessians_for_qff.py, writing the same qcschema-like records (driver, molecule{symbols, geometry in bohr}, return_result in E_h/bohr²)
so that dpir.qff assembles the force field unchanged. Runs in WSL with the xtb binary of the conda env `xtb` (xtb 6.7.1).

    python xtb_hessians_for_qff.py opt <reference.json> <stub.json>     the xtb minimum from a reference geometry, as a stub
    python xtb_hessians_for_qff.py hess <stub_dir> <out_dir>             the xtb Hessian at every stub (existing results skipped)

xtb's Hessian is its own: central differences of analytic gradients, step 0.005 bohr; SCC accuracy --acc 0.01 throughout.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

XTB = os.environ.get("XTB", os.path.expanduser("~/miniforge3/envs/xtb/bin/xtb"))
BOHR_PER_ANGSTROM = 1.8897261246
ACC = os.environ.get("XTB_ACC", "0.01")     # xtb --acc: SCC and integral accuracy (smaller is tighter)


def write_xyz(path, symbols, geom_bohr):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"{len(symbols)}\n\n")
        for s, (x, y, z) in zip(symbols, np.asarray(geom_bohr).reshape(-1, 3) / BOHR_PER_ANGSTROM, strict=True):
            fh.write(f"{s} {x:.10f} {y:.10f} {z:.10f}\n")


def read_xyz(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    n = int(lines[0])
    rows = [ln.split() for ln in lines[2:2 + n]]
    return [r[0] for r in rows], np.array([[float(v) for v in r[1:4]] for r in rows]) * BOHR_PER_ANGSTROM


def read_hessian(path, n_atoms):
    """xtb's `hessian` file (Turbomole $hessian block, E_h/bohr², Cartesian, not mass-weighted) as a 3N × 3N array."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    body = text.split("$hessian", 1)[1].split("$", 1)[0]
    values = np.array(body.split(), float)
    n = 3 * n_atoms
    if values.size != n * n:
        raise ValueError(f"{path}: {values.size} numbers, expected {n * n}")
    return values.reshape(n, n)


def run_xtb(symbols, geom_bohr, flags):
    """Run xtb in a fresh directory on the geometry; returns that directory (the caller reads what it needs). Fails loudly on a non-zero
    exit or a missing 'normal termination'."""
    work = tempfile.mkdtemp(prefix="xtb_")
    write_xyz(os.path.join(work, "in.xyz"), symbols, geom_bohr)
    env = {**os.environ, "OMP_STACKSIZE": os.environ.get("OMP_STACKSIZE", "1G")}
    with open(os.path.join(work, "xtb.log"), "w", encoding="utf-8") as log:
        rc = subprocess.run([XTB, "in.xyz", "--gfn", "2", "--acc", ACC, *flags], cwd=work, stdout=log, stderr=subprocess.STDOUT, env=env,
                            check=False).returncode
    with open(os.path.join(work, "xtb.log"), encoding="utf-8", errors="replace") as fh:
        ok = "normal termination of xtb" in fh.read()
    if rc != 0 or not ok:
        raise RuntimeError(f"xtb {' '.join(flags)} failed (rc {rc}) — see {work}/xtb.log")
    return work


def total_energy(work):
    with open(os.path.join(work, "xtb.log"), encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "TOTAL ENERGY" in line:
                return float(line.split()[3])
    raise RuntimeError(f"no TOTAL ENERGY in {work}/xtb.log")


def optimise(reference, stub):
    """The xtb minimum (--opt extreme) from the reference record's geometry, written as a stub record."""
    with open(reference, encoding="utf-8") as fh:
        ref = json.load(fh)
    sym = ref["molecule"]["symbols"]
    work = run_xtb(sym, ref["molecule"]["geometry"], ["--opt", "extreme"])
    sym2, geom = read_xyz(os.path.join(work, "xtbopt.xyz"))
    if sym2 != sym:
        raise RuntimeError("xtb reordered the atoms")
    os.makedirs(os.path.dirname(stub) or ".", exist_ok=True)
    with open(stub, "w", encoding="utf-8") as fh:
        json.dump({"driver": "hessian", "molecule": {"symbols": sym, "geometry": geom.reshape(-1).tolist()}}, fh)


def hessians(stub_dir, out_dir):
    """The xtb Hessian at every stub of stub_dir, as records in out_dir; one progress line per Hessian."""
    os.makedirs(out_dir, exist_ok=True)
    stubs = sorted(glob.glob(os.path.join(stub_dir, "*.json")))
    todo = [s for s in stubs if not os.path.exists(os.path.join(out_dir, os.path.basename(s)))]
    t_all = time.time()
    for k, path in enumerate(todo, 1):
        t0 = time.time()
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        sym = d["molecule"]["symbols"]
        work = run_xtb(sym, d["molecule"]["geometry"], ["--hess"])
        H = read_hessian(os.path.join(work, "hessian"), len(sym))
        rec = {"driver": "hessian", "model": {"method": "GFN2-xTB", "basis": "xtb 6.7.1", "acc": ACC},
               "molecule": {"symbols": sym, "geometry": d["molecule"]["geometry"]},
               "return_result": H.reshape(-1).tolist(), "properties": {"return_energy": total_energy(work)}}
        tmp = os.path.join(out_dir, os.path.basename(path) + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rec, fh)
        os.replace(tmp, os.path.join(out_dir, os.path.basename(path)))
        print(f"[{time.strftime('%H:%M:%S')}] {k}/{len(todo)} {os.path.basename(path)} in {time.time() - t0:.1f} s", flush=True)
    print(f"done: {len(todo)} Hessians in {(time.time() - t_all) / 60:.1f} min", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("opt")
    o.add_argument("reference")
    o.add_argument("stub")
    h = sub.add_parser("hess")
    h.add_argument("stub_dir")
    h.add_argument("out_dir")
    a = ap.parse_args()
    if a.cmd == "opt":
        optimise(a.reference, a.stub)
    else:
        hessians(a.stub_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
