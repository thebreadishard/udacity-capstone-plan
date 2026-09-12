"""Per-fragment checkpointing for pyscf-forge's LNO-CCSD(T) — plan 05 engine layer 3 (2026-09-12).

Why: pyscf-forge 1.1.1 runs the LNO fragments in a plain loop (`pyscf/lno/lno.py::kernel`) and keeps the
per-fragment results only in memory; its own TODO list says "[ ] chkfile / restart". On 2026-09-12 the
naphthalene cc-pVTZ xtight timing (24 fragments, ~2 h each at the largest) was lost 3 h 35 in when the host
tore the WSL VM down. With this layer a killed run loses only the fragment in progress.

How: a subclass whose `impurity_solve` — called once per fragment, in order, by the upstream kernel — writes
each fragment's three energies (MP2, CCSD, CCSD(T) correlation contributions, with the MP2/CCSD spin
components that `_post_proc` reads) to a JSON file immediately, and on a resumed run returns the stored
tuple for fragments already done without solving them. Nothing upstream is modified; the fragment
construction (`make_las`) still runs for restored fragments (seconds to a minute each), the expensive
CCSD(T) solve does not. Exactness requires that the resumed run build the *same* fragments: same
molecule, basis, thresholds, frozen core and — because Pipek–Mezey localisation is iterative — the same
localised orbitals, which the caller must save on the first run and reload on resume (`save_lo` /
`load_lo` below). The `meta` dictionary guards against mixing runs.

Candidate upstream contribution (see GoalGathering/notes/Software_Changes_Ledger.md): the same hook inside
`lno.py::kernel` with a `chkfile` attribute, which is what their TODO asks for.
"""
import json
import os
import time
from datetime import datetime

import numpy as np
from pyscf import lib
from pyscf.lno import LNOCCSD_T


class FragmentCheckpointError(RuntimeError):
    pass


def save_lo(path, lo_coeff, frozen, extra=None):
    np.savez(path, lo_coeff=np.asarray(lo_coeff), frozen=np.asarray(frozen if frozen is not None else -1),
             saved=str(datetime.now()), **(extra or {}))


def load_lo(path):
    z = np.load(path, allow_pickle=False)
    frozen = z["frozen"]
    frozen = None if frozen.ndim == 0 and int(frozen) == -1 else (int(frozen) if frozen.ndim == 0 else frozen.tolist())
    return z["lo_coeff"], frozen


class CheckpointedLNOCCSD_T(LNOCCSD_T):
    """LNOCCSD_T with a per-fragment JSON checkpoint.

    Set `ckpt_path` (file) and `ckpt_meta` (dict) before `kernel()`; call `ckpt_load()` to read an existing
    checkpoint (returns the number of restored fragments). `ckpt_abort_after = n` raises after `n` *newly*
    computed fragments have been written — for testing the resume path only.
    """
    ckpt_path = None
    ckpt_meta = None
    ckpt_abort_after = None

    def ckpt_load(self):
        self._ckpt_i = 0
        self._ckpt_new = 0
        self._ckpt_done = {}
        if self.ckpt_path and os.path.exists(self.ckpt_path):
            d = json.load(open(self.ckpt_path, encoding="utf-8"))
            if d.get("meta") != self.ckpt_meta:
                raise FragmentCheckpointError(f"checkpoint {self.ckpt_path} belongs to another calculation: "
                                              f"{d.get('meta')} != {self.ckpt_meta}")
            self._ckpt_done = {int(k): v for k, v in d["fragments"].items()}
        return len(self._ckpt_done)

    def _ckpt_write(self):
        tmp = self.ckpt_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"meta": self.ckpt_meta, "written": str(datetime.now()),
                       "fragments": {str(k): v for k, v in sorted(self._ckpt_done.items())}}, f, indent=1)
        os.replace(tmp, self.ckpt_path)

    def kernel(self, eris=None):
        if not hasattr(self, "_ckpt_done"):
            self.ckpt_load()
        return super().kernel(eris)

    def impurity_solve(self, mf, mo_coeff, uocc_loc, eris, frozen=None, log=None):
        i = self._ckpt_i
        self._ckpt_i += 1
        if i in self._ckpt_done:
            r = self._ckpt_done[i]
            ept2 = lib.tag_array(r["e_pt2"], spin_comp=np.asarray(r["pt2_spin_comp"], dtype=float))
            ecc = lib.tag_array(r["e_cc"], spin_comp=np.asarray(r["cc_spin_comp"], dtype=float))
            msg = (f"E_corr(MP2) = {r['e_pt2']:.15g}  E_corr(CCSD) = {r['e_cc']:.15g}  "
                   f"E_corr(CCSD(T)) = {r['e_cc_t']:.15g}  [restored from checkpoint; solved in {r['t_s']:.0f} s on {r['written'][:16]}]")
            return (ept2, ecc, r["e_cc_t"]), msg
        t0 = time.time()
        (ept2, ecc, ecc_t), msg = super().impurity_solve(mf, mo_coeff, uocc_loc, eris, frozen=frozen, log=log)
        self._ckpt_done[i] = {
            "e_pt2": float(ept2), "e_cc": float(ecc), "e_cc_t": float(ecc_t),
            "pt2_spin_comp": [float(x) for x in np.asarray(getattr(ept2, "spin_comp", (0.0, 0.0))).ravel()],
            "cc_spin_comp": [float(x) for x in np.asarray(getattr(ecc, "spin_comp", (0.0, 0.0))).ravel()],
            "n_mo_frag": int(np.asarray(mo_coeff).shape[1]), "t_s": round(time.time() - t0, 1), "written": str(datetime.now()),
        }
        self._ckpt_new += 1
        if self.ckpt_path:
            self._ckpt_write()
        if self.ckpt_abort_after is not None and self._ckpt_new >= int(self.ckpt_abort_after):
            raise FragmentCheckpointError(f"test abort after {self._ckpt_new} newly computed fragment(s); checkpoint written to {self.ckpt_path}")
        return (ept2, ecc, ecc_t), msg

    @property
    def ckpt_summary(self):
        d = getattr(self, "_ckpt_done", {})
        return {"fragments_done": len(d), "fragments_new_this_run": getattr(self, "_ckpt_new", 0),
                "t_fragments_sum_s": round(sum(v["t_s"] for v in d.values()), 1)}
