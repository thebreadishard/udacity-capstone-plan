"""tools/upstream_releases.py (11 Oct 2026): pinned versions are read from the environment listings and a newer PyPI release is flagged;
no network in the tests."""
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
from upstream_releases import pinned_versions, summary, version_key  # noqa: E402


def test_pinned_versions_read_both_spellings_of_a_name(tmp_path):
    (tmp_path / "a.txt").write_text("# comment\npyscf==2.14.0\npyscf_forge==1.1.1\nnumpy==2.3.0\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("pyscf==2.13.1\n", encoding="utf-8")
    assert pinned_versions(str(tmp_path)) == {"pyscf": {"2.14.0": ["a.txt"], "2.13.1": ["b.txt"]}, "pyscf-forge": {"1.1.1": ["a.txt"]}}


def test_version_order_is_numeric_and_a_prerelease_sorts_below_its_release():
    assert version_key("2.14.0") > version_key("2.9.1")
    assert version_key("2.15.0rc1") < version_key("2.15.0")


def test_summary_flags_only_a_release_newer_than_every_pin():
    pinned = {"pyscf": {"2.14.0": ["a.txt"]}, "pyscf-forge": {"1.1.1": ["a.txt"]}}
    line, new = summary(pinned, {"pyscf": ("2.14.0", "2026-07-18"), "pyscf-forge": ("1.1.1", "2026-01-01")})
    assert not new and "NEW" not in line
    line, new = summary(pinned, {"pyscf": ("2.15.0", "2026-11-01"), "pyscf-forge": None})
    assert new and "pyscf pinned 2.14.0, PyPI 2.15.0 (2026-11-01) NEW" in line and "pyscf-forge pinned 1.1.1, PyPI unreachable" in line


def test_the_repository_pins_pyscf():
    assert "pyscf" in pinned_versions()
