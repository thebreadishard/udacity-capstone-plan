"""The newest upstream release of the packages our numbers rest on, against the versions pinned in `environments/` (11 Oct 2026, the user:
pyscf may publish new versions during the project, some carrying our own merged pull requests).

One line for `probes/state.sh`. A release newer than every pinned version is flagged: an environment moves only through the upgrade checklist
in `GoalGathering/notes/Software_Changes_Ledger.md` ('How to use this ledger'), never mid-run. Offline, the line says so and the digest goes on.

    python tools/upstream_releases.py
"""
import glob
import json
import os
import re
import sys
import urllib.request

PACKAGES = ("pyscf", "pyscf-forge")
HERE = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENTS = os.path.join(HERE, "..", "environments")


def canonical(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def version_key(v):
    """Numeric release tuple; a pre-release suffix sorts below its release (2.15.0rc1 < 2.15.0)."""
    parts = []
    for p in v.split("."):
        m = re.match(r"(\d+)(.*)", p)
        parts.append((int(m.group(1)), 0 if m.group(2) else 1) if m else (0, 0))
    return tuple(parts)


def pinned_versions(env_dir=ENVIRONMENTS):
    """{package: {version: [environment files]}} from the `name==version` lines of the frozen environment listings."""
    out = {}
    for path in sorted(glob.glob(os.path.join(env_dir, "*.txt"))):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s;]+)", line.strip())
            if m and canonical(m.group(1)) in PACKAGES:
                out.setdefault(canonical(m.group(1)), {}).setdefault(m.group(2), []).append(os.path.basename(path))
    return out


def latest_release(package, timeout=5):
    """(version, upload date) of the newest PyPI release, or None when PyPI cannot be reached."""
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{package}/json", timeout=timeout) as r:
            info = json.load(r)
    except (OSError, ValueError):
        return None
    v = info["info"]["version"]
    files = info["releases"].get(v) or [{}]
    return v, files[0].get("upload_time", "?")[:10]


def summary(pinned, latest):
    """One digest line and whether any package has a release newer than everything pinned."""
    parts, new = [], False
    for p in PACKAGES:
        pins = sorted(pinned.get(p, {}), key=version_key)
        pin_text = "/".join(pins) if pins else "not pinned"
        rel = latest.get(p)
        if rel is None:
            parts.append(f"{p} pinned {pin_text}, PyPI unreachable")
            continue
        newer = bool(pins) and version_key(rel[0]) > version_key(pins[-1])
        new |= newer
        parts.append(f"{p} pinned {pin_text}, PyPI {rel[0]} ({rel[1]})" + (" NEW" if newer else ""))
    line = "  upstream releases: " + " | ".join(parts)
    if new:
        line += " — a newer release: read its changelog for our pull requests and follow the upgrade checklist (software ledger)"
    return line, new


def main():
    line, _ = summary(pinned_versions(), {p: latest_release(p) for p in PACKAGES})
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
