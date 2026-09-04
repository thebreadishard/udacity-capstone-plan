# Hoofdstuk 12 — Module 07: de campagne-officier

*Udacity-module "Design of Autonomous and Semi-Autonomous Agentic Workflows". In de
rubriek Project 6.*

---

## 1. Wat is de vraag?

Bouw een agent die de dagenlange rekencampagnes onbeheerd uitvoert én die de spelregels
van het plan afdwingt: hij dient batches in, print kostenrecords, schrijft certificaten, en
**weigert** alles wat niet door een poort is gekomen, met een gelogde reden.

## 2. Wat eist de school?

Een klein agentisch systeem met: een duidelijk doel en duidelijke grenzen (enkel- of
meer-agent, gemotiveerd); expliciete redeneer- of beslislogica; **beperkt geheugen of
toestand**; **minstens één tool**; logging en veiligheidsmaatregelen; een
architectuurdiagram; voorbeeldruns met waarneembare uitvoer en **minstens één
mislukking of onverwacht gedrag**; een rapport met persona, beslislogica, geheugen, tools,
veiligheid, geobserveerd gedrag en een ethische overweging gebonden aan *dit* systeem.
Gebouwd met de tools van de cursus. Geen dataset nodig. Niet hergebruikt uit een eerdere
module.

## 3. Invoer — de datastructuur in detail

De officier heeft geen dataset maar een **geheugen** (toestand) en **tools** met elk hun
invoer.

**Geheugen (beperkt, expliciet):**

| Onderdeel | Type | Bron |
|---|---|---|
| de bevroren Ladder | tekst / geparseerde regels | Ladder §1–§6 |
| de budgetregels | record: checkpoint 168 h, B3-voorwaarden, c_CPS | Compute_Budget §1–§2 |
| de pilotnotitie | O14, met haar commit-hash | na de voornotitieprobes |
| Q8-oordelen per familie | tabel: rung, familie, (a)/(b)/(c) geslaagd of niet | uit de Q8-probes |
| status van de twee licenties | record: geleerde prior verdiend op R2? R3?; fragmentlicentie (a)(b)(b′)(c) | uit de betreffende probes |
| Q6-uitslagen per mode en grootteklasse | tabel | uit de Q6-probes |

**Tools en hun invoer:**

| Tool | Invoer | Wat hij controleert vóór hij iets doet |
|---|---|---|
| `check_deck_hash` | deck (O3) | hash klopt met Q0 van de rung |
| `check_budget` | rung, mode, gemeten rekentijd per probe, K_cap, c_CPS | de classificatieregel `tijd × K_cap × c_CPS > 168 h → B3`; B3 alleen als de voorwaarden in het budgetbestand gehaald zijn |
| `queue_submit` | deck, machine | weigert bij verkeerde hash of onvoldaan budget |
| `run_probe` | probe-script, deck | draait en vangt de uitvoer |
| `print_cost_record` | recoveryresultaat (O6), antwoordrecords (O5) | print uitsluitend het vaste formaat van Ladder §1 en niets anders |
| `write_certificate_or_refuse` | alle bovenstaande toestand plus het conceptrapport | zie de weigeringslijst hieronder |

## 4. Bewerking — de beslislogica

De persona is een **conservatieve laboratoriumofficier**: liever een geweigerde claim dan
een ongedekte. Elke beslissing is een controle van een voorwaarde tegen het geheugen, en
elke weigering wordt gelogd met de regel waarnaar ze verwijst. De lijst van weigeringen
(elk een veiligheidsmaatregel in de zin van de rubriek):

- geen "beat"-zin zonder de hash van de pilotnotitie en de uitvoer van de P2-probe;
- geen "beslisbaar"-oordeel zonder u_band van module 03 voor die familie;
- geen batch op R1–R3 zonder mode E;
- geen "beat" uit een mode waarvan de Q6-ruislijn op die grootteklasse niet is gehaald;
- geen grootte-zin zonder Q8(c)-uitvoer in beide verhoudingen (R1→R2 en R2→R3), afgelezen
  bij de gemeenschappelijke drempel;
- **nergens een kostenbijvoeglijknaamwoord** ("schaalonafhankelijk", "O(1)", "verzadigt",
  "groeit niet", met of zonder "-klasse"): een tekstfilter over het conceptrapport is
  onderdeel van de tool;
