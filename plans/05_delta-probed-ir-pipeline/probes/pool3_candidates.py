"""P3-3 (decision 54, 3 Oct 2026): the frozen candidate list of pool 3 — batch 1's three axes, deterministic and reviewable.

Families (design note `Design_Note_2026-10-03_Pool_3_Three_Axes.md`):
  aza4    30 aza-four-rings: every single aromatic C–H → N replacement of pyrene and fluoranthene (RDKit, canonical, distinct) as parents, then
          mixed mono-substituted children (layer B's substituent scheme, `corpus/build_manifest.substituted`) round-robin over parents and substituents.
  five    30 five-ring scaffolds: perylene, benzo[a]pyrene, benzo[e]pyrene, benzo[k]fluoranthene, picene, dibenz[a,h]anthracene as parents (formula and
          ring count checked), then mixed children the same way; n_atoms ≤ 40.
  cation  60 radical cations (charge +1, doublet) on scaffolds the pool knows: the parent rows benzene, naphthalene, anthracene, phenanthrene, pyrene,
          fluoranthene, quinoline, pyridine and their finished substituted children (manifest status done), chosen by hash with one substituent class
          at a time; the rows start from the neutral parent's optimised geometry (`corpus/cation_rows.py`).
Per family the first three parents in hash order form hold-out (c) (never trained); the remaining rows carry `curve_rank` (1 = first) so that the
registered curves 0/10/30(/60) are nested subsets of one frozen list. Ids follow the manifest's scheme `<layer>_<sha1(smiles)[:10]>` with layers
`P3` (neutral) and `P3c` (cation; the sha of the neutral SMILES, so the row is traceable to its parent).

Usage (from the plan directory):
  python probes/pool3_candidates.py out/pool3_candidates_2026-10-03.csv            # writes the CSV and its sha256 beside it
  python probes/pool3_candidates.py <csv> --write-manifest                           # appends the rows to corpus/manifest.csv (status pending) — after review
"""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "corpus"))
sys.path.insert(0, str(PLAN / "probes"))
import build_manifest as BM  # noqa: E402
from rdkit import Chem  # noqa: E402
from rdkit.Chem import rdMolDescriptors  # noqa: E402
from rungC_error_map import kind_of  # noqa: E402

FIELDS = ["id", "layer", "name", "smiles", "n_heavy", "n_atoms", "kind", "family", "parent_id", "charge", "multiplicity", "holdout_c", "curve_rank", "reason"]
QUOTA = {"aza4": 30, "five": 30, "cation": 60}
HOLDOUT_PARENTS = 3
MAX_ATOMS = 40
AZA_SOURCES = {"pyrene": BM.BIG_CORES["pyrene"], "fluoranthene": BM.BIG_CORES["fluoranthene"]}
FIVE_PARENTS = {                                                   # formula checked in tests/test_pool3_candidates.py
    "perylene": "c1cc2cccc3c4cccc5cccc(c(c1)c23)c54",
    "benzo[a]pyrene": "c1ccc2c(c1)cc1ccc3cccc4ccc2c1c34",
    "benzo[e]pyrene": "c1ccc2c(c1)c1cccc3ccc4cccc2c4c31",
    "benzo[k]fluoranthene": "c1ccc2cc3c(cc2c1)-c1cccc2cccc-3c12",
    "picene": "c1ccc2c(c1)ccc1c2ccc2c3ccccc3ccc12",
    "dibenz[a,h]anthracene": "c1ccc2c(c1)ccc1cc3c(ccc4ccccc43)cc12",
}
CATION_PARENTS = {"benzene": 15, "naphthalene": 15, "anthracene": 5, "phenanthrene": 5, "pyrene": 5, "fluoranthene": 5, "quinoline": 5, "pyridine": 5}


def sha(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def formula(smi: str) -> str:
    return rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(smi))


def atom_counts(smi: str) -> tuple[int, int]:
    m = Chem.AddHs(Chem.MolFromSmiles(smi))
    return m.GetNumHeavyAtoms(), m.GetNumAtoms()


