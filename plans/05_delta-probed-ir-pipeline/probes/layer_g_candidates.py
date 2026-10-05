"""Step (c) of the candidate generator's batch route (TASKS 22; `GoalGathering/notes/PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md`,
outcome of 5 Oct 19:0x: both lines met, the generator is a registered source): layer G of the corpus manifest.

One row per new fused aromatic ring system of the frozen gated list — the system's representative is the bare ring system itself when it passed the gate,
otherwise the most frequent passing molecule of that system (ties by SMILES); PubChem-known systems first (the system's SMILES is a molecule of the frozen
PubChem set), then by the system's occurrence count over all proposals, then by SMILES. Ids follow the manifest's scheme `G_<sha1(smiles)[:10]>`; the CSV
is frozen with its SHA-256; `--write-manifest` appends the rows (status pending, deck empty, note = source and list hash) and leaves existing ids alone.
What is computed stays with the composition rule (decision 52) and the steward; the Atlas labels the rows by their source (step d).

    python probes/layer_g_candidates.py out/layer_g_candidates_2026-10-05.csv [--gated <gated csv>] [--manifest <manifest.csv>] [--pubchem <csv>|''] [--write-manifest]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
M06 = PLAN / "modules" / "06_generative_candidates"
sys.path.insert(0, str(M05 / "corpus"))
sys.path.insert(0, str(M06 / "m06"))
import build_manifest as BM  # noqa: E402

GATED = M06 / "out" / "proposals_10x_2026-10-04_gated.csv"
PUBCHEM = M06 / "data" / "pubchem_aromatics_2026-09-24.csv"
SOURCE = "generator v0.1+v0.2"
FIELDS = ["rank", "id", "layer", "name", "smiles", "ring_system", "representative", "system_occurrences", "molecules_in_system", "pubchem_system",
          "n_heavy", "n_atoms", "ring_class", "hetero_class", "source", "list_sha256"]


def sha(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def atom_counts(smiles: str) -> tuple[int, int]:
    from rdkit import Chem
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    return m.GetNumHeavyAtoms(), m.GetNumAtoms()


def gated_rows(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("stage", "pass") == "pass" and r.get("smiles")]


def pubchem_molecules(path: Path | None) -> set:
    if not path or not Path(path).exists():
        return set()
    from gate import pubchem_set
    return pubchem_set(Path(path))


def build(rows: list[dict], manifest_smiles: set, known: set, gated_sha: str) -> list[dict]:
    systems = defaultdict(list)
    for r in rows:
        systems[r["ring_system"]].append(r)
    out = []
    for system, rs in systems.items():
        bare = [r for r in rs if r["smiles"] == system]
        rep = bare[0] if bare else sorted(rs, key=lambda r: (-int(r["occurrences"]), r["smiles"]))[0]
        if rep["smiles"] in manifest_smiles:
            continue
        occ = sum(int(r["occurrences"]) for r in rs)
        nh, na = atom_counts(rep["smiles"])
        out.append(dict(layer="G", smiles=rep["smiles"], ring_system=system, representative="bare system" if bare else "most frequent molecule",
                        system_occurrences=occ, molecules_in_system=len(rs), pubchem_system=system in known, n_heavy=nh, n_atoms=na,
                        ring_class=rep["ring_class"], hetero_class=rep["hetero_class"], source=SOURCE, list_sha256=gated_sha))
    out.sort(key=lambda r: (not r["pubchem_system"], -r["system_occurrences"], r["smiles"]))
    for k, r in enumerate(out, 1):
        r["rank"] = k
        r["id"] = f"G_{sha(r['smiles'])[:10]}"
        r["name"] = f"generator {r['ring_class']} {r['hetero_class']} #{k}" + (" (PubChem)" if r["pubchem_system"] else "")
    return out


def write_csv(rows: list[dict], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_manifest(rows: list[dict], manifest_path: Path, list_sha: str) -> int:
    """Append the layer-G rows (status pending, deck empty, note = source, list hash, ring system); existing ids are left alone. Returns rows added."""
    existing = manifest_rows(manifest_path)
    have = {r["id"] for r in existing}
    term = "\r\n" if b"\r\n" in manifest_path.read_bytes()[:4096] else "\n"
    added = 0
    with open(manifest_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=BM.FIELDS, lineterminator=term)
        for r in rows:
            if r["id"] in have:
                continue
            note = (f"source={r['source']}; list {list_sha[:16]}; system {r['ring_system']}; {r['representative']}; "
                    f"pubchem {'yes' if r['pubchem_system'] else 'no'}; rank {r['rank']}")
            w.writerow(dict(id=r["id"], layer="G", priority=sha(r["smiles"]), name=r["name"], smiles=r["smiles"], qm9_label="", n_heavy=r["n_heavy"],
                            n_atoms=r["n_atoms"], status="pending", machine="", deck="", note=note))
            added += 1
    return added


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_csv")
    ap.add_argument("--gated", default=str(GATED))
    ap.add_argument("--manifest", default=str(M05 / "corpus" / "manifest.csv"))
    ap.add_argument("--pubchem", default=str(PUBCHEM), help="the frozen PubChem set; '' to skip (then no system counts as PubChem-known)")
    ap.add_argument("--write-manifest", action="store_true", help="append the rows to the manifest as layer G")
    a = ap.parse_args()
    gated = Path(a.gated)
    gated_sha = hashlib.sha256(gated.read_bytes()).hexdigest()
    rows = gated_rows(gated)
    manifest_smiles = {BM.canon(r["smiles"]) for r in manifest_rows(Path(a.manifest)) if r.get("smiles")} - {None}
    known = pubchem_molecules(Path(a.pubchem) if a.pubchem else None)
    out = build(rows, manifest_smiles, known, gated_sha)
    digest = write_csv(out, Path(a.out_csv))
    n_pub = sum(r["pubchem_system"] for r in out); n_bare = sum(r["representative"] == "bare system" for r in out)
    print(f"{len(out)} layer-G rows from {len(rows)} passing molecules (gated list {gated_sha[:16]}…): {n_pub} PubChem-known systems first, "
          f"{n_bare} represented by the bare system; n_atoms max {max(r['n_atoms'] for r in out)}; csv sha256 {digest[:16]}…")
    if a.write_manifest:
        added = append_manifest(out, Path(a.manifest), digest)
        print(f"manifest: {added} rows added as layer G ({len(out) - added} already present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
