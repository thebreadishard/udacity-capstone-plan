"""Read-outs of the follow-up records in `out/` that the notebook's section 12 and the report's Addendum 6 quote.

One implementation for both readers: `notebook/make_notebook.py` fills section 12's markdown from these functions when it builds, and
`make_summary.py` writes the report's numbers from the same calls. A reader returns None when its record is absent, so the notebook can say
that a run is still to come; the report requires every record (`make_summary.required`).
"""
import csv
import json
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np

MODULE = Path(__file__).resolve().parents[1]
OUT = MODULE / "out"
MANIFEST = MODULE / "corpus" / "manifest.csv"
FAMILIES = ["ring-ip", "CH-stretch", "CH-oop", "other"]
FAMILY_LINE_CM = 3.0   # decision 53: every family's corrected-ω rms at or under 3 cm⁻¹
CC_ANCHORS = {"A_8448043181": "benzene", "B_8b12a55d3a": "fluorobenzene", "A_6e858b26e5": "pyridine", "A_01f3186607": "naphthalene"}
HINGE_MOLECULES = ["A_fdc27f1bd1", "A_72b86c2331", "A_3100da3761", "A_e72997e726", "A_08dde334d8"]


def record(file_name: str) -> Any:
    """A record of `out/` by its file name, or None when it is absent."""
    path = OUT / file_name
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def seed_mean(name: str, size: int, hold: str = "a", key: str = "coupling_ratio") -> float | None:
    """Seed mean of a rung-C record's read-out at one training size."""
    rec = record(f"{name}.json")
    if rec is None:
        return None
    return float(np.mean([s[hold][key] for s in rec["curve"][str(size)]["per_seed"]]))


def pair_model_mean(name: str, size: int, hold: str = "a", key: str = "coupling_ratio") -> float | None:
    """The rung-B pair model's mean read-out at one training size (its records store the mean, not the seeds)."""
    rec = record(f"{name}.json")
    if rec is None:
        return None
    return float(rec["curve"][str(size)]["B1_mlp"]["mean"][hold][key])


def cc_transfer(prefix: str, column: str, key: str = "coupling_ratio", family: str | None = None) -> dict[str, float] | None:
    """Mean over the three saved models of a leave-one-anchor-out column, per held-out anchor."""
    out: dict[str, list[float]] = {}
    for seed in (0, 1, 2):
        rec = record(f"{prefix}_seed{seed}_2026-10-02.json")
        if rec is None:
            return None
        for held, fold in rec["folds"].items():
            value = fold[column]["freq_rms_by_family"].get(family) if family else fold[column][key]
            out.setdefault(held, []).append(value)
    return {held: float(np.mean(values)) for held, values in out.items()}


def _only_size(rec: dict) -> list[dict]:
    return rec["curve"][next(iter(rec["curve"]))]["per_seed"]


def coverage_mean(tag: str, hold: str = "a", key: str = "coupling_ratio") -> float | None:
    """Seed mean of a coverage record (section 12.3; the record holds one size)."""
    rec = record(f"E7_rungC_coverage_{tag}.json")
    if rec is None:
        return None
    return float(np.mean([s[hold][key] for s in _only_size(rec)]))


def coverage_parent(tag: str, name_prefix: str, hold: str = "a") -> float | None:
    """Seed-mean ratio of the hold-out molecules whose manifest name starts with name_prefix."""
    rec = record(f"E7_rungC_coverage_{tag}.json")
    if rec is None:
        return None
    with MANIFEST.open(encoding="utf-8") as handle:
        names = {row["id"]: row["name"] for row in csv.DictReader(handle)}
    values = [v["coupling_ratio"] for s in _only_size(rec) for i, v in s[hold]["per_molecule"].items()
              if names[i].split("+")[0] == name_prefix and v["coupling_ratio"] is not None]
    return float(np.mean(values)) if values else None


class FamilyRead(NamedTuple):
    per_family: dict[str, float]
    coupling_ratio: float
    best_epochs: list[int | None]
    corrected_freq_rms: float


def family_read(name: str, hold: str = "a") -> FamilyRead | None:
    """Seed means of a record's per-family corrected-ω rms, its coupling ratio, all-mode ω and the best epochs."""
    rec = record(f"{name}.json")
    if rec is None:
        return None
    seeds = _only_size(rec)
    per_family = {f: float(np.mean([s[hold]["diag_rms"][f] for s in seeds if f in s[hold]["diag_rms"]])) for f in FAMILIES}
    return FamilyRead(per_family, float(np.mean([s[hold]["coupling_ratio"] for s in seeds])), [s.get("best_epoch") for s in seeds],
                      float(np.mean([s[hold]["corrected_freq_rms"] for s in seeds])))


def hinge_low_mode_mean(file_name: str) -> float | None:
    """Mean low-mode ('other-low') error of the five hinge molecules in a low-modes record (section 12.5)."""
    rec = record(file_name)
    if rec is None:
        return None
    low = {r["id"]: r["pred"].get("other-low", float("nan")) for r in rec["rows"]}
    return float(np.mean([low[i] for i in HINGE_MOLECULES]))


def matched_pairing_means() -> dict[str, float] | None:
    """Section 12.6's seed means over chain 34's three models on the hold-out (a) molecules with an APT. Notebook cell 86 computes the same
    inline in the kernel; that cell is kept as executed (append-only), so its copy stays."""
    runs = [record(f"E7_rungC_chain34_eval_matched_2026-10-09_seed{s}.json") for s in range(3)]
    if any(r is None for r in runs):
        return None
    keys = ("spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms", "intensity_rel_rms_zero_rule",
            "intensity_rel_rms_matched", "intensity_rel_rms_zero_rule_matched")
    means = {}
    for key in keys:
        per_run = []
        for run in runs:
            with_apt = [v for v in run["a"]["per_molecule"].values() if v.get("spectrum_overlap") is not None]
            per_run.append(np.mean([v[key] for v in with_apt]))
        means[key] = float(np.mean(per_run))
    return means
