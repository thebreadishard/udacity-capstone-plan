# Hoofdstuk 5 — De kern: de geleerde correctie

> **In dit hoofdstuk leer je**
> – wat het oorspronkelijke idee was (Δ-probing) en welke metingen het veranderden;
> – wat het ΔH-netwerk precies leert: het verschil tussen twee Hessianen van hetzelfde molecuul;
> – waarom de correctie in lokale coördinaten wordt geleerd en niet per trilling;
> – hoe het netwerk stap voor stap van molecuul naar correctie gaat;
> – wat de vier lagen van waarheid zijn;
> – hoe goed het netwerk nu is, en wanneer een nieuwe versie het mag vervangen;
> – hoe de coupled-clusterankers het netwerk ijken, en hoeveel ankers dat zou vragen.

---

## §5.1 Het oorspronkelijke idee: Δ-probing

Hoofdstuk 1 definieerde Δ₂: het verschil tussen de dure en de goedkope veerconstanten van een
molecuul. Het bevroren plan van september 2026 wilde Δ₂ per molecuul *opmeten*, met zo weinig
mogelijk dure berekeningen. Dat heette **Δ-probing**.

Een **probe** was één dure meting. Het molecuul werd langs een vast patroon een klein stukje
uitgewijkt, naar voren en naar achteren (±). In elke stand werden de coupled-clusterenergie
(CC) en de DFT-energie berekend. Uit die twee standen en de evenwichtsstand volgt hoe krom het energielandschap langs dat
patroon is (hoofdstuk 4, §4.2). Het verschil tussen de CC-kromming en de DFT-kromming is één stukje
informatie over Δ₂.

Alle patronen van een molecuul stonden vooraf in een vaste lijst, het **deck**. Het plan telde
hoeveel CC-energieën nodig waren tot de teruggevonden Δ₂ goed genoeg was. Dat aantal heette
**K**. De hoop was dat K veel kleiner is dan het aantal berekeningen voor een volledige Hessiaan.
Die hoop rustte op twee vermoedens: Δ₂ is *lokaal* (een correctie hangt vooral af van de directe
buren) en Δ₂ is *dun* (de meeste kruistermen zijn bijna nul). Met die twee vermoedens kun je een
grote tabel terugvinden uit weinig metingen (hoofdstuk 4, §4.4).

## §5.2 Wat de metingen leerden

Drie metingen veranderden het plan.

**De prijs van één dure energie.** Eén energie met lokale coupled cluster (hoofdstuk 3, §3.4) van
een molecuul van 25 atomen kost op strenge instellingen minstens negen uur op acht rekenkernen. Een deck van een paar honderd
energieën per molecuul kost dan weken. Voor duizenden moleculen is dat onbetaalbaar, hoe klein K
ook uitvalt.

**De correctie is lokaal.** Op benzeen werd de volledige CC-correctie berekend en ontleed. Bijna
alles ervan past in een lokaal patroon: elke binding en hoek met zichzelf, paren die een atoom
delen, en paren bindingen in dezelfde ring (§5.4). Buiten dat patroon blijft een rest van 0,09
maal de grootte van de correctie. De koppelingen tussen ringbindingen passen er minder goed in: de
CC-correctie reikt een binding verder dan de DFT-correctie.

**De correctie herhaalt zich.** Op DFT-niveau bleek de correctie van een molecuul met een zijgroep
te bestaan uit het blok van zijn moederkern plus de buurt van de zijgroep. Meet je alleen de
atomen binnen twee bindingen van de zijgroep, dan komen de gecorrigeerde frequenties tot op
1,7 cm⁻¹ terug.

Samen wijzen die drie metingen één kant op. Als de correctie lokaal is, komen dezelfde lokale
situaties in veel moleculen terug: een C–H-binding aan de rand van een ring, een stikstofatoom in
een ring, een chlooratoom aan een ring. Dan hoef je de correctie niet per molecuul op te meten. Je
kunt haar één keer *leren* uit veel voorbeelden, en daarna voor elk nieuw molecuul *voorspellen*.
Dat is de stap van Δ-probing naar het **ΔH-netwerk**.

## §5.3 Wat het netwerk leert: ΔH

Hoofdstuk 2 (§2.3) legde de **Hessiaan** uit: de tabel met alle veerconstanten van een molecuul,
één rij en één kolom per bewegingsrichting van elk atoom. Een molecuul met N atomen heeft een
Hessiaan van 3N bij 3N getallen. Uit de Hessiaan volgen alle trillingsfrequenties.

