#!/usr/bin/env python
"""The Module 05 corpus queue runner (Windows Python). Picks pending molecules from manifest.csv in priority order, builds a
3-D start geometry (RDKit ETKDG + MMFF), runs psi4_worker.py in the conda env `qc`, stores results atomically, updates the
manifest and appends the ledger. Start and stop at will.
    python run_corpus.py [--layer A|B|C] [--max-molecules N] [--max-hours H] [--force] [--dry-run] [--grid-check]
Refuses to start while a plan-05 anchor job runs in WSL (unless --force); one runner at a time (corpus.lock); a progress line
at least hourly; results in molecules/<id>/ (git-ignored)."""
import argparse
import csv
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST, LEDGER, LOCK = HERE / "manifest.csv", HERE / "ledger.csv", HERE / "corpus.lock"
DECK = HERE / "decks" / "deck_v1.json"
CATION_DECK = HERE / "decks" / "deck_v1_cation.json"     # pool 3 (decision 54, 3 Oct 2026): layer P3c rows run UKS, charge 1, doublet
CATION_DISTORT_ANG = 0.01                                # the seeded Cartesian distortion of cation_rows.py (a Jahn–Teller minimum must be reachable in c1)
_CATION_DECK: dict = {}
QC_PYTHON = Path(os.environ["CORPUS_QC_PYTHON"]) if os.environ.get("CORPUS_QC_PYTHON") else None   # 28 Sep 2026: no personal default path  # 2026-09-18: overridable so the same runner works on a Linux host (Hetzner CPX62)
QM9_VAC = HERE.parent / "data" / "hessian_qm9" / "hessian_qm9_DatasetDict" / "vacuum"
FIELDS = ["id", "layer", "priority", "name", "smiles", "qm9_label", "n_heavy", "n_atoms", "status", "machine", "deck", "note"]
RETRY_OPT_OPTIONS = {"opt_coordinates": "cartesian", "geom_maxiter": 200}  # 2026-09-20: --retry-failed; near-linear bends (ethynyl) stall optking's internals
LEDGER_FIELDS = ["id", "layer", "name", "machine", "deck", "start", "end", "seconds_total", "seconds_optimise", "seconds_hessian_b3lyp", "seconds_hessian_wb97x", "peak_rss_gb", "status", "note"]


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def opt_options_for(row, retry_failed=False):
    """Cartesian optimisation coordinates (RETRY_OPT_OPTIONS) for a retry and, since 30 Sep 2026, from the start for any molecule with a triple
    bond: optking's internal coordinates stall on the near-linear bend (B_4a601408a5, naphthalene+COOH+ethynyl, five hours without a line)."""
    if retry_failed or "#" in (row.get("smiles") or ""):
        return dict(RETRY_OPT_OPTIONS)
    return None


def dump_stack(pid, path):
    """Python stack of a running worker through py-spy (`py-spy dump --pid`, twice a minute apart, main process and subprocesses) into `path`; writes
    a one-line note when py-spy is not installed or cannot attach. Evidence for the upstream report of a stall (30 Sep 2026)."""
    spy = shutil.which("py-spy") or str(Path(sys.executable).with_name("py-spy"))
    if not Path(spy).exists():
        Path(path).write_text("py-spy not installed in this environment; no stack captured\n")
        return False
    lines = []
    for i in range(2):
        r = subprocess.run([spy, "dump", "--pid", str(pid), "--subprocesses", "--nonblocking"], capture_output=True, text=True, check=False, timeout=120)
        lines.append(f"=== py-spy dump {i + 1} at {datetime.now():%Y-%m-%d %H:%M:%S} (exit {r.returncode})\n{r.stdout}{r.stderr}")
        if i == 0:
            time.sleep(60)
    Path(path).write_text("\n".join(lines))
    return True


