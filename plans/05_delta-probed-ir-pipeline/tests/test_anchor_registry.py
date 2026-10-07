"""Anchor registry (7 Oct 2026): one carried entry per molecule; a carried file must be VALID, unchanged and carry H_raw/H_projected; reads take the
carried file or refuse (override named); one read uses one tier. Synthetic files in a temporary plan root — no quantum chemistry."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import anchor_registry as AR  # noqa: E402


def _npz(root: Path, rel: str, status="VALID"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez(p, H_raw=np.eye(3), H_projected=np.eye(3), status=status)
    return p


def _entry(root, rel, mol="A_x", status="carried", tier="DZ", kind="full"):
    return dict(mol_id=mol, name="x", path=rel, level="CCSD(T)/cc-pVDZ", tier=tier, kind=kind, status=status, date="2026-10-07",
                sha16=AR.sha16(root / rel), checks="—", note="—")


def test_one_carried_per_molecule_and_valid_files(tmp_path):
    _npz(tmp_path, "a/h.npz")
    _npz(tmp_path, "b/h.npz")
    _npz(tmp_path, "c/hessian_ccsd_t_IMAGINARY.npz", status="IMAGINARY")
    ok = [_entry(tmp_path, "a/h.npz"), _entry(tmp_path, "b/h.npz", status="superseded")]
    assert AR.check_all(ok, tmp_path) == []
    two = [_entry(tmp_path, "a/h.npz"), _entry(tmp_path, "b/h.npz")]
    assert any("exactly one" in q for q in AR.check_all(two, tmp_path))
    bad = [_entry(tmp_path, "c/hessian_ccsd_t_IMAGINARY.npz")]
    assert any("own verdict" in q for q in AR.check_all(bad, tmp_path))


def test_changed_file_is_caught(tmp_path):
    _npz(tmp_path, "a/h.npz")
    e = _entry(tmp_path, "a/h.npz")
    np.savez(tmp_path / "a/h.npz", H_raw=2 * np.eye(3), H_projected=np.eye(3), status="VALID")
    assert any("changed" in q for q in AR.check_all([e], tmp_path))
    with pytest.raises(SystemExit, match="changed"):
        AR.require_carried_anchor("A_x", tmp_path / "a/h.npz", entries=[e], root=tmp_path)


def test_require_carried_refuses_others_and_names_the_carried_file(tmp_path):
    _npz(tmp_path, "a/h.npz")
    _npz(tmp_path, "b/h.npz")
    entries = [_entry(tmp_path, "a/h.npz"), _entry(tmp_path, "b/h.npz", status="superseded")]
    assert AR.require_carried_anchor("A_x", tmp_path / "a/h.npz", entries=entries, root=tmp_path)["path"] == "a/h.npz"
    with pytest.raises(SystemExit, match="carried version is a/h.npz"):
        AR.require_carried_anchor("A_x", tmp_path / "b/h.npz", entries=entries, root=tmp_path)
    assert AR.require_carried_anchor("A_x", tmp_path / "b/h.npz", allow=True, entries=entries, root=tmp_path) is None
    with pytest.raises(SystemExit, match="registered for A_x"):
        AR.require_carried_anchor("A_y", tmp_path / "a/h.npz", entries=entries, root=tmp_path)


def test_one_tier_per_read(tmp_path):
    a = dict(tier="TZ")
    b = dict(tier="DZ")
    assert AR.require_one_tier({"A": a, "B": dict(tier="TZ")}) == "TZ"
    with pytest.raises(SystemExit, match="several tiers"):
        AR.require_one_tier({"A": a, "B": b})
    assert AR.require_one_tier({"A": a, "B": b}, allow=True) is None


def test_the_project_registry_is_consistent():
    if not AR.STATUS_FILE.exists():
        pytest.skip("no registry")
    entries = json.loads(AR.STATUS_FILE.read_text(encoding="utf-8"))["anchors"]
    present = [e for e in entries if (AR.PLAN / e["path"]).exists()]
    if len(present) < len(entries):
        pytest.skip("anchor files not on this machine (CI)")
    assert AR.check_all(entries) == []


def test_register_promotes_and_supersedes(tmp_path):
    _npz(tmp_path, "a/h.npz")
    _npz(tmp_path, "b/h.npz")
    sf = tmp_path / "S.json"
    AR.save([_entry(tmp_path, "a/h.npz")], sf)
    new = dict(mol_id="A_x", name="x", path="b/h.npz", level="composite", tier="TZ", kind="composite", status="experimental", date="2026-10-08",
               checks="—", note="—")
    out = AR.register(new, promote=True, root=tmp_path, status_file=sf)
    st = {e["path"]: e["status"] for e in out}
    assert st == {"a/h.npz": "superseded", "b/h.npz": "carried"} and "superseded 2026-10-08 by b/h.npz" in out[0]["note"]
    assert AR.load(sf) == out
    with pytest.raises(SystemExit, match="already registered"):
        AR.register(new, root=tmp_path, status_file=sf)