Het netwerk leert het verschil tussen twee Hessianen van hetzelfde molecuul:

> **Definitie 5.1 — ΔH**
> ΔH = H_beter − H_goedkoop, met H_goedkoop de Hessiaan uit de goedkope berekening (B3LYP) en
> H_beter de Hessiaan uit een betere berekening, op dezelfde geometrie. Het ΔH-netwerk krijgt het
> molecuul en H_goedkoop, en voorspelt ΔH.

Een trainingsvoorbeeld is dus een paar: van één molecuul de goedkope en de betere Hessiaan. De
pijplijn gebruikt de voorspelling zo:

1. bereken H_goedkoop met B3LYP;
2. laat het netwerk ΔH voorspellen;
3. tel op: H_gecorrigeerd = H_goedkoop + ΔH;
4. diagonaliseer H_gecorrigeerd: dat geeft de trillingsfrequenties (hoofdstuk 4, §4.1).

ΔH is de Hessiaanvorm van Δ₂ uit hoofdstuk 1. Het netwerk voorspelt dus precies de grootheid die
Δ-probing wilde opmeten.

De trainingsverzameling heet het **corpus**. Het bestaat uit 1.236 moleculen in vijf lagen: 46 met
de hand gekozen moederkernen, 327 varianten daarvan met zijgroepen, 743 moleculen van een tweede,
bredere laag, 60 moleculen met vijf of meer ringen en nieuwe ringtypen, en 60 kationen. Van elk
molecuul staan de geometrie, de B3LYP-Hessiaan, de ωB97X-Hessiaan en de gegevens voor de
bandsterkte in het corpus. De Hessianen zijn **analytisch** berekend: met een formule voor de
tweede afgeleide, in plaats van door het molecuul steeds een stukje te verschuiven en verschillen
te nemen. Dat haalt rekenruis weg die bij de zachte trillingen groter was dan de fout van het
netwerk.

## §5.4 De taal van de correctie: lokale coördinaten

Een correctie kun je in verschillende "talen" opschrijven. De vraag is in welke taal ze eenvoudig
is.

De eerste taal is die van de **trillingen** (de modebasis): een tabel met één rij en kolom per
trilling. De getallen op de diagonaal verschuiven elke trilling; de getallen ernaast heten
**koppelingen** en mengen trillingen. In die taal lukte het leren niet. Netwerken die koppelingen
per trilling voorspelden, deden het met 45, 100 of 175 voorbeeldmoleculen niet beter dan de regel
"alle koppelingen zijn nul". Meer data hielp niet. De reden: een trilling is een beweging van het
hele molecuul, en in een ander molecuul bestaat dezelfde trilling niet.

De tweede taal is die van **lokale coördinaten**: bindingslengtes, hoeken tussen twee bindingen,
en de hoek waarmee een atoom uit het vlak steekt. Zo'n coördinaat bestaat in elk molecuul op
dezelfde manier. Het netwerk voorspelt per paar lokale coördinaten één getal, voor drie soorten
paren:

- een coördinaat met zichzelf (de diagonaal: de stijfheid van die ene binding of hoek);
- twee coördinaten die een atoom delen;
- twee bindingen in dezelfde ring.

Andere paren krijgen geen getal. Dat is het lokaliteitsvermoeden van §5.1, ingebouwd in het
netwerk. Op de DFT-proxy zit ongeveer drie kwart van ΔH in precies dit patroon.

Van die lokale tabel, ΔF genoemd, gaat het netwerk terug naar atoombewegingen met een vaste
vertaaltabel B. B zegt per lokale coördinaat hoe die verandert als een atoom een klein stukje
beweegt. De formule is ΔH = Bᵀ · ΔF · B (hoofdstuk 4, §4.1: matrixvermenigvuldiging). Twee
eigenschappen volgen vanzelf. ΔH is symmetrisch, zoals elke Hessiaan. En het verschuiven of
draaien van het hele molecuul kost geen energie, omdat geen enkele lokale coördinaat daardoor
verandert.

## §5.5 Het netwerk stap voor stap

Een **neuraal netwerk** is een rekenprogramma met heel veel instelbare getallen. **Trainen** betekent:
die getallen zo instellen dat het programma op de voorbeelden het goede antwoord geeft. Het
ΔH-netwerk bestaat uit twee delen, een **romp** en een **kop**.

**Stap 1 — de invoer.** Per atoom: het atoomsoort (C, H, N, O, F, S of Cl) en de positie. Per paar
atomen: drie getallen uit hun blok van de B3LYP-Hessiaan, gekozen zo dat ze niet veranderen als je
het molecuul draait. Meer krijgt het netwerk niet.

