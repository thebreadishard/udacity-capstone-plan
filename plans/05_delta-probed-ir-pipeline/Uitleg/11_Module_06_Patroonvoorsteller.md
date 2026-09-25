# Hoofdstuk 11 — Module 06: de kandidatenvoorsteller

*Udacity-module "Generative AI Applications". In de rubriek Project 5. Stand van 25 september 2026; het ontwerp van 12 september staat als gedateerd kader in §9.*

---

## 1. Wat is de vraag?

Kan een klein generatief model nieuwe aromatische moleculen voorstellen die lijken op wat er bestaat, maar er niet in staan — zodat de
pijplijn van plan 05 straks weet **welke moleculen ze als volgende moet doorrekenen**, binnen de families waarvoor haar geleerde correctie is
vrijgegeven?

Dat is een andere vraag dan de rest van het plan stelt. Modules 02 tot 05 gaan over *hoe goed* een spectrum wordt; module 06 gaat over
*waarvan* je er een wilt. De atlas (hoofdstuk 6, de website) toont duizenden moleculen met een status op de ladder; module 06 is de bron van
nieuwe rijen, duidelijk gelabeld als "voorgesteld door een model", nooit als data.

## 2. Wat eist de school?

Een klein generatief systeem: een taak en dataset kiezen; een **GAN, VAE of Transformer-generator** implementeren en trainen (diffusie hoeft
niet); voorbeelden genereren; de kwaliteit beoordelen met sterke en zwakke gevallen uit eigen uitvoer; een rapport met minstens één ethische
overweging die aan *deze* data en *dit* model is gebonden. De dataset moet openbaar of duidelijk gedocumenteerd zijn, niet synthetisch of
AI-gegenereerd, en niet hergebruikt uit een eerdere module. Gegenereerde uitvoer telt nooit als dataset.

## 3. Invoer — de datastructuur in detail

**De bevroren PubChem-set.** Op 24 september 2026 zijn uit PubChem, de openbare moleculendatabank van de Amerikaanse National Institutes of
Health, alle moleculen opgehaald die een van negen aromatische kernen bevatten (benzeen, naftaleen, antraceen, fenantreen, pyreen, en vier
kernen met een stikstof-, zuurstof- of zwavelatoom in de ring), en daarna gefilterd: neutraal, alleen de elementen C, H, N, O, S, F en Cl, hooguit
30 zware atomen, en minstens twee **versmolten** aromatische ringen (ringen die een zijde delen, zoals in naftaleen). Dat leverde 160.972
moleculen op, elk als één regel:

| Veld | Type | Betekenis |
|---|---|---|
| cid | getal | het PubChem-nummer, de sleutel naar het openbare record |
| smiles | tekst | de molecuulstructuur als tekenreeks (§4 legt uit wat dat is) |
| formule, aantal zware atomen, aantal aromatische ringen | tekst, getal, getal | voor de statistiek en voor de conditie-tokens |
| kernen | lijst | welke van de negen zoekkernen het molecuul bevat |
| scaffold, split | tekst | het Murcko-skelet (het molecuul zonder zijgroepen) en de daaruit gehashte groep: train / validatie / test |

De **splitsing per skelet** is het belangrijkste ontwerpbesluit van de invoer. Wie willekeurig splitst, laat het model op de testset moleculen zien
die bijna gelijk zijn aan trainingsmoleculen (dezelfde kern, één andere zijgroep), en "nieuw" betekent dan niets. Hier gaan alle moleculen met
hetzelfde skelet naar dezelfde groep, via een hash van het skelet (hoofdstuk 4 §4.6), dus reproduceerbaar op elke machine.

**Wat er niet in zit.** Geen spectra, geen berekeningen van dit project, geen labdata. De set staat los van modules 02 tot 05, met een
eigen README (zoekvraag, filters, aantallen per stap, datum, SHA-256 van het bestand) en een Zenodo-uitgave (CC0: publiek domein, zoals
PubChem zelf).

## 4. Bewerking

**SMILES.** Een molecuul kun je als tekst schrijven: `c1ccccc1` is benzeen (zes aromatische koolstofatomen in een ring), `Cc1ccccc1` is tolueen
(een methylgroep eraan), `c1ccc2ccccc2c1` is naftaleen. De taal heeft een grammatica — ringen moeten sluiten, haakjes moeten kloppen, elk
atoom heeft een toegestaan aantal bindingen — en een tekenreeks die de grammatica schendt is geen molecuul. Dat is precies wat deze taak
geschikt maakt voor een generatief model: je kunt van elke uitvoer **exact** controleren of hij deugt, met een programma (RDKit) dat de
tekenreeks probeert te lezen.

