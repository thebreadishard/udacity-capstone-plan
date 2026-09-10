#!/usr/bin/env python
"""Plan-05 engine patch 1 (2026-09-10): pyscf-forge 1.1.1 vs pyscf >= 2.14 on the DF vvvv path.

pyscf 2.14.0 gives pyscf.cc.dfccsd._contract_vvvv_t2 the signature
    (mycc, mol, vvL, VVL, t2, out=None, verbose=None)
while pyscf-forge 1.1.1 (and its master as of 2026-09-10) still calls it with six arguments from
pyscf/lno/lnoccsd.py::_DFChemistsERIs._contract_vvvv_t2, so `t2` arrives as None and the run dies with
"AttributeError: 'NoneType' object has no attribute 'shape'". The path is taken only when a fragment's
vvvv block does not fit in memory — every benzene run passed, the first naphthalene fragment of that
size did not (naphthalene cc-pVTZ tight timing, 2026-09-10, 4 h 26 min lost).

Run with the venv's python:  ~/qc05/bin/python apply_pyscf_forge_dfvvvv_patch.py
Idempotent; writes the unified diff next to itself. Mirrors pyscf's own _DFChemistsERIs, which passes
vvL twice for real orbitals.
"""
import difflib, inspect, io, pathlib, sys
import pyscf.lno.lnoccsd as lnoccsd
from pyscf.cc import dfccsd

p = pathlib.Path(lnoccsd.__file__)
s = io.open(p, encoding="utf-8").read()
OLD = """    def _contract_vvvv_t2(self, mycc, t2, direct=False, out=None, verbose=None):
        assert(not direct)
        return dfccsd._contract_vvvv_t2(mycc, self.mol, self.vvL, t2, out, verbose)"""
NEW = """    def _contract_vvvv_t2(self, mycc, t2, direct=False, out=None, verbose=None):
        assert(not direct)
        # Plan-05 engine patch 1 (2026-09-10): pyscf >= 2.14 signature (mycc, mol, vvL, VVL, t2, out,
        # verbose); pyscf-forge 1.1.1 passed six arguments, so t2 arrived as None on the DF vvvv path.
        import inspect as _inspect
        if len(_inspect.signature(dfccsd._contract_vvvv_t2).parameters) >= 7:
            return dfccsd._contract_vvvv_t2(mycc, self.mol, self.vvL, self.vvL, t2, out, verbose)
        return dfccsd._contract_vvvv_t2(mycc, self.mol, self.vvL, t2, out, verbose)"""
nparams = len(inspect.signature(dfccsd._contract_vvvv_t2).parameters)
print(f"pyscf dfccsd._contract_vvvv_t2 has {nparams} parameters; lnoccsd at {p}")
if NEW in s:
    print("already patched"); sys.exit(0)
if s.count(OLD) != 1:
    print("NOT_APPLIED: expected call site not found exactly once"); sys.exit(1)
new_s = s.replace(OLD, NEW)
diff = difflib.unified_diff(s.splitlines(True), new_s.splitlines(True), "lnoccsd.py (pyscf-forge 1.1.1)", "lnoccsd.py (plan-05 patch 1)")
io.open(pathlib.Path(__file__).with_name("pyscf_forge_1.1.1_lnoccsd_dfvvvv_pyscf2.14.patch"), "w", encoding="utf-8", newline="\n").write("".join(diff))
io.open(p, "w", encoding="utf-8", newline="\n").write(new_s)
print("patched")
