"""Refresh m05/deltah_model.py from the architecture sheet and assert they are identical below the header (22 Sep 2026)."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
SRC = HERE.parents[2] / "GoalGathering" / "architecture" / "51_deltaH_model_pytorch.py"
DST = HERE / "deltah_model.py"
HEADER = DST.read_text(encoding="utf-8").split("\n\n", 1)[0] + "\n\n"
DST.write_text(HEADER + SRC.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
assert DST.read_text(encoding="utf-8").split("\n\n", 1)[1] == SRC.read_text(encoding="utf-8"), "copy differs from the sheet"
print("deltah_model.py refreshed from", SRC.relative_to(HERE.parents[3]))
