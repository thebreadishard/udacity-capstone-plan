"""The anchor release for paper D (decision 56, 3 Oct 2026): every VALID coupled-cluster anchor directory packed into one versioned archive with a manifest
(SHA-256 and size per file, the validation numbers parsed from each run log, the git commit of the repository), ready for the Zenodo deposit. The
counterpart of `modules/05_support_predictor/m05/build_release.py` for the corpus. Mechanical: nothing in the manifest is typed by hand.

    python tools/build_anchor_release.py anchors_2026-10-03          # writes data/anchor_release/anchors_2026-10-03.tar.gz, _manifest.json and README.md
    python tools/build_anchor_release.py anchors_2026-10-03 --check  # exit 1 if the archive's files no longer match the manifest (sha256)

Only run directories whose `e8_fd.log` says "Hessian written (VALID)" enter; psi4/pyscf scratch never does (there is none in these directories).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import time
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
RESULTS = PLAN / "probes" / "results_m1"
OUT = PLAN / "modules" / "05_support_predictor" / "data" / "anchor_release"
# label → (run directory, molecule, corpus id); the same list as the data paper's make_paper.py
ANCHORS = [
    ("benzene", "e8_benzene_ccpvdz_dip_2026-10-03", "benzene", "A_8448043181"),
    ("fluorobenzene", "e8_fluorobenzene_ccpvdz_2026-09-30", "fluorobenzene", "B_8b12a55d3a"),
    ("pyridine", "e8_pyridine_ccpvdz_2026-09-30", "pyridine", "A_6e858b26e5"),
    ("naphthalene", "e8_naphthalene_ccpvdz_tlambda_2026-10-02", "naphthalene", "A_01f3186607"),
    ("anthracene", "e8_anthracene_ccpvdz_2026-10-05", "anthracene", "A_a1e6ec1862"),
    ("benzene_cation", "e8_benzene_cation_ccpvdz_2026-10-05", "benzene radical cation", "C_benzene"),
]
HEAD = re.compile(r"E8 FD Hessian: (\d+) atoms, (\S+), frozen (\d+) .*?step ([0-9.]+) bohr, (\d+) displacements")
VALID = re.compile(r"Hessian written \(VALID\); FD asymmetry max ([0-9.e+-]+) a\.u\.")
ROUTES = re.compile(r"translational sum rule ([0-9.e+-]+) E_h/bohr².*?energy route max \|H_kk − d²E/dx_k²\| ([0-9.e+-]+) E_h/")
EXCLUDE = {".tmp", ".pid"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validation(rundir: Path) -> dict | None:
    log = rundir / "e8_fd.log"
    if not log.exists():
        return None
    text = log.read_text(encoding="utf-8", errors="replace")
    heads, valid, routes = HEAD.findall(text), VALID.findall(text), ROUTES.findall(text)
    if not (heads and valid and routes and (rundir / "hessian_ccsd_t.npz").exists()):
        return None
    atoms, basis, frozen, step, ndisp = heads[-1]
    return {"atoms": int(atoms), "basis": basis, "frozen_core": int(frozen), "step_bohr": float(step), "displacements": int(ndisp),
            "fd_asymmetry_au": float(valid[-1]), "translational_sum_rule_au": float(routes[-1][0]), "energy_route_max_au": float(routes[-1][1])}


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=str(PLAN), check=False).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def collect(results: Path = RESULTS) -> tuple[list[dict], list[str]]:
    entries, left_out = [], []
    for label, rundir, molecule, corpus_id in ANCHORS:
        d = results / rundir
        v = validation(d)
        if v is None:
            left_out.append(f"{label} ({rundir}: {'no directory' if not d.exists() else 'no VALID Hessian'})")
            continue
        files = []
        for p in sorted(d.rglob("*")):
            if p.is_file() and p.suffix not in EXCLUDE:
                files.append({"path": f"{label}/{p.relative_to(d).as_posix()}", "bytes": p.stat().st_size, "sha256": sha256(p)})
        entries.append({"label": label, "molecule": molecule, "corpus_id": corpus_id, "run_dir": rundir, "level": f"CCSD(T)/{v['basis']}", **v, "files": files})
    return entries, left_out


def readme(name: str, entries: list[dict]) -> str:
    rows = "\n".join(f"| {e['molecule']} | {e['atoms']} | {e['frozen_core']} | {e['displacements']} | {e['fd_asymmetry_au']:.1e} | {e['translational_sum_rule_au']:.1e} | {e['energy_route_max_au']:.1e} |" for e in entries)
    return f"""# {name} — coupled-cluster anchors (plan 05)

