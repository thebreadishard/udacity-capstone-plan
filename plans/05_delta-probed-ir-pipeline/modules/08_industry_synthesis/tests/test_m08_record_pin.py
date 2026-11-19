"""The certificate record, pinned before module 08's reads move behind one resolver (TASKS 20, 14 November 2026).

The standalone plan of 18 October routes every file module 08 reads through `m08/paths.resolve`, so that the submitted repository
can read a frozen `snapshot/` instead of the plan's live folders. That is a change to twenty read sites, and the way to make it safe
is to pin what the module produces first: two certificates, one anchored (naphthalene, a composite anchor) and one at the project's
first molecule (benzene), with the fields that move between builds left out (`VOLATILE`).

The comparison is `tests/pin_tools.first_difference`, the one the other pins use. The volatile fields are dropped by path and
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

GOLDEN = PLAN / "tests" / "data" / "m08_certificates_pin.json"   # the project keeps its goldens together
PINNED = ("naphthalene", "benzene")
# the build's minute, the commit it was built at, and the website export's build stamp and catalogue-manifest hash, which change on
# every rebuild of the export though no value a certificate states has changed (TASKS 273)
VOLATILE = (
    ("date",),
    ("provenance", "commit"),
    ("provenance", "export_built_utc"),
    ("provenance", "export_sources_sha256", "manifest"),
)


def stripped(record: dict) -> dict:
    """The record without the fields that move between two builds of the same state."""
    out = json.loads(json.dumps(record))
    for *parents, leaf in VOLATILE:
        node = out
        for key in parents:
            node = node.get(key) if isinstance(node, dict) else None
        if isinstance(node, dict):
            node.pop(leaf, None)
    return out


def pin_difference(pinned: dict, fresh: dict) -> str | None:
    """The first place where a fresh certificate departs from its pin, the volatile fields left out on both sides."""
    return first_difference(stripped(pinned), stripped(fresh))


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
    assert (diff := pin_difference(pinned[name], records()[name])) is None, diff


def pinned_naphthalene() -> dict:
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}")
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["naphthalene"]


def test_the_pin_holds_no_volatile_field() -> None:
    """A volatile field written into the pin would be compared after all, since the comparison strips both sides only of what it
    finds; keeping them out of the file keeps the pin readable as what it watches."""
    pinned = pinned_naphthalene()
    assert stripped(pinned) == pinned


def test_an_export_rebuild_does_not_break_the_pin() -> None:
    pinned = pinned_naphthalene()
    rebuilt = json.loads(json.dumps(pinned))
    rebuilt["provenance"]["export_built_utc"] = "2099-01-01T00:00:00Z"
    rebuilt["provenance"]["export_sources_sha256"]["manifest"] = "0" * 64
    rebuilt["provenance"]["commit"] = "deadbee"
    rebuilt["date"] = "2099-01-01 00:00"
    assert pin_difference(pinned, rebuilt) is None


@pytest.mark.parametrize(("path", "value"), [
    (("provenance", "licence", "errors", "CH-oop", "a"), 9.99),
    (("provenance", "export_sources_sha256", "ledger"), "0" * 64),
])
def test_the_pin_still_bites_on_a_certificate_value(path: tuple[str, ...], value: object) -> None:
    """A licence error or the export's source ledger changing is a change the pin exists to catch."""
    pinned = pinned_naphthalene()
    changed = json.loads(json.dumps(pinned))
    node = changed
    for key in path[:-1]:
        node = node[key]
    if node[path[-1]] == value:
        pytest.fail(f"the pin already holds {value!r} at {path}: pick another value")
    node[path[-1]] = value
    assert (diff := pin_difference(pinned, changed)) is not None
    assert diff.startswith("$." + ".".join(path)), diff


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
