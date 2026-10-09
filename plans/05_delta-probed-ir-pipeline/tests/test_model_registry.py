"""Decision 55 (3 Oct 2026): the model registry. A checkpoint's recipe is read from the checkpoint; the hold-out numbers and commit from the record
beside it; a checkpoint without a reviewed status stops the generator; an unknown status is refused; --check detects a stale registry; the loaders'
guard lets only `carried` models through unless the override is given; and the committed registries are current.
Decision 59 (4 Oct 2026): every entry names its network; versions follow the rule (carried → 1.x, experimental → 0.x); checkpoints in sub-folders
are keyed by their relative path; the overview lists one row per network with its current version."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
import model_registry as MR  # noqa: E402

DH = "ΔH-network"


def _fake(out: Path, name="X_2026-10-03", n=30, seed=0, with_record=True):
    ctor = {"aggregation": "sum", "tensor_input": False, "sqm_scale": True, "n_pair_features": 12, "hidden": 256, "n_s": 64, "n_v": 16, "n_blocks": 3}
    args = {"pool_layers": "A,A2,B", "use_analytic": True, "epochs": 200, "patience": 20, "lr": 3e-4, "head": "hybrid"}
    ck = {"state": {}, "ctor": ctor, "args": args, "aux_mode": "both", "kring_weight": 0.3, "kdiag_weight": 0.1, "kdiag_mode": "family", "pattern": "f",
          "aux_target": "projected", "ls_lam": 1e-3, "head": "hybrid", "n": n, "seed": seed,
          "provenance": {"git_commit": "abcdef0123456789", "git_dirty": False}}
    p = out / f"{name}_model_n{n}_seed{seed}.pt"
    torch.save(ck, p)
    if with_record:
        rec = {"date": "2026-10-03 12:00", "curve": {str(n): {"per_seed": [{"a": {"coupling_ratio": 0.2345, "corrected_freq_rms": 2.71},
                                                                           "b": {"coupling_ratio": 0.3456, "corrected_freq_rms": 3.6}}]}}}
        (out / f"{name}.json").write_text(json.dumps(rec), encoding="utf-8")
    return p


def _status(path: Path, entries: dict) -> Path:
    path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    return path


def test_rows_read_recipe_numbers_and_commit(tmp_path):
    p = _fake(tmp_path)
    st = _status(tmp_path / "status.json", {p.name: {"status": "carried", "network": DH, "version": "1.0", "chain": "24", "note": "n"}})
    table, missing = MR.rows(tmp_path, st)
    assert not missing and len(table) == 1
    r = table[0]
    assert r["kind"] == "hybrid" and r["status"] == "carried" and r["chain"] == "24" and r["network"] == DH and r["version"] == "1.0"
    assert "pattern f" in r["recipe"] and "kdiag 0.1 family" in r["recipe"] and "sqm α on" in r["recipe"] and "n 30, seed 0" in r["recipe"]
    assert r["a"] == "0.23 / 2.71" and r["b"] == "0.35 / 3.60" and r["commit"] == "abcdef012" and r["saved"] == "2026-10-03 12:00"
    md = MR.render(table)
    assert md.startswith("# Saved networks") and "`X_2026-10-03_model_n30_seed0.pt`" in md and "| 1.0 |" in md


def test_missing_status_stops_and_bad_status_refused(tmp_path, capsys):
    p = _fake(tmp_path)
    st = _status(tmp_path / "status.json", {})
    assert MR.main(["--out-dir", str(tmp_path), "--status-file", str(st), "--registry", str(tmp_path / "M.md")]) == 1
    assert "no reviewed status" in capsys.readouterr().err
    _status(st, {p.name: {"status": "fine", "network": DH}})
    with pytest.raises(ValueError):
        MR.rows(tmp_path, st)


def test_network_name_and_version_rules(tmp_path):
    """Decision 59: an entry names one of the four networks; carried needs 1.x; experimental may only carry 0.x."""
    p = _fake(tmp_path)
    st = tmp_path / "status.json"
    for bad in ({"status": "carried", "network": "some net", "version": "1.0"},
                {"status": "carried", "network": DH},                                   # carried without a production version
                {"status": "carried", "network": DH, "version": "0.3"},
                {"status": "experimental", "network": DH, "version": "1.2"}):
        _status(st, {p.name: bad})
        with pytest.raises(ValueError):
            MR.rows(tmp_path, st)
    for ok in ({"status": "experimental", "network": "learned order scorer (P2)", "version": "0.2"},
               {"status": "experimental", "network": "candidate generator"},            # a search cell: no number
               {"status": "superseded", "network": DH, "version": "1.0"},
               {"status": "candidate", "network": DH, "chain": "34c"}):
        _status(st, {p.name: ok})
        assert MR.rows(tmp_path, st)[0][0]["status"] == ok["status"]


def test_nested_checkpoints_are_keyed_by_relative_path(tmp_path):
    """Module 06 saves `seed0/model_seed0.pt`; a plain state dict is listed with its parameter count and first tensor."""
    sub = tmp_path / "seed0"
    sub.mkdir()
    torch.save({"tok.weight": torch.zeros(33, 8), "head.weight": torch.zeros(33, 8)}, sub / "model_seed0.pt")
    table, missing = MR.rows(tmp_path, _status(tmp_path / "status.json", {}))
    assert missing == ["seed0/model_seed0.pt"] and table == []
    st = _status(tmp_path / "status.json", {"seed0/model_seed0.pt": {"status": "experimental", "network": "candidate generator", "version": "0.1"}})
    table, missing = MR.rows(tmp_path, st)
    assert not missing and table[0]["model"] == "seed0/model_seed0.pt" and table[0]["kind"] == "state dict"
    assert table[0]["recipe"].startswith("528 parameters in 2 tensors; first tensor tok.weight (33, 8)")


def test_overview_one_row_per_network_with_current_version():
    tables = {"05": [dict(model="a.pt", network=DH, version="1.1", status="carried", chain="34"),
                     dict(model="b.pt", network=DH, version="1.0", status="superseded", chain="24"),
                     dict(model="c.pt", network=DH, version="—", status="smoke", chain="x")],
              "standout": [dict(model="p2.pt", network="learned order scorer (P2)", version="0.1", status="experimental", chain="P2")]}
    md = MR.render_overview(tables)
    rows = [ln for ln in md.splitlines() if ln.startswith("| ")][1:]          # the header row, then one row per network
    assert len(rows) == len(MR.NETWORKS)
    assert "| v1.1 (34; 1 seeds) |" in rows[0] and "v1.0 — superseded (24), 1 seed" in rows[0] and "3: carried 1, superseded 1, smoke 1" in rows[0]
    assert "none in production (0.x)" in rows[2] and "v0.1 — experimental (P2), 1 seed" in rows[2]
    assert "none in production (0.x)" in rows[1] and rows[1].rstrip().endswith("| 0: none |")


def test_check_detects_a_stale_registry(tmp_path):
    p = _fake(tmp_path)
    st = _status(tmp_path / "status.json", {p.name: {"status": "smoke", "network": DH}})
    reg = tmp_path / "M.md"
    args = ["--out-dir", str(tmp_path), "--status-file", str(st), "--registry", str(reg)]
    assert MR.main(args) == 0 and MR.main([*args, "--check"]) == 0
    reg.write_text(reg.read_text(encoding="utf-8") + "x", encoding="utf-8")
    assert MR.main([*args, "--check"]) == 1


def test_require_carried_guard(tmp_path):
    p = _fake(tmp_path)
    st = tmp_path / "status.json"
    with pytest.raises(SystemExit):
        MR.require_carried(p, status_file=st)                                   # no status file: unknown model
    _status(st, {p.name: {"status": "superseded", "network": DH}})
    with pytest.raises(SystemExit):
        MR.require_carried(p, status_file=st)
    assert MR.require_carried(p, allow=True, status_file=st)["status"] == "superseded"
    _status(st, {p.name: {"status": "carried", "network": DH, "version": "1.0"}})
    assert MR.require_carried(p, status_file=st)["status"] == "carried"


def test_status_file_is_found_from_the_checkpoint_path(tmp_path):
    """A loader passes only the checkpoint path; the registry knows which module's status file covers it, keyed by the relative path."""
    sf, key = MR.status_file_for(MR.MODULES["06"]["out"] / "seed0" / "model_seed0.pt")
    assert sf == MR.MODULES["06"]["status"] and key == "seed0/model_seed0.pt"
    sf, key = MR.status_file_for(MR.MODULES["standout"]["out"] / "p1_seed0.pt")
    assert sf == MR.MODULES["standout"]["status"] and key == "p1_seed0.pt"
    with pytest.raises(SystemExit):
        MR.status_file_for(tmp_path / "x.pt")


