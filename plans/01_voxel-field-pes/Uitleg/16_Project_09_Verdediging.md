# Hoofdstuk 16 — Project 09: de mondelinge verdediging

> **In dit hoofdstuk leer je**
> – hoe een academische verdediging is opgebouwd;
> – waarom dit het gevaarlijkste moment van de hele opleiding is;
> – welke twee vragen vrijwel zeker gesteld worden, en wat het antwoord is;
> – wat een "afgevuurde ladder-trede" is en waarom je die zelf moet noemen.

**Positie in de keten:** het laatste onderdeel van de master.
**Eigenaar volgens het plan:** degene die project 08 schrijft.

---

## §16.1 Wat is de vraag?

De schoolopdracht: een presentatie van 15 minuten over het systeem uit project 08,
gevolgd door 15 minuten vragen van de mentor.

De vraag eronder is anders van aard dan alle voorgaande. Het gaat niet meer om
een berekening maar om iets menselijks:

> **Kun je je eigen werk eerlijk verdedigen, inclusief alles wat niet gelukt is?**

## §16.2 Invoer

| Wat | Vorm |
|---|---|
| Het systeem uit project 08 | Het geïntegreerde artefact |
| De reflectiepaper | 1500–2000 woorden |
| Alle toetsrapporten | Per fase: drempel, gemeten waarde, oordeel |
| Het overzicht van gebruikte terugvalopties | Zie §16.5 |

## §16.3 De opbouw van de presentatie

De opdracht schrijft zeven onderdelen voor:

| # | Onderdeel | Wat er in dit project komt te staan |
|---|---|---|
| 1 | Context en probleemstelling | Sterrenkundige moleculen; de $N^7$-muur (§1.4) |
| 2 | Overzicht van het systeem | De pijplijn van §6.6 |
| 3 | Integratie van eerdere projecten | Hoe 04, 05, 06 en 07 samenkomen |
| 4 | Technische keuzes en afwegingen | Route B, de referentiesplitsing, roosterkeuze |
| 5 | Ethiek en verantwoorde AI | De fail-closed agent; het risico van vervuilde leerstof |
| 6 | Evaluatie, beperkingen en risico's | De drie foutbronnen; wat níét is aangetoond |
| 7 | Beroepsmatige relevantie | Waar deze werkwijze verder toepasbaar is |

Onderdeel 6 verdient bijzondere aandacht. Het plan eist dat drie soorten fouten
**apart** worden gerapporteerd en nooit tot één "nauwkeurigheidsgetal" worden
samengevoegd:

| Foutbron | Wat het is | Hoe gemeten |
|---|---|---|
| **A — modelfout** | Het geleerde model tegen CCSD(T) | De toetsrapporten van fase 1 |
| **B — elektronenstructuurfout** | CCSD(T)/cc-pVTZ tegen de CBS-referentie | De audit uit Stappenplan 3.1 |
| **C — kernbewegingsfout** | Klassieke simulatie tegen de echte kwantumtrilling | Alleen te schatten, en dat wordt erkend |

De verleiding is groot om te zeggen "wij zitten binnen 12 cm⁻¹". Dat is precies
wat niet mag: één getal verhult welke van de drie bronnen de fout veroorzaakt, en
verhult daarmee wat er verbeterd zou moeten worden.

## §16.4 De twee vragen die komen

Het plan bereidt twee vragen voor. Beide zijn zogeheten *free kills*: vragen
waarop een onvoorbereid antwoord het hele verhaal onderuithaalt.

### Vraag 1 — "Is dit niet gewoon orbital-free DFT?"

**Waarom die komt.** Omdat het antwoord ja is. De formule
$E = E_{\text{es}}[\rho] + \int\varepsilon_\theta\,\mathrm dV$ met een voorspelde
$\rho$ is per definitie een orbital-free dichtheidsfunctionaaltheorie, en dat
vakgebied bestaat al vijftien jaar (§12.5).

**Het voorbereide antwoord.** Beaam het onmiddellijk en noem het naaste voorwerk
zelf: Brockherde en anderen, 2017. Leg dan uit wat er wél overblijft: de
combinatie van CCSD(T)-data, conservatieve krachten via autograd, emergente
banden bij bevroren gewichten, en een vooraf geregistreerde vergelijking met een
graafnetwerk.

**Wat je niet moet doen.** De oude leus "dit is geen DFT" herhalen. Het plan is
daar expliciet over: laat die zin niet bij een examinator terechtkomen. Wat
verboden is, zijn kant-en-klare functionalen en data van DFT-kwaliteit; de vórm
$E = \mathcal E[\rho]$ is juist het onderwerp (§3.7).

### Vraag 2 — "Waarom telt een natuurkundesimulator als een CNN?"

