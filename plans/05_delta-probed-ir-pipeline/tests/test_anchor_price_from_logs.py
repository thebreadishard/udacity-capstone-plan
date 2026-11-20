"""The anchor's price from its run logs (`probes/anchor_price_from_logs.py`, TASKS 290), on synthetic log text with the edge cases —
a restarted run, lanes that end at different times, a missing gradient line, a queue restarted with fewer lanes, a day change in a
worker log — and on the real logs where the record on disk must be what the script reads today."""
import json
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anchor_price_from_logs as AP  # noqa: E402  (after the sys.path insert)

HOST = "ubuntu-32gb-hel1-9"
HEADER = "E8 FD Hessian: 3 atoms, cc-pvdz, frozen 2, step 0.005 bohr, 9 displacements, {threads} threads, max_memory 9000 MB"
SYMMETRY = "symmetry: 2 operations, orbits [[0, 1], [2]], 3 displacements (6 gradients) instead of 9"
# (time, coordinate, sign, seconds): lane 1 holds coordinates 0 and 1 and ends at 08:40:00, lane 2 holds 7 and ends at 09:00:05
GRADIENTS = (("08:10:00", 0, "p", 600), ("08:20:00", 0, "m", 600), ("08:30:00", 1, "p", 600), ("08:30:05", 7, "p", 1800),
             ("08:40:00", 1, "m", 600), ("09:00:05", 7, "m", 1800))


def stamp(time: str, body: str) -> str:
    return f"[2026-10-01 {time}] {body}"


def anchors_log(starts: tuple[str, ...] = ("06:00:00", "07:00:00"), host: str = HOST) -> str:
    return "\n".join(stamp(t, f"chain (corrected route) start on {host}") for t in starts)


def fd_log(gradients: tuple = GRADIENTS, reference_s: int = 3600) -> str:
    """A run launched at 06:00, killed, relaunched at 07:00: the first attempt's check line must not be counted."""
    lines = [stamp("06:00:00", HEADER.format(threads=16)),
             stamp("06:30:00", "fast (T) lambda two-route check: max |kernel − pyscf| = 2.1e-17 (l2_t; limit 1e-10; 1700 s)"),
             stamp("07:00:00", HEADER.format(threads=16)),
             stamp("07:20:00", "fast (T) lambda two-route check: max |kernel − pyscf| = 1.7e-17 (l2_t; limit 1e-10; 1000 s)"),
             "cycle = 1  norm(lambda1,lambda2) = 0.07",
             stamp("07:50:00", "fast (T) density two-route check: max |kernel − pyscf| = 3.5e-17 (doo[for_grad=False]; limit 1e-10; 1500 s)"),
             stamp("08:00:00", "(T) lambda 1600 s, gradient 5 s"),
             stamp("08:00:00", f"reference: E = -76.241, max|grad| 7.87e-03, {reference_s} s"),
             stamp("08:00:00", HEADER.format(threads=8)), stamp("08:00:00", SYMMETRY),
             stamp("08:00:00", "partial run: displacement indices [0, 1]"),
             stamp("08:00:05", HEADER.format(threads=4)), stamp("08:00:05", SYMMETRY),
             stamp("08:00:05", "partial run: displacement indices [7]")]
    for i, (time, k, sign, s) in enumerate(gradients):
        lines.append(stamp(time, f"coordinate {k:2d} {sign}: E − E0 =    -18.47 µE_h, {s} s  ({i + 1}/54 gradients)"))
        if sign == "m":
            lines.append(stamp(time, f"pair check coordinate {k:2d}: max |mean(g+, g−) − g0| = 1.5e-05 a.u. (limit 1e-04)"))
    lines += [stamp("09:00:30", HEADER.format(threads=16)), stamp("09:00:30", SYMMETRY),
              stamp("09:00:30", "Hessian written (VALID); FD asymmetry max 1.61e-05 a.u.")]
    return "\n".join(lines)


