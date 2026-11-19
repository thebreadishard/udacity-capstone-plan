"""The licence of the learned correction (decision 65, the user 29 Oct 2026; amended by the user on 16 Nov 2026): a mode family is
licensed where the error of what the product delivers — the corrected band positions of the carried ΔH network's seed-mean correction —
is within decision 53's 3 cm⁻¹ on both hold-outs. It is read from the network's product-error record, never typed in; until the
amendment it was read on the first-order diagonal error averaged over the seeds, which the statement still gives under its own name.
Where a licensed family's bootstrap interval over molecules reaches above the line, the statement says so with the interval and the
number of molecules. The licence holds at the level the network is measured at, the DFT proxy (ωB97X); no coupled-cluster licence
exists. It replaces the layer-B rule of the proof-of-learning pre-registration (25 Sep 2026), which was written before the ΔH network."""
from __future__ import annotations

from .accuracy import AMENDED, FIRST_ORDER, HOLDOUTS, LICENCE_LINE_CM, LICENCE_QUANTITY, PRODUCT, QUANTITY_NAMES, carried_accuracy, stated_errors
from .own_spread import N_HYDROGEN_SWAPS, N_LISTINGS, N_ROTATIONS, N_SWAPS, SEED

# isort: split
from promotion_read import FAMILIES  # probes/, on the path through m08.pipeline

RULE = (f"decision 65 (29 Oct 2026, amended {AMENDED}): a mode family is licensed where the error of what the product delivers — the "
        f"{QUANTITY_NAMES[PRODUCT]}: the carried ΔH network's seeds' mean ΔH added to the B3LYP Hessian and diagonalised, each corrected "
        "band paired to its ωB97X band by mode overlap and counted in the family of its B3LYP partner — is within 3 cm⁻¹ (decision 53) on "
        "both hold-outs, at the DFT-proxy level; until the amendment the licence was read on the first-order diagonal error averaged over "
        "the seeds, which the records keep under its own name; it replaces the layer-B rule of 25 Sep 2026; and since pipeline 0.15 a "
        "band's licence follows its own measured spread (m08/own_spread.py, aromir's rule): the networks correct the same molecule given "
        f"in other ways — {N_ROTATIONS} random rotations, the mirror image and a rotated mirror image, {N_LISTINGS} random listings of "
        "the atoms put into the canonical order and swaps of atoms the bond graph cannot tell apart (all of them up to "
        f"{N_SWAPS}; of more, {N_SWAPS} symmetries of the heavy-atom skeleton and {N_HYDROGEN_SWAPS} exchanges of hydrogens), drawn "
        f"with the seed {SEED} — each band is paired with itself by its motion, and it is licensed only when its position lay no more "
        f"than {LICENCE_LINE_CM:g} cm⁻¹ from the printed one in every presentation tried: the distance from the printed presentation, "
        "not the range between presentations, and a sample, not a bound; where that cannot be measured, no band is licensed; the "
        "corrected positions are printed either way. It replaces the rule by a molecule's group of 19 Nov 2026 (TASKS 288), whose "
        "measurement — the release's invariance record, <stem>_invariance.json beside the release networks — describes the network "
        "and decides no licence")
OWN_SPREAD_CONDITION = ("own position moved by no more than the licence line in the {tried}presentations tried (this molecule turned, "
                        "mirrored or listed in another atom order)")
"""aromir's statement (`certificate._statement` at bb8eb62), word for word: the licence's condition on a band's own spread. `tried` is
the number of presentations with a space after it, or empty where none is known."""
RULE_SOURCE = f"README.md, decision 65 as amended on {AMENDED}"


def _errors(family: str, errors: dict[str, dict[str, float]]) -> str:
    return f"{family} ({' / '.join(str(v) for v in errors[family].values())})"


def caveats(accuracy: dict, licensed: list[str]) -> list[str]:
    """One sentence per licensed family and hold-out whose licence rests on an interval that crosses the line — the 97.5th percentile
    of the bootstrap over molecules lies above it: the interval, the number of molecules that have such bands (not every molecule of
    a hold-out has a CH-oop band) and the share of resamples under the line."""
    out = []
    for f in licensed:
        for h in HOLDOUTS:
            p = accuracy["holdouts"][h][PRODUCT][f]
            if p["interval_crosses_line"]:
                n, of = p["n_molecules_with_modes"], p["n_molecules"]
                rests = f"{n} molecules" if n == of else f"{n} of the hold-out's {of} molecules (the others have no such band)"
                out.append(f"{f} on hold-out ({h}) rests on {rests}: the 95 % interval of a bootstrap over molecules "
                           f"is {p['interval'][0]}–{p['interval'][1]} cm⁻¹ and crosses the line "
                           f"({round(100 * p['share_below_line'])} % of the resamples lie under it)")
    return out


def caveat_sentence(licence: dict) -> str:
    """The licence's caveats as the one sentence every page prints with the licence — under a table of licensed families or bands and
    at the end of a statement that names them; '' when there is none. `licence` is `state()`'s result or a certificate's licence block.
    A certificate stored before the amendment of 16 Nov 2026 has no caveats field: its licence was read on the first-order quantity,
    for which no interval was measured, so it has none to print."""
    notes = licence.get("caveats", [])
    return f"Licence caveat: {'; '.join(notes)}." if notes else ""


def state(accuracy: dict | None = None) -> dict:
    """The licence under the carried network's records, or under `accuracy` (a `network_accuracy` result with its product-error record)
    when given: read on the product's quantity, with the first-order one beside it under its own name."""
    acc = carried_accuracy() if accuracy is None else accuracy
    quantity, errors = stated_errors(acc)
    if quantity != LICENCE_QUANTITY:
        raise ValueError(f"this accuracy was stored before the amendment of {AMENDED} and holds the {QUANTITY_NAMES[quantity]} only; "
                         f"the licence is read on the {QUANTITY_NAMES[LICENCE_QUANTITY]}")
    first_order = {f: {h: acc["holdouts"][h]["readouts"][f]["mean"] for h in HOLDOUTS} for f in FAMILIES}
    licensed = [f for f in FAMILIES if all(v <= LICENCE_LINE_CM for v in errors[f].values())]
    notes = caveats(acc, licensed)
    statement = ("licensed at the DFT proxy: " + (", ".join(_errors(f, errors) for f in licensed) or "no family")
                 + "; not licensed: " + (", ".join(_errors(f, errors) for f in FAMILIES if f not in licensed) or "none")
                 + f" — {QUANTITY_NAMES[quantity]} on hold-outs (a) / (b) in cm⁻¹ against {LICENCE_LINE_CM:g} (decision 65 as amended on "
                 + f"{AMENDED})" + "".join(f"; {n}" for n in notes)
                 + f"; the {QUANTITY_NAMES[FIRST_ORDER]}, which the licence read until then: "
                 + ", ".join(_errors(f, first_order) for f in FAMILIES) + "; no coupled-cluster licence")
    return dict(licensed_families=licensed, errors=errors, quantity=quantity, quantity_name=QUANTITY_NAMES[quantity],
                first_order_errors=first_order, caveats=notes, line_cm=LICENCE_LINE_CM, rule=RULE, rule_source=RULE_SOURCE,
                sources=acc["sources"], statement=statement)
