"""TASKS 174: redo what the Coriolis frame error touched (the user, 4 Nov 2026: 'Ja, maak ze opnieuw en herhaal de vier uitlezingen').

The fix (`coriolis_zeta` in the principal frame) changes VPT2 fundamentals and nothing else, so: the stored reports are rebuilt from
their stored Hessians, the GVPT2 labels from the rebuilt reports (in WSL, `gvpt2_labels.py` with the fixed pyVPT2 solver), and the four
reads are run twice with today's read scripts — on the inputs before the rebuild and after — so that only the fix separates them. The
'before' run must reproduce the stored reads (it checks the mapping of folders to options, which the reads did not record).

    python probes/coriolis_redo_174.py reads before       # today's read scripts on the stored (pre-fix) reports and labels
    python probes/coriolis_redo_174.py rebuild            # every stored qff_report.md/.npz again with `python -m dpir.qff`
    (WSL) gvpt2_labels.py for G and X                     # see the ledger entry of 4 Nov
    python probes/coriolis_redo_174.py reads after
    python probes/coriolis_redo_174.py compare
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
RES = PLAN / "probes" / "results_m1"
OUT = RES / "coriolis_redo_2026-11-04"
S2 = RES / "s2_anharmonic_2026-10-18"
ROOT = S2 / "s2"
SEL = RES / "s2_training_set_2026-10-14" / "selection.json"
EXTRA = f"A_8448043181={RES / 's1_anharmonic_benzene_2026-10-13' / 's1_benzene' / 'G'}"
GV = S2 / "gvpt2"
XTB = RES / "s2_xtb_2026-10-18"
S1 = RES / "s1_anharmonic_benzene_2026-10-13" / "s1_benzene"
IMIDAZOLE_G = ROOT / "B_151c8ce719" / "G"
SAME_CM = 1e-7   # cm⁻¹: a server-built report rebuilt on the laptop differs by ~1e-10 in φ and 3e-12 in ω (BLAS), not by the fix
STYRENE_G = ROOT / "A_8f6ed7c002" / "G"   # styrene; its 15 Oct diagnosis read this setting from a scratch copy

# folder of the stored read → (script, extra options); the scope and label source of each S2 read are inferred from its folder name
# and confirmed by the 'before' run reproducing the stored json
S2_READS = {
    "read_v2": ("s2_read.py", []),
    "read_a2_dvpt2_scope": ("s2_read.py", ["--scope", "no-linear-xh"]),
    "read_a2_gvpt2_all": ("s2_read.py", ["--gvpt2-dir", str(GV), "--scope", "all"]),
    "read_a2_gvpt2_scope": ("s2_read.py", ["--gvpt2-dir", str(GV), "--scope", "no-linear-xh"]),
    "read_a3_gvpt2_nolam": ("s2_read.py", ["--gvpt2-dir", str(GV), "--scope", "no-large-amplitude"]),
    "search_all": ("s2_search.py", ["--gvpt2-dir", str(GV), "--scope", "all"]),
    "search_no-large-amplitude": ("s2_search.py", ["--gvpt2-dir", str(GV), "--scope", "no-large-amplitude"]),
}
STORED = {**{k: S2 / k for k in S2_READS}, "read_a4": XTB / "read_a4", "s1_compare": S1}


def run(cmd: list[str]) -> None:
    """One subprocess with the plan's src on the path; a failure stops the redo."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONPATH=str(PLAN / "src") + os.pathsep + str(PLAN / "probes"))
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=PLAN, env=env, check=False)
    if r.returncode != 0:
        raise SystemExit(f"failed ({r.returncode}): {' '.join(cmd)}")


def reads(tag: str) -> None:
    """The S2 reads and searches, the xtb read, S1's compare and the two noise diagnoses of TASKS 156 (c) into OUT/<tag>/."""
    base = OUT / tag
    py = sys.executable
    for name, (script, opts) in S2_READS.items():
        run([py, f"probes/{script}", str(ROOT), "--selection", str(SEL), "--extra", EXTRA, *opts, "--out", str(base / name)])
    run([py, "probes/s2_xtb_read.py", str(ROOT), "--selection", str(SEL), "--extra", EXTRA, "--gvpt2-dir", str(GV),
         "--xtb-root", str(XTB / "xtb"), "--xtb-gvpt2-dir", str(XTB / "gvpt2_x"), "--out", str(base / "read_a4")])
    (base / "s1_compare").mkdir(parents=True, exist_ok=True)
    run([py, "probes/s1_anharmonic_level.py", "compare", str(S1 / "R"), str(S1 / "G"), str(S1 / "B"),
         "--out", str(base / "s1_compare" / "compare.json")])
    for name, setting in (("diag_imidazole", IMIDAZOLE_G), ("diag_styrene", STYRENE_G)):
        (base / name).mkdir(parents=True, exist_ok=True)
        run([py, "probes/qff_noise_diagnosis.py", str(setting), "--decouple-below", "120", "--out", str(base / name / "decouple_120.json")])


