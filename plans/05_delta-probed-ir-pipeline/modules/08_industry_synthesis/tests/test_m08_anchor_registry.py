"""The certificate's anchored rung quotes the anchor registry (TASKS 20, 14 November 2026).

Before this, a certificate at rung 4 said what a regular expression had found in an evidence page. The registry
(`m05/anchor_registry.py`, decision 62) is the project's own answer to which coupled-cluster Hessian is in force for a molecule, and
it carries the level, the basis tier, the kind, the date, the digest and the checks. These tests pin that the certificate quotes that
entry, that a molecule without one is told apart from a molecule below the anchored rung, and that a rung 4 the registry does not
know says so in the record rather than showing nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08.certify import ANCHOR_REGISTRY, carried_anchor  # noqa: E402

REGISTRY_FIELDS = ("mol_id", "name", "path", "level", "tier", "kind", "status", "date", "sha16", "checks")


def registry() -> list[dict]:
    return json.loads((PLAN / ANCHOR_REGISTRY).read_text(encoding="utf-8"))["anchors"]


def test_the_registry_the_certificate_reads_carries_the_fields_it_quotes() -> None:
    carried = [e for e in registry() if e["status"] == "carried"]
    assert carried, "the registry has no carried anchor; the certificate's anchored rung would have nothing to quote"
    for entry in carried:
        missing = [f for f in REGISTRY_FIELDS if not str(entry.get(f, "")).strip()]
        assert not missing, f"{entry.get('name')} is missing {missing}"


def test_a_molecule_with_an_anchor_gets_its_entry() -> None:
    first = next(e for e in registry() if e["status"] == "carried")
    found = carried_anchor(first["mol_id"], first["name"])
    assert found is not None and found["sha16"] == first["sha16"] and found["level"] == first["level"]


def test_the_name_finds_the_entry_when_the_id_does_not() -> None:
    first = next(e for e in registry() if e["status"] == "carried")
    assert carried_anchor("not_a_molecule_id", first["name"]) == first


def test_a_molecule_without_an_anchor_gets_none() -> None:
    assert carried_anchor("not_a_molecule_id", "not a molecule") is None


def test_a_superseded_entry_is_not_an_anchor() -> None:
    """benzene's cc-pVDZ Hessians are superseded or invalid; only the TZ one is in force."""
    older = [e for e in registry() if e["status"] in ("superseded", "invalid")]
    assert older, "no superseded entry in the registry; this test needs rewriting"
    for entry in older:
        found = carried_anchor(entry["mol_id"], entry["name"])
        assert found is None or found["sha16"] != entry["sha16"]


def test_two_carried_entries_for_one_molecule_are_refused(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The registry allows one carried anchor per molecule; a second is a mistake the certificate must not average over."""
    import m08.certify as C
    from m08 import paths
    twice = {"anchors": [dict(mol_id="X_1", name="x", status="carried", level="l", tier="TZ", kind="full",
                              date="2026-11-14", sha16="0" * 16, checks="—", path="p") for _ in range(2)]}
    (tmp_path / "ANCHORS_STATUS.json").write_text(json.dumps(twice), encoding="utf-8")
    (tmp_path / paths.PLAN_MARKER).write_text("a plan root for this test\n", encoding="utf-8")   # so the resolver reads it live
    monkeypatch.setattr(paths, "PLAN", tmp_path)
    monkeypatch.setattr(C, "ANCHOR_REGISTRY", "ANCHORS_STATUS.json")
    with pytest.raises(ValueError, match="allows one"):
        C.carried_anchor("X_1", "x")
