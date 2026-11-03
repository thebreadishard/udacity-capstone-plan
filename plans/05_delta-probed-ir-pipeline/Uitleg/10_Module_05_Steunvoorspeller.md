# Hoofdstuk 10 — Module 05: de ΔH-voorspeller (de "steunvoorspeller")

*Udacity-module "Deep Learning Systems". In de rubriek Project 4. De bijnaam in de bestandsnaam komt uit het eerste ontwerp, waarin het
netwerk alleen voorspelde wélke elementen van de correctie groot zijn (de "steun", Engels: support). Het netwerk voorspelt nu de correctie
zelf.*

---

## 1. Wat is de vraag?

Kan een neuraal netwerk uit de goedkope berekening van een molecuul voorspellen hoe de krachtmatrix van dat molecuul (de Hessiaan,
[hoofdstuk 4](04_Wiskunde_Gereedschap.md)) gecorrigeerd moet worden naar een betere berekening, zo nauwkeurig dat de trillingsfrequenties
in elke bandfamilie binnen 3 cm⁻¹ kloppen, ook bij moleculen die het netwerk nooit heeft gezien?

Die correctie heet ΔH: de betere Hessiaan min de goedkope. Het netwerk dat haar voorspelt heet in alle teksten van het project het
**ΔH-netwerk**. Het is het hart van het eindproduct: de pijplijn van module 08 ([hoofdstuk 13](13_Module_08_Synthese.md)) telt de
voorspelde ΔH op bij de goedkope Hessiaan en rekent daaruit het spectrum.

## 2. Wat eist de school?

