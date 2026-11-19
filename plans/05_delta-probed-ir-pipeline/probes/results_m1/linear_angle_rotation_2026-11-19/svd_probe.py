"""TASKS 287 probe: singular values of B around 3N-6 for the linear-group molecules, carried and with the invariant axis."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import rotation_probe as P

rng = np.random.default_rng(3)


def report(tag):
    for name in ("diphenylacetylene", "benzonitrile", "phenylacetylene", "biphenyl"):
        g = json.loads((P.CORPUS / P.MOLS[name] / "geometry.json").read_text(encoding="utf-8"))
        x = np.asarray(g["coords_bohr"], float)
        x = x - x.mean(0)
        N = len(x)
        rows = []
        for k in range(4):
            R = np.eye(3) if k == 0 else P.random_rotation(rng)
            ic, _vals, B = P.build(g["symbols"], x @ R.T)
            s = np.linalg.svd(B, compute_uv=False)
            n = 3 * N - 6
            rows.append(f"s[{n - 1}]={s[n - 1]:.2e} s[{n}]={s[n] if len(s) > n else 0:.2e} s[{n + 1}]={s[n + 1] if len(s) > n + 1 else 0:.2e}")
        lin = [(p.a, p.b, p.c, p.axis) for p in ic.Internals if isinstance(p, P.LinearAngle)]
        ang = []
        for a, b, c, _ in lin[::2]:
            u, v = x[a] - x[b], x[c] - x[b]
            ang.append(np.degrees(np.arccos(np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v))))
        print(f"[{tag}] {name}: K={B.shape[0]} 3N-6={3 * N - 6} lin angles (deg) {np.round(ang, 4)}")
        for r in rows:
            print("    ", r)


report("carried")
P.LinearAngle.reset = P.invariant_reset
report("fix")