**Het model.** Een Transformer die tekst tekens voor teken schrijft, van links naar rechts, zoals een taalmodel: gegeven de tekens tot nu toe,
voorspel het volgende. Vier lagen, ongeveer drie miljoen parameters, zelf geschreven in PyTorch zonder voorgetrainde gewichten; de
woordenschat is 33 tekens. Trainen betekent: op de 125.000 trainingsmoleculen leren welk teken waarschijnlijk volgt. Genereren betekent: beginnen
met een starttoken en steeds een volgend teken trekken, met een **temperatuur** die zegt hoe avontuurlijk het trekken is (laag: veilig en
herhalend; hoog: nieuw en vaker ongeldig).

**De conditie-tokens: de ene ontwerpverandering.** Twee extra tokens vooraan, tijdens het trainen meegeschreven: het aantal ringen (2, 3, 4 of
meer) en welke heteroatomen erin zitten (geen, N, O, S, gemengd). Daarna kan de atlas vragen om "drie ringen, één stikstof" en meet het
notebook of het model **gehoorzaamt**.

**Alles vooraf vastgelegd.** Vóór er getraind werd, staat op papier wat gemeten wordt en wat verwacht: geldigheid (leest RDKit het?) minstens
85 %; uniciteit (geen kopieën van elkaar) minstens 95 %; nieuwheid (niet in de trainingsset) minstens 50 %, en met een skelet dat de training
nooit zag minstens 30 %; uit het hoofd geleerd (letterlijke trainingsmoleculen) hoogstens 10 %; gehoorzaamheid aan de conditie minstens
80 %; en de **projectpassing** — het deel van de nieuwe, geldige moleculen dat neutraal is, binnen de elementen van het corpus valt, hoogstens
30 zware atomen heeft en versmolten aromatisch is — tussen 30 en 60 %. Drie zaadjes moeten binnen ±0,03 op geldigheid liggen. Slaagt het model
niet, dan is dát het gepubliceerde resultaat.

## 5. Uitvoer — de datastructuur in detail

- **Het getrainde model** met versiehash, en het notebook dat van boven naar beneden draait: data inspecteren, model, leercurves, 10.000
  voorbeelden per zaadje, de metingen tegen de voorspellingen, histogrammen van grootte en samenstelling tegen de testset, **mislukte gevallen
  getoond** (ongeldige tekenreeksen, kopieën, geladen moleculen, moleculen buiten de families) en vijf voorstellen naast hun drie dichtstbijzijnde
  trainingsburen.
- **Een lijst kandidaten** met hun projectpassing — de invoer voor de atlas, gelabeld als modeluitvoer.
- Rapport in de zes voorgeschreven secties (overzicht, data, modelontwerp en training, beoordeling van de uitvoer, ethiek en verantwoord
  gebruik, beperkingen en vervolg) met literatuurverwijzingen; `requirements.txt`; een provenance-bestand met elke run, ook de mislukte.

Wat er uitdrukkelijk **niet** uitkomt: data. Een voorgesteld molecuul is een suggestie; pas als de pijplijn het heeft doorgerekend, is er een
spectrum, en dat is dan een gewoon record met provenance, net als elk ander.

## 6. Waarom deze module, en wat ze voor de pijplijn doet

De pijplijn heeft na module 05 een geleerde correctie die per familie is vrijgegeven. Een correctie zonder kandidaten is een antwoord zonder vraag:
de atlas moet weten welke moleculen het waard zijn om te rekenen. Twee dingen maakt module 06 daarvoor meetbaar. Ten eerste de
*projectpassing*: welk deel van wat een model "in de stijl van PubChem" verzint, valt binnen de families waar onze correctie iets over zegt. Ten
tweede het *sturen*: of je met een paar tokens vooraan de generator naar het soort molecuul kunt leiden dat de atlas nodig heeft. Beide zijn
getallen waar de rest van het project op verder kan; geen van beide vergt één dure berekening. Valt module 06 weg, dan draait de pijplijn
gewoon, maar dan kiest een mens de kandidaten; dat is een zwakkere vorm van "dragend" dan bij modules 02 tot 05, en het plan zegt dat hardop.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Geldigheid is geleerd, geen garantie.** In de SMILES-taal kan het model ongeldige tekenreeksen schrijven; het notebook telt ze en toont
  ze. Er bestaat een alternatieve schrijfwijze (SELFIES) waarin elke tekenreeks een molecuul is; die staat in het rapport als vervolg, niet als
  excuus.
