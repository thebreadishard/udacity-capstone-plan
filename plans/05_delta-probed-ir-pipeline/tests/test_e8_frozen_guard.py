"""E8 incident of 27 September 2026: the frozen-core count must follow the elements (benzene 6, naphthalene 10), and a stated mismatch refuses."""
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SRC = PLAN / "probes" / "e8_cc_hessian_fd.py"


def _guard_namespace():
    """The guard functions, read from the source without importing pyscf (the laptop has no qc env for it)."""
    import numpy as np
    ns = {"np": np}
    text = SRC.read_text(encoding="utf-8")
    exec(text[text.index("CORE_ORBITALS = {"): text.index("def gradient(")], ns)
    return ns


def _core_orbital_count(symbols):
    return _guard_namespace()["core_orbital_count"](symbols)


def test_core_count_follows_the_elements():
    assert _core_orbital_count(["C"] * 6 + ["H"] * 6) == 6          # benzene
    assert _core_orbital_count(["C"] * 10 + ["H"] * 8) == 10        # naphthalene — the run of 24–27 Sep used 6
    assert _core_orbital_count(["c", "s", "h"]) == 6                 # thiophene-like: 1 + 5 + 0, case-insensitive


def test_guard_is_wired_into_the_cli():
    text = SRC.read_text(encoding="utf-8")
    assert 'add_argument("--frozen", type=int, default=None' in text          # no silent benzene default any more
    assert "a.frozen != derived and not a.allow_frozen_mismatch" in text      # the refusal


def test_pair_consistency_is_zero_on_a_quadratic_surface_and_flags_a_jump():
    import numpy as np
    ns = _guard_namespace()
    g0 = np.array([0.01, -0.02, 0.0])
    H_col = np.array([0.5, 0.1, 0.0])
    h = 0.005
    gp, gm = g0 + h * H_col, g0 - h * H_col                                   # exact quadratic surface: mean(g+, g−) = g0
    assert ns["pair_consistency"](gp, gm, g0) == 0.0
    assert ns["pair_consistency"](gp + 3e-4, gm, g0) > ns["FIRST_PAIR_LIMIT"]   # a 3e-4 jump on one side (the incident's size) is flagged
    assert ns["pair_consistency"](gp + 1e-6, gm, g0) < ns["FIRST_PAIR_LIMIT"]   # numerical noise of 1e-6 is not


def test_failfast_is_wired_into_the_assembly():
    text = SRC.read_text(encoding="utf-8")
    assert "hessian_ccsd_t_INVALID.npz" in text and "raise SystemExit(2)" in text and "raise SystemExit(3)" in text
