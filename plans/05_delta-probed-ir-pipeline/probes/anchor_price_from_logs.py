"""What naphthalene's anchor cost to compute, read from the logs of the runs that made it (TASKS 290, 20 Nov 2026).

The anchor in force for naphthalene is a composite (decision 62): the CCSD(T)/cc-pVDZ finite-difference Hessian of 1–2 October 2026
plus the basis step MP2/cc-pVTZ − MP2/cc-pVDZ on the same displacements, computed in the MP2 rows queue of 7 October. Module 08's
price table quotes this anchor's price in its refusals, so the price is re-derived here from the run logs and written as a record.

Attribution (one rule for both parts, `RULE`): a machine-hour is a wall-clock hour of the rented machine, charged to the molecule
by the share of the machine's lanes that worked for it. A machine-hour is priced at the list price in `m08/prices.py`.

    python probes/anchor_price_from_logs.py            # writes probes/results_m1/anchor_price_2026-11-20/{anchor_price.json,RESULT.md}
    python probes/anchor_price_from_logs.py --out DIR
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import prices  # noqa: E402  (after the sys.path insert) the list prices and host classes have one implementation

RESULTS = PLAN / "probes" / "results_m1"
CC_DIR = RESULTS / "e8_naphthalene_ccpvdz_tlambda_2026-10-02"
MP2_DIR = RESULTS / "composite_rows_2026-10-07"
OUT_DIR = RESULTS / "anchor_price_2026-11-20"
MOLECULE = "naphthalene"
# The queue's logs do not print a host name. The machine is the CCX53: the obstacle ledger's entry of 7 Oct 17:2x ("the MP2 rows
# queue … exceeded the CCX53's 122 GB"), and queue.log quotes its own script, which the parser requires before it prices the step.
MP2_MACHINE = "CCX53"
MP2_QUEUE_SCRIPT = "mp2_rows_queue_ccx53.sh"
MP2_MACHINE_SOURCE = f"obstacle ledger, 7 Oct 17:2x (the MP2 rows queue on the CCX53); queue.log names its script {MP2_QUEUE_SCRIPT}"
RULE = ("a machine-hour is a wall-clock hour of the rented machine, charged to the molecule by the share of the machine's lanes that "
        "worked for it: a run the machine was rented for is charged its whole wall-clock span from launch to end, lost attempts "
        "and idle gaps included, also where other work ran beside it; a job in a queue of N lanes shared with other molecules is "
        "charged its own wall time / N, and the "
        "queue's own losses (failed starts, another molecule's killed job) are not charged to this molecule")
STAMP_TOLERANCE_S = 60     # a logged duration and the stamps around it may differ by the lines written in between

STAMP = re.compile(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\] (.*)$")
CHAIN_START = re.compile(r"chain \(corrected route\) start on (\S+)")
HEADER_THREADS = re.compile(r"E8 FD Hessian: .*?(\d+) threads")
HEADER_ATOMS = re.compile(r"E8 FD Hessian: (\d+) atoms")
PARTIAL = re.compile(r"partial run: displacement indices \[([\d, ]+)\]")
SYMMETRY = re.compile(r"symmetry: .*?(\d+) displacements \((\d+) gradients\)")
GRADIENT = re.compile(r"coordinate\s+(\d+) ([pm]): .*?, (\d+) s ")
REFERENCE = re.compile(r"reference: E = .*?, (\d+) s$")
KERNEL_CHECK = re.compile(r"fast \(T\) (lambda|density) two-route check: .*?; (\d+) s\)")
VALID = "Hessian written (VALID)"
QUEUE_START = re.compile(r"=== QUEUE start: \d+ jobs, (\d+) workers x (\d+) threads, .*?(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) UTC")
MP2_JOB = re.compile(r"^\[(\d\d:\d\d:\d\d)\] mp2 (cc-pv[dt]z) k=(\d+): .*\((\d+) s\)$")
MP2_ROWS = re.compile(r"rows/(.+)_(ccpv[dt]z)_k(\d+)\.npz")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def stamped(text: str) -> list[tuple[datetime, str]]:
    """The log's lines that carry a full time stamp, in file order; library output between them carries none and is left out."""
    out = []
    for line in text.splitlines():
        m = STAMP.match(line)
        if m:
            out.append((datetime.strptime(m.group(1), TIME_FORMAT), m.group(2)))
    return out


