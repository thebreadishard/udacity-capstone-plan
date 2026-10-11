"""TASKS 42 (the user, 10 Oct 2026: files no longer needed live only in the git history): list the tracked files that may be removed, each with
the reason it qualifies or the reference that keeps it. Nothing is removed here; the list goes into the commit message of the `git rm`.

A candidate (a dated one-off `probes/*_MMDD.sh|py`, or a tool named in SUPERSEDED) is removable when
  1. no process runs it (`ps -ef` in Git Bash, `ps` in WSL) and no job table or run spec names it (probes/watch_jobs.tsv, probes/runs/*.json);
  2. no kept code names it: a script, module, test, notebook, config or job file (code extensions below) outside the run records
     (`results_*`, `out/`); references among candidates do not count once both go (a fixed point);
  3. its outcome is recorded — one of: its name appears in a Markdown document (ledger, TASKS, registrations, READMEs, notes); the chain
     or lever its header names ('chain 24', 'Chain 36', 'Lever 5') appears in one; a log or result file it writes (out/…, results_m1/…) exists on disk.
A file name inside a comment line (#, rem, ::, //) is documentation, not use, and keeps nothing.
Documents that cite a removed file keep the path: git keeps the file.

    python tools/cleanup_candidates.py [--no-processes]      # prints the table; exit 0
"""
import argparse
import fnmatch
import glob
import os
import re
import subprocess
import sys

PLAN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.abspath(os.path.join(PLAN, "..", ".."))
REL = os.path.relpath(PLAN, ROOT).replace(os.sep, "/")
DATED = re.compile(r"^probes/[^/]+_[0-9]{4}[a-z]?\.(sh|py)$")
SUPERSEDED = {   # tool → why it is no longer used
    "tools/backup_loop.sh": "superseded 9 Oct 2026 by the scheduled task CapstoneDataBackup (tools/backup_task.cmd); its header says so",
}
CODE = ("*.py", "*.sh", "*.cmd", "*.ps1", "*.json", "*.tsv", "*.ipynb", "*.toml", "*.yml", "*.yaml", "*.mjs", "*.ts", "*.astro")
RECORDS = ("*/results_*/*", "*/out/*", "*/runs_archive/*")       # run records: their mentions keep nothing


def tracked(root=ROOT):
    out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, check=True).stdout.decode("utf-8")
    return [p for p in out.split("\0") if p]


def candidates(files, rel=REL):
    """{repo path: why it is a candidate} for the plan's dated one-offs and the superseded tools."""
    out = {}
    for p in files:
        if not p.startswith(rel + "/"):
            continue
        q = p[len(rel) + 1:]
        if DATED.match(q):
            out[p] = "dated one-off"
        elif q in SUPERSEDED:
            out[p] = SUPERSEDED[q]
    return out


COMMENT = re.compile(r"^\s*(#|rem\b|::|//)", re.I)
CHAIN = re.compile(r"\b(chain|lever)s?[ _]?(\d+[a-z]?)\b", re.I)
OUTPUT = re.compile(r"(?:out|results_m1)/[\w./\-]+?\.(?:log|json|md|npz|csv)")


def code_lines(text):
    """The text without its comment lines."""
    return "\n".join(line for line in text.split("\n") if not COMMENT.match(line))


def evidence(path, text, docs, plan=PLAN):
    """How a candidate's outcome is recorded: (kind, where), or None."""
    name = os.path.basename(path)
    named = sorted(f for f, t in docs.items() if mention(name).search(t))
    if named:
        return "named", named[0]
    header = "\n".join(text.split("\n")[:6])
    for kind, n in CHAIN.findall(header):
        pat = re.compile(rf"\b{kind.lower()}s?[ _]?{re.escape(n)}\b", re.I)
        hit = sorted(f for f, t in docs.items() if pat.search(t))
        if hit:
            return f"{kind.lower()} {n} recorded", hit[0]
    for out in OUTPUT.findall(text):
        for base in (plan, os.path.join(plan, "probes"), os.path.join(plan, "modules", "05_support_predictor")):
            if os.path.exists(os.path.join(base, out)):
                return "output on disk", out
    return None


def mention(name):
    """A regex for a file name as a word of its own (not inside a longer name)."""
    return re.compile(r"(?<![\w.\-])" + re.escape(name) + r"(?![\w\-])")


def is_code(path):
    return any(fnmatch.fnmatch(os.path.basename(path), pat) for pat in CODE) and not any(fnmatch.fnmatch(path, pat) for pat in RECORDS)


def referrers(cands, texts):
    """{candidate: [code files that name it]}: by file name, and for a Python module by `import stem` / `from stem import`."""
    out = {}
    for c in cands:
        name = os.path.basename(c)
        pats = [mention(name)]
        if name.endswith(".py"):
            stem = re.escape(name[:-3])
            pats.append(re.compile(rf"^\s*(?:from\s+{stem}\s+import|import\s+{stem}\b)", re.M))
        out[c] = sorted(f for f, t in texts.items() if f != c and is_code(f) and any(p.search(code_lines(t)) for p in pats))
    return out


def fixed_point(cands, refs):
    """The candidates whose referrers are all removable themselves; a kept referrer keeps the candidate (iterated until stable)."""
    removable = set(cands)
    changed = True
    while changed:
        changed = False
        for c in sorted(removable):
            if any(r not in removable for r in refs[c]):
                removable.discard(c)
                changed = True
    return removable


def running_texts(use_processes=True):
    """Command lines of running processes (Git Bash and WSL) and the job tables: a candidate named here is in use."""
    parts = []
    if use_processes:
        for cmd in (["ps", "-ef"], ["wsl.exe", "-e", "ps", "-eo", "args"]):
            try:
                parts.append(subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
                                            check=False).stdout or "")
            except (OSError, subprocess.SubprocessError):
                parts.append("")
    for p in [os.path.join(PLAN, "probes", "watch_jobs.tsv"), *glob.glob(os.path.join(PLAN, "probes", "runs", "*.json"))]:
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8", errors="replace").read())
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-processes", action="store_true", help="skip ps (tests, or a machine where the jobs do not run)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    files = tracked()
    texts = {}
    for f in files:
        if is_code(f) or f.endswith(".md"):
            try:
                texts[f] = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()
            except OSError:
                pass
    cands = candidates(files)
    refs = referrers(cands, texts)
    removable = fixed_point(cands, refs)
    live = running_texts(not a.no_processes)
    docs = {f: t for f, t in texts.items() if f.endswith(".md")}
    rows = []
    for c in sorted(cands):
        name = os.path.basename(c)
        kept_by = [r for r in refs[c] if r not in removable]
        recorded = evidence(c, texts.get(c, ""), docs)
        if mention(name).search(live):
            rows.append((c, "KEEP", "running or in a job table / run spec"))
        elif kept_by:
            rows.append((c, "KEEP", "named by kept code: " + ", ".join(kept_by[:3]) + (" …" if len(kept_by) > 3 else "")))
        elif not recorded:
            rows.append((c, "REVIEW", "no record found (name, chain, output): is its outcome recorded?"))
        else:
            rows.append((c, "REMOVE", f"{cands[c]}; {recorded[0]}: {recorded[1]}"))
    for c, verdict, why in rows:
        print(f"{verdict:6} {c}  — {why}")
    n = {v: sum(1 for r in rows if r[1] == v) for v in ("REMOVE", "KEEP", "REVIEW")}
    print(f"\n{len(rows)} candidates: {n['REMOVE']} remove, {n['KEEP']} keep, {n['REVIEW']} review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