def test_a_restarted_run_is_charged_from_its_first_launch_and_names_what_was_lost() -> None:
    cc = AP.parse_cc_run(fd_log(), anchors_log())
    assert (cc["host"], cc["machine"], cc["n_starts"]) == (HOST, "CPX62", 2)
    assert cc["wall_s"] == cc["machine_seconds"] == 3 * 3600 + 30
    assert cc["parts"] == dict(lost_before_relaunch_s=3600, reference_s=3600, gradients_s=3605, assembly_s=25)
    assert sum(cc["parts"].values()) == cc["wall_s"]


def test_only_the_finished_attempts_two_route_checks_are_counted() -> None:
    reference = AP.parse_cc_run(fd_log(), anchors_log())["reference"]
    assert reference["two_route_checks_s"] == {"lambda": 1000, "density": 1500}
    assert reference["two_route_checks_sum_s"] == 2500 and "seconds_without_checks" not in reference


def test_lanes_that_end_at_different_times_keep_their_own_spans_and_threads() -> None:
    grads = AP.parse_cc_run(fd_log(), anchors_log())["gradients"]
    first, second = grads["lanes"]
    assert (first["displacements"], first["threads"], first["n_gradients"], first["span_s"]) == ([0, 1], 8, 4, 2400)
    assert (second["displacements"], second["threads"], second["n_gradients"], second["span_s"]) == ([7], 4, 2, 3600)
    assert first["gradient_s"]["sum"] == 2400 and second["gradient_s"] == dict(min=1800, max=1800, sum=3600, each=[1800, 1800])
    assert (grads["n_gradients"], grads["span_s"], grads["ended"]) == (6, 3605, "2026-10-01 09:00:05")


def test_a_run_that_started_once_lost_nothing() -> None:
    cc = AP.parse_cc_run(fd_log().split("\n", 2)[2], anchors_log(starts=("07:00:00",)))
    assert cc["n_starts"] == 1 and cc["parts"]["lost_before_relaunch_s"] == 0 and cc["wall_s"] == 2 * 3600 + 30


def test_a_missing_gradient_line_raises_and_names_the_coordinate() -> None:
    without = tuple(g for g in GRADIENTS if (g[1], g[2]) != (7, "m"))
    with pytest.raises(ValueError, match="lacks the gradient line of coordinate 7 m"):
        AP.parse_cc_run(fd_log(gradients=without), anchors_log())


def test_a_gradient_line_given_twice_raises() -> None:
    with pytest.raises(ValueError, match="coordinate 0 p has two gradient lines"):
        AP.parse_cc_run(fd_log(gradients=(*GRADIENTS, ("08:50:00", 0, "p", 600))), anchors_log())


def test_a_reference_line_that_does_not_fit_its_stamps_raises() -> None:
    with pytest.raises(ValueError, match="not the same attempt"):
        AP.parse_cc_run(fd_log(reference_s=9000), anchors_log())


def test_a_log_without_a_valid_hessian_or_with_two_hosts_raises() -> None:
    with pytest.raises(ValueError, match="exactly one 'Hessian written"):
        AP.parse_cc_run(fd_log().replace("(VALID)", "(IMAGINARY)"), anchors_log())
    two_hosts = anchors_log(starts=("06:00:00",)) + "\n" + anchors_log(starts=("07:00:00",), host="ubuntu-32gb-hel1-3")
    with pytest.raises(ValueError, match="several hosts"):
        AP.parse_cc_run(fd_log(), two_hosts)


QUEUE = ("=== QUEUE start: 4 jobs, 2 workers x 8 threads, max_memory 26000 2026-10-07 23:00:00 UTC\n"
         "mp2_rows_queue_ccx53.sh: line 24: 390182 Killed                  OMP_NUM_THREADS=8 $PY cc_composite_full_check.py compute\n"
         "--- heartbeat 2026-10-07 23:59:59 UTC: 1 of 4 jobs done; 2 workers; 120 GB free\n"
         "=== QUEUE start: 4 jobs, 1 workers x 8 threads, max_memory 60000 2026-10-08 01:00:00 UTC\n")
