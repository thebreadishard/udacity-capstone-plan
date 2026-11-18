"""Candidates for the demo's live run (TASKS 152; the user's demo plan of 30 Oct 2026: the supervisor picks a molecule the network has not
seen that computes within half an hour). Each recognisable aromatic of a hand list goes through the pipeline's own checks without computing
anything: admission (`pipeline.admit`: elements, charge, aromaticity, the carried models), seen-ness (`m08.seen`: by canonical SMILES against
the training ids and the hold-outs), the catalogue (`Catalog.find`) and the laptop-time estimate (`m08.runtime`). The table lists every
candidate with its verdict; the short list is the admitted, unseen ones within half an hour.

    python probes/demo_candidates.py [--threads 6] [--out modules/08_industry_synthesis/out/demo_candidates_2026-10-30.md]
"""
from __future__ import annotations

import argparse
import functools
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402
from m08 import runtime as RT  # noqa: E402
from m08 import seen as S  # noqa: E402
from m08.catalog import Catalog  # noqa: E402

OUT = PLAN / "modules" / "08_industry_synthesis" / "out" / "demo_candidates_2026-10-30.md"
CANDIDATES = {   # name: SMILES — small aromatics a spectroscopist recognises, around the half-hour size (≈ 170 basis functions)
    "quinoline": "c1ccc2ncccc2c1", "isoquinoline": "c1ccc2cnccc2c1", "quinoxaline": "c1ccc2nccnc2c1", "quinazoline": "c1ccc2ncncc2c1",
    "cinnoline": "c1ccc2nnccc2c1", "phthalazine": "c1ccc2cnncc2c1", "indole": "c1ccc2[nH]ccc2c1", "benzofuran": "c1ccc2occc2c1",
    "benzothiophene": "c1ccc2sccc2c1", "benzoxazole": "c1ccc2ocnc2c1", "benzothiazole": "c1ccc2scnc2c1", "benzimidazole": "c1ccc2[nH]cnc2c1",
    "indene": "C1C=Cc2ccccc21", "azulene": "c1ccc2cccc2cc1", "1-naphthol": "Oc1cccc2ccccc12", "2-naphthol": "Oc1ccc2ccccc2c1",
    "1-naphthylamine": "Nc1cccc2ccccc12", "1-fluoronaphthalene": "Fc1cccc2ccccc12", "2-fluoronaphthalene": "Fc1ccc2ccccc2c1",
    "1-methylnaphthalene": "Cc1cccc2ccccc12", "2-methylnaphthalene": "Cc1ccc2ccccc2c1", "1-chloronaphthalene": "Clc1cccc2ccccc12",
    "8-hydroxyquinoline": "Oc1cccc2cccnc12", "4-hydroxyquinoline": "Oc1ccnc2ccccc12", "2-methylquinoline": "Cc1ccc2ccccc2n1",
    "1,5-naphthyridine": "c1cnc2cccnc2c1", "1,8-naphthyridine": "c1cnc2ncccc2c1", "4-fluoroquinoline": "Fc1ccnc2ccccc12",
    "5-fluoroindole": "Fc1ccc2[nH]ccc2c1", "benzonitrile": "N#Cc1ccccc1", "phenol": "Oc1ccccc1", "anisole": "COc1ccccc1",
    "styrene": "C=Cc1ccccc1", "phenylacetylene": "C#Cc1ccccc1", "biphenylene": "c1ccc2c(c1)-c1ccccc1-2", "acenaphthylene": "C1=Cc2cccc3cccc1c23",
}


def timing(smiles: str, threads: int, pyscf: str) -> dict:
    """The candidate's laptop time on step 3's pyscf version; where that version has no fit yet, the fitted other version's time,
    labelled as such (`RT.estimate_or_other`); none where no version has one."""
    e = RT.estimate_or_other(smiles, threads, pyscf)
    if e is None:
        return {"functions": None, "minutes": None, "within_half_hour": False, "time_on": f"no pyscf {pyscf} fit yet"}
    on = f"pyscf {e['pyscf']}'s time, not {pyscf}'s (no {pyscf} fit yet)" if e["other_version"] else f"pyscf {pyscf}"
    return {"functions": e["basis_functions"], "minutes": round(e["seconds"] / 60), "within_half_hour": e["within_half_hour"], "time_on": on}


def verdict(name: str, smiles: str, models: tuple[Path, ...], seen: S.Seen, catalog: Catalog, estimate: Callable[[str], dict]) -> dict:
    """One candidate through the checks; a refusal by admission is a verdict, not an error."""
    with tempfile.TemporaryDirectory() as tmp:
        cfg = P.PipelineConfig(name="candidate", out_root=Path(tmp), smiles=smiles, models=models, psi4_python=Path(sys.executable))
        try:
            adm = P.admit(cfg)
        except P.Refused as r:
            return {"name": name, "smiles": smiles, "admitted": False, "reason": "; ".join(r.reasons)}
    row = catalog.find(adm.smiles)
    st = S.status(adm.smiles, seen, row["id"] if row else None)
    t = estimate(adm.smiles)
    return {"name": name, "smiles": adm.smiles, "admitted": True, "atoms": adm.n_atoms, "functions": t["functions"],
            "minutes": t["minutes"], "time_on": t["time_on"], "role": st["role"], "seen": st["text"],
            "short_list": st["role"] in ("unseen", "catalogue") and t["within_half_hour"]}


def markdown(rows: list[dict], threads: int) -> str:
    short = [r for r in rows if r.get("short_list")]
    lines = ["# Demo candidates: unseen by the network, within half an hour (TASKS 152)", "",
             f"Laptop estimates at {threads} threads (`m08.runtime`); seen-ness by canonical SMILES (`m08.seen`). "
             f"Short list: {len(short)} of {len(rows)}.", "",
             "| name | SMILES | atoms | basis functions | est. minutes | estimated on | the network | short list |",
             "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (not r.get("short_list"), r.get("minutes") or 1e9)):
        if r["admitted"]:
            minutes = "—" if r["minutes"] is None else r["minutes"]
            lines.append(f"| {r['name']} | `{r['smiles']}` | {r['atoms']} | {r['functions'] or '—'} | {minutes} | {r['time_on']} | "
                         f"{r['seen']} | {'yes' if r['short_list'] else 'no'} |")
        else:
            lines.append(f"| {r['name']} | `{r['smiles']}` | — | — | — | — | refused: {r['reason']} | no |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--pyscf", default=P.WSL_PYSCF_VERSION, help="step 3's pyscf version: the estimate is fitted on that version's runs")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args(argv)
    models = P.carried_models(P.NK.MEASUREMENT)
    seen, catalog = S.load(models), Catalog()
    estimate = functools.partial(timing, threads=a.threads, pyscf=a.pyscf)
    rows = [verdict(n, s, models, seen, catalog, estimate) for n, s in CANDIDATES.items()]
    text = markdown(rows, a.threads)
    tmp = a.out.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(a.out)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
