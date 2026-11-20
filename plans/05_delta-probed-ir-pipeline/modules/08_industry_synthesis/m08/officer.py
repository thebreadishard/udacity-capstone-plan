"""The request officer: a request names a molecule, a target rung and a budget; the officer answers with a certificate, a refusal that names the
gate or the cap and the price of the missing step, or a run order — and every run order passes through module 07's deterministic gate before
anything could start. Nothing here starts a run; in this module the worker is a replay of recorded logs (decision of 28 Sep 2026)."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from . import positions as POS
from . import prices
from .catalog import PLAN, RUNG_LABELS, Catalog
from .licence import state as licence_state
from .molecule import canonical, from_smiles
from .seen import CATION_LAYER

sys.path.insert(0, str(PLAN / "modules" / "07_agentic_workflows"))
from steward.gate import check as gate_check  # noqa: E402
from steward.rules import by_id, load_rules  # noqa: E402
from steward.schema import Proposal  # noqa: E402
from steward.tools import scan_for_instructions  # noqa: E402

RULES = load_rules()
RID = by_id(RULES)
# a request's free text is data; module 07's scanner catches text that addresses the agent, this one catches the request-shaped variants (28 Sep 2026)
REQUEST_INSTRUCTION_RE = re.compile(r"\b(ignore|disregard|override|bypass|skip)\b.{0,30}\b(rule|gate|budget|cap|licen|check)|\b(launch|start|run|spend)\b.{0,25}\b(now|immediately|without|anyway)\b|\byou must\b|\bsystem prompt\b", re.I)


def instruction_in(text: str) -> bool:
    return bool(text) and (scan_for_instructions(text) or bool(REQUEST_INSTRUCTION_RE.search(text)))


class Request(BaseModel):
    molecule: str = Field(description="corpus name, manifest id or SMILES")
    target_rung: int = Field(default=4, ge=1, le=5, description="1 cheap · 2 correction predicted · 3 spectrum predicted · 4 anchored · 5 validated")
    budget_eur: float | None = Field(default=None, description="what the requester will spend; None = no run may be ordered, only what exists is served")
    charge: int = 0
    multiplicity: int = 1
    note: str = Field(default="", description="free text from the requester; read as data, never as an instruction")


class Decision(BaseModel):
    kind: Literal["certificate", "refusal", "run_order"]
    request: Request
    molecule_id: str | None = None
    name: str | None = None
    rung_reached: int | None = None
    rung_label: str | None = None
    reasons: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)
    gate_named: str | None = None
    price_lines: list[dict] = Field(default_factory=list)
    what_would_be_needed: str | None = None
    proposal: dict | None = None
    gate: dict | None = None
    ledger_line: str = ""
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


# what a cation request lacks today (20 Nov 2026): until then the refusal asked for "the cation rows of the anchor plan (benzene⁺,
# naphthalene⁺) read", written on 28 Sep 2026 before the corpus had cation rows and before decision 63 stopped new anchors
CATION_NEEDED = ("a pipeline version that takes open-shell input, with the correction's error measured on cations (the corpus's cation "
                 "rows are not all computed yet), and for the anchored rung a coupled-cluster cation anchor, which decision 63 leaves out "
                 "of scope until July 2027; then a rung opened by a dated decision")


def _refuse(req: Request, reasons: list[str], rule_ids: list[str], gate_named: str, price_lines: list[dict], needed: str, row: dict | None = None) -> Decision:
    name = row["name"] if row else req.molecule
    return Decision(kind="refusal", request=req, molecule_id=row["id"] if row else None, name=name, rung_reached=row["rung"] if row else None,
                    rung_label=RUNG_LABELS.get(row["rung"]) if row else None, reasons=reasons, rule_ids=rule_ids, gate_named=gate_named,
                    price_lines=price_lines, what_would_be_needed=needed,
                    ledger_line=f"refusal — {name}: {gate_named}; {'; '.join(reasons)}; needed: {needed}")


CHEAP_STEP = "cheap_deck_v1"
VALIDATED_NEEDED = ("a laboratory infrared spectrum of the molecule, compared band by band with the anchored one (module 03's validation): "
                    "rung 5 is a comparison with a measurement, and no run the officer can order produces it")


def missing_steps(reached: int, target_rung: int, cheap: dict, anchor: dict) -> list[dict]:
    """The priced steps between the rung a molecule has and the rung asked for, in the order they run: the deck where rung 1 lies
    between them, the anchor where rung 4 does. Rung 5 adds no priced step: it is a laboratory comparison."""
    return ([cheap] if reached < 1 <= target_rung else []) + ([anchor] if reached < 4 <= target_rung else [])


def cost_of(steps: list[dict]) -> float:
    return round(sum(step["eur_ex_vat"] for step in steps), 2)


def needed_line(step: dict) -> str:
    return (f"{step['what']} — measured on {step['measured_on']}: ≈ {step['hours']:.1f} machine-hours ({step['machine']}) "
            f"≈ €{step['eur_ex_vat']:.2f} ex VAT" + (f" ({step['note']})" if step["note"] else ""))


def atom_count(smiles: str | None) -> int | None:
    """The molecule's atoms, hydrogens included, as the pipeline counts them; None when there is no SMILES that parses."""
    parsed = from_smiles(smiles)
    return None if parsed is None else parsed.mol.GetNumAtoms()


