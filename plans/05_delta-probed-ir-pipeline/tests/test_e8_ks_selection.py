"""E8 --ks option (fixed 28 Sep 2026): the slice and the comma list both index the displacement list; the comma list used to be read as raw
coordinate indices, which produced the two 'extra' partial runs of the 27 September incident."""
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SRC = PLAN / "probes" / "e8_cc_hessian_fd.py"


def _select():
    import numpy as np
    ns = {"np": np}
    text = SRC.read_text(encoding="utf-8")
    exec(text[text.index("CORE_ORBITALS = {"): text.index("def gradient(")], ns)   # no pyscf on the laptop; the helpers are read from the source
    return ns["select_displacements"]


def test_empty_spec_keeps_the_whole_list():
    assert _select()([3, 7, 11, 15], "") == [3, 7, 11, 15]


def test_slice_and_comma_list_index_the_same_list():
    sel = _select()
    ks = [3, 7, 11, 15]                                   # a symmetry-reduced displacement list (coordinate indices)
    assert sel(ks, "0:2") == [3, 7]
    assert sel(ks, "1,3") == [7, 15]                      # before the fix this returned [1, 3] — coordinates outside the reduced list
    assert sel(ks, "2:") == [11, 15]


def test_main_uses_the_helper():
    text = SRC.read_text(encoding="utf-8")
    assert "ks = select_displacements(ks, a.ks)" in text