def seconds(later: datetime, earlier: datetime) -> int:
    return round((later - earlier).total_seconds())


def one(found: list, what: str):
    """The single match a log must hold; a log with none or several is not the run this script reads."""
    if len(found) != 1:
        raise ValueError(f"expected exactly one {what} in the log, found {len(found)}")
    return found[0]


def chain_starts(anchors_log: str) -> tuple[str, list[datetime]]:
    """The host and every start of the chain: the first is the launch, a later one a relaunch."""
    starts = [(t, m.group(1)) for t, body in stamped(anchors_log) if (m := CHAIN_START.search(body))]
    if not starts:
        raise ValueError("the anchors log holds no 'chain (corrected route) start on <host>' line")
    hosts = {host for _, host in starts}
    if len(hosts) != 1:
        raise ValueError(f"the chain started on several hosts ({sorted(hosts)}): one machine's price cannot be charged")
    return hosts.pop(), [t for t, _ in starts]


def lanes_of(lines: list[tuple[datetime, str]]) -> list[dict]:
    """The partial runs: their displacement indices, threads and start, each from the run header that precedes its 'partial run' line."""
    lanes, threads = [], None
    for t, body in lines:
        if m := HEADER_THREADS.search(body):
            threads = int(m.group(1))
        elif m := PARTIAL.search(body):
            if threads is None:
                raise ValueError("a 'partial run' line without a run header before it: the lane's threads are unknown")
            lanes.append(dict(displacements=[int(k) for k in m.group(1).split(",")], threads=threads, started=t))
    if not lanes:
        raise ValueError("the log holds no 'partial run: displacement indices' line: no production gradients to read")
    return lanes


def lane_gradients(lane: dict, gradients: dict[tuple[int, str], tuple[datetime, int]]) -> dict:
    """One lane's gradients: both signs of each of its displacements, with the seconds the log gives each; a missing one raises."""
    missing = [f"{k} {sign}" for k in lane["displacements"] for sign in "pm" if (k, sign) not in gradients]
    if missing:
        raise ValueError(f"the log lacks the gradient line of coordinate {', '.join(missing)}: the run is not complete in this log")
    own = [gradients[(k, sign)] for k in lane["displacements"] for sign in "pm"]
    ended = max(t for t, _ in own)
    per_gradient = [s for _, s in own]
    return dict(displacements=lane["displacements"], threads=lane["threads"], started=lane["started"].strftime(TIME_FORMAT),
                ended=ended.strftime(TIME_FORMAT), span_s=seconds(ended, lane["started"]), n_gradients=len(own),
                gradient_s=dict(min=min(per_gradient), max=max(per_gradient), sum=sum(per_gradient), each=per_gradient))


def production(lines: list[tuple[datetime, str]]) -> dict:
    """The displaced gradients of the run: per lane, and the span from the first lane's start to the last gradient."""
    lanes = lanes_of(lines)
    gradients: dict[tuple[int, str], tuple[datetime, int]] = {}
    for t, body in lines:
        if m := GRADIENT.search(body):
            key = (int(m.group(1)), m.group(2))
            if key in gradients:
                raise ValueError(f"coordinate {key[0]} {key[1]} has two gradient lines: this log mixes runs")
            gradients[key] = (t, int(m.group(3)))
    read = [lane_gradients(lane, gradients) for lane in lanes]
    expected = {(int(m.group(1)), int(m.group(2))) for _, body in lines if (m := SYMMETRY.search(body))}
    counted = (sum(len(lane["displacements"]) for lane in read), sum(lane["n_gradients"] for lane in read))
    if expected != {counted}:
        raise ValueError(f"the lanes hold {counted[0]} displacements ({counted[1]} gradients); the log's symmetry line says {sorted(expected)}")
    if len(gradients) != counted[1]:
        raise ValueError(f"the log holds {len(gradients)} gradient lines, the lanes account for {counted[1]}")
    started = min(lane["started"] for lane in lanes)
    ended = max(datetime.strptime(lane["ended"], TIME_FORMAT) for lane in read)
    return dict(n_gradients=counted[1], started=started.strftime(TIME_FORMAT), ended=ended.strftime(TIME_FORMAT),
                span_s=seconds(ended, started), lanes=read)


