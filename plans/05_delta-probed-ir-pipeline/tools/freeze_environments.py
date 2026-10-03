"""Frozen listings of every Python environment the plan runs in (3 Oct 2026, the user: "Doe maar" after the requirements audit).

One file per environment under `environments/`: a header (name, command, python version, when) and the sorted package list as the environment's own
tool prints it (`pip freeze` for venvs and the system Python, `conda list --export` for conda environments). Editable installs and local file
references are dropped (they are paths, not versions). The Windows system listing is also written as module 05's `requirements.txt` with the
module's header, because that is the environment its notebook and probes run in.

    python tools/freeze_environments.py            # regenerate every listing that can be reached from this machine
    python tools/freeze_environments.py --check    # exit 1 when a reachable listing differs from the committed file (the header's date is ignored)

Environments that cannot be listed from this machine (a WSL environment when WSL is absent, a server) are reported as skipped, never as failures;
the servers' listings arrive through the full-fetch waiters (`probes/fetch_*_full_*.sh`, `environment_*.txt` beside the results) and are copied here
by hand with a dated name. Mechanical: nothing in the listings is typed by hand.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
ENV_DIR = PLAN / "environments"
M05_REQ = PLAN / "modules" / "05_support_predictor" / "requirements.txt"
REPO = PLAN.parents[1]
WSL = ["wsl", "-e", "bash", "-lc"]
ENVIRONMENTS = {
    # name: (what runs there, listing command, python-version command)
    "windows-python314": ("modules 05/06 and the Windows probes (torch, rdkit, geometric)", [sys.executable, "-m", "pip", "freeze"], [sys.executable, "--version"]),
    "windows-venv313": ("module 07 (LangGraph)", [str(REPO / ".venv" / "Scripts" / "python.exe"), "-m", "pip", "freeze"], [str(REPO / ".venv" / "Scripts" / "python.exe"), "--version"]),
    "wsl-qc05": ("our pyscf branch, the E8 anchors, gate 1, the LNO probes", [*WSL, "~/qc05/bin/python -m pip freeze"], [*WSL, "~/qc05/bin/python --version"],
                 [("pyscf source checkout (pip shows only 2.14.0; the package was built from this branch)",
                   [*WSL, "cd ~/pyscf-master && echo \"$(git rev-parse --abbrev-ref HEAD) $(git log -1 --format='%h %cs') dirty=$(git status --short | wc -l)\""])]),
    "wsl-vpt2": ("psi4 + pyVPT2 (route 2 of 22 Sep)", [*WSL, "~/miniforge3/bin/conda list -n vpt2 --export"], [*WSL, "~/miniforge3/envs/vpt2/bin/python --version"]),
}
M05_HEADER = ("# Module 05 — the Windows environment its notebook, trainer and probes run in (system Python 3.14, CPU-only torch). Frozen by\n"
              "# tools/freeze_environments.py from `pip freeze`; identical to environments/windows-python314.txt. Regenerate with that tool after any install.\n")


def run(cmd: list[str], timeout: int = 300) -> str | None:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    return p.stdout


def normalise(text: str) -> list[str]:
    """The package lines only: no comments, no blank lines, no editable or local-file installs; sorted, case-insensitively."""
    out = []
    for ln in text.replace("\r", "").split("\n"):
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("-e ") or " @ file:" in s or s.startswith("@"):
            continue
        out.append(s)
    return sorted(set(out), key=str.lower)


def locals_of(text: str) -> list[str]:
    """The editable and local-file installs the listing drops from the body — kept as header comments so that a branch checkout stays visible."""
    out = []
    for ln in text.replace("\r", "").split("\n"):
        s = ln.strip()
        if s.startswith("-e ") or " @ file:" in s:
            out.append(s)
    return sorted(out)


def body_of(text: str) -> list[str]:
    """What is compared: every line that is not a header comment."""
    return [ln for ln in text.replace("\r", "").split("\n") if ln and not ln.startswith("#")]


def listing(name: str) -> tuple[str | None, str]:
    """(text, python version) for one environment, or (None, reason) when it cannot be listed here."""
    _what, cmd, pycmd, *rest = ENVIRONMENTS[name]
    extras = rest[0] if rest else []
    raw = run(cmd)
    if raw is None:
        return None, "not reachable from this machine"
    ver = (run(pycmd) or "").strip().replace("\n", " ")
    header = (f"# environment: {name} — {_what}\n# command: {' '.join(cmd[-1:] if cmd[:3] == WSL else cmd)}\n# python: {ver}\n"
              f"# frozen: {time.strftime('%Y-%m-%d %H:%M')} on {_host()} by tools/freeze_environments.py\n")
    header += "".join(f"# local install (not a version): {ln}\n" for ln in locals_of(raw))
    for label, xcmd in extras:                                              # provenance a package list cannot show (a branch checkout behind a plain version)
        out = (run(xcmd) or "unavailable").strip().replace("\n", " ")
        header += f"# {label}: {out}\n"
    return header + "\n".join(normalise(raw)) + "\n", ver


def _host() -> str:
    import platform
    return platform.node()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", default=None, help="comma list of environment names")
    a = ap.parse_args(argv)
    names = a.only.split(",") if a.only else list(ENVIRONMENTS)
    ENV_DIR.mkdir(exist_ok=True)
    stale, written, skipped = [], [], []
    for name in names:
        text, info = listing(name)
        target = ENV_DIR / f"{name}.txt"
        if text is None:
            skipped.append(f"{name} ({info})")
            continue
        if a.check:
            if not target.exists() or body_of(target.read_text(encoding="utf-8")) != body_of(text):
                stale.append(name)
            if name == "windows-python314" and (not M05_REQ.exists() or body_of(M05_REQ.read_text(encoding="utf-8")) != body_of(text)):
                stale.append("module 05 requirements.txt")
            continue
        target.write_text(text, encoding="utf-8")
        written.append(f"{name} ({len(body_of(text))} packages, {info})")
        if name == "windows-python314":
            M05_REQ.write_text(M05_HEADER + text, encoding="utf-8")
            written.append("module 05 requirements.txt")
    if skipped:
        print("skipped: " + "; ".join(skipped))
    if a.check:
        if stale:
            print("environments STALE: " + ", ".join(stale) + " — run tools/freeze_environments.py", file=sys.stderr)
            return 1
        print(f"environments ok ({len(names) - len(skipped)} checked)")
        return 0
    print("written: " + "; ".join(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