@pytest.mark.skipif(not (M05 / "out" / "MODELS_STATUS.json").exists() or not any((M05 / "out").glob("*.pt")),
                    reason="module 05 checkpoints not present (CI has the status file but no *.pt; the check is meaningful only beside the checkpoints)")
def test_committed_registries_are_current():
    r = subprocess.run([sys.executable, str(M05 / "m05" / "model_registry.py"), "--check"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=str(M05), check=False)
    assert r.returncode == 0, (r.stderr or "") + (r.stdout or "")


def test_candidate_status_is_listed_but_refused_as_a_base(tmp_path):
    """3 Oct 2026: a checkpoint a registered chain saved but nobody has read is 'candidate' — in the table, never a base for a read."""
    p = _fake(tmp_path)
    st = _status(tmp_path / "status.json", {p.name: {"status": "candidate", "network": DH, "chain": "34"}})
    table, missing = MR.rows(tmp_path, st)
    assert not missing and table[0]["status"] == "candidate"
    with pytest.raises(SystemExit):
        MR.require_carried(p, status_file=st)
    assert MR.require_carried(p, allow=True, status_file=st)["status"] == "candidate"


def test_add_candidates_enters_new_models_and_never_overwrites(tmp_path):
    """8 Oct 2026: a chain script registers its saved models as 'candidate' itself (chain 36's read was refused when that was done by hand)."""
    p0, p1 = _fake(tmp_path, seed=0), _fake(tmp_path, seed=1)
    st = _status(tmp_path / "status.json", {p0.name: {"status": "carried", "network": DH, "version": "1.1", "chain": "34"}})
    with pytest.raises(SystemExit):                                         # a reviewed entry is never overwritten
        MR.add_candidates([p0, p1], "37", "note", DH, status_file=st)
    assert MR.add_candidates([p1], "37", "coverage test", DH, status_file=st) == [p1.name]
    s = json.loads(st.read_text(encoding="utf-8"))
    assert s[p0.name]["status"] == "carried" and s[p1.name] == {"status": "candidate", "network": DH, "version": "", "chain": "37", "note": "coverage test"}
    with pytest.raises(SystemExit):
        MR.require_carried(p1, status_file=st)


def test_add_candidates_with_another_unentered_checkpoint(tmp_path, capsys):
    """9 Oct 2026 (chain 38): entering one set while another checkpoint in the folder has no status stops the rebuild (the guard), but the
    entered candidates stay recorded and the message says so."""
    p0, p1 = _fake(tmp_path, name="A_2026-10-09", seed=0), _fake(tmp_path, name="B_2026-10-09", seed=0)
    st = _status(tmp_path / "status.json", {})
    args = ["--out-dir", str(tmp_path), "--status-file", str(st), "--registry", str(tmp_path / "MODELS.md")]
    assert MR.main([*args, "--add-candidates", str(p0), "--chain", "38"]) == 1
    err = capsys.readouterr().err
    assert p1.name in err and "ARE recorded" in err
    assert json.loads(st.read_text(encoding="utf-8"))[p0.name]["status"] == "candidate"
    assert MR.main([*args, "--add-candidates", str(p1), "--chain", "38"]) == 0

