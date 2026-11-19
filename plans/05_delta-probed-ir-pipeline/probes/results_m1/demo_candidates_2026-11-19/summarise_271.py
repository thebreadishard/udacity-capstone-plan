"""Print out.json as a markdown table: every candidate, then the ones outside the corpus that pass the gates and the half hour."""
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
STEP3_215 = 462 / 324     # benzene: 2.15.0's step 3 alone against 2.14.0's whole run (TASKS 270) — a floor on the slowdown


def ids(xs, k=3):
    if not xs:
        return "-"
    s = ", ".join(f"{i}({lay},{st})" if isinstance(i, str) and lay else str(i) for i, lay, st in xs[:k]) if isinstance(xs[0], list) \
        else ", ".join(xs[:k])
    return s + (f" +{len(xs) - k}" if len(xs) > k else "")


print("| name | SMILES | atoms | bf | est min (2.14.0) | ≥ min ×1.43 (2.15.0) | ≤30? | corpus rows | release | meas. trained "
      "| hold-out | cation trained (rel) | gates |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
keep = []
for r in d["rows"]:
    corp = ids(r["corpus"])
    ho = f"{r['holdout'][0]}: {', '.join(r['holdout'][1])}" if r["holdout"] else "-"
    gates = "pass" if not r["gates"] else "; ".join(r["gates"])
    if not r["inside_sizes"]:
        gates += " (outside 8-40 atoms)"
    mins = r["seconds"] / 60
    print(f"| {r['name']} | `{r['smiles']}` | {r['atoms']} | {r['nbf']} | {mins:.0f} | {mins * STEP3_215:.0f} | {'yes' if r['half_hour'] else 'no'} "
          f"| {corp} | {ids(r['release'])} | {ids(r['meas_trained'])} | {ho} | {ids(r['release_cation'])} | {gates} |")
    if not r["corpus"] and not r["gates"] and r["inside_sizes"] and r["half_hour"]:
        keep.append(r)
print()
print("KEEP (outside corpus, gates pass, inside sizes, ≤ 30 min on the 2.14.0 fit):")
for r in keep:
    print(f"- {r['name']} `{r['smiles']}` atoms {r['atoms']} bf {r['nbf']} est {r['seconds'] / 60:.0f} min (x1.43: {r['seconds'] / 60 * STEP3_215:.0f})"
          f" cation_rel {r['release_cation']} cation_meas {r['meas_cation']}")