- **Nieuw is niet hetzelfde als goed.** Honderd procent nieuwheid met twee procent geldigheid is geen prestatie maar ruis. Lees de vijf
  getallen altijd samen, en lees de projectpassing als het getal dat de atlas gebruikt.
- **Uit het hoofd leren.** Een model dat trainingsmoleculen teruggeeft, "genereert" niets en schendt bovendien de omgang met de depositoren van
  PubChem; het percentage staat in het rapport, met de grens van 10 % vooraf.
- **De vertekening van PubChem.** Scheikundigen deponeren wat ze gemaakt of geoctrooieerd hebben — medicijnachtige zijgroepen — niet de kale
  koolwaterstoffen van de interstellaire ruimte. Het model erft die smaak. De vergelijking met de soortenlijst van de NASA-PAH-databank (alleen als
  vergelijking, nooit als trainingsdata) zegt hoe ver de uitvoer van de sterrenkundige verdeling af staat.
- **Misbruik.** Een generator van aromatische structuren is een generator van *kandidaten voor spectroscopie*, niet van recepten; het rapport en de
  modelkaart zeggen dat, en het model voorspelt geen eigenschappen richting giftigheid.
- **De pijplijncontrole is geen resultaat.** Het notebook heeft een snelle stand (2.000 moleculen, twee rondes) om te bewijzen dat alles van
  boven naar beneden draait; de getallen daaruit staan met een banner "geen resultaat" in het rapport. Op 25 september ving die controle drie
  fouten vóór er echt getraind was — een tekenbibliotheek die op een server zonder beeldscherm ontbrak, een cel die geen lege uitvoer verdroeg,
  en een fout in de herkenning van heteroatomen in de tekenreeks (de letters "Cc", koolstof naast aromatisch koolstof, werden voor een element
  aangezien). Controleer dat het ingeleverde notebook de *volledige* run is: drie zaadjes, twintig rondes, 10.000 voorbeelden.

## 8. In het kort

Module 06 traint een tekst-Transformer op 161.000 versmolten-aromatische moleculen uit PubChem, gesplitst per skelet, en laat hem nieuwe
moleculen schrijven. Vooraf vastgelegde metingen — geldigheid, uniciteit, nieuwheid, uit-het-hoofd, gehoorzaamheid aan conditie-tokens en
projectpassing — zeggen of de voorstellen deugen en of ze bruikbaar zijn voor de atlas. Kandidaten zijn suggesties, geen data; pas de
pijplijn maakt er een spectrum van.

## 9. Gedateerd kader: het ontwerp van 12 september 2026, en waarom het veranderde

Tot 24 september heette deze module de *patroonvoorsteller*: een VAE die, gegeven de trillingen van een molecuul, **meetpatronen** zou
voorstellen — verplaatsingen waarlangs de dure energieën worden gemeten — met als succesmaat of er met die voorstellen minder metingen (K_off,
hoofdstuk 5) nodig waren om Δ₂ terug te vinden. De trainingsdata zouden de antwoordrecords van de DFT-tegen-DFT-proefruns zijn.

Dat ontwerp is losgelaten om twee redenen die het plan zelf opleverde. Ten eerste bleek in de week van 19 tot 24 september dat de correctie
niet per meetpatroon maar **lokaal in bindingen en hoeken** leeft (hoofdstuk 10); daarmee werd de vraag "welk patroon nu?" een vraag over
symmetrie en buurten, die met vaste regels beter beantwoord wordt dan met een generator. Ten tweede vroeg de atlas — de website die op 23
september is ontworpen — om iets wat het plan nog niet had: een bron van *nieuwe moleculen* binnen de vrijgegeven families. Een generatief
model over moleculen levert dat, met een openbare dataset die precies aan de eisen van de rubriek voldoet. De oude tekst staat in de
git-geschiedenis van dit bestand (commit vóór 25 september 2026); de nieuwe module is op 24 september ontworpen en vooraf vastgelegd
(`modules/06_generative_candidates/DESIGN_2026-09-24.md`, `PRE_REGISTRATION.md`).

*Bron: `modules/06_generative_candidates/` (DESIGN_2026-09-24.md, PRE_REGISTRATION.md, README.md, PROVENANCE.md),
[Rubrics/06](../../../Rubrics/06_Generative_AI_Applications.md).*
