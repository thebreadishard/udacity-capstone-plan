# Hoofdstuk 2 — Natuurkunde: trillingen en licht

> **In dit hoofdstuk leer je**
> – hoe een molecuul trilt en waarom een veer het goede model is;
> – wat een normaaltrilling is en hoeveel er zijn;
> – wat de Hessiaan is en waarom die het hart van het hele plan vormt;
> – het verschil tussen harmonisch en anharmonisch, en wat een resonantie is;
> – waarom temperatuur banden verschuift, en waarom dat voor de labdata uitmaakt.

---

## §2.1 Eén veer

Een massa m aan een veer met veerconstante k trilt met hoekfrequentie

ω = √(k / m).

Dat ken je uit de natuurkunde. Voor een molecuul met twee atomen is dit al bijna het hele
verhaal: de binding gedraagt zich als een veer, de "massa" is een combinatie van de twee
atoommassa's, en de frequentie van de absorptieband volgt uit k.

Een stijvere binding (grotere k) trilt sneller; een zwaarder atoom (grotere m) trilt
trager. Dat is waarom een C–H-strektrilling (licht waterstofatoom) rond 3050 cm⁻¹ zit en
een C–C-strektrilling rond 1600 cm⁻¹.

## §2.2 Veel veren tegelijk: normaaltrillingen

Een molecuul met N atomen heeft 3N coördinaten (x, y en z per atoom). Drie daarvan
beschrijven een verschuiving van het hele molecuul en drie een draaiing; die kosten geen
energie. Blijven over: **3N − 6 trillingen**. Benzeen heeft er 30, naftaleen 48, coroneen
102, en de C₃₈₄H₄₈-schijf 1290. Dat getal heet in het plan **M**, het aantal modes.

Als je één atoom een zetje geeft, gaat niet dat ene atoom trillen maar het hele molecuul,
in een ingewikkelde combinatie. Er bestaan echter M bijzondere bewegingspatronen waarbij
*alle* atomen netjes met dezelfde frequentie heen en weer gaan, elk langs zijn eigen
richting. Die patronen heten **normaaltrillingen** of **normale modes**. Elke willekeurige
trilling is een optelsom van normale modes, en elke band in het spectrum hoort bij één
normale mode (soms bij een combinatie, zie §2.5).

> **Definitie 2.1 — Normale mode**
> Een normale mode is een bewegingspatroon van alle atomen samen waarbij iedereen met één
> gemeenschappelijke frequentie trilt. Een molecuul met N atomen heeft er M = 3N − 6. De
> uitwijking langs een mode wordt aangeduid met een dimensieloze coördinaat q; q = 1 is
> ongeveer de uitwijking die de trilling in zijn laagste energietoestand heeft.

De normale modes van één molecuul kun je grofweg indelen in **families** naar wat er
beweegt: C–H-strek (rond 3050 cm⁻¹), C–C-strek in de ring (1400–1600 cm⁻¹), C–H-buiging in
het vlak (1000–1300 cm⁻¹), C–H-buiging uit het vlak (700–900 cm⁻¹). Het plan scoort en
rapporteert per familie, omdat de nauwkeurigheid van de rekenmethoden per familie
verschilt en omdat de sterrenkunde vooral in bepaalde families geïnteresseerd is (de
6,2 en 7,7 µm-banden zijn C–C-strek).

Het netwerk en zijn licentie (hoofdstukken 10 en 13) gebruiken vier families, met een vaste regel
op frequentie en bewegingsrichting: **CH-stretch** (boven 2800 cm⁻¹, vooral waterstof beweegt),
**ring-ip** (950–1750 cm⁻¹, beweging in het vlak: de C–C-strek en de C–H-buiging in het vlak
samen), **CH-oop** (600–1050 cm⁻¹, beweging uit het vlak, met waterstof erin) en **'other'**: de
rest, zoals zachte trillingen van het hele skelet en trillingen van zijgroepen.

## §2.3 De Hessiaan: alle veerconstanten in één tabel

Voor één veer is de energie E = ½ k x². De veerconstante is de tweede afgeleide van de
energie naar de uitwijking: k = d²E/dx².

Voor een molecuul met 3N coördinaten is er niet één veerconstante maar een hele tabel: hoe
verandert de kracht op atoom i in richting a als je atoom j in richting b een beetje
verplaatst? Die tabel van alle tweede afgeleiden heet de **Hessiaan**. Het is een
vierkante tabel (matrix, zie hoofdstuk 4) met 3N rijen en 3N kolommen; voor benzeen dus
36 × 36 = 1296 getallen, waarvan door symmetrie de helft dubbel is.

