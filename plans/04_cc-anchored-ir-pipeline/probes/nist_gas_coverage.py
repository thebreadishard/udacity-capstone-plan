"""Does NIST WebBook hold GAS-PHASE infrared spectra for the R2/R3 molecules?

WHY THIS PROBE EXISTS (2026-09-02)

  Round-6 Pass B, finding 1: the R2-R3 "beat" comparisons are only decidable if a
  gas-phase scoreboard exists for pyrene / tetracene / chrysene (R2) and coronene
  (R3). Ar-matrix positions carry a shift systematic that may exceed the beat
  margin. The standing disagreement with the reviewer is whether the M03
  matrix-gas gate can ever open. That is an empirical question. This probe asks
  the empirical half of it: which of the promised molecules have gas-phase IR in
  the NIST WebBook at all, and at what resolution and coverage.

  This is a coverage probe, not the M03 statistics. It downloads the raw JCAMP-DX
  files, reads their metadata (##STATE, points, range, grid), and prints a table.
  Band positions and matrix-vs-gas deltas are M03's job, under its own hash.

METHOD

  JCAMP fetch recipe carried from plan-02 probes/verify_oop_bands_2026-08-27.py
  (git history): webbook.nist.gov/cgi/cbook.cgi?JCAMP=C<CAS>&Index=<i>&Type=IR.
  NIST serves one spectrum per index; indices are scanned until two consecutive
  misses. Phase is read from ##STATE; some records put it in ##TITLE, both are
  reported. Files are cached in nist_cache/ so reruns are offline.

Run:  python nist_gas_coverage.py
Exit: prints a per-molecule table and a GATE INPUT summary; prints NOT_RUN per
      molecule if the network fails and no cache exists.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from pathlib import Path

CACHE = Path(__file__).parent / "nist_cache"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"}
MAX_INDEX = 12  # scan 0..MAX_INDEX, stop after 2 consecutive misses
DELAY_S = 5.0   # politeness delay between live requests; NIST rate-limits bursts
RETRIES = 4

# rung, name, NIST id ("C" + CAS without punctuation)
MOLECULES = [
    ("R0 (promised, gas expected)", "benzene",      "C71432"),
    ("R1 (promised, gas expected)", "naphthalene",  "C91203"),
    ("R2 (promised, A-scored)",     "pyrene",       "C129000"),
    ("R2 (promised, A-scored)",     "tetracene",    "C92240"),
    ("R2 (promised, A-scored)",     "chrysene",     "C218019"),
    ("R2 (reported, not scored)",   "triphenylene", "C217594"),
    ("R3 (promised, A-scored)",     "coronene",     "C191071"),
]


def fetch(nist_id: str, index: int) -> str | None:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"{nist_id}_{index}.jdx"
    miss = CACHE / f"{nist_id}_{index}.miss"
    if path.exists():
        return path.read_text(encoding="utf-8")
    if miss.exists():
        return None
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={nist_id}&Index={index}&Type=IR"
    text = None
    for attempt in range(RETRIES):
        time.sleep(DELAY_S * (attempt + 1))
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                text = r.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            # NIST answers a nonexistent index with 404 + "##TITLE=Spectrum not found."
            # That is a definitive miss, not a network failure. (Learned 2026-09-03:
            # an earlier version retried these for six hours.)
            if e.code == 404:
                miss.write_text("", encoding="utf-8")
                return None
            continue
        except Exception:
            continue
    if text is None:
        raise ConnectionError(url)
    if "##XYDATA" not in text and "##PEAK TABLE" not in text:
        miss.write_text("", encoding="utf-8")
        return None
    path.write_text(text, encoding="utf-8")
    return text


def meta_of(text: str) -> dict:
    meta = {}
    for line in text.splitlines():
        if line.startswith("##") and "=" in line:
            key, val = line[2:].split("=", 1)
            meta[key.strip().upper()] = val.strip()
    return meta


def describe(meta: dict) -> tuple[str, str]:
    state = meta.get("STATE", "?").lower()
    npoints = meta.get("NPOINTS", "?")
    firstx, lastx = meta.get("FIRSTX"), meta.get("LASTX")
    rng = "?"
    grid = "?"
    if firstx and lastx and npoints not in (None, "?"):
        try:
            lo, hi, n = float(firstx), float(lastx), int(npoints)
            lo, hi = min(lo, hi), max(lo, hi)
            rng = f"{lo:.0f}-{hi:.0f}"
            if n > 1:
                grid = f"{(hi - lo) / (n - 1):.1f}"
        except ValueError:
            pass
    return state, f"{npoints} pts, {rng} cm-1, grid ~{grid}"


def main() -> None:
    # verdicts: True = gas found (definitive even if the scan later broke);
    # False = full scan, no gas; None = scan incomplete and no gas seen yet.
    gas_by_name: dict[str, bool | None] = {}
    for rung, name, nist_id in MOLECULES:
        print(f"\n{name}  ({nist_id})  —  {rung}")
        found_any, gas_found, misses, complete = False, [], 0, True
        for index in range(MAX_INDEX + 1):
            try:
                text = fetch(nist_id, index)
            except ConnectionError as exc:
                print(f"  scan incomplete: network failure at index {index} ({exc})")
                complete = False
                break
            if text is None:
                misses += 1
                if misses >= 2 and found_any:
                    break
                continue
            misses = 0
            found_any = True
            state, desc = describe(meta_of(text))
            marker = "GAS " if "gas" in state else "     "
            if "gas" in state:
                gas_found.append(index)
            print(f"  {marker}index {index}: state={state or '?'};  {desc}")
        if not found_any and complete:
            print("  no IR spectra of any phase in the WebBook")
        gas_by_name[name] = True if gas_found else (False if complete else None)

    print("\n" + "=" * 72)
    print("GATE INPUT (coverage only; deltas are M03's job):")
    scored = [("pyrene", "R2"), ("tetracene", "R2"), ("chrysene", "R2"), ("coronene", "R3")]
    for name, rung in scored:
        val = gas_by_name.get(name)
        verdict = ("gas-phase IR PRESENT" if val
                   else "gas-phase IR ABSENT (full scan)" if val is False
                   else "INCOMPLETE (rerun; cache keeps progress)")
        print(f"  {rung} {name:12s}: {verdict}")
    known = [v for n, _ in scored if (v := gas_by_name.get(n)) is not None]
    if known:
        print(f"  => the M03 matrix-gas gate has NIST gas input for {sum(known)} of {len(known)}"
              " checked A-scored R2/R3 molecules.")
        print("     ABSENT does not close the gate by itself (other verified gas sources may"
              " exist: PAHdb gas library, literature); PRESENT means the gate can open.")


if __name__ == "__main__":
    main()
