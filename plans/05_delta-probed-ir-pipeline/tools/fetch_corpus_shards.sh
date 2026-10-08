#!/usr/bin/env bash
# fetch_corpus_shards.sh (8 Oct 2026; from the scratchpad's fetch_nextpool.sh of 2 Oct, which knew one server and two fixed directories and whose
# closing count line was broken) — pull manifest.csv, ledger.csv, the runner logs and the finished molecule folders of corpus runner directories on a
# rented server into corpus/<shards>/<name>/ (tar over ssh, psi4 scratch excluded); with "merge" they are then merged into the local corpus by
# corpus/merge_shards.py (a row is taken only when it is done/failed there and pending here; nothing is deleted; the manifest and ledger are backed up).
#   bash tools/fetch_corpus_shards.sh <user@host> <shards dir> <name>=<remote corpus dir> [<name>=<remote corpus dir> …] [merge]
#   bash tools/fetch_corpus_shards.sh root@46.62.227.91 shards_pool3 a=/root/…/corpus_p3 b=/root/…/corpus_p3b
set -u
# no-set-e: a failed fetch of one directory is reported and the others continue
KEY=$HOME/.ssh/hetzner_g_measure
HOST=$1; SHARDS=$2; shift 2
C=/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/corpus
MERGE=0; PAIRS=()
for x in "$@"; do
  if [ "$x" = merge ]; then MERGE=1; else PAIRS+=("$x"); fi
done
[ ${#PAIRS[@]} -gt 0 ] || { echo "give at least one <name>=<remote corpus dir>"; exit 2; }
fetched=()
for p in "${PAIRS[@]}"; do
  name=${p%%=*}; remote=${p#*=}
  dest="$C/$SHARDS/$name"
  mkdir -p "$dest"
  ssh -i "$KEY" -o ConnectTimeout=25 -o BatchMode=yes "$HOST" \
    "cd '$remote' && tar czf - --exclude='psi4.out' --exclude='worker_stdout.txt' --exclude='psi.*.clean' --exclude='*.pre_fetch*' --exclude='timer.dat' --exclude='*.tmp' manifest.csv ledger.csv \$(ls *.log 2>/dev/null) molecules 2>/dev/null" \
    < /dev/null > "$dest.tgz"
  if [ -s "$dest.tgz" ] && (cd "$dest" && tar xzf "../$name.tgz"); then
    echo "$name: $(ls "$dest/molecules" 2>/dev/null | wc -l) molecule folders; manifest $(grep -c ',done,' "$dest/manifest.csv") done, $(grep -c ',failed,' "$dest/manifest.csv") failed rows"
    fetched+=("$SHARDS/$name/")
  else
    echo "$name: nothing fetched from $HOST:$remote (ssh failed or empty)"
  fi
  rm -f "$dest.tgz"
done
if [ $MERGE = 1 ] && [ ${#fetched[@]} -gt 0 ]; then
  (cd "$C" && PYTHONUTF8=1 python merge_shards.py "${fetched[@]}" 2>&1 | tail -n 8)
fi