> **Definitie 2.2 — Hessiaan**
> De Hessiaan H is de matrix van tweede afgeleiden van de energie naar de atoomposities:
> H_ij = ∂²E/∂x_i∂x_j. Op de diagonaal staan de "eigen" veerconstanten van elke
> coördinaat; buiten de diagonaal staat hoe sterk twee coördinaten aan elkaar gekoppeld
> zijn.

Uit de Hessiaan volgen de normale modes en hun frequenties in één wiskundige stap
(diagonaliseren, hoofdstuk 4). Dat is waarom de Hessiaan het hart van het plan is: **wie de
Hessiaan goed heeft, heeft de harmonische bandposities goed.** Het plan-05-idee is precies
dat je niet de hele Hessiaan met de dure methode hoeft te berekenen, maar alleen de
*correctie* op de goedkope Hessiaan. Die correctie is een even grote matrix en heet Δ₂, in
het gebouwde product ΔH. Het product meet die correctie niet per molecuul: een neuraal netwerk
voorspelt haar (hoofdstuk 10).

Schrijf je de Hessiaan niet in atoomcoördinaten maar in de coördinaten van de goedkope
normale modes, dan is de goedkope Hessiaan zelf diagonaal (dat is de definitie van
normale modes). De correctie Δ₂ is dan een matrix waarvan de diagonaal zegt "deze mode moet
iets stijver of slapper" en de niet-diagonale elementen zeggen "deze twee modes zijn toch
een beetje aan elkaar gekoppeld". Het eerste ontwerp verwachtte dat die niet-diagonale
elementen vooral groot zijn tussen modes met bijna dezelfde frequentie. De metingen wezen anders
uit. In de modebasis bleken de koppelingen niet te leren, omdat een normale mode een richting
zonder vast teken is. In lokale coördinaten (bindingslengtes en hoeken) zit driekwart van de
correctie in paren die een atoom of een ring delen. Het netwerk leert de correctie daarom in lokale
coördinaten en zet haar daarna om naar de modes (besluit 49, hoofdstuk 5).

## §2.4 Harmonisch en anharmonisch

Een echte binding is geen ideale veer. De energiekromme is niet precies een parabool: bij
uitrekken wordt de binding slapper, bij indrukken stijver. De parabool is de **harmonische
benadering**; de afwijkingen ervan heten **anharmoniciteit**.

In een machtreeks:

E(q) = ½ k q² + (1/6) φ₃ q³ + (1/24) φ₄ q⁴ + …

De coëfficiënten φ₃ en φ₄ heten de kubische en kwartische krachtconstanten. Anharmoniciteit
verschuift de banden meestal een paar procent omlaag ten opzichte van de harmonische
frequentie: een harmonische C–H-strek van 3200 cm⁻¹ wordt in werkelijkheid rond 3050 cm⁻¹
waargenomen.

Plan 05 maakt hier een scherpe keuze. De **dure** methode wordt alleen gebruikt voor de
harmonische correctie Δ₂. De anharmonische correctie komt uit de **goedkope** methode.
Waarom? Twee redenen. Ten eerste laat de literatuur (twee studies aan kleine moleculen, items
14 en 27; een PAK-precedent bestaat niet) zien dat het grootste deel van het verschil tussen
goedkope en dure spectra in de harmonische term zit; anharmonische
constanten zijn bij de goedkope methode al redelijk. Ten tweede zou het opmeten van de dure
anharmonische constanten het aantal benodigde berekeningen enorm vergroten, en juist dat
aantal wil het plan klein houden. Het plan belooft daarom uitdrukkelijk **geen**
coupled-clustercorrectie op anharmonische constanten.

De vorm van het eindspectrum is daarmee ν = ω + Δ_anh: de harmonische frequentie ω, verbeterd
door het netwerk, plus de anharmonische verschuiving Δ_anh uit DFT. Voor Δ_anh is niveau G gekozen
(B3LYP/6-31G*). Een grotere basisset veranderde alleen de kwartische constanten van de trillingen
uit het vlak, en bracht die verder van CCSD(T) af. De pijplijn rekent nu nog harmonisch; de
anharmonische stap is in aanbouw.

## §2.5 Resonanties