- geen geleerde prior in een gescoord spectrum van R0–R3, en geen op R4–R6 zonder licentie
  verdiend op R2 én R3;
- geen bereikrung voordat R3 gescoord is;
- geen R6-taak anders dan in fragmenten, en geen voordat de vier delen van de
  fragmentlicentie zijn geslaagd ((b) geslaagd of via (b′) opgelost);
- geen lokale-CC-probe voordat probe M1 is geslaagd;
- geen lokale-CC-gradiënt in een verplaatste stand vóór de pilotnotitie.

## 5. Uitvoer — de datastructuur in detail

- **Kostenrecords** (O7), één per rung en per mode, in het vaste formaat.
- **Certificaten** (O13) of **weigeringen**: een weigering is een record `{wat werd
  gevraagd, welke regel blokkeerde, verwijzing naar Ladder-paragraaf, tijdstip}`.
- **Het logboek**: elke beslissing met voorwaarde, uitkomst en verwijzing.
- **Het architectuurdiagram**: persona → redeneerlus → geheugen → tools → log.
- **Geobserveerde mislukkingen voor het rapport**, vooraf benoemd: een vergiftigde
  deck-hash → weigering; een conceptzin met "size-independent" → weigering met de
  verwijzing naar Ladder §1.
- Notebook of script, `requirements.txt`, rapport.

## 6. Waarom deze module?

Vanaf R1 zijn de probe-batches meerdaagse onbeheerde wachtrijen, eerst op de laptop, later
op een cluster. Iemand moet ze indienen, bewaken en de uitkomsten in het vaste formaat
opschrijven. Maar de diepere reden is dat het plan uit tientallen "mag niet"-regels bestaat
die alleen iets waard zijn als ze *uitvoerbaar* zijn. De officier is de bestuurbaarheid van
het plan in code: pre-registratie wordt van een belofte een controle. Zonder module 07
stopt elke beloofde rung, want niemand mag een kostenrecord met de hand schrijven.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Eén agent, gemotiveerd.** De rubriek vraagt om een keuze enkel/meer-agent met reden. Eén
  officier volstaat: alle beslissingen zijn regelcontroles tegen één geheugen; twee agenten
  zouden alleen een tweede plek voor fouten geven. Controleer dat het rapport dit zegt.
- **Beperkt geheugen, echt beperkt.** Het geheugen is de lijst van §3 en niets meer: geen
  labdata (die zou anders via de agent de recovery kunnen bereiken).
- **Minstens één tool** is ruim gehaald; controleer dat elke tool echt iets *weigert*
  en niet alleen doorgeeft.
- **De mislukking moet echt gebeuren.** De rubriek eist een geobserveerd falen uit eigen
  runs. De twee vooraf benoemde gevallen (vergiftigde hash; verboden woord) moeten in het
  notebook als echte runs staan.
- **Ethiek gebonden aan dit systeem.** De voor de hand liggende: een agent die claims
  weigert, kan ook ten onrechte weigeren (een te strenge regel blokkeert een echt
  resultaat); en de autonomie van een agent die B3-rekentijd indient. Beide moeten met
  voorbeelden uit de eigen runs worden besproken, niet in het algemeen.
- **Mag vroeg beginnen.** De officier kan starten zodra de Ladder en één probe bestaan, en
  moet dan alles weigeren wat hij niet kan certificeren. Dat is een goede eerste testrun.

## 8. In het kort

Module 07 bouwt een conservatieve agent met een beperkt, expliciet geheugen (Ladder,
budget, pilotnotitie, poortuitslagen) en zes tools die batches indienen, kostenrecords in
het vaste formaat printen en certificaten schrijven of weigeren. Elke regel van het plan is
een gelogde weigering; het kostenbijvoeglijknaamwoord-filter en de hashcontrole zijn de
twee vooraf benoemde mislukkingsgevallen. Zonder deze module mag geen enkele rung een
resultaat opschrijven.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §3 (Module 07),
[Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md) §1
en §6, [Compute_Budget_2026-09-03.md](../GoalGathering/Compute_Budget_2026-09-03.md) §2,
[Rubrics/07](../../../Rubrics/07_Design_of_Autonomous_and_Semi_Autonomous_Agentic_Workflows.md).*
