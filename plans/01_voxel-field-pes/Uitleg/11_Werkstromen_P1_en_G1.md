# Hoofdstuk 11 — Werkstromen P1 en G1: het eigenlijke experiment

> **In dit hoofdstuk leer je**
> – waarom de belangrijkste twee stappen van dit onderzoek géén schoolproject zijn;
> – hoe de verliesfunctie van het veldmodel is opgebouwd, term voor term;
> – wat een equivariant graafnetwerk is en waarom dat een eerlijke tegenstander is;
> – wat pre-registratie is en waarom die hier alles bepaalt;
> – welke conclusies vooraf zijn toegestaan — inclusief "we weten het niet".

**Categorie:** geen schoolmodule. Ongewaardeerde onderzoekswerkstroom.
**Positie in de keten:** na de watercampagne; P1 en G1 draaien parallel.

---

## §11.1 Waarom dit geen schoolproject is

Een merkwaardige eigenschap van dit plan: de twee stappen die de eigenlijke
onderzoeksvraag beantwoorden, leveren **geen studiepunten** op.

Dat is een bewuste keuze, en het is de oplossing van het eerste blokkerende punt
uit de kritische beoordelingen. Fase 1 — het trainen van het veldmodel op water —
paste namelijk in geen enkele schoolopdracht:

| Zou het passen bij… | Nee, want… |
|---|---|
| Project 04 | Dat vraagt een tabel en een eenvoudig model, geen $32^3$-tensoren |
| Project 05 | Dat is de enige plek voor een groot netwerk, en dat moet op benzeen wegens de regel dat datasets niet hergebruikt mogen worden |
| Project 07 | De agent mag gereedschap gebruiken, niet zelf trainen |
| Project 08 | Daar mag niets voor het eerst gebeuren |

De oplossing: noem het wat het is — onderzoek — en geef het een eigen plaats in
de planning, met eigen leverbare producten en een eigen faalscenario. Zo wordt
voorkomen dat de belangrijkste stap een "spooktaak" wordt die overal een beetje
en nergens echt thuishoort.

---

## §11.2 Werkstroom P1: het veldmodel op water

### Invoer

| Wat | Vorm | Omvang |
|---|---|---|
| Volumetrische tensoren | `.npz`, $32^3$ per configuratie | ≥ 2000 configuraties |
| Per configuratie | kernposities, doel-$\Delta\rho$, energie, krachten, dipoolmoment | zie §6.4 |
| Eén Hessiaan | bij de evenwichtsstand | 1 stuk |
| Splitsingsbestand | JSON met hash | 1 bestand |

Let op die ene Hessiaan. Een Hessiaan bij elke configuratie zou onbetaalbaar
zijn, dus het plan telt ze: één voor water, één voor benzeen, allebei alleen bij
de evenwichtsstand. Ook dat is een verbetering ten opzichte van een eerdere
versie, die vaag sprak van "geselecteerde stationaire punten" zonder aantal.

### De verliesfunctie

Trainen betekent: een getal minimaliseren dat aangeeft hoe fout het model zit.
Dat getal heet de verliesfunctie.

$$L_{\text{train}} = \lambda_E L_E + \lambda_F L_F + \lambda_H L_H + \lambda_\rho L_\rho + \lambda_\mu L_\mu$$

| Term | Waarop | Waarom nodig |
|---|---|---|
| $L_E$ | De energie | Het hoofddoel |
| $L_F$ | De krachten | Energie alleen legt de *helling* van het landschap niet vast |
| $L_H$ | De Hessiaan bij evenwicht | Krachten alleen leggen de *kromming* niet vast, en kromming is de trillingsfrequentie |
| $L_\rho$ | De deformatiedichtheid $\Delta\rho$ | Dit stuurt het **argument** van de energiefunctionaal, niet zomaar een extraatje |
| $L_\mu$ | Het dipoolmoment | Nodig voor de intensiteiten (§2.6) |

De $\lambda$'s zijn weegfactoren die bepalen hoe zwaar elke term meetelt.

