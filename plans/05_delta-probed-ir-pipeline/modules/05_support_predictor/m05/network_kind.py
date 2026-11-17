"""A ΔH-network's kind (decision 66, 17 Nov 2026; GoalGathering/notes/Design_2026-11-17_Measurement_and_Release_Networks.md).

A version is a pair with one recipe. Its **measurement networks** train without the hold-outs: every error, licence and promotion is
read on them. Its **release networks** train on every molecule with labels of the carried kind, the hold-outs and their twins included:
they are what the pipeline and the public package ship, and they have no held-out error of their own.

'Trained on' is not 'fitted on': under the recipe's inner validation each seed's network takes gradient steps on a random part of its
pool (85 % under the carried recipe's --inner-val 0.15) and is stopped on the rest, a different part per seed. A release network's
pool holds every molecule, so every molecule is fitted or stopped on by every release network; as each seed draws its own part, not
every molecule is fitted by every network, and a share inner_val^seeds of them (0.15³ ≈ 0.3 % for three seeds) by none. The
certificate and the trainer's log say so in one wording (`fitting_sentence`); whether a training used its whole pool is
`trained_on_whole_pool`.

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


_SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _about_percent(share: float) -> str:
    """A share as a rounded percentage: whole percents from 1 % up, one significant digit below."""
    percent = 100 * share
    return f"{percent:.0f}" if percent >= 1 else f"{percent:.1g}"


def fitting_sentence(networks: int, inner_val: float) -> str:
    """How each of `networks` networks used the molecules it trained on under inner validation `inner_val`: fitted on a random
    1 - inner_val of them and stopped on the rest, a part drawn per seed, so a molecule is fitted by none with probability
    inner_val ** networks. Without inner validation each is fitted on all of them. One wording, for the certificate and the trainer's
    log (review of 17 Nov 2026: 'fitted by most of the networks' was false — with three, 0.85³ ≈ 61 % are fitted by all)."""
    if networks < 1 or not 0 <= inner_val < 1:
        raise ValueError(f"{networks} networks with inner validation {inner_val}: at least one network and a share in [0, 1)")
    if not inner_val:
        return f"each of the {networks} networks is fitted on all of the molecules, none kept back for stopping"
    fitted, stopped = f"{100 * (1 - inner_val):g}", f"{100 * inner_val:g}"
    return (f"each of the {networks} networks is fitted on a random {fitted} % of the molecules and stopped on the other {stopped} %, a "
            f"different {stopped} % per seed, so not every molecule is fitted by every network (with {networks} networks about "
            f"{inner_val:g}{str(networks).translate(_SUPERSCRIPT)} ≈ {_about_percent(inner_val ** networks)} % by none)")


def trained_on_whole_pool(record: Mapping, n: int) -> bool:
    """Whether a network saved at size `n` trained on every molecule of its training record's pool. The trainer reads `--sizes`
    against the pool before the hold-out twins leave it (`rungC_train.pool_sizes` before `drop_twins`) and trains on `pool[:n]`, so
    `--sizes all` on 1,082 molecules of which two are twins saves n1082 beside a pool of 1,080 (v1.4; chain 42: n978, pool 976): the
    whole pool was used where n reaches the pool, not only where it equals it."""
    pool = record.get("pool")
    if not isinstance(pool, int):
        raise ValueError(f"the training record states no pool size ({pool!r}); whether the whole pool was used cannot be read")
    return n >= pool
