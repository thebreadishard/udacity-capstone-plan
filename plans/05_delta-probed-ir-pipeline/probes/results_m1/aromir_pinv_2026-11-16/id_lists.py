"""The id lists of the pseudo-inverse re-read (TASKS 236), written beside this file.

- `ids_seleval18.txt`: the selection molecules whose error in the WSL smoke of 16 Nov differs from the trainer's Windows number by
  more than 1e-3 cm-1 (the rule of `v14_seleval_smoke_2026-11-16/peek_seleval18.py`, on the record kept in its `wsl_eval/`).
- `ids_scan_wrong_count.txt`: the corpus molecules where numpy's default cutoff keeps a count other than 3N-6 in the Linux scan.
- `ids_reread.txt`: both lists, the three molecules of the 15 Nov release check and TASKS 230's biphenyl, each id once.

    python id_lists.py <plan folder>
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELEASE_CHECK = ("A_3100da3761", "A_541c53d1a5", "B_0da4a5aea1")   # aromir_release_v1.3_2026-11-15/delta_h_compare.json
ORDER_READ = ("A_fdc27f1bd1", "A_ea73419366")                      # TASKS 230: biphenyl, 1-methylnaphthalene
TOLERANCE_CM = 1e-3


def main() -> None:
    plan = Path(sys.argv[1]).resolve()
    out = plan / "modules" / "05_support_predictor" / "out" / "v14"
    smoke = plan / "probes" / "results_m1" / "v14_seleval_smoke_2026-11-16" / "wsl_eval"
    exploded = json.loads((smoke / "E7_rungC_v14s1a_c00_control_seleval_seed0.json").read_text(encoding="utf-8"))
    trainer = json.loads((out / "E7_rungC_v14s1a_c00_control.json").read_text(encoding="utf-8"))
    trainer_sel = trainer["curve"]["913"]["per_seed"][0]["sel"]["per_molecule"]
    bad = sorted(mol for mol, read in exploded["selall"]["per_molecule"].items()
                 if abs(read["corrected_freq_rms"] - trainer_sel[mol]["corrected_freq_rms"]) > TOLERANCE_CM)
    with (HERE / "b_gap_scan_wsl.tsv").open(encoding="utf-8", newline="") as handle:
        wrong = sorted(row["id"] for row in csv.DictReader(handle, delimiter="\t") if row["kept_by_default"] != row["rank"])
    everything = list(dict.fromkeys([*bad, *RELEASE_CHECK, *ORDER_READ, *wrong]))
    for name, ids in (("ids_seleval18.txt", bad), ("ids_scan_wrong_count.txt", wrong), ("ids_reread.txt", everything)):
        (HERE / name).write_text("\n".join(ids) + "\n", encoding="utf-8")
    print(f"{len(bad)} selection molecules off by more than {TOLERANCE_CM} cm-1 in the WSL smoke; {len(wrong)} corpus molecules with a "
          f"wrong kept count in the scan; {len(set(bad) & set(wrong))} of the {len(bad)} are among those; {len(everything)} ids to re-read")


if __name__ == "__main__":
    main()
