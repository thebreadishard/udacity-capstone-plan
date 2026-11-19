"""TASKS 287 probe: corpus molecules whose geomeTRIC primitives (the carried construction) hold LinearAngle; streaming, geometry only."""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from geometric.internal import LinearAngle, PrimitiveInternalCoordinates
from geometric.molecule import Molecule

BOHR2ANG = 0.529177210903
CORPUS = Path(sys.argv[1])
out = Path(sys.argv[2])
rows = []
for d in sorted((CORPUS / "molecules").iterdir()):
    gp = d / "geometry.json"
    if not gp.is_file():
        continue
    g = json.loads(gp.read_text(encoding="utf-8"))
    M = Molecule()
    M.elem = [s.capitalize() for s in g["symbols"]]
    M.xyzs = [np.asarray(g["coords_bohr"], float) * BOHR2ANG]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    lin = [p for p in ic.Internals if isinstance(p, LinearAngle)]
    analytic = (d / "hessian_b3lyp_analytic.npz").is_file() and (d / "hessian_wb97x_analytic.npz").is_file()
    rows.append((d.name, len(g["symbols"]), len(lin) // 2, analytic))
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "n_atoms", "n_linear_centres", "both_analytic"])
    w.writerows(rows)
n_lin = [r for r in rows if r[2] > 0]
print(f"molecules {len(rows)}; with LinearAngle {len(n_lin)}; of those with both analytic Hessians {sum(r[3] for r in n_lin)}"
      f" (all with both analytic: {sum(r[3] for r in rows)})")
for r in n_lin:
    print("  ", r)
