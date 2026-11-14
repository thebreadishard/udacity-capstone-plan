"""The reading window as a setting of the reads (TASKS 219, 14 Nov 2026): one filter, named presets, and every reader taking the window
it reads in. The CH-stretch family sits above 2800 cm-1, outside the window S2, S2b and S3 were registered with, so the window had to
become a setting before that family could be read at all.

The last test is the guard that matters: the window is defaulted, so a reader that forgets to pass it on would silently read the
registered 550-2000 cm-1 and nobody would see it in the numbers. It walks the reads' syntax trees and insists that every call to a
window-taking function passes one.
"""
from __future__ import annotations

import ast
import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s2_read as R

from test_s2_read import molecule

CH = R.WINDOWS["ch"]
PROBES = PLAN / "probes"
# the five reads, and everything else in probes/ that imports their window-taking functions: s2_diagnose.py called concat
# and loso with no window for as long as the guard looked only at the five (14 Nov 2026, the independent review)
SOURCES = ("s2_read", "s2_xtb_read", "s2_search")
# the five reads: the files where the window-takers are defined, so a definition there is one of them. Elsewhere only an
# import from them counts - s1tz_read.py has a `curve` of its own that has nothing to do with these (14 Nov 2026).
OWN = {*SOURCES, "s2b_read", "s3_read"}
IMPORTS = re.compile(r"from (" + "|".join(SOURCES) + r") import")
READS = tuple(sorted({f"{m}.py" for m in SOURCES} | {"s2b_read.py", "s3_read.py"}
                     | {p.name for p in (PLAN / "probes").glob("*.py") if IMPORTS.search(p.read_text("utf-8"))}))
# function name → (the position of its window parameter, counting from 0, or None when it is keyword-only in practice)
WINDOW_TAKERS = {"in_window": 1, "concat": 1, "loso": 4, "curve": 5, "x0_read": 1, "build": 4, "window_size": 1,
                 "window_table": 1, "fit_on": 4, "loso_predictions": 3, "nested": 3, "read_scope": 1, "load_set": 1}


def spread(rng: np.random.Generator, omega: tuple[float, ...]) -> dict:
    """A synthetic molecule with its modes placed at `omega`, so a window has something to keep and something to drop."""
    mol = molecule(rng)
    mol["omega"] = np.resize(np.array(omega, float), len(mol["omega"]))
    return mol


def dataset_at(omega: tuple[float, ...], n_scaf: int = 6) -> dict:
    rng = np.random.default_rng(11)
    return {f"s{i:02d}": [spread(rng, omega) for _ in range(2)] for i in range(n_scaf)}


def test_the_registered_window_is_the_default_and_has_not_moved():
    mid, ch = R.WINDOWS["mid"], R.WINDOWS["ch"]
    assert mid == (550.0, 2000.0) and ch == (2800.0, math.inf) and sorted(R.WINDOWS) == ["ch", "mid"]
    assert mid == R.WINDOW and ch == CH


def test_both_bounds_are_included_and_the_ch_window_has_no_upper_bound():
    assert list(R.in_window([549.9, 550.0, 1200.0, 2000.0, 2000.1])) == [False, True, True, True, False]
    assert list(R.in_window([2799.9, 2800.0, 3100.0, 99999.0], CH)) == [False, True, True, True]


def test_concat_keeps_the_modes_of_the_window_it_is_given():
    mols = [spread(np.random.default_rng(2), (400.0, 900.0, 1500.0, 3050.0))]
    assert len(R.concat(mols)["omega"]) == 8                      # the 900 and 1500 of each of the 16 modes' four-fold spread
    assert (R.concat(mols, CH)["omega"] == 3050.0).all()
    assert len(R.concat(mols, CH)["omega"]) == 4


def test_the_curve_reads_only_the_window_it_is_given():
    data = dataset_at((900.0, 1500.0, 3050.0, 3100.0))
    mid, ch = R.curve(data, n_subsets=2, window=R.WINDOW), R.curve(data, n_subsets=2, window=CH)
    assert mid["all"]["n_modes"] == 96 and ch["all"]["n_modes"] == 96   # eight of each molecule's sixteen modes in either window
    assert mid["all"]["c"] != ch["all"]["c"]                            # different modes, so a different read


def test_a_window_with_no_modes_says_so_instead_of_failing_inside_numpy():
    data = dataset_at((900.0, 1200.0, 1500.0, 1800.0))                  # nothing above 2800
    with pytest.raises(ValueError, match="nothing to read"):
        R.curve(data, n_subsets=2, window=CH)


