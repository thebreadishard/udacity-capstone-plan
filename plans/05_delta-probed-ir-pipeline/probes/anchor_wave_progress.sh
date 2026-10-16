#!/usr/bin/env bash
# probes/anchor_wave_progress.sh <list file> [--dry-run] (16 Oct 2026; TASKS 51, anchor set three wave 2) — runs probes/anchor_wave.sh on the
# list and gives tools/runspec.py the progress lines it needs. The wave's own log (anchors.log) has a line per stage, hours apart; the work
# in between is files: the FD gradients (grad_*.npy) and the field route's cached fields (apt_ccsd_t_field.npz.fields/). Every INTERVAL_S
# this wrapper counts those files for the list's molecules and prints a progress line only when the count changed, so a stalled wave
# prints nothing and the runspec's progress gap raises the alarm. Its last line is "wave done" (exit 0) or "wave FAILED rc=N".
#   bash probes/anchor_wave_progress.sh /root/dpir/wave2.txt            (through tools/runspec.py, probes/runspecs/anchors3_wave2.json)
#   bash probes/anchor_wave_progress.sh /root/dpir/wave2.txt --dry-run  (list, geometries and python checked; nothing runs)
# The environment (ROOT, PY, LOG, TWO_ROUTE, FAST) passes through to anchor_wave.sh unchanged.
# no-set-e: the wave's exit code is read and reported, not propagated by the shell
set -u
LIST=${1:?list file}
ROOT=${ROOT:-/root/dpir/probes}
PY=${PY:-/root/miniforge3/envs/qc05/bin/python}
INTERVAL_S=${INTERVAL_S:-600}
say() { echo "=== (AS3W) $* $(date '+%F %T')"; }

[ -f "$LIST" ] || { say "wave FAILED: no list file $LIST"; exit 2; }
names=()
while IFS='|' read -r name geom _rest; do
  [ -z "$name" ] && continue
  [ -f "$geom" ] || { say "wave FAILED: $name has no geometry $geom"; exit 2; }
  names+=("$name")
done < "$LIST"
[ "${#names[@]}" -gt 0 ] || { say "wave FAILED: $LIST lists no molecule"; exit 2; }

if [ "${2:-}" = "--dry-run" ]; then
  [ -x "$PY" ] || { say "dry run FAILED: no python at $PY"; exit 2; }
  [ -f "$ROOT/anchor_wave.sh" ] || { say "dry run FAILED: no $ROOT/anchor_wave.sh"; exit 2; }
  bash -n "$ROOT/anchor_wave.sh" || { say "dry run FAILED: anchor_wave.sh does not parse"; exit 2; }
  say "dry run ok: ${names[*]} from $LIST"
  exit 0
fi

count_files() {
  local n=0 name out
  for name in "${names[@]}"; do
    out="$ROOT/results/${name}_ccpvdz"
    n=$((n + $(find "$out" -maxdepth 1 -name 'grad_*.npy' 2>/dev/null | wc -l)))
    n=$((n + $(find "$out/apt_ccsd_t_field.npz.fields" -maxdepth 1 -type f 2>/dev/null | wc -l)))
  done
  echo "$n"
}

bash "$ROOT/anchor_wave.sh" "$LIST" < /dev/null &
wave=$!
say "wave started (pid $wave): ${names[*]}"
last=$(count_files)
while kill -0 "$wave" 2>/dev/null; do
  sleep "$INTERVAL_S" & wait $!
  now=$(count_files)
  [ "$now" != "$last" ] && say "progress: $now result files (was $last)"
  last=$now
done
wait "$wave"; rc=$?
if [ "$rc" -eq 0 ]; then say "wave done"; else say "wave FAILED rc=$rc"; fi
exit "$rc"
