"""A chain runner's wait condition (13 Oct 2026): exit 0 when every id in the given files (one per line, '#' comments) has its corpus folder in
module 05's corpus/molecules with geometry.json and both analytic Hessians; else exit 1 with one status line naming what is missing (first ten).

    python probes/ids_have_labels.py <ids file> [...] [--molecules modules/05_support_predictor/corpus/molecules]
"""
import argparse
import sys
from pathlib import Path

MOLECULES = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus" / "molecules"
NEEDED = ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz")


def missing(ids: list, molecules: Path) -> dict:
    out = {}
    for i in ids:
        lack = [f for f in NEEDED if not (molecules / i / f).exists()]
        if lack:
            out[i] = lack
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--molecules", default=str(MOLECULES))
    a = ap.parse_args()
    ids = [s.strip() for f in a.files for s in open(f, encoding="utf-8") if s.strip() and not s.startswith("#")]
    miss = missing(ids, Path(a.molecules))
    print(f"labelled {len(ids) - len(miss)}/{len(ids)}" + ("" if not miss else "; missing " + ", ".join(f"{i} ({'/'.join(v)})" for i, v in list(miss.items())[:10])))
    return 0 if not miss else 1


if __name__ == "__main__":
    sys.exit(main())
