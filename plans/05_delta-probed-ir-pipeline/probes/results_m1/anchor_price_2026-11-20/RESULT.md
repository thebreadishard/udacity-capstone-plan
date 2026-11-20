# What naphthalene's anchor cost to compute — read from its run logs

Written by `probes/anchor_price_from_logs.py`; the numbers are in `anchor_price.json` beside this file. Prices are list prices ex VAT (`modules/08_industry_synthesis/m08/prices.py`).

**The anchor (composite, decision 62): 21.28 machine-hours, € 5.83.**

**Attribution rule.** A machine-hour is a wall-clock hour of the rented machine, charged to the molecule by the share of the machine's lanes that worked for it: a run the machine was rented for is charged its whole wall-clock span from launch to end, lost attempts and idle gaps included, also where other work ran beside it; a job in a queue of N lanes shared with other molecules is charged its own wall time / N, and the queue's own losses (failed starts, another molecule's killed job) are not charged to this molecule.

## The CCSD(T)/cc-pVDZ Hessian

- Molecule: 18 atoms. Machine: ubuntu-32gb-hel1-2 (CPX62), rented for this run: share 1.
- As it ran: launched 2026-10-01 06:32:39, Hessian written VALID 2026-10-02 01:39:34: 68,815 s = 19.12 h → € 3.98 at € 0.208/h.
- Starts: 2 (the last at 2026-10-01 11:19:01). From the launch to the last start 17,182 s (4.77 h, € 0.99) produced nothing the Hessian uses.
- Reference gradient: 24,821 s (6.89 h). The timers of the one-off two-route checks of the (T) kernels against pyscf's slow routes read 5,609 s (lambda) + 18,817 s (density) = 24,426 s (€ 1.41). That is an upper bound on what the checks added: a timer may enclose work a reference gradient needs anyway, and no reference without the checks has been timed.
- Displaced gradients: 30 in 2 lanes, 2026-10-01 18:12:43 → 2026-10-02 01:39:12: 26,789 s = 7.44 h. lane 1: 14 gradients on 8 threads, 1,666–1,730 s each, 2026-10-01 18:12:43 → 2026-10-02 00:47:50 (6.59 h); lane 2: 16 gradients on 8 threads, 1,596–1,718 s each, 2026-10-01 18:12:48 → 2026-10-02 01:39:12 (7.44 h).
- Assembly after the last gradient: 22 s.

## The MP2 basis step (cc-pVTZ − cc-pVDZ)

- Machine: CCX53 (obstacle ledger, 7 Oct 17:2x (the MP2 rows queue on the CCX53); queue.log names its script mp2_rows_queue_ccx53.sh).
- Jobs: 30, finished 2026-10-07 10:53:57 → 2026-10-07 15:10:01. ccpvdz: 15 jobs, 76–82 s each, 1,186 s together; ccpvtz: 15 jobs, 1,937–2,053 s each, 29,924 s together.
- Lanes sharing the machine while they ran: [4] (threads per lane [8]). Job time 31,110 s; charged 7,777.5 s = 2.16 h → € 1.85 at € 0.855/h.

## What these numbers are and are not

- They are the wall-clock time of the two runs that made the anchor in force, as those runs ran, at list prices. The coupled-cluster figure includes a lost first attempt and the one-off checks; both are stated above and neither is taken out.
- A second molecule on the same environment does not repeat the two-route checks. That is a statement about the gate, not a measured cheaper price: no run without them has been timed on this machine, and the figure above is only a bound.
- The coupled-cluster machine did not run this job alone: anchors.log names target-cache builds beside the first attempt as the cause of its kill. The machine was rented for the anchor, so the whole span is charged to it all the same.
- The MP2 figure charges each job its own wall time divided by the lanes that ran; it does not include the queue's failed starts or another molecule's killed job and its rerun.
- Not included: the B3LYP geometry, renting time before the launch (bootstrap, gate, smoke test) and after the last log line, VAT, and the person's time.
- It is naphthalene's price (18 atoms). A larger molecule costs more, and no larger molecule's composite is priced here.
