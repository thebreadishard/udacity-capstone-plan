"""The measured price table (28 September 2026; the anchor's entries re-derived from the run logs on 20 November 2026). Every entry names
the record it comes from; nothing here is an estimate without a source.
Prices are Hetzner list prices excluding VAT as the ledger recorded them; the laptop is owned hardware and is priced at €0 with its hours shown."""
from __future__ import annotations

MACHINES = {
    "CPX62": dict(eur_per_hour=0.208, description="Hetzner CPX62, 16 shared AMD vCPU, 32 GB, Helsinki",
                  source="obstacle ledger, 18 Sep 08:0x (layer A on a rented CPX62: €0.208/h)"),
    "CCX53": dict(eur_per_hour=0.855, description="Hetzner CCX53, 32 dedicated vCPU, 128 GB, Helsinki",
                  source="obstacle ledger, 27 Sep (CCX53 ubuntu-128gb-hel1-2 at €0.855/h)"),
    "laptop": dict(eur_per_hour=0.0, description="the project laptop (Asus18, 8 threads); owned hardware, electricity not metered",
                   source="corpus ledger machine column 'Asus18'"),
}

# machine names as the corpus ledger and the run logs write them → price class
HOST_CLASS = {"Asus18": "laptop", "laptop": "laptop", "ubuntu-128gb-hel1-2": "CCX53"}


def host_class(machine: str) -> str:
    if machine in HOST_CLASS:
        return HOST_CLASS[machine]
    if machine.startswith("ubuntu-32gb-hel1"):
        return "CPX62"
    if machine.startswith("ubuntu-128gb"):
        return "CCX53"
    return "unknown"


def eur(hours: float, machine: str) -> float:
    return round(hours * MACHINES[machine]["eur_per_hour"], 2)


# Naphthalene's anchor, in seconds as `probes/anchor_price_from_logs.py` reads them from the run logs; a test holds these equal to
# its record. A machine-hour is a wall-clock hour of the rented machine, charged by the share of its lanes that worked for the molecule.
ANCHOR_RECORD = "probes/results_m1/anchor_price_2026-11-20/anchor_price.json"
CC_RUN_S = 68_815            # launch → Hessian written VALID, the CPX62 held for this run alone
CC_TWO_ROUTE_CHECKS_S = 24_426   # inside it: the (T) kernels against pyscf's slow routes (5,609 s lambda + 18,817 s density)
CC_LOST_S = 17_182           # inside it: the first attempt, killed for memory, and the wait for its relaunch
MP2_JOB_S = 31_110           # the 30 MP2 jobs' own wall time
MP2_CHARGED_S = 7_777.5      # a quarter of it: four lanes shared the CCX53

# measured steps: what one step costs, where it was measured, and what it buys
STEPS = {
    "cheap_deck_v1": dict(
        what="corpus deck v1: B3LYP/6-31G* optimisation + analytic Hessians at B3LYP and ωB97X (the cheap rung)",
        measured_on="naphthalene (18 atoms), laptop: 3,419.9 s total (corpus ledger row A_01f3186607, 14 Sep 2026); layer A2 on a CPX62: "
                    "≈ 70 min per 3–4-ring mono-substituted molecule",
        hours=70 / 60, machine="CPX62",
        source="corpus ledger modules/05_support_predictor/corpus/ledger.csv; obstacle ledger 21 Sep (A2 ≈ 70 min per molecule on a CPX62)",
        note=""),
    "anchor_cc_dz_hessian_naphthalene": dict(
        what="the coupled-cluster part of an anchor: CCSD(T)/cc-pVDZ finite-difference Hessian with symmetry (E8 route, explicit (T) lambda)",
        measured_on=f"naphthalene (18 atoms), CPX62 ubuntu-32gb-hel1-2, 1–2 Oct 2026: {CC_RUN_S:,} s of wall clock from launch to the Hessian "
                    "written VALID, the machine held for this run — the reference gradient, then 15 symmetry-unique displacements → 30 "
                    "gradients in two lanes of 8 threads",
        hours=CC_RUN_S / 3600, machine="CPX62",
        source=f"{ANCHOR_RECORD}, written by probes/anchor_price_from_logs.py from "
               "probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/e8_fd.log and "
               "probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/anchors.log",
        note=f"the run as it ran: {CC_TWO_ROUTE_CHECKS_S:,} s of it (€{eur(CC_TWO_ROUTE_CHECKS_S / 3600, 'CPX62'):.2f}) were the one-off "
             "two-route checks of the (T) kernels against pyscf's slow routes, a validation gate that a second molecule on the same "
             f"environment does not repeat, and {CC_LOST_S:,} s (€{eur(CC_LOST_S / 3600, 'CPX62'):.2f}) a first attempt lost to a memory "
             "kill; no run without them has been timed, so neither is taken out of the price"),
    "anchor_mp2_basis_step_naphthalene": dict(
        what="the basis step of an anchor: MP2/cc-pVTZ − MP2/cc-pVDZ rows on the coupled-cluster Hessian's displacements",
        measured_on=f"naphthalene (18 atoms), CCX53, 7 Oct 2026: 15 cc-pVTZ and 15 cc-pVDZ jobs of 8 threads, {MP2_JOB_S:,} s of job time in "
                    "a queue of four lanes shared with four other molecules' rows, so a quarter of the machine for that time",
        hours=MP2_CHARGED_S / 3600, machine="CCX53",
        source=f"{ANCHOR_RECORD}, written by probes/anchor_price_from_logs.py from "
               "probes/results_m1/composite_rows_2026-10-07/queue.log, probes/results_m1/composite_rows_2026-10-07/jobs.txt and the "
               "worker_*.log files beside them",
        note="the queue's failed starts and another molecule's killed job are not charged to naphthalene"),
    "anchor_m3_family_reading_naphthalene": dict(
        what="one family's anchor reading along a mode (M3: cc-pVDZ + cc-pVTZ curvature, LNO-CCSD(T), five points)",
        measured_on="naphthalene, laptop: 4,201 s per cc-pVDZ energy, 12.2 h per cc-pVTZ energy at tight thresholds",
        hours=5 * (12.2 + 4201 / 3600), machine="laptop",
        source="probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md (12.2 h per TZ energy); REPRODUCE.md row on the neutral price (4,201 s)",
        note=""),
    "cation_energy_naphthalene_plus": dict(
        what="one LNO-CCSD(T) energy of naphthalene⁺ (the cation rung, closed)",
        measured_on="naphthalene⁺, rented 16-core machine: 34,411 s per energy",
        hours=34411 / 3600, machine="CPX62",
        source="REPRODUCE.md row 49 (cation_price_readout.py); obstacle 9",
        note=""),
}

