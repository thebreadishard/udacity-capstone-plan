#!/usr/bin/env bash
# probes/uhf_t_blocked_bench.sh <cap MB> <threads> -- <bench arguments> (26 Oct 2026, software ledger row 52) — the blocked open-shell
# CCSD(T) gradient bench (probes/uhf_t_blocked_bench.py) in WSL with qc05's pyscf, under probes/wsl_capped.sh so the run spec's memory
# bound is the cap. Bench paths are WSL paths (/mnt/c/...); '--dry-run' among the bench arguments prints the sizes only, uncapped.
#   bash probes/uhf_t_blocked_bench.sh 12288 8 -- /mnt/c/.../geometry.json /mnt/c/.../out --charge 1 --spin 1 --block 16
set -euo pipefail
CAP=${1:?cap in MB}; THREADS=${2:?threads}; shift 2
[ "${1:-}" = "--" ] && shift
[ "$#" -gt 0 ] || { echo "uhf_t_blocked_bench.sh: no bench arguments"; exit 2; }
PW=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline
ARGS=$(printf '%q ' "$@")
ENV="export OMP_NUM_THREADS=$THREADS PYTHONUNBUFFERED=1 PYSCF_TMPDIR=\$HOME/qc_tmp TMPDIR=\$HOME/qc_tmp; mkdir -p \$HOME/qc_tmp; cd $PW"
case " $* " in
  *" --dry-run "*) MSYS_NO_PATHCONV=1 wsl -e bash -c "$ENV && \$HOME/qc05/bin/python probes/uhf_t_blocked_bench.py $ARGS --threads $THREADS" ;;
  *) MSYS_NO_PATHCONV=1 wsl -e bash -c "$ENV && bash probes/wsl_capped.sh $CAP -- /usr/bin/time -f '(UB) max RSS %M kB, wall %e s' \
       \$HOME/qc05/bin/python probes/uhf_t_blocked_bench.py $ARGS --threads $THREADS --max-memory $((CAP * 85 / 100))" ;;
esac
