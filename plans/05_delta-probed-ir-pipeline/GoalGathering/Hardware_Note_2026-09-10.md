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
not fit in 22 GB; one naphthalene LNO-CCSD(T)/cc-pVTZ energy takes ≥ 4.4 h and writes 18 GB of
scratch; the R1 deck is 474 such energies. Priorities: memory, then cores, then NVMe scratch, native
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
- Ubuntu 24.04 LTS or newer for the 10 GbE / 2.5 GbE controllers.
- Whether pyscf-forge's LNO-CCSD(T) can use a GPU at all (expected: no); if the M05 DFT corpus or the
  M2 autodiff work needs one, it is a separate, later purchase.
- Expected gain, to be measured on day one with `probes/anchor_single_point_timing.py`: one
  naphthalene cc-pVTZ energy from ≥ 4.4 h to an expected 1–2 h; that number re-sizes the R1 deck.

## Alternatives weighed

Renting compute instead of buying: the R2/R3 rungs need ≈ 220 GB per canonical pyrene energy and are
cluster work whatever is bought; a €5,000 desktop covers R0–R1 and all preparatory DFT permanently.
The calendar already splits it that way (proposal §12; §13 item 5 asks the supervisor to sponsor the
cluster request).
