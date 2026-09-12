#!/usr/bin/env python
"""Module 05 — inventory of the Hessian QM9 download (vacuum split only extracted). Prints, measured not asserted:
archive size / md5 / sha256, the Arrow shard sizes and sha256, row counts, the schema, one example record's shapes,
the heavy-atom distribution, the composition counts and an 'aromatic-like' proxy count (>= 6 C and H <= C) that
bounds the size of the recomputed B3LYP subset (RECIPE: the size itself is fixed later by a dated note).
Run:  python inspect_hessian_qm9.py     (writes ../out/HESSIAN_QM9_SUMMARY.md and .json)"""
import collections, hashlib, json
from datetime import datetime
from pathlib import Path
import numpy as np
import pyarrow as pa, pyarrow.ipc as ipc

HERE = Path(__file__).resolve().parent
D = HERE.parent / "data" / "hessian_qm9"
OUT = HERE.parent / "out"; OUT.mkdir(exist_ok=True)
EXPECTED_MD5 = "f3e36130e5cc47021ab403767a19ddf7"     # figshare API, file 49271011


def sha256(p, algo="sha256"):
    h = hashlib.new(algo)
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    zp = D / "hessian_qm9_DatasetDict.zip"
    rec = json.load(open(D / "figshare_record_26363959.json", encoding="utf-8"))
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "record": {"title": rec["title"], "doi": rec["doi"], "version": rec["version"], "license": rec["license"]["name"], "published": rec["published_date"]},
           "archive": {"file": zp.name, "bytes": zp.stat().st_size, "md5": sha256(zp, "md5"), "sha256": sha256(zp)}}
    out["archive"]["md5_matches_figshare"] = out["archive"]["md5"] == EXPECTED_MD5
    vac = D / "hessian_qm9_DatasetDict" / "vacuum"
    shards = sorted(vac.glob("data-*.arrow"))
    out["vacuum_shards"] = [{"file": s.name, "bytes": s.stat().st_size, "sha256": sha256(s)[:16]} for s in shards]
    n_rows = 0; heavy = collections.Counter(); comp = collections.Counter(); arom = 0; labels = []; natoms = collections.Counter()
    example = None
    for s in shards:
        tab = ipc.open_stream(pa.memory_map(str(s))).read_all()
        n_rows += tab.num_rows
        if example is None:
            row = tab.slice(0, 1).to_pylist()[0]
            H = np.array(row["hessian"]); n = len(row["atomic_numbers"])
            example = {"label": row["label"], "natoms": n, "hessian_shape": list(H.shape), "hessian_symmetric": bool(np.allclose(H.reshape(3 * n, 3 * n), H.reshape(3 * n, 3 * n).T, atol=1e-6)),
                       "frequencies_shape": list(np.array(row["frequencies"]).shape), "normal_modes_shape": list(np.array(row["normal_modes"]).shape), "energy": row["energy"], "schema": tab.schema.names}
        for z, lab in zip(tab.column("atomic_numbers").to_pylist(), tab.column("label").to_pylist()):
            c = collections.Counter(z); nh = sum(1 for a in z if a > 1); heavy[nh] += 1; natoms[len(z)] += 1
            comp[(c[6], c[1], c[7], c[8], c[9])] += 1
            if c[6] >= 6 and c[1] <= c[6]:
                arom += 1; labels.append(lab)
    out.update({"vacuum_rows": n_rows, "example": example, "heavy_atoms_histogram": dict(sorted(heavy.items())), "natoms_min_max": [min(natoms), max(natoms)],
                "aromatic_like_proxy": {"rule": "n_C >= 6 and n_H <= n_C", "count": arom, "share": round(arom / n_rows, 4)},
                "compositions_most_common": [{"C,H,N,O,F": list(k), "n": v} for k, v in comp.most_common(10)], "n_distinct_compositions": len(comp)})
    json.dump(out, open(OUT / "HESSIAN_QM9_SUMMARY.json", "w"), indent=1)
    (D / "aromatic_like_labels.txt").write_text("\n".join(labels), encoding="utf-8")
    L = [f"# Hessian QM9 — inventory of the download — {out['date']}", "",
         f"Record: {rec['title']} — DOI {rec['doi']} (version {rec['version']}, {rec['license']['name']}, published {rec['published_date'][:10]}); paper Williams et al., Scientific Data 12 (2025), DOI 10.1038/s41597-024-04361-2. Downloaded 2026-09-12 with the user's permission.", "",
         f"Archive `{zp.name}`: {out['archive']['bytes']:,} bytes; md5 `{out['archive']['md5']}` ({'matches figshare' if out['archive']['md5_matches_figshare'] else 'MISMATCH'}); sha256 `{out['archive']['sha256']}`. Splits in the archive: vacuum, thf, toluene, water (9.47 GB unpacked); **only `vacuum/` extracted** ({sum(s['bytes'] for s in out['vacuum_shards'])/1e9:.2f} GB, 5 Arrow stream shards).", "",
         f"**Vacuum split: {n_rows:,} molecules.** Schema: {', '.join(example['schema'])}. Example `{example['label']}`: {example['natoms']} atoms, hessian {example['hessian_shape']} (symmetric: {example['hessian_symmetric']}), frequencies {example['frequencies_shape']}, normal_modes {example['normal_modes_shape']}.", "",
         "Heavy atoms per molecule: " + ", ".join(f"{k}: {v:,}" for k, v in sorted(heavy.items())) + f" (atoms {min(natoms)}–{max(natoms)}).", "",
         f"Aromatic-like proxy (n_C ≥ 6 and n_H ≤ n_C, a composition rule, not ring detection): **{arom:,} molecules ({arom/n_rows:.1%})** — labels in `data/hessian_qm9/aromatic_like_labels.txt`; an upper bound for the recomputed B3LYP subset, whose size the RECIPE fixes by dated note after the Hessian timing.", "",
         "Most common compositions (C,H,N,O,F): " + "; ".join(f"{tuple(k)}: {v}" for k, v in comp.most_common(6)) + f"; {len(comp)} distinct compositions.", "",
         "Shards (sha256 first 16): " + ", ".join(f"{s['file']} {s['sha256']}" for s in out["vacuum_shards"]), "",
         "Units and conventions of the fields (energies, Hessian units, frequency columns) are to be read from the paper before any use — not assumed here."]
    (OUT / "HESSIAN_QM9_SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
