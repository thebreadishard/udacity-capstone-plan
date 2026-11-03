# Hoofdstuk 11 — Module 06: de kandidatenvoorsteller

*Udacity-module "Generative AI Applications". In de rubriek Project 5.*

---

## 1. Wat is de vraag?

Kan een klein generatief model nieuwe aromatische moleculen voorstellen die lijken op wat er bestaat, maar er niet in staan — zodat de
pijplijn van plan 05 weet **welke moleculen ze als volgende kan doorrekenen**, binnen het soort moleculen waarop haar geleerde correctie
getraind is?

Dat is een andere vraag dan de rest van het plan stelt. Modules 02 tot 05 gaan over *hoe goed* een spectrum wordt; module 06 gaat over
*waarvan* je er een wilt. De Spectrum Atlas (de website van het project) toont de moleculen van het corpus met hun spectrum en hun status;
module 06 is een bron van nieuwe kandidaten, duidelijk gelabeld als "voorgesteld door een model", nooit als data. Het model heet in de teksten
van het project de **kandidatengenerator**. Het staat buiten de pijplijn en heeft daarom een versienummer onder 1 (0.1 en 0.2, besluit 59).

## 2. Wat eist de school?

Een klein generatief systeem: een taak en dataset kiezen; een **GAN, VAE of Transformer-generator** implementeren en trainen (diffusie hoeft
niet); voorbeelden genereren; de kwaliteit beoordelen met sterke en zwakke gevallen uit eigen uitvoer; een rapport met minstens één ethische
overweging die aan *deze* data en *dit* model is gebonden. De dataset moet openbaar of duidelijk gedocumenteerd zijn, niet synthetisch of
AI-gegenereerd, en niet hergebruikt uit een eerdere module. Gegenereerde uitvoer telt nooit als dataset.

## 3. Invoer — de datastructuur in detail

**De bevroren PubChem-set.** Uit PubChem, de openbare moleculendatabank van de Amerikaanse National Institutes of Health, zijn alle moleculen
opgehaald die een van negen aromatische kernen van twee versmolten ringen bevatten: naftaleen, chinoline, isochinoline, indool, benzofuraan,
benzothiofeen, chinoxaline, benzimidazool en azuleen. Dat waren er 404.877. Daarna is gefilterd: neutraal, alleen de elementen C, H, N, O,
S, F en Cl, hooguit 30 zware atomen, geen isotopen, en minstens twee **versmolten** aromatische ringen (ringen die een zijde delen, zoals in
naftaleen). Na het verwijderen van dubbele moleculen bleven er 160.972 over, elk als één regel:

| Veld | Type | Betekenis |
|---|---|---|
| cid | getal | het PubChem-nummer, de sleutel naar het openbare record |
| smiles | tekst | de molecuulstructuur als tekenreeks (§4 legt uit wat dat is) |
| formule, aantal zware atomen, aantal aromatische ringen | tekst, getal, getal | voor de statistiek en voor de conditie-tokens |
| kernen | lijst | welke van de negen zoekkernen het molecuul bevat |

De **splitsing per skelet** is het belangrijkste ontwerpbesluit van de invoer. Het skelet (Murcko-skelet) is het molecuul zonder zijn
zijgroepen. Wie willekeurig splitst, laat het model op de testset moleculen zien die bijna gelijk zijn aan trainingsmoleculen (dezelfde kern,
één andere zijgroep), en "nieuw" betekent dan niets. Hier gaan alle moleculen met hetzelfde skelet naar dezelfde groep, via een hash van het
skelet ([hoofdstuk 4](04_Wiskunde_Gereedschap.md)), dus reproduceerbaar op elke machine. De verdeling is 80 / 10 / 10 %: 125.065
trainingsmoleculen, 15.434 voor validatie en 20.473 voor de test.

**Wat er niet in zit.** Geen spectra, geen berekeningen van dit project, geen labdata. De set staat los van modules 02 tot 05. Ze heeft een
eigen README met de zoekvraag, de filters, de aantallen na elke stap en de SHA-256-controlesom van het bestand, en het bestand zelf staat in
de repository van de module. PubChem is publiek domein.

## 4. Bewerking