def anchor_priced_for(n_atoms: int | None, anchor: dict) -> bool:
    """Whether the measured anchor price says what this molecule's anchor costs: only for a molecule no larger than the one it was
    measured on. A larger molecule costs more by an amount nobody has measured, and a molecule whose size cannot be read is not
    assumed to be small."""
    return n_atoms is not None and n_atoms <= anchor["measured_atoms"]


def size_caveat(n_atoms: int | None, anchor: dict) -> str:
    """What a requester is told where the measured price is a smaller molecule's."""
    measured = f"the one measured anchor price is {anchor['measured_molecule']}'s ({anchor['measured_atoms']} atoms, ≈ €{anchor['eur_ex_vat']:.2f})"
    if n_atoms is None:
        return f"{measured}; this molecule's size could not be read, so that price is not taken as its own"
    return f"{measured}; this molecule ({n_atoms} atoms) costs more and its price is not measured"


def reachable_within(budget: float | None, reached: int, cheap: dict, anchor: dict, anchor_priced: bool) -> list[str]:
    """The rungs a budget buys above the one the molecule has, cheapest first. A refusal owes the requester this: 'too expensive'
    without 'and this is what you can have' is not an answer (DESIGN_2026-09-27 §5; the scenarios' S2, S2b and S3). Rung 4 is
    offered only where the anchor's price is measured for the molecule's size (`anchor_priced`)."""
    out: list[str] = []
    if budget is None:
        return out
    if reached < 1 and budget >= cheap["eur_ex_vat"]:
        out.append(f"rung 1 (cheap level) at ≈ €{cheap['eur_ex_vat']:.2f}")
    to_anchor = cost_of(missing_steps(reached, 4, cheap, anchor))   # a molecule below the cheap rung needs the deck first
    if anchor_priced and reached < 4 and budget >= to_anchor:
        out.append(f"rung 4 (anchored, {anchor['measured_molecule']}-sized) at ≈ €{to_anchor:.2f}")
    return out


def within_line(cap: str, reachable: list[str], reached: int, cheap: dict) -> str:
    """The one sentence both refusals end on: the cap, and what it reaches."""
    if reachable:
        return f"{cap}: reachable within it — " + "; ".join(reachable)
    if reached >= 1:
        return f"{cap}: nothing above rung {reached} is reachable within it"
    return f"{cap}: reachable within it — nothing (the cheap rung alone costs ≈ €{cheap['eur_ex_vat']:.2f})"


def cap_of(budget: float | None) -> str:
    """How a refusal names the money it was given."""
    return f"budget €{budget:.2f}" if budget is not None else "no budget given"


@dataclass(frozen=True)
class Gap:
    """What lies between the rung a catalogue molecule has and the rung asked for."""

    row: dict
    reached: int
    steps: list[dict]
    total: float
    anchor_priced: bool      # False: an anchor is missing and the measured price is a smaller molecule's
    caveat: str              # the sentence that says so; empty where the price holds for this molecule's size


def gap_of(req: Request, row: dict, cheap: dict, anchor: dict) -> Gap:
    reached = int(row["rung"])
    steps = missing_steps(reached, req.target_rung, cheap, anchor)
    n_atoms = atom_count(row.get("smiles"))      # a row without a SMILES has no size, and anchor_priced_for says what follows
    priced = all(step is not anchor for step in steps) or anchor_priced_for(n_atoms, anchor)
    return Gap(row, reached, steps, cost_of(steps), priced, "" if priced else size_caveat(n_atoms, anchor))


