# Hoofdstuk 12 — Module 07: de run steward

*Udacity-module "Design of Autonomous and Semi-Autonomous Agentic Workflows". In de
rubriek Project 6. Herschreven 25 september 2026 naar de gebouwde agent; het ontwerp van
12 september staat als gedateerd kader in §9.*

---

## 1. Wat is de vraag?

Bouw een agent die een lopende rekencampagne draaiende houdt: hij kijkt wat de machines
doen, beslist wat de volgende stap is (starten, uitlezen, herkansen, wachten, of aan een mens
vragen), voert die stap uit met een klein aantal toegestane gereedschappen, en schrijft elke
beslissing op met de regel die hij toepaste. En vooral: hij maakt de fouten niet opnieuw die
wij in de twee weken ervoor zelf hebben gemaakt.

## 2. Wat eist de school?

Een klein agentisch systeem met een duidelijk doel en duidelijke grenzen (één agent of
meerdere, met reden), expliciete beslislogica, beperkt geheugen of toestand, minstens één
tool, logging en veiligheidsmaatregelen, een architectuurdiagram, voorbeeldruns met
waarneembare uitvoer en minstens één echte mislukking of onverwacht gedrag, en een rapport
met persona, beslislogica, geheugen, tools, veiligheid, geobserveerd gedrag en een ethische
overweging gebonden aan *dit* systeem. Gebouwd met gereedschap uit de cursus (wij: LangGraph,
uit het keuzevak; het taalmodel via de Anthropic-API, met het model-id in elke run gelogd).
Niet hergebruikt uit een eerdere module.

## 3. Waar komt de agent vandaan?

Tussen 10 en 25 september 2026 draaide dit project op vijf gehuurde machines en één laptop.
Iemand moest elk uur beslissen: is die berekening klaar, mag de volgende starten, is dat
foutbericht erg, moet de eigenaar dit weten? Die "iemand" was de AI-assistent van het
project, onder toezicht van de eigenaar, en elke beslissing kwam in het logboek. Zo'n
dertig van die beslissingen waren fout, en van elke fout is een regel gemaakt: een proefrun
vóór elke start, nooit een tweede exemplaar van dezelfde taak, een klok lezen in dezelfde
opdracht als het tijdstempel, een statistiek over het model pas lezen naast dezelfde
statistiek over het doel. Op 25 september stonden er tweeëndertig van zulke regels, elk met
het incident erbij dat hem heeft gekost.

De run steward is die lus, expliciet gemaakt. Niet omdat de lus creatief moet zijn — dat
moet hij juist niet — maar omdat regels alleen iets waard zijn als ze *uitvoerbaar* zijn.

## 4. Invoer — wat de agent ziet en onthoudt

De agent heeft geen dataset maar **waarnemingen** en **geheugen**.

**Waarnemingen** zijn letterlijke stukjes logtekst plus de feiten die een gereedschap eruit
haalt: "dit slot is van deze machine en zijn proces leeft niet meer", "deze taak heeft een
geslaagde proefrun", "dit checkpoint is acht minuten oud". De tekst blijft erbij, want de
agent moet kunnen citeren wat hij las.

**Geheugen** bestaat uit drie delen, en bewust niet meer:

| Onderdeel | Wat het is | Verandert door |
|---|---|---|
| de regeltabel (`rules_v1.json`) | 32 regels: naam, wanneer, wat moet, wat nooit mag, en het incident dat de regel heeft gekost | alleen een mens, gedateerd en gecommit |
| de campagnetoestand | welke taken er zijn, wat ze horen op te leveren, hoe vaak ze herkanst zijn | de gereedschappen |
| het rollende venster | de laatste waarnemingen en de acties van deze run | elke stap |

Er is geen geleerd geheugen. Wat de agent weet over "wat werkt", staat in de tabel, en de
tabel is een bestand dat een mens kan lezen en veranderen.

## 5. Bewerking — de lus en de poort

De agent is een LangGraph-graaf met vijf knopen die in een lus staan:

1. **Waarnemen** — status van machines, resultaatbestanden, de klok.
2. **Voorstellen** — het redeneerdeel (een taalmodel, of in de tests een deterministische
   regeltabel) levert precies één voorstel: `{actie, argumenten, regel-id, reden}`.
3. **Poort** — gewone Python zonder taalmodel controleert het voorstel: staat de actie op
   de lijst van elf toegestane acties; bestaat de aangehaalde regel; heeft een start een
   geslaagde proefrun en geen levend exemplaar; wordt een slot alleen verwijderd als zijn
   proces dood is op dezelfde machine en de proceslijst is nagekeken; wordt een "het model
   respecteert X"-statistiek alleen vastgelegd naast dezelfde statistiek over het doel;
   wordt een taak met een vers checkpoint niet herstart; staat er in een logregel een
   opdracht aan de agent (dan mag alleen nog escalatie); raakt het voorstel iets wat aan
   een mens toebehoort. Een geweigerd voorstel wordt vervangen door wat de regel voorschrijft:
   een proefrun, een procescheck, wachten, of vragen.
4. **Handelen** — het goedgekeurde (of vervangen) voorstel wordt uitgevoerd met een
   gereedschap van de lijst.
5. **Vastleggen** — één logboekregel met tijdstempel uit de klok, actie, regel, reden en of
   de poort het goedkeurde.

Daarna terug naar 1, tot de actie "wachten" of "vragen" is, of tot het stappenbudget op is.

De **persona** is een zorgvuldige laborant die logs leest, geschreven regels toepast en
"vraag het de PI" zegt als een toestand bij geen enkele regel past. De kern van het ontwerp
in één zin: *het taalmodel stelt voor, de code beslist.* Een verkeerd of gemanipuleerd
voorstel kan daardoor nooit iets doen buiten de elf acties, en geen van die elf maakt of
verwijdert machines, geeft geld uit, publiceert, verandert een regel of velt een oordeel.