**Stap 2 — de romp leert de omgeving.** Elk atoom begint met een korte lijst getallen die zijn soort
beschrijft. Daarna stuurt elk atoom drie keer een "bericht" naar alle atomen binnen 5 ångström
(0,5 nanometer). Bij elke ronde past elk atoom zijn lijst aan op wat de buren sturen. Na drie
rondes beschrijft de lijst van een atoom zijn omgeving: wat er naast zit, en wat daar weer naast
zit. De romp is zo gebouwd dat draaien of spiegelen van het molecuul de uitkomst niet verandert, en
dat de volgorde waarin je de atomen opschrijft er niet toe doet. Zo'n netwerk heet **equivariant**.

**Stap 3 — de kop voorspelt per paar.** Voor elk toegestaan paar lokale coördinaten (§5.4) neemt de
kop de omgevingslijsten van de betrokken atomen, de soort paar en de B3LYP-veerconstanten van dat
paar. Daaruit maakt hij één getal: de correctie ΔF voor dat paar.

**Stap 4 — terug naar de Hessiaan.** Met ΔH = Bᵀ · ΔF · B wordt de lokale tabel een correctie op de
Hessiaan (§5.4).

**Stap 5 — drie keer, en het gemiddelde.** Het netwerk wordt drie keer getraind, elk vanuit een
andere willekeurige start (een **seed**). De pijplijn gebruikt het gemiddelde van de drie
voorspellingen. Het verschil tussen de drie geeft een indruk van hoe zeker het netwerk is.

Bij het trainen gelden twee regels. Ten eerste houdt elke training een deel van de voorbeelden
apart als **validatieset**. De training stopt als de fout op die set niet meer daalt, en het beste
moment wordt bewaard (**early stopping**, beslissing 51). Zonder die regel leert een netwerk de
voorbeelden uit het hoofd. Ten tweede wordt een netwerk pas gebruikt als het een versie is waar het
project tevreden over is.

**Versies.** Een versienummer hoort bij een recept: de keuzes voor invoer, netwerk en training.
Versies 1.x zitten in de pijplijn, versies 0.x zijn experimenten (beslissing 59). Elk opgeslagen
netwerk heeft een status. Alleen een netwerk met de status **gedragen** (*carried*) mag voor verder
werk worden gebruikt; de programma's weigeren andere (beslissing 55). Een nieuwe versie wordt alleen
gedragen als ze op beide hold-outs in geen van vijf maten slechter is dan de huidige, en in ten
minste één maat beter (beslissing 57). Die vijf maten zijn de fout per familie (vier) en de
koppelingsfout (§5.7). De gedragen versie is nu **v1.3**; v1.0 tot en met v1.2 zijn vervangen.

## §5.6 Vier lagen van waarheid

Het netwerk leert van ωB97X, een betere DFT-variant. Maar ωB97X is zelf ook niet "de waarheid". Het
plan legt daarom vast welke rol elk rekenniveau speelt (beslissing 60):

| Laag | Wat het is | Hoeveel moleculen | Taak |
|---|---|---|---|
| 1. invoer | B3LYP/6-31G*, de goedkope berekening | elk molecuul | de invoer van het netwerk; blijft in de pijplijn |
| 2. opstap | ωB97X/6-31G* | duizenden | hier leert het netwerk de *vorm* van de correctie: families, koppelingen, ringskeletten |
| 3. ankers | CCSD(T)-Hessianen | elf | de ijklaag: bepaalt wat "goed" is voor de harmonische correctie |
| 4. de wereld | lab- en sterrenkundige spectra | tientallen | de controle van buitenaf op de hele keten |

De kern van deze indeling: hoe goed het netwerk uiteindelijk is, hangt af van de bovenste laag
waarop het geijkt wordt, niet van de laag waarop het voortraint. De opstap wordt beoordeeld op hoe
weinig de ankers daarna nog moeten bijstellen. De notaties "/6-31G*" en "cc-pVDZ" noemen de
**basisset**: hoe fijn de berekening de elektronen beschrijft (hoofdstuk 3, §3.7).

## §5.7 Hoe goed het netwerk nu is

De nauwkeurigheid wordt gemeten op de twee hold-outs van hoofdstuk 1: acht moleculen die nooit in
de training zaten (hold-out a) en 39 moleculen op twee ringskeletten die het netwerk nooit zag
(hold-out b). Alle getallen zijn op proxyniveau: de gecorrigeerde B3LYP-frequenties tegen de
ωB97X-frequenties.

