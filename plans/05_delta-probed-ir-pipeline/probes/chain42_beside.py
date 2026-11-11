"""Chain 42's beside items on set T, without lines (PreRegistration_2026-10-12_Large_PAH_Size_Test.md, 'Reported beside'): per arm, the seed
means (and range) of the four families' diagonal rms, the ring-coupling ratio, the corrected ω rms and the zero rule's ω rms, from the same
per-seed rungC_eval_saved records chain42_read.py reads. The intensity read with the four's field-route APTs is not here: the corpus holds no
APT of set T (each record's `intensity_n` is 0). Writes out/read_chain42_beside.{json,md} under module 05.

    python probes/chain42_beside.py
"""
import json
import os
import tempfile
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
MOD_OUT = PLAN / "modules" / "05_support_predictor" / "out"
ARMS = {"arm 0": "E7_rungC_chain42_arm0", "arm D": "E7_rungC_chain42_armD"}
SEEDS = (0, 1, 2)
FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")
SCALARS = ("coupling_ratio", "corrected_freq_rms", "corrected_freq_rms_zero_rule")


def seed_records(prefix: str) -> list[dict]:
    """The three seeds' evaluation records of one arm; a missing seed stops the read."""
    paths = [MOD_OUT / f"{prefix}_eval_frozenb_seed{s}.json" for s in SEEDS]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise SystemExit(f"missing evaluation records: {', '.join(missing)}")
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def summary(values: list[float]) -> dict:
    return {"mean": float(np.mean(values)), "min": float(np.min(values)), "max": float(np.max(values))}


def arm_beside(records: list[dict]) -> dict:
    """Seed means of the families and scalars on set T; a molecule dropped at evaluation stops the read."""
    for r in records:
        if r["T"].get("dropped"):
            raise SystemExit(f"set T lost {r['T']['dropped']} at evaluation - not read")
    out = {f: summary([r["T"]["diag_rms"][f] for r in records]) for f in FAMILIES}
    out |= {k: summary([r["T"][k] for r in records]) for k in SCALARS}
    return out


def table(beside: dict) -> str:
    rows = ["| quantity | " + " | ".join(beside) + " |", "|---|" + "---|" * len(beside)]
    for key in (*FAMILIES, *SCALARS):
        cells = [f"{v[key]['mean']:.3g} ({v[key]['min']:.3g}–{v[key]['max']:.3g})" for v in beside.values()]
        rows.append(f"| {key} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def write_atomic(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main() -> int:
    beside = {arm: arm_beside(seed_records(prefix)) for arm, prefix in ARMS.items()}
    md = ("# Chain 42 — beside items on set T (no lines): seed mean (seed range), cm⁻¹ except the ratio\n\n" + table(beside) + "\n\n"
          "The intensity read with the four's field-route APTs is not in these records (no APT of set T in the corpus).\n")
    write_atomic(MOD_OUT / "read_chain42_beside.json", json.dumps(beside, indent=1) + "\n")
    write_atomic(MOD_OUT / "read_chain42_beside.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