Soms ligt de frequentie van één mode toevallig heel dicht bij die van een combinatie van
twee andere (bijvoorbeeld 2 × 1500 ≈ 3000). Dan "praten" die toestanden met elkaar en
verschuift én splitst de band. Dat heet een **Fermi-resonantie**. Bij PAK's is de
C–H-strekregio er berucht om: er liggen zoveel combinatiebanden dat de gewone
storingsrekening het opgeeft.

Het plan heeft hier vooraf regels voor, overgenomen uit plan 04: een resonantie wordt
herkend met vaste drempels, de betrokken toestanden worden samen behandeld, en als dat te
veel worden (een "polyad-cap") wordt de C–H-strekfamilie op die rung **niet gescoord** in
plaats van fout gescoord. De verzameling modes die samen moeten worden behandeld heet de
"resonantie-gesloten familieset"; die wordt tot één stap diep gesloten (de partners van
een gescoorde mode doen mee, de partners van de partners niet). Die regels horen bij de
anharmonische stap: een harmonisch spectrum kent geen resonanties.

## §2.6 Temperatuur: warme banden

Bij kamertemperatuur zitten de meeste moleculen in hun laagste trillingstoestand, maar
niet allemaal: laagfrequente modes (rond 200–400 cm⁻¹) zijn al voor een deel aangeslagen.
Een molecuul dat al in een lage mode trilt, absorbeert bij een iets *andere* frequentie
voor een hoge mode, omdat de anharmoniciteit de modes koppelt. Het gevolg: een band
verschuift (bijna altijd naar lagere frequentie) en verbreedt naarmate het monster warmer
is. Dat heet een **hot band**-verschuiving.

Dit is geen bijzaak voor het plan. Veel openbare gasfasespectra van PAK's zijn gemeten in
hete damp (245 °C voor naftaleen in één databank; rond 250 °C in de GC-IR-bibliotheek die
voor pyreen wordt gebruikt), terwijl de berekening een koud molecuul beschrijft. De gemeten
verschuiving ligt tussen ongeveer 0,01 en 0,05 cm⁻¹ per kelvin, afhankelijk van de band (Joblin
e.a. 1995). Over ruim 200 graden is dat 2 tot 10 cm⁻¹: net zo groot als het effect dat het plan
wil aantonen. Hoofdstuk 8 legt uit hoe het plan hiermee
omgaat (een temperatuurterm in de meetonzekerheid, en de voorkeur voor spectra bij
kamertemperatuur, die voor benzeen en naftaleen blijken te bestaan).

## §2.7 Gas en matrix

Labspectra van PAK's bestaan in twee soorten. **Gasfase**: het molecuul zweeft vrij; dat is
wat de berekening beschrijft. **Matrixisolatie**: het molecuul zit bij ongeveer 10 K
ingevroren in vast argon; dat is koud en scherp, maar de omringende argonatomen verschuiven
de banden een paar cm⁻¹. Voor grotere PAK's bestaan vaak alleen matrixspectra.

Het plan behandelt die twee verschillend. Gasfasedata mag direct worden vergeleken, met
de gemeten onzekerheid u_band. Matrixdata mag alleen worden gebruikt als module 03 eerst
heeft gemeten hoe groot de matrixverschuiving per familie is, en alleen voor families
waar die verschuiving kleiner is dan de te winnen marge. Anders wordt de vergelijking
vooraf "onbeslisbaar op matrix" verklaard.

## In het kort

Een molecuul met N atomen heeft M = 3N − 6 normale trillingen, elk met een frequentie die
uit de veerconstanten volgt. Alle veerconstanten samen vormen de Hessiaan; wie de Hessiaan
goed heeft, heeft de harmonische bandposities goed. Plan 05 corrigeert de Hessiaan met
een geleerde correctie (Δ₂, in het product ΔH) en laat de anharmonische correctie aan de goedkope
methode over; die stap is nog niet in de pijplijn. Het netwerk en de licentie werken met vier
families: CH-stretch, ring-ip, CH-oop en 'other'. Resonanties worden met vaste regels behandeld of eerlijk niet gescoord.
Temperatuur verschuift banden met een paar cm⁻¹, dus de temperatuur van het labspectrum
telt mee in de onzekerheid; gas en matrix worden verschillend behandeld.

*Bron: [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) (methode-skelet),
[Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md) §2
(beslisbaarheid, temperatuurterm) en §3 (resonantiesluiting, Δ₂-only),
[Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) §3; besluiten 11 en
49 in de [README](../README.md); de familieregel in `m05/learning_curve_layerA.py`; de anharmonische stap in `../TASKS.md` (taak 53);
de temperatuurhellingen in de Ladder §2 (item 52 van de literatuurlijst).*
