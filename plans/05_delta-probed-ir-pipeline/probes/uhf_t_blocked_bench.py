"""Peak memory and wall time of the blocked open-shell CCSD(T) gradient on a real cation (software ledger row 52; TASKS 98).

    python probes/uhf_t_blocked_bench.py <geometry.json> <out dir> --charge 1 --spin 1 [--basis cc-pvdz] [--block 16] [--slab-mb 2000]
                                         [--max-memory 10000] [--threads 8] [--dry-run]

UHF, UCCSD (frozen core by the E8 probe's rule), then with `uhf_t_blocked.install()` the explicit (T) lambda and the UCCSD(T) gradient,
as pyscf's grad/test/test_uccsd_t.py calls them. A line '=== (UB) <stage> done' per stage with wall time and the process's peak RSS; pyscf's
own log at level 5 in <out dir>/pyscf.log; the energies, the gradient and the stage table in <out dir>/bench.json. Benzene⁺/cc-pVDZ is
the molecule pyscf's own path could not run (out of memory at 31.5 GB, 30 Sep 2026). --dry-run prints the sizes and the block memory only.
"""
from __future__ import annotations

import argparse
import json
import logging
import resource
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "t_density_kernel"))
from e8_cc_hessian_fd import core_orbital_count  # noqa: E402, RUF100  (pre-commit's pinned ruff flags the import after the path insert)
from library_log import pyscf_mole  # noqa: E402, RUF100

TAG = "UB"


@dataclass(frozen=True)
class Sizes:
    nbf: int
    frozen: int
    occ: tuple[int, int]
    vir: tuple[int, int]


def stamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def peak_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6           # kB on Linux


def sizes(mol, frozen: int) -> Sizes:
    na, nb = mol.nelec
    nmo = mol.nao_nr()
    return Sizes(nmo, frozen, (na - frozen, nb - frozen), (nmo - na, nmo - nb))


def block_memory_gb(s: Sizes, block: int) -> dict[str, float]:
    """One o³·B³ block array, a block step (BLOCK_ARRAYS of them) and γ1's paired sweep (PAIRED_ARRAYS of o³·v·B²), in GB."""
    from uhf_t_blocked import BLOCK_ARRAYS, PAIRED_ARRAYS
    o, v = max(s.occ), max(s.vir)
    return {"per_block_array": o**3 * block**3 * 8 / 1e9, "block_step": BLOCK_ARRAYS * o**3 * block**3 * 8 / 1e9,
            "paired_sweep": PAIRED_ARRAYS * o**3 * v * block**2 * 8 / 1e9, "pyscf_whole_array": o**3 * v**3 * 8 / 1e9}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("geometry", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--charge", type=int, required=True)
    ap.add_argument("--spin", type=int, required=True, help="2S")
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--block", type=int, default=16)
    ap.add_argument("--slab-mb", type=float, default=2000.0)
    ap.add_argument("--max-memory", type=int, default=10000, help="pyscf's max_memory, MB")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.spin < 1:
        raise SystemExit("--spin: an open-shell bench needs 2S ≥ 1")
    g = json.loads(a.geometry.read_text(encoding="utf-8"))
    atom = list(zip(g["symbols"], g["coords_bohr"], strict=True))
    frozen = core_orbital_count(g["symbols"])
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / "pyscf.log", "a", encoding="utf-8") as log:
        mol = pyscf_mole(log, atom=atom, unit="Bohr", basis=a.basis, charge=a.charge, spin=a.spin, max_memory=a.max_memory)
        s = sizes(mol, frozen)
        mem = block_memory_gb(s, a.block)
        print(f"=== ({TAG}) start: {a.geometry.parent.name} charge {a.charge} 2S {a.spin} {a.basis}: {s.nbf} functions, frozen {s.frozen}, "
              f"occ {s.occ}, vir {s.vir}; block {a.block}: {mem['per_block_array']:.2f} GB per block array, block step "
              f"{mem['block_step']:.2f} GB, paired sweep {mem['paired_sweep']:.2f} GB, "
              f"pyscf's whole o³v³ array {mem['pyscf_whole_array']:.1f} GB {stamp()}", flush=True)
        if a.dry_run:
            return 0
        return run(mol, s, a)


def run(mol, s: Sizes, a: argparse.Namespace) -> int:
    import uhf_t_blocked as U
    from pyscf import cc, lib, scf
    from pyscf.cc import uccsd_t_lambda
    from pyscf.grad import uccsd_t as uccsd_t_grad
    lib.num_threads(a.threads)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=f"({TAG}) %(message)s", force=True)
    stages, t0 = [], time.time()

    def done(stage: str, **extra) -> None:
        """wall_s is the time since the run started (the stage's own time is the difference to the stage before)."""
        wall = round(time.time() - t0, 1)
        own = round(wall - (stages[-1]["wall_s"] if stages else 0.0), 1)
        stages.append({"stage": stage, "wall_s": wall, "stage_s": own, "peak_rss_gb": round(peak_gb(), 3), **extra})
        print(f"=== ({TAG}) {stage} done: {own} s ({wall} s since the start), peak RSS {stages[-1]['peak_rss_gb']} GB {stamp()}", flush=True)

    mf = scf.UHF(mol).run(conv_tol=1e-10)
    done("UHF", e=mf.e_tot, converged=bool(mf.converged))
    mycc = cc.UCCSD(mf, frozen=s.frozen).run(conv_tol=1e-9, conv_tol_normt=1e-7)
    done("UCCSD", e=mycc.e_tot, converged=bool(mycc.converged))
    eris = mycc.ao2mo()
    U.install(block=a.block, slab_mb=a.slab_mb)
    e_t = mycc.ccsd_t(eris=eris)
    done("(T) energy", e_t=e_t)
    conv, l1, l2 = uccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-8)
    done("(T) lambda", converged=bool(conv))
    grad = uccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris=eris)
    done("gradient", max_abs=float(np.abs(grad).max()))
    record = {"molecule": str(a.geometry), "charge": a.charge, "spin": a.spin, "basis": a.basis, "sizes": s.__dict__, "block": a.block,
              "slab_mb": a.slab_mb, "max_memory": a.max_memory, "threads": a.threads, "e_uhf": mf.e_tot, "e_uccsd": mycc.e_tot,
              "e_t": e_t, "lambda_converged": bool(conv), "gradient": np.asarray(grad).tolist(), "stages": stages}
    tmp = a.out / "bench.json.tmp"
    tmp.write_text(json.dumps(record, indent=1), encoding="utf-8")
    tmp.replace(a.out / "bench.json")
    print(f"=== ({TAG}) run done: {stages[-1]['wall_s']} s, peak RSS {stages[-1]['peak_rss_gb']} GB {stamp()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