def run_worker(cmd, work_dir, stall_s=5400.0, max_s=8 * 3600.0, poll_s=30.0, dump=True):
    """Run the psi4 worker under a stall guard. Returns (stdout, stderr, guard) with guard None when the worker ended by itself, 'stalled' when no
    file in work_dir changed for stall_s seconds, 'timeout' when max_s elapsed; in both guard cases the stack is dumped (dump_stack, unless
    dump=False) and the worker is terminated (then killed)."""
    work_dir = Path(work_dir)
    out_f, err_f = work_dir / "worker_stdout.raw", work_dir / "worker_stderr.raw"
    with open(out_f, "w") as fo, open(err_f, "w") as fe:
        p = subprocess.Popen(cmd, stdout=fo, stderr=fe, text=True)
        t0 = time.time(); guard = None
        while True:
            try:
                p.wait(timeout=poll_s)
                break
            except subprocess.TimeoutExpired:
                pass
            now = time.time()
            newest = max((f.stat().st_mtime for f in work_dir.iterdir() if f.is_file()), default=t0)
            if now - max(newest, t0) > stall_s:
                guard = "stalled"
            elif now - t0 > max_s:
                guard = "timeout"
            if guard:
                if dump:
                    try:
                        dump_stack(p.pid, work_dir / "stall_stack.txt")
                    except Exception as e:  # noqa: BLE001 — the dump is evidence, never a reason to keep a stalled worker alive
                        (work_dir / "stall_stack.txt").write_text(f"stack dump failed: {e!r}\n")
                p.terminate()
                try:
                    p.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    p.kill(); p.wait()
                break
    stdout, stderr = out_f.read_text(errors="replace"), err_f.read_text(errors="replace")
    out_f.unlink(missing_ok=True); err_f.unlink(missing_ok=True)
    return stdout, stderr, guard


def anchor_job_running():
    try:
        r = subprocess.run(["wsl", "-e", "bash", "-lc", "pgrep -af 'm1_frozen|anchor_single|dryrun_dft|naphthalene_geometry' | grep -v pgrep | wc -l"], capture_output=True, text=True, check=False, timeout=30)
        return int(r.stdout.strip() or 0) > 0
    except (OSError, subprocess.SubprocessError, ValueError):
        return False


def read_manifest():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def queue_order(rows):
    """Run order (DESIGN, dated addition 2026-09-12): layer A first (timing-test rows at the front), then layers B and A2
    alternating by their position inside each layer (class axis and size axis grow together), then pool 3 (P3c and P3 alternating, 3 Oct 2026), then layer C.
    Inside a layer the position is the hashed priority order of the manifest."""
    pos = {}
    for L in ("A", "A2", "B", "P3", "P3c", "C"):
        # startswith, not ==: a crash-recovered timing-test row ("timing-test redone-after-crash") keeps its front position
        # (bug found 2026-09-14 12:5x: naphthalene was skipped for diphenylacetylene; the first fix of 12:5x broke the line with an inline comment, repaired 15:2x)
        for i, r in enumerate(sorted([r for r in rows if r["layer"] == L], key=lambda r: (0 if r.get("note", "").startswith("timing-test") else 1, r["priority"]))):
            pos[r["id"]] = i
    def key(r):
        if r["layer"] == "A": return (0, pos[r["id"]], 0)
        if r["layer"] in ("B", "A2"): return (1, pos[r["id"]], 0 if r["layer"] == "B" else 1)
        if r["layer"] in ("P3c", "P3"): return (2, pos[r["id"]], 0 if r["layer"] == "P3c" else 1)   # pool 3 (decision 54): cations and neutrals alternating, after A2/B, before C
        return (3, pos[r["id"]], 0)
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


def cation_parent(row):
    """The neutral parent id a P3c row names in its note (`parent <id>`, written by probes/pool3_candidates.py)."""
    import re
    m = re.search(r"parent (\S+?)(?:;|$)", row.get("note", ""))
    if not m:
        raise ValueError(f"{row.get('id')}: a P3c row needs 'parent <id>' in its note")
    return m.group(1)


def parent_geometry_path(row):
    p = HERE / "molecules" / cation_parent(row) / "geometry.json"
    if not p.exists():
        raise RuntimeError(f"{row.get('id')}: the neutral parent {cation_parent(row)} has no geometry.json under molecules/ — compute or merge it first")
    return p


def deck_for(row, base, overrides):
    """(deck, hash) for a manifest row: layer P3c runs the cation deck (loaded once, the thread/memory overrides applied, the hash of the file on disk);
    every other layer the base deck."""
    if row.get("layer") != "P3c":
        return base
    if "deck" not in _CATION_DECK:
        d = json.load(open(CATION_DECK)); d.update(overrides)
        _CATION_DECK.update(deck=d, hash=hashlib.sha256(CATION_DECK.read_bytes()).hexdigest()[:12])
    return _CATION_DECK["deck"], _CATION_DECK["hash"]


