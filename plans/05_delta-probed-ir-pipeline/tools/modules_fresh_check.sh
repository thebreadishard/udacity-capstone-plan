#!/bin/bash
# Fresh-environment check of Udacity modules 02-04 (22 Sep 2026, decision 47 spirit): for each module, a new venv,
# `pip install -r requirements.txt` exactly as a grader would, then the notebook executed top to bottom with nbconvert.
# If the frozen requirements do not install on Linux (Windows-only wheels), that is recorded and a fallback set is installed
# so that the notebook itself can still be judged. Output: /root/modules_check/modules_fresh_check.log and per-module logs.
set -u
ROOT=/root/modules_check
LOG=$ROOT/modules_fresh_check.log
PY=/root/miniforge3/bin/python3
cd $ROOT || exit 1
echo "[$(date '+%F %T')] start; python $($PY --version 2>&1)" > $LOG
for m in 02_opponent_atlas 03_lab_scoreboard 04_calibrated_harmonic; do
  d=$ROOT/modules/$m
  echo "[$(date '+%F %T')] === $m" >> $LOG
  $PY -m venv $ROOT/venv_$m >> $ROOT/$m.pip.log 2>&1
  VPY=$ROOT/venv_$m/bin/python
  $VPY -m pip install --quiet --upgrade pip >> $ROOT/$m.pip.log 2>&1
  if $VPY -m pip install --quiet -r $d/requirements.txt >> $ROOT/$m.pip.log 2>&1; then
    echo "  requirements.txt installed cleanly" >> $LOG
  else
    nbad=$(grep -ciE "error|no matching distribution" $ROOT/$m.pip.log)
    echo "  requirements.txt did NOT install as frozen ($nbad error lines; first: $(grep -iE 'no matching distribution|error' $ROOT/$m.pip.log | head -n 1 | cut -c1-140))" >> $LOG
    echo "  fallback: installing the packages the notebook imports" >> $LOG
    $VPY -m pip install --quiet jupyter nbconvert ipykernel pandas numpy matplotlib scipy scikit-learn seaborn statsmodels python-docx >> $ROOT/$m.pip.log 2>&1
  fi
  $VPY -m pip install --quiet nbconvert ipykernel jupyter_client >> $ROOT/$m.pip.log 2>&1
  nb=$(ls $d/notebook/*.ipynb | head -n 1)
  echo "  executing $(basename $nb)" >> $LOG
  t0=$(date +%s)
  if (cd $d/notebook && timeout 3600 nice -n 10 $VPY -m nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 --output executed_check.ipynb "$(basename $nb)" > $ROOT/$m.nb.log 2>&1); then
    echo "  notebook ran top to bottom in $(( $(date +%s) - t0 )) s" >> $LOG
  else
    echo "  NOTEBOOK FAILED after $(( $(date +%s) - t0 )) s; last lines:" >> $LOG
    grep -vE "^\s*$" $ROOT/$m.nb.log | tail -n 6 | cut -c1-160 | sed 's/^/    /' >> $LOG
  fi
  echo "  imports not in requirements.txt (heuristic):" >> $LOG
  $VPY - "$nb" "$d/requirements.txt" >> $LOG 2>&1 <<'EOF'
import json, re, sys
nb, req = sys.argv[1], sys.argv[2]
cells = json.load(open(nb))["cells"]
mods = set()
for c in cells:
    if c["cell_type"] != "code": continue
    for line in "".join(c["source"]).splitlines():
        m = re.match(r"\s*(?:from|import)\s+([A-Za-z_][\w]*)", line)
        if m: mods.add(m.group(1))
std = {"os","sys","re","json","math","pathlib","itertools","collections","datetime","hashlib","warnings","io","textwrap","functools","typing","glob","subprocess","time","string","random","csv","zipfile","gzip","urllib","shutil"}
alias = {"sklearn":"scikit-learn","PIL":"pillow","yaml":"pyyaml","docx":"python-docx"}
reqs = {l.split("==")[0].split(">=")[0].strip().lower().replace("_","-") for l in open(req) if l.strip() and not l.startswith("#")}
missing = sorted(m for m in mods if m not in std and alias.get(m, m).lower().replace("_","-") not in reqs)
print("    " + (", ".join(missing) if missing else "none"))
EOF
done
echo "[$(date '+%F %T')] DONE" >> $LOG