def reference_of(lines: list[tuple[datetime, str]], relaunched: datetime) -> dict:
    """The reference gradient of the attempt that finished, and the one-off two-route checks of the (T) kernels inside it."""
    after = [(t, body) for t, body in lines if t >= relaunched]
    at, ref_s = one([(t, int(m.group(1))) for t, body in after if (m := REFERENCE.search(body))], "reference line after the last start")
    if abs(seconds(at, relaunched) - ref_s) > STAMP_TOLERANCE_S:
        raise ValueError(f"the reference line says {ref_s} s, its stamp is {seconds(at, relaunched)} s after the last start: not the same attempt")
    checks: dict[str, int] = {}
    for t, body in after:
        if t <= at and (m := KERNEL_CHECK.search(body)):
            if m.group(1) in checks:
                raise ValueError(f"two {m.group(1)} two-route check lines in one attempt: which one the reference holds is not decided")
            checks[m.group(1)] = int(m.group(2))
    return dict(ended=at.strftime(TIME_FORMAT), seconds=ref_s, two_route_checks_s=checks, two_route_checks_sum_s=sum(checks.values()))


def atoms_of(lines: list[tuple[datetime, str]]) -> int:
    """The molecule's atom count as every run header of the log states it."""
    counts = {int(m.group(1)) for _, body in lines if (m := HEADER_ATOMS.search(body))}
    if len(counts) != 1:
        raise ValueError(f"the run headers name {sorted(counts)} as atom counts: one molecule's log names exactly one")
    return counts.pop()


def parse_cc_run(fd_log: str, anchors_log: str) -> dict:
    """The coupled-cluster Hessian run as it ran: launch to VALID, split into what was lost, the reference, the gradients, the assembly."""
    host, starts = chain_starts(anchors_log)
    lines = stamped(fd_log)
    launched, relaunched = starts[0], starts[-1]
    valid = one([t for t, body in lines if VALID in body], "'Hessian written (VALID)' line")
    reference = reference_of(lines, relaunched)
    grads = production(lines)
    wall = seconds(valid, launched)
    parts = dict(lost_before_relaunch_s=seconds(relaunched, launched), reference_s=reference["seconds"], gradients_s=grads["span_s"],
                 assembly_s=seconds(valid, datetime.strptime(grads["ended"], TIME_FORMAT)))
    if abs(sum(parts.values()) - wall) > STAMP_TOLERANCE_S:
        raise ValueError(f"the parts sum to {sum(parts.values())} s, launch to VALID is {wall} s: the log has a stretch this script does not name")
    return dict(host=host, machine=prices.host_class(host), n_atoms=atoms_of(lines), launched=launched.strftime(TIME_FORMAT), n_starts=len(starts),
                relaunched=relaunched.strftime(TIME_FORMAT), valid=valid.strftime(TIME_FORMAT), wall_s=wall, parts=parts,
                reference=reference, gradients=grads, machine_share=1.0, machine_seconds=wall)


def expected_jobs(jobs_txt: str, molecule: str) -> set[tuple[str, int]]:
    """The (basis, displacement) jobs the queue's job list names for the molecule."""
    jobs = set()
    for line in jobs_txt.splitlines():
        fields = line.strip().split("|")
        if len(fields) >= 4 and fields[0] == molecule:
            jobs.add((fields[2].replace("-", ""), int(fields[3])))
    if not jobs:
        raise ValueError(f"the job list names no job of {molecule}")
    return jobs


def queue_segments(queue_log: str) -> list[tuple[datetime, int, int]]:
    """Every start of the queue: when, with how many workers (lanes) and threads per worker."""
    segments = [(datetime.strptime(m.group(3), TIME_FORMAT), int(m.group(1)), int(m.group(2))) for m in QUEUE_START.finditer(queue_log)]
    if not segments:
        raise ValueError("the queue log holds no '=== QUEUE start' line")
    return segments