> **Waarom $L_\mu$ er vanaf het begin in zit**
> Een eerdere versie van het plan zei: "voeg $L_\mu$ toe als de dipooltoets niet
> gehaald wordt." Dat is bij nader inzien verboden, en om een goede reden. Als je
> pas een term toevoegt nadat je de uitslag hebt gezien, dan kies je je model op
> grond van de test — en dan meet de test niets meer (§4.9). De term zit er dus
> vanaf de eerste productierun in, of hij zit er niet in.
>
> Er is ook een inhoudelijke reden dat hij niet gemist kan worden: $L_\rho$ is een
> gemiddelde kwadratische fout over de hele doos, en zo'n maat let vooral op de
> plaatsen waar de dichtheid groot is. Het dipoolmoment hangt juist af van de ijle
> buitenrand van de wolk. Een model kan $L_\rho$ dus uitstekend halen en toch een
> beroerd dipoolmoment hebben.

Wat er nadrukkelijk **niet** in staat: er is geen enkele term die iets met een
spectrum te maken heeft. Een eerdere versie van het plan had die wel, en die is
geschrapt met deze redenering: als je een model beloont voor het produceren van
de goede pieken, dan zal het leren om de goede pieken te produceren — desnoods
met twee fouten die elkaar toevallig opheffen. Je test dan niet meer of de
natuurkunde klopt.

### De toetsingseisen van fase 1

Voordat er ook maar één simulatie mag draaien, moeten deze eisen gehaald zijn:

| Eis | Drempel | Waarom die waarde |
|---|---|---|
| Machinefout | $< 0{,}1$ meV/Å | Tien keer onder de modeleis (§5.4) |
| Krachtfout (RMSE) | $< \max(1\ \mathrm{meV/\text{Å}},\ 3\times$ ruisniveau van de data$)$ | Boven de onvermijdelijke datafout, niet boven machinefouten |
| Harmonische frequenties | binnen 5 cm⁻¹ van de CCSD(T)-Hessiaan | Een derde van de spectrale eindeis |
| Dipoolmoment | $\lVert\boldsymbol\mu_\theta - \boldsymbol\mu_{\mathrm{QM}}\rVert < 0{,}01\ e\,a_0$ | ≈ 1,4% van het dipoolmoment van water (Voorbeeld 6.1) |
| Dipoolafgeleide | relatieve fout $< 5\%$ | Volgt uit de 10%-eis op intensiteiten (Voorbeeld 2.5) |
| Roosterfout in $\boldsymbol\mu$ | $< 0{,}1\%$ bij starre verschuiving | Het dipoolmoment mag niet van de roosterplaats afhangen |

De drie dipooleisen zijn **voorwaarden vooraf**. Het plan verwoordt waarom
scherp: het spectrum $I(\omega)$ is een functie van $\boldsymbol\mu(t)$, dus
50 picoseconde simuleren kan een verkeerde dipoolafgeleide niet repareren — het
verspilt er alleen rekentijd aan.

### Uitvoer

- Bevroren gewichten van het productiemodel;
- bevroren gewichten van de twee vergelijkingsbenen (zie §11.3);
- een toetsrapport met per eis: drempel, gemeten waarde, oordeel;
- de splitsings- en observabelenmanifesten.

---

## §11.3 Drie modellen, één eerlijke vergelijking

Nu het scherpste stuk denkwerk van het hele plan. Het komt uit de derde
beoordelingsronde en het corrigeert een fout die makkelijk over het hoofd te zien
is.

**Het probleem.** De oorspronkelijke opzet was: train het veldmodel (met
dichtheidsdata) en train een graafmodel (zonder dichtheidsdata), en kijk wie
wint. Maar stel het veldmodel wint. Wat heb je dan aangetoond?

Niets over de voorstelling. Het veldmodel had namelijk **meer informatie**: het
kreeg naast energieën en krachten ook nog eens de complete elektronenwolk
voorgeschoteld. Een winst kan dan net zo goed komen door die extra informatie als
door de voorstellingswijze. De twee oorzaken zijn niet te scheiden.

**De oplossing.** Train drie modellen in plaats van twee.

| Been | Krijgt te zien | Waarvoor dient het |
|---|---|---|
| **MACE-EF** | Energie + krachten | De tegenstander: een graafmodel |
| **Field-EF** | Energie + krachten (dus $\lambda_\rho = 0$) | Het veldmodel met **exact dezelfde** informatie |
| **Field-EFρ** | Energie + krachten + dichtheid | Alleen dit been krijgt de dichtheid erbij |

Nu kun je twee onafhankelijke vragen beantwoorden:

1. **Field-EF tegen MACE-EF** — gelijke informatie, verschillende voorstelling.
   Dít is de hoofdvraag uit hoofdstuk 1.
2. **Field-EFρ tegen Field-EF** — gelijke voorstelling, verschillende informatie.
   Dit meet wat dichtheidssupervisie oplevert.

