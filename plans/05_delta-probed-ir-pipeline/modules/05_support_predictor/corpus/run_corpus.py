#!/usr/bin/env python
"""The Module 05 corpus queue runner (Windows Python). Picks pending molecules from manifest.csv in priority order, builds a
3-D start geometry (RDKit ETKDG + MMFF), runs psi4_worker.py in the conda env `qc`, stores results atomically, updates the
manifest and appends the ledger. Start and stop at will.
    python run_corpus.py [--layer A|B|C] [--max-molecules N] [--max-hours H] [--force] [--dry-run] [--grid-check]
Refuses to start while a plan-05 anchor job runs in WSL (unless --force); one runner at a time (corpus.lock); a progress line
at least hourly; results in molecules/<id>/ (git-ignored)."""
import argparse, csv, hashlib, json, os, shutil, socket, subprocess, sys, time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST, LEDGER, LOCK = HERE / "manifest.csv", HERE / "ledger.csv", HERE / "corpus.lock"
DECK = HERE / "decks" / "deck_v1.json"
QC_PYTHON = Path(r"C:\Users\thebr\.conda\envs\qc\python.exe")
QM9_VAC = HERE.parent / "data" / "hessian_qm9" / "hessian_qm9_DatasetDict" / "vacuum"
FIELDS = ["id", "layer", "priority", "name", "smiles", "qm9_label", "n_heavy", "n_atoms", "status", "machine", "deck", "note"]
LEDGER_FIELDS = ["id", "layer", "name", "machine", "deck", "start", "end", "seconds_total", "seconds_optimise", "seconds_hessian_b3lyp", "seconds_hessian_wb97x", "peak_rss_gb", "status", "note"]


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def anchor_job_running():
    try:
        r = subprocess.run(["wsl", "-e", "bash", "-lc", "pgrep -af 'm1_frozen|anchor_single|dryrun_dft|naphthalene_geometry' | grep -v pgrep | wc -l"], capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip() or 0) > 0
    except Exception:
        return False


def read_manifest():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def queue_order(rows):
    """Run order (DESIGN, dated addition 2026-09-12): layer A first (timing-test rows at the front), then layers B and A2
    alternating by their position inside each layer (class axis and size axis grow together), then layer C.
    Inside a layer the position is the hashed priority order of the manifest."""
    pos = {}
    for L in ("A", "A2", "B", "C"):
        for i, r in enumerate(sorted([r for r in rows if r["layer"] == L], key=lambda r: (0 if r.get("note") == "timing-test" else 1, r["priority"]))):
            pos[r["id"]] = i
    def key(r):
        if r["layer"] == "A": return (0, pos[r["id"]], 0)
        if r["layer"] in ("B", "A2"): return (1, pos[r["id"]], 0 if r["layer"] == "B" else 1)
        return (2, pos[r["id"]], 0)
    return sorted(rows, key=key)


def write_manifest(rows):
    tmp = MANIFEST.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); [w.writerow({k: r.get(k, "") for k in FIELDS}) for r in rows]
    os.replace(tmp, MANIFEST)