JOBS = "naphthalene|A_01|cc-pvtz|0|g.json\nnaphthalene|A_01|cc-pvdz|0|g.json\nnaphthalene|A_01|cc-pvtz|1|g.json\nanthracene|A_02|cc-pvtz|0|g.json\n"


def job(time: str, basis: str, k: int, s: int, molecule: str) -> str:
    return f"[{time}] mp2 {basis} k={k}: H_kk +0.738459 ({s} s)\n→ rows/{molecule}_{basis.replace('-', '')}_k{k}.npz.part.npz (1 displacements)\n"


def workers() -> dict[str, str]:
    """Worker 0 runs past midnight under two lanes; worker 1's last job ends after the queue restarted with one lane."""
    return {"worker_0.log": job("23:30:00", "cc-pvtz", 0, 1000, "naphthalene") + job("00:10:00", "cc-pvdz", 0, 100, "naphthalene"),
            "worker_1.log": job("23:40:00", "cc-pvtz", 0, 2000, "anthracene") + job("01:30:00", "cc-pvtz", 1, 600, "naphthalene")}


def test_a_job_is_charged_its_wall_time_over_the_lanes_of_the_queue_start_it_ran_under() -> None:
    mp2 = AP.parse_mp2_step(QUEUE, JOBS, workers(), "naphthalene")
    assert (mp2["n_jobs"], mp2["job_seconds"], mp2["lanes_sharing"], mp2["threads_per_lane"]) == (3, 1700, [1, 2], [8])
    assert mp2["by_basis"]["ccpvtz"]["machine_seconds"] == 1000 / 2 + 600 / 1 and mp2["by_basis"]["ccpvdz"]["machine_seconds"] == 100 / 2
    assert mp2["machine_seconds"] == 1150.0
    assert (mp2["first_job_ended"], mp2["last_job_ended"]) == ("2026-10-07 23:30:00", "2026-10-08 01:30:00")


def test_another_molecules_jobs_are_not_charged() -> None:
    assert AP.parse_mp2_step(QUEUE, JOBS, workers(), "anthracene")["machine_seconds"] == 1000.0


def test_a_job_the_list_names_and_no_worker_finished_raises() -> None:
    logs = workers() | {"worker_1.log": job("23:40:00", "cc-pvtz", 0, 2000, "anthracene")}
    with pytest.raises(ValueError, match="no worker log holds the finished job of naphthalene ccpvtz k=1"):
        AP.parse_mp2_step(QUEUE, JOBS, logs, "naphthalene")


def test_a_job_finished_twice_or_without_its_rows_line_raises() -> None:
    twice = workers() | {"worker_2.log": job("23:50:00", "cc-pvtz", 0, 900, "naphthalene")}
    with pytest.raises(ValueError, match="finished twice"):
        AP.parse_mp2_step(QUEUE, JOBS, twice, "naphthalene")
    bare = workers() | {"worker_2.log": "[23:50:00] mp2 cc-pvtz k=5: H_kk +0.1 (900 s)\n"}
    with pytest.raises(ValueError, match="not followed by its own rows line"):
        AP.parse_mp2_step(QUEUE, JOBS, bare, "naphthalene")


def test_a_molecule_without_jobs_or_a_log_without_a_queue_start_raises() -> None:
    with pytest.raises(ValueError, match="names no job of pyrene"):
        AP.parse_mp2_step(QUEUE, JOBS, workers(), "pyrene")
    with pytest.raises(ValueError, match="no '=== QUEUE start' line"):
        AP.parse_mp2_step("mp2_rows_queue_ccx53.sh: line 24\n--- heartbeat\n", JOBS, workers(), "naphthalene")