def aza_parents() -> dict:
    """{name: canonical SMILES} of every distinct single C–H → N replacement of the aza sources."""
    out = {}
    for cname, csmi in AZA_SOURCES.items():
        core = Chem.MolFromSmiles(csmi)
        seen = set()
        for a in core.GetAtoms():
            if a.GetIsAromatic() and a.GetSymbol() == "C" and a.GetTotalNumHs() == 1:
                rw = Chem.RWMol(core)
                at = rw.GetAtomWithIdx(a.GetIdx())
                at.SetAtomicNum(7)
                at.SetNumExplicitHs(0)
                try:
                    Chem.SanitizeMol(rw)
                except Exception:  # noqa: BLE001 — rdkit raises several C++ exception types; any means "not a valid molecule"
                    continue
                smi = Chem.MolToSmiles(rw)
                if smi not in seen:
                    seen.add(smi)
                    out[f"aza-{cname}-{len(seen)}"] = smi
    return out


def children(parents: dict, quota: int, max_atoms: int, exclude: set) -> list[tuple[str, str]]:
    """Mixed mono-substituted children, round-robin over parents (hash order) and substituents (hash order), one product per (parent, substituent)
    chosen by hash, until `quota` rows; canonical, distinct, not in `exclude`, n_atoms ≤ max_atoms."""
    out, seen = [], set(exclude)
    pnames = sorted(parents, key=lambda n: sha(parents[n]))
    snames = sorted(BM.SUBS, key=sha)
    for k in range(len(snames)):
        for pn in pnames:
            if len(out) >= quota:
                return out
            sn = snames[(k + pnames.index(pn)) % len(snames)]
            prods = sorted((BM.canon(s) for s in BM.substituted(parents[pn], BM.SUBS[sn])), key=sha)
            for smi in prods:
                if smi and smi not in seen and atom_counts(smi)[1] <= max_atoms:
                    seen.add(smi)
                    out.append((f"{pn}+{sn}", smi))
                    break
    return out


def manifest_rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def neutral_rows(family: str, parents: dict, exclude: set) -> list[dict]:
    n_par = len(parents)
    rows = [{"name": n, "smiles": s, "parent_id": "", "is_parent": True} for n, s in parents.items()]
    rows += [{"name": n, "smiles": s, "parent_id": "", "is_parent": False} for n, s in children(parents, QUOTA[family] - n_par, MAX_ATOMS, exclude | set(parents.values()))]
    for r in rows:
        r.update(layer="P3", id=f"P3_{sha(r['smiles'])[:10]}", charge=0, multiplicity=1, family=family)
    return rows


def cation_rows(manifest: list[dict]) -> list[dict]:
    """Parents by name (status done) and their finished children `<core>+...` (≤ 2 substituents), one substituent class at a time, by hash."""
    done = [r for r in manifest if r["status"] == "done" and r["layer"] in ("A", "A2", "B")]
    by_name = {r["name"]: r for r in done}
    rows = []
    for core, quota in CATION_PARENTS.items():
        par = by_name.get(core)
        if par is None:
            raise RuntimeError(f"cation parent {core!r} has no finished neutral row")
        rows.append({"name": f"{core}+", "smiles": par["smiles"], "parent_id": par["id"], "is_parent": True, "family": "cation"})
        kids = [r for r in done if r["name"].startswith(core + "+") and r["name"].count("+") <= 2]
        kids.sort(key=lambda r: (r["name"].count("+"), sha(r["id"])))
        taken, used_sub = [], set()
        for pass_ in (0, 1):                                            # first one child per substituent class, then fill
            for r in kids:
                if len(taken) >= quota - 1:
                    break
                sub = r["name"].split("+", 1)[1]
                if r in taken or (pass_ == 0 and sub in used_sub):
                    continue
                taken.append(r)
                used_sub.add(sub)
        rows += [{"name": r["name"] + "+", "smiles": r["smiles"], "parent_id": r["id"], "is_parent": False, "family": "cation"} for r in taken]
    for r in rows:
        r.update(layer="P3c", id=f"P3c_{sha(r['smiles'])[:10]}", charge=1, multiplicity=2)
    return rows