def worker_jobs(worker_log: str, day: datetime) -> list[dict]:
    """The finished jobs of one worker: molecule, basis, displacement, seconds and end time. The log stamps the time of day only, so
    the date is the queue's, moved on a day where the clock runs backwards."""
    jobs, lines, previous = [], worker_log.splitlines(), None
    for i, line in enumerate(lines):
        m = MP2_JOB.match(line)
        if not m:
            continue
        rows = MP2_ROWS.search(lines[i + 1]) if i + 1 < len(lines) else None
        if rows is None or (rows.group(2), int(rows.group(3))) != (m.group(2).replace("-", ""), int(m.group(3))):
            raise ValueError(f"the job line '{line}' is not followed by its own rows line: the molecule of the job is unknown")
        ended = datetime.combine(day.date(), datetime.strptime(m.group(1), "%H:%M:%S").time())
        while previous is not None and ended < previous:
            ended += timedelta(days=1)
        previous = ended
        jobs.append(dict(molecule=rows.group(1), basis=rows.group(2), k=int(rows.group(3)), seconds=int(m.group(4)), ended=ended))
    return jobs


def lanes_at(segments: list[tuple[datetime, int, int]], ended: datetime) -> tuple[int, int]:
    """The workers and threads of the queue start a job finished under."""
    before = [(workers, threads) for start, workers, threads in segments if start <= ended]
    if not before:
        raise ValueError(f"a job ended at {ended}, before the queue's first start")
    return before[-1]


def basis_summary(jobs: list[dict]) -> dict:
    per_job = [job["seconds"] for job in sorted(jobs, key=lambda job: job["k"])]
    return dict(n_jobs=len(jobs), job_s=dict(min=min(per_job), max=max(per_job), sum=sum(per_job), each=per_job),
                machine_seconds=round(sum(job["seconds"] / job["lanes"] for job in jobs), 1))


def parse_mp2_step(queue_log: str, jobs_txt: str, worker_logs: dict[str, str], molecule: str) -> dict:
    """The molecule's MP2 jobs in the rows queue: per basis the jobs and their seconds, the lanes that shared the machine, and the
    machine time charged by `RULE`. A job the list names and no worker finished raises."""
    if MP2_QUEUE_SCRIPT not in queue_log:
        raise ValueError(f"queue.log does not name {MP2_QUEUE_SCRIPT}: nothing in these logs says the queue ran on the {MP2_MACHINE}")
    segments = queue_segments(queue_log)
    expected = expected_jobs(jobs_txt, molecule)
    found: dict[tuple[str, int], dict] = {}
    for name, text in sorted(worker_logs.items()):
        for job in worker_jobs(text, segments[0][0]):
            key = (job["basis"], job["k"])
            if job["molecule"] != molecule:
                continue
            if key in found:
                raise ValueError(f"{molecule} {key[0]} k={key[1]} finished twice ({found[key]['worker']} and {name}): which one is charged is not decided")
            workers, threads = lanes_at(segments, job["ended"])
            found[key] = job | dict(worker=name, lanes=workers, threads=threads)
    missing = sorted(expected - set(found))
    if missing:
        raise ValueError(f"no worker log holds the finished job of {molecule} {', '.join(f'{b} k={k}' for b, k in missing)}")
    if set(found) != expected:
        raise ValueError(f"the worker logs hold jobs of {molecule} the job list does not name: {sorted(set(found) - expected)}")
    by_basis = {basis: basis_summary([j for j in found.values() if j["basis"] == basis]) for basis in sorted({b for b, _ in found})}
    ends = [job["ended"] for job in found.values()]
    return dict(machine=MP2_MACHINE, machine_source=MP2_MACHINE_SOURCE, lanes_sharing=sorted({j["lanes"] for j in found.values()}),
                threads_per_lane=sorted({j["threads"] for j in found.values()}), first_job_ended=min(ends).strftime(TIME_FORMAT),
                last_job_ended=max(ends).strftime(TIME_FORMAT), n_jobs=len(found), by_basis=by_basis,
                job_seconds=sum(j["seconds"] for j in found.values()),
                machine_seconds=round(sum(b["machine_seconds"] for b in by_basis.values()), 1))


def priced(part: dict) -> dict:
    """The part's machine-hours at its machine's list price; a machine the price table does not hold is refused."""
    if part["machine"] not in prices.MACHINES:
        raise ValueError(f"the run's machine class is {part['machine']!r}: the price table has no "
                         "list price for it, so the run cannot be priced")
    hours = part["machine_seconds"] / 3600
    return dict(machine=part["machine"], machine_hours=round(hours, 3), eur_per_hour=prices.MACHINES[part["machine"]]["eur_per_hour"],
                eur_ex_vat=prices.eur(hours, part["machine"]))


