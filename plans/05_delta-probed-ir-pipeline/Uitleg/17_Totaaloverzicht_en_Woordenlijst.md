# Hoofdstuk 17 — Totaaloverzicht en woordenlijst

---

## §17.1 De hele keten in één tabel

| Stap | Wie | Erin | Eruit | Poort |
|---|---|---|---|---|
| Tegenstander bouwen | M02 | PAHdb v4.00 | atlas (O8) | — |
| Waarheid bouwen | M03 | PAHdb-exp., NIST, PNNL, documentatie | scorebord met u_band (O9); matrixtolerantie | toets vooraf vastgelegd |
| Goedkope tegenstander | M04 | koppeltabel (O10, eigen DOI) | gekalibreerde kolom; onzekerheidslaag | Q4-uitzondering, leave-molecule-out |
| Voornotitieprobes | probes | DFT, één CC-punt | dry run (c, K_cap, w), M1, haalbaarheid, run/no-run, σ | pilotnotitie pas daarna |
| Pilotnotitie | student | alles hierboven, geen Δ₂ | O14, gecommit | verzegelde fits gaan open |
| Deck | probes (+M06 vóór hash) | O2, prior, q_s | O3 met hash | onveranderlijk daarna |
| Probes | batchrunner via M07 | deck | antwoordrecords (O5) | hash-controle, budgetregel |
| Recovery | solver | O5, prior | Δ₂, ρ-curve, K, K_off, c₀, Δ₁ (O6) | stopregel, K_cap |
| Licenties | probes | O6, referenties | Q6 / Q7 / Q8-uitslagen | fail-closed zinnen |
| Spectrum | pijplijn | DFT + Δ₂ + geometrieterm, GVPT2 | bandposities per familie | resonantieregels |
| Score | M08 | spectrum, O8, O9, M04-kolom | beat / verloren / onbeslisbaar per familie | u_band, Δ = 0-nulrij |
| Record en certificaat | M07 | alles | O7, O13 of weigering | de weigeringslijst |
| Steunvoorspeller | M05 | Δ₂-corpus (O11) | geleerde prior; P3 | licentie verdiend op R2 én R3 |
| Patroonvoorsteller | M06 | antwoordcorpus (O12) | voorstellen vóór de hash | K_off-vergelijking |
| Fragmenten (R6) | pijplijn | fragmenten uit de DFT-geometrie | Δ₂ per fragment | licentie (a)(b)(b′)(c) |
| Mode G | bijproject | PySCFAD | gradiënten erbij op gelicentieerde rungs | M2–M5, stopcriterium |
| Paper en verdediging | M08, M09 | alles | paper; presentatie | geen kostenbijvoeglijknaamwoord |

## §17.2 Woordenlijst

**Anharmonisch** — afwijking van het ideale-veergedrag; verschuift banden meestal omlaag.
Plan 05 corrigeert dit niet met CC.

**Arm A / B / C** — drie manieren om de lokale-CC-energie bij een verplaatste stand te
berekenen: alles bevroren (A), bezette orbitalen overgebracht met verse virtuele ruimtes
(B), alles vers (C). Het probe-object is A; de referentie voor de ruislijn is B.

**Atlas** — de tabel van berekende PAHdb-banden (module 02); "lijn A" van de tegenstanders.

**Band, bandpositie** — piek in het infraroodspectrum en zijn frequentie in cm⁻¹.

**Basisset** — de verzameling functies waaruit orbitalen worden opgebouwd; cc-pVTZ op R0–R1.

**Beat** — het plan claimt "beat" voor een familie als de eigen bandposities aantoonbaar
dichter bij het lab liggen dan die van elke tegenstander, en alleen waar u_band dat kan
beslissen.

**Bereikrung** — R4–R6: geen labdata; een spectrum met foutbudget, geen winstclaim.

**Bevroren ruimte** — de orbitaalruimtes van de lokale CC-methode, één keer gekozen en
door projectie overgebracht naar elke verplaatste stand (hoofdstuk 3).