**SMILES.** Een molecuul kun je als tekst schrijven: `c1ccccc1` is benzeen (zes aromatische koolstofatomen in een ring), `Cc1ccccc1` is tolueen
(een methylgroep eraan), `c1ccc2ccccc2c1` is naftaleen. De taal heeft een grammatica — ringen moeten sluiten, haakjes moeten kloppen, elk
atoom heeft een toegestaan aantal bindingen — en een tekenreeks die de grammatica schendt is geen molecuul. Dat maakt deze taak geschikt voor
een generatief model: van elke uitvoer kun je **exact** controleren of hij deugt, met een programma (RDKit) dat de tekenreeks probeert te
lezen.

**Het model.** Een Transformer die tekst teken voor teken schrijft, van links naar rechts, zoals een taalmodel: gegeven de tekens tot nu toe,
voorspel het volgende. Vier lagen, ongeveer 3,2 miljoen parameters, zelf geschreven in PyTorch zonder voorgetrainde gewichten; de
woordenschat is 33 tekens. Trainen betekent: op de 125.065 trainingsmoleculen leren welk teken waarschijnlijk volgt. Genereren betekent:
beginnen met een starttoken en steeds een volgend teken trekken, met een **temperatuur** die zegt hoe avontuurlijk het trekken is (laag:
veilig en herhalend; hoog: nieuw en vaker ongeldig). Elke run traint drie *zaadjes*: drie runs die alleen verschillen in het toeval waarmee
ze beginnen, zodat de spreiding zichtbaar is.

**De conditie-tokens: de ene ontwerpverandering.** Twee extra tokens vooraan, tijdens het trainen meegeschreven: het aantal ringen (2, 3, 4 of
meer) en welke heteroatomen erin zitten (geen, N, O, S, gemengd). Daarna kun je vragen om "drie ringen, één stikstof", en meet het notebook
of het model **gehoorzaamt**.

**Alles vooraf vastgelegd.** Vóór er getraind werd, stond op papier wat gemeten wordt en wat verwacht: geldigheid (leest RDKit het?) minstens
85 %; uniciteit (geen kopieën van elkaar) minstens 95 %; nieuwheid (niet in de trainingsset) minstens 50 %, en met een skelet dat de training
nooit zag minstens 30 %; uit het hoofd geleerd (letterlijke trainingsmoleculen) hoogstens 10 %; gehoorzaamheid aan de conditie minstens
80 %; en de **projectpassing** — het deel van de nieuwe, geldige moleculen dat neutraal is, binnen de elementen van het corpus valt, hoogstens
30 zware atomen heeft en versmolten aromatisch is — tussen 30 en 60 %. Drie zaadjes moeten binnen ±0,03 op geldigheid liggen. Een model dat
de grenzen niet haalt, wordt met die uitkomst gepubliceerd.

**De uitkomst.** De volledige run draaide op een gehuurde machine: drie zaadjes en het geconditioneerde model, elk 10.000 voorbeelden, het
notebook van boven naar beneden. Tegen de grenzen, in dezelfde volgorde: geldigheid **0,92** (grens 0,85), uniciteit **0,99** (0,95),
nieuwheid **0,91** (0,50), nieuw skelet **0,53** (0,30), uit het hoofd **0,10** (hoogstens 0,10, precies op de grens), gehoorzaamheid aan de
conditie **0,87** (0,80). Zes van de zeven grenzen zijn gehaald, en de drie zaadjes liggen binnen ±0,03 op geldigheid. De zevende, de
**projectpassing**, kwam uit op **0,945** waar 0,30–0,60 was voorspeld: het model blijft veel dichter bij de versmolten-aromatische familie dan
voorspeld. Dat telt als een misvoorspelling van het project, niet als een zwakte van het model, en zo staat het in de uitkomstsectie van de
pre-registratie; de grens wordt niet achteraf verschoven. De eenvoudige tekenreeksbaseline zonder netwerk, een 5-gram-model, verloor op elke
regel (geldigheid 0,03).

## 5. Uitvoer — de datastructuur in detail

