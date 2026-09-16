"""Checkpoint layer for pyVPT2 (2026-09-16; own software, Software Changes Ledger row 14).

pyVPT2 runs every displaced-geometry task through `AtomicComputer.compute` (`pyvpt2/task_base.py`), keeping the
AtomicResult only in memory; an interruption (16 Sep 02:32: a Windows Update restart after 9 h of benzene) loses
everything. This module wraps that method without touching the installed package: before a task runs, its
AtomicInput (molecule, model, keywords, driver) is hashed; if `<cache_dir>/<hash>.json` exists the stored
AtomicResult is loaded and the task is skipped; otherwise the task runs and its result is written at once. A restart
therefore costs at most the one task that was running.

Use:   from vpt2_checkpoint import install;  install(cache_dir)   — before pyvpt2.vpt2_from_schema(...)
The cache key does not include the program version, so a cache directory belongs to one environment; name it so.
"""
import hashlib
import json
import logging
import os

log = logging.getLogger("vpt2_checkpoint")
STATS = {"hits": 0, "misses": 0, "dir": None}


def install(cache_dir):
    import pyvpt2.task_base as tb
    from qcelemental.models import AtomicResult
    os.makedirs(cache_dir, exist_ok=True)
    STATS["dir"] = cache_dir
    original = tb.AtomicComputer.compute
    if getattr(original, "_vpt2_checkpoint", False):
        return STATS

    def key_of(self):
        inp = self.plan()
        d = json.loads(inp.json())
        d.pop("id", None); d.pop("extras", None); d.pop("provenance", None)
        # a re-optimised reference geometry differs between runs at the 1e-8 bohr level (measured 16 Sep: 2–9e-9);
        # the displacements are 0.05, so rounding to 1e-6 bohr keeps every task distinct and every rerun identical
        if "molecule" in d and "geometry" in d["molecule"]:
            # "+ 0.0" turns -0.0 into 0.0: a coordinate that is zero by symmetry carries ±1e-10 noise and would otherwise
            # hash as "-0.0" in one run and "0.0" in the next (measured 16 Sep 07:0x: two of seven water tasks missed for this)
            d["molecule"]["geometry"] = [round(float(v), 6) + 0.0 for v in d["molecule"]["geometry"]]
        blob = json.dumps(d, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:24]

    def compute(self, client=None):
        k = key_of(self)
        path = os.path.join(cache_dir, k + ".json")
        if os.path.exists(path):
            res = AtomicResult.parse_file(path)
            # extras["qcvars"] is untyped JSON: psi4 arrays (e.g. CURRENT DIPOLE GRADIENT) come back as lists, and
            # pyVPT2 hands them to psi4's set_variable, which needs arrays (measured 16 Sep: TypeError on the reload)
            qcv = (res.extras or {}).get("qcvars")
            if isinstance(qcv, dict):
                import numpy as np
                for name, v in list(qcv.items()):   # `name`, not `k`: `k` is the cache key logged below
                    if isinstance(v, list):
                        arr = np.asarray(v, dtype=float)
                        if arr.ndim == 1:   # the JSON round trip flattens psi4's matrices; psi4 needs them 2-D again
                            if "HESSIAN" in name:
                                n = int(round(arr.size ** 0.5)); arr = arr.reshape(n, n)
                            elif "GRADIENT" in name:
                                arr = arr.reshape(-1, 3)
                        qcv[name] = arr
            self.result = res
            self.computed = True
            STATS["hits"] += 1
            log.info("vpt2_checkpoint: hit %s", k)
            return
        original(self, client) if client is not None else original(self)
        if getattr(self, "result", None) is not None and getattr(self.result, "success", False):
            tmp = path + ".tmp"
            with open(tmp, "w") as f:
                f.write(self.result.json())
            os.replace(tmp, path)
            STATS["misses"] += 1
            log.info("vpt2_checkpoint: stored %s", k)

    compute._vpt2_checkpoint = True
    tb.AtomicComputer.compute = compute
    return STATS
