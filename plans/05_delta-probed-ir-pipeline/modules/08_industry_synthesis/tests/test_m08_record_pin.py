"""The certificate record, pinned before module 08's reads move behind one resolver (TASKS 20, 14 November 2026).

The standalone plan of 18 October routes every file module 08 reads through `m08/paths.resolve`, so that the submitted repository
can read a frozen `snapshot/` instead of the plan's live folders. That is a change to twenty read sites, and the way to make it safe
is to pin what the module produces first: two certificates, one anchored (naphthalene, a composite anchor) and one at the project's
first molecule (benzene), with the two fields that move between builds left out.

The comparison is `tests/pin_tools.first_difference`, the one the other pins use. The two volatile fields are dropped by path and
not by name, because `date` also names the anchor registry's own field, which the pin must keep watching.

    python modules/08_industry_synthesis/tests/test_m08_record_pin.py --write-golden
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
PLAN = MODULE.parents[1]
sys.path.insert(0, str(MODULE))
sys.path.insert(0, str(PLAN / "tests"))
from pin_tools import first_difference  # noqa: E402

GOLDEN = HERE / "fixtures" / "certificates_pin.json"
PINNED = ("naphthalene", "benzene")
VOLATILE = (("date",), ("provenance", "commit"))     # the build's minute and the commit it was built at


def stripped(record: dict) -> dict:
    """The record without the two fields that move between two builds of the same state."""
    out = json.loads(json.dumps(record))
    for *parents, leaf in VOLATILE:
        node = out
        for key in parents:
            node = node[key]
        node.pop(leaf, None)
    return out


def records() -> dict[str, dict]:
    from m08.catalog import Catalog
    from m08.certify import certificate

    catalog = Catalog()
    rows = {name: next(r for r in catalog.rows if r["name"] == name) for name in PINNED}
    return {name: stripped(certificate(row, catalog)) for name, row in rows.items()}


@pytest.mark.parametrize("name", PINNED)
def test_the_certificate_record_is_unchanged(name: str) -> None:
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing what the module reads")
    pinned = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert name in pinned, f"{name} is not in the pin; write it again"
    assert (diff := first_difference(pinned[name], records()[name])) is None, diff


def test_the_pin_covers_an_anchored_rung() -> None:
    """A pin that had only seen an unanchored certificate would not protect the anchor block."""
    fresh = records()
    assert fresh["naphthalene"]["rung"]["reached"] >= 4
    assert fresh["naphthalene"]["anchor"]["entry"], "naphthalene is the anchored case; the pin needs one"


if __name__ == "__main__":
    if sys.argv[1:] != ["--write-golden"]:
        sys.exit(__doc__)
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_text(json.dumps(records(), indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"pinned {len(PINNED)} certificates to {GOLDEN} ({GOLDEN.stat().st_size} bytes)")
