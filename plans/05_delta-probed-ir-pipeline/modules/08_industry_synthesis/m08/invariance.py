"""How far a network version's answer moves when the same molecule is turned, mirrored or listed in another atom order, and the licence
rule that follows from it (TASKS 288, the project owner's decision of 19 Nov 2026, as aromir's certificate at 07b215d): while the version's
invariance record shows a spread above the licence line for the molecule's group — with or without a linear group — no band of the
molecule is licensed; the corrected positions are still printed. A molecule with a linear group whose version did not measure every
change on such molecules is not licensed either ('not measured'): a licence is a claim that needs its measurement. A molecule without
one keeps its licence where its group was not measured, as before versions had the record. The record is aromir's
(`<stem>_invariance.json` beside the networks it measured, with its provenance); the networks that ran must be the ones it names."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

import numpy as np

from . import accuracy as A

# isort: split
import e7_t2_sqm as T2  # module 05's code, on the path through m08.pipeline
import internal_coords as IC

RECORD_SUFFIX = "_invariance.json"
WITH, WITHOUT = "with_linear_group_cm", "without_linear_group_cm"
NOT_CHANGES = ("network_version", "source", "provenance")        # the record's fields that are not a change

# aromir's certificate.py at 07b215d, word for word; the keys are the record's field names, aromir's are its `Invariance.spreads` names
CHANGE_PHRASES = {
    "rotation": "a rotation",
    "mirror_image": "a mirror image",
    "xyz_atom_order": "another xyz listing",
}
"""The changes of the invariance record the licence reads, each with the phrase its sentences use. A user's input can make all three: an
xyz file in any orientation, the other configuration of a molecule whose one stereo element is one centre and any listing of an xyz
file's atoms."""
CHANGES = ", ".join(list(CHANGE_PHRASES.values())[:-1]) + (
    f" or {list(CHANGE_PHRASES.values())[-1]}"
)
SPREAD_CHANGES = f"{CHANGES} of the atoms"
STILL_PRINTED = (
    "so the network's correction for this molecule is not licensed; the corrected positions "
    "are still printed"
)


@dataclass(frozen=True)
class Withheld:
    """Why no band of a molecule is licensed: its group's recorded spread above the licence line (None: not measured), what each band's
    licence column says and the sentence the certificate's statement gives."""

    spread_cm: float | None
    note: str
    reason: str


@dataclass(frozen=True)
class GroupSpread:
    """What a version's invariance record says of the molecules of one group: the largest spread, cm⁻¹, over the changes of
    `CHANGE_PHRASES` measured on them (None when none was), the phrase of the change that gave it (empty when none was measured; a tie
    goes to the first in `CHANGE_PHRASES`) and whether every one of those changes was measured on the group."""

    spread_cm: float | None
    change: str
    complete: bool


def has_linear_group(symbols: list[str], coords_bohr: np.ndarray) -> bool:
    """Whether the network's internal coordinates of a molecule hold a linear angle (`e7_t2_sqm.internals`, the inputs the network is
    built on). geomeTRIC makes an angle linear from the geometry and the bonds alone (|cos| ≥ 0.95 of a bonded triple, about 162°), so
    the primitive settings' angle choice, which only renumbers the atoms, does not change the answer."""
    _, types = T2.internals(symbols, np.asarray(coords_bohr, float), IC.CARRIED)
    return any(t[0] == "linear" for t in types)


def record_path(models: tuple[str, ...]) -> Path:
    """Where the models' invariance record lies: `<stem>_invariance.json` beside them (`accuracy.version_record_path`)."""
    return A.version_record_path(models, RECORD_SUFFIX)


