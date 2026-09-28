"""The replay worker (decision 1 of 28 Sep 2026: replay, not live). A run order in this module never provisions a machine: the worker re-executes
the *recorded* run of the molecule — the corpus ledger row the export carries — and returns the run record marked as a replay with its source.
The live path (a rented server per job, budget cap, OAuth) is documented in the design note and switched on only when the licence exists."""
from __future__ import annotations

import time


def replay_run(mol: dict | None) -> dict | None:
    """The recorded cheap-rung run of a computed molecule, replayed: the same machine, deck and seconds as the ledger row; nothing is computed."""
    if not mol or not mol.get("ledger"):
        return None
    led = mol["ledger"]
    return dict(replay=True, replayed_at=time.strftime("%Y-%m-%d %H:%M"), machine=led["machine"], deck=led["deck"], start=led["start"], end=led["end"],
                seconds_total=float(led["seconds_total"]), seconds_optimise=float(led.get("seconds_optimise") or 0), seconds_hessian_b3lyp=float(led.get("seconds_hessian_b3lyp") or 0),
                seconds_hessian_wb97x=float(led.get("seconds_hessian_wb97x") or 0), peak_rss_gb=led.get("peak_rss_gb"), status=led["status"],
                source=f"corpus ledger row {led['id']} (machine {led['machine']}, {led['start']} → {led['end']})")


def execute_run_order(decision: dict, catalog) -> dict:
    """What the worker does with a run order in replay mode: if a recorded run exists for the job's molecule and rung, it is replayed and reported;
    otherwise the order is queued with the gate's verdict attached and no machine is touched."""
    mid = decision.get("molecule_id")
    gate = decision.get("gate") or {}
    if not gate.get("approved"):
        return dict(executed=False, queued=True, reason="the module 07 gate did not approve the launch (" + "; ".join(gate.get("reasons", [])) + ")",
                    forced_action=gate.get("forced_action"), machine_touched=False)
    mol = catalog.molecule(mid) if mid else None
    run = replay_run(mol)
    if run is None:
        return dict(executed=False, queued=True, reason="no recorded run to replay for this molecule; a live worker would provision a machine here", machine_touched=False)
    return dict(executed=True, queued=False, run=run, machine_touched=False)
