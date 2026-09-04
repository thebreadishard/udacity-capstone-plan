# Hoofdstuk 1 — Het probleem

> **In dit hoofdstuk leer je**
> – welke moleculen het project bestudeert en waarom sterrenkundigen erin geïnteresseerd zijn;
> – wat een infraroodspectrum is en waarom de *positie* van de banden het doel is;
> – wat "beter dan de beste bestaande voorspelling" precies betekent;
> – hoe de "ladder" van steeds grotere moleculen in elkaar zit;
> – waarom plan 05 de dure berekening anders aanpakt dan plan 04.

---

## §1.1 De moleculen: PAK's

Het project gaat over **polycyclische aromatische koolwaterstoffen**, afgekort PAK's (in het
Engels PAH's). Dat zijn platte moleculen die bestaan uit aan elkaar geplakte zeshoekige
koolstofringen met waterstofatomen aan de rand. Benzeen (één ring) is het kleinste lid van
de familie; naftaleen heeft twee ringen, pyreen vier, coroneen zeven. Aan de bovenkant van
dit project staat een molecuul met 384 koolstofatomen en 48 waterstofatomen: een schijf van
ruim honderd ringen.

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

## §1.3 Het doel: bandposities, en niets anders

Het plan belooft één ding: de **posities** van de banden. Niet hoe sterk ze zijn, niet hoe
breed. De reden is praktisch: van de kleine PAK's is de positie in het lab tot op ongeveer
1 cm⁻¹ bekend, en dat is precies het soort getal waarop een voorspelling kan worden
afgerekend.

> **Definitie 1.1 — De maatstaf**
> De pijplijn is geslaagd voor een molecuul als haar bandposities aantoonbaar dichter bij de
> laboratoriumwaarden liggen dan de beste voorspelling die er nu, voor dat molecuul, ergens
> bestaat — per band beoordeeld, en alleen daar waar de labdata het verschil kan beslissen.

Twee woorden in die definitie doen veel werk.

**"De beste voorspelling die er nu bestaat"** is geen vaag begrip. Het plan legt vooraf vast
tegen wie het speelt: een openbare NASA-databank met berekende spectra (PAHdb), een
zelfgebouwde slimme "gekalibreerde" versie daarvan (module 04), en voor kleine moleculen de
allerbeste rekenmethoden uit de literatuur. Die tegenstanders staan met versienummer in het
document [Frozen_Lines_to_Beat](../GoalGathering/Frozen_Lines_to_Beat.md) en mogen
achteraf niet meer worden verwisseld. Dat heet **pre-registratie**: je schrijft op wat je
gaat meten voordat je meet, zodat je niet achteraf de meetlat kunt verschuiven.

**"Waar de labdata het verschil kan beslissen"** is de tweede beperking. Als een labspectrum
zelf maar tot op 8 cm⁻¹ nauwkeurig is, kun je er geen twee voorspellingen mee uit elkaar
houden die 3 cm⁻¹ van elkaar verschillen. Het plan rekent daarom per band uit hoe
onzeker de labwaarde is (dat getal heet u_band, zie hoofdstuk 8) en verklaart een
vergelijking vooraf **onbeslisbaar** als die onzekerheid groter is dan de te winnen marge.
Dat is geen zwakte maar eerlijkheid: het plan zegt van tevoren welke vergelijkingen het
niet kán winnen of verliezen.

## §1.4 De ladder

Het plan werkt zich van klein naar groot langs een vaste reeks moleculen, de **ladder**.
Elke trede heet een **rung** (het Engelse woord voor sport van een ladder), genummerd R0
tot en met R6.

| Rung | Molecuul | Atomen | Soort | Wat er gebeurt |
|---|---|---|---|---|
| R0 | benzeen | 12 | nauwkeurigheid | alles wordt hier voor het eerst uitgeprobeerd; er bestaat een gouden referentieberekening om de methode te ijken |
| R1 | naftaleen | 18 | nauwkeurigheid | de eerste échte test: is de methode glad genoeg en klopt de teruggevonden correctie? |
| R2 | pyreen, chryseen, trifenyleen, tetraceen | 26–30 | nauwkeurigheid | voorbij wat de literatuur al goed kan |
| R3 | coroneen | 36 | nauwkeurigheid | het grootste molecuul met een bruikbaar labspectrum |
| R4 | circumcoroneen-klasse | ~72–120 | bereik | geen labdata meer; alleen theorie tegen theorie |
| R5 | ~C₂₁₆ | ~250 | bereik | idem |
| R6 | C₃₈₄H₄₈-klasse | 432 | bereik | het einddoel: een spectrum waar niemand er een heeft |

De scheidslijn tussen **nauwkeurigheidsrungs** (R0–R3) en **bereikrungs** (R4–R6) is
principieel. Op R0–R3 bestaat labdata en kan het plan winnen of verliezen. Op R4–R6
bestaat die niet; daar levert het plan een spectrum met een eerlijke foutenmarge, zonder
te claimen dat het "beter" is. De claims zijn dus van verschillend soort, en het plan houdt
ze strikt uit elkaar.