Er zijn drie soorten maten.

- **De fout per familie**, in cm⁻¹. Drie van de vier families blijven op beide hold-outs onder
  3 cm⁻¹ en zijn daarmee vrijgegeven (beslissing 65). De familie "overig" blijft erboven (3,62 en
  3,89 cm⁻¹). De volledige tabel staat in hoofdstuk 1, §1.3.
- **De koppelingsfout.** Dit is de typische fout in de voorspelde koppelingen, gedeeld door de
  typische grootte van die koppelingen. 0 is perfect; 1 is niet beter dan "alle koppelingen nul".
  Voor v1.3 is ze 0,18 op hold-out (a) en 0,26 op hold-out (b), tegen een streefwaarde van 0,25.
- **De vorm van het spectrum.** Deze maat zegt hoe goed het getekende spectrum op het
  ωB97X-spectrum lijkt. Ze loopt van 0 tot 1, met 1 voor dezelfde vorm. Zonder correctie is de overlap 0,28 op
  hold-out (a) en 0,37 op hold-out (b); met de correctie 0,98 en 0,97.

Bij de hold-outs hoort een les. Hold-out (a) telde eerst tien moleculen. Twee daarvan stonden ook in
een andere laag van het corpus en zaten zo toch in de training. Een programma dat per molecuul
nagaat of het netwerk het al zag, vond dat. Op de schone acht liggen de fouten 0,04 tot
0,27 cm⁻¹ hoger. De trainer gooit zulke dubbelgangers nu standaard weg.

## §5.8 De ankers: de ijklaag

Een **anker** is een molecuul waarvan de volledige Hessiaan met CCSD(T) is berekend, de standaardvorm
van coupled cluster (hoofdstuk 3, §3.3). Het project heeft er elf: acenaftyleen, antraceen, azuleen,
benzeen, benzonitril, fluorbenzeen, isochinoline, naftaleen, pyridine, chinoline en chinoxaline.

**Het niveau.** CCSD(T) in de grote basisset cc-pVTZ is voor de meeste ankers te duur. De standaard is
daarom een samenstelling: CCSD(T) in de kleinere basisset cc-pVDZ, plus de stap van cc-pVDZ naar
cc-pVTZ zoals een goedkopere methode (MP2) die ziet. Bij benzeen is de volledige CCSD(T)/cc-pVTZ
berekend. De kleine basisset alleen gaf bij antraceen een onmogelijke trilling uit het vlak, met een
negatieve kromming; met de basisstap verdwijnt die.

**Twee routes per anker.** Elk anker wordt op twee onafhankelijke manieren gecontroleerd (beslissing 61).
De eerste route controleert of de krachten die de Hessiaan opbouwen kloppen met de energieën waaruit
ze volgen. De tweede route vergelijkt het rekenhart van de berekening met een andere implementatie.
Die regel komt uit ervaring. Een reeks ankers bleek eens berekend met een verkeerde tussenstap, terwijl
alle controles van dat moment slaagden. Pas een tweede, onafhankelijke route liet de fout zien.

**Het register.** Elke CC-Hessiaan staat in een register (beslissing 62). Niets wordt overschreven: een
betere versie wordt een nieuwe regel en de oude heet dan vervangen. Per molecuul is precies één versie
gedragen, en elke berekening gebruikt die of weigert.

**Hoe een anker het netwerk ijkt.** Het netwerk is voorgetraind op de opstap (laag 2). Daarna wordt
de kop een korte tijd bijgetraind op de ankers: dat heet **fijnafstemmen**. De romp blijft daarbij
staan. Om te meten hoe goed dat werkt, wordt het netwerk telkens afgestemd zonder het anker waarop
daarna wordt gemeten. Gemiddeld over de zes oudste ankers geeft het fijnafstemmen van de hele kop een
fout van 6,25 cm⁻¹ voor de trillingen uit het vlak. Dat is ongeveer de helft van de fout als alleen de
laatste laag van de kop wordt bijgesteld (13,69 cm⁻¹). Die metingen zijn gedaan met een eerdere netwerkversie (v1.1). De lat van
3 cm⁻¹ op CC-niveau wordt dus niet geclaimd.

**Het aantal ankers dat nodig is.** Elf ankers zijn te weinig om dat te meten. Het project deed daarom een
**generale repetitie** op proxyniveau, met honderden moleculen waarvan het antwoord bekend is:

1. train een netwerk op een bewust vervormde correctie, die verschilt van de echte zoals de
   CC-correctie op de ankers van de proxy verschilt;
