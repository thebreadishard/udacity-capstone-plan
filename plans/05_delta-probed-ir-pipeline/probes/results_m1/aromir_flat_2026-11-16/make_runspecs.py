"""Write the four run specs of TASKS 248's evidence: one `aromir spectrum` each, in WSL under a memory cap.

    python make_runspecs.py <plan folder>

The specs differ in the molecule only, so they are written from one template; each is launched by hand, one at a time, with
`python tools/runspec.py launch probes/runspecs/aromir_flat_<name>.json` after `python tools/runspec.py check`.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MOLECULES = {
    "vinylfuran": ("C=Cc1ccoc1", "B_1e0fa2d7f0", 13,
                   "the molecule that ended without a spectrum on 16 Nov (aromir cb01c7c, 4,029 s): a vinyl torsion, label mode -11.95"),
    "methoxypicoline": ("COc1ccc(C)nc1", "B_04f049ae58", 18,
                        "a methyl rotor whose label mode is imaginary (-10.96 analytic, -7.17 measured)"),
    "hydroxy_cf3_pyridine": ("Oc1cncc(C(F)(F)F)c1", "B_0f06474656", 15,
                             "a real, positive soft mode (9.51 analytic, 15.82 measured; a CF3 rotor)"),
    "benzene": ("c1ccccc1", "A_8448043181", 12,
                "no soft mode: to show that nothing moved against aromir cb01c7c's certificate of 16 Nov"),
}
HOURS = {"vinylfuran": 2.0, "methoxypicoline": 3.0, "hydroxy_cf3_pyridine": 5.0, "benzene": 0.7}
THREADS = {"vinylfuran": 8, "methoxypicoline": 8, "hydroxy_cf3_pyridine": 4, "benzene": 4}
"""Since 16 Nov 21:0x a run beside the live training has 4 threads and runs under nice -n 10: the evening's runs on 8
threads took the training from 33 to about 124 s per epoch. The two runs launched before that keep their specs."""


def spec(name: str) -> dict[str, object]:
    smiles, corpus_id, n_atoms, why = MOLECULES[name]
    threads = THREADS[name]
    nice = "nice -n 10 " if threads < 8 else ""  # 8 was the count before the rule
    out = f"probes/results_m1/aromir_flat_2026-11-16/{name}"
    command = (
        f'MSYS_NO_PATHCONV=1 wsl -e bash -c "export OMP_NUM_THREADS={threads} PYTHONUNBUFFERED=1 PYTHONUTF8=1 '
        "PYSCF_TMPDIR=/home/thebreadishard/qc_tmp TMPDIR=/home/thebreadishard/qc_tmp; mkdir -p /home/thebreadishard/qc_tmp; "
        "cd /mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline && echo '=== (AROMIR) start' && "
        "git -C /home/thebreadishard/aromir-src log --oneline -1 && bash probes/wsl_capped.sh 4096 -- " + nice + "/usr/bin/time -f "
        "'(AROMIR) max RSS %M kB, wall %e s' /home/thebreadishard/aromir_dev/bin/aromir spectrum "
        f"'{smiles}' --out {out} --threads {threads} --max-memory-mb 2048; echo '=== (AROMIR) done: {name}'\""
    )
    return {
        "name": f"aromir_flat_{name}",
        "purpose": (
            f"TASKS 248, 16 Nov 2026: `aromir spectrum` end to end on {smiles} ({n_atoms} atoms, corpus {corpus_id}) with the "
            f"rule for flat coordinates (saved optimiser progress, geomeTRIC's Q-Chem-style test after 100 gradients, the step "
            f"off a saddle point sized from its curvature, a flat coordinate printed and named): {why}. Read against the "
            "corpus's B3LYP positions and its label's soft mode (probes/results_m1/aromir_e2e_2026-11-16/"
            "end_to_end_against_corpus_b3lyp.py). In WSL from ~/aromir_dev (the code of ~/aromir-src as checked out at launch, "
            "its commit on the log's second line; pyscf 2.15.0), capped by probes/wsl_capped.sh beside the live training."
        ),
        "host": "laptop",
        "workdir": "probes/results_m1",
        "command": command,
        "sources": [{"local": "probes/wsl_capped.sh"}],
        "progress": {"regex": "\\(AROMIR\\)|aromir|step|saved", "max_gap_minutes": 120,
                     "heartbeat_glob": f"aromir_flat_2026-11-16/{name}/*"},
        "marker_regex": "^=== \\(AROMIR\\) |^KILLED|\\(AROMIR\\) max RSS|^done: |^refused|^failed|^unphysical",
        "end_regex": "^=== \\(AROMIR\\) done: ",
        "threads": threads,
        "estimate": {"hours": HOURS[name], "basis": (
            "16 Nov, aromir on 8 threads beside the training: benzene 559 s, benzonitrile 1,435 s, 3-vinylfuran 4,029 s with "
            "(a run on 4 threads under nice is taken as twice as long) "
            "two optimisations (the second 100 steps) and one Hessian; a second Hessian adds about 23 min for 13 atoms, and "
            "fluorine or 18 atoms more basis functions"
        )},
        "memory": {"peak_gb": 4.0, "basis": (
            "a bound: probes/wsl_capped.sh stops the run at 4096 MB (pyscf max_memory 2048); the three runs of 16 Nov peaked "
            "at 1.89 to 2.44 GB"
        )},
        "resumable": False,
    }


def main() -> None:
    plan = Path(sys.argv[1]).resolve()
    for name in MOLECULES:
        path = plan / "probes" / "runspecs" / f"aromir_flat_{name}.json"
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(spec(name), indent=1) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        print(f"wrote {path.relative_to(plan)}")


if __name__ == "__main__":
    main()
