# Hoofdstuk 15 — Het bijproject en de reviewgeschiedenis

> **In dit hoofdstuk leer je**
> – wat het mode-G-bijproject was, wat het heeft gemeten en waarom het niet is gebouwd;
> – hoe plan 05 is beoordeeld: vier rondes van twee lezingen, en wat elke ronde veranderde;
> – waarom de reviewlus is gesloten en de tekst bevroren, en hoe het plan sindsdien verandert;
> – wat er nog openstaat, in welke volgorde.

---

## §15.1 Het bijproject: mode G

Het bevroren plan rekende de dure correctie uit met losse energieën (mode E). Een
**gradiënt** (de kracht op alle atomen) levert per berekening 3N getallen in plaats van één,
waarbij N het aantal atomen is. Gradiënten (mode G) zouden het aantal dure berekeningen dus
sterk kunnen verlagen. Voor lokale CC(T) met bevroren ruimtes bestond toen geen
productieklare gradiënt. De gebruiker besliste (beslissing 5): mode E is de gegarandeerde
route, en de gradiënt wordt gebouwd in een **vooraf geregistreerd bijproject**, met eigen
mijlpalen, een eigen urenbudget en een hard stopcriterium. Dat stopcriterium is de les van
plan 01, dat aan een bodemloze put ten onder ging.

**Het gereedschap** was PySCFAD, een versie van het rekenpakket PySCF die met automatische
differentiatie werkt: een programma dat energieën uitrekent, levert er automatisch de
afgeleiden bij. Twee metingen zijn gedaan:

- **M2a, de prijs van een gradiënt.** Een gradiënt kostte 6,04 keer zoveel als één energie
  (LNO-CCSD(T), benzeen, basisset 6-31G, acht rekenkernen). Dat lag binnen de vooraf gestelde
  grens van 20. Met de grotere basisset cc-pVDZ paste de berekening niet in 32 GB geheugen.
- **M2b, de juiste grootheid.** De lokale-CC-module die PySCFAD meelevert, berekent niet de
  grootheid van het plan: op de drie probemodes van benzeen week ze 5,5 / 8,2 / 26,4 µE_h af,
  tegen een grens van 6.

Daarop besliste de gebruiker (beslissing 43) de gradiënt zelf te schrijven, in Python op
JAX. Die gradiënt is niet gebouwd: het project koos een andere route. De ankers zijn nu
gewone (niet-lokale) CCSD(T)-Hessianen, berekend uit analytische CCSD(T)-gradiënten in
pyscf, met een basissetcorrectie van MP2 naar cc-pVTZ (het ankerregister,
[ANCHORS.md](../modules/ANCHORS.md)). De les van die route staat in de werkregels van de
repository: een nieuwe bibliotheekaanroep noemt de test van de bibliotheek die dezelfde
aanroep doet. Zes dagen coupled-cluster-rekenwerk gebruikten een functie die verkeerd was
aangeroepen en er toch goed uitzag. Sinds beslissing 63 ligt nieuw coupled-cluster-werk
stil tot juli 2027.

## §15.2 Hoe het plan is beoordeeld

Elk plan in deze repository doorloopt hetzelfde proces: schrijven → **Pass A** (een koude
lezing door een verse lezer zonder geheugen en zonder web: zegt de tekst wat hij denkt te
zeggen?) → verbeteren → **Pass B** (een vijandige domeinlezer mét web: klopt de
wetenschap en de architectuur?) → verbeteren. Plan 05 kreeg vier rondes, genummerd 7 tot
en met 10 (de nummering loopt door over de plannen heen).

| Ronde | Pass A | Pass B | Wat er wezenlijk veranderde |
|---|---|---|---|
| 7 (3 sept) | 21 punten | voorwaardelijk, 13 | Δ₃/Δ₄ ingetrokken; noise line voor mode E; de eerste versie van de licenties |
| 8 (4 sept) | 11 + 9 | voorwaardelijk, 8 + 10 | één σ-schatter; ruisbewuste stopregel; absolute η₈; vierdelige fragmentlicentie; het bevroren-ruimte-object; u_band; mode E op elke rung; de canonieke haalbaarheidsprobe |
| 9 (4 sept) | 5 + 23 | voorwaardelijk, 6 + 6 | **±paren** (de lineaire term Δ₁·p domineerde het ruwe antwoord); **projectie in plaats van toewijzing** voor de bevroren ruimte; R1 per familie omdat naftaleen alleen heet leek te bestaan; σ met n − p en gepoold; 36 gradiënten per mijlpaal |
| 10 (4 sept) | 7 + 13 | voorwaardelijk, 4 + 13 | ruis per energie in de dry run; de referentie-offset c₀ **geïdentificeerd** uit een tweede amplitude (een gefitte constante was niet identificeerbaar); **Δ₁ dragend**: de eerste-orde-geometrieterm; **het PNNL-kamertemperatuurspectrum van naftaleen gevonden**, dus R1 weer verwacht onvoorwaardelijk |

