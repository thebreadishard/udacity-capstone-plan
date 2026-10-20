"""Regression pin of `probes/anchor_deck_rehearsal.py` (decision 58's rehearsal, 20 Oct 2026), written before its clean-code refactor: the three
registered runs of 4 Oct on today's files — pyridine with the analytic B3LYP alone (--no-network), pyridine and naphthalene with chain 34's three
carried models — compared without the date and the seconds.

DECK_PROBES=<folder> selects the folder whose script is tested (default: this checkout's probes; a worktree's for a refactor). The script reads
the corpus and the models from this checkout (--molecules; model paths given in full).

    python tests/test_anchor_deck_rehearsal_regression.py --write-golden      # with the script as it is before a change
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from pin_tools import DATA, PLAN, environment, require_pinning_environment, single_thread_env

GOLDEN = DATA / "anchor_deck_rehearsal_golden.json"
R = PLAN / "probes" / "results_m1"
MODELS = [str(PLAN / "modules" / "05_support_predictor" / "out" / f"E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed{s}.pt") for s in range(3)]
CASES = {"pyridine_no_network": (R / "e8_pyridine_ccpvdz_2026-09-30", "A_6e858b26e5", ["--no-network"]),
         "pyridine_chain34": (R / "e8_pyridine_ccpvdz_2026-09-30", "A_6e858b26e5", ["--models", *MODELS]),
         "naphthalene_chain34": (R / "e8_naphthalene_ccpvdz_tlambda_2026-10-02", "A_01f3186607", ["--models", *MODELS])}
VOLATILE = ("date", "seconds")


def probes() -> Path:
    return Path(os.environ.get("DECK_PROBES", PLAN / "probes")).resolve()


def run_case(case: str, work: Path, folder: Path) -> dict:
    anchor, mol_id, extra = CASES[case]
    prefix = work / case
    argv = [str(folder / "anchor_deck_rehearsal.py"), str(anchor), mol_id, str(prefix), "--threads", "1",
            "--molecules", str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"), *extra]
    subprocess.run([sys.executable, *argv], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True, capture_output=True, cwd=PLAN)
    rec = {k: v for k, v in json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8")).items() if k not in VOLATILE}
    md = Path(f"{prefix}.md").read_text(encoding="utf-8")
    md = re.sub(r"\d{4}-\d\d-\d\d \d\d:\d\d", "<date>", md.replace(str(prefix), "<prefix>"))
    return {"json": json.dumps(rec, sort_keys=True).replace(json.dumps(str(prefix))[1:-1], "<prefix>"), "md": re.sub(r"\b\d+ s\b", "<s> s", md)}


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_rehearsal_is_unchanged(case, tmp_path):
    pytest.importorskip("torch")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the script")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    assert run_case(case, tmp_path, probes()) == golden["cases"][case]


if __name__ == "__main__":
    import tempfile

    if sys.argv[1:] != ["--write-golden"]:
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        pin = {"environment": environment(), "cases": {c: run_case(c, Path(tmp), probes()) for c in sorted(CASES)}}
    GOLDEN.write_text(json.dumps(pin, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned {len(CASES)} cases to {GOLDEN}")