def append_ledger(rec):
    new = not LEDGER.exists()
    with open(LEDGER, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if new: w.writeheader()
        w.writerow({k: rec.get(k, "") for k in LEDGER_FIELDS})


def start_geometry(row):
    """Layers A/B: RDKit ETKDG + MMFF from SMILES. Layer C: the Hessian QM9 geometry (Angstrom) by label."""
    if row["layer"] == "C":
        import pyarrow as pa, pyarrow.ipc as ipc, numpy as np
        for s in sorted(QM9_VAC.glob("data-*.arrow")):
            tab = ipc.open_stream(pa.memory_map(str(s))).read_all()
            labs = tab.column("label").to_pylist()
            if row["qm9_label"] in labs:
                i = labs.index(row["qm9_label"]); r = tab.slice(i, 1).to_pylist()[0]
                sym = {1: "H", 6: "C", 7: "N", 8: "O", 9: "F"}
                return [[sym[z], *xyz] for z, xyz in zip(r["atomic_numbers"], r["positions"])], False
        raise RuntimeError("label not found in Hessian QM9 vacuum split")
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.AddHs(Chem.MolFromSmiles(row["smiles"]))
    if AllChem.EmbedMolecule(m, randomSeed=0) != 0:
        AllChem.EmbedMolecule(m, randomSeed=0, useRandomCoords=True)
    AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
    conf = m.GetConformer()
    return [[a.GetSymbol(), *conf.GetAtomPosition(a.GetIdx())] for a in m.GetAtoms()], True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", default=None); ap.add_argument("--max-molecules", type=int, default=None); ap.add_argument("--max-hours", type=float, default=None)
    ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--grid-check", action="store_true", help="timing test: repeat the B3LYP Hessian on the finer grid")
    a = ap.parse_args()
    deck = json.load(open(DECK)); deck_hash = hashlib.sha256(DECK.read_bytes()).hexdigest()[:12]
    machine = socket.gethostname()
    if LOCK.exists():
        log(f"another runner holds {LOCK} (started {LOCK.read_text().strip()}); exiting"); return 2
    if anchor_job_running() and not a.force:
        log("a plan-05 anchor job is running in WSL; refusing to start (use --force to override, it will be noted in the ledger)"); return 3
    if not QC_PYTHON.exists():
        log(f"psi4 environment not found at {QC_PYTHON}"); return 4
    LOCK.write_text(f"{machine} {datetime.now():%Y-%m-%d %H:%M}")
    t_start = time.time(); done = 0; last_report = time.time(); virtually_done = set()
    try:
        while True:
            rows = read_manifest()
            # crash recovery: running rows without a complete result folder go back to pending
            for r in rows:
                if r["status"] == "running" and not (HERE / "molecules" / r["id"] / "result.json").exists():
                    r["status"] = "pending"; r["note"] = (r.get("note", "") + " redone-after-crash").strip()
            todo = [r for r in queue_order(rows) if r["status"] == "pending" and r["id"] not in virtually_done and (a.layer is None or r["layer"] == a.layer)]
            if not todo:
                log("nothing pending; done"); break
            if a.max_molecules is not None and done >= a.max_molecules:
                log(f"reached --max-molecules {a.max_molecules}"); break
            if a.max_hours is not None and (time.time() - t_start) / 3600 >= a.max_hours:
                log(f"reached --max-hours {a.max_hours}"); break
            r = todo[0]
            if a.dry_run:
                log(f"would run {r['id']} {r['layer']} {r['name']} ({r['n_atoms']} atoms)"); done += 1; virtually_done.add(r["id"])
                if a.max_molecules and done >= a.max_molecules: break
                continue
            r["status"] = "running"; r["machine"] = machine; r["deck"] = deck_hash; write_manifest(rows)
            out_final = HERE / "molecules" / r["id"]; out_tmp = HERE / "molecules" / (r["id"] + ".tmp")
            shutil.rmtree(out_tmp, ignore_errors=True); out_tmp.mkdir(parents=True)
            t0 = datetime.now(); log(f"start {r['id']} {r['layer']} {r['name']} ({r['n_atoms']} atoms)")
            status = "failed"; res = {}
            try:
                xyz, optimise = start_geometry(r)
                job = {"id": r["id"], "layer": r["layer"], "xyz_angstrom": xyz, "deck": deck, "out_dir": str(out_tmp), "optimise": optimise, "grid_check": a.grid_check}
                jp = out_tmp / "job.json"; json.dump(job, open(jp, "w"))
                p = subprocess.run([str(QC_PYTHON), str(HERE / "psi4_worker.py"), str(jp)], capture_output=True, text=True)
                (out_tmp / "worker_stdout.txt").write_text(p.stdout + "\n---stderr---\n" + p.stderr)
                if (out_tmp / "result.json").exists():
                    res = json.load(open(out_tmp / "result.json")); status = res.get("status", "failed")
            except Exception as e:
                (out_tmp / "runner_error.txt").write_text(repr(e))
            shutil.rmtree(out_final, ignore_errors=True); os.replace(out_tmp, out_final)
            rows = read_manifest()
            for rr in rows:
                if rr["id"] == r["id"]:
                    rr["status"] = status; rr["machine"] = machine; rr["deck"] = deck_hash
                    if a.force: rr["note"] = (rr.get("note", "") + " forced-beside-anchor-job").strip()
            write_manifest(rows)
            tm = res.get("timings_s", {})
            append_ledger(dict(id=r["id"], layer=r["layer"], name=r["name"], machine=machine, deck=deck_hash, start=f"{t0:%Y-%m-%d %H:%M:%S}", end=f"{datetime.now():%Y-%m-%d %H:%M:%S}",
                               seconds_total=tm.get("total", ""), seconds_optimise=tm.get("optimise", ""), seconds_hessian_b3lyp=tm.get("hessian_b3lyp", ""), seconds_hessian_wb97x=tm.get("hessian_wb97x", ""),
                               peak_rss_gb=res.get("peak_rss_gb", ""), status=status, note="forced" if a.force else ""))
            done += 1
            log(f"{status} {r['id']} in {tm.get('total', '?')} s (opt {tm.get('optimise', '-')}, B3LYP {tm.get('hessian_b3lyp', '-')}, wB97X {tm.get('hessian_wb97x', '-')})")
            if time.time() - last_report > 3600 or True:
                left = len(todo) - 1; last_report = time.time()
                log(f"progress: {done} this session, {left} pending in scope, {(time.time() - t_start) / 3600:.2f} h elapsed")
    finally:
        LOCK.unlink(missing_ok=True)
    subprocess.run([sys.executable, str(HERE / "status.py")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