Field-EF en Field-EFρ zijn verder tot in de puntjes identiek: dezelfde
architectuur, dezelfde startgetallen, hetzelfde trainingsschema. Alleen
$\lambda_\rho$ verschilt. Zo verandert er precies één ding tegelijk — het
grondbeginsel van elk experiment.

Het volledige productiemodel (met $E$, $F$, $H$, $\rho$ én $\mu$) doet aan deze
vergelijking niet mee. Dat is het beste *systeem*, en het levert de spectra, maar
het kan de vraag naar de voorstelling niet beantwoorden.

---

## §11.4 Werkstroom G1: de tegenstander

> **Definitie 11.1 — Grafenneuraal netwerk (GNN)**
> Een model dat een molecuul voorstelt als een graaf: atomen zijn knopen, nabije
> atoomparen zijn verbindingen. Elke knoop wisselt herhaaldelijk informatie uit
> met zijn buren en bouwt zo een beschrijving van zijn omgeving op.

> **Definitie 11.2 — Equivariantie**
> Een model is rotatie-equivariant als geldt: draai je het molecuul, dan draaien
> de voorspelde krachten **exact even hard mee**. Dat is geen benadering maar een
> wiskundige eigenschap van de constructie.

**MACE** is een modern equivariant graafnetwerk en geldt in dit vakgebied als een
sterke standaard. In dit project wordt het **vanaf nul** getraind op onze eigen
CCSD(T)-data. Een kant-en-klaar, op DFT-data voorgetraind exemplaar zou niet
mogen: dat zou een andere theorie zijn, en dus een oneerlijke vergelijking.

> **Een vooraf opgeschreven nadeel**
> MACE is per constructie exact rotatie-equivariant. Het veldmodel is dat níét,
> want een kubisch voxelrooster is niet in alle richtingen hetzelfde (§9.5).
>
> Dat is een echt nadeel voor het veldmodel, en het plan doet er iets bijzonders
> mee: het eist dat de rotatiefout van de motor **gepubliceerd wordt vóórdat** de
> vergelijking plaatsvindt. Anders zijn twee heel verschillende conclusies later
> niet uit elkaar te houden:
> - "de veldvoorstelling generaliseert slechter" — een resultaat over het idee;
> - "onze discretisatie breekt een symmetrie die de tegenstander gratis krijgt" —
>   een resultaat over de uitvoering.
>
> Alleen vooraf gemeten getallen kunnen dat onderscheid maken.

---

## §11.5 Pre-registratie: de regels vóór de wedstrijd

> **Definitie 11.3 — Pre-registratie**
> Het vooraf vastleggen van de volledige opzet en analyse van een experiment, in
> een gedateerd en onveranderlijk document, vóórdat de data wordt bekeken.

Het plan is hier onverbiddelijk: een vergelijking tussen een zelfgebouwd model en
een volwassen, door de makers afgestemd programma is **geen experiment** totdat
het volgende vaststaat, in een opslagmoment dat vooraf gaat aan elke training.

> **Stappenplan 11.1 — De zeven pre-registratie-eisen ([Distilled Plan §7.1](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md))**
>
> **1. Bevroren splitsing.** Eén bestand `splits/{molecuul}_{versie}.json`, met een
> controlegetal dat in elk rapport wordt vermeld. Niemand splitst opnieuw.
>
> **2. Startgetallen en foutbalken.** Minstens drie trainingen per model met
> verschillende startwaarden. Resultaten als gemiddelde ± standaarddeviatie. *Eén
> getal is geen resultaat.*
>
> **3. Gelijke afstemming.** Even veel afstelpogingen en even veel rekentijd voor
> beide modellen, uitsluitend op de validatiedata. MACE begint bij het recept van
> zijn eigen makers — een niet-afgestelde tegenstander is een stroman, en een
> beoordelaar zal dat zeggen.
>
> **4. Vooraf vastgelegde effectgrootte.** De maat is de verhouding
> $$r = \frac{\mathrm{RMSE}^{F}_{\text{Field-EF}}}{\mathrm{RMSE}^{F}_{\text{MACE-EF}}}$$
> op de achtergehouden trillingsfamilie. De uitslagregel:
>
> | Uitslag | Voorwaarde |
> |---|---|
> | veld wint | $r < 1 - \Delta$ met niet-overlappende foutbalken |
> | graaf wint | $r > 1 + \Delta$ met niet-overlappende foutbalken |
> | **niet vast te stellen** | in alle andere gevallen |
>
> $\Delta$ is voorlopig $0{,}10$ en wordt definitief vastgesteld op driemaal de
> gemeten spreiding tussen startgetallen **op de validatiedata**, vóórdat een van
> beide modellen de achtergehouden familie ziet.
>
> **5. Verstorende factoren vooraf benoemd**, zodat ze later geen excuus kunnen
> worden: de equivariantie-asymmetrie, het verschil in volwassenheid van de
> software, de gelijke datahoeveelheid, het feit dat dichtheidsdata bevoorrechte
> informatie is, welke terugvalopties zijn gebruikt.
>
> **6. Analyse bevroren.** Maat, samenvatting over startgetallen en de vorm van de
> grafiek liggen vast vóór de testevaluatie. Geen achteraf zoeken naar een maat die
> beter uitkomt.
>
> **7. De testverzameling wordt één keer aangeraakt.** Elke herhaling moet met
> reden worden gemeld.