**Biaslijn** — Q6-test: bevroren Δ₂ tegen volledig-CCSD(T)-Δ₂ op benzeen, per mode binnen τ.

**c, c₀** — c is de stopconstante (ρ* = c·ρ_noise, uit de dry run); c₀ is de fout in de
gedeelde referentie-energie, bepaald uit de tweede amplitude en afgetrokken.

**Certificaat** — het uitvoerobject per molecuul: spectrum, foutbudget, beat-uitslagen,
kostenrecord, licenties, hashes — of een weigering.

**CMA** — Concordant Mode Approach, een bestaande methode; CMA-0 is het diagonale
enkelmode-blok van dit plan; CMA-2 selecteert enkele niet-diagonale elementen.

**Coupled cluster (CC), CCSD(T)** — de nauwkeurige, dure rekenmethode; de "gouden standaard".

**Deck** — de vooraf vastgelegde, gehashte lijst patronen van een rung met alle instellingen.

**Δ, Δ₁, Δ₂** — verschil CC − DFT: Δ₁ de kracht in de DFT-stand (gemeten, gebruikt voor de
eerste-orde-geometrieterm), Δ₂ de Hessiaancorrectie (het beloofde object).

**DFT** — dichtheidsfunctionaaltheorie, de goedkope methode (B3LYP als hoofdfunctionaal).

**Dry run** — generale repetitie van de hele machinerie met DFT tegen DFT (B3LYP tegen een
functionaal met veel exacte uitwisseling), met een ruiskolom per energie; levert c, K_cap,
n_min(G), w en de strafgewichten.

**Eerste-orde-geometrieterm** — Σ φ_iij·δq_j: de correctie omdat Δ₂ in de DFT-stand wordt
gemeten en niet in het eigen minimum van het gecorrigeerde landschap; toegepast en per band
geprint; geen atoom wordt verplaatst.

**Familie** — groep modes naar bewegingstype (C–H-strek, C–C-strek, C–H-buiging in/uit het
vlak); de eenheid van scoren en rapporteren.

**Fragmentlicentie** — de vier metingen (a)(b)(b′)(c) die fragmentgewijs opmeten op R6
toestaan; "in afwachting van (b′)" is een mogelijke toestand.

**Gepoolde σ** — σ² gemiddeld over de vier Q6-modes van één arm; de gepoolde waarde beslist.

**Hash** — vingerafdruk van data; maakt vooraf-vastleggen controleerbaar.

**Hessiaan** — matrix van tweede afgeleiden van de energie; bepaalt de harmonische
frequenties.

**Hot band** — verschuiving van een band door thermisch aangeslagen lage modes; de reden dat
de temperatuur van een labspectrum in u_band zit.

**K, K_off, K_cap, n_min(G)** — K het aantal CC-energieën (mode E; ±paar = 2) of gradiënten
(mode G) tot de stopregel; K_off = K − 2M; K_cap het plafond; n_min(G) het minimumaantal in
mode G.

**Kostenrecord** — de vaste regel per rung en mode met K, K_off, σ, c₀, ρ-getallen,
rekentijd, machine, script.

**Licentie (Q6/Q7/Q8; geleerde prior; fragment)** — een reeks metingen die iets toestaat;
nooit een aanname.

**Lokale CC (DLPNO, LNO)** — CC-varianten die verre elektronencorrelatie weglaten en
daardoor bijna lineair schalen.

**M** — aantal normale modes, 3N − 6.

**Matrixisolatie** — labspectrum van een molecuul ingevroren in argon bij ~10 K; verschoven
ten opzichte van gas; alleen bruikbaar achter de matrix–gas-poort.

**Mode E / mode G** — Δ₂ uit energieën (gegarandeerd) / uit gradiënten (bijproject, erbij).

**Normale mode** — bewegingspatroon waarbij alle atomen met één frequentie trillen.

