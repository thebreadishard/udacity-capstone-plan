# Hoofdstuk 12 — Module 07: de run steward

*Udacity-module "Design of Autonomous and Semi-Autonomous Agentic Workflows". In de
rubriek Project 6.*

---

## 1. Wat is de vraag?

De berekeningen van dit project draaien dagenlang op gehuurde machines en een laptop, en 's
nachts gaat er van alles mis: een taak sterft, een slotbestand blokkeert de volgende taak,
een log valt stil terwijl het werk doorgaat. Bouw een agent die zo'n rekencampagne bewaakt:
hij kijkt wat de machines doen, kiest de volgende stap (uitlezen, starten, herkansen,
wachten of een mens vragen), voert die uit met een kleine lijst toegestane acties, en
schrijft elke beslissing op met de regel die hij toepaste. Vooral moet hij de fouten niet
herhalen die het project zelf heeft gemaakt.

Het eerste ontwerp van deze module heette de *campagne-officier* (vandaar de bestandsnaam
van dit hoofdstuk). De weigeringen van dat ontwerp zijn poortregels van de run steward
geworden.

## 2. Wat eist de school?

Een klein agentisch systeem met een duidelijk doel en duidelijke grenzen (één agent of
meerdere, met reden), expliciete beslislogica, beperkt geheugen of toestand, minstens één
tool, logging en veiligheidsmaatregelen, een architectuurdiagram, voorbeeldruns met
waarneembare uitvoer en minstens één echte mislukking of onverwacht gedrag, en een rapport
met persona, beslislogica, geheugen, tools, veiligheid, geobserveerd gedrag en een ethische
overweging die over *dit* systeem gaat. Het systeem gebruikt gereedschap uit de cursus en is
niet hergebruikt uit een eerdere module. Hier: LangGraph (uit het keuzevak over LangChain en
LangGraph), met een taalmodel via een API waarvan het model-id in elke run wordt gelogd.

## 3. Invoer — wat de agent ziet en onthoudt

De agent heeft geen dataset maar **waarnemingen** en **geheugen**.

**Waarnemingen** zijn letterlijke stukken logtekst plus de feiten die een gereedschap
eruit haalt: "dit slot hoort bij deze machine en zijn proces leeft niet meer", "deze taak
heeft een geslaagde proefrun", "dit checkpoint is acht minuten oud". De tekst blijft
erbij, zodat de agent kan citeren wat hij las.

**Geheugen** bestaat uit drie delen, bewust niet meer:

| Onderdeel | Wat het is | Verandert door |
|---|---|---|
| de regeltabel (`rules_v2.json`) | 41 regels: naam, wanneer, wat moet, wat nooit mag, en het incident waaruit de regel kwam | alleen een mens, gecommit |
| de campagnetoestand | welke taken er zijn, wat ze horen op te leveren, hoe vaak ze herkanst zijn | de gereedschappen |
| het rollende venster | de laatste waarnemingen en de acties van deze run | elke stap |

**Waar de regels vandaan komen.** Toen het project op vijf gehuurde machines en een laptop
draaide, nam de AI-assistent van het project elk uur zulke beslissingen, onder toezicht
van de eigenaar. Van elke foute beslissing is een regel gemaakt. Regels 1–32 komen uit de
eerste twee weken: een proefrun vóór elke start, nooit een tweede exemplaar van dezelfde
taak, de klok lezen in dezelfde opdracht als het tijdstempel. Regels 33–41 komen uit de
week daarna, onder meer: een nieuwe aanroep van een softwarebibliotheek noemt de test van
die bibliotheek die dezelfde aanroep doet (na het lambda-incident: zes dagen
coupled-cluster-rekenwerk met een functie die verkeerd was aangeroepen en er toch goed
uitzag); "gevalideerd"
staat er alleen met het getal en waartegen; instellingen die van de elementen afhangen
worden per molecuul afgeleid; een gehuurde server wordt pas verwijderd als alle resultaten
binnen zijn; een controle die een fout ziet, stopt de taak in plaats van te waarschuwen.

Er is geen geleerd geheugen. Wat de agent weet over "wat werkt", staat in de tabel, en die
tabel is een bestand dat een mens kan lezen en veranderen.

## 4. Bewerking — de lus en de poort

De agent is een LangGraph-graaf met vijf knopen in een lus:

1. **Waarnemen** — de status van machines, resultaatbestanden, de klok.
2. **Voorstellen** — het redeneerdeel (een taalmodel, of het deterministische beleid dat de
   regeltabel letterlijk toepast) levert precies één voorstel:
   `{actie, argumenten, regel-id, reden}`.
3. **Poort** — gewone Python zonder taalmodel controleert het voorstel. Staat de actie op de
   lijst van elf? Bestaat de aangehaalde regel? Heeft een start een geslaagde proefrun en
   geen levend exemplaar? Wordt een slot alleen verwijderd als zijn proces dood is op
   dezelfde machine? Wordt een statistiek over het model alleen vastgelegd naast dezelfde
   statistiek over het doel? Staat er in een logregel een opdracht aan de agent? Dan mag
   alleen nog escalatie. 29 van de 41 regels dwingt de poort zelf af. Een geweigerd voorstel
   wordt vervangen door wat de regel voorschrijft: een proefrun, een procescheck, wachten of
   vragen.
4. **Handelen** — het goedgekeurde of vervangen voorstel wordt uitgevoerd.
5. **Vastleggen** — één logboekregel met tijdstempel, actie, regel, reden en het oordeel van
   de poort.

Daarna terug naar 1, tot de actie "wachten" of "vragen" is of het stappenbudget op is.