- **Het getrainde model** met versie en status in het register (`modules/06_generative_candidates/MODELS.md`), en het notebook dat van boven
  naar beneden draait: data inspecteren, model, leercurves, 10.000 voorbeelden per zaadje, de metingen tegen de voorspellingen, histogrammen
  van grootte en samenstelling tegen de testset, **mislukte gevallen getoond** (ongeldige tekenreeksen, kopieën, geladen moleculen,
  moleculen buiten de families) en vijf voorstellen naast hun drie dichtstbijzijnde trainingsburen.
- **Een gekeurde lijst kandidaten** (object O12 van [hoofdstuk 6](06_Datastructuren_en_Pijplijn.md)). Een tienvoudige geconditioneerde run trok 130.000 voorbeelden. Daarvan gingen er 23.769 door de keuring
  (geldig, binnen de grenzen van het corpus, op een ringsysteem dat het corpus nog niet bevat), op 2.272 nieuwe versmolten aromatische ringsystemen; 308 daarvan zijn
  zelf moleculen uit PubChem. Daarmee is de generator een vooraf vastgelegde bron voor het corpus: zijn voorstellen kunnen als een eigen,
  apart gelabelde laag worden doorgerekend. Er is nog geen voorstel doorgerekend, en nog geen voorstel staat in de Atlas.
- Rapport in de zes voorgeschreven secties (overzicht, data, modelontwerp en training, beoordeling van de uitvoer, ethiek en verantwoord
  gebruik, beperkingen en vervolg) met literatuurverwijzingen; een modelkaart; `requirements.txt`; een provenance-bestand met elke run, ook de
  mislukte.

Wat er uitdrukkelijk **niet** uitkomt: data. Een voorgesteld molecuul is een suggestie; pas als de pijplijn het heeft doorgerekend, is er een
spectrum, en dat is dan een gewoon record met provenance, net als elk ander.

## 6. Waarom deze module, en wat ze voor de pijplijn doet

Het ΔH-netwerk van module 05 is getraind op aromaten van 8 tot 30 atomen met de elementen van het corpus. Een correctie zonder
kandidaten is een antwoord zonder vraag: het project moet weten welke moleculen het waard zijn om te rekenen. Twee dingen maakt module 06
daarvoor meetbaar. Ten eerste de *projectpassing*: welk deel van wat een model "in de stijl van PubChem" verzint, valt binnen het soort
moleculen waar de correctie iets over zegt. Ten tweede het *sturen*: of je met een paar tokens vooraan de generator naar het soort molecuul
kunt leiden dat het corpus nog mist. Beide zijn getallen waar de rest van het project op verder kan, en geen van beide vergt een dure
berekening. Valt module 06 weg, dan draait de pijplijn gewoon, maar dan kiest een mens de kandidaten. Dat is een zwakkere vorm van "dragend"
dan bij modules 02 tot 05, en het plan zegt dat hardop.

Het oorspronkelijke idee voor deze plek, een generator van *meetpatronen* voor de dure berekening, leeft voort als een aparte
standout-module (`modules/standout_pattern_proposer/`). Daaruit komt de volgordescorer die bepaalt in welke volgorde de stukken van een dure
berekening worden gerekend (besluit 58).

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Geldigheid is geleerd, geen garantie.** In de SMILES-taal kan het model ongeldige tekenreeksen schrijven; het notebook telt ze en toont
  ze. Er bestaat een alternatieve schrijfwijze (SELFIES) waarin elke tekenreeks een molecuul is; die staat in het rapport als vervolg.
- **Nieuw is niet hetzelfde als goed.** Honderd procent nieuwheid met twee procent geldigheid is ruis. Lees de vijf getallen altijd samen, en
  lees de projectpassing als het getal dat het corpus gebruikt.
- **Uit het hoofd leren.** Een model dat trainingsmoleculen teruggeeft, "genereert" niets en schendt bovendien de omgang met de depositoren van
  PubChem. Het percentage staat in het rapport, met de grens van 10 % vooraf; het model ligt er precies op. Bij een lagere temperatuur (0,7)
  stijgt het naar 18–19 %, de vooraf aangekondigde ruil: meer geldig, meer gekopieerd.
