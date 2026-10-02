"""E8 --max-memory (29 Sep 2026, the parallel anchor chain): the switch exists with the former hard-coded default, every gradient call passes it,
and the mol is built from it — read from the source, since the laptop has no pyscf. Also the parallel chain script: bash -n and fail-fast."""
import ast
import re
import subprocess
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SRC = PLAN / "probes" / "e8_cc_hessian_fd.py"
CHAIN = PLAN / "probes" / "run_anchors_hel23_parallel.sh"


def test_max_memory_switch_default_and_plumbing():
    text = SRC.read_text(encoding="utf-8")
    tree = ast.parse(text)
    grad = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "gradient")
    names = [a.arg for a in grad.args.args]
    defaults = dict(zip(names[-len(grad.args.defaults):], [getattr(d, "value", d) for d in grad.args.defaults], strict=True))
    assert defaults["max_memory"] == 26000
    assert re.search(r'add_argument\("--max-memory", type=int, default=26000', text)
    assert re.search(r"gto\.M\([^\n]*max_memory=max_memory", text) and "max_memory=26000)" not in text   # the hard-coded value is gone from gto.M
    assert text.count("a.charge, a.spin, a.max_memory, fast") == 3   # reference, the separate two-route check (2 Oct 2026), displaced gradients


def test_parallel_chain_parses_and_fails_fast():
    text = CHAIN.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text and "--max-memory" in text and "--only-reference" in text
    assert "kill -TERM \"$victim\"" in text and "GUARD_MB" in text                         # memory guard stops one named pid, never a pattern
    r = subprocess.run(["bash", "-n", str(CHAIN)], capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
