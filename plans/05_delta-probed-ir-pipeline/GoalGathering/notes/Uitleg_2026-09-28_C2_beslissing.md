# Uitleg voor 28 september — wat ging er mis met C2, en wat is de keuze?

Geschreven 27 september 23:1x voor het gesprek van morgen (de gebruiker: "Ik begrijp de beslissing niet, dus morgen graag eenvoudiger en meer
in detail bespreken"). Alle getallen staan in `PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md` (wijzigingen van 22:0x en 22:4x).

## 1. Waar ging het over

Trede C is het "echte" netwerk: het kijkt naar de atomen in de ruimte en voorspelt de correctie op de Hessiaan (ΔH) als een object dat mee-
draait met het molecuul. We vergelijken het met het eenvoudige paarmodel van 23 september, dat op 175 moleculen een ratio van 0,43 haalt
(0,43 = de ringkoppelingsfout is nog 43 % van "niets doen"). Lager is beter.

Twee smaken waren geregistreerd:

- **C1** — het netwerk leert alleen op onze 175 moleculen.
- **C2** — het netwerk leert eerst op 41.645 kleine moleculen uit QM9 (waarvan de Hessianen bekend zijn), en pas daarna op onze 175.
  Het idee: het "lichaam" van het netwerk (alles behalve de laatste laag) leert op QM9 alvast wat een Hessiaan is; onze 175 hoeven dan alleen
  de correctie te leren. Dat heet voortrainen (pretraining) en bijleren (fine-tuning).

## 2. Wat er gebeurde

- **C1** kwam na de eerlijke zoektocht (verliesfunctie, leersnelheid, langer trainen) op 0,81. Ver van het paarmodel (0,43).
- **C2, poging 1 (21:34):** het voortrainen ging goed, maar bij het bijleren werd elke stap "NaN" (geen getal meer). Oorzaak: één invoerkanaal
  (de goedkope Hessiaan H_low) was tijdens het voortrainen leeg gelaten. Gerepareerd: dat kanaal krijgt tijdens het voortrainen een eenvoudige
  vervanger uit de geometrie. Plus een wacht: zodra een verlies geen getal meer is, stopt de run meteen.
- **C2, poging 2 (22:03):** voortrainen weer goed. Bijleren liep bij 45 en 100 moleculen; bij 100 was de ratio 0,81–0,86, dus gelijk aan C1 bij
  175. Toen sloeg de wacht aan op één molecuul van 23 atomen.

## 3. De eigenlijke oorzaak, gemeten

Ik heb het voorgetrainde lichaam losgelaten op vier van onze moleculen en gekeken hoe groot zijn uitvoer is:

| molecuul | atomen | uitvoer voorgetraind lichaam | uitvoer vers lichaam |
|---|---|---|---|
| benzeen | 12 | 0,85 | 16 |
| naftaleen | 18 | 1,1 | 28 |
| carbazool+SH | 23 | 10¹⁸ | 35 |
| nog een 23-atomig molecuul | 23 | 10¹⁷ | 36 |

Een vers (ongetraind) lichaam blijft netjes; het voorgetrainde lichaam is netjes op kleine moleculen en ontploft op grote. Waarom: in elke laag
telt het netwerk de boodschappen van alle buren binnen 5 Å bij elkaar op, zonder te delen door het aantal buren. In QM9 heeft een atoom
typisch 11 buren; in een 23-atomig gefuseerd ringsysteem 15 tot 21. Gewichten die op "11 buren" zijn afgesteld worden bij 21 buren elke laag
een beetje te groot, en dat stapelt op tot 10¹⁸. Het ligt dus niet aan het kanaal en niet aan het bijleren, maar aan een ontwerpkeuze in het
netwerk die pas zichtbaar wordt als je van kleine naar grote moleculen overstapt.

Vergelijking: een recept dat per gast één schep zout voorschrijft, werkt voor een tafel van 11, maar bij 21 gasten is de soep oneetbaar.
Deel je het zout door het aantal gasten (normaliseren), dan smaakt het aan beide tafels.

## 4. De keuze

**Optie A — normaliseren en beide opnieuw draaien (mijn advies).** Het netwerk deelt de opgetelde buurboodschappen door het aantal buren
(of normaliseert per laag). Dat is een wijziging van de geregistreerde architectuur, dus C1 moet met hetzelfde lichaam opnieuw, anders is de
vergelijking C1 tegen C2 niet eerlijk. Kosten: ≈ 40 min (C1-winnaar) + 27 min (voortrainen) + 40 min (C2), op de laptop. Vooraf de
voorvluchtcontrole: het lichaam moet op onze grootste moleculen onder 10³ blijven, anders draait er niets.
Wat we dan weten: of voortrainen op QM9 helpt (C2 onder C1) — de vraag waarvoor stap 3 geregistreerd is.

**Optie B — stoppen bij de C1-winnaar (0,81).** Geen wijziging, geen run. Wat we dan *niet* weten: of voortrainen helpt. De regel van de
voorregistratie zegt dat de zin "richtingen en context helpen niet bij 175" pas mag worden geschreven ná stap 3, en stap 3 is niet gelezen.
Bij B blijft die zin dus ongeschreven, in beide richtingen.

**Waarom A:** de wacht heeft precies gedaan waarvoor hij is (een ontploffing als incident melden, niet als resultaat), en de oorzaak is
gemeten en klein om te repareren. Onze regel (25 september) is: geen negatieve conclusie over een model zonder de geregistreerde zoektocht af
te maken. Voor het voorstel (§3.5) verandert er bij A niets tot de uitlezing; bij B blijft trede C een open eind.

## 5. Wat u niet hoeft te beslissen

De volgorde: eerst de hersortering van laag B (uw "3: morgen"), dan A als u dat kiest — beide op verschillende machines (Helsinki resp. de
laptop), dus ze hinderen elkaar niet.
