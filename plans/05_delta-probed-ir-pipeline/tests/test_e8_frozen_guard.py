"""E8 incident of 27 September 2026: the frozen-core count must follow the elements (benzene 6, naphthalene 10), and a stated mismatch refuses."""
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SRC = PLAN / "probes" / "e8_cc_hessian_fd.py"


def _core_orbital_count(symbols):
    """The function under test, read from the source without importing pyscf (the laptop has no qc env for it)."""
    ns = {}
    text = SRC.read_text(encoding="utf-8")
    start = text.index("CORE_ORBITALS = {")
    end = text.index("def gradient(")
    exec(text[start:end], ns)
    return ns["core_orbital_count"](symbols)


def test_core_count_follows_the_elements():
    assert _core_orbital_count(["C"] * 6 + ["H"] * 6) == 6          # benzene
    assert _core_orbital_count(["C"] * 10 + ["H"] * 8) == 10        # naphthalene — the run of 24–27 Sep used 6
    assert _core_orbital_count(["c", "s", "h"]) == 6                 # thiophene-like: 1 + 5 + 0, case-insensitive


def test_guard_is_wired_into_the_cli():
    text = SRC.read_text(encoding="utf-8")
    assert 'add_argument("--frozen", type=int, default=None' in text          # no silent benzene default any more
    assert "a.frozen != derived and not a.allow_frozen_mismatch" in text      # the refusal
