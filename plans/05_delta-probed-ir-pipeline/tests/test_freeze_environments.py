"""tools/freeze_environments.py (3 Oct 2026): the listing is normalised (comments, blanks, editable and local-file installs dropped; sorted), the
header is ignored by the comparison, an unreachable environment is skipped and never fails the check, a changed package makes --check fail, and
module 05's requirements.txt follows the Windows listing."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import freeze_environments as FE  # noqa: E402


def test_normalise_drops_noise_and_sorts():
    raw = "# a comment\nzeta==1.0\n\n-e git+https://x/y.git#egg=y\nalpha==2.0\nlocalpkg @ file:///C:/tmp/x.whl\nBeta==3.0\n"
    assert FE.normalise(raw) == ["alpha==2.0", "Beta==3.0", "zeta==1.0"]


def test_local_installs_survive_as_header_comments():
    raw = "alpha==2.0\n-e git+https://x/pyscf.git@t3#egg=pyscf\nlocalpkg @ file:///C:/tmp/x.whl\n"
    assert FE.locals_of(raw) == ["-e git+https://x/pyscf.git@t3#egg=pyscf", "localpkg @ file:///C:/tmp/x.whl"]
    assert FE.normalise(raw) == ["alpha==2.0"]


def test_header_is_not_compared():
    a = "# environment: x\n# frozen: 2026-10-03 17:00\nalpha==2.0\n"
    b = "# environment: x\n# frozen: 2026-10-04 09:00\nalpha==2.0\n"
    assert FE.body_of(a) == FE.body_of(b) == ["alpha==2.0"]


def test_check_skips_unreachable_and_fails_on_drift(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(FE, "ENV_DIR", tmp_path / "environments")
    monkeypatch.setattr(FE, "M05_REQ", tmp_path / "m05_requirements.txt")
    monkeypatch.setattr(FE, "ENVIRONMENTS", {"fake": ("a test env", ["fake-list"], ["fake-ver"]), "gone": ("absent", ["none"], ["none"])})
    state = {"pkgs": "alpha==2.0\nbeta==1.0\n"}

    def fake_run(cmd, timeout=300):
        if cmd == ["fake-list"]:
            return state["pkgs"]
        if cmd == ["fake-ver"]:
            return "Python 3.14.6"
        return None
    monkeypatch.setattr(FE, "run", fake_run)
    assert FE.main([]) == 0
    out = capsys.readouterr().out
    assert "skipped: gone" in out and "fake (2 packages" in out
    assert (tmp_path / "environments" / "fake.txt").read_text(encoding="utf-8").endswith("alpha==2.0\nbeta==1.0\n")
    assert FE.main(["--check"]) == 0
    state["pkgs"] = "alpha==2.1\nbeta==1.0\n"
    assert FE.main(["--check"]) == 1
    assert "STALE: fake" in capsys.readouterr().err


def test_module05_requirements_follow_the_windows_listing(tmp_path, monkeypatch):
    monkeypatch.setattr(FE, "ENV_DIR", tmp_path / "environments")
    monkeypatch.setattr(FE, "M05_REQ", tmp_path / "requirements.txt")
    monkeypatch.setattr(FE, "ENVIRONMENTS", {"windows-python314": ("w", ["l"], ["v"])})
    monkeypatch.setattr(FE, "run", lambda cmd, timeout=300: "torch==2.14.0+cpu\nrdkit==2026.3.6\ngeometric==1.1.1\n" if cmd == ["l"] else "Python 3.14.6")
    assert FE.main([]) == 0
    req = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
    assert req.startswith("# Module 05") and FE.body_of(req) == ["geometric==1.1.1", "rdkit==2026.3.6", "torch==2.14.0+cpu"]
    assert FE.main(["--check"]) == 0


@pytest.mark.skipif(not (PLAN / "environments" / "windows-python314.txt").exists(), reason="no committed listings")
def test_committed_windows_listing_names_the_probe_dependencies():
    body = FE.body_of((PLAN / "environments" / "windows-python314.txt").read_text(encoding="utf-8"))
    names = {ln.split("==")[0].lower() for ln in body}
    assert {"torch", "rdkit", "geometric", "numpy", "scipy"} <= names
