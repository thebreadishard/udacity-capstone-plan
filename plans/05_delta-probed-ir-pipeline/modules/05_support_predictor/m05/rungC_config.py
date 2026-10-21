"""The rung-C trainer's settings as one validated, frozen object (TASKS 72, 16 Oct 2026).

`rungC_train.py` grew one flag per lever; a flag that did nothing in a combination was ignored without a word (`--kdiag-weight` outside
`--aux both`, the hybrid-head switches under the Cartesian head, `--patience` without an inner validation set), and `--save-model` with the
wrong head was refused only after the first seed had trained. `TrainConfig` refuses every such combination before any data is loaded and
lists all of them at once. Field names are the command line's `dest` names, so a checkpoint's `args` and a record's fields keep their keys.

The defaults are still the registered recipe C1 of 27 Sep 2026; the carried recipe is `probes/chain_runner.RECIPE_V11`. Moving the defaults
to the carried recipe waits until no queued chain relies on a default (TASKS 72)."""
from __future__ import annotations

import argparse
import math
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Literal

from learning_curve_layerA import FAMILIES
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from rungC_equivariant import AGGREGATION, AGGREGATIONS, AUX_WEIGHT, N_BLOCKS, N_S
from rungC_targets import LAM_REL

KRING_WEIGHT = 1.0
HYBRID_HIDDEN = 128
EPOCHS = 60
SMOKE_EPOCHS = 2
SMOKE_POOL = 5
SMOKE_HOLDOUT = 3
NAMED_SIZES = ("all", "half")
HYBRID_ONLY = {"sqm_scale": "--sqm-scale", "pair_features": "--pair-features", "parity_odd_mixed": "--parity-odd-mixed",
               "hinge_feature": "--hinge-feature", "save_model": "--save-model"}