def start_geometry(row):
    """Layers A/B: RDKit ETKDG + MMFF from SMILES. Layer C: the Hessian QM9 geometry (Angstrom) by label."""
    if row.get("restart_geometry"):  # --restart-from (2026-09-24): twisted geometry from saddle_restarts.py, bohr -> Angstrom, then optimise as usual
        g = json.load(open(row["restart_geometry"], encoding="utf-8")); b = 0.529177210903
        return [[s, x * b, y * b, z * b] for s, (x, y, z) in zip(g["symbols"], g["coords_bohr"], strict=True)], True
    if row["layer"] == "P3c":  # pool 3 cations (decision 54): the neutral parent's optimised geometry (bohr → Å) with the seeded distortion, then UKS optimisation
        import numpy as np
        g = json.load(open(parent_geometry_path(row), encoding="utf-8")); b = 0.529177210903
        xyz = np.asarray(g["coords_bohr"], float) * b + np.random.default_rng(0).normal(0.0, CATION_DISTORT_ANG, (len(g["symbols"]), 3))
        return [[s, *map(float, r)] for s, r in zip(g["symbols"], xyz, strict=True)], True
    if row["layer"] == "C":
        import pyarrow as pa
        import pyarrow.ipc as ipc
        for s in sorted(QM9_VAC.glob("data-*.arrow")):
            tab = ipc.open_stream(pa.memory_map(str(s))).read_all()
            labs = tab.column("label").to_pylist()
            if row["qm9_label"] in labs:
                i = labs.index(row["qm9_label"]); r = tab.slice(i, 1).to_pylist()[0]
                sym = {1: "H", 6: "C", 7: "N", 8: "O", 9: "F"}
                return [[sym[z], *xyz] for z, xyz in zip(r["atomic_numbers"], r["positions"], strict=True)], False
        raise RuntimeError("label not found in Hessian QM9 vacuum split")
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.AddHs(Chem.MolFromSmiles(row["smiles"]))
    if AllChem.EmbedMolecule(m, randomSeed=0) != 0:
        AllChem.EmbedMolecule(m, randomSeed=0, useRandomCoords=True)
    AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
    conf = m.GetConformer()
    return [[a.GetSymbol(), *conf.GetAtomPosition(a.GetIdx())] for a in m.GetAtoms()], True