Alle bevindingen zijn dezelfde dag in de tekst gesloten; de lijsten staan in de README van
het plan. Pass B van ronde 10 bevestigde dat alle twaalf sluitingen van ronde 9 standhielden.

Na de bevriezing zijn niet het plan maar de gebouwde onderdelen beoordeeld: een review van de
codekwaliteit, per module een rubriekchecklist (`RUBRIC_CHECKLIST_*.md` in elke modulemap),
en een review van modules 02–08 tegen hun rubrieken
([REVIEW_2026-10-17.md](../modules/REVIEW_2026-10-17.md)).

## §15.3 Waarom de lus is gesloten

Na ronde 10 vroeg de gebruiker om een analyse: convergeren de rondes, of herstellen we
vooral onze eigen fouten uit de vorige ronde? De uitkomst: de domeinreviewer vond per ronde
minder en lichtere punten (8 → 6 → 4 blokkerend), maar een groeiend deel van de koude
lezingen bestond uit *naden*: oude formuleringen die een patch over veertien bestanden
had laten staan. Twee van die zelf-veroorzaakte fouten waren wél ernstig (een stopregel
die de lege oplossing accepteerde; een constante die elke frequentie dezelfde kant op zou
schuiven), dus de rondes waren hun geld waard; maar de resterende risico's zaten niet meer
in de tekst maar in metingen. De reviewers zeiden dat zelf: geen enkele voorwaarde vereist
nog een meting vooraf, en hun "wat zou het beslissen"-lijsten bestaan uit probes.

Besluit: geen ronde 11. Wel een kleine mechanische **naadcontrole** van de laatste patch
(19 naden, alle gesloten). Daarna is de tekst **bevroren**: elk bindend document draagt de
regel "Frozen text as of 2026-09-04". De Ladder is de enige bindende plek per regel; andere
bestanden verwijzen ernaar.

Het plan verandert sindsdien via **genummerde beslissingen** in de README van het plan, elk
met de woorden van de gebruiker erbij; er zijn er nu 65. Zo verving de geleerde correctie
(het ΔH-netwerk) de oorspronkelijke probe-aanpak, en legde beslissing 63 het eindpunt van de
capstone vast.

## §15.4 Wat er openstaat, in volgorde

1. **Het bewijs compleet maken**, tot eind november 2026 (beslissing 63). Betaald rekenwerk
   stopt op 15 november 2026; daarna rekent alleen de laptop.
2. **De demonstratie van de pijplijn** op de afspraak met de begeleider van 25 november 2026
   (onder voorbehoud; beslissing 64).
3. **De schrijffase**, december 2026 – februari 2027: modules 08 en 09, het concept van paper
   D (het datapaper), de opzet van paper C, en versie 0 van de productrepository.
4. **Inleveren** van de modules tussen januari en juni 2027; maart – juni 2027 is buffer en
   overdracht. Na juni 2027 beslist de begeleider hoe nieuwe coupled-cluster-ankers worden
   gemaakt.
5. **Mapping Pass 6**, de aftekening van de mapping module voor module. De gebruiker heeft
   gevraagd ermee te wachten; hoofdstuk 16 is de checklist ervoor.

## In het kort

Het mode-G-bijproject heeft twee dingen gemeten: een gradiënt kost ongeveer zes energieën,
en de meegeleverde lokale-CC-module berekent niet de grootheid van het plan. De eigen
gradiënt is niet gebouwd; de ankers komen nu uit analytische CCSD(T)-gradiënten in pyscf. Plan 05
doorliep vier reviewrondes van twee lezingen; daarna is de tekst bevroren en verandert het
plan via genummerde beslissingen. Wat rest: het bewijs afmaken, de demonstratie, de
schrijffase en het inleveren.

*Bron: [Side_Project_2026-09-04_ModeG_Gradients.md](../GoalGathering/notes/Side_Project_2026-09-04_ModeG_Gradients.md),
[README.md](../README.md) (reviewrecord; beslissingen 43, 63 en 64),
[Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md](../GoalGathering/notes/Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md)
obstakel 7, [Seam_Check_2026-09-04_Round10B_patch.md](../GoalGathering/reviews/Seam_Check_2026-09-04_Round10B_patch.md),
[ANCHORS.md](../modules/ANCHORS.md), [REVIEW_2026-10-17.md](../modules/REVIEW_2026-10-17.md).*
