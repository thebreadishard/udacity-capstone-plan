"""Paper D's deposit tooling (3 Oct 2026). zenodo_deposit: the token comes from the environment or the git-ignored .env and is never echoed; the metadata
file is validated; no 'publish' command exists. build_anchor_release: only VALID run directories enter, the manifest carries a SHA-256 per file, the archive
holds the same files plus a README, and --check detects a changed file. No network in any test."""
import json
import shutil
import sys
import tarfile
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import build_anchor_release as BR  # noqa: E402
import zenodo_deposit as ZD  # noqa: E402

BENZENE = PLAN / "probes" / "results_m1" / "e8_benzene_ccpvdz_dip_2026-10-03"


def test_token_from_env_file_only_when_env_is_empty(tmp_path, monkeypatch):
    monkeypatch.delenv("ZENODO_SANDBOX_TOKEN", raising=False)
    monkeypatch.setattr(ZD, "REPO", tmp_path)
    (tmp_path / ".env").write_text("OTHER=1\nZENODO_SANDBOX_TOKEN=\"abc123\"\n", encoding="utf-8")
    assert ZD.read_token(sandbox=True) == "abc123"
    monkeypatch.setenv("ZENODO_SANDBOX_TOKEN", "fromenv")
    assert ZD.read_token(sandbox=True) == "fromenv"
    monkeypatch.delenv("ZENODO_SANDBOX_TOKEN")
    (tmp_path / ".env").write_text("OTHER=1\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        ZD.read_token(sandbox=True)


def test_metadata_file_is_valid_and_no_publish_command():
    md = ZD.load_metadata(PLAN / "tools" / "zenodo" / "metadata_paper_D.json")
    m = md["metadata"]
    assert m["upload_type"] == "dataset" and m["license"] == "cc-by-4.0" and m["access_right"] == "open"
    assert [c["name"] for c in m["creators"]] == ["Petrignani, Frederic", "Petrignani, Annemieke"]
    assert m.get("prereserve_doi") is True
    src = (PLAN / "tools" / "zenodo_deposit.py").read_text(encoding="utf-8")
    assert "actions/publish" not in src


@pytest.mark.skipif(not (BENZENE / "hessian_ccsd_t.npz").exists(), reason="benzene anchor not present")
def test_anchor_release_manifest_archive_and_check(tmp_path, monkeypatch):
    results = tmp_path / "results"
    results.mkdir()
    shutil.copytree(BENZENE, results / "e8_benzene_ccpvdz_dip_2026-10-03", ignore=shutil.ignore_patterns("grad_*", "ener_*", "dip_*"))
    (results / "e8_x_invalid").mkdir()
    (results / "e8_x_invalid" / "e8_fd.log").write_text("E8 FD Hessian: 3 atoms, cc-pvdz, frozen 1 (derived), step 0.005 bohr, 18 displacements\n",
                                                         encoding="utf-8")
    monkeypatch.setattr(BR, "ANCHORS", [("benzene", "e8_benzene_ccpvdz_dip_2026-10-03", "benzene", "A_8448043181"),
                                        ("x", "e8_x_invalid", "x", "X"), ("y", "e8_missing", "y", "Y")])
    out = tmp_path / "release"
    m = BR.build("anchors_test", out_dir=out, results=results)
    assert m["n_anchors"] == 1 and len(m["left_out"]) == 2
    e = m["anchors"][0]
    assert e["atoms"] == 12 and e["frozen_core"] == 6 and 0 < e["fd_asymmetry_au"] < 1e-3
    names = {f["path"] for f in e["files"]}
    assert "benzene/hessian_ccsd_t.npz" in names and "benzene/e8_fd.log" in names
    with tarfile.open(out / "anchors_test.tar.gz") as tar:
        members = set(tar.getnames())
    assert "anchors_test/benzene/hessian_ccsd_t.npz" in members and "anchors_test/README.md" in members
    assert BR.check("anchors_test", out_dir=out, results=results) == 0
    (results / "e8_benzene_ccpvdz_dip_2026-10-03" / "e8_fd.log").write_text("changed", encoding="utf-8")
    assert BR.check("anchors_test", out_dir=out, results=results) == 1
    man = json.load(open(out / "anchors_test_manifest.json", encoding="utf-8"))
    assert man["archive_sha256"] == BR.sha256(out / "anchors_test.tar.gz")