CCSD(T)/cc-pVDZ Cartesian Hessians of aromatic molecules by central finite differences (step as listed) of analytic gradients with the triples
lambda equations solved explicitly, at the B3LYP/6-31G* geometry of the corpus row. One directory per molecule:

- `hessian_ccsd_t.npz` — `H_raw`, `H_projected` (translations/rotations projected out; hartree/bohr²), `freq_cm`; `apt_ccsd_t.npz` (dipole derivatives) where computed;
- `reference.npz` — energy, gradient, coordinates (bohr), charge, spin at the reference geometry;
- `grad_<k>_<sign>.npy`, `ener_<k>_<sign>.npy`, `dip_<k>_<sign>.npy` — gradient, energy and dipole at displacement k, ±;
- `e8_fd.log`, `run.log`, `chain.log`, `partial_*.log` — the run record with the checks; `two_route_check.*` where the check ran separately.

| molecule | atoms | frozen core | gradients | FD asymmetry (a.u.) | sum rule (E_h/a0²) | energy route (E_h/a0²) |
|---|---|---|---|---|---|---|
{rows}

The manifest beside the archive lists SHA-256 and size per file and the repository commit. Licence CC BY 4.0. Produced by
`probes/e8_cc_hessian_fd.py` (symmetry reconstruction `probes/e8_symmetry.py`) in https://github.com/thebreadishard/udacity-capstone-plan.
"""


def build(name: str, out_dir: Path = OUT, results: Path = RESULTS) -> dict:
    entries, left_out = collect(results)
    if not entries:
        raise SystemExit("no VALID anchor to release")
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{name}.tar.gz"
    rd = readme(name, entries)
    (out_dir / f"{name}_README.md").write_text(rd, encoding="utf-8")
    with tarfile.open(archive, "w:gz") as tar:
        for e in entries:
            d = results / e["run_dir"]
            for f in e["files"]:
                tar.add(d / f["path"].split("/", 1)[1], arcname=f"{name}/{f['path']}")
        info = tarfile.TarInfo(f"{name}/README.md")
        data = rd.encode("utf-8")
        info.size = len(data)
        info.mtime = int(time.time())
        import io
        tar.addfile(info, io.BytesIO(data))
    manifest = {"release": name, "built_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "repository_commit": git_commit(), "n_anchors": len(entries),
                "left_out": left_out, "archive": archive.name, "archive_sha256": sha256(archive), "archive_bytes": archive.stat().st_size, "anchors": entries}
    (out_dir / f"{name}_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def check(name: str, out_dir: Path = OUT, results: Path = RESULTS) -> int:
    mp = out_dir / f"{name}_manifest.json"
    if not mp.exists():
        print(f"no manifest {mp}", file=sys.stderr)
        return 1
    m = json.load(open(mp, encoding="utf-8"))
    bad = []
    for e in m["anchors"]:
        d = results / e["run_dir"]
        for f in e["files"]:
            p = d / f["path"].split("/", 1)[1]
            if not p.exists() or sha256(p) != f["sha256"]:
                bad.append(f["path"])
    arch = out_dir / m["archive"]
    if not arch.exists() or sha256(arch) != m["archive_sha256"]:
        bad.append(m["archive"])
    if bad:
        print("anchor release STALE: " + ", ".join(bad[:8]) + (" …" if len(bad) > 8 else ""), file=sys.stderr)
        return 1
    print(f"anchor release ok ({m['n_anchors']} anchors, {m['archive_bytes']:,} bytes)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        return check(a.name)
    m = build(a.name)
    print(f"built {m['archive']} ({m['archive_bytes']:,} bytes, sha256 {m['archive_sha256'][:16]}…): {m['n_anchors']} anchors; left out: {', '.join(m['left_out']) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