def build_record(cc: dict, mp2: dict, sources: dict[str, list[str]]) -> dict:
    cc_price, mp2_price = priced(cc), priced(mp2)
    rate = cc_price["eur_per_hour"] / 3600
    return dict(
        molecule=MOLECULE, written_by="probes/anchor_price_from_logs.py", rule=RULE, sources=sources,
        cc_dz_hessian=cc | dict(price=cc_price, of_which_eur=dict(
            two_route_checks_at_most=round(cc["reference"]["two_route_checks_sum_s"] * rate, 2),
            lost_before_relaunch=round(cc["parts"]["lost_before_relaunch_s"] * rate, 2))),
        mp2_basis_step=mp2 | dict(price=mp2_price),
        anchor=dict(machine_hours=round((cc["machine_seconds"] + mp2["machine_seconds"]) / 3600, 3),
                    eur_ex_vat=round(cc_price["eur_ex_vat"] + mp2_price["eur_ex_vat"], 2)))


def hours(s: float) -> str:
    return f"{s / 3600:.2f} h"


def result_markdown(r: dict) -> str:
    """RESULT.md: the numbers, where each comes from, and what they are not."""
    cc, mp2, ref = r["cc_dz_hessian"], r["mp2_basis_step"], r["cc_dz_hessian"]["reference"]
    lanes = "; ".join(f"lane {i + 1}: {lane['n_gradients']} gradients on {lane['threads']} threads, {lane['gradient_s']['min']:,}–"
                      f"{lane['gradient_s']['max']:,} s each, {lane['started']} → {lane['ended']} ({hours(lane['span_s'])})"
                      for i, lane in enumerate(cc["gradients"]["lanes"]))
    checks = " + ".join(f"{s:,} s ({name})" for name, s in ref["two_route_checks_s"].items())
    bases = "; ".join(f"{basis}: {b['n_jobs']} jobs, {b['job_s']['min']:,}–{b['job_s']['max']:,} s each, {b['job_s']['sum']:,} s together"
                      for basis, b in mp2["by_basis"].items())
    return "\n".join([
        f"# What {r['molecule']}'s anchor cost to compute — read from its run logs", "",
        f"Written by `{r['written_by']}`; the numbers are in `anchor_price.json` beside this file. Prices are list prices ex VAT "
        "(`modules/08_industry_synthesis/m08/prices.py`).", "",
        f"**The anchor (composite, decision 62): {r['anchor']['machine_hours']:.2f} machine-hours, € {r['anchor']['eur_ex_vat']:.2f}.**", "",
        f"**Attribution rule.** {r['rule'][0].upper()}{r['rule'][1:]}.", "",
        "## The CCSD(T)/cc-pVDZ Hessian", "",
        f"- Molecule: {cc['n_atoms']} atoms. Machine: {cc['host']} ({cc['machine']}), rented for this run: share 1.",
        f"- As it ran: launched {cc['launched']}, Hessian written VALID {cc['valid']}: {cc['wall_s']:,} s = {hours(cc['wall_s'])} → "
        f"€ {cc['price']['eur_ex_vat']:.2f} at € {cc['price']['eur_per_hour']}/h.",
        f"- Starts: {cc['n_starts']} (the last at {cc['relaunched']}). From the launch to the last start {cc['parts']['lost_before_relaunch_s']:,} s "
        f"({hours(cc['parts']['lost_before_relaunch_s'])}, € {cc['of_which_eur']['lost_before_relaunch']:.2f}) produced nothing the Hessian uses.",
        f"- Reference gradient: {ref['seconds']:,} s ({hours(ref['seconds'])}). The timers of the one-off two-route checks of the (T) "
        f"kernels against pyscf's slow routes read {checks} = {ref['two_route_checks_sum_s']:,} s "
        f"(€ {cc['of_which_eur']['two_route_checks_at_most']:.2f}). That is an upper bound on what the checks added: a timer may "
        "enclose work a reference gradient needs anyway, and no reference without the checks has been timed.",
        f"- Displaced gradients: {cc['gradients']['n_gradients']} in {len(cc['gradients']['lanes'])} lanes, {cc['gradients']['started']} → "
        f"{cc['gradients']['ended']}: {cc['gradients']['span_s']:,} s = {hours(cc['gradients']['span_s'])}. {lanes}.",
        f"- Assembly after the last gradient: {cc['parts']['assembly_s']} s.", "",
        "## The MP2 basis step (cc-pVTZ − cc-pVDZ)", "",
        f"- Machine: {mp2['machine']} ({mp2['machine_source']}).",
        f"- Jobs: {mp2['n_jobs']}, finished {mp2['first_job_ended']} → {mp2['last_job_ended']}. {bases}.",
        f"- Lanes sharing the machine while they ran: {mp2['lanes_sharing']} (threads per lane {mp2['threads_per_lane']}). Job time "
        f"{mp2['job_seconds']:,} s; charged {mp2['machine_seconds']:,} s = {hours(mp2['machine_seconds'])} → € {mp2['price']['eur_ex_vat']:.2f} "
        f"at € {mp2['price']['eur_per_hour']}/h.", "",
        "## What these numbers are and are not", "",
        "- They are the wall-clock time of the two runs that made the anchor in force, as those runs ran, at list prices. The "
        "coupled-cluster figure includes a lost first attempt and the one-off checks; both are stated above and neither is taken out.",
        "- A second molecule on the same environment does not repeat the two-route checks. That is a statement about the gate, not a "
        "measured cheaper price: no run without them has been timed on this machine, and the figure above is only a bound.",
        "- The coupled-cluster machine did not run this job alone: anchors.log names target-cache builds beside the first attempt "
        "as the cause of its kill. The machine was rented for the anchor, so the whole span is charged to it all the same.",
        "- The MP2 figure charges each job its own wall time divided by the lanes that ran; it does not include the queue's failed "
        "starts or another molecule's killed job and its rerun.",
        "- Not included: the B3LYP geometry, renting time before the launch (bootstrap, gate, smoke test) and after the last log "
        "line, VAT, and the person's time.",
        f"- It is {r['molecule']}'s price (18 atoms). A larger molecule costs more, and no larger molecule's composite is priced here.", ""])