# The anchor of the route in force (decision 62: a composite) is the sum of its measured parts, each on its own machine.
ANCHOR_STEP = "anchor_composite_naphthalene"
ANCHOR_PARTS = (("the coupled-cluster Hessian", "anchor_cc_dz_hessian_naphthalene"), ("the MP2 basis step", "anchor_mp2_basis_step_naphthalene"))


def step_price(step: str) -> dict:
    s = STEPS[step]
    return dict(step=step, what=s["what"], machine=s["machine"], hours=round(s["hours"], 2), eur_ex_vat=eur(s["hours"], s["machine"]),
                measured_on=s["measured_on"], source=s["source"], note=s["note"])


def anchor_price() -> dict:
    """The price line of a whole-molecule anchor: the composite's parts added, euros as the sum of the parts' euros so that a reader
    can add the lines. It is naphthalene's price; nothing larger has been priced."""
    parts = [(label, step_price(step)) for label, step in ANCHOR_PARTS]
    return dict(
        step=ANCHOR_STEP,
        what="the anchor for a whole molecule by the route in force (decision 62): a CCSD(T)/cc-pVDZ finite-difference Hessian with symmetry "
             "plus the basis step MP2/cc-pVTZ − MP2/cc-pVDZ",
        machine=" + ".join(p["machine"] for _, p in parts),
        hours=round(sum(STEPS[step]["hours"] for _, step in ANCHOR_PARTS), 2),
        eur_ex_vat=round(sum(p["eur_ex_vat"] for _, p in parts), 2),
        measured_on="naphthalene (18 atoms), 1–7 Oct 2026, from the run logs: "
                    + " and ".join(f"{label} {p['hours']:.2f} h on a {p['machine']} (€{p['eur_ex_vat']:.2f})" for label, p in parts),
        source=ANCHOR_RECORD + " (probes/anchor_price_from_logs.py)",
        note="; ".join(p["note"] for _, p in parts) + "; measured for naphthalene: a larger molecule costs more than this and its price is "
             "not measured yet",
        parts=[p for _, p in parts])


def table_record() -> dict:
    """The table as a record: what the notebook writes into results.json and the paper reads back."""
    return dict(machines=MACHINES, steps={k: step_price(k) for k in STEPS}, anchor=anchor_price())


def price_of_run(seconds: float, machine: str) -> dict:
    """The cost record line of a run that already happened: seconds from the ledger row, hours × the machine's list price."""
    cls = host_class(machine)
    if cls == "unknown":
        return dict(machine=machine, machine_class="unknown", seconds=seconds, eur_ex_vat=None, source="machine not in the price table")
    return dict(machine=machine, machine_class=cls, seconds=round(seconds, 1), hours=round(seconds / 3600, 3), eur_ex_vat=eur(seconds / 3600, cls),
                source=MACHINES[cls]["source"])