**Onbeslisbaar door constructie** — een familie waarvan u_band groter is dan de beat-marge;
vooraf verklaard, geen winst en geen verlies.

**Patroon (p), ±paar** — een uitwijkingsvector van alle atomen; gaat altijd als paar +p en
−p de berekening in.

**Pilotnotitie** — het gedateerde document met alle bevroren getallen, gecommit vóór de
eerste lokale-CC-Δ₂.

**Pre-registratie** — vooraf vastleggen wat je meet en waartegen, controleerbaar door
hashes en datums.

**Prior (structureel / geleerd)** — de voorkennis die de recovery nodig heeft om uit weinig
metingen een dunne Δ₂ terug te vinden: een frequentieband met straf buiten de band, of het
door module 05 voorspelde patroon.

**Probe** — één dure meting (een ±paar met CC en DFT); ook: elk vooraf omschreven script in
`probes/` dat een getal print.

**Q6, Q7, Q8** — de ankerlicentie (ruis, bias, drempel), de probinglicentie (recovery tegen
volledige referentie op R0–R1), en lokaliteit/verzadiging (directe koppelingen, K_off-groei).

**R_s, R_a** — de symmetrische combinatie ½[ΔE(+p) + ΔE(−p)] − ΔE(0) (het antwoord; bevat
Δ₂) en de antisymmetrische ½[ΔE(+p) − ΔE(−p)] (bevat Δ₁).

**Recovery** — het terugrekenen van Δ₂ uit de antwoorden met een prior.

**ρ, ρ_noise, ρ\*, ρ_max, ρ\*_common** — achtergehouden fout; ruisvloer; stopdrempel
c·ρ_noise; de vloer 0,5 waarboven "op ruisniveau"; de gemeenschappelijke drempel waarbij
Q8(c) twee rungs vergelijkt.

**Rung** — trede van de ladder R0–R6.

**Ruislijn** — Q6-test: σ_E ≤ 0,82·τ·q_s² (mode E), σ_g ≤ 2,8·τ·q_s (mode G).

**Scorebord** — de tabel van gemeten banden met u_band (module 03).

**σ_E, σ_g** — per-punt-ruis van de energie- of gradiëntverschillen, √(SSR/(n − p)),
gepoold per arm.

**Steun (support)** — welke elementen van Δ₂ groot zijn; het doel van module 05.

**τ, τ₇, η₈, ε₈, γ, d₇, r_c, r_f, h** — de bevroren drempels: kleinste beat-marge;
Q7-tolerantie; koppelingsafwijking; verre-aandeel; verzadigingsfactor;
onderscheidbaarheidsfactor; gemeten lokaliteitslengte; kleinste slagende fragmentstraal;
Cartesische probestap.

**u_band, u_T, u_296, χ_max** — gemeten bandonzekerheid van een labband; haar
temperatuurterm; het 0 → 296 K-aandeel per molecuul; de herinnerde maximale
hot-band-helling (0,03 cm⁻¹/K).

**Verzegeld bestand** — de fitcoëfficiënten van de gladheidsprobe en de ruwe M1-energieën;
gaan pas open met de commit-hash van de pilotnotitie.

## §17.3 Waar je verder leest

- Het bindende geheel: de [README](../README.md) van plan 05 en de reeks documenten in
  `GoalGathering/`, te beginnen met de woordenlijst van de
  [Overarching_Goal](../GoalGathering/Overarching_Goal.md).
- De regels: de [Ladder](../GoalGathering/Frozen_Ladder_and_Tolerances.md).
- De modules: de [Capstone_Mapping](../GoalGathering/Capstone_Mapping.md) en de
  rubrieken in `Rubrics/`.
- De probes in hun volgorde: [probes/README.md](../probes/README.md).
- Het waarom voor de begeleider: het [Project_Proposal](../GoalGathering/Project_Proposal_2026-09-03.md).

*Einde van de uitleg. Geschreven op 4 september 2026 bij de bevroren tekst van plan 05.*
