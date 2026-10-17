"""Refuse a training whose analytic labels are not in the corpus (17 Oct 2026: chain 35h's 'analytic' arm trained with 44 analytic labels
instead of the smallest half's 413, because its fetch failed silently). A chain runs this as the step before the training.

    python probes/require_analytic_labels.py --min 413 --max-atoms 22

Counts the corpus molecules of at most --max-atoms atoms that hold both analytic Hessians (hessian_b3lyp_analytic.npz and
hessian_wb97x_analytic.npz); exit 0 when the count reaches --min, exit 1 with the count otherwise.
"""
import argparse
import json
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent / "modules" / "05_support_predictor" / "corpus" / "molecules"
LABELS = ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz")


def count_labelled(corpus: Path, max_atoms: int) -> int:
    """Molecules with both analytic Hessians and at most max_atoms atoms."""
    n = 0
    for mol in corpus.iterdir():
        if not all((mol / name).is_file() for name in LABELS):
            continue
        with open(mol / "geometry.json", encoding="utf-8") as f:
            if len(json.load(f)["symbols"]) <= max_atoms:
                n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--min", type=int, required=True, help="the analytic labels the training must have")
    ap.add_argument("--max-atoms", type=int, required=True, help="the size bound of the labelled half")
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    args = ap.parse_args(argv)
    n = count_labelled(args.corpus, args.max_atoms)
    if n < args.min:
        print(f"REFUSED: {n} molecules of ≤ {args.max_atoms} atoms carry both analytic Hessians, {args.min} required")
        return 1
    print(f"ok: {n} molecules of ≤ {args.max_atoms} atoms carry both analytic Hessians (≥ {args.min})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
