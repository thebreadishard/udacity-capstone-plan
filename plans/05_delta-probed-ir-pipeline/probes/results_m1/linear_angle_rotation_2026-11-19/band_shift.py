"""TASKS 287 probe: how far v1.4's bands move at the stored orientation when the linear-angle axis is made invariant (trained on carried)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AROMIR = HERE.parent / "aromir_fix"
sys.path.insert(0, str(AROMIR / "src"))
sys.path.insert(0, str(AROMIR / "scripts"))
sys.path.insert(0, str(HERE))
import invariant_axis  # noqa: E402
import measure_invariance as MI  # noqa: E402
from aromir import release  # noqa: E402
from geometric.internal import LinearAngle  # noqa: E402

CORPUS = Path(sys.argv[1])
loaded = release.load(AROMIR / "src" / "aromir" / "releases" / "v1.4")
ids = MI.corpus_ids(CORPUS / "molecules", CORPUS / "manifest.csv")
stored = {name: MI.stored_molecule(CORPUS / "molecules" / ids[s]) for s, name in MI.MOLECULES}
carried = {name: MI.corrected(loaded, *stored[name]) for name in stored}
original_reset = LinearAngle.reset
LinearAngle.reset = invariant_axis.invariant_reset
fixed = {name: MI.corrected(loaded, *stored[name]) for name in stored}
for name in stored:
    print(f"{name:20s} stored orientation, carried vs invariant axis: {MI.largest_difference([fixed[name]], carried[name]):.3e} cm-1")