De toegestane conclusies liggen daarmee ook vast:

| Uitkomst | Wat je mag zeggen |
|---|---|
| Field-EF wint van MACE-EF | Steun voor de veldhypothese bij gelijke supervisie |
| Field-EF wint niet, Field-EFρ wel | De dichtheidsgesuperviseerde pijplijn wint; over de voorstelling is niets aangetoond |
| Geen van beide veldbenen wint | Geen aangetoond voordeel ten opzichte van het graafmodel |
| Alles binnen de marge | **Niet vast te stellen** |

Die laatste regel is opmerkelijk en verdient nadruk. In het plan staat letterlijk
dat "inconclusive" een **publiceerbare uitkomst** is. De vraag was of de
veldvoorstelling beter generaliseert, en "we konden het niet vaststellen" is
daarop een eerlijk antwoord. Dat vooraf opschrijven haalt de druk weg om
achteraf een winnaar te fabriceren.

---

## §11.6 Wat als het misgaat?

Elke werkstroom heeft een uitgeschreven faalscenario. Zonder zo'n scenario is een
plan alleen geldig als alles lukt, en dat is geen plan.

**Als P1 zijn eisen niet haalt:**

- Project 07 gaat gewoon door. De agent moet de controles uitvoeren, de gemeten
  waarde naast de drempel zetten en **GEZAKT** uitspreken. Een geblokkeerde toets
  is een geldige demonstratie; een verzonnen "geslaagd" niet.
- De fasen 2 en 3 worden gemarkeerd als geblokkeerd — niet stilzwijgend
  overgeslagen en niet vervangen door een benzeenmodel.
- Project 05 mag alleen doorgaan als de *architectuur* stabiel is. Was de motor
  zelf kapot, dan begint 05 niet.
- Project 08 meldt de vergelijking als onvolledig.

**Als G1 ontbreekt of andere splitsingen gebruikt:**

- Project 08 mag de veld-tegen-graafbewering **niet** doen.
- Het model van project 04 mag níét in de plaats van MACE worden gezet. Dat zijn
  totaal verschillende dingen.
- Als laatste redmiddel mag de onderzoeksvraag schriftelijk worden afgezwakt tot
  "veld tegen eenvoudig netwerk". Dat is een zwakkere scriptie, maar het is beter
  dan een gehaaste, niet-afgestelde MACE-run in de laatste week.

De slotzin van deze paragraaf in het plan is de moeite waard: *"A GNN win on the
pre-registered transfer split is a valid thesis. A missing G1 is not."* Verliezen
mag. Niet meten mag niet.

## In het kort

- P1 (veldmodel op water) en G1 (graafmodel op dezelfde data) zijn de kern van het onderzoek, maar leveren geen studiepunten op.
- De verliesfunctie combineert energie, krachten, kromming, dichtheid en dipoolmoment — en bevat nooit iets spectraals.
- Er worden drie modellen getraind: MACE-EF, Field-EF en Field-EFρ, zodat voorstelling en informatie los van elkaar te meten zijn.
- De hele opzet wordt vooraf vastgelegd: splitsing met controlegetal, drie startgetallen, gelijk afsteltijd, en een vooraf gekozen effectgrootte $\Delta$.
- "Niet vast te stellen" is vooraf toegestaan als eindconclusie.
- Voor beide werkstromen staat het faalscenario uitgeschreven; ontbrekend bewijs telt nooit als geslaagd.