- **De vertekening van PubChem, gemeten.** Scheikundigen deponeren wat ze gemaakt of geoctrooieerd hebben — medicijnachtige zijgroepen — niet
  de kale koolwaterstoffen van de interstellaire ruimte. Het model erft die smaak. De vergelijking met de NASA-PAH-databank (alleen als
  vergelijking, nooit als trainingsdata) laat zien hoe ver: de voorstellen hebben een mediaan van 18 koolstofatomen en bijna altijd een
  heteroatoom (91 % bevat stikstof), de PAK's van de databank een mediaan van 34 koolstofatomen en zelden een heteroatoom (12 % stikstof). De
  generator volgt zijn trainingsverdeling, en die ligt ver van de sterrenkundige.
- **Misbruik.** Een generator van aromatische structuren is een generator van *kandidaten voor spectroscopie*, niet van recepten. Het rapport
  en de modelkaart zeggen dat, en het model voorspelt geen eigenschappen richting giftigheid.
- **Een opnieuw getraind zaadje is een nieuwe run.** Het netwerk van het derde zaadje is na de run niet opgeslagen, alleen zijn
  trainingslog. Toen het notebook later opnieuw werd uitgevoerd, trainde het dat zaadje daarom opnieuw, en dat model haalde een geldigheid
  van 0,65 in plaats van 0,92. Een nieuw getraind zaadje reproduceert niets, dus de oorspronkelijke run blijft het resultaat en het nieuwe
  netwerk staat als ongeldig in het register. Sindsdien worden de getrokken voorbeelden bewaard, zodat een herhaling opgeslagen uitvoer
  keurt; voor het eerste zaadje gaf dat precies dezelfde getallen. Het derde zaadje opnieuw trainen en opslaan staat op de takenlijst vóór de
  inlevering. Controleer dat het ingeleverde notebook de oorspronkelijke run toont.
- **Stoppen op tijd.** Elke run hield een validatieset achter en had een stopregel (besluit 51), maar die kon binnen het plafond van twintig
  rondes nooit ingrijpen: de leersnelheid liep volgens een vast schema precies bij het plafond naar nul, en de drempel voor "geen verbetering"
  was te fijn. De curven waren in de laatste rondes vlak tot op een honderdste van de spreiding tussen de zaadjes, dus de getallen zijn er niet
  door begrensd. Een volgende run gebruikt een grovere drempel en een schema dat niet bij het plafond eindigt.
- **De pijplijncontrole is geen resultaat.** Het notebook heeft een snelle stand (2.000 moleculen, één zaadje) om te bewijzen dat alles van
  boven naar beneden draait; de getallen daaruit zijn als "geen resultaat" gelabeld. Die controle ving drie fouten vóór er echt getraind
  werd — een tekenbibliotheek die op een server zonder beeldscherm ontbrak, een cel die geen lege uitvoer verdroeg, en een fout in de
  herkenning van heteroatomen in de tekenreeks (de letters "Cc", koolstof naast aromatisch koolstof, werden voor een element aangezien).
  Controleer dat het ingeleverde notebook de *volledige* run is: drie zaadjes, twintig rondes, 10.000 voorbeelden.

## 8. In het kort

Module 06 traint een tekst-Transformer op 161.000 versmolten-aromatische moleculen uit PubChem, gesplitst per skelet, en laat hem nieuwe
moleculen schrijven. Vooraf vastgelegde metingen — geldigheid, uniciteit, nieuwheid, uit-het-hoofd, gehoorzaamheid aan conditie-tokens en
projectpassing — zeggen of de voorstellen deugen en of ze bruikbaar zijn voor het corpus. Het model haalde zes van de zeven vooraf vastgelegde
grenzen; de zevende, de projectpassing, lag ver bóven de voorspelling. Een gekeurde lijst van 2.272 nieuwe ringsystemen ligt klaar als
aparte bron voor het corpus. Kandidaten zijn suggesties, geen data; pas de pijplijn maakt er een spectrum van.

*Bron: `modules/06_generative_candidates/` (README.md, PRE_REGISTRATION.md met de uitkomstsecties, `data/README.md`, MODELS.md),
`GoalGathering/notes/PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md`, `modules/MODELS.md`, besluiten 51, 58 en 59 in de
[README van plan 05](../README.md), [Rubrics/06](../../../Rubrics/06_Generative_AI_Applications.md).*
