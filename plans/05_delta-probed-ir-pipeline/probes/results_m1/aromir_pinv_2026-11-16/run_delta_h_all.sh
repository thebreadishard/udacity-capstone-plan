#!/usr/bin/env bash
# run_delta_h_all.sh <windows deps folder> — aromir's ΔH for ids_reread.txt four times (TASKS 236): the fixed source (~/aromir-src,
# branch pinv-rank) and the unfixed one (~/aromir-main, main at 43d93a4), each in WSL (~/aromir_dev) and on Windows (the system
# Python with safetensors from the folder given), then the comparisons. Run from Git Bash in this folder.
set -uo pipefail
# no-set-e: each read's end line is printed, a failed read shows in its log
DEPS=${1:?folder that holds safetensors for the Windows Python}
HERE=/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/results_m1/aromir_pinv_2026-11-16
export PYTHONUTF8=1 OMP_NUM_THREADS=4
for which in fixed:aromir-src before:aromir-main; do
  tag=${which%%:*}; src=${which##*:}
  MSYS_NO_PATHCONV=1 wsl.exe -e bash -lc "cd $HERE && export OMP_NUM_THREADS=4 PYTHONUTF8=1 && PYTHONPATH=\$HOME/$src/src ~/aromir_dev/bin/python aromir_delta_h.py ../../.. ids_reread.txt delta_h_wsl_$tag.npz > delta_h_wsl_$tag.log 2>&1; tail -1 delta_h_wsl_$tag.log"
  PYTHONPATH="$DEPS;//wsl.localhost/Ubuntu/home/thebreadishard/$src/src" python aromir_delta_h.py ../../.. ids_reread.txt "delta_h_windows_$tag.npz" > "delta_h_windows_$tag.log" 2>&1
  tail -1 "delta_h_windows_$tag.log"
done
{
  python compare_delta_h.py delta_h_wsl_fixed.npz delta_h_windows_before.npz compare_wsl_fixed_vs_windows_before.json
  python compare_delta_h.py delta_h_wsl_fixed.npz delta_h_windows_before.npz compare18_wsl_fixed_vs_windows_before.json --ids ids_seleval18.txt --show 18
  python compare_delta_h.py delta_h_wsl_fixed.npz delta_h_windows_fixed.npz compare_wsl_fixed_vs_windows_fixed.json --show 3
  python compare_delta_h.py delta_h_windows_fixed.npz delta_h_windows_before.npz compare_windows_fixed_vs_before.json --show 2
  python compare_delta_h.py delta_h_wsl_before.npz delta_h_windows_before.npz compare_wsl_before_vs_windows_before.json --show 3
} 2>&1 | tee compare_delta_h.log