De elf acties: status lezen, een resultaatbestand lezen, processen controleren, een
achtergebleven slot verwijderen, een proefrun, starten, mislukte rijen opnieuw in de rij
zetten, een meting vastleggen, een logboekregel schrijven, wachten, en een mens
waarschuwen. Geen van die elf maakt of verwijdert machines, geeft geld uit, publiceert,
verandert een regel of velt een wetenschappelijk oordeel.

De **persona** is een zorgvuldige laborant die logs leest, geschreven regels toepast en
"vraag het de onderzoeksleider" zegt als een toestand bij geen enkele regel past. De kern
van het ontwerp: *het taalmodel stelt voor, de code beslist.*

**Hoe hij is getest.** Niet op een echte machine: de agent speelt opgenomen logs na. Er zijn
17 scenario's, elk met vooraf vastgelegd welke reeks acties goed is en welke verboden is.
S1–S8 komen uit de echte logs van één dag, bijvoorbeeld een achtergebleven slot na een
gedode taak, een training waarvan de uitvoer stil bleef terwijl de checkpoints wél
verschenen, en een logregel waarin iemand de agent opdraagt een map te wissen. S9–S17
toetsen de regels 33–41; ze zijn vastgelegd vóórdat het beleid ervoor werd geschreven.

## 5. Uitvoer — wat de agent oplevert

- **Acties**, elk met de regel die ze rechtvaardigt, en **het logboek**: per stap één regel,
  met de reden van een eventuele weigering.
- **Escalaties**: een bericht aan de mens met de waarneming geciteerd en de overwogen
  regels. Dat is de enige weg naar buiten.
- **De uitslag** met het deterministische beleid: 17 van de 17 scenario's goed, met 13
  escalaties. Onder de oude regeltabel (regels 1–32) haalde het beleid 0 van de 9 nieuwe
  scenario's. Daarnaast 29 tests van de poort, elk met een negatieve controle: een test die
  faalt als je de betreffende beveiliging weghaalt.
- Voor de school: het notebook `agentic_system.ipynb`, het rapport
  `Agentic_AI_System_Design_Report.pdf`, het architectuurdiagram en `requirements.txt`.

Module 08 gebruikt de poort: de verzoekbehandelaar van module 08 schrijft een opdracht tot
rekenen als een voorstel in het schema van de steward, en dat voorstel gaat door dezelfde
poort.

**De echte mislukking, zoals de rubriek die vraagt.** In het scenario met één mislukt
molecuul stelde de eerste versie van het beleid elke stap dezelfde logboekregel voor, tot het
stappenbudget op was. De regel "één regel per gebeurtenis" stond in de tabel, maar niet in
de toestand van het beleid, en de poort bewaakte herhaling niet. Dezelfde fout dook later
op een tweede plek op, bij het uitlezen van resultaten. De les: een regel in een prompt is
een verzoek, alleen een poort is een garantie.

## 6. Waarom deze module?

Een campagne draait 's nachts door, en iemand moet de regels toepassen terwijl de mensen
slapen. De diepere reden: dit project heeft zijn regels duur betaald. Een agent die ze
afdwingt, maakt van een regel een controle in plaats van een belofte. Het logboek is na te
spelen: elke regel citeert zijn regel en zijn waarneming, dus een lezer kan het met één
specifieke stap oneens zijn. De ethische overweging van het rapport hangt daaraan: een agent
die andermans geld uitgeeft en het bewijsmateriaal schrijft, moet tot op de regel
controleerbaar zijn, en zijn grenzen moeten in de structuur zitten, niet in zijn goede wil.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De run met het taalmodel ontbreekt nog.** De rubriek eist die niet strikt, maar het
  rapport belooft hem. De gebruiker besliste hem later te draaien met de API-sleutel van de
  cursus (Vocareum), 51 aanroepen. Tot dan is het deterministische beleid de referentie, en
  zegt het rapport dat.
- **Broosheid.** Het deterministische beleid kent alleen de vormen van toestand die de
  regels beschrijven. Een nieuwe soort fout leidt tot escalatie, niet tot een oplossing; dat
  is de bedoeling, maar het rapport moet het zeggen.
- **Nooit live.** De agent is alleen op nagespeelde logs beoordeeld en raakt geen machine
  aan. Als hij ooit live gaat, leest eerst een tweede lezer de poort.
- **Rapportsecties.** Het rapport volgt de zeven secties van Task 6 van de rubriek.
- **Bij het inleveren.** De repository `udacity-agentic-workflows` en een vers
  `requirements.txt` met `pip freeze` in de omgeving met LangGraph.

## 8. In het kort

Module 07 bouwt de run steward: één begrensde LangGraph-agent die waarneemt, één actie
voorstelt met de regel erbij, door een deterministische poort gaat, handelt met elf
toegestane acties en elke stap vastlegt. Zijn geheugen is een tabel van 41 regels uit de
eigen fouten van het project. Op 17 nagespeelde scenario's haalt het deterministische
beleid 17 van de 17; de run met het taalmodel wacht op de sleutel van de cursus.

*Bron: [README.md](../modules/07_agentic_workflows/README.md),
[RUBRIC_CHECKLIST_2026-09-25.md](../modules/07_agentic_workflows/RUBRIC_CHECKLIST_2026-09-25.md),
[DESIGN_2026-09-25.md](../modules/07_agentic_workflows/DESIGN_2026-09-25.md),
[rules_v2.json](../modules/07_agentic_workflows/rules/rules_v2.json),
[scenarios.json](../modules/07_agentic_workflows/scenarios/scenarios.json),
`notebook/results.json` en `steward/schema.py` van module 07,
[REVIEW_2026-10-17.md](../modules/REVIEW_2026-10-17.md),
[Rubrics/07](../../../Rubrics/07_Design_of_Autonomous_and_Semi_Autonomous_Agentic_Workflows.md).*
