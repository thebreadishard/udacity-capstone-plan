"""Shared tools of the regression pins (TASKS 72, 16 Oct 2026): the frozen corpus and its record, the environment bit-identity depends on,
and the comparison of JSON trees. The pins themselves are `test_rungC_train_regression.py` and `test_rungC_cc_transfer_regression.py`."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]


HEAVY_PIN_GB = 6.0   # a pin that loads the corpus (and torch) peaks near 2 GB; 4 GB stay for the running jobs to grow into


def free_commit_gb() -> float | None:
    """Memory the system can still commit, in GB (Windows: the commit limit minus the charge; elsewhere MemAvailable); None if unknown."""
    if os.name == "nt":
        import ctypes

        class _Status(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total_phys", ctypes.c_ulonglong),
                        ("avail_phys", ctypes.c_ulonglong), ("total_commit", ctypes.c_ulonglong), ("avail_commit", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong), ("avail_extended", ctypes.c_ulonglong)]
        status = _Status()
        status.length = ctypes.sizeof(_Status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
        return status.avail_commit / 1e9
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1e6
    return None


def require_free_memory(gb: float = HEAVY_PIN_GB) -> None:
    """Skip, with the numbers, a pin that loads the corpus when less than `gb` can be committed: the suite also runs beside the laptop's jobs,
    and on 20 Oct 2026 (19:47) two such pins took the memory a running read and a WSL job needed — both failed."""
    free = free_commit_gb()
    if free is not None and free < gb:
        pytest.skip(f"not run beside the laptop's jobs: {free:.1f} GB can be committed, this pin needs about {gb:g} GB with room for them")
DATA = PLAN / "tests" / "data"
PIN_CORPUS = DATA / "rungC_pin_corpus"
M05 = PLAN / "modules" / "05_support_predictor" / "m05"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin_record() -> dict:
    return json.loads((PIN_CORPUS / "pin_corpus.json").read_text(encoding="utf-8"))


def corpus_changes(root: Path, record: dict) -> list[str]:
    """What differs between the frozen corpus on disk and its record: changed, missing or extra files, extra molecule folders."""
    listed = record["sha256"]
    on_disk = {f"{p.parent.name}/{p.name}": p for p in (root / "molecules").glob("*/*") if p.is_file()}
    changes = [f"{k}: {'missing' if k not in on_disk else 'changed'}" for k, h in listed.items() if k not in on_disk or sha256(on_disk[k]) != h]
    changes += [f"{k}: not in the record" for k in sorted(on_disk.keys() - listed.keys())]
    folders = {p.name for p in (root / "molecules").iterdir() if p.is_dir()}
    changes += [f"{d}/: not in the record" for d in sorted(folders - {m["id"] for m in record["molecules"]})]
    return changes


def environment() -> dict:
    """What bit-identity depends on beyond the code: CI's Linux torch gave other checkpoint bytes than this laptop's (16 Oct 2026)."""
    import platform

    import geometric
    import numpy
    import torch

    return {"system": platform.system(), "python": platform.python_version(), "torch": torch.__version__, "numpy": numpy.__version__,
            "geometric": geometric.__version__}


def environment_mismatch(pinned: dict, here: dict) -> str | None:
    """None where the pin was written; elsewhere the reason bit-identity cannot be expected, naming what differs."""
    differs = {k: (pinned.get(k), here.get(k)) for k in pinned.keys() | here.keys() if pinned.get(k) != here.get(k)}
    return f"bit-identity holds in the pinning environment only; differs: {dict(sorted(differs.items()))}" if differs else None


def require_pinning_environment(golden: dict) -> None:
    """Skip in CI, fail elsewhere, when this is not the environment the golden was written in — an upgrade cannot switch a pin off."""
    if message := environment_mismatch(golden["environment"], environment()):
        if os.environ.get("CI"):
            pytest.skip(message)
        pytest.fail(message + " — re-pin here with the code as it was before the change under test")


def require_frozen_corpus() -> None:
    assert corpus_changes(PIN_CORPUS, pin_record()) == [], "the frozen corpus changed: rebuild it and re-pin with the code before the change"


def single_thread_env() -> dict:
    """Two runs with two torch threads differed by up to 1.4e-6 relative; the BLAS counts must be set before numpy is imported."""
    return os.environ | {v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")} | {"PYTHONUTF8": "1"}


def stable(record, volatile: frozenset[str]):
    """The record without the given fields (wall clock, provenance, temporary paths), at any depth."""
    if isinstance(record, dict):
        return {k: stable(v, volatile) for k, v in record.items() if k not in volatile}
    if isinstance(record, list):
        return [stable(v, volatile) for v in record]
    return record


def first_difference(a, b, path: str = "$") -> str | None:
    """The path of the first entry where two JSON trees differ (NaN equals NaN, as in the serialised record)."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return f"{path}: keys {sorted(a.keys() ^ b.keys())}"
        return next((d for k in a if (d := first_difference(a[k], b[k], f"{path}.{k}"))), None)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} vs {len(b)}"
        return next((d for i, (x, y) in enumerate(zip(a, b, strict=True)) if (d := first_difference(x, y, f"{path}[{i}]"))), None)
    if json.dumps(a) != json.dumps(b):
        return f"{path}: {a!r} vs {b!r}"
    return None


def digest(array) -> str:
    """sha256 of an array's bytes (a torch tensor or anything numpy can hold)."""
    import numpy as np

    if hasattr(array, "detach"):
        array = array.detach().cpu().contiguous().numpy()
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()