def stored_reports() -> list[Path]:
    """Every qff_report.md beside a hess folder under results_m1, outside deployed code copies."""
    return sorted(p for p in RES.rglob("qff_report.md") if "dpir" not in p.parts and (p.parent / "hess").is_dir())


def rebuild() -> None:
    """Each stored report again from its own Hessians with its own flags; the old pair kept under OUT/before_inputs/."""
    for rep in stored_reports():
        text = rep.read_text(encoding="utf-8")
        m = re.search(r"--disp ([0-9.]+)", text)
        if not m:
            raise SystemExit(f"{rep}: no --disp in its provenance")
        keep = OUT / "before_inputs" / rep.parent.relative_to(RES)
        keep.mkdir(parents=True, exist_ok=True)
        for f in ("qff_report.md", "qff_report.npz"):
            if not (keep / f).exists():   # a second run (after a stop) must not replace the pre-fix copy with a rebuilt one
                shutil.copy2(rep.parent / f, keep / f)
        noisy = ["--allow-noisy"] if "--allow-noisy" in text else []
        run([sys.executable, "-m", "dpir.qff", str(rep.parent / "hess"), "--disp", m.group(1), *noisy, "--out", str(rep)])
        old, new = np.load(keep / "qff_report.npz"), np.load(rep.parent / "qff_report.npz")
        for k in old.files:
            same = np.array_equal(old[k], new[k]) or (old[k].dtype.kind == "f" and np.allclose(old[k], new[k], rtol=0, atol=SAME_CM))
            if not (k.startswith("nu") or k.startswith("chi")) and not same:
                raise SystemExit(f"{rep}: array {k} changed — the fix must change only ν and χ")


def gap(a: float, b: float) -> float:
    """|a − b|, with two NaNs equal (a read writes NaN where a fit has no value)."""
    return 0.0 if (np.isnan(a) and np.isnan(b)) else abs(a - b)


def first_numbers(obj, prefix: str = "") -> dict[str, float]:
    """Every number in a json tree, by path; a key that is a file path keeps only its last part (the stored S1 compare names server
    folders, a local run local ones)."""
    out: dict[str, float] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out |= first_numbers(v, f"{prefix}.{re.split(r'[/\\]', str(k))[-1]}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out |= first_numbers(v, f"{prefix}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out[prefix] = float(obj)
    return out


def verdicts(obj) -> dict[str, object]:
    """The non-numeric verdict fields of a read (booleans, strings, lists of names), by path."""
    out: dict[str, object] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (bool, str)) or (isinstance(v, list) and all(isinstance(x, str) for x in v)):
                out[k] = v
            elif isinstance(v, dict):
                out |= {f"{k}.{kk}": vv for kk, vv in verdicts(v).items()}
    return out


def compare() -> None:
    """Per read: does 'before' reproduce the stored json, which verdict fields differ after, and the largest number change."""
    lines = ["# TASKS 174 — the reads before and after the Coriolis fix", ""]
    for name in [*S2_READS, "read_a4", "s1_compare"]:
        pick = lambda d: next(iter(sorted(d.glob("*.json"))))  # noqa: E731
        stored = json.loads(pick(STORED[name]).read_text(encoding="utf-8"))
        before = json.loads(pick(OUT / "before" / name).read_text(encoding="utf-8"))
        after = json.loads(pick(OUT / "after" / name).read_text(encoding="utf-8"))
        ns, nb, na = first_numbers(stored), first_numbers(before), first_numbers(after)
        repro = max((gap(ns[k], nb[k]) for k in ns.keys() & nb.keys()), default=0.0)
        moved = {k: (nb[k], na[k]) for k in nb.keys() & na.keys() if gap(nb[k], na[k]) > 0}
        top = max(moved.items(), key=lambda kv: abs(kv[1][1] - kv[1][0]), default=None)
        vb, va = verdicts(before), verdicts(after)
        flips = {k: (vb[k], va.get(k)) for k in vb if vb[k] != va.get(k)}
        lines.append(f"## {name}")
        lines.append(f"- 'before' against the stored json: largest number difference {repro:.3g}")
        lines.append(f"- numbers changed by the fix: {len(moved)}" + (f"; largest {top[0]}: {top[1][0]:.6g} → {top[1][1]:.6g}" if top else ""))
        lines.append(f"- verdict fields changed: {len(flips)}" + "".join(f"\n  - {k}: {b!r} → {a!r}" for k, (b, a) in flips.items()))
        lines.append("")
    (OUT / "compare.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="step", required=True)
    r = sub.add_parser("reads")
    r.add_argument("tag", choices=("before", "after"))
    sub.add_parser("rebuild")
    sub.add_parser("compare")
    args = ap.parse_args(argv)
    if args.step == "reads":
        reads(args.tag)
    elif args.step == "rebuild":
        rebuild()
    else:
        compare()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
