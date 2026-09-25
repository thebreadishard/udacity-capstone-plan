# Hoofdstuk 10 — Module 05: de ΔH-voorspeller (de "steunvoorspeller")

*Udacity-module "Deep Learning Systems". In de rubriek Project 4. Stand van 25 september 2026; §9 bewaart het ontwerp van 12 september als
gedateerd kader, §10 legt uit hoe je weet dat een netwerk echt leert.*

---

## 1. Wat is de vraag?

Kan een neuraal netwerk, alleen uit goedkope DFT-kenmerken van een molecuul, voorspellen *hoe* de goedkope trillingsberekening gecorrigeerd
moet worden naar een betere — niet trilling voor trilling, maar als het hele **blok per bandfamilie**: de verschuiving van elke band én de
koppelingen tussen de banden van één familie — zodat de dure metingen daar geplaatst worden waar het netwerk nog niet zeker is, en er minder
van nodig zijn?

## 2. Wat eist de school?

Een deep-learning-experiment in PyTorch: een probleemdomein kiezen (**beeld, tekst of reeks**), een model uit de familie **CNN, RNN of
Transformer**, een baseline trainen, en **precies één** ding veranderen voor een gecontroleerde vergelijking ("zeg wat er veranderde en wat gelijk
bleef"). Beide modellen evalueren, met leercurves. "Hoge nauwkeurigheid is niet vereist." De dataset moet openbaar zijn vóór de module, niet
synthetisch of AI-gegenereerd, en **niet hergebruikt uit een eerdere capstone-module**; samengestelde echte datasets zijn toegestaan. Het rapport
moet een ethiek-paragraaf hebben en het notebook een samenvatting van 4–6 zinnen.

## 3. Invoer — de datastructuur in detail

**Het corpus, object O11: zelf gemaakt, in lagen.** Zeven gemeten PAK-tensoren zijn geen deep-learning-dataset, en de openbare databank
Hessian QM9 bevat vrijwel geen aromaten van de maat die het plan nodig heeft. Daarom heeft het project sinds 12 september een eigen **corpusfabriek**:
voor elk molecuul rekent ze de geometrie met B3LYP/6-31G* uit, en dan twee Hessianen op precies die geometrie, één met B3LYP en één met ωB97X.
Het verschil ΔH = H(ωB97X) − H(B3LYP) is de *plaatsvervanger* van de echte correctie (coupled cluster min DFT): twee functionalen met een
sterk verschillend aandeel exacte uitwisseling, zodat het verschil dezelfde soort structuur heeft als het echte verschil. Het corpus bestaat in
lagen:

| Laag | Wat | Waarom | Stand 25 september |
|---|---|---|---|
| A | de aromaten van 22–30 atomen die op de ladder lijken: benzeen, naftaleen, antraceen, fenantreen, pyreen, fluorantheen, carbazool, acridine … | de "groottebrug" | 45 klaar |
| A2 | dezelfde veertien kernen, elk met vijftien zijgroepen (CH₃, OH, NH₂, F, Cl, CN, CHO, COOH, OCH₃, NO₂, CF₃, vinyl, ethynyl, CONH₂, SH) | veertien skeletten leren geen regel; honderden omgevingen wel | 199 klaar; 15 zadelpunten worden heropgelost |
| B | negentien kleine kernen (benzeen, pyridine, thiofeen, indool, chinoline …) met dezelfde zijgroepen, tot 26 atomen | de grote leercurve: 4.353 moleculen in vaste gehashte volgorde | gestart 25 september, vijf gehuurde machines |
| C | de geconjugeerde deelverzameling van Hessian QM9 (6.055 moleculen, alleen B3LYP erbij) | brede kleine-moleculenbasis | gepland |

Elk molecuul heeft een map met de geometrie, de twee Hessianen, de frequenties en een resultaatrecord; een **uitgave** (release) is een bevroren
bestand met een lijst van id's en een controlesom per Hessiaan, en krijgt een Zenodo-DOI. De uitgave van 24 september telt 229 moleculen.

**Twee routes, één regel.** Psi4 rekent deze Hessianen als eindige verschillen van gradiënten (hoofdstuk 4 §4.2), en dat maakt ruis: op
benzeen zat in de ωB97X-Hessiaan een fout van 133 cm⁻¹ die niets met de chemie te maken had. Sindsdien geldt de regel dat elke verdachte
Hessiaan een **tweede route** krijgt, een analytische Hessiaan uit pyscf, en dat de uitgave de analytische versie gebruikt waar die bestaat.
Zo zijn vijf moleculen "genezen" en vijftien echte zadelpunten ontmaskerd (hoofdstuk 4 §4.5: ruis en de stopregel).

**De vorm per molecuul:**

| Onderdeel | Type | Betekenis |
|---|---|---|
| tokens | reeks van M records | één per DFT-trilling: frequentie, welke atomen bewegen, atoomomgevingskenmerken, de familie |
| K | matrix M × M | de correctie in de basis van de B3LYP-trillingen, in cm⁻¹: de diagonaal is de bandverschuiving, de rest de koppelingen |
| familieblok | per familie een deelmatrix van K | het **doel**: verschuiving én koppelingen van één familie samen (sinds 19 september) |
| steun | matrix M × M van 0/1 | welke elementen van K groot zijn — de tweede kop van het netwerk |
| splits-hash | tekst | per molecuul: train / validatie / test, reproduceerbaar |

**Probleemdomein en modelfamilie, expliciet verklaard:** domein **reeks** (een molecuul als reeks van M trillings-tokens), model **Transformer**
(aandacht tussen tokens: de plek waar "zijn trillingen i en j gekoppeld?" leeft). Dat is de ingeleverde baseline van deze module. Wat het
project daarnaast leerde over de *taal* waarin je de correctie moet opschrijven, staat in §6.

**Wat er niet in zit.** Geen labdata. De PAK's van de ladder en alles wat groter is dan het corpus zijn **alleen testset**.

## 4. Bewerking

1. Corpus bouwen met de fabriek (lagen A en A2 op gehuurde machines, september 2026), de tweede route op verdachte moleculen, splitsen per
   molecuul met hash, uitgeven met DOI.
2. Baseline-Transformer trainen op het familieblok; leercurves loggen.
3. **De gecontroleerde vergelijking, bevroren in het recept vóór het trainen:** één ding anders, al het andere gelijk, drie zaadjes. In het
   ingeleverde notebook is dat de tweede kop (de steun) aan of uit; het recept zegt precies wat veranderde en wat niet.
4. Evalueren op de weggehouden moleculen: per familie de fout op de diagonaal (bandverschuivingen, in cm⁻¹) en op de koppelingen, tegen twee
   regels zonder netwerk — "geen correctie" en "de mediaan van de familie" — zodat elk getal een betekenis heeft.
5. Aanvullingen in dezelfde notebook (secties 7, 8 en 9): de tweede route op benzeen, de heropgeloste zadelpunten, de coupled-cluster-controle E8,
   en de lokaliteitstoetsen E9, E10 en de grootte-extrapolatie van 24–25 september. Sectie 8 is *append-only* uitgevoerd: de cellen van eerder
   zijn niet opnieuw gedraaid, hun uitvoer is bewaard, en het notebook vermeldt dat.

## 5. Uitvoer — de datastructuur in detail

- **Het getrainde model** met versiehash, en de uitgave van het corpus met DOI.
- **Per familie een getal**: de fout van de voorspelde bandverschuiving op de testset (op de uitgave van 229 moleculen: 2,6 / 3,9 / 5,4 / 8,5 cm⁻¹ voor
  C–H-strek / C–H-uit-het-vlak / ring-in-het-vlak / overig, tegen 44 / 24 / 20 / 19 zonder correctie) en de gemiddelde precisie van de steunkop.
- **De geleerde prior** voor een nieuw molecuul: een voorspelde K met een onzekerheid, die als `prior = geleerd` met modelhash in het deck (O3) van
  een rung gaat waar dat mag (hoofdstuk 5 §5.4).
- Notebook, `requirements.txt`, rapport met de vereiste zinnen: het corpus is eigen berekende ab-initiodata, openbaar met DOI, niet AI-gegenereerd,
  in geen eerdere module gebruikt; het lab is nooit trainings-, validatie- of stopinvoer.

## 6. Wat het project onderweg leerde: de taal van de correctie

Dit is het deel dat op 12 september nog niet bestond en dat de reviewer moet zien, omdat het laat zien dat er *geleerd* is.

**De koppelingen leerden niet, tot de taal veranderde (E6 → E7, 19–23 september).** In de basis van de trillingen (K per trillingspaar) leerde geen
enkel model de koppelingen: de leercurve bleef vlak bij 45, 100 en 175 moleculen. De reden is wiskundig: een trilling is een richting in een
36-dimensionale ruimte, en die richting heeft geen vast teken — draai je hem om, dan wisselt de koppeling van teken zonder dat een kenmerk van de
trilling dat verraadt. Het label per trillingspaar is dus slecht gedefinieerd. Schrijf dezelfde correctie op in de taal van **bindingen en hoeken**
(interne coördinaten: rek van een binding, buiging van een hoek), dan is elk element tekenvast en lokaal, en dan leert hetzelfde netwerk op
dezelfde 175 moleculen de koppelingen wél: de fout op de ringkoppelingen halveert tegenover "geen correctie", ook op skeletten die het nooit zag,
en ook op de kale kernen zonder zijgroepen (0,43 tegen 0,47 bij 175 moleculen; gecorrigeerde frequenties 4,7 tot 5,2 cm⁻¹ tegen 23 zonder correctie).

**De correctie is lokaal, en dat is drie keer gemeten.** Driekwart van ΔH zit in bindingsparen die een atoom delen of in dezelfde ring liggen (E7);
de echte coupled-cluster-correctie van benzeen zit voor 98 % in datzelfde patroon, één binding verder (E8, 24 september); en de correctie van een
molecuul met zijgroep is het blok van zijn moederkern plus de buurt van de zijgroep (E9): een kwart van de Hessiaan-kolommen geeft de gecorrigeerde
frequenties tot 1,7 cm⁻¹ terug. Voor rigide zijgroepen kan dat buurtblok zelfs één keer gemeten en overgezet worden (E10). Hoofdstuk 5 §5.9 zegt
wat dat voor de telling van dure metingen betekent.

**Symmetrie: een meting die niets mat, en wat ze ons toch leerde (E11.2, 25 september).** Een eerste lezing, dezelfde ochtend, zei dat het
paarmodel de symmetrie van het molecuul niet respecteerde: spiegelbeeldparen zouden antwoorden krijgen die de helft van hun eigen grootte
uiteenliepen. Die lezing was fout, en de fout is leerzaam. De meetlat deelde paren in klassen in op grond van het soort atomen, niet op grond van
hun onderlinge ligging: in benzeen zaten ortho-, meta- en paraparen in één klasse, en het verschil tussen die drie is echte natuurkunde, geen
asymmetrie. De controle die vooraf had gemoeten, dezelfde meetlat langs het dóél leggen, gaf hetzelfde getal (0,58 tegen 0,52 voor het model).
Met echte symmetriebanen, de paren die een spiegeling of draaiing van het molecuul in elkaar overvoert, is het doel wél symmetrisch (benzeen 0,03)
en blijkt iets anders: het paarmodel krijgt voor spiegelbeeldparen precies dezelfde invoer, want zijn kenmerken zijn atoomsoorten, afstanden
en ringafstanden, en die veranderen niet onder een spiegeling. Het geeft dus vanzelf hetzelfde antwoord. Symmetrie zit in dit model ingebouwd,
niet geleerd, en de test kon die twee nooit uit elkaar houden. Wat blijft staan: het paarmodel kent geen richtingen, alleen getallen per paar,
en voor een correctie op de volledige krachtmatrix in de ruimte, een grootheid mét richtingen, is een **equivariant** netwerk nodig: een netwerk
waarvan de tussenresultaten meedraaien met het molecuul. Dat is de volgende versie van deze module, om díe reden, en niet omdat E11.2 het zou
hebben afgedwongen.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De herbruikclausule.** Het corpus is eigen berekende data, in geen eerdere module gebruikt; controleer dat het rapport dat zegt en de DOI noemt.
- **Domein en familie letterlijk.** "Reeks" en "Transformer" met zoveel woorden; de verandering van precies één ding in het recept vóór het trainen.
- **Ruis in de labels.** Elke uitgave meldt welke Hessianen langs de tweede route zijn vervangen en waarom; een molecuul dat "genezen" is, staat
  erbij met beide getallen. Controleer dat de uitgave van het notebook overeenkomt met de uitgave in de provenance.
- **Append-only eerlijk.** Cellen die niet opnieuw gedraaid zijn, mogen niet opnieuw *geschreven* zijn. Op 24 september overschreef het
  uitvoerhulpje per ongeluk twee zware cellen met hun definitie-kopieën; dat is op 25 september ontdekt, hersteld uit de commit van 23 september en
  in de provenance opgeschreven. Controleer dat de trainingscellen uitvoer en een uitvoernummer hebben.
- **Het bewijs is een curve, geen tabel.** Zie §10: niets in dit hoofdstuk is een bewijs dat het netwerk leert wat het voor grote PAK's moet leren;
  de vooraf vastgelegde leercurve op laag B is dat wel of niet.

## 8. In het kort

Module 05 traint een Transformer die uit DFT-kenmerken per bandfamilie het correctieblok voorspelt, op een eigen corpus van ωB97X−B3LYP-verschillen
in lagen, uitgegeven met DOI. Onderweg leerde het project dat de correctie lokaal is en in de taal van bindingen en hoeken geleerd moet worden, dat
het huidige paarmodel symmetrie niet respecteert, en dat het echte bewijs een vooraf vastgelegde leercurve is die op 25 september is gestart.

## 9. Gedateerd kader: stand van zaken op 12 september 2026

Dit hoofdstuk beschrijft het plan zoals het is bevroren. Sindsdien is er gemeten, en dat verandert
één aanname in §3.

**Hessian QM9 is binnen.** Het bestand van 6,3 GB is gedownload en gecontroleerd (md5 klopt); alleen het
vacuümdeel is uitgepakt: 41.645 moleculen met per molecuul de geometrie, de energie, de krachten, de
Hessiaan, de frequenties en de normaalmodes. Het artikel is gelezen voor de eenheden (Å, eV, eV/Å²,
cm⁻¹) en de conventies. Twee dingen die je bij gebruik moet weten: de Hessianen zijn *numeriek*
(eindige verschillen met een verplaatsing van 0,01 a.u.; de makers melden dat de frequenties daar tot
15 cm⁻¹ gevoelig voor zijn, dus dat is de ruisvloer van elk label dat we eruit maken), en translaties en
rotaties zijn er niet uitgeprojecteerd (dat doen wij zelf voordat Δ₂ wordt gevormd).

**De aanname "benzeenderivaten oververtegenwoordigd" klopt niet.** Een ringtelling uit de geometrie
(bindingen uit covalente stralen, ringen uit de bindingsgraaf, platheid gecontroleerd) geeft: 66 van de
41.645 moleculen hebben een geheel-koolstof aromatische zesring, benzeen zelf zit er één keer in.
Wat er wél ruim in zit, 6.055 moleculen, zijn platte geconjugeerde vijf- en zesringen met stikstof of
zuurstof erin: pyridine-, pyrrool- en furaanachtigen. De "aromaat-zware QM9-deelverzameling" van §3 is
in werkelijkheid een geconjugeerde, heteroaromatische deelverzameling. De PAK-testset ligt dus nog
verder buiten de trainingsverdeling dan §3 aannam.

**Het antwoord dat klaarstaat: een eigen corpusfabriek.** Omdat QM9 gewoon DFT is en DFT-Hessianen
van kleine aromaten goedkoop zijn (gemeten op de laptop: benzeen 3 tot 7 minuten per Hessiaan,
naftaleen 13 minuten, pyreen 54 minuten), is in `modules/05_support_predictor/corpus/` een
wachtrij klaargezet die molecuul voor molecuul beide Hessianen rekent (B3LYP en ωB97X, 6-31G*), in
vier lagen en in een vaste volgorde (de laag A′ is later op 12 september toegevoegd, op besluit van de opdrachtgever):

| laag | inhoud | aantal in het manifest |
|---|---|---|
| A, grootte-brug (ouders) | aromaten van 12 tot 30 atomen, van benzeen tot pyreen, met aza- en oxa-varianten | 45 |
| A′, grootte-brug als verdeling | dezelfde grote kernen (antraceen, fenantreen, pyreen, fluorantheen, acridine, carbazool, …) elk met één zijgroep uit vijftien; toegevoegd op 12 september op besluit van de opdrachtgever, omdat 45 ouders geen regel kunnen leren | 868 |
| B, de klasse | mono- en digesubstitueerde aromatische en heteroaromatische kernen tot 26 atomen | 4.353 |
| C, QM9 geconjugeerd | de 6.055 uit de ringtelling; alleen de B3LYP-Hessiaan hoeft nog | 6.055 |

De fabriek kan op elk moment gestopt en weer gestart worden (laptop, straks de desktop, ooit een
cluster); omdat de volgorde binnen een laag vastligt, is elke tussenstand een reproduceerbare
deelverzameling en zijn "de eerste 300, 600, 1.200" van laag B geneste sets voor een leercurve. De
volgorde over de lagen heen: eerst A (de vijf timingmoleculen voorop), dan om en om B en A′ zodat de
klasse-as en de grootte-as samen groeien, dan C.
Hoeveel er uiteindelijk gerekend wordt, staat met opzet nergens: dat wordt een gedateerde notitie na
een timingtest van vijf moleculen, precies zoals §3 al voorschreef voor de QM9-deelverzameling.
Er is nog niets gerekend. De vier eigen lagen zijn op 12 september als kandidaat overgenomen (gedateerde
notitie in de mapping); hoeveel er echt gerekend wordt, beslist de timingtest van vijf moleculen — en die
kan pas draaien als er geen ankerberekening loopt (regel: één zware berekening tegelijk op de laptop).

*Bron: `modules/05_support_predictor/PROVENANCE.md`, `out/HESSIAN_QM9_SUMMARY.md`,
`out/HESSIAN_QM9_RINGS.md`, `corpus/DESIGN_2026-09-12.md`; gedateerde notitie van 12 september in
[Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §Module 05.*

## 10. Hoe weet je dat een netwerk echt iets geleerd heeft? (gedateerde aanvulling, 25 september 2026)

Een netwerk dat op zijn trainingsvoorbeelden goed scoort, heeft nog niets bewezen. Een leerling die de antwoorden van het oefenexamen uit zijn
hoofd kent, heeft ook geen wiskunde geleerd. De vraag die in dit hoofdstuk telt is dus niet "hoe klein is de fout?", maar "hoe weet je dat het
netwerk de *regel* heeft gevonden en niet de *antwoorden*?" Daar zijn drie soorten bewijs voor, en we gebruiken ze alle drie.

**Eerste bewijs: toetsen op wat het netwerk nooit zag, en dat steeds moeilijker maken.** Het makkelijkste is een paar moleculen achterhouden
uit dezelfde verzameling. Moeilijker is een heel *skelet* achterhouden: alle moleculen die op een bepaalde kern zijn gebouwd, bijvoorbeeld alles
met een carbazool-kern, zodat het netwerk die kern nooit ziet en er toch over moet oordelen. Het moeilijkst, en voor ons het belangrijkst, is
*groter*: leer alleen van kleine moleculen en toets op grotere. Dat is precies de richting waarin de pijplijn straks moet werken, want de PAK's
die in de ruimte tellen zijn groter dan alles wat we kunnen doorrekenen. Als de fout bij elke stap ongeveer gelijk blijft, heeft het netwerk iets
algemeens geleerd. Als de fout bij "groter" ineens omhoog schiet, kende het alleen de maten die het gezien had.

**Tweede bewijs: de leercurve.** Geef het netwerk 50, 100, 200, 1.000 voorbeelden en zet de fout uit tegen het aantal. Bij echt leren daalt die
lijn en blijft ze dalen; bij uit het hoofd leren blijft ze vlak, want elk nieuw voorbeeld vertelt dan niets over het volgende. Het sterkste bewijs
dat wij hebben is een *vergelijking* van twee curves op dezelfde gegevens. Toen we het netwerk vroegen om de correctie per trilling op te
schrijven, bleef de curve voor de koppelingen tussen trillingen vlak, hoe veel moleculen we ook gaven. Toen we dezelfde correctie opschreven in
de taal van bindingen en hoeken — lokaal, in de buurt van elk atoom — begon dezelfde curve te dalen. Dezelfde data, dezelfde voorbeelden, een
andere taal: dat is het verschil tussen "het kan niet" en "het kan, als je het goed vraagt". Omdat een curve pas overtuigt als ze lang genoeg is,
loopt sinds 25 september een nieuwe: van 100 tot 1.200 kleine moleculen, met de drie toetsen van het eerste bewijs, en met de leesregel — wat
telt als slagen en wat als falen — op papier gezet vóórdat het eerste getal bestond. Zo kan niemand achteraf de lat verplaatsen, wij ook niet.

**Derde bewijs: controles die moeten mislukken, en controles die moeten kloppen.** Schud de antwoorden door elkaar, zodat elk molecuul de
correctie van een ander molecuul te leren krijgt, en train opnieuw. Als het netwerk dan óók een dalende curve laat zien, meet onze meetlat iets
anders dan leren, en dan mag geen enkele eerdere curve tellen. Andersom: in een symmetrisch molecuul, zoals benzeen, zijn er atomen die
elkaars spiegelbeeld zijn. Niemand heeft het netwerk verteld welke dat zijn. Als het voor spiegelbeeldparen toch hetzelfde antwoord geeft, heeft
het de natuurkunde gevonden en niet de tabel onthouden. (Deze controle werkt alleen bij een model dat de symmetrie kán schenden. Bij ons
paarmodel zit ze in de kenmerken ingebouwd, en dan meet de controle niets; dat leerden we op 25 september, zie §8.) Een derde controle is de *ruisvloer*: onze correcties komen zelf uit berekeningen met een
kleine meetfout, en een netwerk kan niet nauwkeuriger worden dan zijn leerstof. Een curve die tot aan die vloer zakt en daar stopt is het beste
wat er te halen valt; een curve die ver boven de vloer blijft hangen zegt dat het model, en niet de data, de grens is.

**Waar we staan, eerlijk.** De verschuiving van elke trilling apart leert het netwerk goed. De koppelingen tussen trillingen leert het op
skeletten die het nooit zag én op de kale moederkernen zonder zijgroepen, met een curve die daalt; die kale kernen zijn juist de moleculen
die het meest op de grote PAK's lijken, en de curve daalt daar nog te langzaam om al van bewijs te spreken. (Een eerdere versie van deze
alinea, dezelfde ochtend, noemde die curve vlak; dat kwam uit een achterhaald resultaatbestand en is gecorrigeerd.) Kleine moleculen leren het netwerk iets over grotere, maar langzamer dan ze elkaar leren.
Dat is geen mislukking en geen succes; het is de stand van een curve die nog kort is. Het bewijs dat dit ontwerp werkt, is een curve die lang
genoeg is, op de drie moeilijke toetsen, met de leesregel van tevoren. Die curve loopt nu.
