# Hardware note — a €5,000 workstation for the anchor runs (proposed 2026-09-10, parked by the user)

**Status (evening 2026-09-10).** The user has an extra budget of €5,000. The configuration below was
assembled in Alternate's PC-Builder and sits **in the user's shopping cart, not ordered**: the user
will reconsider once the first steps of the plan show it is worth it (the naphthalene timing and P13,
the R0 licence). Cart as built: the system with assembly €4,319.80 + Eaton Ellipse PRO 1200 DIN UPS
€329 + shipping €6.95 = **€4,655.75**. Checks done: the memory kit KF556C40BBK2-128 is on the ASUS
QVL of the ProArt X870E-Creator for both Ryzen 7000 and 9000 (2 × 64 GB, DDR5-5600, EXPO, slots 1–2;
the single module KF556C40BB-64 is not listed — hence the kit); the board supports ECC and non-ECC
unbuffered DIMMs. Still to do at ordering time: re-check prices; fill the "special instructions"
field (latest BIOS, EXPO on for the 2 × 64 GB, verify 128 GB recognised); note that an assembled
system cannot be returned. This note keeps
the research so it is not redone. Prices are Alternate.nl on 2026-09-10 (in stock unless noted) and
will move; **DDR5 cost ≈ €16.5 per GB that day**, which is what shaped the design.

**What the measurements say the machine must fix** (Compute_Budget §3; probes): the laptop runs the
anchor on 8 threads under a 22 GB WSL ceiling; the canonical CCSD(T)/cc-pVTZ gradient of benzene did
not fit in 22 GB; one naphthalene LNO-CCSD(T)/cc-pVTZ energy takes **11.5 h at 19.8 GB peak memory (measured 2026-09-11)** and
writes 18 GB of scratch; the R1 deck is 474 such energies = 5,450 laptop-hours. The laptop is at its memory
ceiling at naphthalene already; pyrene does not fit it. Priorities: memory, then cores, then NVMe scratch, native
Linux (no WSL ceiling); a GPU is irrelevant for the anchor (pyscf-forge LNO is CPU-only — to verify).

## Configuration A (recommended): AM5, 16 cores, 128 GB now → 256 GB later

| part | product | price |
|---|---|---|
| CPU | AMD Ryzen 9 9950X, 16C/32T — https://www.alternate.nl/AMD/Ryzen-9-9950X-4-4-GHz-5-7-GHz-Turbo-Boost-socket-AM5-processor/html/product/100065780 | €499 |
| motherboard | ASUS ProArt X870E-Creator WiFi (4 × DDR5, max 256 GB, 4 × M.2: 2 Gen5 + 2 Gen4, 10 GbE + 2.5 GbE) — https://www.alternate.nl/ASUS/ProArt-X870E-CREATOR-WIFI-socket-AM5-moederbord/html/product/100076507 | €389 |
| memory | Kingston FURY Beast 128 GB kit (2 × 64 GB) DDR5-5600 CL40, KF556C40BBK2-128 — https://www.alternate.nl/Kingston-FURY/Beast-128-GB-DDR5-5600-2x-64-GB-werkgeheugen/html/product/100140713 (on the ASUS QVL; the single module KF556C40BB-64 at €1,059 is not) | €2,289 |
| system + results SSD | Samsung 990 PRO 2 TB — https://www.alternate.nl/Samsung/990-PRO-2-TB-SSD/html/product/1864243 | €347 |
| scratch SSD | Lexar NM790 2 TB — https://www.alternate.nl/Lexar/NM790-2-TB-SSD/html/product/1916729 | €259 |
| cooler | Noctua NH-D15 G2 — https://www.alternate.nl/Noctua/NH-D15-G2-CPU-koeler/html/product/100067139 | €149 |
| PSU | be quiet! Power Zone 2 modular 850 W, 80 PLUS Platinum, art. 100112864 (chosen over the Pure Power 13 M: Platinum, quieter at our ≈ 250 W load) | €119.90 |
| case | Fractal Design Define 7 — https://www.alternate.nl/Fractal-Design/Define-7-midi-tower-behuizing/html/product/1602114 | €169 |
| assembly | Alternate assembly service | €99 |
| UPS | Eaton Ellipse PRO 1200 DIN, 1200 VA / 750 W, USB, sine-wave output per Eaton (verify in the datasheet) — https://www.alternate.nl/Eaton-Power-Quality/Ellipse-PRO-1200-DIN-ups/html/product/1464124 | €329 |
| **total in cart** | incl. €6.95 shipping | **€4,655.75** |

With the remaining €344: nothing now. Later options in order: the scratch drive → Samsung 990 PRO
4 TB (+€440; product 100011336); a spare case fan. Do **not** buy a third memory module (three modules
degrade AM5 memory operation); save toward modules three and four together.

## Why not Threadripper today

9960X (24 cores) €1,499 (product 100145427); cheapest TRX50 board (Gigabyte TRX50 Aero D) €659;
128 GB of registered DDR5 not listed at Alternate and ≥ €2,300 at the day's prices; total > €5,300
before drives, and eight memory channels only pay with 4–8 modules. Right machine when memory
prices normalise.

## To verify before ordering

- ~~The ProArt board's memory QVL lists 64 GB modules~~ — **done 2026-09-10**: KF556C40BBK2-128 is on the
  QVL for Ryzen 7000 and 9000 (slots 1–2).
- ECC: the board supports ECC and non-ECC unbuffered DIMMs (ASUS tech specs); no ECC DDR5 UDIMM was
  listed at Alternate → a non-ECC build for now, ECC possible later.
