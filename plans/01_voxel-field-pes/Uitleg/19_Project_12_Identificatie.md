# Hoofdstuk 19 — Project 12: herkenning in een echte sterrenkundige meting

> **In dit hoofdstuk leer je**
> – hoe een PAK in de ruimte eigenlijk infrarood licht uitzendt;
> – waarom 300 K de verkeerde temperatuur is, en welke temperatuur wel klopt;
> – wat pre-registratie betekent als je met echte waarnemingen werkt;
> – wat "willekeurig groot" na alle drie de horizonprojecten nog mag betekenen.

**Geen Udacity-module.** Post-master's.
**Hangt af van:** project 11 (bandfamilies met genoemde toleranties en een foutbudget).

---

## §19.1 Wat is de vraag?

> Kunnen de diagnostische infraroodbandfamilies van **met naam genoemde**
> PAK-groottes en ladingstoestanden, berekend met een goud-verankerd
> energielandschap en een GVPT2-achtige kernbewegingsmethode, worden gebruikt om
> de aanwezigheid van die soorten in een **bevroren** sterrenkundige dataset te
> **ondersteunen of te verwerpen** — met het foutbudget zichtbaar?

Dit is het project waarin de oorspronkelijke ambitie uit hoofdstuk 1 eindelijk
wordt aangeraakt. Let op hoe voorzichtig hij inmiddels is geformuleerd: geen
"wij identificeren de PAK's in het heelal", maar een **fail-closed
identificatie-experiment op een vooraf vastgelegde lijst kandidaten**.

## §19.2 Wat dit onderscheidt van project 08

| Project 08 (master) | Project 12 |
|---|---|
| JWST als inkadering: *waarom het later zou uitmaken* | Eén bevroren waarneming als **data** |
| Betrouwbaarheidsgecontroleerde enveloppen van kleine moleculen | Bandfamilies van grote PAK's uit project 11 |
| Simulatie bij 300 K met behoud van energie | Zie §19.3 — dat klopt hier niet |
| Mag geen capaciteit claimen die niet gebouwd is | Mag identificatie claimen, **maar alleen** binnen de vooraf vastgelegde lijst en toleranties |

## §19.3 Hoe een PAK in de ruimte licht uitzendt

Dit is de natuurkunde die het hele project op zijn kop zet.

In een laboratorium meet je absorptie: je schijnt infrarood licht door een monster
en kijkt wat er ontbreekt. In een interstellaire wolk gebeurt iets heel anders.

> **Stappenplan 19.1 — Het emissiemechanisme**
> 1. Een PAK-molecuul, dat zwevend in het bijna-vacuüm heel koud is, vangt **één
>    ultraviolet foton** op van een nabije jonge ster. Dat foton draagt ongeveer
>    5 tot 13 elektronvolt.
> 2. Die energie gaat binnen picoseconden over in **trillingsenergie**, verdeeld
>    over alle trillingen tegelijk. Het molecuul is nu, in zekere zin, gloeiend heet.
> 3. Het molecuul koelt af door achtereenvolgens infrarode fotonen uit te zenden —
>    een **cascade**, die seconden kan duren.
> 4. Daarna is het weer koud, tot het volgende ultraviolette foton langskomt.

> **Voorbeeld 19.1 — Waarom 300 K de verkeerde temperatuur is**
> Coroneen $\mathrm{C_{24}H_{12}}$ heeft 36 atomen. Stel het vangt een foton van
> 10 eV. Wat is de bijbehorende "temperatuur" direct na de opname?
>
> *Uitwerking.*
> Aantal trillingen: $3 \times 36 - 6 = 102$.
> De energie verdeelt zich daarover volgens $E \approx (3N-6)\,k_B T$:
> $$T \approx \frac{E}{(3N-6)k_B} = \frac{10 \times 1{,}602\times10^{-19}}{102 \times 1{,}381\times10^{-23}} \approx 1{,}1\times10^{3}\ \mathrm{K}.$$
>
> Ongeveer **1100 K**, niet 300 K. Bovendien is dat geen vaste temperatuur maar een
> waarde die tijdens de cascade daalt.