**Waarom die komt.** Omdat het eruitziet alsof de opdracht wordt ontweken.

**Het voorbereide antwoord.** De NCA-laag is een convolutie met een venster van
$3\times3\times3$ die overal dezelfde geleerde bewerking toepast — wiskundig
precies wat een driedimensionaal CNN doet. Dat het rooster een elektronenwolk
bevat in plaats van beeldpunten, verandert daar niets aan (§12.4).

## §16.5 De ladders die zijn afgevuurd

Dit is het onderdeel dat het plan het scherpst formuleert:

> *"which ladder rungs fired — because a rung that fired and went unmentioned is
> the fastest way to lose a defense."*

Er zijn drie terugvalladders in het plan, en elke gebruikte trede moet uit
zichzelf worden genoemd:

| Ladder | Waar | Wat een gebruikte trede betekent |
|---|---|---|
| Escalatieladder voor $\varepsilon_\theta$ (§12.6) | Is de plaatselijke functionaal vervangen door een niet-plaatselijke? | Dan is de conclusie over "veldvoorstellingen" beperkter |
| Kostenkrimpladder (§12.7) | Is het aantal benzeenconfiguraties verkleind? Is de dichtheid van een goedkopere methode? | Dan geldt een uitzondering op de nauwkeurigheidsbelofte |
| Dichtheidsladder (§12.7) | Is er een fijner rooster of een pseudopotentiaal gebruikt? | Dan is het theorieniveau van de leerstof veranderd |

De logica erachter: een examinator die zelf ontdekt dat er een trede is gebruikt
die niet werd genoemd, gaat zich afvragen wat er nog meer niet is genoemd. Zelf
melden kost een halve minuut; ontdekt worden kost het vertrouwen in het hele
verhaal.

## §16.6 Wat níét is gebouwd

Een verdediging vraagt ook om een duidelijke opsomming van wat er buiten bereik
bleef:

- **Geen identificatie van PAK's in JWST-data.** Dat is project 12.
- **Geen grote PAK's.** De grootste doorgerekende molecule is benzeen, met één ring.
- **Geen spectraallijnen.** Alleen bandposities en relatieve enveloppen, binnen een
  genoemde marge.
- **Geen bewijs dat het veldmodel wint**, tenzij de vooraf vastgelegde
  effectgrootte dat aantoont — en "niet vast te stellen" is een toegestane
  uitkomst (§11.5).

Dat is een ongebruikelijk bescheiden lijst voor een afstudeerpresentatie. Maar
het is precies het punt: elke bewering in dit project is teruggebracht tot iets
wat met een meting kan worden ondersteund.

## §16.7 Uitvoer

| Wat | Vorm |
|---|---|
| De presentatie | 15 minuten, zeven onderdelen |
| De verdediging | 15 minuten vragen |
| Het verdedigingsdocument | Eén pagina, voorbereid vóór de presentatie |

Dat laatste document is de concrete opdracht die het plan in
[Capstone_Mapping §8.5](../GoalGathering/Capstone_Mapping.md) formuleert. Het bevat:
wat er is beweerd, wat er niet is gebouwd, de twee vragen met hun antwoorden, en
de lijst van gebruikte laddertreden.

## §16.8 Waarom deze stap?

Het plan noemt dit "de plek met het hoogste risico dat het eerlijke verhaal onder
vragen instort", en dat is een treffende omschrijving. Alle voorzorgsmaatregelen
uit de voorgaande hoofdstukken — de vooraf vastgelegde splitsingen, de audits, de
toetsrapporten, de taalregels — hebben hier hun nut te bewijzen.

De diepere reden dat het werkt: als je een jaar lang alleen dingen hebt opgeschreven
die je kunt onderbouwen, dan is een verdediging niet meer dan voorlezen wat er
staat. De moeilijkheid van een verdediging is recht evenredig met de hoeveelheid
die je onderweg hebt opgesmukt.

## In het kort

- **Invoer:** het systeem uit project 08, alle toetsrapporten en het overzicht van gebruikte terugvalopties.
- **Bewerking:** een presentatie in zeven vaste onderdelen, plus 15 minuten vragen.
- **Uitvoer:** een verdedigd eindwerk, met een verdedigingsdocument van één pagina als voorbereiding.
- De drie foutbronnen (model, elektronenstructuur, kernbeweging) worden apart gerapporteerd, nooit samengevoegd tot één getal.
- Twee vragen zijn te verwachten: "is dit orbital-free DFT?" (antwoord: ja, en dit is wat er overblijft) en "waarom is dit een CNN?" (antwoord: een $3\times3\times3$-convolutie).
- Elke gebruikte trede van elke terugvalladder wordt uit zichzelf genoemd.