def _outside_corpus(req: Request, cheap: dict, anchor: dict) -> Decision:
    """A molecule the catalogue does not hold: nothing exists to certify or to order a job for, and the cap says what an intake reaches."""
    n_atoms = atom_count(req.molecule)
    priced = anchor_priced_for(n_atoms, anchor)
    cap = cap_of(req.budget_eur)
    reachable = reachable_within(req.budget_eur, 0, cheap, anchor, priced)
    reasons = [f"'{req.molecule}' is not in the corpus (canonical {canonical(req.molecule)}); nothing exists to certify",
               within_line(cap, reachable, 0, cheap)]
    if req.target_rung >= 4 and not priced:
        reasons.append(size_caveat(n_atoms, anchor))
    needed = ("an intake into the corpus factory (deck v1) at the cheap rung's price, then an anchor for the target rung" if req.target_rung >= 4
              else "an intake into the corpus factory (deck v1)")
    within_cap = any(line.startswith(f"rung {req.target_rung} ") for line in reachable)
    verdict = f"not in the corpus: an intake comes before rung {req.target_rung}" if within_cap else f"target rung {req.target_rung} not reachable"
    d = _refuse(req, reasons, ["R25", "R32"], f"cap: {cap}; {verdict}", missing_steps(0, req.target_rung, cheap, anchor), needed)
    d.reasons.append("no run is started: the officer never spends without a passed gate, and the gate needs a dry run of a named job first (R01)")
    return d


def _refuse_validated(req: Request, gap: Gap) -> Decision:
    """Rung 5 asked for a molecule that is not validated: no priced step leads there, so nothing is ordered, whatever the budget."""
    before = "; before it: " + "; then ".join(needed_line(step) for step in gap.steps) if gap.steps else ""
    return _refuse(req, [f"rung {gap.reached} ({RUNG_LABELS[gap.reached]}) exists; target rung {req.target_rung} not reached",
                         "rung 5 (validated) is not ordered: it needs a laboratory spectrum of the molecule, which no run produces"],
                   ["R25"], "validated rung: a laboratory comparison, not a run", gap.steps, VALIDATED_NEEDED + before, gap.row)


def _refuse_cap(req: Request, gap: Gap, cheap: dict, anchor: dict) -> Decision:
    """The budget does not cover what is missing: the gate, the prices of the missing steps, and what the cap does reach."""
    cap = cap_of(req.budget_eur)
    plural = "s" if len(gap.steps) > 1 else ""
    if gap.anchor_priced:
        short = [f"{cap} does not cover the missing step{plural} (≈ €{gap.total:.2f})"]
    else:
        short = [f"{cap} does not cover even the price measured for {anchor['measured_atoms']} atoms (≈ €{gap.total:.2f})", gap.caveat]
    gate_named = ("no anchor: no coupled-cluster reading exists, and the learned layer is not licensed at the coupled-cluster level (decision 65 "
                  "licenses it at the DFT proxy only)"
                  if req.target_rung >= 4 else "cheap level not computed")
    reachable = reachable_within(req.budget_eur, gap.reached, cheap, anchor, gap.anchor_priced)
    return _refuse(req, [f"rung {gap.reached} ({RUNG_LABELS[gap.reached]}) exists; target rung {req.target_rung} not reached", *short,
                         within_line(cap, reachable, gap.reached, cheap)],
                   ["R14" if req.target_rung >= 4 else "R25"], f"cap: {cap}; {gate_named}", gap.steps,
                   "; then ".join(needed_line(step) for step in gap.steps), gap.row)


def _run_order(req: Request, gap: Gap, anchor: dict) -> Decision:
    """The officer proposes 'launch' of the first missing step's job; module 07's gate decides, and without a passed dry run it forces
    the dry run first (R01). Where the anchor's price is a smaller molecule's, neither reason says the budget covers this one."""
    row, first = gap.row, gap.steps[0]
    plural = "s" if len(gap.steps) > 1 else ""
    job = f"{'deck_v1' if first['step'] == CHEAP_STEP else 'anchor_e8'}:{row['id']}"
    # the first missing step runs where the price table measured it: the deck, or the coupled-cluster Hessian of an anchor
    host = first["parts"][0]["machine"] if "parts" in first else first["machine"]
    if gap.anchor_priced:
        why = f"budget covers the missing step{plural}"
        order = f"request for {row['name']} at rung {req.target_rung} under budget €{req.budget_eur:.2f} ≥ €{gap.total:.2f}"
    else:
        why = (f"budget €{req.budget_eur:.2f} meets the price measured for {anchor['measured_atoms']} atoms (≈ €{gap.total:.2f}), not this "
               f"molecule's: {gap.caveat}; the dry run the gate forces is what prices it")
        order = (f"request for {row['name']} at rung {req.target_rung}: budget €{req.budget_eur:.2f} meets the anchor price measured for "
                 f"{anchor['measured_atoms']} atoms (€{gap.total:.2f} with every missing step), which is not this molecule's; the dry run prices it")
    proposal = Proposal(action="launch", args={"host": host, "job": job}, rule_id="R01", reason=order)
    state = {"observations": [{"source": "request officer", "text": req.note, "facts": {"host": host, "job_due": job}}], "actions_taken": []}
    g = gate_check(proposal, state, RID)
    verdict = "approved" if g.approved else "not approved — " + "; ".join(g.reasons)
    substituted = "approved" if g.approved else "substituted " + (g.forced_action.action if g.forced_action else "")
    return Decision(kind="run_order", request=req, molecule_id=row["id"], name=row["name"], rung_reached=gap.reached,
                    rung_label=RUNG_LABELS[gap.reached], reasons=[f"rung {gap.reached} exists; target {req.target_rung}; {why}", f"gate: {verdict}"],
                    rule_ids=["R01"] + (["R06"] if not g.approved else []), gate_named=None if g.approved else "module 07 gate (R01: dry run first)",
                    price_lines=gap.steps, what_would_be_needed="; then ".join(needed_line(step) for step in gap.steps),
                    proposal=proposal.model_dump(),
                    gate=dict(approved=g.approved, reasons=g.reasons, forced_action=g.forced_action.model_dump() if g.forced_action else None),
                    ledger_line=f"run order — {row['name']} → {job}: gate {substituted}")


