"""tools/py39_check.py: every 3.10 form it looks for is found in a synthetic file, the 3.9 forms that look alike are not, and postponed
annotations exempt annotations but not run-time aliases."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import py39_check as P

CASES = {
    "zip(strict=) is 3.10": "for a, b in zip(x, y, strict=True):\n    pass\n",
    "pairwise is 3.10": "import itertools\nitertools.pairwise(x)\n",
    "bit_count is 3.10": "n = (5).bit_count()\n",
    "X | Y in isinstance is 3.10": "isinstance(x, int | str)\n",
    "dataclass(kw_only) is 3.10": "from dataclasses import dataclass\n@dataclass(kw_only=True)\nclass A:\n    x: int\n",
    "X | Y in an annotation without postponed annotations": "def f(x: int | None) -> None:\n    pass\n",
    "X | Y type alias evaluated at run time": "Alias = dict[str, int] | None\n",
    "not Python 3.9 grammar": "match x:\n    case 1:\n        pass\n",
}


@pytest.mark.parametrize("what", sorted(CASES))
def test_each_310_form_is_found(tmp_path, what):
    f = tmp_path / "m.py"
    f.write_text(CASES[what], encoding="utf-8")
    found = P.findings(f)
    assert len(found) == 1 and what in found[0], found


def test_39_forms_that_look_alike_pass(tmp_path):
    f = tmp_path / "m.py"
    f.write_text("from __future__ import annotations\n"
                 "def f(x: int | None, d: dict[str, int] | None = None) -> tuple[int, ...] | None:\n    return None\n"
                 "flags = 1 | 2\nmerged = {'a': 1} | {'b': 2}\nfor a, b in zip(x, y):\n    pass\n'abc'.removesuffix('c')\n",
                 encoding="utf-8")
    assert P.findings(f) == []


def test_postponed_annotations_do_not_cover_a_run_time_alias(tmp_path):
    f = tmp_path / "m.py"
    f.write_text("from __future__ import annotations\nAlias = int | None\n", encoding="utf-8")
    assert [s.split(": ", 1)[1] for s in P.findings(f)] == ["X | Y type alias evaluated at run time"]
