"""A live certificate of measurement networks is what it was before decision 66 — the whole record and the whole page.

`tests/data/m08_live_certificate_pin.json` holds the certificate `tests/live_certificate_pin.build` gives with master's `m08` of
17 Nov 2026 (7ed3058e, the last commit before the release networks' branch), rewritten for the wording changes of the demo review
of 18 Nov (the hold-out descriptions, the read-outs' definition, the coupled-cluster note, the caveat once) and for the baseline
column on PAHdb's 6-31G* factors of 19 Nov (TASKS 247; the commit is in the file): v1.3's tracked records, the frozen corpus's
benzene, a zero correction. This checkout must give the same record, key for key, and the same page, byte for byte. It replaces a
comparison made by hand (two sha256 in a commit message). Numbers come out of an eigensolver, so the pin holds in the environment it
was written in (recorded in it): elsewhere it skips in CI and fails locally, as the trainer's pin does.

    python tests/test_m08_live_certificate_pin.py --write-golden [PLAN FOLDER OF THE CHECKOUT WHOSE m08 WRITES IT]   # after a deliberate change
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

from live_certificate_pin import build
from pin_tools import DATA, PIN_CORPUS, environment, first_difference, require_frozen_corpus, require_pinning_environment

GOLDEN = DATA / "m08_live_certificate_pin.json"


def certificate(plan: Path, work: Path) -> dict:
    """The pinned certificate by the `m08` of the checkout at `plan`; no checkpoint is opened."""
    sys.path.insert(0, str(plan / "modules" / "08_industry_synthesis"))
    m08 = {name: importlib.import_module(f"m08.{name}") for name in ("accuracy", "live_certificate", "pipeline")}
    m08["pipeline"].train_ids = lambda models: set()                          # v1.3's checkpoints are not in git; benzene is not among their ids
    return build(m08, PIN_CORPUS / "molecules" / "A_8448043181", work)


def test_a_measurement_certificate_is_the_pinned_record_and_page(tmp_path, monkeypatch):
    pytest.importorskip("torch")
    require_frozen_corpus()
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    plan = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(plan / "modules" / "08_industry_synthesis"))
    from m08 import pipeline as P

    monkeypatch.setattr(P, "train_ids", P.train_ids)                           # `certificate` replaces it; put it back afterwards
    got = certificate(plan, tmp_path)
    assert (diff := first_difference(golden["record"], got["record"])) is None, diff
    assert got["page"] == golden["page"]
    assert "measured on molecules the network never saw" in got["record"]["statement"] and "release" not in got["page"]
    assert got["record"]["molecule"]["seen"]["role"] == "a" and set(got["record"]["network"]) == {"name", "version", "models", "predicts"}


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or sys.argv[1] != "--write-golden":
        sys.exit(__doc__)
    import subprocess
    import tempfile

    plan = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else Path(__file__).resolve().parents[1]
    commit = subprocess.run(["git", "-C", str(plan), "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp:
        pin = {"environment": environment(), "written_by_m08_at_commit": commit} | certificate(plan, Path(tmp))
    GOLDEN.write_text(json.dumps(pin, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"pinned the live certificate with the m08 of {plan} to {GOLDEN}")