class TrainConfig(BaseModel):
    """Every setting of one trainer run. Construct it with `parse_config`, or directly in tests; it is valid or it does not exist."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    molecules: str
    out_prefix: str
    threads: int = Field(8, ge=1)
    sizes: str = "45,100,175"
    pool_layers: str = "A,A2"
    seeds: str = "0,1,2"
    epochs: int | None = Field(None, ge=1)
    lr: float = Field(1e-3, gt=0)
    split: Literal["e6", "layerB"] = "e6"
    use_analytic: bool = False
    smoke: bool = False
    aux_weight: float = Field(AUX_WEIGHT, ge=0)
    loss: Literal["registered", "internal"] = "registered"
    scale: Literal["rms", "class"] = "rms"
    inner_val: float = Field(0.0, ge=0, lt=1)
    patience: int = Field(0, ge=0)
    kring_weight: float = Field(KRING_WEIGHT, ge=0)
    hinge_feature: bool = False
    kdiag_mode: Literal["all", "family", "family-low"] = "all"
    kdiag_weight: float = Field(0.0, ge=0)
    save_model: bool = False
    size_test_min_atoms: int = Field(0, ge=0)
    pool_max_atoms: int = Field(0, ge=0)
    exclude_ids_file: str | None = None
    aux: Literal["all", "pattern", "kring", "both"] = "all"
    zero_hlow: bool = False
    tensor_input: bool = False
    head: Literal["cartesian", "hybrid"] = "cartesian"
    sqm_scale: bool = False
    pair_features: bool = False
    parity_odd_mixed: bool = False
    hybrid_hidden: int = Field(HYBRID_HIDDEN, ge=1)
    pattern: Literal["c", "d", "e", "f"] = "c"
    aux_target: Literal["projected", "ls", "kfit"] = "projected"
    ls_lam: float = Field(LAM_REL, ge=0)
    body_blocks: int = Field(N_BLOCKS, ge=1)
    body_width: int = Field(N_S, ge=1)
    overfit_one: str | None = None
    pretrained: str | None = None
    aggregation: str = AGGREGATION
    pretrained_elements: list[int] | None = None
    family_scale: str | None = None

    @field_validator("family_scale")
    @classmethod
    def _family_scale_list(cls, v: str | None) -> str | None:
        if v is not None:
            parse_family_scale(v)
        return v

    @field_validator("aggregation")
    @classmethod
    def _known_aggregation(cls, v: str) -> str:
        if v not in AGGREGATIONS:
            raise ValueError(f"aggregation {v!r}: one of {list(AGGREGATIONS)}")
        return v

    @field_validator("sizes")
    @classmethod
    def _size_list(cls, v: str) -> str:
        bad = [s for s in v.split(",") if s not in NAMED_SIZES and not (s.isdigit() and int(s) > 0)]
        if bad:
            raise ValueError(f"sizes {v!r}: positive integers or {NAMED_SIZES}, not {bad}")
        return v

    @field_validator("seeds")
    @classmethod
    def _seed_list(cls, v: str) -> str:
        if not all(s.isdigit() for s in v.split(",")):
            raise ValueError(f"seeds {v!r}: comma-separated non-negative integers")
        return v

    @model_validator(mode="after")
    def _combinations(self) -> TrainConfig:
        if problems := self.conflicts():
            raise ValueError("options that do not combine:\n  - " + "\n  - ".join(problems))
        return self

    def conflicts(self) -> list[str]:
        """Every combination in which an option would do nothing, or something other than its name says."""
        hybrid_only = [f"{flag} works only with --head hybrid" for field, flag in HYBRID_ONLY.items() if self.head != "hybrid" and getattr(self, field)]
        return hybrid_only + [reason for applies, reason in CONFLICTS if applies(self)]

    def missing_files(self) -> list[str]:
        """Input files the run names that do not exist — checked before the corpus is loaded."""
        return [f"{flag} {path}: not found" for flag, path in (("--exclude-ids-file", self.exclude_ids_file), ("--pretrained", self.pretrained))
                if path and not Path(path).is_file()]

    def resolved(self) -> TrainConfig:
        """The settings the run trains with: the epoch default of the mode (2 under --smoke, else 60), and --overfit-one's documented
        diagnostic recipe (no inner validation, no early stopping)."""
        update: dict = {"epochs": self.epochs or (SMOKE_EPOCHS if self.smoke else EPOCHS)}
        if self.overfit_one:
            update |= {"inner_val": 0.0, "patience": 0}
        return self.model_copy(update=update)

    @property
    def seed_list(self) -> list[int]:
        return [int(s) for s in self.seeds.split(",")]

    @property
    def family_scales(self) -> dict[str, float]:
        """The --family-scale factors per mode family; empty when the labels are not distorted."""
        return parse_family_scale(self.family_scale) if self.family_scale else {}


def parse_family_scale(text: str) -> dict[str, float]:
    """'CH-oop=-0.43,other=-1.16' as {family: factor}; refuses an unknown or repeated family and a factor that is not a finite number."""
    out: dict[str, float] = {}
    for item in text.split(","):
        name, sep, value = item.partition("=")
        if not sep or name not in FAMILIES:
            raise ValueError(f"family_scale {item!r}: <family>=<factor> with a family of {FAMILIES}")
        if name in out:
            raise ValueError(f"family_scale: {name} given twice")
        try:
            factor = float(value)
        except ValueError:
            raise ValueError(f"family_scale {item!r}: the factor is not a number") from None
        if not math.isfinite(factor):
            raise ValueError(f"family_scale {item!r}: the factor is not finite")
        out[name] = factor
    return out


CONFLICTS: tuple[tuple[Callable[[TrainConfig], object], str], ...] = (   # (truthy when the conflict applies, the reason)
    (lambda c: c.head == "hybrid" and c.aux not in ("pattern", "kring", "both"),
     "--head hybrid needs --aux pattern, kring or both: its output lives on the pattern"),
    (lambda c: c.head != "hybrid" and c.hybrid_hidden != HYBRID_HIDDEN,
     "--hybrid-hidden sets the width of the hybrid head; the Cartesian head has none"),
    (lambda c: c.parity_odd_mixed and c.pair_features,
     "--parity-odd-mixed with --pair-features: rung B's pair features carry signed primitive values (parity-odd)"),
    (lambda c: c.head == "hybrid" and c.scale == "class",
     "--scale class sets the Cartesian head's output scale; the hybrid head has none"),
    (lambda c: c.aux != "both" and (c.kdiag_weight or c.kring_weight != KRING_WEIGHT),
     "--kring-weight and --kdiag-weight weigh terms inside --aux both only"),
    (lambda c: c.kdiag_mode != "all" and not c.kdiag_weight,
     "--kdiag-mode chooses the form of a K-diagonal term that --kdiag-weight 0 switches off"),
    (lambda c: c.aux_target != "projected" and c.aux not in ("pattern", "both"),
     "--aux-target replaces the pattern term's target; --aux all/kring have no pattern term"),
    (lambda c: c.ls_lam != LAM_REL and c.aux_target == "projected",
     "--ls-lam is the ridge of the ls/kfit targets; the projected target has none"),
    (lambda c: c.loss == "internal" and c.aux_weight != AUX_WEIGHT,
     "--aux-weight weighs the internal term beside the Cartesian one; --loss internal trains on the internal term alone"),
    (lambda c: c.patience and not c.inner_val,
     "--patience stops on the inner validation set; --inner-val 0 has none, so early stopping would be off"),
    (lambda c: c.pretrained and c.tensor_input,
     "--tensor-input is a fresh-body variant; the pretrained bodies carry no weights for it"),
    (lambda c: c.pretrained and (c.body_blocks, c.body_width) != (N_BLOCKS, N_S),
     f"--body-blocks/--body-width do not fit a pretrained body ({N_BLOCKS}, {N_S})"),
    (lambda c: c.pretrained_elements and not c.pretrained,
     "--pretrained-elements describes a --pretrained checkpoint, and none is given"),
    (lambda c: c.split == "layerB" and (c.size_test_min_atoms or c.pool_max_atoms or c.exclude_ids_file),
     "--split layerB builds its own pool; the size split and --exclude-ids-file act on the e6 pool"),
    (lambda c: c.smoke and c.overfit_one,
     "--smoke and --overfit-one each set the pool, sizes and hold-outs; choose one"),
)


def build_parser(description: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--sizes", default="45,100,175", help="the pair model's registered sizes; 'all' = the whole pool, 'half' = half of it")
    ap.add_argument("--pool-layers", default="A,A2",
                    help="split e6: keep only these layers in the pool (the registered floor's pool was layer A + A2; layer B entered the corpus later)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--epochs", type=int, default=None, help=f"default {EPOCHS} ({SMOKE_EPOCHS} under --smoke unless given)")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--split", default="e6", help="e6 (default) or layerB, as in e7_rungB_pairs.py")
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--smoke", action="store_true",
                    help=f"{SMOKE_POOL} pool molecules, {SMOKE_EPOCHS} epochs, seed 0, hold-outs cut to {SMOKE_HOLDOUT} each: mechanics only, never a result")
    ap.add_argument("--aux-weight", type=float, default=AUX_WEIGHT, help="weight of the internal term beside the Cartesian one (registered 0.1)")
    ap.add_argument("--loss", default="registered", choices=["registered", "internal"], help="'internal' = the relative internal-ΔF term alone")
    ap.add_argument("--scale", default="rms", choices=["rms", "class"],
                    help="Cartesian head: output scale = training RMS ΔH (registered) or one per entry class")
    ap.add_argument("--inner-val", type=float, default=0.0, help="fraction of the training ids held out per seed as inner validation")
    ap.add_argument("--patience", type=int, default=0, help="early stopping on the inner validation term, best state restored (0 = off)")
    ap.add_argument("--kring-weight", type=float, default=KRING_WEIGHT, help="weight of the kring term inside --aux both (the pattern term keeps weight 1)")
    ap.add_argument("--hinge-feature", action="store_true", help="hybrid head: train the hinge-class embedding of the body "
                    "(ring4 / ring5 / linear / rotor / sp3 per atom, from the bond graph); without it the embedding stays frozen at zero")
    ap.add_argument("--kdiag-mode", default="all", choices=["all", "family", "family-low"],
                    help="the K-diagonal term: 'all' = one relative mse over all modes; 'family' = the mean over mode families of the per-family "
                         "relative mse, so that CH-oop and other weigh as much as the C–H stretches; 'family-low' = as 'family' with the 'other' "
                         "modes below 700 cm⁻¹ as their own family")
    ap.add_argument("--kdiag-weight", type=float, default=0.0, help="weight of a term on the diagonal of K over all modes inside --aux both (0 = off)")
    ap.add_argument("--save-model", action="store_true", help="hybrid head: save the trained model per size and seed next to the record")
    ap.add_argument("--size-test-min-atoms", type=int, default=0, help="pool molecules with at least this many atoms become hold-out (s) and never train")
    ap.add_argument("--pool-max-atoms", type=int, default=0, help="train only on pool molecules with at most this many atoms")
    ap.add_argument("--exclude-ids-file", default=None, help="coverage ablation: ids (one per line) dropped from the training pool; hold-outs untouched")
    ap.add_argument("--aux", default="all", choices=["all", "pattern", "kring", "both"],
                    help="internal term: 'all' (registered) = every entry of B⁺ᵀ ΔH B⁺; 'pattern' = the pair model's pattern only, one "
                         "standardisation scale per pair class; 'kring' = the ring-mode block of K; 'both' = pattern + kring")
    ap.add_argument("--zero-hlow", action="store_true", help="diagnostic: zero the B3LYP Hessian input channels; the ratio must collapse towards the zero rule")
    ap.add_argument("--tensor-input", action="store_true", help="the B3LYP 3×3 pair blocks as rank-2 equivariant edge features (fresh body only)")
    ap.add_argument("--head", default="cartesian", choices=["cartesian", "hybrid"],
                    help="'hybrid' = equivariant encoder → ΔF on the pair model's pattern (with F_low,pq/pp/qq as inputs) → ΔH = Bᵀ ΔF B")
    ap.add_argument("--sqm-scale", action="store_true", help="hybrid head: add α_class · F_low,pq to the residual (one α per pair class, initialised at 0)")
    ap.add_argument("--pair-features", action="store_true", help="hybrid head: rung B's 66 pair features beside the encoder's features")
    ap.add_argument("--parity-odd-mixed", action="store_true", help="hybrid head (TASKS 52): reflection-equivariant — a pair of a parity-odd "
                    "primitive (dihedral, wag) and an even one gets ΔF = r · sin(odd value) and |F_pq| as input; off = the carried models' head")
    ap.add_argument("--hybrid-hidden", type=int, default=HYBRID_HIDDEN, help="hybrid head: width of its MLP")
    ap.add_argument("--pattern", default="c", choices=["c", "d", "e", "f"], help="'c' = the registered pattern; 'd' = (c) + disjoint pairs one bond "
                    "apart; 'e' / 'f' = up to two / three bonds apart")
    ap.add_argument("--aux-target", default="projected", choices=["projected", "ls", "kfit"],
                    help="target of the pattern term — 'projected' = B⁺ᵀ ΔH B⁺ on the pattern (registered), 'ls' = the mass-weighted least-squares "
                         "ΔF supported on the pattern, 'kfit' = the same in the read-out's metric, the mode-basis K; both ridge-anchored by --ls-lam")
    ap.add_argument("--ls-lam", type=float, default=LAM_REL, help="ridge of the ls/kfit target toward the projected truth, relative to the normal "
                    "matrix's mean diagonal (0 = plain least squares — explodes on redundant internals)")
    ap.add_argument("--body-blocks", type=int, default=N_BLOCKS, help=f"interaction blocks of a fresh body (registered: {N_BLOCKS})")
    ap.add_argument("--body-width", type=int, default=N_S, help=f"scalar and vector channels of a fresh body (registered: {N_S})")
    ap.add_argument("--overfit-one", default=None, metavar="ID",
                    help="diagnostic: pool, size and both hold-outs = this one molecule; no inner validation, no early stopping; must reach ratio << 0.1")
    ap.add_argument("--pretrained", default=None, help="a `rungC_pretrain.py` checkpoint; its body is loaded, the head re-initialised per seed")
    ap.add_argument("--aggregation", default=AGGREGATION, choices=list(AGGREGATIONS),
                    help="neighbour-message pooling in the body: mean (default since 28 Sep) or sum (the body registered on 25 Sep)")
    ap.add_argument("--family-scale", default=None, metavar="FAMILY=FACTOR,...",
                    help="proxy check (a): multiply each named mode family's diagonal block of the training label (low level's mode basis) by its "
                         "factor; the read-outs still compare with the undistorted label")
    ap.add_argument("--pretrained-elements", default=None,
                    help="comma list of atomic numbers a pre-28-Sep checkpoint was trained on (Hessian QM9: 1,6,7,8,9); newer checkpoints carry it")
    return ap


def _fields(ns: argparse.Namespace) -> dict:
    fields = dict(vars(ns))
    if fields["pretrained_elements"]:
        fields["pretrained_elements"] = [int(z) for z in fields["pretrained_elements"].split(",")]
    return fields


def config_from_argv(argv: Sequence[str], description: str = "rung C trainer") -> TrainConfig:
    """The command line as a validated config, combinations only: input files are checked where the run starts (`parse_config`), because a
    chain's relative paths resolve in its step's folder and an earlier step may write them."""
    return TrainConfig(**_fields(build_parser(description).parse_args(argv)))


def parse_config(argv: Sequence[str] | None = None, description: str = "rung C trainer") -> TrainConfig:
    """The command line as a validated config; a conflict or a missing input file ends the program with every reason listed."""
    ap = build_parser(description)
    try:
        cfg = TrainConfig(**_fields(ap.parse_args(argv)))
    except ValueError as e:
        ap.error(str(e))
    if missing := cfg.missing_files():
        ap.error("; ".join(missing))
    return cfg