De gevolgen zijn goed zichtbaar in het spectrum. Bij zulke energieën zijn de
banden merkbaar **verbreed** en **naar het rood verschoven** ten opzichte van een
koude meting, doordat de anharmoniciteit (§2.8) bij grote uitwijkingen sterker
merkbaar wordt.

Daarom eist het plan dat er één omgevingsmodel wordt gekozen en gedocumenteerd:
een microcanonische temperatuur na een genoemde ultraviolette energie, of een
gepubliceerd cascademodel, of een beargumenteerde temperatuurverdeling die bij de
gekozen waarneming past. En het voegt eraan toe: **je lost dit niet op door langer
te simuleren.** Een langere simulatie bij 300 K blijft een simulatie bij de
verkeerde temperatuur.

## §19.4 Pre-registratie, opnieuw — maar nu strenger

Je kent het principe uit §11.5. Hier is het nog belangrijker, omdat de
waarneming al bestaat en de verleiding om te blijven zoeken tot iets past
navenant groter is.

> **Stappenplan 19.2 — Wat vóór het aanraken van de waarneming vastligt**
> 1. **De kandidatenlijst.** Welke moleculen en welke ladingstoestanden? Een
>    deelverzameling van wat project 11 heeft berekend.
> 2. **De bandfamilies.** Welke van de gebieden 3 μm, 6–9 μm en 11–12 μm worden
>    gebruikt? Met naam genoemd.
> 3. **De maat.** Een venster rond het bandcentrum, een $\chi^2$ op de relatieve
>    intensiteiten, of iets gelijkwaardigs.
> 4. **De beslisregel** — GESLAAGD, VERWORPEN of NIET GEÏDENTIFICEERD — inclusief
>    wat er gebeurt als **twee isomeren even goed passen**.
>
> De lijst wijzigen nadat de JWST-data is bekeken, geldt als een mislukking van het
> experiment.

Dat laatste punt over isomeren is niet theoretisch. Antraceen en fenantreen hebben
allebei drie ringen en dezelfde formule $\mathrm{C_{14}H_{10}}$; ze verschillen
alleen in de manier waarop de ringen aan elkaar zitten. Hun spectra lijken sterk
op elkaar. Zonder een vooraf vastgelegde regel voor zo'n geval kun je achteraf
altijd de isomeer kiezen die het beste uitkomt.

## §19.5 Eén waarneming, van tevoren gekozen

De waarneming is één bevroren, van een versienummer voorzien product:

- een genoemd JWST-spectrum met een genoemde meetopening, **of**
- een genoemde deelverzameling van PAHdb of laboratoriumdata, als de claim
  methodevalidatie is in plaats van een nieuwe astronomische ontdekking.

De regel erbij: *"Do not shop surveys until one matches."* Blijven zoeken tot er
een dataset is die past, is precies de fout die pre-registratie moet voorkomen.

## §19.6 Fail-closed identificatie

Dezelfde discipline als bij de agent uit hoofdstuk 14: noem de gemeten waarde
naast de vooraf vastgelegde drempel. De toegestane uitkomsten zijn:

| Uitkomst | Voorwaarde |
|---|---|
| **Ondersteund** | Alle beoordeelde banden binnen de tolerantie, en geen even goed passende alternatieve verklaring |
| **Verworpen** | De banden vallen buiten de tolerantie |
| **Niet geïdentificeerd / ontaard** | Twee of meer soorten passen even goed — beide worden gerapporteerd |

En het oordeel dat uitdrukkelijk **niet** telt:

> Een presentatieplaat met "in overeenstemming met PAK's", zonder een lijst van
> soorten, is een mislukking.