def test_the_command_line_names_a_window_and_defaults_to_the_registered_one():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", nargs="*", default=[])
    R.add_window_argument(ap)
    assert R.options_from_args(ap.parse_args([])).window == R.WINDOW
    assert R.options_from_args(ap.parse_args(["--window", "ch"])).window == CH
    with pytest.raises(SystemExit):
        ap.parse_args(["--window", "2800-inf"])


def test_the_xtb_read_and_the_search_take_the_window_too():
    X = pytest.importorskip("s2_xtb_read")
    S = pytest.importorskip("s2_search")
    rng = np.random.default_rng(5)
    by_scaf = {}
    for i in range(4):
        mols = []
        for _ in range(2):
            m = spread(rng, (900.0, 1500.0, 3050.0, 3100.0))
            m[X.XTB_KEY] = m["delta"] * 0.9 - 1.5
            mols.append(m)
        by_scaf[f"s{i:02d}"] = mols
    mid, ch = X.x0_read(by_scaf), X.x0_read(by_scaf, CH)
    assert sum(v["n"] for v in mid.values()) == sum(v["n"] for v in ch.values()) == 64   # 8 of each molecule's 16 modes, 8 molecules
    assert any(mid[fa]["rms"] != ch[fa]["rms"] for fa in mid)
    assert (S.window_table(by_scaf["s00"], CH)["omega"] >= 2800.0).all()


def test_the_read_reports_its_own_size_before_any_model_is_fitted():
    """The CH-stretch registration, section 2: the modes per family per force field and in all, which rule 4 turns on."""
    data = dataset_at((900.0, 1500.0, 3050.0, 3100.0), n_scaf=3)
    for mols in data.values():
        for i, m in enumerate(mols):
            m["id"] = f"{id(mols)}-{i}"
    mid, ch = R.window_size(data), R.window_size(data, CH)
    assert mid["molecules"] == ch["molecules"] == 6
    assert mid["modes"] == ch["modes"] == 48                        # eight of each molecule's sixteen modes in either window
    assert sum(mid["per_family"].values()) == mid["modes"]
    assert set(mid["per_molecule"]) == set(ch["per_molecule"]) and len(mid["per_molecule"]) == 6


def test_a_mode_set_without_an_id_is_still_counted():
    one = {"s00": [spread(np.random.default_rng(1), (900.0,))]}
    assert R.window_size(one)["modes"] == 16


def window_taking_names(tree: ast.Module, stem: str) -> set[str]:
    """The window-taking names this file means: what it imports from the read machinery, and - in the five reads only - what
    it defines. Matching by name alone flagged s1tz_read.py's own `curve` (14 Nov 2026, the independent review)."""
    names: set[str] = set()
    if stem in OWN:
        names |= {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)} & set(WINDOW_TAKERS)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in SOURCES:
            names |= {alias.asname or alias.name for alias in node.names} & set(WINDOW_TAKERS)
    return names


def calls_without_a_window(path: Path) -> list[str]:
    """Every call in `path` to a window-taking function that passes no window, by name and line."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    taking = window_taking_names(tree, path.stem)
    missed = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
        if name not in taking:
            continue
        if any(k.arg == "window" for k in node.keywords) or len(node.args) > WINDOW_TAKERS[name]:
            continue
        missed.append(f"{path.name}:{node.lineno} {name}(...)")
    return missed


@pytest.mark.parametrize("name", READS)
def test_every_read_passes_the_window_on(name):
    missed = calls_without_a_window(PROBES / name)
    assert not missed, "a call that would silently read the registered window: " + "; ".join(missed)


def test_an_open_bound_is_written_as_null_so_the_record_is_json():
    """Python writes float('inf') as Infinity, which RFC 8259 has no word for and no other parser reads."""
    import json

    assert R.window_record(R.WINDOW) == [550.0, 2000.0]
    assert R.window_record(CH) == [2800.0, None]
    text = json.dumps({"window": R.window_record(CH)})
    assert "Infinity" not in text
    assert json.loads(text, parse_constant=_no_constants) == {"window": [2800.0, None]}


def _no_constants(name: str):
    raise AssertionError(f"the record carries {name}, which is not JSON")


def test_the_guard_covers_every_file_that_imports_the_window_takers():
    """The list is derived, not kept by hand: a new consumer of concat or loso is guarded the day it is written."""
    assert {"s2_read.py", "s2b_read.py", "s3_read.py", "s2_diagnose.py"} <= set(READS)
    assert len(READS) >= 8