def restart_rows(path, rows):
    """--restart-from <restart_jobs_<date>.json> (saddle_restarts.py, 24 September 2026): two pseudo-rows per saddle-point molecule, <id>_r+ and
    <id>_r-, starting from the geometries displaced along the imaginary mode. The manifest is never touched; the results go to molecules/<id>_r+
    and molecules/<id>_r- (the original directory stays), and the corpus ledger gets one record per restart with the displacement in the note.
    build_release.py skips *_r+ / *_r- directories unless asked (the keep-one-of-two rule is a decision after the re-optimisation)."""
    by_id = {r["id"]: r for r in rows}; out = []
    for j in json.load(open(path, encoding="utf-8")):
        base = by_id[j["id"]]
        for sign, f in zip(("+", "-"), j["files"], strict=True):
            g = json.load(open(HERE / f, encoding="utf-8")); rf = g["restart_from"]; amp = abs(rf["displacement_angstrom"])
            out.append({**base, "id": f"{j['id']}_r{sign}", "name": f"{base['name']} (restart {sign}{amp} A)", "n_atoms": str(len(g["symbols"])),
                        "restart_geometry": str(HERE / f), "restart_note": f"restart-from:{Path(path).name} {sign}{amp}A along {rf['functional']} imaginary {rf['imaginary_cm']}cm-1"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", default=None); ap.add_argument("--max-molecules", type=int, default=None); ap.add_argument("--max-hours", type=float, default=None)
    ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--grid-check", action="store_true", help="timing test: repeat the B3LYP Hessian on the finer grid")
    ap.add_argument("--threads", type=int, default=None, help="override the deck's thread count for this runner only (2026-09-18; the deck file and its hash are unchanged; noted in the ledger)")
    ap.add_argument("--memory-gb", type=int, default=None, help="override the deck's psi4 memory for this runner only (2026-09-18; noted in the ledger)")
    ap.add_argument("--shard", default=None, help="i/K: this runner takes only the pending rows whose id hashes to shard i of K (2026-09-19; several rented machines share one layer without collisions; manifests are merged afterwards by merge_shards.py)")
    ap.add_argument("--retry-failed", action="store_true", help="take the rows with status failed (within --layer/--shard) once more, with opt_coordinates cartesian and geom_maxiter 200; the result folder is replaced (2026-09-20: E6 acenaphthylene+ethynyl, optking 50 steps)")
    ap.add_argument("--stall-min", type=float, default=90.0, help="stall guard (30 Sep 2026): terminate the psi4 worker when no file in the molecule's work dir changed for this many minutes (B_4a601408a5 sat five hours in optking)")
    ap.add_argument("--worker-max-hours", type=float, default=8.0, help="stall guard: terminate the psi4 worker after this many hours regardless (layer B takes ≈ 1.5 h per molecule on a CPX62)")
    ap.add_argument("--restart-from", default=None, help="restart_jobs_<date>.json from saddle_restarts.py: run <id>_r+ and <id>_r- from the twisted geometries; manifest untouched (2026-09-24)")
    ap.add_argument("--ids", default=None, help="comma-separated manifest ids to (re)run regardless of status; the result folder is replaced (2026-09-15: benzene grid rerun with per-mode frequencies)")
    a = ap.parse_args()
    deck = json.load(open(DECK)); deck_hash = hashlib.sha256(DECK.read_bytes()).hexdigest()[:12]
    machine = socket.gethostname()
    overrides = {k: v for k, v in (("threads", a.threads), ("memory_gb", a.memory_gb)) if v is not None}
    deck.update(overrides)  # the in-memory job deck; DECK on disk and deck_hash are untouched
    override_note = " ".join(f"{k}={v}" for k, v in overrides.items())
    if LOCK.exists():
        held = LOCK.read_text().strip(); parts = held.split()
        stale = False
        if len(parts) >= 4 and parts[-2] == "pid" and parts[0] == machine:          # 25 Sep 2026 (hel1-16 handover): a lock from a dead runner on this host is stale
            try: os.kill(int(parts[-1]), 0)
            except OSError: stale = True
        if stale:
            log(f"stale {LOCK.name} from a dead runner on this host ({held}); removed"); LOCK.unlink(missing_ok=True)
        else:
            log(f"another runner holds {LOCK} (started {held}); exiting"); return 2
    if anchor_job_running() and not a.force:
        log("a plan-05 anchor job is running in WSL; refusing to start (use --force to override, it will be noted in the ledger)"); return 3
    if QC_PYTHON is None or not QC_PYTHON.exists():
        log(f"psi4 environment not found ({QC_PYTHON}); set CORPUS_QC_PYTHON to the python of the psi4 environment"); return 4
    LOCK.write_text(f"{machine} {datetime.now():%Y-%m-%d %H:%M} pid {os.getpid()}")
    t_start = time.time(); done = 0; last_report = time.time(); virtually_done = set()
    try:
        while True:
            rows = read_manifest()
            # crash recovery: running rows without a complete result folder go back to pending
            for r in rows:
                if r["status"] == "running" and not (HERE / "molecules" / r["id"] / "result.json").exists():
                    r["status"] = "pending"; r["note"] = (r.get("note", "") + " redone-after-crash").strip()
            if a.restart_from:
                todo = [r for r in restart_rows(a.restart_from, rows) if r["id"] not in virtually_done and not (HERE / "molecules" / r["id"] / "result.json").exists()]
            elif a.ids:
                # every named id runs once: it is added to virtually_done below whether it is dry-run or run
                # (2026-09-15 17:20: without this the runner restarted benzene as soon as it had finished it)
                wanted = set(a.ids.split(","))
                todo = [r for r in rows if r["id"] in wanted and r["id"] not in virtually_done]
            else:
                want_status = "failed" if a.retry_failed else "pending"
                todo = [r for r in queue_order(rows) if r["status"] == want_status and r["id"] not in virtually_done and (a.layer is None or r["layer"] == a.layer) and (a.shard is None or int(hashlib.sha1(r["id"].encode()).hexdigest(), 16) % int(a.shard.split("/")[1]) == int(a.shard.split("/")[0]))]
            if not todo:
                log("nothing pending; done"); break
            if a.max_molecules is not None and done >= a.max_molecules:
                log(f"reached --max-molecules {a.max_molecules}"); break
            if a.max_hours is not None and (time.time() - t_start) / 3600 >= a.max_hours:
                log(f"reached --max-hours {a.max_hours}"); break
            r = todo[0]
            if a.ids or a.retry_failed or a.restart_from:  # a retried molecule that fails again must not be picked up in the next loop
                virtually_done.add(r["id"])
            if a.dry_run:
                log(f"would run {r['id']} {r['layer']} {r['name']} ({r['n_atoms']} atoms)"); done += 1; virtually_done.add(r["id"])
                if a.max_molecules and done >= a.max_molecules: break
                continue
            row_deck, row_hash = deck_for(r, (deck, deck_hash), overrides)               # P3c rows: the cation deck and its own hash
            if not a.restart_from: r["status"] = "running"; r["machine"] = machine; r["deck"] = row_hash; write_manifest(rows)
            out_final = HERE / "molecules" / r["id"]; out_tmp = HERE / "molecules" / (r["id"] + ".tmp")
            shutil.rmtree(out_tmp, ignore_errors=True); out_tmp.mkdir(parents=True)
            t0 = datetime.now(); log(f"start {r['id']} {r['layer']} {r['name']} ({r['n_atoms']} atoms)")
            status = "failed"; res = {}; guard = None; opts = None
            try:
                xyz, optimise = start_geometry(r)
                job = {"id": r["id"], "layer": r["layer"], "xyz_angstrom": xyz, "deck": row_deck, "out_dir": str(out_tmp), "optimise": optimise, "grid_check": a.grid_check}
                opts = opt_options_for(r, a.retry_failed)
                if opts: job["opt_options"] = opts
                jp = out_tmp / "job.json"; json.dump(job, open(jp, "w"))
                p_out, p_err, guard = run_worker([str(QC_PYTHON), str(HERE / "psi4_worker.py"), str(jp)], out_tmp,
                                                 stall_s=a.stall_min * 60.0, max_s=a.worker_max_hours * 3600.0)   # result.json decides; the guard only ends a stall
                (out_tmp / "worker_stdout.txt").write_text(p_out + "\n---stderr---\n" + p_err)
                if guard:
                    log(f"GUARD {guard}: {r['id']} terminated after {(datetime.now() - t0).total_seconds():.0f} s (no file change for {a.stall_min} min or beyond {a.worker_max_hours} h)")
                if (out_tmp / "result.json").exists():
                    res = json.load(open(out_tmp / "result.json")); status = res.get("status", "failed")
            except Exception as e:  # noqa: BLE001 — the corpus runner records any failure of one molecule and continues with the next
                (out_tmp / "runner_error.txt").write_text(repr(e))
            shutil.rmtree(out_final, ignore_errors=True); os.replace(out_tmp, out_final)
            if not a.restart_from:
                rows = read_manifest()
                for rr in rows:
                    if rr["id"] == r["id"]:
                        rr["status"] = status; rr["machine"] = machine; rr["deck"] = row_hash
                        if a.force: rr["note"] = (rr.get("note", "") + " forced-beside-anchor-job").strip()
                write_manifest(rows)
            tm = res.get("timings_s", {})
            append_ledger(dict(id=r["id"], layer=r["layer"], name=r["name"], machine=machine, deck=row_hash, start=f"{t0:%Y-%m-%d %H:%M:%S}", end=f"{datetime.now():%Y-%m-%d %H:%M:%S}",
                               seconds_total=tm.get("total", ""), seconds_optimise=tm.get("optimise", ""), seconds_hessian_b3lyp=tm.get("hessian_b3lyp", ""), seconds_hessian_wb97x=tm.get("hessian_wb97x", ""),
                               peak_rss_gb=res.get("peak_rss_gb", ""), status=status, note=" ".join(x for x in (("forced" if a.force else ""), ("retry:" + ",".join(f"{k}={v}" for k, v in RETRY_OPT_OPTIONS.items()) if a.retry_failed else ("linear-bend:cartesian" if opts else "")), (guard or ""), override_note, r.get("restart_note", "")) if x)))
            done += 1
            log(f"{status} {r['id']} in {tm.get('total', '?')} s (opt {tm.get('optimise', '-')}, B3LYP {tm.get('hessian_b3lyp', '-')}, wB97X {tm.get('hessian_wb97x', '-')})")
            if time.time() - last_report > 3600 or True:
                left = len(todo) - 1; last_report = time.time()
                log(f"progress: {done} this session, {left} pending in scope, {(time.time() - t_start) / 3600:.2f} h elapsed")
    finally:
        LOCK.unlink(missing_ok=True)
    subprocess.run([sys.executable, str(HERE / "status.py")], check=False)   # the digest is informational
    return 0


if __name__ == "__main__":
    sys.exit(main())
