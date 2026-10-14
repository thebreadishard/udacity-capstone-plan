"""TASKS 61 step 1 (14 Oct 2026; design note `GoalGathering/notes/Design_2026-10-14_Rungs_4_5_Broad_Sets.md`): the frozen candidate list that
fills rung 4 of the slow ladder (decision 39) with broad sets — the five four-ring benzenoid families the corpus lacks, each the bare parent plus
29 mixed mono-substituted children (decision 52: ≈ 30 cover a family).

Families: tetracene, chrysene, benz[a]anthracene, benzo[c]phenanthrene, triphenylene (the closed-shell four-ring benzenoids other than pyrene,
by the enumeration of 14 Oct; formula and ring count checked in tests). Children use layer B's substituent scheme (`corpus/build_manifest.SUBS`,
`substituted`): round j takes, for each substituent in hash order, its j-th product in hash order not yet taken — so the first 15 children carry
15 different substituents and later rounds add positions; canonical, distinct, n_atoms ≤ 40, no SMILES of the manifest, of pool 3's frozen list or of hold-outs (b)/(c).
**Tetracene is the test family (the user, 14 Oct: 'tetraceen akkoord'):** its 30 rows carry test_family = 1 and are never trained. In each of
the four training families the parent has curve_rank 1 and the children 2..30 in generation order (substituents before positions), so the
registered curve 0 / 10 / 20 / 30 per family is a nested subset of this one list and every point of it is breadth first. Ids `R4_<sha1(smiles)[:10]>`; a parent that already exists as a pending layer-G row (the generator's
bare ring system) is recorded in `same_as`, and `--write-manifest` sets that row to status 'moved' so the molecule is computed once.
Price per row: lane-hours on the labels server's measured fit (`probes/price_large_labels.py`, both exponents).

    python probes/rung4_candidates.py modules/05_support_predictor/out/rung4_candidates_2026-10-14.csv [--write-manifest]
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "corpus"))
sys.path.insert(0, str(PLAN / "probes"))
import build_manifest as BM  # noqa: E402
import price_large_labels as PL  # noqa: E402
from pool3_candidates import atom_counts, manifest_rows, sha  # noqa: E402
from rdkit import Chem  # noqa: E402
from rungC_error_map import kind_of  # noqa: E402

PARENTS = {                                                        # formula C18H12 and four rings checked in tests/test_rung4_candidates.py
    "tetracene": "c1ccc2cc3cc4ccccc4cc3cc2c1",
    "chrysene": "c1ccc2c(c1)ccc1c3ccccc3ccc21",
    "benz[a]anthracene": "c1ccc2cc3c(ccc4ccccc43)cc2c1",
    "benzo[c]phenanthrene": "c1ccc2c(c1)ccc1ccc3ccccc3c12",
    "triphenylene": "c1ccc2c(c1)c1ccccc1c1ccccc21",
}
TEST_FAMILY = "tetracene"
PER_FAMILY = 30
MAX_ATOMS = 40
LAYER = "R4"
FIELDS = ["id", "layer", "name", "smiles", "n_heavy", "n_atoms", "kind", "family", "is_parent", "test_family", "curve_rank", "same_as",
          "nbas", "lane_hours_lo", "lane_hours_hi", "reason"]
HOLDOUT_FILES = [M05 / "corpus" / "holdout_c.txt", M05 / "corpus" / "holdout_b_frozen_2026-10-08.txt"]
POOL3_LIST = M05 / "out" / "pool3_candidates_2026-10-03.csv"           # pool 3 is computed but not merged yet: its SMILES count as known


def family_children(parent_smi: str, quota: int, max_atoms: int, exclude: set) -> list[tuple[str, str]]:
    """(substituent, SMILES) children of one parent: round j takes each substituent's j-th unused product (hash order), substituents in hash
    order, until `quota`."""
    snames = sorted(BM.SUBS, key=sha)
    prods = {sn: sorted({BM.canon(s) for s in BM.substituted(parent_smi, BM.SUBS[sn])} - {None}, key=sha) for sn in snames}
    out, seen = [], set(exclude)
    for j in range(max(len(p) for p in prods.values())):
        for sn in snames:
            if len(out) >= quota:
                return out
            if j < len(prods[sn]):
                smi = prods[sn][j]
                if smi not in seen and atom_counts(smi)[1] <= max_atoms:
                    seen.add(smi)
                    out.append((sn, smi))
    return out


def holdout_ids() -> set:
    ids = set()
    for p in HOLDOUT_FILES:
        if p.exists():
            ids |= {ln.split()[0] for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}
    return ids


def lane_hours(symbols_nbas: int, fits) -> tuple[float, float]:
    h = sorted(float(np.exp(p * np.log(symbols_nbas) + c)) / 3600 * PL.OPT_ALLOWANCE for p, c in fits)
    return round(h[0], 2), round(h[1], 2)


def price_fits():
    rows = json.load(open(Path(PL.OUT) / "labels_lane_times.json"))
    n = np.array([PL.nbas(r["symbols"]) for r in rows], float)
    t = np.array([r["seconds"] for r in rows], float)
    return [PL.fit(n, t), PL.fit(n[n >= np.median(n)], t[n >= np.median(n)])]


def nbas_of(smi: str) -> int:
    m = Chem.AddHs(Chem.MolFromSmiles(smi))
    return sum(PL.NBAS[a.GetSymbol()] for a in m.GetAtoms())


def build(manifest_path: Path) -> list[dict]:
    manifest = manifest_rows(manifest_path)
    held = holdout_ids()
    by_smiles = {}
    for r in manifest:
        if r["smiles"]:
            by_smiles.setdefault(BM.canon(r["smiles"]), []).append(r)
    known = set(by_smiles) | {BM.canon(r["smiles"]) for r in manifest if r["id"] in held and r["smiles"]}
    if POOL3_LIST.exists():
        known |= {BM.canon(r["smiles"]) for r in manifest_rows(POOL3_LIST)}
    fits = price_fits()
    rows = []
    for fam in sorted(PARENTS, key=lambda f: sha(PARENTS[f])):
        psmi = BM.canon(PARENTS[fam])
        prior = [r for r in by_smiles.get(psmi, []) if r["layer"] != LAYER]
        if any(r["status"] != "pending" or r["layer"] != "G" for r in prior):
            raise RuntimeError(f"{fam}: the parent exists in the manifest as {[(r['id'], r['status']) for r in prior]} — not a pending layer-G row")
        fr = [{"name": fam, "smiles": psmi, "is_parent": 1, "same_as": ",".join(r["id"] for r in prior)}]
        fr += [{"name": f"{fam}+{sn}", "smiles": smi, "is_parent": 0, "same_as": ""}
               for sn, smi in family_children(psmi, PER_FAMILY - 1, MAX_ATOMS, known | {psmi})]
        if len(fr) != PER_FAMILY:
            raise RuntimeError(f"{fam}: {len(fr)} rows, not {PER_FAMILY}")
        test = int(fam == TEST_FAMILY)
        for rank, r in enumerate(fr, start=1):                     # generation order: every curve point is breadth first over substituents
            nh, na = atom_counts(r["smiles"])
            nb = nbas_of(r["smiles"])
            lo, hi = lane_hours(nb, fits)
            r.update(id=f"{LAYER}_{sha(r['smiles'])[:10]}", layer=LAYER, family=fam, test_family=test, curve_rank=0 if test else rank,
                     n_heavy=nh, n_atoms=na, kind=kind_of(r["smiles"])["kind"], nbas=nb, lane_hours_lo=lo, lane_hours_hi=hi,
                     reason="rung 4 broad set (TASKS 61)" + ("; parent" if r["is_parent"] else "") + ("; test family, never trained" if test else ""))
            rows.append(r)
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
    """Append the rows (status pending; note = family, parent/test flags) and set each `same_as` layer-G row to 'moved'; existing ids are left
    alone. The manifest is rewritten atomically. Returns the rows added."""
    existing = manifest_rows(manifest_path)
    have = {r["id"] for r in existing}
    moved = {g: r["id"] for r in rows for g in r["same_as"].split(",") if g}
    for r in existing:
        if r["id"] in moved and r["status"] == "pending":
            r["status"] = "moved"
            r["note"] = (r.get("note", "") + f" computed as {moved[r['id']]} (rung 4, TASKS 61)").strip()
    added = []
    for r in rows:
        if r["id"] in have:
            continue
        note = f"rung4 {r['family']}" + ("; parent" if r["is_parent"] else "") + ("; test family" if r["test_family"] else "")
        added.append(dict(id=r["id"], layer=r["layer"], priority=sha(r["smiles"]), name=r["name"], smiles=r["smiles"], qm9_label="",
                          n_heavy=r["n_heavy"], n_atoms=r["n_atoms"], status="pending", machine="", deck="", note=note))
    term = "\r\n" if b"\r\n" in manifest_path.read_bytes()[:4096] else "\n"      # keep the file's own line ending
    tmp = manifest_path.with_suffix(".rung4.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=BM.FIELDS, lineterminator=term)
        w.writeheader()
        for r in existing + added:
            w.writerow({k: r.get(k, "") for k in BM.FIELDS})
    tmp.replace(manifest_path)
    return len(added)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_csv")
    ap.add_argument("--manifest", default=str(M05 / "corpus" / "manifest.csv"))
    ap.add_argument("--write-manifest", action="store_true", help="append the rows to the manifest (after the registration and the user's word)")
    a = ap.parse_args()
    rows = build(Path(a.manifest))
    digest = write_csv(rows, Path(a.out_csv))
    lo, hi = sum(r["lane_hours_lo"] for r in rows), sum(r["lane_hours_hi"] for r in rows)
    fams = {f: sum(r["family"] == f for r in rows) for f in PARENTS}
    print(f"{len(rows)} rows {fams}; test family {TEST_FAMILY}; n_atoms {min(r['n_atoms'] for r in rows)}–{max(r['n_atoms'] for r in rows)}; "
          f"lane-hours {lo:.0f}–{hi:.0f} (CCX53: {lo / PL.LANES / 24:.1f}–{hi / PL.LANES / 24:.1f} days, €{lo / PL.LANES * PL.CCX53_EUR_PER_H:.0f}–"
          f"{hi / PL.LANES * PL.CCX53_EUR_PER_H:.0f}); sha256 {digest[:16]}…")
    if a.write_manifest:
        print(f"manifest: {append_manifest(rows, Path(a.manifest))} rows appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
