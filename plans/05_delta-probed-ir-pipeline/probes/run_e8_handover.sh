#!/bin/bash
# CCX53, 24 Sep 2026: when the running chain reports the benzene symmetric smoke PASS, stop that chain (it would start naphthalene as one
# slow process) and hand over to run_e8_naph_parallel.sh (three partial runs). On FAIL nothing is started; the user decides.
cd /root/e8 || exit 1
LOG=/root/e8/chain_ccx53.log
until grep -q "benzene symmetric = full: PASS\|BENZENE SYMMETRIC vs FULL: FAIL\|BENZENE SYMMETRIC SMOKE FAILED" $LOG; do sleep 60; done
if grep -q "benzene symmetric = full: PASS" $LOG; then
  pkill -f "[b]ash ./run_e8_ccx53.sh"; pkill -f "[b]ash run_e8_ccx53.sh"; sleep 2
  pkill -f "[e]8_cc_hessian_fd.py molecules/A_01f3186607"; sleep 2
  rm -f results/naphthalene_ccpvdz/stdout.log
  echo "[$(date "+%F %T")] handover: single-process naphthalene stopped; starting the three partial runs" >> $LOG
  nohup setsid bash ./run_e8_naph_parallel.sh > /root/e8/run_e8_naph_parallel.out 2>&1 < /dev/null &
else
  echo "[$(date "+%F %T")] handover: benzene smoke did not pass; nothing started" >> $LOG
fi