def assign_splits(rows: list[dict]) -> list[dict]:
    """Per family: the first HOLDOUT_PARENTS parents in hash order → hold-out (c); the rest get curve_rank 1.. in hash order."""
    out = []
    for fam in QUOTA:
        fr = [r for r in rows if r["family"] == fam]
        parents = sorted((r for r in fr if r["is_parent"]), key=lambda r: sha(r["id"]))
        held = {r["id"] for r in parents[:HOLDOUT_PARENTS]}
        rest = sorted((r for r in fr if r["id"] not in held), key=lambda r: sha(r["id"]))
        for r in fr:
            r["holdout_c"] = int(r["id"] in held)
            r["curve_rank"] = 0 if r["id"] in held else 1 + [x["id"] for x in rest].index(r["id"])
        out += fr
    return out


def build(manifest_path: Path) -> list[dict]:
    manifest = manifest_rows(manifest_path)
    known = {r["smiles"] for r in manifest if r["smiles"]}
    rows = neutral_rows("aza4", aza_parents(), known) + neutral_rows("five", FIVE_PARENTS, known) + cation_rows(manifest)
    rows = assign_splits(rows)
    for r in rows:
        nh, na = atom_counts(r["smiles"])
        k = kind_of(r["smiles"])
        r.update(n_heavy=nh, n_atoms=na, kind=k["kind"],
                 reason={"aza4": "nitrogen in a four-ring (Q2)", "five": "five rings (Q3)", "cation": "charge axis (Q1)"}[r["family"]]
                 + ("; parent" if r["is_parent"] else "") + ("; hold-out (c)" if r["holdout_c"] else ""))
    return rows


def write_csv(rows: list[dict], path: Path) -> str:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    Path(str(path) + ".sha256").write_text(digest + "  " + path.name + "\n", encoding="utf-8")
    return digest


def append_manifest(rows: list[dict], manifest_path: Path) -> int:
    """Append the rows to the manifest (status pending, deck empty, note = family/parent/charge); existing ids are left alone. Returns rows added."""
    existing = manifest_rows(manifest_path)
    have = {r["id"] for r in existing}
    added = 0
    with open(manifest_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=BM.FIELDS, lineterminator="\n")
        for r in rows:
            if r["id"] in have:
                continue
            note = f"pool3 {r['family']}" + (f"; parent {r['parent_id']}" if r["parent_id"] else "") + (f"; charge {r['charge']} mult {r['multiplicity']}" if r["charge"] else "")
            w.writerow(dict(id=r["id"], layer=r["layer"], priority=sha(r["smiles"]), name=r["name"], smiles=r["smiles"], qm9_label="", n_heavy=r["n_heavy"],
                            n_atoms=r["n_atoms"], status="pending", machine="", deck="", note=note))
            added += 1
    return added


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_csv")
    ap.add_argument("--manifest", default=str(M05 / "corpus" / "manifest.csv"))
    ap.add_argument("--write-manifest", action="store_true", help="append the rows to the manifest (after the user's review of the CSV)")
    a = ap.parse_args()
    rows = build(Path(a.manifest))
    digest = write_csv(rows, Path(a.out_csv))
    fams = {f: sum(r["family"] == f for r in rows) for f in QUOTA}
    held = {f: sum(r["family"] == f and r["holdout_c"] for r in rows) for f in QUOTA}
    print(f"{len(rows)} rows {fams}; hold-out (c) {held}; sha256 {digest[:16]}…; n_atoms max {max(r['n_atoms'] for r in rows)}")
    if a.write_manifest:
        print(f"manifest: {append_manifest(rows, Path(a.manifest))} rows appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
