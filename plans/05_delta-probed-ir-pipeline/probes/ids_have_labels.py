"""A chain runner's wait condition (13 Oct 2026): exit 0 when every id in the given files (one per line, '#' comments) has its corpus folder in
module 05's corpus/molecules with geometry.json and its labels; else exit 1 with one status line naming what is missing (first ten).

    python probes/ids_have_labels.py <ids file> [...] [--labels analytic|any] [--max-missing N] [--molecules …/corpus/molecules]

--labels analytic (the default) needs both analytic Hessians; --labels any (17 Oct 2026, the user: chain 41 on the FD labels its registration
allows — 'analytic where the molecule has them, else FD' — with the analytic re-read later) takes both analytic or both FD Hessians.
--max-missing N (26 Oct 2026, chain 35's full read) still exits 0 when at most N ids lack their labels — the label server's failed molecules,
which train on FD — and names them in the status line.
"""
import argparse
import sys
from pathlib import Path

MOLECULES = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus" / "molecules"
GEOMETRY = "geometry.json"
LABEL_SETS = {"analytic": (("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"),),
              "any": (("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"), ("hessian_b3lyp.npz", "hessian_wb97x.npz"))}


def missing(ids: list[str], molecules: Path, labels: str = "analytic") -> dict[str, list[str]]:
    """Per id what it lacks: geometry.json, and the first acceptable label set when none is complete."""
    out = {}
    for i in ids:
        folder = molecules / i
        lack = [] if (folder / GEOMETRY).exists() else [GEOMETRY]
        sets = LABEL_SETS[labels]
        if not any(all((folder / f).exists() for f in s) for s in sets):
            lack += [f for f in sets[0] if not (folder / f).exists()]
        if lack:
            out[i] = lack
    return out


def read_ids(files: list[str]) -> list[str]:
    ids = []
    for name in files:
        with open(name, encoding="utf-8") as f:
            ids += [s.strip() for s in f if s.strip() and not s.startswith("#")]
    return ids


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--labels", choices=sorted(LABEL_SETS), default="analytic")
    ap.add_argument("--molecules", default=str(MOLECULES))
    ap.add_argument("--max-missing", type=int, default=0, help="ids allowed to lack their labels (named in the status line)")
    a = ap.parse_args(argv)
    if a.max_missing < 0:
        ap.error(f"--max-missing {a.max_missing}: must be 0 or more")
    ids = read_ids(a.files)
    miss = missing(ids, Path(a.molecules), a.labels)
    detail = "" if not miss else "; missing " + ", ".join(f"{i} ({'/'.join(v)})" for i, v in list(miss.items())[:10])
    print(f"labelled ({a.labels}) {len(ids) - len(miss)}/{len(ids)}{detail}")
    return 0 if len(miss) <= a.max_missing else 1


if __name__ == "__main__":
    sys.exit(main())
