#!/bin/bash
# v1.4's errors with aromir's own code (decision 66): the capstone form of the record, the hold-outs in aromir's layout,
# `aromir evaluate` on the measurement networks, then the record aromir ships, checked against the capstone form.
# Run from this folder in WSL: bash evaluate.sh <plan folder in WSL> <aromir's v1.3 evaluation.json>
set -euo pipefail
PLAN=$1
V13=$2
PY=~/aromir_dev/bin/python
export OMP_NUM_THREADS=2 PYTHONUNBUFFERED=1
echo "start $(date -Is)"
$PY make_evaluation_record.py capstone "$PLAN" "$V13" measurement/evaluation.json
cp measurement/evaluation.json evaluation_capstone.json
rm -rf holdouts
$PY ../aromir_audit_fixes_2026-11-16/holdouts_for_aromir.py "$PLAN" v14/E7_rungC_v14s3clean_c00_control_eval_clean_seed0.json holdouts a8=a b=b
nice -n 10 ~/aromir_dev/bin/aromir evaluate holdouts --release measurement --out measured.json
nice -n 10 $PY product_error.py "$PLAN" product_error.json measurement > product_error.txt
$PY make_evaluation_record.py aromir measured.json evaluation_capstone.json product_error.json evaluation.json
cp evaluation.json measurement/evaluation.json
cp evaluation.json release/evaluation.json
cp measured.json release/measured.json
cp measured.json measurement/measured.json
echo "end $(date -Is)"
