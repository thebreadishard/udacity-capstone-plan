"""A ΔH-network's kind (decision 66, 17 Nov 2026; GoalGathering/notes/Design_2026-11-17_Measurement_and_Release_Networks.md).

A version is a pair with one recipe. Its **measurement networks** train without the hold-outs: every error, licence and promotion is
read on them. Its **release networks** train on every molecule with labels of the carried kind, the hold-outs and their twins included:
they are what the pipeline and the public package ship, and they have no held-out error of their own.

The kind is a setting of the training (`rungC_train.py --network-kind`) and is stored in the checkpoint's own arguments; every other
place — the training record, an evaluation record, the model registry — repeats what the checkpoint says. A checkpoint, record or
registry entry written before decision 66 states no kind: every network trained until then left the hold-outs out, so it is a
measurement network. That default is stated here and nowhere else (`stated_kind`).

No heavy import: module 08 and the readers under probes/ use this file without torch."""
from __future__ import annotations

from collections.abc import Mapping

MEASUREMENT = "measurement"
RELEASE = "release"
KINDS = (MEASUREMENT, RELEASE)
FIELD = "network_kind"
INSAMPLE_PREFIX = "insample_"          # the evaluator's set names for a release network's read on molecules it trained on


class ReleaseNetworkError(ValueError):
    """A hold-out error was asked of a release network, which trained on the hold-out."""


def stated_kind(holder: Mapping, what: str) -> str:
    """The kind `holder` states — a checkpoint's arguments, a record, a registry entry; without the field it predates decision 66 and
    is a measurement network. A value outside KINDS is refused."""
    kind = holder.get(FIELD, MEASUREMENT)
    if kind not in KINDS:
        raise ValueError(f"{what} states {FIELD} {kind!r}; one of {KINDS}")
    return kind


def kind_of_checkpoint(ck: object, what: str = "the checkpoint") -> str:
    """The kind a saved network was trained as, from its own saved arguments. A checkpoint without training arguments (a pretrained
    body, a scorer's state) never had a hold-out pool to train on and is a measurement network."""
    args = ck.get("args") if isinstance(ck, Mapping) else None
    return stated_kind(args if isinstance(args, Mapping) else {}, what)


def refuse_release(kind: str, source: str, reading: str) -> None:
    """Raise when `kind` is release: `reading` (what was about to be read, as a noun phrase) would be an in-sample number."""
    if kind == RELEASE:
        raise ReleaseNetworkError(
            f"{source} is a release network (decision 66): it trained on every molecule with labels, the hold-outs included, so "
            f"{reading} would be an in-sample number under a hold-out's name; read it on the version's measurement networks")


def insample_name(name: str) -> str:
    """The set name a release network's in-sample read is written under: never a hold-out's own name."""
    return f"{INSAMPLE_PREFIX}{name}"
