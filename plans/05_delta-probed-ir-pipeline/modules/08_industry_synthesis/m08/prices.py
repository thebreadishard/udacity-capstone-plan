"""The measured price table (28 September 2026). Every entry names the record it comes from; nothing here is an estimate without a source.
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


# measured steps: what one step costs, where it was measured, and what it buys
STEPS = {
    "cheap_deck_v1": dict(
        what="corpus deck v1: B3LYP/6-31G* optimisation + analytic Hessians at B3LYP and ωB97X (the cheap rung)",
        measured_on="naphthalene (18 atoms), laptop: 3,419.9 s total (corpus ledger row A_01f3186607, 14 Sep 2026); layer A2 on a CPX62: ≈ 70 min per 3–4-ring mono-substituted molecule",
        hours_cpx62=70 / 60, machine="CPX62",
        source="corpus ledger `corpus/ledger.csv`; obstacle ledger 21 Sep (A2 ≈ 70 min per molecule on a CPX62)"),
    "anchor_e8_cc_hessian_naphthalene": dict(
        what="the anchor for a whole molecule: CCSD(T)/cc-pVDZ finite-difference Hessian with symmetry (E8 route)",
        measured_on="naphthalene (18 atoms), CCX53: 15 displacements → 30 gradients at ≈ 4.25 h each, three processes of 10 threads in parallel → ≈ 43 machine-hours",
        hours_ccx53=10 * 4.25, machine="CCX53",
        source="probes/results_m1 partial logs of the frozen-10 rerun (28 Sep 2026: 15,240–15,295 s per gradient); pre-registration E8 of 23 Sep",
        note="measured for naphthalene; a larger molecule costs more than this and its price is not measured yet"),
    "anchor_m3_family_reading_naphthalene": dict(
        what="one family's anchor reading along a mode (M3: cc-pVDZ + cc-pVTZ curvature, LNO-CCSD(T), five points)",
        measured_on="naphthalene, laptop: 4,201 s per cc-pVDZ energy, 12.2 h per cc-pVTZ energy at tight thresholds",
        hours_laptop=5 * (12.2 + 4201 / 3600), machine="laptop",
        source="probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md (12.2 h per TZ energy); REPRODUCE.md row on the neutral price (4,201 s)"),
    "cation_energy_naphthalene_plus": dict(
        what="one LNO-CCSD(T) energy of naphthalene⁺ (the cation rung, closed)",
        measured_on="naphthalene⁺, rented 16-core machine: 34,411 s per energy",
        hours_cpx62=34411 / 3600, machine="CPX62",
        source="REPRODUCE.md row 49 (cation_price_readout.py); obstacle 9"),
}


def eur(hours: float, machine: str) -> float:
    return round(hours * MACHINES[machine]["eur_per_hour"], 2)


def step_price(step: str) -> dict:
    s = STEPS[step]
    m = s["machine"]
    hours = s.get("hours_cpx62") or s.get("hours_ccx53") or s.get("hours_laptop") or 0.0
    return dict(step=step, what=s["what"], machine=m, hours=round(hours, 2), eur_ex_vat=eur(hours, m), measured_on=s["measured_on"], source=s["source"],
                note=s.get("note", ""))


def price_of_run(seconds: float, machine: str) -> dict:
    """The cost record line of a run that already happened: seconds from the ledger row, hours × the machine's list price."""
    cls = host_class(machine)
    if cls == "unknown":
        return dict(machine=machine, machine_class="unknown", seconds=seconds, eur_ex_vat=None, source="machine not in the price table")
    return dict(machine=machine, machine_class=cls, seconds=round(seconds, 1), hours=round(seconds / 3600, 3), eur_ex_vat=eur(seconds / 3600, cls),
                source=MACHINES[cls]["source"])