- **Operating system decided 2026-09-10: Ubuntu 24.04 LTS (or newer LTS), headless, driven over SSH from
  the laptop** (Tailscale for access from elsewhere). Omarchy/Arch was weighed and set aside for the
  compute node: rolling updates would move kernel, glibc and BLAS under a pinned engine on a machine
  that runs unattended for weeks, and its desktop layer is unused headless. Day-one list: Ubuntu,
  the `qc05` venv with engine patch 1, SSH key from the laptop, Tailscale, NUT for the UPS, the repo
  clone, then the naphthalene timing as the first run (laptop vs desktop number).
- Whether pyscf-forge's LNO-CCSD(T) can use a GPU at all (expected: no); if the M05 DFT corpus or the
  M2 autodiff work needs one, it is a separate, later purchase.
- Expected gain, to be measured on day one with `probes/anchor_single_point_timing.py`: one
  naphthalene cc-pVTZ energy from the measured 11.5 h to an expected 3–5 h (16 cores at desktop clocks, no
  memory pressure); that number re-sizes the R1 deck — at 4 h the deck is 1,900 h ≈ 11 weeks of one machine.

## Alternatives weighed

Renting compute instead of buying: the R2/R3 rungs need ≈ 220 GB per canonical pyrene energy and are
cluster work whatever is bought; a €5,000 desktop covers R0–R1 and all preparatory DFT permanently.
The calendar already splits it that way (proposal §12; §13 item 5 asks the supervisor to sponsor the
cluster request).

**Dated note 2026-09-12 — the cart at the moment of deletion (the user empties the cart to order laptop
memory; the UPS moved to the Alternate wishlist, the PC configuration could not — it is a PC-Builder bundle,
art. no. 74807 "ALTERNATE Compleet pc-systeem", not an article).** Components and prices as shown on
zakelijk.alternate.nl on 12 September, checked against the table above: assembly €99.00; AMD Ryzen 9 9950X
€499.00; ASUS ProArt X870E-Creator WiFi €389.00; Noctua NH-D15 G2 €148.90; Kingston FURY Beast 128 GB
(2 × 64 GB) DDR5-5600 €2,289.00; Lexar NM790 2 TB €259.00; Fractal Design Define 7 €169.00; be quiet! Power
Zone 2 850 W €119.90; **Samsung 990 PRO 2 TB €354.00 (was €347 on 10 September, the only change)**. System
with assembly **€4,326.80** (10 September: €4,319.80); with the UPS (€329) and shipping (€6.95) it would be
€4,662.75. Everything needed to rebuild the configuration is in the table above (product numbers and
URLs); nothing is lost by deleting the cart line. The €5,000 decision itself is unchanged: parked until the
first results.

*Same day, laptop memory:* the Vivobook 18 M1807HA has two SO-DIMM slots, both holding 16 GB DDR5-5600
(Micron MTC8C1084S1SC56BD1 and Samsung M425R2GA3EB0-CWM, 1.1 V), firmware maximum 64 GB. Upgrade to 64 GB
= replace both by 2 × 32 GB DDR5-5600 SO-DIMM: at Alternate either the Kingston FURY Impact kit KF556S40IBK2-64
(CL40, €999) or two Corsair Vengeance CMSX32GX5M1A5600C48 (CL48, 2 × €439 = €878); no Corsair 2 × 32 kit
listed. **Ordered 2026-09-12 (afternoon): 2 × Corsair CMSX32GX5M1A5600C48, €878 + €6.95 shipping = €884.95; expected Tuesday 15 September.** Installation only when no job runs (not during the naphthalene xtight timing); afterwards the WSL ceiling goes to ≈ 50 GB by a dated Budget note and the parked 25 GB lever is superseded. Consequence for the Budget: the WSL ceiling can go to ≈ 50 GB, so a
naphthalene xtight energy fits without the memory levers and a pyrene energy probably fits too; speed is
unchanged.

**Correction, same day (2026-09-12, evening):** the two-slot reading above was wrong. ASUS's own spec page for the
Vivobook 18 (M1807) reads, for the M1807HA, "16GB DDR5 on board, 16GB DDR5 SO-DIMM, Max Total system memory up
to: 32GB" — **one SO-DIMM slot plus 16 GB soldered**. The SMBIOS table lists two "SODIMM" devices, but the
channel-A Micron device has serial 00000000 (the soldered memory, described by a module-style part number) and
only the channel-B Samsung module carries a real serial (the socketed one). The firmware's "64 GB maximum" is
the controller's array limit, not the board's. Consequences: at most one 32 GB module can be fitted, giving
16 + 32 = **48 GB, and only if the firmware accepts a 32 GB module in the slot** (ASUS states 32 GB total as the
maximum; the memory controller of the Ryzen 7 260 supports it, so the risk is a BIOS refusal, not a hardware
one). Of the two modules ordered, one is superfluous in every case. Options for the user: cancel one module
before shipping or return it within the return period; on arrival fit one 32 GB module and check that Windows
reports 48 GB; if the BIOS refuses, return both. The WSL ceiling with 48 GB: ≈ 36–38 GB — enough for the
naphthalene xtight energy, marginal for pyrene. The mistake was mine (reading "2 memory devices, SO-DIMM form
factor" as two slots without checking the manufacturer's sheet); the checking rule for hardware from now on:
the manufacturer's spec page before the firmware table.

**Order cancelled by the user the same evening (2026-09-12).** The laptop stays at 32 GB; the memory levers of the Budget's parked note (25 GB ceiling, max_memory, swap) remain the only way to fit larger jobs on it. A single 32 GB module for 48 GB remains a possible later step, subject to the firmware accepting it; not planned.