Een deep-learning-experiment in PyTorch: een probleemdomein kiezen (**beeld, tekst of reeks**), een model uit de familie **CNN, RNN of
Transformer**, een baseline trainen, en **precies één** ding veranderen voor een gecontroleerde vergelijking ("zeg wat er veranderde en wat
gelijk bleef"). Beide modellen evalueren, met leercurves. "Hoge nauwkeurigheid is niet vereist." De dataset moet openbaar zijn vóór de
module, niet synthetisch of AI-gegenereerd, en **niet hergebruikt uit een eerdere capstone-module**; samengestelde echte datasets zijn
toegestaan. Het rapport moet een ethiek-paragraaf hebben en het notebook een samenvatting van 4–6 zinnen.

## 3. Invoer — de datastructuur in detail

**Het corpus: zelf berekend, in lagen.** Een neuraal netwerk leert van voorbeelden, en voor deze taak bestond geen geschikte openbare
verzameling. De openbare databank Hessian QM9 is wel gedownload en geteld, maar bevat moleculen van hooguit negen zware atomen en vrijwel
geen aromatische ringen; ze zit daarom niet in de dataset. Het project rekent zijn voorbeelden zelf uit met een **corpusfabriek**. Voor elk
molecuul optimaliseert die de geometrie met B3LYP/6-31G\* en rekent ze op precies die geometrie twee Hessianen uit: één met B3LYP en één met
ωB97X. Dat zijn twee DFT-methoden ([hoofdstuk 3](03_Scheikunde_DFT_en_Coupled_Cluster.md)) met een sterk verschillend aandeel exacte
uitwisseling. Hun verschil ΔH = H(ωB97X) − H(B3LYP) is de **plaatsvervanger** (proxy) van de echte correctie, coupled cluster min DFT. Het
heeft dezelfde soort structuur als het echte verschil, maar kost een fractie. Het corpus (object O11 van [hoofdstuk 6](06_Datastructuren_en_Pijplijn.md)) telt 1.236 moleculen in vijf lagen:

| Laag | Wat | Waarom | Aantal |
|---|---|---|---|
| A | met de hand gekozen aromaten, van benzeen tot pyreen, met varianten waarin een stikstof- of zuurstofatoom in de ring zit | de ouders: de kale kernen die het meest op de grote PAK's lijken | 46 |
| A2 | grote kernen (drie en vier ringen) met één zijgroep uit een vaste lijst van vijftien (CH₃, OH, NH₂, F, Cl, CN, …) | een handvol skeletten leert geen regel; honderden omgevingen wel | 327 |
| B | kleine aromatische en heteroaromatische kernen (benzeen, pyridine, thiofeen, indool, chinoline, …) met zijgroepen, tot 26 atomen | de breedte: veel chemische omgevingen voor weinig rekentijd | 743 |
| P3 | pool 3: aromaten van vier ringen met stikstof in de ring, en aromaten van vijf ringen | twee assen die het corpus nog miste: stikstof in grote ringen en grootte | 60 |
| P3c | radicaalkationen (een molecuul met één elektron minder, dus één positieve lading) op bekende skeletten | geladen PAK's komen veel voor in de ruimte en hebben een ander spectrum | 60 |

Elk molecuul heeft een eigen map (object O2) met de geometrie, de twee Hessianen en een resultaatrecord; bij een deel van de moleculen staat er ook de
APT bij, de tabel waaruit de hoogte van elke band volgt. Het netwerk van dit hoofdstuk (versie 1.3, §4) is getraind op de lagen A, A2 en B;
de lagen P3 en P3c zijn er voor de volgende versie.

**Twee routes, één regel.** Psi4 rekent een Hessiaan uit eindige verschillen van gradiënten ([hoofdstuk 4](04_Wiskunde_Gereedschap.md)), en
dat geeft ruis. In de ωB97X-Hessiaan van benzeen zat een fout tot 133 cm⁻¹ die niets met de chemie te maken had: het rekenrooster van psi4
was te grof voor de kleine stapgrootte. Daarom geldt de regel dat elke verdachte Hessiaan een **tweede route** krijgt (besluit 50): een
analytische Hessiaan uit pyscf, exact afgeleid in plaats van uit kleine stapjes geschat. Voor 862 moleculen staat zo'n analytische Hessiaan
klaar, en de training gebruikt die waar ze bestaat. Analytische labels veranderen het niveau van de leerstof niet; ze halen er de meetruis
uit (besluit 60).

**De vorm per molecuul, zoals het netwerk hem ziet:**

| Onderdeel | Type | Betekenis |
|---|---|---|
| atomen | lijst van N records | atoomsoort en plaats (x, y, z) in de B3LYP-geometrie |
| goedkope Hessiaan | per atoompaar drie getallen | de B3LYP-krachtmatrix, geschreven als getallen die niet veranderen als je het molecuul draait |
| interne coördinaten | lijst | de rek van elke binding, de buiging van elke hoek, de verdraaiing om elke binding |
| doel ΔH | matrix 3N × 3N | het verschil ωB97X − B3LYP, in de eenheden van de Hessiaan |
| familie per trilling | label | C–H-strek, ring-in-het-vlak, C–H-uit-het-vlak of "overig"; alleen voor de beoordeling |

**De toetsverzamelingen.** Een netwerk toets je op moleculen die het nooit zag. Zo'n achtergehouden verzameling heet een *hold-out*. Module 05
heeft er twee, en geen van beide komt ooit in de training:

- **Hold-out (a)**: tien ouders uit laag A. Ze lijken het meest op de grote PAK's waar het product voor bedoeld is.
- **Hold-out (b)**: 69 moleculen op twee skeletten, fluorantheen en fluoreen. Van die skeletten zit geen enkel molecuul in de training, dus
  hier moet het netwerk oordelen over ringsystemen die het nooit zag.

Wat overblijft, vormt de pool: 972 moleculen waaruit versie 1.3 er 750 trekt. Van die 750 gaat 15 % naar een *validatieset*: moleculen
waarop het netwerk tijdens de training niet leert, maar waarop gemeten wordt wanneer het moet stoppen (§4).

**Probleemdomein en modelfamilie, expliciet verklaard.** Het ingeleverde notebook gebruikt het domein **reeks**: een molecuul als reeks van
trillingstokens, één per DFT-trilling, met frequentie, familie en omgevingskenmerken. Het model is een **Transformer**: een netwerk dat elk
token laat "kijken" naar alle andere tokens, de plek waar de vraag "zijn trillingen i en j gekoppeld?" leeft. Het notebook traint op een
bevroren uitgave van 224 moleculen uit de lagen A en A2. Dat is de baseline van de school. Het ΔH-netwerk van het eindproduct is de opvolger
ervan, en §6 legt uit waarom het er anders uitziet.

**Wat er niet in zit.** Geen labdata. Laboratorium- en sterrenkundige spectra zijn de buitenste controle van de hele keten, nooit
trainings-, validatie- of stopinvoer.

## 4. Bewerking

**De gecontroleerde vergelijking van het notebook.** De baseline is een Transformer van twee lagen (135.939 parameters); de ene verandering is
vier lagen (235.907 parameters), al het andere gelijk. Beide worden met drie *zaadjes* getraind: drie trainingsruns die alleen verschillen in
het toeval waarmee ze beginnen, zodat je de spreiding ziet. Twee regels zonder netwerk dienen als tegenstander: "geen correctie" en "de
mediaan van de familie in de trainingsset". Zo heeft elk getal een betekenis.

**Het ΔH-netwerk, versie 1.3.** Dit is het netwerk dat de pijplijn gebruikt. [Hoofdstuk 5](05_De_Kern_Delta_Probing.md) (§5.5) volgt het stap voor
stap; hier staat wat de module bouwt en traint. Het netwerk bestaat uit twee delen.

- **Het lichaam** (`m05/rungC_equivariant.py`) is een *equivariant* netwerk. Equivariant betekent: draai je het molecuul in de ruimte, dan
  draaien alle tussenresultaten precies mee. Het netwerk hoeft dat dus niet uit voorbeelden te leren; het zit in de bouw. Het lichaam stuurt
  in drie rondes berichten tussen atomen die binnen 5 Å van elkaar liggen. Na die rondes heeft elk atoom een beschrijving van 64 getallen en
  64 pijltjes van zijn eigen omgeving.
- **De kop** (`m05/rungC_hybrid.py`) zet die beschrijvingen om in de correctie. Hij voorspelt één getal per paar interne coördinaten, en
  alleen voor paren die dicht bij elkaar liggen: dezelfde coördinaat, paren die een atoom delen, paren binnen een ring en hun naaste buren.
  Dat getal hangt af van de beschrijvingen van de betrokken atomen, van het soort paar en van de goedkope krachtconstante van dat paar. Een
  deel van de voorspelling is een factor maal die goedkope krachtconstante, met één factor per soort paar; het netwerk leert alleen wat
  daarna overblijft. De correctie in interne coördinaten wordt met de Wilson-matrix B omgezet naar de Hessiaan: ΔH = Bᵀ ΔF B. Die omzetting is
  vaste wiskunde en maakt ΔH vanzelf symmetrisch.

Samen hebben lichaam en kop 172.194 instelbare getallen. De training (`m05/rungC_train.py`) gebruikt 750 moleculen met analytische labels
waar die er zijn. De verliesfunctie, het getal dat de training zo klein mogelijk maakt, bevat naast de fout op ΔH een term die de vier
families even zwaar laat tellen, zodat de kleine familie "overig" niet ondersneeuwt.

**Stoppen op tijd (besluit 51).** Elke training in het project houdt een validatieset achter en stopt als de fout daarop twintig rondes lang
niet meer daalt, met een plafond van 200 rondes. Daarna wordt de beste toestand teruggezet en wordt de beste ronde naast het plafond
opgeschreven. Ligt de beste ronde binnen tien procent van het plafond, dan telt de run niet als resultaat en wordt hij opnieuw gedaan met een
hoger plafond. Zonder die regel leert een netwerk de trainingsvoorbeelden uit het hoofd, of het stopt voordat het klaar is.

**Drie zaadjes, één versie (besluiten 55, 57 en 59).** Elk opgeslagen netwerk staat met zijn recept, zijn toetsgetallen en een status in een
register (`modules/05_support_predictor/MODELS.md`, object O15). Een versienummer hoort bij een recept: versie 1.3 zijn drie
netwerken met hetzelfde recept, en de pijplijn neemt het gemiddelde van hun drie voorspellingen. Werk wordt alleen gedaan met een versie die
*gedragen* is: een versie waar het project tevreden over is. Een nieuwe versie wordt alleen gedragen als ze op geen van vijf getallen slechter
is dan de vorige, op geen van beide hold-outs, en op minstens één beter. Die vijf getallen zijn de fout van elk van de vier families en de
koppelingsratio (punt 5 van dit hoofdstuk). Versie 1.3 haalde dat: op 9 van de 10 getallen beter dan versie 1.1, op geen slechter. Een volgende versie, 1.4, is
vooraf vastgelegd en neemt ook de kationen en pool 3 mee.

**Hoe je weet dat het netwerk echt leert.** Een netwerk dat op zijn trainingsvoorbeelden goed scoort, heeft nog niets bewezen. Een leerling
die de antwoorden van het oefenexamen uit zijn hoofd kent, heeft ook geen wiskunde geleerd. Het project gebruikt drie soorten bewijs.

1. *Toetsen op wat het nooit zag, steeds moeilijker.* Een paar moleculen achterhouden is makkelijk. Een heel skelet achterhouden is moeilijker:
   dat is hold-out (b). Het moeilijkst is *groter*: leren van kleine moleculen en toetsen op grotere, want de PAK's in de ruimte zijn groter
   dan alles wat het corpus bevat. Die toets, op moleculen voorbij de maat van het corpus, loopt nog.
2. *De leercurve.* Geef het netwerk bijvoorbeeld 100, 300 en 750 voorbeelden en zet de fout uit tegen het aantal. Bij echt leren daalt die lijn; bij uit het
   hoofd leren blijft ze vlak, want elk nieuw voorbeeld vertelt dan niets over het volgende.
3. *Controles die moeten mislukken.* Schud de antwoorden door elkaar, zodat elk molecuul de correctie van een ander krijgt, en train opnieuw.
   Dan moet het netwerk verliezen wat het met de echte antwoorden won, en dat doet het. Daarnaast is er de *ruisvloer*: een netwerk kan niet
   nauwkeuriger worden dan zijn leerstof. Met de eindige-verschillen-labels lag die vloer voor de C–H-uit-het-vlak-familie op 3,3 cm⁻¹, vlak
   bij de doelwaarde zelf; daarom traint versie 1.3 op analytische labels.

**De meting.** De fout wordt gemeten op de frequenties, de grootheid waar het spectrum om draait. De gecorrigeerde
Hessiaan wordt opgelost tot trillingen, en per familie wordt de rms-fout van de frequenties berekend tegen de ωB97X-waarheid. Rms is de
wortel uit het gemiddelde van de gekwadrateerde fouten, in cm⁻¹. Elk getal is het gemiddelde over de drie zaadjes.

**Van de plaatsvervanger naar coupled cluster.** De proxy leert het netwerk de *vorm* van de correctie op duizend moleculen. Wat "juist" is,
bepalen de coupled-cluster-ankers: moleculen waarvan het project een CCSD(T)-Hessiaan heeft ([hoofdstuk 3](03_Scheikunde_DFT_en_Coupled_Cluster.md)).
Dat zijn de lagen van waarheid van besluit 60: B3LYP is de invoer, ωB97X de opstap, CCSD(T) de ijking en het lab de buitenste controle
([hoofdstuk 5](05_De_Kern_Delta_Probing.md), §5.6 en §5.8).

- *De ankers.* Het register (`modules/ANCHORS.md`, object O14, besluit 62) bevat elf gedragen ankers: acenaftyleen, antraceen, azuleen, benzeen,
  benzonitril, fluorbenzeen, isochinoline, naftaleen, pyridine, chinoline en chinoxaline. De standaard is CCSD(T) in de basisset cc-pVDZ,
  plus een correctie voor de stap naar de grotere basisset cc-pVTZ die met de goedkopere methode MP2 is berekend; benzeen is volledig met
  CCSD(T)/cc-pVTZ gerekend. Niets wordt overschreven: een betere versie van een anker is een nieuwe regel, de oude wordt "vervangen". Elk
  anker krijgt twee onafhankelijke controles (besluit 61), omdat een berekening die er goed uitziet toch fout kan zijn.
- *De overdracht.* Het netwerk wordt op de ankers bijgesteld: het lichaam blijft vast, de kop leert verder op de CC-correctie. Getoetst wordt
  steeds op een anker dat bij het bijstellen buiten bleef. Bijstellen van alleen de laatste laag van de kop bleek te weinig: die kon de
  correctie uit het vlak zelfs op de eigen ankers niet volgen. Met de hele kop halveerde de fout op het achtergehouden anker: C–H-uit-het-vlak
  van 12,3 naar 6,5 cm⁻¹, gemeten op versie 1.1 met zes ankers. In de vastgelegde herhaling met de vijf nieuwe ankers erbij daalde die
  familie van 7,2 naar 6,3 cm⁻¹, en de bandhoogtes van de drie minst symmetrische ankers kwamen dichter bij CCSD(T) dan zonder correctie. De doelwaarde van 3 cm⁻¹ op
  CC-niveau is daarmee niet gehaald, en het project claimt haar niet.
- *Het aantal ankers.* Hoeveel ankers een familie nodig heeft, is op de proxy nagespeeld: een netwerk dat een opzettelijk andere correctie leerde, die het niveau
  en de samenhang van de echte CC-correctie nabootst, wordt met k moleculen met de ware correctie bijgesteld. Ring-in-het-vlak en C–H-strek
  halen 3 cm⁻¹ bij 100 moleculen, C–H-uit-het-vlak bij ongeveer 167, en "overig" niet binnen 200.
- *De grens van de capstone (besluit 63).* De capstone eindigt met het bewijs op de proxy: de pijplijn staat, de correctie per familie is
  geleerd en getoetst met twee DFT-methoden, en de bestaande ankers vormen de brug naar coupled cluster. Nieuwe ankers vallen buiten de
  capstone tot juli 2027.

## 5. Uitvoer — de datastructuur in detail

**Het netwerk.** Drie opgeslagen netwerken van versie 1.3, elk met zijn recept, zijn toetsgetallen en de commit waarmee het gemaakt is, in
het register. De pijplijn laadt ze, laat ze alle drie ΔH voorspellen en telt het gemiddelde op bij de B3LYP-Hessiaan; die voorspelde correctie is
object O4 van [hoofdstuk 6](06_Datastructuren_en_Pijplijn.md).

**De fout per familie en de vrijgave (besluit 65).** Een familie is *vrijgegeven* als de gemiddelde fout van de gedragen versie op beide
hold-outs binnen 3 cm⁻¹ blijft. De vrijgave volgt dus elke nieuwe versie. Voor versie 1.3, in cm⁻¹, met "geen correctie" ter vergelijking
(over alle trillingen samen 23,4 op (a) en 23,0 op (b)):

| familie | hold-out (a), de acht schone moleculen | hold-out (b) | vrijgegeven |
|---|---|---|---|
| ring-in-het-vlak | 1,77 | 2,12 | ja |
| C–H-strek | 1,19 | 2,50 | ja |
| C–H-uit-het-vlak | 2,17 | 2,70 | ja |
| overig | 3,62 | 3,89 | nee |

Twee van de tien moleculen van hold-out (a) bleken als tweeling in laag B toch in de training te zitten (punt 6 van dit hoofdstuk). De
vrijgave en het certificaat van de pijplijn lezen daarom de acht schone moleculen. Met de twee lekken erbij lag elke familie 0,04 tot
0,27 cm⁻¹ lager; de vrijgave is voor geen enkele familie anders. [Hoofdstuk 5](05_De_Kern_Delta_Probing.md) (§5.7) zet deze getallen naast de rest van
het plan.

Naast de frequenties is er de **koppelingsratio**: de fout op de koppelingen tussen ringtrillingen gedeeld door de fout van "geen correctie".
Voor versie 1.3 is die 0,17 op de oorspronkelijke tien moleculen van (a) en 0,26 op (b). Een ratio van 1 zou betekenen dat het netwerk niets aan de koppelingen heeft geleerd.

De vrijgave geldt op het niveau waarop het netwerk gemeten is, de proxy ωB97X. Een vrijgave op coupled-cluster-niveau bestaat niet. Het
certificaat van de pijplijn markeert per band of zijn familie vrijgegeven is en of het netwerk het molecuul in de training heeft gezien.

**Het ingeleverde notebook.** De hoofdrun van het notebook geeft per familie de fout van de voorspelde bandverschuiving op de testset, in
cm⁻¹, gemiddeld over drie zaadjes:

| model | C–H-strek | C–H-uit-het-vlak | ring-in-het-vlak | overig |
|---|---|---|---|---|
| geen correctie | 43,78 | 24,08 | 20,34 | 19,23 |
| mediaan van de familie | 2,71 | 8,12 | 15,64 | 14,53 |
| baseline (twee lagen) | 3,18 | 4,05 | 5,46 | 8,30 |
| vier lagen | 2,61 | 4,03 | 5,22 | 8,58 |

De verschuivingen worden geleerd: vier tot zes keer beter dan "geen correctie" in de families uit het vlak en van de ring. De koppelingen in
deze basis leert geen enkel model; elk model zit daar op "geen correctie". De extra lagen veranderen niets buiten de spreiding van de
zaadjes. Dat is de eerlijke uitkomst van het ingeleverde experiment, en de aangevulde secties van het notebook laten zien wat het project
er daarna uit leerde.

**Verder:** het rapport met de vereiste zinnen (het corpus is eigen berekende ab-initiodata, niet AI-gegenereerd, in geen eerdere module
gebruikt; het lab is nooit trainings-, validatie- of stopinvoer), `requirements.txt`, en de corpusuitgaven met een controlesom per bestand.
De data zijn openbaar in de GitHub-repository van het plan; een Zenodo-uitgave met DOI is in voorbereiding.

## 6. Waarom deze module?

Zonder module 05 heeft de pijplijn alleen de goedkope tegenstander van module 04: B3LYP-frequenties met een schaalfactor
([hoofdstuk 9](09_Module_04_Baseline.md)). Op de hold-outs zitten de B3LYP-frequenties zonder correctie 23 cm⁻¹ (rms) naast de
ωB97X-waarheid; met het ΔH-netwerk 2 tot 3 cm⁻¹. Het netwerk is het enige
deel van de pijplijn dat iets *leert*, en het is het deel waar de vernieuwing van het plan zit: een correctie die per familie gemeten,
vrijgegeven en later met weinig coupled-cluster-ankers geijkt kan worden.

**Wat de module het project leerde.** Het ingeleverde experiment liet zien wat niet werkte. De lessen daarna bepaalden hoe het ΔH-netwerk
eruitziet.

- **De taal van de correctie.** In de basis van de trillingen leerde geen enkel model de koppelingen: de leercurve bleef vlak bij 45, 100 en
  175 moleculen. De reden is wiskundig. Een trilling is een richting zonder vast teken: draai je hem om, dan wisselt de koppeling van teken
  zonder dat een kenmerk van de trilling dat verraadt. Het label per trillingspaar is dus slecht gedefinieerd. Schrijf je dezelfde correctie
  op in de taal van bindingen en hoeken (interne coördinaten), dan is elk element tekenvast en lokaal. Op dezelfde 175 moleculen leerde een
  eenvoudig paarmodel de koppelingen dan wél: ratio 0,43 en 0,47 op de twee hold-outs, gecorrigeerde frequenties 4,7 en 5,1 cm⁻¹ tegen 23
  zonder correctie. Sindsdien worden koppelingen in interne coördinaten geleerd (besluit 49; [hoofdstuk 5](05_De_Kern_Delta_Probing.md), §5.4).
- **De correctie is lokaal, drie keer gemeten.** Driekwart van ΔH zit in paren die een atoom delen of in dezelfde ring liggen. De echte
  coupled-cluster-correctie van benzeen zit voor 98 % in datzelfde patroon, één binding verder. En de correctie van een molecuul met een
  zijgroep is het blok van zijn moederkern plus de buurt van de zijgroep: een kwart van de kolommen van de Hessiaan geeft de gecorrigeerde
  frequenties tot op 1,7 cm⁻¹ terug. Daarom kijkt de kop van het netwerk alleen naar paren die dicht bij elkaar liggen.
- **Een meting die niets mat.** Een symmetrietoets leek te zeggen dat het paarmodel spiegelbeeldparen verschillend behandelde. De meetlat
  deelde paren echter in naar atoomsoort, niet naar ligging; in benzeen zaten ortho-, meta- en paraparen in één klasse, en hun verschil is
  echte natuurkunde. Dezelfde meetlat langs het doel gaf hetzelfde getal. Het paarmodel geeft spiegelbeeldparen vanzelf hetzelfde antwoord,
  want zijn kenmerken veranderen niet onder een spiegeling. Symmetrie zat dus ingebouwd, en de toets kon ingebouwd en geleerd niet uit
  elkaar houden. Wat bleef staan: het paarmodel kent geen richtingen, en een correctie van de volledige krachtmatrix in de ruimte heeft die
  wel. Daarom is het lichaam van het ΔH-netwerk equivariant. De les: leg een meetlat eerst langs het doel, dan pas langs het model.
- **Een vloer die van onszelf was.** Een week lang bleef elke variant van de kop op dezelfde fout steken. De oorzaak lag bij het doel:
  een hulpterm in de verliesfunctie mikte op een grootheid die de kop door zijn bouw nooit kon bereiken. Met een doel dat binnen het bereik
  van de kop ligt, een kleinste-kwadratenpassing op het patroon, verdween de vloer, en de fout op de ringkoppelingen zakte naar een ratio van
  0,22. De les: controleer of een doel bereikbaar is voordat je een plateau als grens van het model leest.
- **Ruis in de leerstof.** De fout van 133 cm⁻¹ in de benzeen-Hessiaan leidde tot de tweede route. Later bleek de ruis van de
  eindige-verschillen-labels in de familie uit het vlak 3,3 cm⁻¹ te zijn, vlak bij de doelwaarde. Op analytische labels daalde de fout van die
  familie op de oorspronkelijke tien van hold-out (a) van 2,36 naar 1,99 cm⁻¹, met hetzelfde recept.
- **Dekking per familie van skeletten.** Haal je alle 130 moleculen met drie ringen uit de pool, dan stijgt de fout op ongeziene ouders met
  drie ringen van 0,15 naar 0,5. Zet je ze in stappen terug (0, 31, 62, 123 kinderen), dan zakt die naar 0,45, 0,22, 0,17 en 0,15. De eerste
  dertig kinderen van een familie leveren driekwart van de winst, zestig bijna alles. Dat is de regel voor elke nieuwe pool (besluit 52):
  eerst elke familie dertig, dan zestig waar de beste nauwkeurigheid nodig is.
- **Een toets die niet schoon was.** Twee moleculen van hold-out (a), 2-naftoëzuur en benzonitril, stonden ook in laag B, onder een tweede
  code, en kwamen zo in de training. Een controle in de pijplijn die vraagt of het netwerk een molecuul al heeft gezien, vond ze. De trainer laat
  zulke tweelingen nu standaard weg, en een toets op een verzameling met een tweeling wordt geweigerd.
- **Alleen gedragen versies.** Een resultaat van een verkeerde netwerkversie kan het project van zijn pad brengen. Daarom weigeren de
  programma's die een netwerk laden elke versie die niet gedragen is, tenzij die uitzondering met naam in het record staat (besluit 55).
- **Het plafond van de hoofdrun.** In de hoofdrun van het notebook lagen de beste rondes tegen het plafond
  van 30. Opnieuw getraind met een plafond van 100 lagen de beste rondes tussen 25 en 45, en de testfouten binnen 0,9 cm⁻¹ van de eerste run:
  het plafond begrensde het aantal rondes, de getallen nauwelijks. Daaruit kwam de stopregel van §4 voor elke lerende module.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De herbruikclausule.** Het corpus is eigen berekende data, in geen eerdere module gebruikt. Controleer dat het rapport dat zegt, en dat
  het naar de uitgave verwijst die er bij inlevering is (de GitHub-repository, of de Zenodo-DOI als die er dan is).
- **Domein en familie letterlijk.** "Reeks" en "Transformer" met zoveel woorden, en de ene verandering (twee naar vier lagen) in het recept
  vóór het trainen.
- **Notebook en eindproduct uit elkaar houden.** Het ingeleverde experiment is de Transformer in de trillingsbasis; het netwerk van de
  pijplijn is het equivariante ΔH-netwerk. Controleer dat het rapport zegt welk getal bij welk netwerk hoort, en dat een getal over "het
  netwerk" de gedragen versie noemt.
- **Ruis in de labels.** Elke uitgave meldt welke Hessianen langs de tweede route zijn vervangen en waarom. Controleer dat de uitgave van
  het notebook overeenkomt met de uitgave in de provenance.
- **Append-only eerlijk.** Het notebook bewaart de hoofdrun zoals die gedraaid is; latere secties zijn eraan toegevoegd zonder de eerdere
  cellen opnieuw te draaien. Cellen die niet opnieuw gedraaid zijn, mogen ook niet opnieuw *geschreven* zijn. Eén keer overschreef een
  uitvoerhulpje per ongeluk twee zware cellen met hun definitie; dat is hersteld uit de vorige commit en in de provenance opgeschreven.
  Controleer dat de trainingscellen uitvoer en een uitvoernummer hebben.
- **De vrijgave is geen CC-vrijgave.** De 3 cm⁻¹ geldt op de proxy. Controleer dat geen tekst een familie "vrijgegeven" noemt zonder dat
  niveau, en dat "overig" nergens als vrijgegeven staat.
- **Hold-outs schoon houden.** Een molecuul kan onder twee namen in het corpus staan. Controleer dat de toetsgetallen uit een run komen
  waarin de trainer de tweelingen heeft weggelaten.

## 8. In het kort

Module 05 traint het ΔH-netwerk: een equivariant lichaam en een kop die per paar nabije interne coördinaten één correctiegetal voorspelt.
Het leert op een eigen corpus van 1.236 moleculen in vijf lagen het verschil tussen ωB97X en B3LYP. Versie 1.3, drie zaadjes op 750
moleculen met vroeg stoppen, brengt de frequenties van 23 cm⁻¹ fout naar 2 tot 3. Ring-in-het-vlak, C–H-strek en C–H-uit-het-vlak zijn
vrijgegeven op beide hold-outs; "overig" niet. De elf coupled-cluster-ankers vormen de brug naar het echte niveau, waar de doelwaarde nog
niet gehaald is. Onderweg leerde de module dat de correctie lokaal is en in bindingen en hoeken geleerd moet worden, dat een meetlat eerst
langs het doel moet, en dat een toets alleen telt als hij schoon is.

*Bron: `modules/05_support_predictor/README.md`, `modules/MODELS.md`, `modules/05_support_predictor/MODELS.md`, `modules/ANCHORS.md`,
`modules/PIPELINE.md`; besluiten 49–63 en 65 in de [README van plan 05](../README.md); de leesrecords
`modules/05_support_predictor/out/E7_rungC_chain35_read.md`, `holdout_a_clean_read_2026-10-30.md` en
`anchor_count_2026-10-29/anchor_count_read.md`; `GoalGathering/notes/Diagnosis_2026-10-21_Set_Three_Read.md`; de rubriek
[Rubrics/05](../../../Rubrics/05_Deep_Learning_Systems.md).*