def write_atomic(target: Path, content: str) -> None:
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")   # LF as the repository keeps its JSON, whatever the platform
    tmp.replace(target)


def read_logs(cc_dir: Path, mp2_dir: Path) -> dict:
    """The record of the real logs."""
    workers = sorted(mp2_dir.glob("worker_*.log"))
    if not workers:
        raise FileNotFoundError(f"no worker_*.log in {mp2_dir}")
    cc = parse_cc_run((cc_dir / "e8_fd.log").read_text(encoding="utf-8"), (cc_dir / "anchors.log").read_text(encoding="utf-8"))
    mp2 = parse_mp2_step((mp2_dir / "queue.log").read_text(encoding="utf-8"), (mp2_dir / "jobs.txt").read_text(encoding="utf-8"),
                         {w.name: w.read_text(encoding="utf-8") for w in workers}, MOLECULE)
    relative = {"cc_dz_hessian": [cc_dir / "e8_fd.log", cc_dir / "anchors.log"],
                "mp2_basis_step": [mp2_dir / "queue.log", mp2_dir / "jobs.txt", *workers]}
    return build_record(cc, mp2, {part: [p.resolve().relative_to(PLAN).as_posix() for p in files] for part, files in relative.items()})


def main() -> None:
    ap = argparse.ArgumentParser(description="Re-derive the price of naphthalene's composite anchor from its run logs.")
    ap.add_argument("--out", type=Path, default=OUT_DIR, help="folder for anchor_price.json and RESULT.md")
    a = ap.parse_args()
    record = read_logs(CC_DIR, MP2_DIR)
    a.out.mkdir(parents=True, exist_ok=True)
    write_atomic(a.out / "anchor_price.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    write_atomic(a.out / "RESULT.md", result_markdown(record))
    print(f"{MOLECULE}: CC/DZ Hessian {hours(record['cc_dz_hessian']['machine_seconds'])} € {record['cc_dz_hessian']['price']['eur_ex_vat']:.2f}; "
          f"MP2 basis step {hours(record['mp2_basis_step']['machine_seconds'])} € {record['mp2_basis_step']['price']['eur_ex_vat']:.2f}; "
          f"anchor € {record['anchor']['eur_ex_vat']:.2f} → {a.out}")


if __name__ == "__main__":
    main()