def decide(req: Request, catalog: Catalog) -> Decision:  # noqa: PLR0911  one return per gate, in the scenarios' order; its split is TASKS 139
    lic = licence_state()
    # 0. the note is data (module 07, R24): an instruction addressed to the system is refused, not followed
    if instruction_in(req.note):
        return _refuse(req, ["the request text contains an instruction addressed to the system; requests are data, never commands"], ["R24"],
                       "instruction in observed content (R24)", [], "a request that names a molecule, a rung and a budget")
    # 1. the input: a parsable molecule, and a rung that is open for its charge state
    row = catalog.find(req.molecule)
    if row is None and canonical(req.molecule) is None:
        return _refuse(req, [f"'{req.molecule}' is neither a corpus name, a manifest id nor a SMILES RDKit can parse"], ["R25"], "invalid input", [],
                       "a valid SMILES, corpus name or manifest id")
    if req.charge != 0 or req.multiplicity != 1:
        return _refuse(req, [f"charge {req.charge}, multiplicity {req.multiplicity}: the cation rung is closed (obstacle 9; the measured price of one "
                             "naphthalene⁺ energy is on the line below). The corpus holds radical-cation rows at the DFT level (layer "
                             f"{CATION_LAYER} of its manifest), but no certificate rung exists for a charged or open-shell species: the "
                             "pipeline takes neutral closed-shell molecules only and the anchor registry carries no cation anchor"],
                       ["R25"], "cation rung closed (obstacle 9)", [prices.step_price("cation_energy_naphthalene_plus")],
                       CATION_NEEDED, row)
    # 2. outside the corpus: the cap decides what is reachable
    cheap = prices.step_price(CHEAP_STEP)
    anchor = prices.anchor_price()
    if row is None:
        return _outside_corpus(req, cheap, anchor)
    # 3. in the corpus: what exists against what is asked
    reached = int(row["rung"])
    if req.target_rung in (2, 3):
        return _refuse(req, [f"a corrected spectrum is computed by the pipeline (m08/pipeline.py, on the laptop), not by the replay worker — "
                             f"{lic['statement']}; {POS.PIPELINE}"], ["R14"], "the corrected rungs are the pipeline's (licence: decision 65)",
                       [anchor],
                       "a pipeline run of the molecule: python -m m08.pipeline --name <name> --smiles <SMILES> --out <folder>", row)
    if reached >= req.target_rung:
        return Decision(kind="certificate", request=req, molecule_id=row["id"], name=row["name"], rung_reached=reached, rung_label=RUNG_LABELS[reached],
                        reasons=[f"rung {reached} ({RUNG_LABELS[reached]}) reached; target {req.target_rung}"], rule_ids=[],
                        ledger_line=f"certificate — {row['name']} at rung {reached} ({RUNG_LABELS[reached]}), target {req.target_rung}")
    # 4. the target is above what exists: name the gate and the price; order a run only under a budget that meets it, and only through the gate
    gap = gap_of(req, row, cheap, anchor)
    if req.target_rung >= 5:
        return _refuse_validated(req, gap)
    if req.budget_eur is None or req.budget_eur < gap.total:
        return _refuse_cap(req, gap, cheap, anchor)
    return _run_order(req, gap, anchor)