def test_the_record_prices_each_part_on_its_own_machine_and_adds_them() -> None:
    record = AP.build_record(AP.parse_cc_run(fd_log(), anchors_log()), AP.parse_mp2_step(QUEUE, JOBS, workers(), "naphthalene"), {})
    cc, mp2 = record["cc_dz_hessian"], record["mp2_basis_step"]
    assert cc["price"] == dict(machine="CPX62", machine_hours=3.008, eur_per_hour=0.208, eur_ex_vat=0.63)
    assert mp2["price"] == dict(machine="CCX53", machine_hours=0.319, eur_per_hour=0.855, eur_ex_vat=0.27)
    assert cc["of_which_eur"] == dict(two_route_checks_at_most=0.14, lost_before_relaunch=0.21)
    assert record["anchor"] == dict(machine_hours=3.328, eur_ex_vat=0.9)
    text = AP.result_markdown(record)
    assert "3.33 machine-hours, € 0.90" in text and "Starts: 2" in text and "1,000 s (lambda) + 1,500 s (density) = 2,500 s" in text
    assert "upper bound on what the checks added" in text and "without them the reference is" not in text


def test_the_record_on_disk_is_what_the_script_reads_from_the_real_logs(tmp_path: Path) -> None:
    """The record `m08/prices.py` cites, re-derived: the tracked logs give the tracked record, to the byte."""
    record = AP.read_logs(AP.CC_DIR, AP.MP2_DIR)
    AP.write_atomic(tmp_path / "anchor_price.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    AP.write_atomic(tmp_path / "RESULT.md", AP.result_markdown(record))
    for name in ("anchor_price.json", "RESULT.md"):
        assert (tmp_path / name).read_text(encoding="utf-8") == (AP.OUT_DIR / name).read_text(encoding="utf-8"), f"{name} is not the script's output"
    lanes = record["cc_dz_hessian"]["gradients"]["lanes"]
    assert [(lane["n_gradients"], lane["threads"], lane["ended"]) for lane in lanes] == [(14, 8, "2026-10-02 00:47:50"), (16, 8, "2026-10-02 01:39:12")]


def test_the_record_holds_the_atom_count_of_the_run_headers() -> None:
    assert AP.parse_cc_run(fd_log(), anchors_log())["n_atoms"] == 3
    mixed = fd_log().replace("3 atoms", "4 atoms", 1)
    with pytest.raises(ValueError, match=r"name \[3, 4\] as atom counts"):
        AP.parse_cc_run(mixed, anchors_log())


def test_two_hessian_written_lines_or_a_check_given_twice_raise() -> None:
    twice = fd_log() + "\n" + stamp("09:10:00", "Hessian written (VALID); FD asymmetry max 1.61e-05 a.u.")
    with pytest.raises(ValueError, match=r"exactly one 'Hessian written \(VALID\)' line in the log, found 2"):
        AP.parse_cc_run(twice, anchors_log())
    again = fd_log().replace(stamp("07:50:00", "fast (T) density"), stamp("07:50:00", "fast (T) lambda"))
    with pytest.raises(ValueError, match="two lambda two-route check lines in one attempt"):
        AP.parse_cc_run(again, anchors_log())


def test_a_queue_log_that_does_not_name_the_ccx53_script_is_not_priced() -> None:
    with pytest.raises(ValueError, match=r"does not name mp2_rows_queue_ccx53\.sh"):
        AP.parse_mp2_step(QUEUE.replace("mp2_rows_queue_ccx53.sh", "mp2_rows_queue.sh"), JOBS, workers(), "naphthalene")


def test_a_run_on_a_machine_the_price_table_does_not_hold_is_refused_with_the_reason() -> None:
    cc = AP.parse_cc_run(fd_log(), anchors_log(host="some-new-host"))
    assert cc["machine"] == "unknown"
    with pytest.raises(ValueError, match="machine class is 'unknown': the price table has no list price"):
        AP.priced(cc)
