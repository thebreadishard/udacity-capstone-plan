# Hoofdstuk 1 — Het probleem

> **In dit hoofdstuk leer je**
> – welke moleculen het project bestudeert en waarom sterrenkundigen erin geïnteresseerd zijn;
> – wat een infraroodspectrum is en waarom de *positie* van de banden het doel is;
> – wat de pijplijn nu toont, waartegen ze wordt afgerekend en wat ze belooft;
> – hoe de "ladder" van steeds grotere moleculen in elkaar zit;
> – waarom plan 05 de dure berekening anders aanpakt dan plan 04;
> – waar het project eindigt en welke vier beweringen het dan onderbouwt.

---

## §1.1 De moleculen: PAK's

Het project gaat over **polycyclische aromatische koolwaterstoffen**, afgekort PAK's (in het
Engels PAH's). Dat zijn platte moleculen die bestaan uit aan elkaar geplakte zeshoekige
koolstofringen met waterstofatomen aan de rand. Benzeen (één ring) is het kleinste lid van
de familie; naftaleen heeft twee ringen, pyreen vier, coroneen zeven. Aan de bovenkant van
dit project staat een molecuul met 384 koolstofatomen en 48 waterstofatomen: een schijf van
ruim honderd ringen.

Het project neemt ook verwanten van de PAK's mee. In sommige ringen zit een stikstofatoom op
de plaats van een koolstofatoom. Aan de rand kan een zijgroep hangen, bijvoorbeeld een
fluor-, chloor-, zuurstof- of zwavelgroep. En een deel van de moleculen mist één elektron: het
draagt dan een positieve lading en heet een **kation**. Zulke geladen PAK's komen in de ruimte
veel voor.

Sterrenkundigen zien in het infrarode licht van nevels en sterrenstelsels een vast patroon
van banden dat aan PAK's wordt toegeschreven. Om te bepalen *welke* PAK's dat zijn, moet je
per molecuul weten waar zijn banden precies liggen. Dat meten in het lab lukt alleen voor de
kleine leden van de familie; voor de grote is een berekening de enige weg.

## §1.2 Wat een infraroodspectrum is

Een molecuul kan trillen: de atomen bewegen ten opzichte van elkaar, als knikkers die met
veren zijn verbonden. Elke manier van trillen heeft een eigen frequentie. Schijn je
infrarood licht op het molecuul, dan wordt precies het licht geabsorbeerd waarvan de
frequentie bij een trilling past. Een grafiek van "hoeveel licht wordt geabsorbeerd" tegen
"frequentie" is het infraroodspectrum. De pieken heten **banden**.

Frequenties worden in dit vakgebied uitgedrukt in **golfgetallen**, eenheid cm⁻¹ (per
centimeter): het aantal golflengten dat in één centimeter past. Een C–H-strektrilling zit
rond 3050 cm⁻¹, een C–C-strektrilling in de ring rond 1600 cm⁻¹, en het uit-het-vlak
buigen van een C–H-binding rond 900 cm⁻¹. Hoofdstuk 2 legt uit waar die getallen vandaan
komen.

Het project deelt de trillingen in vier **families** in, naar de beweging:

- **C–H-strek**: een waterstofatoom beweegt heen en weer langs zijn binding;
- **ring in het vlak** (ring-ip, van *in-plane*): het koolstofskelet ademt of vervormt binnen het
  vlak van het molecuul;
- **C–H uit het vlak** (CH-oop, van *out-of-plane*): een waterstofatoom wipt boven en onder het
  vlak;
- **overig**: de rest, vooral zachte, langzame bewegingen van het hele molecuul.

Elke nauwkeurigheid in dit boek wordt per familie gegeven, omdat de families zich verschillend
gedragen.

## §1.3 Wat de pijplijn toont, waartegen ze wordt afgerekend en wat ze belooft

Het eindproduct is één programma, de **pijplijn**: een molecuul erin, zijn infraroodspectrum
eruit. Het molecuul gaat erin als een korte tekstcode (een SMILES-string, zoals `c1ccccc1` voor
benzeen) of als een lijst atoomposities. Van elke band in het spectrum wil je drie dingen
weten: waar hij zit (de **positie**, in cm⁻¹), hoe sterk hij is (de **intensiteit**) en hoe
breed hij is. Het plan gaat met die drie verschillend om. Daarom houdt het drie werkwoorden
uit elkaar: tonen, afrekenen en beloven.