def load_record(models: tuple[str, ...], sha16: dict[str, str]) -> dict | None:
    """The invariance record of the models that ran, or None where their version has none. `models` are keys under module 05's out/,
    `sha16` the hashes of the files that ran by file name; a record that names other networks, by name or by hash, is refused."""
    path = record_path(models)
    if not path.is_file():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    measured = record["provenance"]["networks"]
    names = {PureWindowsPath(key).name for key in models}
    if names != set(measured):
        raise ValueError(f"{path.name} measured {sorted(measured)}, and {sorted(names)} ran")
    differ = sorted(n for n in names if not measured[n].startswith(sha16[n]))
    if differ:
        raise ValueError(f"{path.name} measured other files under the names {differ}")
    return record


def group_spread(record: dict | None, *, linear_group: bool) -> GroupSpread:
    """The largest spread the record gives molecules with or without a linear group. A record that names other changes than
    `CHANGE_PHRASES` is refused: a change the licence does not read would otherwise stay out of the largest."""
    if record is None:
        return GroupSpread(spread_cm=None, change="", complete=False)
    changes = [key for key in record if key not in NOT_CHANGES]
    if changes != list(CHANGE_PHRASES):
        raise ValueError(f"the invariance record names the changes {changes}, the licence reads {list(CHANGE_PHRASES)}")
    measured = {
        CHANGE_PHRASES[name]: value
        for name in changes
        if (value := record[name][WITH if linear_group else WITHOUT]) is not None
    }
    if not measured:
        return GroupSpread(spread_cm=None, change="", complete=False)
    change = max(measured, key=measured.__getitem__)
    return GroupSpread(spread_cm=measured[change], change=change, complete=len(measured) == len(changes))


def _too_far(spread: GroupSpread, line: float, *, linear_group: bool) -> Withheld:
    """Say that a molecule's group moved by more than the licence line."""
    value = spread.spread_cm
    if linear_group:
        return Withheld(
            spread_cm=value,
            note=(
                "the molecule has a linear group, and molecules with one moved by up to "
                f"{value:.2f} cm⁻¹ under {CHANGES}, more than the licence line"
            ),
            reason=(
                "the molecule has a linear group (an angle near 180°, as in a nitrile or an "
                f"alkyne), and the measured spread under {SPREAD_CHANGES} for molecules with "
                f"one ({value:.2f} cm⁻¹, from the release's invariance record) exceeds the "
                f"licence line of {line:g} cm⁻¹, {STILL_PRINTED}"
            ),
        )
    return Withheld(
        spread_cm=value,
        note=(
            f"molecules without a linear group moved by up to {value:.2f} cm⁻¹ under "
            f"{spread.change}, more than the licence line"
        ),
        reason=(
            "the molecule has no linear group, and the measured spread under "
            f"{spread.change} for molecules without one ({value:.2f} cm⁻¹, from the "
            f"release's invariance record) exceeds the licence line of {line:g} cm⁻¹, "
            f"{STILL_PRINTED}"
        ),
    )


UNMEASURED = Withheld(
    spread_cm=None,
    note=(
        "the molecule has a linear group, and the spread of molecules with one under "
        f"{CHANGES} was not measured for this release"
    ),
    reason=(
        "the molecule has a linear group (an angle near 180°, as in a nitrile or an "
        f"alkyne), and the spread under {SPREAD_CHANGES} was not measured for this "
        f"release on a molecule with one, {STILL_PRINTED}"
    ),
)


def withheld_by_spread(record: dict | None, line: float, *, linear_group: bool) -> Withheld | None:
    """Why a molecule's bands are not licensed for its group's spread; None when they may be: the largest spread of its group above the
    line withholds the licence; a molecule with a linear group is withheld also where its group was not measured on every change."""
    spread = group_spread(record, linear_group=linear_group)
    if spread.spread_cm is not None and spread.spread_cm > line:
        return _too_far(spread, line, linear_group=linear_group)
    if linear_group and not spread.complete:
        return UNMEASURED
    return None


def condition(*, linear_group: bool) -> str:
    """The licence's condition on the spread, in the words of aromir's statement: the molecule's group moved by no more than the line."""
    group = "with" if linear_group else "without"
    return (f"molecules {group} a linear group moved by no more than the licence line "
            f"under {SPREAD_CHANGES} in the release's invariance record")
