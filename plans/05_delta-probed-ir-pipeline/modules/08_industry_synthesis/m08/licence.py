"""The licence of the learned correction (decision 65, the user 29 Oct 2026): a mode family is licensed where the carried ΔH network's
seed-mean error is within decision 53's 3 cm⁻¹ on both hold-outs — read from the network's own evaluation records, never typed in. The
licence holds at the level the network is measured at, the DFT proxy (ωB97X); no coupled-cluster licence exists. It replaces the layer-B
rule of the proof-of-learning pre-registration (25 Sep 2026), which was written before the ΔH network."""
from __future__ import annotations

from .accuracy import HOLDOUTS, LICENCE_LINE_CM, carried_accuracy

# isort: split
from promotion_read import FAMILIES  # probes/, on the path through m08.pipeline

RULE = ("decision 65 (29 Oct 2026): a mode family is licensed where the carried ΔH network's seed-mean error is within 3 cm⁻¹ "
        "(decision 53) on both hold-outs, at the DFT-proxy level its evaluation measures; it replaces the layer-B rule of 25 Sep 2026")
RULE_SOURCE = "README.md, decision 65"


def _errors(family: str, errors: dict[str, dict[str, float]]) -> str:
    return f"{family} ({' / '.join(str(v) for v in errors[family].values())})"


def state(accuracy: dict | None = None) -> dict:
    """The licence under the carried network's evaluation records, or under `accuracy` (a `network_accuracy` result) when given."""
    acc = carried_accuracy() if accuracy is None else accuracy
    errors = {f: {h: acc["holdouts"][h]["readouts"][f]["mean"] for h in HOLDOUTS} for f in FAMILIES}
    licensed = [f for f in FAMILIES if all(v <= LICENCE_LINE_CM for v in errors[f].values())]
    statement = ("licensed at the DFT proxy: " + (", ".join(_errors(f, errors) for f in licensed) or "no family")
                 + "; not licensed: " + (", ".join(_errors(f, errors) for f in FAMILIES if f not in licensed) or "none")
                 + f" — seed-mean error on hold-outs (a) / (b) in cm⁻¹ against {LICENCE_LINE_CM:g}; no coupled-cluster licence")
    return dict(licensed_families=licensed, errors=errors, line_cm=LICENCE_LINE_CM, rule=RULE, rule_source=RULE_SOURCE,
                sources=acc["sources"], statement=statement)
