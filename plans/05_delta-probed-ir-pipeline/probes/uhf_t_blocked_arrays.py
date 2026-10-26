"""How many block arrays the blocked open-shell (T) code (probes/t_density_kernel/uhf_t_blocked.py) holds at once — the counts PR D's memory
rule (pyscf/cc/uccsd_t_blocked.py block_size) rests on. tracemalloc's peak of make_intermediates, gamma1_intermediates and
gamma2_intermediates at block sizes that divide H2O+/aug-cc-pVDZ's alpha virtual count, fitted as peak = base + N·o³B³·8 + M·o³·v·B²·8 bytes.

    python probes/uhf_t_blocked_arrays.py      (WSL, qc05's pyscf; about a minute)
"""
from __future__ import annotations

import sys
import tracemalloc
from collections.abc import Callable
from pathlib import Path

import numpy as np
from pyscf import cc, gto, scf

sys.path.insert(0, str(Path(__file__).resolve().parent / "t_density_kernel"))
import uhf_t_blocked as U

BLOCKS = (4, 6, 9, 12, 18)


def fit(peaks: list[int], o: int, nv: int) -> tuple[float, float, float, float]:
    """(base bytes, N, M, worst residual bytes) of the least-squares fit."""
    x = np.column_stack([np.ones(len(BLOCKS)), [o**3 * b**3 * 8 for b in BLOCKS], [o**3 * nv * b**2 * 8 for b in BLOCKS]])
    coef, *_ = np.linalg.lstsq(x, np.array(peaks, float), rcond=None)
    return coef[0], coef[1], coef[2], float(np.abs(x @ coef - peaks).max())


def traced_peak(call: Callable[[], object]) -> int:
    tracemalloc.start()
    try:
        call()
        return tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()


def main() -> None:
    mol = gto.M(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", charge=1, spin=1, basis="aug-cc-pvdz", verbose=0)
    mycc = cc.UCCSD(scf.UHF(mol).run(conv_tol=1e-10)).run(conv_tol=1e-9, conv_tol_normt=1e-7)
    eris = mycc.ao2mo()
    l1, l2 = mycc.solve_lambda()
    t1, t2 = mycc.t1, mycc.t2
    o, nv = max(mycc.nocc), max(n - k for n, k in zip(mycc.nmo, mycc.nocc, strict=True))
    U.inputs(t1, t2, eris)                  # the eris accessors' first call outside the traced window
    calls = {"lambda": lambda b: U.make_intermediates(mycc, t1, t2, eris, block=b),
             "gamma1": lambda b: U.gamma1_intermediates(mycc, t1, t2, l1, l2, eris, for_grad=True, block=b),
             "gamma2": lambda b: U.gamma2_intermediates(mycc, t1, t2, l1, l2, eris, block=b)}
    print(f"H2O+/aug-cc-pVDZ: o {o}, v {nv}, blocks {BLOCKS}")
    for what, call in calls.items():
        peaks = [traced_peak(lambda b=b, call=call: call(b)) for b in BLOCKS]
        base, n, m, worst = fit(peaks, o, nv)
        print(f"{what}: peaks MB {[round(p / 1e6, 1) for p in peaks]}; base {base / 1e6:.1f} MB, N {n:.1f} of o3B3, M {m:.1f} of o3vB2; "
              f"worst fit residual {worst / 1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