2. stem het af op k moleculen met de echte correctie, voor k van 100 tot 200;
3. meet de fout op moleculen die in geen van beide stappen zaten.

De uitkomst: de ring in het vlak en de C–H-strek komen bij 100 moleculen binnen 3 cm⁻¹, C–H uit het
vlak bij ongeveer 167 (tussen 153 en 177), en "overig" niet binnen 200. De goedkoopste 167 ankers
zouden samen ongeveer 3.500 serveruren kosten, rond € 729 (de CC-Hessiaan en de CC-bandsterktes in
cc-pVDZ, zonder de MP2-stap). Het aantal 167 is een getal uit de repetitie, geen
CC-meting. Het zegt hoeveel voorbeelden een voorgetraind netwerk nodig heeft om naar een nieuwe
correctie te verschuiven.

Nieuwe ankers horen niet bij het afstudeerproject (beslissing 63). Hoe ze na juni 2027 worden gemaakt,
beslist de begeleider.

## §5.9 Wat er van Δ-probing overbleef

Het deck, de telling K en de licenties per probe zijn vervangen door het netwerk, de hold-outs en de
licentie per familie. Vier gedachten uit het oorspronkelijke plan bleven:

- **Δ in plaats van alles.** Het netwerk voorspelt alleen de correctie op een goedkope berekening, het
  verschil uit Definitie 1.2.
- **Lokaliteit.** Het vermoeden dat Δ₂ lokaal is, zit nu in de bouw van het netwerk: alleen paren van
  nabije coördinaten krijgen een getal.
- **Vastleggen vóór je meet.** Het bevroren plan schreef alle drempels op in een pilotnotitie vóór de
  eerste meting. Nu heeft elk experiment een pre-registratie met de voorspelling, de leesregel en wat
  als winst of verlies telt.
- **Eerlijk verliezen.** Het plan had voor elke mislukking een vooraf geschreven zin. Nu krijgt een
  familie die de lat niet haalt geen licentie, en het certificaat zegt dat bij elke band van die
  familie.

## In het kort

Het oorspronkelijke plan wilde de correctie Δ₂ per molecuul opmeten met weinig dure probes. Metingen
lieten zien dat één dure energie uren kost, en dat de correctie lokaal is en zich tussen moleculen
herhaalt. Daarom leert het project de correctie: het ΔH-netwerk voorspelt het verschil tussen een
goedkope en een betere Hessiaan van hetzelfde molecuul. Het werkt in lokale coördinaten, met een
equivariante romp die de omgeving van elk atoom leert en een kop die per paar coördinaten één getal
geeft. Het leert de vorm van de correctie op duizenden moleculen met ωB97X als opstap. Op twee
hold-outs blijven drie van de vier families onder 3 cm⁻¹. De elf CCSD(T)-ankers vormen de ijklaag; met
een eerdere versie geeft fijnafstemmen op die ankers ongeveer 6 cm⁻¹ voor de trillingen uit het vlak. Een
generale repetitie zegt dat zo'n 100 tot 167 ankers drie families binnen 3 cm⁻¹ zouden brengen.

*Bron: [README.md](../README.md) beslissingen 49, 50, 51, 55, 57, 59, 60, 61, 62, 63 en 65;
[Note_2026-10-05_Layers_of_Truth.md](../GoalGathering/notes/Note_2026-10-05_Layers_of_Truth.md);
[PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md](../GoalGathering/notes/PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md);
[PreRegistration_2026-09-23_E8_CC_Correction_Locality.md](../GoalGathering/notes/PreRegistration_2026-09-23_E8_CC_Correction_Locality.md);
de code van het netwerk (`m05/rungC_equivariant.py`, `m05/rungC_hybrid.py`); [MODELS.md](../modules/MODELS.md);
[ANCHORS.md](../modules/ANCHORS.md); de maten van v1.3 uit `m08/accuracy.py`;
[PreRegistration_2026-10-12_Anchor_Set_Three.md](../GoalGathering/notes/PreRegistration_2026-10-12_Anchor_Set_Three.md)
(de herhaling met de hele kop); [Design_2026-10-21_Few_Anchor_Proxy_Check.md](../GoalGathering/notes/Design_2026-10-21_Few_Anchor_Proxy_Check.md)
en [anchor_count_read.md](../modules/05_support_predictor/out/anchor_count_2026-10-29/anchor_count_read.md) (de generale
repetitie); `out/anchor_plan/count_n167.md` (de prijs); [TASKS.md](../TASKS.md) taak 140. Het oorspronkelijke
idee: [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md) §1 en §3.*