Die zin is streng maar terecht. "In overeenstemming met PAK's" is al decennia
bekend en zegt niets nieuws. De vraag is *welke* PAK's, en van welke grootte en
lading.

Er hoort ook een **negatieve controle** bij: minstens één soort die volgens de
methode móét falen — verkeerde lading of verkeerde grootte. Als je methode alles
goedkeurt wat je erin stopt, keurt hij niets werkelijk goed.

## §19.7 Wat "willekeurig groot" nog mag betekenen

Na alle drie de horizonprojecten is de verdedigbare zin deze:

> Een meeschalend energielandschap, goud-verankerd op kleine aromaten, plus
> GVPT2-achtige anharmoniciteit, voorspelt **de diagnostische infraroodbandfamilies**
> van PAK's **tot een gemeten grootte en ladingstoestand**, en die families kunnen
> worden gebruikt in een fail-closed identificatie tegen [genoemde dataset].

Het is nadrukkelijk **niet** dit:

> Eén model, elke $\mathrm{C}_n$, chemisch nauwkeurige rovibrationele lijnen en
> intensiteiten, alle PAK's in JWST geïdentificeerd.

En de definitie die het plan aan "willekeurig groot" geeft, is misschien wel de
mooiste zin van de hele repository:

> **"Any size" in practice means: transfer until the measured error exceeds the
> band tolerance, then stop or change theory.**

Oftewel: je gaat door tot je gemeten fout de tolerantie overschrijdt, en dan stop
je of verander je van theorie. "Willekeurig groot" is geen eigenschap van een
methode maar een **gemeten grens**.

## §19.8 Invoer en uitvoer

**Invoer:**

- De anharmonische bandfamilies met intensiteiten uit project 11;
- het foutbudget A–D uit project 11;
- één bevroren waarnemingsproduct;
- het pre-registratiedocument, gedateerd vóór de analyse.

**Uitvoer:**

| Product | Inhoud |
|---|---|
| Methodenotitie over excitatie en omgeving | Welk model, en waarom dat past bij deze waarneming |
| Pre-registratie + bronvermelding van de waarneming | Gedateerd |
| Identificatietabel | Soort × bandfamilie × maat × oordeel |
| Foutbudget | De vier termen van project 11, plus een vijfde voor de excitatie |
| Negatieve controle | De soort die moest falen, en of hij faalde |
| Beperkingenparagraaf | Elke soort die deze methode **niet** kan bereiken, met reden |

## §19.9 Verboden

Uit [`12_Astrophysical_PAH_Identification.md`](../GoalGathering/Horizon/12_Astrophysical_PAH_Identification.md):

- JWST-data als trainingsdata gebruiken;
- lijnlijstnauwkeurigheid claimen;
- "willekeurige grootte" claimen;
- doen alsof de inkaderingsparagraaf van project 08 dit werk al beschreef;
- dit een Udacity-module noemen.

Die eerste is de belangrijkste. Zou je het model op de waarneming trainen, dan
zou het leren de waarneming te reproduceren, en zou een match niets meer bewijzen.
Het energielandschap blijft energie-gedreven, van begin tot eind.

## In het kort

- **De muur:** een berekende bandfamilie confronteren met een echte sterrenkundige waarneming.
- Een PAK in de ruimte zendt uit ná het opnemen van één ultraviolet foton; de bijbehorende temperatuur is ruwweg 1100 K, niet 300 K, en daalt tijdens een cascade.
- Alles ligt vooraf vast: de kandidatenlijst, de bandfamilies, de maat, de beslisregel en de omgang met gelijkende isomeren.
- Eén bevroren waarneming; niet doorzoeken tot er iets past.
- Drie toegestane uitkomsten: ondersteund, verworpen, of niet geïdentificeerd — plus een verplichte negatieve controle.
- "Willekeurig groot" betekent: overdragen tot de **gemeten** fout de bandtolerantie overschrijdt, en dan stoppen of van theorie veranderen.
