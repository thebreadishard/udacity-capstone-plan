"""TASKS 287 probe: v1.4's band spreads (aromir's measure_invariance design, seed 7) with and without the invariant linear-angle axis.

Usage: python network_spreads.py <corpus folder> [fix]. Writes nothing into the release; prints per-molecule spreads.
"""
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AROMIR = HERE.parent / "aromir_fix"
sys.path.insert(0, str(AROMIR / "src"))
sys.path.insert(0, str(AROMIR / "scripts"))
sys.path.insert(0, str(HERE))
import geometric  # noqa: E402
import measure_invariance as MI  # noqa: E402
from aromir import release  # noqa: E402

CORPUS = Path(sys.argv[1])
if "fix" in sys.argv:
    import invariant_axis
    from geometric.internal import LinearAngle
    LinearAngle.reset = invariant_axis.invariant_reset
    print("== invariant linear-angle axis ==")
else:
    print("== carried ==")
import aromir  # noqa: E402

print("aromir from", aromir.__file__, "geomeTRIC", geometric.__version__)
loaded = release.load(AROMIR / "src" / "aromir" / "releases" / "v1.4")
ids = MI.corpus_ids(CORPUS / "molecules", CORPUS / "manifest.csv")
rng = np.random.default_rng(MI.SEED)
with tempfile.TemporaryDirectory() as scratch:
    for smiles, name in MI.MOLECULES:
        found = MI.spreads(loaded, MI.stored_molecule(CORPUS / "molecules" / ids[smiles]), rng, Path(scratch))
        print(f"{name:20s} {ids[smiles]}: rotation {found.rotation:.3e}  mirror {found.mirror_image:.3e}  listings {found.xyz_atom_order:.3e}",
              flush=True)