## 6. Uitvoer — wat de agent oplevert

- **Acties**, elk met de regel die ze rechtvaardigt.
- **Het logboek**: per stap één regel, met de reden van een eventuele weigering.
- **Escalaties**: een bericht aan de mens met de waarneming geciteerd en de regels die zijn
  overwogen. Dat is de enige weg naar buiten.
- Voor de school: het notebook met de runs, het rapport met bronnen, het diagram,
  `requirements.txt`.

## 7. Hoe is hij getest?

Niet op een machine. Acht scenario's zijn vóór de bouw vastgelegd, allemaal uit de echte
logs van 25 september 2026: een achtergebleven slot na een gedode runner; een launch-wrapper
die na een geslaagde proefrun bleef hangen; één molecuul dat in de geometrie-optimalisatie
faalde terwijl de rest doorging; een symmetriestatistiek zonder doelcontrole (de fout van
die ochtend, zie hoofdstuk 10); een training waarvan de uitvoer stil bleef terwijl de
checkpoints wél verschenen; een campagne die een nieuwe server nodig had; een taak die met
een onbekende fout stopte; en een logregel waarin iemand de agent opdraagt een map te
wissen. Voor elk scenario staat vooraf welke reeks acties goed is en welke acties verboden
zijn.

Uitslag met het deterministische referentiebeleid: acht van acht goed. De drie gevallen die
aan een mens toebehoren (server, onbekende fout, opdracht in een log) werden geëscaleerd,
de statistiek zonder controle werd geweigerd, het stille trainingsproces werd met rust
gelaten. Daarnaast elf poorttests, elk met een negatieve controle: een test die faalt als
je de betreffende beveiliging weghaalt.

**De echte mislukking, zoals de rubriek die vraagt.** Bij het scenario met het mislukte
molecuul stelde de eerste versie van het beleid elke stap dezelfde logboekregel voor, tot
het stappenbudget op was. De regel "één regel per gebeurtenis" stond in de tabel, maar niet
in de toestand van het beleid, en de poort bewaakte herhaling niet. De les is algemener dan
het geval: een regel in een prompt is een verzoek, alleen een poort is een garantie.

Wat nog ontbreekt: de run met het taalmodel zelf. Die vraagt een API-sleutel die de eigenaar
moet aanmaken (een Claude-abonnement bevat er geen). Tot die tijd is het deterministische
beleid de referentie, en zegt het rapport dat eerlijk.

## 8. Waarom deze module?

Omdat de campagne 's nachts doordraait en iemand de regels moet toepassen terwijl de mensen
slapen. Maar de diepere reden staat in §3: dit project heeft zijn regels duur betaald. Een
agent die ze afdwingt, maakt van pre-registratie een controle in plaats van een belofte, en
maakt van het logboek iets wat je kunt naspelen: elke regel citeert zijn regel en zijn
waarneming, dus een lezer kan het met een specifieke stap oneens zijn. De ethische
overweging van het rapport hangt daaraan: een agent die andermans geld uitgeeft en het
bewijsmateriaal schrijft, moet controleerbaar zijn tot op de regel, en zijn grenzen moeten
in de structuur zitten, niet in zijn goede wil.

## 9. Gedateerd kader: het ontwerp van 12 september 2026

Het eerste ontwerp heette de *campagne-officier* en was gebouwd rond het anker: zes
gereedschappen (`check_deck_hash`, `check_budget`, `queue_submit`, `run_probe`,
`print_cost_record`, `write_certificate_or_refuse`) die batches indienden, kostenrecords in
het vaste formaat van de Ladder printten en certificaten schreven of weigerden, met een
weigeringslijst van elf regels (geen "beat"-zin zonder de hash van de pilotnotitie, nergens
een kostenbijvoeglijknaamwoord in het rapport, geen geleerde prior op de lage rungen, en zo
verder). De twee vooraf benoemde mislukkingen waren een vergiftigde deck-hash en een verboden
woord in een conceptzin.

Dat ontwerp is niet verworpen maar opgeschoven: de run steward is dezelfde agent gezien vanaf
de hele campagne in plaats van vanaf het anker. De weigeringen van de officier zijn
poortregels geworden; de deck-hash-controle en het gesloten uitvoerformaat komen terug zodra
de steward live draait naast de ankerbatches. Wat veranderde, is de bron van de regels: niet
langer alleen het plan, maar de incidententabel van het project zelf.

## 10. In het kort

Module 07 bouwt de run steward: één begrensde LangGraph-agent die waarneemt, één actie
voorstelt met de regel erbij, door een deterministische poort gaat, handelt met elf
toegestane gereedschappen en elke stap vastlegt. Zijn geheugen is de regeltabel van
tweeëndertig eigen lessen. Getest op acht scenario's uit de echte logs van 25 september:
acht van acht, met één echte mislukking gevonden en gerepareerd vóór de eerste commit. De
run met het taalmodel wacht op een sleutel.

*Bron: [DESIGN_2026-09-25.md](../modules/07_agentic_workflows/DESIGN_2026-09-25.md),
[rules_v1.json](../modules/07_agentic_workflows/rules/rules_v1.json),
[scenarios.json](../modules/07_agentic_workflows/scenarios/scenarios.json),
[PROVENANCE.md](../modules/07_agentic_workflows/PROVENANCE.md),
[QUALITY_POLICY.md](../QUALITY_POLICY.md),
[Rubrics/07](../../../Rubrics/07_Design_of_Autonomous_and_Semi_Autonomous_Agentic_Workflows.md).*