**Tonen** doet de pijplijn voor alle drie. Elk molecuul krijgt een compleet spectrum, en bij
elk getal staat waar het vandaan komt.

- De *positie* is het getal waar het project om draait. De pijplijn rekent eerst met een
  goedkope methode (DFT, hoofdstuk 3). Daarna voegt een getraind neuraal netwerk, het
  **ΔH-netwerk**, er een correctie aan toe (hoofdstuk 5). De posities volgen uit de
  gecorrigeerde berekening.
- De *intensiteit* komt uit de goedkope methode alleen. Het netwerk verandert haar niet.
- De *breedte* is een tekenkeuze: elke band wordt getekend met een vaste breedte van
  10 cm⁻¹, en het spectrum vermeldt dat.

Bij elk spectrum hoort een **certificaat**. Dat zegt per band hoe goed hij bekend is. Het zegt
ook of het netwerk dit molecuul tijdens de training al heeft gezien, en of het molecuul groter
is dan de moleculen waarop het netwerk leerde.

Wat de pijplijn doet, is ook buiten de projectmap te zien. De **Spectrum Atlas** is een
openbare website met de spectra van alle moleculen uit de trainingsverzameling, de gemeten
nauwkeurigheid van het netwerk en de licentie hieronder
([thebreadishard.github.io/spectrum-atlas](https://thebreadishard.github.io/spectrum-atlas/)).
Op dezelfde site laat de **pijplijnshow** zien hoe een molecuul station voor station door de
pijplijn gaat, met de echt gemeten rekentijd per station. De eerste versie van de hele pijplijn
wordt gedemonstreerd op het gesprek met de begeleider van 25 november 2026 (beslissing 64).

**Afrekenen** betekent: de voorspelling vergelijken met een waarde die beter is. Dat gebeurt op
twee niveaus.

Het eerste niveau is het laboratorium. Daar staat de maatstaf die het plan vooraf vastlegde:

> **Definitie 1.1 — De maatstaf**
> De pijplijn is geslaagd voor een molecuul als haar bandposities aantoonbaar dichter bij de
> laboratoriumwaarden liggen dan de beste voorspelling die er nu, voor dat molecuul, ergens
> bestaat — per band beoordeeld, en alleen daar waar de labdata het verschil kan beslissen.

De definitie bevat twee beperkingen.

**"De beste voorspelling die er nu bestaat"** is vooraf vastgelegd. Het plan speelt tegen een
openbare NASA-databank met berekende spectra (PAHdb), tegen een zelfgebouwde, slim bijgestelde
versie van de goedkope methode (module 04), en voor kleine moleculen tegen de allerbeste
rekenmethoden uit de literatuur. Die tegenstanders staan met versienummer in het document
[Frozen_Lines_to_Beat](../GoalGathering/Frozen_Lines_to_Beat.md) en mogen achteraf niet meer
worden verwisseld. Dat heet **pre-registratie**: je schrijft op wat je gaat meten en hoe je het
leest voordat je meet, zodat je de meetlat achteraf niet kunt verschuiven. Elk experiment in
het project heeft zo'n pre-registratie.

**"Waar de labdata het verschil kan beslissen"** is de tweede beperking. Als een labspectrum
zelf maar tot op 8 cm⁻¹ nauwkeurig is, kun je er geen twee voorspellingen mee uit elkaar
houden die 3 cm⁻¹ van elkaar verschillen. Het plan rekent daarom per band uit hoe onzeker de
labwaarde is (dat getal heet u_band, zie hoofdstuk 8). Is die onzekerheid groter dan de te
winnen marge, dan heet de vergelijking vooraf **onbeslisbaar**.

Voor intensiteiten is het lab schaars. De meeste gasfasespectra zijn niet gekalibreerd: er
staat geen concentratie bij, dus de sterkte is alleen relatief. Alleen bij benzeen en naftaleen
bestaat een gekalibreerde gasfasemeting (de NIST Quantitative-reeks en het PNNL-record). Daar
wordt ook de intensiteit afgerekend; bij de andere moleculen staat ze in het spectrum zonder
oordeel.

Een labspectrum meet de echte trillingen, inclusief het effect dat een veer bij grote uitwijking
stugger of slapper wordt (**anharmoniciteit**, hoofdstuk 2). De pijplijn rekent de posities nu
nog met perfecte veren (**harmonisch**). De anharmonische stap is ontworpen en het rekenniveau
ervoor is gekozen, maar hij zit nog niet in de pijplijn. Daarom gebeurt het afrekenen nu op het
tweede niveau.

Het tweede niveau is een **proxy**: een plaatsvervanger voor de dure waarheid. Een tweede, betere
DFT-variant (ωB97X) speelt de rol van "beter". Het netwerk leert de correctie van de goedkope
variant (B3LYP) naar de betere. Daarna wordt gemeten hoe goed die correctie is op moleculen die
het netwerk nooit heeft gezien. Die moleculen heten **hold-outs**: ze worden vóór de training
apart gezet. Het project heeft er twee. Hold-out (a) bestaat uit acht moleculen uit de eerste,
met de hand gekozen laag van de verzameling, waaronder benzeen en fenantreen. Hold-out (b)
bestaat uit 39 moleculen: alle moleculen met zijgroepen op twee ringskeletten waarvan het
netwerk geen enkel voorbeeld zag.

Op deze proxytaak is het netwerk ook vergeleken met de gangbare reparatie van de goedkope
methode: alle posities vermenigvuldigen met één best passende **schaalfactor**, een getal iets
onder 1. Het netwerk was in elke familie beter; bij een eerdere netwerkversie was de fout voor
de ring in het vlak 1,82 cm⁻¹ tegen 15,47 cm⁻¹ met de beste schaalfactor.

**Beloven** doet het plan alleen voor posities, en per familie. Een familie is **vrijgegeven**
(heeft een **licentie**) als de fout van het netwerk op beide hold-outs binnen 3 cm⁻¹ blijft
(beslissing 65). De fout van één molecuul is de typische afwijking van zijn gecorrigeerde
posities ten opzichte van de ωB97X-posities: de wortel uit het gemiddelde kwadraat van de
verschillen (de **rms**). Het netwerk wordt drie keer getraind, telkens vanuit een andere
willekeurige start; zo'n trainingsrun heet een **seed**. De tabel geeft het gemiddelde over de
drie seeds. Voor de huidige netwerkversie, v1.3, staat het zo:

| Familie | fout op hold-out (a) | fout op hold-out (b) | vrijgegeven |
|---|---|---|---|
| ring in het vlak | 1,77 cm⁻¹ | 2,12 cm⁻¹ | ja |
| C–H-strek | 1,19 cm⁻¹ | 2,50 cm⁻¹ | ja |
| C–H uit het vlak | 2,17 cm⁻¹ | 2,70 cm⁻¹ | ja |
| overig | 3,62 cm⁻¹ | 3,89 cm⁻¹ | nee |

Het certificaat markeert elke band volgens deze tabel. Een band uit de familie "overig" krijgt
dus geen belofte.

Bij deze tabel horen twee kanttekeningen. Ten eerste geldt de licentie op proxyniveau: ze zegt
hoe goed het netwerk de stap van B3LYP naar ωB97X voorspelt. Een licentie op het niveau van de
dure methode (coupled cluster) bestaat niet. Ten tweede stonden er eerst tien moleculen in
hold-out (a). Een controle in de pijplijn vond dat twee daarvan ook in een latere laag van de
verzameling stonden en via die dubbelganger tóch in de training zaten. Ze zijn uit hold-out (a)
gehaald, en de trainer gooit zulke dubbelgangers nu standaard weg. De fouten op de schone acht liggen 0,04 tot 0,27 cm⁻¹ hoger; de licentie
veranderde voor geen enkele familie. De les: een hold-out is pas schoon als een programma dat
heeft gecontroleerd.

## §1.4 De ladder

Het plan werkt zich van klein naar groot langs een vaste reeks moleculen, de **ladder**.
Elke trede heet een **rung** (het Engelse woord voor sport van een ladder), genummerd R0
tot en met R6. De namen in de tabel geven de grootte van een trede aan. Een trede zelf is een
zo groot mogelijke verzameling moleculen van die grootte, want één molecuul per trede zegt
niets over of het geleerde meegaat naar de volgende.

| Rung | Molecuul | Atomen | Soort | Wat er gebeurt |
|---|---|---|---|---|
| R0 | benzeen | 12 | nauwkeurigheid | alles wordt hier voor het eerst uitgeprobeerd; er bestaat een gouden referentieberekening om de methode te ijken |
| R1 | naftaleen | 18 | nauwkeurigheid | de eerste echte test van de correctie |
| R2 | pyreen, chryseen, trifenyleen, tetraceen | 26–30 | nauwkeurigheid | voorbij wat de literatuur al goed kan |
| R3 | coroneen | 36 | nauwkeurigheid | het grootste molecuul met een bruikbaar labspectrum |
| R4 | circumcoroneen-klasse | ~72–120 | bereik | geen labdata meer; alleen theorie tegen theorie |
| R5 | ~C₂₁₆ | ~250 | bereik | idem |
| R6 | C₃₈₄H₄₈-klasse | 432 | bereik | het einddoel: een spectrum waar niemand er een heeft |

De scheidslijn tussen **nauwkeurigheidsrungs** (R0–R3) en **bereikrungs** (R4–R6) is
principieel. Op R0–R3 bestaat labdata en kan het plan winnen of verliezen. Op R4–R6
bestaat die niet; daar levert het plan een spectrum met een eerlijke foutenmarge, zonder
te claimen dat het "beter" is.

De ladder wordt langzaam beklommen, ring voor ring en met kationen erbij. Het netwerk is
getraind op moleculen van 8 tot 30 atomen; dat zijn de treden R0 tot en met R2. Of de
correctie meegaat naar moleculen van 34 tot 60 atomen, zoals coroneen (R3) en iets grotere
schijven, wordt nu gemeten. R4 tot en met R6 vallen buiten het afstudeerproject.

## §1.5 Waarom een nieuwe aanpak: het probleem van plan 04

Om een nauwkeurig spectrum te berekenen heb je een nauwkeurige rekenmethode nodig. De
beste methode die praktisch haalbaar is heet **coupled cluster** (CC, hoofdstuk 3); de
standaardvorm heet CCSD(T). Ze is ook peperduur: de rekentijd groeit zo snel met de grootte
van het molecuul dat een groot PAK op een supercomputer nog vele uren per molecuul zou kosten.

Plan 04 wilde met CC het hele **energielandschap** van het molecuul in kaart brengen: de
energie als functie van alle atoomposities in de buurt van de evenwichtsstand. Uit dat
landschap volgen de trillingen. Maar het landschap is een enorm object, en elk punt erin
kost een CC-berekening.

Plan 05 draait de vraag om. Een goedkope methode (**DFT**, hoofdstuk 3) geeft al een
landschap dat *bijna* goed is: de fouten zitten in de fijne details. Het plan berekent daarom
alleen het **verschil** tussen CC en DFT. Dat verschil heet in dit plan **Δ** (delta).

> **Definitie 1.2 — Δ**
> Δ is het verschil tussen de dure (coupled-cluster) en de goedkope (DFT) beschrijving van
> het molecuul, uitgedrukt in de krachtconstanten van de trillingen. Plan 05 belooft
> alleen het tweede-orde-deel daarvan, Δ₂: de correctie op de "veerconstanten".

Het oorspronkelijke plan wilde Δ₂ per molecuul opmeten met zo weinig mogelijk dure
berekeningen. Dat rustte op twee vermoedens: dat Δ₂ *lokaal* is (een correctie op een binding
hangt vooral van de directe buren af) en dat Δ₂ *dun* is (de meeste kruistermen tussen
trillingen zijn verwaarloosbaar). De metingen bevestigden de lokaliteit. Ze lieten ook zien
dat één dure berekening van een middelgroot molecuul uren kost, zodat zelfs weinig berekeningen
per molecuul te veel is. Daarom leert het project de correctie nu één keer, uit veel
voorbeelden, en voorspelt het haar daarna voor elk nieuw molecuul. Hoofdstuk 5 legt die stap
uit, en hoofdstuk 4 het wiskundig gereedschap erachter.

## §1.6 Waar het project eindigt

Het afstudeerproject eindigt met het **bewijs op proxyniveau** (beslissing 63). Dat bewijs heeft
drie delen:

1. de pijplijn staat en werkt van molecuul tot spectrum;
2. de correctie per familie is geleerd en getest met twee DFT-varianten (B3LYP naar ωB97X), op
   de hold-outs en op moleculen groter dan die in de trainingsverzameling;
3. de bestaande CC-berekeningen, de **ankers**, vormen de brug naar het dure niveau.

Nieuwe CC-ankers horen niet bij het afstudeerproject. Hoe ze na juni 2027 worden gemaakt, beslist
de begeleider. Betaalde rekentijd op gehuurde servers stopt op 15 november 2026; daarna rekent
het project alleen op de laptop. Het bewijs is eind november 2026 compleet. Van december 2026 tot
februari 2027 worden de modules en het eerste artikel geschreven; maart tot juni 2027 is buffer
en overdracht.

Voor het gesprek met de begeleider ordent het project zijn bewijs in vier beweringen:

1. **Het netwerk leert de correctie, en die gaat mee naar grotere moleculen.** Het eerste deel
   staat in de licentietabel van §1.3. Het tweede deel wordt nu gemeten.
2. **Een paar voorbeelden van een nieuw niveau verschuiven een voorgetraind netwerk.** Een
   netwerk dat de proxycorrectie kent, past zich met weinig voorbeelden aan een andere
   correctie aan (hoofdstuk 5).
3. **Het aantal ankers per nauwkeurigheid, met prijzen.** Een generale repetitie op proxyniveau
   zegt hoeveel ankers elke familie nodig heeft, en wat die zouden kosten (hoofdstuk 5).
4. **De elf ankers als brug.** De elf bestaande CC-berekeningen laten zien hoe het netwerk zich
   op het dure niveau gedraagt. De lat van 3 cm⁻¹ op dat niveau wordt niet geclaimd.

Bij kosten geldt een taalregel: het plan noemt alleen gemeten getallen en prijzen en zet ze naast
elkaar. Bijvoeglijke naamwoorden over kosten, zoals "schaalonafhankelijk" of "verzadigend",
gebruikt het niet.

## §1.7 Wat er in dit hoofdstuk niet stond

Drie dingen komen later. De natuurkunde van trillingen en de Hessiaan, de tabel met alle
veerconstanten, staan in hoofdstuk 2. Wat DFT en CC precies doen, staat in hoofdstuk 3. Hoe het
netwerk de correctie leert en hoe de ankers het ijken, staat in hoofdstuk 5.

## In het kort

Het project bouwt een programma dat voor een PAK-molecuul, of een verwant ervan, het
infraroodspectrum voorspelt. De posities komen uit een goedkope DFT-berekening plus een
correctie van een getraind netwerk; de intensiteiten komen uit DFT alleen. Op lange termijn wordt
de pijplijn afgerekend tegen labdata die nauwkeurig genoeg is om dat te beslissen. In het
afstudeerproject gebeurt het afrekenen op proxyniveau: het netwerk leert de stap tussen twee
DFT-varianten en wordt gemeten op twee hold-outs. Drie van de vier families zijn vrijgegeven,
met een fout onder 3 cm⁻¹ op beide hold-outs; de familie "overig" niet. Een licentie op het dure
CC-niveau bestaat niet. Het project eindigt met het bewijs op proxyniveau en de elf bestaande
CC-ankers als brug; nieuwe ankers komen na juni 2027.

*Bron: [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) (de maatstaf, verboden
formuleringen), [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§2, [Why_05_Supersedes_04.md](../GoalGathering/Why_05_Supersedes_04.md);
[README.md](../README.md) beslissingen 39, 53, 63, 64 en 65; [PIPELINE.md](../modules/PIPELINE.md)
(pijplijn 0.9, wat ze aanneemt en wat het certificaat claimt); [MODELS.md](../modules/MODELS.md)
(ΔH-netwerk v1.3); de fouten per familie uit `m08/licence.py` op de evaluatierecords van v1.3
(hold-out (a) zonder de twee dubbelgangers); [TASKS_closed.md](../TASKS_closed.md) taak 157
(de dubbelgangers in hold-out (a)); [TASKS.md](../TASKS.md) taak 140 (de vier beweringen) en
taak 53 (de anharmonische stap).*
