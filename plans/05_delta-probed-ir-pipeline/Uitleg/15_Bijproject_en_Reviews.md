# Hoofdstuk 15 — Het bijproject en de reviewgeschiedenis

> **In dit hoofdstuk leer je**
> – wat het mode-G-bijproject is, wat het belooft en wanneer het stopt;
> – hoe plan 05 is beoordeeld: vier rondes van twee lezingen, en wat elke ronde veranderde;
> – waarom de reviewlus op 4 september 2026 is gesloten en de tekst bevroren;
> – welke schulden er nog openstaan en in welke volgorde ze worden betaald.

---

## §15.1 Het bijproject: mode G

Hoofdstuk 5 legde uit dat een **gradiënt** (de kracht op alle atomen) per berekening 3N
getallen oplevert in plaats van één, en dat mode G daardoor het aantal probes K sterk zou
kunnen verlagen. Het probleem: voor lokale CC(T) met bevroren ruimtes bestond op 3
september 2026 geen productieklare gradiënt. De gebruiker besliste (beslissing 5, deel 2):
mode E is de *gegarandeerde* route, maar geen plafond; de gradiënt wordt gebouwd in een
**vooraf geregistreerd bijproject**.

**Het gereedschap.** PySCFAD, een versie van het PySCF-pakket die met automatische
differentiatie (AD) werkt: een programma dat energieën uitrekent, kan er automatisch de
afgeleiden bij leveren. In de openbare code staat een lokale-CC-module met een
(T)-bestand; of de (T)-term daarin van begin tot eind differentieerbaar is, is het eerste
dat het bijproject print.

**De mijlpalen**, elk met een geprinte slaagvoorwaarde:

| Mijlpaal | Molecuul | Wat er moet blijken |
|---|---|---|
| M1 (hoofdproject, niet het bijproject) | benzeen | bevroren ruimtes kunnen worden opgeslagen, overgebracht en herladen; de energie is glad langs drie modes |
| M2 | benzeen | de AD-gradiënt klopt met eindige verschillen van dezelfde bevroren energie (72 herprojecteerde energieën); σ_g onder de mode-G-ruislijn; de "projectieterm" geprint |
| M3 | naftaleen | hetzelfde, plus rekentijd en geheugen ≤ 28 GB, 36 gradiënten |
| M4 | pyreen | run/no-run, correctheid en σ_g; geclassificeerd als laptop of cluster |
| M5 | coroneen | run/no-run én beide controles |

Waar een mijlpaal slaagt, mag mode G op de bijbehorende rung **erbij** draaien. Het
bijproject heeft een eigen urenbudget, een kalender-checkpoint van twaalf weken na de
pilotnotitie en een **stopcriterium**: is M3 dan niet gehaald, of faalt de
correctheidscontrole van M2 na één herafleiding, dan stopt het per gedateerde notitie en
draait mode E ongestoord door. Dat is de les van plan 01, dat aan een bodemloze put ten
onder ging. Verwachting, opgeschreven: M4 en M5 zijn clusterwerk, dus de mode-G-grootte-zin
is voorwaardelijk aan het cluster.

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

## §15.3 Waarom de lus is gesloten

Op 4 september vroeg de gebruiker om een analyse: convergeren de rondes, of herstellen we
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
regel "Frozen text as of 2026-09-04" — wijzigingen alleen via een gedateerde notitie die
de bevinding of meting noemt, de Ladder is de enige bindende plek per regel, andere
bestanden verwijzen ernaar.

## §15.4 Wat er openstaat, in volgorde

1. **Mapping Pass 6**: de aftekening module voor module (hoofdstuk 16 bereidt die voor). De
   gebruiker heeft gevraagd ermee te wachten.
2. **De eerste literatuurschulden**: items 52–53 (hot-band-hellingen per familie), 56–57 en
   59 (de meetcondities van de benzeen- en naftaleenbronnen), 60 — lezen vóórdat module 03
   u_band print.
3. **Probe M1**: kan de gekozen code ruimtes bevriezen? Zo nee: stop 1.
4. **De voornotitieprobes**: de dry run met ruiskolom, de canonieke haalbaarheidsprobe, de
   gradiënt-run/no-run, de R0-pilot, de gladheidsprobe (72 energieën).
5. **De pilotnotitie**, en pas daarna de eerste echte probe.

## In het kort

Het bijproject bouwt de gradiëntroute (mode G) met vijf mijlpalen, een eigen budget en
een hard stopcriterium; slaagt het, dan draait mode G naast mode E. Plan 05 doorliep vier
reviewrondes van twee lezingen; de laatste twee veranderden het ontwerp op drie wezenlijke
punten (±paren, projectie, de Δ₁-term) en vonden een betere labbron voor naftaleen. Op 4
september 2026 is de lus gesloten en de tekst bevroren; wat rest zijn metingen, in een
vaste volgorde.

*Bron: [Side_Project_2026-09-04_ModeG_Gradients.md](../GoalGathering/Side_Project_2026-09-04_ModeG_Gradients.md),
[README.md](../README.md) (reviewrecord en "Not yet done"),
[Seam_Check_2026-09-04_Round10B_patch.md](../GoalGathering/Seam_Check_2026-09-04_Round10B_patch.md).*
