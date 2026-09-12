#!/usr/bin/env python
"""Plan-05 engine patch 2 (2026-09-12): pyscf-forge 1.1.1 vs NumPy 2 on the out-of-core DF-ERI path.

pyscf/lno/lnoccsd.py::_cp reads
    return np.array(a, copy=False, order='C')
Under NumPy 2 `copy=False` means "never copy" and raises ValueError when a copy is unavoidable — which it is
when `a` is a slice of an h5py dataset, i.e. exactly when a fragment's Lov block lives on disk because
max_memory was set below its size. Every in-core run passed; the first run with `--max-memory 16000`
(naphthalene cc-pVTZ xtight timing, 2026-09-12 12:36) died in `_make_df_eris` after the SCF. NumPy's own
migration guide prescribes `np.asarray(a, order='C')` (copy only when needed; identical to the NumPy 1.x
meaning of copy=False).

Run with the venv's python:  ~/qc05/bin/python apply_pyscf_forge_numpy2_cp_patch.py
Idempotent; writes the unified diff next to itself. Re-apply after any reinstall of pyscf-forge (as patch 1).
"""
import difflib, io, pathlib, sys
import numpy as np
import pyscf.lno.lnoccsd as lnoccsd

p = pathlib.Path(lnoccsd.__file__)
s = io.open(p, encoding="utf-8").read()
OLD = """def _cp(a):
    return np.array(a, copy=False, order='C')"""
NEW = """def _cp(a):
    # Plan-05 engine patch 2 (2026-09-12): NumPy 2 raises on copy=False when a copy is unavoidable
    # (h5py slices on the out-of-core path); asarray keeps the NumPy 1.x meaning.
    return np.asarray(a, order='C')"""
print(f"numpy {np.__version__}; lnoccsd at {p}")
if NEW in s:
    print("already patched"); sys.exit(0)
if s.count(OLD) != 1:
    print("NOT_APPLIED: expected _cp definition not found exactly once"); sys.exit(1)
new_s = s.replace(OLD, NEW)
diff = difflib.unified_diff(s.splitlines(True), new_s.splitlines(True), "lnoccsd.py (pyscf-forge 1.1.1)", "lnoccsd.py (plan-05 patch 2)")
io.open(pathlib.Path(__file__).with_name("pyscf_forge_1.1.1_lnoccsd_numpy2_cp.patch"), "w", encoding="utf-8").writelines(diff)
io.open(p, "w", encoding="utf-8").write(new_s)
print("patched; diff written")
