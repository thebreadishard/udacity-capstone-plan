"""Decision 55 (3 Oct 2026): the model registry. A checkpoint's recipe is read from the checkpoint; the hold-out numbers and commit from the record
beside it; a checkpoint without a reviewed status stops the generator; an unknown status is refused; --check detects a stale registry; the loaders'
guard lets only `carried` models through unless the override is given; and the committed MODELS.md of module 05 is current."""
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


def test_rows_read_recipe_numbers_and_commit(tmp_path):
    p = _fake(tmp_path)
    st = tmp_path / "status.json"
    st.write_text(json.dumps({p.name: {"status": "carried", "chain": "24", "note": "n"}}), encoding="utf-8")
    table, missing = MR.rows(tmp_path, st)
    assert not missing and len(table) == 1
    r = table[0]
    assert r["kind"] == "hybrid" and r["status"] == "carried" and r["chain"] == "24"
    assert "pattern f" in r["recipe"] and "kdiag 0.1 family" in r["recipe"] and "sqm α on" in r["recipe"] and "n 30, seed 0" in r["recipe"]
    assert r["a"] == "0.23 / 2.71" and r["b"] == "0.35 / 3.60" and r["commit"] == "abcdef012" and r["saved"] == "2026-10-03 12:00"
    md = MR.render(table)
    assert md.startswith("# Saved networks") and "`X_2026-10-03_model_n30_seed0.pt`" in md


def test_missing_status_stops_and_bad_status_refused(tmp_path, capsys):
    p = _fake(tmp_path)
    st = tmp_path / "status.json"
    st.write_text("{}", encoding="utf-8")
    assert MR.main(["--out-dir", str(tmp_path), "--status-file", str(st), "--registry", str(tmp_path / "M.md")]) == 1
    assert "no reviewed status" in capsys.readouterr().err
    st.write_text(json.dumps({p.name: {"status": "fine"}}), encoding="utf-8")
    with pytest.raises(ValueError):
        MR.rows(tmp_path, st)


def test_check_detects_a_stale_registry(tmp_path):
    p = _fake(tmp_path)
    st = tmp_path / "status.json"
    st.write_text(json.dumps({p.name: {"status": "smoke"}}), encoding="utf-8")
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
    st.write_text(json.dumps({p.name: {"status": "superseded"}}), encoding="utf-8")
    with pytest.raises(SystemExit):
        MR.require_carried(p, status_file=st)
    assert MR.require_carried(p, allow=True, status_file=st)["status"] == "superseded"
    st.write_text(json.dumps({p.name: {"status": "carried"}}), encoding="utf-8")
    assert MR.require_carried(p, status_file=st)["status"] == "carried"


@pytest.mark.skipif(not (M05 / "out" / "MODELS_STATUS.json").exists(), reason="module 05 out/ not present")
def test_committed_registry_is_current():
    r = subprocess.run([sys.executable, str(M05 / "m05" / "model_registry.py"), "--check"], capture_output=True, text=True, cwd=str(M05), check=False)
    assert r.returncode == 0, r.stderr + r.stdout
