"""The request officer: a request names a molecule, a target rung and a budget; the officer answers with a certificate, a refusal that names the
gate or the cap and the price of the missing step, or a run order — and every run order passes through module 07's deterministic gate before
anything could start. Nothing here starts a run; in this module the worker is a replay of recorded logs (decision of 28 Sep 2026)."""
from __future__ import annotations

import re
import sys
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from . import prices
from .catalog import PLAN, RUNG_LABELS, Catalog, canonical, family
from .licence import state as licence_state

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


def _families_of(mol: dict | None) -> list[str]:
    if not mol:
        return []
    freqs = mol.get("frequencies_cm", {}).get("b3lyp", {}).get("vibrational", [])
    seen: list[str] = []
    for f in freqs:
        fam = family(float(f))
        if fam not in seen:
            seen.append(fam)
    return seen


def _refuse(req: Request, reasons: list[str], rule_ids: list[str], gate_named: str, price_lines: list[dict], needed: str, row: dict | None = None) -> Decision:
    name = row["name"] if row else req.molecule
    return Decision(kind="refusal", request=req, molecule_id=row["id"] if row else None, name=name, rung_reached=row["rung"] if row else None,
                    rung_label=RUNG_LABELS.get(row["rung"]) if row else None, reasons=reasons, rule_ids=rule_ids, gate_named=gate_named,
                    price_lines=price_lines, what_would_be_needed=needed,
                    ledger_line=f"refusal — {name}: {gate_named}; {'; '.join(reasons)}; needed: {needed}")


def decide(req: Request, catalog: Catalog) -> Decision:
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
                             "naphthalene⁺ energy is on the line below); no certificate rung exists for open-shell species yet"], ["R25"],
                       "cation rung closed (obstacle 9)", [prices.step_price("cation_energy_naphthalene_plus")],
                       "the cation rows of the anchor plan (benzene⁺, naphthalene⁺) read and a rung opened by a dated decision", row)
    # 2. outside the corpus: the cap decides what is reachable
    cheap = prices.step_price("cheap_deck_v1"); anchor = prices.step_price("anchor_e8_cc_hessian_naphthalene")
    if row is None:
        reachable = []
        if req.budget_eur is not None and req.budget_eur >= cheap["eur_ex_vat"]:
            reachable.append(f"rung 1 (cheap level) at ≈ €{cheap['eur_ex_vat']:.2f}")
        if req.budget_eur is not None and req.budget_eur >= anchor["eur_ex_vat"]:
            reachable.append(f"rung 4 (anchored, naphthalene-sized) at ≈ €{anchor['eur_ex_vat']:.2f}")
        cap = f"budget €{req.budget_eur:.2f}" if req.budget_eur is not None else "no budget given"
        reasons = [f"'{req.molecule}' is not in the corpus (canonical {canonical(req.molecule)}); nothing exists to certify",
                   f"{cap}: reachable within it — " + ("; ".join(reachable) if reachable else "nothing (the cheap rung alone costs ≈ €" + f"{cheap['eur_ex_vat']:.2f})")]
        needed = ("an intake into the corpus factory (deck v1) at the cheap rung's price, then an anchor for the target rung" if req.target_rung >= 4
                  else "an intake into the corpus factory (deck v1)")
        d = _refuse(req, reasons, ["R25", "R32"], f"cap: {cap}; target rung {req.target_rung} not reachable", [cheap, anchor], needed)
        d.reasons.append("no run is started: the officer never spends without a passed gate, and the gate needs a dry run of a named job first (R01)")
        return d
    # 3. in the corpus: what exists against what is asked
    mol = catalog.molecule(row["id"])
    fams = _families_of(mol)
    reached = int(row["rung"])
    if req.target_rung in (2, 3):
        unlicensed = [f for f in fams if f not in lic["licensed_families"]] or ["all families"]
        return _refuse(req, [f"the learned layer is not licensed for {', '.join(unlicensed)} — {lic['statement']}"], ["R14"],
                       "licence of the learned layer (proof-of-learning pre-registration)", [anchor],
                       "the registered learning curve read at 1,200 molecules with a pass on the three hold-outs; until then an anchor (rung 4) is the only route to a corrected spectrum", row)
    if reached >= req.target_rung:
        return Decision(kind="certificate", request=req, molecule_id=row["id"], name=row["name"], rung_reached=reached, rung_label=RUNG_LABELS[reached],
                        reasons=[f"rung {reached} ({RUNG_LABELS[reached]}) reached; target {req.target_rung}"], rule_ids=[],
                        ledger_line=f"certificate — {row['name']} at rung {reached} ({RUNG_LABELS[reached]}), target {req.target_rung}")
    # 4. the target is above what exists: name the gate and the price; order a run only under a budget that covers it, and only through the gate
    missing = anchor if req.target_rung >= 4 else cheap
    gate_named = ("no anchor: the learned layer is not licensed for " + ", ".join(fams or ["its families"]) + " and no coupled-cluster reading exists"
                  if req.target_rung >= 4 else "cheap level not computed")
    needed = f"{missing['what']} — measured on {missing['measured_on']}: ≈ {missing['hours']:.1f} h on a {missing['machine']} ≈ €{missing['eur_ex_vat']:.2f} ex VAT" + (f" ({missing['note']})" if missing.get("note") else "")
    if req.budget_eur is None or req.budget_eur < missing["eur_ex_vat"]:
        d = _refuse(req, [f"rung {reached} ({RUNG_LABELS[reached]}) exists; target rung {req.target_rung} not reached",
                          f"budget {'not given' if req.budget_eur is None else f'€{req.budget_eur:.2f}'} does not cover the missing step (≈ €{missing['eur_ex_vat']:.2f})"],
                    ["R14" if req.target_rung >= 4 else "R25"], gate_named, [missing], needed, row)
        return d
    # a run order: the officer proposes 'launch' of a named job; module 07's gate decides — without a passed dry run it forces the dry run first (R01)
    job = f"{'anchor_e8' if req.target_rung >= 4 else 'deck_v1'}:{row['id']}"
    proposal = Proposal(action="launch", args={"host": "CCX53" if req.target_rung >= 4 else "CPX62", "job": job}, rule_id="R01",
                        reason=f"request for {row['name']} at rung {req.target_rung} under budget €{req.budget_eur:.2f} ≥ €{missing['eur_ex_vat']:.2f}")
    state = {"observations": [{"source": "request officer", "text": req.note, "facts": {"host": proposal.args["host"], "job_due": job}}], "actions_taken": []}
    g = gate_check(proposal, state, RID)
    return Decision(kind="run_order", request=req, molecule_id=row["id"], name=row["name"], rung_reached=reached, rung_label=RUNG_LABELS[reached],
                    reasons=[f"rung {reached} exists; target {req.target_rung}; budget covers the missing step", f"gate: {'approved' if g.approved else 'not approved — ' + '; '.join(g.reasons)}"],
                    rule_ids=["R01"] + (["R06"] if not g.approved else []), gate_named=None if g.approved else "module 07 gate (R01: dry run first)",
                    price_lines=[missing], what_would_be_needed=needed, proposal=proposal.model_dump(),
                    gate=dict(approved=g.approved, reasons=g.reasons, forced_action=g.forced_action.model_dump() if g.forced_action else None),
                    ledger_line=f"run order — {row['name']} → {job}: gate {'approved' if g.approved else 'substituted ' + (g.forced_action.action if g.forced_action else '')}")
