"""Regression pin of the proxy fine-tune script `m05/proxy_transfer_check.py` (TASKS 82, 28 Oct 2026), written before its fine-tune gains
the early-stopped recipes of the anchor-price follow-up: the modes it has must give the same record and table to the bit.

Inputs, all fixed: the frozen corpus (`tests/data/rungC_pin_corpus/`, copied into the test's folder, since the script writes its
least-squares target cache beside the molecules) and the transfer pin's proxy model (`tests/data/rungC_cc_pin_model.pt`), saved under a
trainer's name beside a one-line record. The frozen set's four molecules with analytic labels: benzene and phenanthrene as the reservoir,
the other two as the read set; k = 1 (two draws), four steps, every fine-tune mode but scratch (the pin model has no training record to
take a recipe from). The run goes through `tests/cc_pin_runner.py`, which replaces only the model-registry gate.

    python tests/test_proxy_transfer_check_regression.py --write-golden [SCRIPT]       # with the script as it is before a change
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pin_tools import (
    DATA,
    M05,
    PIN_CORPUS,
    environment,
    first_difference,
    require_frozen_corpus,
    require_pinning_environment,
    single_thread_env,
    stable,
)

SCRIPT = M05 / "proxy_transfer_check.py"
RUNNER = Path(__file__).with_name("cc_pin_runner.py")
MODEL = DATA / "rungC_cc_pin_model.pt"
GOLDEN = DATA / "proxy_transfer_check_golden.json"
RESERVOIR = ("A_8448043181", "A_541c53d1a5")                    # benzene, phenanthrene
READ = ("A_e72997e726", "A_fdc27f1bd1")
SWITCHES = ["--k", "1", "--subsets", "2", "--modes", "head_l2,head,head_all", "--steps", "4", "--head-l2", "0.1", "--threads", "1",
            "--allow-any-model"]
VOLATILE = frozenset({"date", "seconds", "model", "reservoir_file", "read_file"})


def argv_for(work: Path) -> list[str]:
    """The script's command line, with the corpus, the model under a trainer's name, its record and the id files written into `work`."""
    shutil.copytree(PIN_CORPUS / "molecules", work / "corpus" / "molecules")
    shutil.copyfile(MODEL, work / "pin_model_n10_seed0.pt")
    (work / "pin.json").write_text(json.dumps({"provenance": {"command": "the transfer pin's model (tests/data)"}}), encoding="utf-8")
    (work / "reservoir.txt").write_text("\n".join(RESERVOIR) + "\n", encoding="utf-8")
    (work / "read.txt").write_text("\n".join(READ) + "\n", encoding="utf-8")
    return [str(work / "corpus" / "molecules"), str(work / "pin_model_n10_seed0.pt"), str(work / "out"),
            "--reservoir", str(work / "reservoir.txt"), "--read", str(work / "read.txt"), *SWITCHES]


def run_check(work: Path, script: Path = SCRIPT, extra: tuple[str, ...] = ()) -> dict:
    """Run the script once in a fresh single-threaded process; its stable record and table."""
    subprocess.run([sys.executable, str(RUNNER), str(script), *argv_for(work), *extra], env=single_thread_env(), stdin=subprocess.DEVNULL,
                   check=True)
    record = stable(json.loads((work / "out.json").read_text(encoding="utf-8")), VOLATILE)
    table = (work / "out.md").read_text(encoding="utf-8")
    table = re.sub(r"Base `[^`]*`", "Base `<model>`", table)
    table = re.sub(r"\| \d+ \|\n", "| <s> |\n", table)
    return {"record": record, "table": table}


def test_the_pinned_fine_tunes_are_unchanged(tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the script")
    require_frozen_corpus()
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    assert (diff := first_difference(golden["run"], run_check(tmp_path))) is None, diff


def test_the_pin_covers_every_mode_it_names():
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    draws = json.loads(GOLDEN.read_text(encoding="utf-8"))["run"]["record"]["draws"]
    assert len(draws) == 2 and all(sorted(d["modes"]) == ["head", "head_all", "head_l2"] for d in draws)


def test_the_early_stopped_modes_run_on_the_pin(tmp_path):
    """The follow-up's modes beside head_all on the pin's whole reservoir (k 2, one draw): one fit and one validation molecule, at most
    three epochs; the body's last block moves the prediction."""
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    require_frozen_corpus()
    run = run_check(tmp_path, extra=("--k", "2", "--subsets", "1", "--modes", "head_all,head_all_es,body1_es", "--es-max-epochs", "3",
                                     "--es-patience", "1"))
    rec = run["record"]
    assert rec["early_stop"] == {"max_epochs": 3, "val": 0.15, "patience": 1} and len(rec["draws"]) == 1
    modes = rec["draws"][0]["modes"]
    assert "best_epoch" not in modes["head_all"]
    for m in ("head_all_es", "body1_es"):
        e = modes[m]
        assert 1 <= e["best_epoch"] <= e["epochs_run"] <= 3 and (e["n_fit"], e["n_val"]) == (1, 1) and e["final_loss"] > 0
    assert modes["body1_es"]["read"]["family_mean"] != modes["head_all_es"]["read"]["family_mean"]


if __name__ == "__main__":
    if sys.argv[1:2] != ["--write-golden"]:
        raise SystemExit(__doc__)
    import tempfile

    script = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else SCRIPT
    with tempfile.TemporaryDirectory() as tmp:
        run = run_check(Path(tmp), script)
    tmp_golden = GOLDEN.with_name(GOLDEN.name + ".tmp")
    tmp_golden.write_text(json.dumps({"environment": environment(), "script": str(script.relative_to(M05.parents[2])), "run": run},
                                     indent=1) + "\n", encoding="utf-8")
    tmp_golden.replace(GOLDEN)
    print(f"wrote {GOLDEN}")