## §1.5 Waarom een nieuwe aanpak: het probleem van plan 04

Om een nauwkeurig spectrum te berekenen heb je een nauwkeurige rekenmethode nodig. De
beste methode die praktisch haalbaar is heet **coupled cluster** (CC, hoofdstuk 3). Ze is
ook peperduur: de rekentijd groeit zo snel met de grootte van het molecuul dat een groot
PAK op een supercomputer nog "vele, vele uren" zou kosten per molecuul.

Plan 04 wilde met CC het hele **energielandschap** van het molecuul in kaart brengen: de
energie als functie van alle atoomposities in de buurt van de evenwichtsstand. Uit dat
landschap volgen de trillingen. Maar het landschap is een enorm object, en elk punt erin
kost een CC-berekening.

Plan 05 draait de vraag om. Een goedkope methode (**DFT**, hoofdstuk 3) geeft al een
landschap dat *bijna* goed is: de fouten zitten in de fijne details. Waarom dan het hele
landschap met CC overdoen? Bereken alleen het **verschil** tussen CC en DFT, en meet dat
verschil met zo weinig mogelijk CC-berekeningen op. Dat verschil heet in dit plan **Δ**
(delta).

> **Definitie 1.2 — Δ**
> Δ is het verschil tussen de dure (coupled-cluster) en de goedkope (DFT) beschrijving van
> het molecuul, uitgedrukt in de krachtconstanten van de trillingen. Plan 05 belooft
> alleen het tweede-orde-deel daarvan, Δ₂: de correctie op de "veerconstanten".

Het idee dat Δ met weinig metingen te bepalen is, rust op twee vermoedens die het plan
niet aanneemt maar **meet**: dat Δ₂ *lokaal* is (een correctie op een binding hangt vooral
van de directe buren af) en dat Δ₂ *dun* is (de meeste kruistermen tussen trillingen zijn
verwaarloosbaar). Als die vermoedens kloppen, kan het aantal benodigde CC-berekeningen
veel kleiner zijn dan het aantal dat een volledig landschap zou vragen. Hoofdstuk 5 legt
uit hoe dat opmeten ("probing") in zijn werk gaat, en hoofdstuk 4 het wiskundig
gereedschap erachter.

## §1.6 Drie vragen die het plan beantwoordt

Het plan formuleert zijn ambitie als drie vragen, die je in deel B steeds terugziet.

1. **Nauwkeurigheid (R0–R3).** Zijn de bandposities met Δ₂ beter dan die van de
   tegenstanders, per band, waar de labdata het kan beslissen?
2. **Kosten (alle rungs).** Hoeveel CC-berekeningen had de correctie nodig, per rung, en
   groeit dat aantal van naftaleen naar coroneen langzamer dan het molecuul zelf? Dat
   aantal heet **K** en wordt gemeten, nooit vooraf gekozen.
3. **Bereik (R6).** Kan dezelfde pijplijn, met Δ₂ opgemeten in stukken (fragmenten), een
   spectrum met foutenmarge leveren voor een molecuul waar niemand er een heeft?

Bij vraag 2 hoort een strenge taalregel: het plan mag nergens zeggen dat de kosten
"schaalonafhankelijk" zijn of "verzadigen". Het mag alleen de gemeten getallen noemen en
naast elkaar zetten. Bijvoeglijke naamwoorden over kosten zijn verboden. Die regel komt
in hoofdstuk 12 terug, want de campagne-officier controleert hem met een tekstfilter.

## §1.7 Wat er in dit hoofdstuk niet stond

Twee dingen zijn bewust weggelaten en komen later. Ten eerste de rekenchemie zelf: wat
DFT en CC precies doen (hoofdstuk 3). Ten tweede het werkelijke bewijs dat Δ₂ lokaal en
dun is: dat bewijs bestaat nog niet, het plan legt alleen vast welke metingen het zouden
leveren en wat er gebeurt als ze mislukken (hoofdstuk 5).

## In het kort

Het plan bouwt een programma dat voor een PAK-molecuul de posities van de
infraroodbanden voorspelt, en die voorspelling moet per band beter zijn dan de beste
bestaande, gemeten tegen labdata die nauwkeurig genoeg is om dat te beslissen. De dure
coupled-clusterberekening wordt niet op het hele molecuul losgelaten, maar alleen op het
verschil met een goedkope DFT-berekening, en dat verschil wordt met zo weinig mogelijk
dure metingen opgemeten. Het plan klimt langs een ladder van benzeen (12 atomen) naar een
schijf van 432 atomen, en houdt de claims voor kleine moleculen (winnen of verliezen)
strikt gescheiden van die voor grote (een spectrum met foutenmarge, zonder winstclaim).

*Bron: [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) (prime directive, de
drie vragen, verboden formuleringen), [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§2, [Why_05_Supersedes_04.md](../GoalGathering/Why_05_Supersedes_04.md).*
