# Hoofdstuk 12 — Project 05: het vlaggenschip op benzeen

> **In dit hoofdstuk leer je**
> – wat een gecontroleerd experiment in machine learning is;
> – waarom een natuurkundesimulator toch als "CNN" mag gelden;
> – wat er nieuw is aan dit werk, en wat aantoonbaar niet;
> – wat de stelling van Teller met dit project te maken heeft;
> – wat er gebeurt als de rekentijd tegenvalt.

**Categorie in het plan:** (A) natuurlijke aansluiting.
**Positie in de keten:** het grootste en duurste onderdeel; hangt af van de benzeencampagne.

---

## §12.1 Wat is de vraag?

De schoolopdracht: bouw met PyTorch een netwerk uit één van drie families (CNN,
RNN of Transformer) en voer minstens één **gecontroleerd vergelijkingsexperiment**
uit — een basisversie en een versie waarin precies één ding is veranderd.

De onderzoeksvraag eronder:

> De dichtheidscodeerder uit §5.7 bestaat uit plaatselijke NCA-lagen, eventueel
> aangevuld met een globale FNO-laag. **Levert die FNO-laag werkelijk iets op?**

Dat is geen bijzaak. In §5.8 stond de redenering dat een puur plaatselijk netwerk
meer dan zestig stappen nodig heeft om informatie één benzeenring over te
brengen. De FNO is de voorgestelde oplossing. Maar een redenering is geen bewijs,
en dus wordt het gemeten.

## §12.2 Invoer

| Kenmerk | Waarde |
|---|---|
| Molecuul | Benzeen, $\mathrm{C_6H_6}$ |
| Aantal configuraties | **Streefgetal** ≥ 5000 |
| Rooster | **Streefgetal** $64^3$, $\Delta x = 0{,}20$ Å |
| Vorm | Volumetrische tensoren (`.npz` of HDF5) + een manifest-CSV |
| Inhoud per configuratie | Kernposities, doel-$\Delta\rho$, CCSD(T)-energie, afgeleiden, analytisch dipoolmoment |
| Opslag | Extern gehost, met een DOI en toegangsinstructies |

Let op het woord **streefgetal**. Het plan is daar consequent in: 5000 en $64^3$
zijn doelen, geen beloftes. Ze worden pas beloftes nadat de kostenmeting uit fase
0b heeft laten zien dat ze haalbaar zijn (§12.6). De schoolopdracht staat
uitdrukkelijk toe dat een grote dataset extern wordt gehost, en daar wordt gebruik
van gemaakt.

## §12.3 Het gecontroleerde experiment

> **Definitie 12.1 — Gecontroleerd experiment**
> Twee trainingen die in **alles** gelijk zijn, behalve in precies één punt. Elk
> verschil in de uitkomst is dan aan dat ene punt toe te schrijven.

| Wat blijft gelijk | Wat verandert |
|---|---|
| De energieformule $\mathcal E$ | De codeerder: |
| De vaste elektrostatica $E_{\text{es}}$ | **A.** alleen plaatselijke NCA-lagen |
| De data, de splitsing, de startgetallen | **B.** plaatselijke NCA-lagen **plus** een FNO-laag |
| De verliesfunctie en de weegfactoren | |

De vraag is dus letterlijk: verbetert de niet-plaatselijke laag de voorspelde
dichtheid, en daarmee de energie en de krachten?

> **Wat dit experiment níét is**
> Het is niet de veld-tegen-graafvergelijking uit hoofdstuk 11. Dat is een ander
> experiment, met een ander model, in een andere werkstroom. Een graafnetwerk
> invoegen zou geen "één veranderde variabele" zijn maar een compleet andere
> voorstelling.
>
> Het is evenmin een test van de Poisson-oplosser. De FNO zit in de codeerder; de
> oplosser blijft de vaste Hockney–Eastwood-methode. Zou je de FNO als geleerde
> Poisson-oplosser inzetten, dan zou fase 0 iets valideren wat hier stilletjes
> vervangen wordt (§5.8).

## §12.4 De rubriekvraag: is dit wel een CNN?

Een beoordelaar zou kunnen denken dat hier een natuurkundesimulator wordt
ingeleverd om de opdracht te ontwijken. Het plan draagt daarom op om de
rechtvaardiging expliciet in het verslag te zetten.

> **De redenering**
> Een tweedimensionaal convolutioneel netwerk (CNN) voor beelden werkt zo: schuif
> een klein venstertje (bijvoorbeeld $3\times3$ pixels) over de afbeelding en pas
> overal dezelfde geleerde bewerking toe.
>
> De NCA-laag doet exact hetzelfde, maar in drie dimensies: een venstertje van
> $3\times3\times3$ voxels, met overal dezelfde geleerde bewerking. Dat *is* een
> driedimensionale convolutie. Het rooster is geen foto maar een elektronenwolk,
> en dat verandert niets aan de wiskunde van de laag.

Verder moeten er nog twee zinnen in het verslag staan, die uit
[Capstone_Mapping §5.2](../GoalGathering/Capstone_Mapping.md) komen:

1. **Route B expliciet noemen:** het netwerk voorspelt uitsluitend een energie; de
   krachten volgen door automatisch differentiëren (§4.3).
2. **Geen spectrale verliesterm:** getraind wordt alleen op statische grootheden.
   Elk spectrum dat elders wordt getoond, is een evaluatie achteraf met bevroren
   gewichten.

Daarnaast eist de opdracht een paragraaf **Ethiek en verantwoord gebruik** en het
tonen van minstens één concreet voorbeeld van modelgedrag: overfitting,
instabiliteit of een misser.

## §12.5 Wat is hier eigenlijk nieuw?

Dit is de vraag waarop de mondelinge verdediging (hoofdstuk 16) waarschijnlijk zal
draaien, en het plan bereidt het antwoord voor.

De eerste nieuwheidscontrole werd uitgevoerd in gesprekken met twee AI-systemen en
kwam met een geruststellend antwoord. Dat antwoord was fout, en de fout was
structureel: de formule $E = E_{\text{es}}[\rho] + \int\varepsilon_\theta\,\mathrm dV$
met een voorspelde $\rho$ **is** machine-geleerde orbital-free DFT — een
onderzoeksrichting met een geschiedenis van vijftien jaar.

> **Eerlijke opsomming: dit is niet nieuw**
> - een geleerde functionaal van $\rho$ (Snyder e.a., 2012);
> - het overslaan van de Kohn–Sham-vergelijkingen met een geleerde afbeelding
>   $\mathbf R \to \rho$ (Brockherde e.a., 2017);
> - moleculaire dynamica op zo'n model (idem, 2017);
> - het opschalen naar grotere systemen (M-OFDFT, 2024).
>
> Brockherde e.a. (2017) is het naaste voorwerk: zij leren $\mathbf R \to \rho \to E$
> en draaien er dynamica mee. Een examinator heeft één zoekopdracht nodig om daar te
> komen. Het plan zegt dan ook: noem het zelf, als eerste.

> **Wat er dan wél overblijft**
> De **combinatie** van vier dingen:
> 1. CCSD(T)-data in plaats van DFT-data;
> 2. een conservatieve energie waaruit de krachten via autograd volgen, in plaats
>    van een rechtstreeks gefitte energie-afbeelding;
> 3. infraroodbanden als emergente uitkomst bij bevroren gewichten;
> 4. een **vooraf geregistreerde** vergelijking met een equivariant graafnetwerk.
>
> En dan de zin die de eerlijkheid van dit plan het best samenvat: haalt een
> beoordelaar punt 4 weg, dan blijft er een stapsgewijze variatie op een bestaand
> vakgebied over. Dat is de eerlijke lezing, en het is nog steeds een scriptie.

## §12.6 De stelling van Teller: het echte risico

Er is een klassiek resultaat dat als een schaduw boven dit project hangt.

> **Eigenschap 12.1 — Stelling van Teller (1962)**
> In de zuivere Thomas–Fermi-theorie — een functionaal die uitsluitend naar de
> **plaatselijke** waarde van $\rho$ kijkt — binden moleculen helemaal niet. Er
> bestaat geen enkel molecuul.

Dat is geen detail maar een fundamenteel bezwaar. En kijk nu naar wat dit project
in eerste instantie bouwt: $\varepsilon_\theta$ mag uitsluitend naar plaatselijke,
uit de dichtheid afgeleide getallen kijken (§5.7). Dat is precies de vorm waarvan
bekend is dat hij het slechtst overdraagt. Het moderne M-OFDFT-werk uit 2024
moest **wezenlijke niet-plaatselijkheid** in de functionaal inbouwen om de
gewenste nauwkeurigheid te halen.

Het plan verdedigt zich met twee argumenten, en schrijft er eerlijk bij dat als
één van beide wegvalt, de vorm ook wegvalt:

1. **$\varepsilon_\theta$ is geen universele functionaal.** Hij hoeft niet voor
   alle moleculen te werken, maar alleen op een smalle strook: één molecuul, in
   thermisch bereikbare standen, met minstens 2000 voorbeelden. Op zo'n strook
   heffen systematische fouten tussen nabije standen elkaar grotendeels op.
2. **De referentiesplitsing verkleint zijn taak enorm.** Zonder splitsing zou de
   geleerde term het volledige bereik van ongeveer 76 hartree moeten overspannen
   (de totale energie van water). Met splitsing hoeft hij alleen de bindingsrest
   te leveren, ongeveer 1 hartree — een factor 76 minder.

En er ligt een **vooraf vastgelegde escalatieladder** klaar, zodat er later niet
stilletjes van vorm veranderd wordt:

| Trede | Wat er verandert |
|---|---|
| 1 | Plaatselijke $\varepsilon_\theta$ — de standaardkeuze |
| 2 | De verankeringsvorm omwisselen (zie hieronder) |
| 3 | **Niet-plaatselijke** $\varepsilon_\theta$ — de les van M-OFDFT |
| 4 | Een heel andere voorstelling (atomaire basis) — dat is een andere scriptie, dus horizon |

De cruciale regel: pas ná trede 3 mag het antwoord op de onderzoeksvraag negatief
worden genoemd. Een mislukking op trede 1 is een resultaat over
$\varepsilon_\theta$, niet over de veldhypothese.

> **De verankeringssplitsing (trede 2)**
> Er zijn twee manieren om de geleerde energieterm te definiëren:
> - **(i) verdwijnende verankering:** $\varepsilon_\theta$ is per constructie nul
>   waar $\Delta\rho = 0$. Dat verwijdert de kerngedomineerde bijdrage volledig.
> - **(ii) verschilvorm:** $\varepsilon_\theta = g_\theta(\rho_{\text{tot}}) - g_\theta(\rho_{\text{ref}})$.
>   Dat behoudt een echte functionaal van de totale dichtheid, maar de wegstreping
>   is numeriek in plaats van analytisch.
>
> Het plan kiest **niet** vooraf, maar schrijft een meting voor: bepaal in fase 0
> de integratiefout van beide vormen tegen een fijn referentierooster en kies dan.
> En het legt vast dat die keuze in fase 0 of P1 valt, **niet** in dit project —
> want twee varianten meeslepen naar de duurste run is precies hoe een
> gecontroleerd experiment ontspoort.

## §12.7 De krimpladder: wat als het niet past?

Benzeen is de grootste kostenpost van het hele plan (Voorbeeld 1.1). Daarom ligt
er een **vooraf** opgeschreven terugvalroute klaar, met de instructie: stop bij de
eerste trede die past.

> **Stappenplan 12.1 — De kostenkrimpladder**
> 1. Verklein het aantal benzeenconfiguraties: 5000 → 2000 → 1000. Het theorieniveau blijft.
> 2. Sla de dichtheid op $32^3$ op in plaats van $64^3$.
> 3. Neem de dichtheid van een goedkopere methode, terwijl energie en afgeleiden
>    CCSD(T) blijven. **Dit is een echte inbreuk op de nauwkeurigheidsbelofte** en
>    mag alleen met een schriftelijke uitzonderingsclausule.
> 4. De benzeencampagne wordt horizon. Project 05 moet dan opnieuw worden ingericht.

Daarnaast bestaat er een tweede, onafhankelijke ladder voor het geval het rooster
de deformatiedichtheid tóch niet aankan: fijner rooster → een extra geleerde
kernterm → een klein-kern-pseudopotentiaal → alleen water.

Het opvallende is dat deze laddering al vóór de meting is opgeschreven. Dat is
geen pessimisme maar methode: een terugvaloptie die je pas bedenkt nadat het is
misgegaan, is een improvisatie; een die je vooraf opschrijft, is een beslissing.

Het plan is over de verwachting trouwens opmerkelijk open. In
[Capstone_Mapping §8.3](../GoalGathering/Capstone_Mapping.md) staat de rekensom dat
het kritieke pad zonder de rekencampagnes al ongeveer 840 werkuren beslaat, oftewel
84 kalenderweken bij 10 uur per week. Daar moeten de campagnes nog bij. De
conclusie in het plan: dat de krimpladder in werking treedt, is **verwacht**.

## §12.8 Uitvoer

| Bestand | Inhoud |
|---|---|
| `deep_learning.ipynb` | Het notitieboek met beide varianten |
| `Deep_Learning_Systems_Analysis_Report.pdf` | Verslag, inclusief ethiekparagraaf en gedragsvoorbeeld |
| `requirements.txt` | Softwareversies |
| Toegangsinstructies | De dataset staat extern |

Voor het onderzoek: de bevroren gewichten van het benzeenmodel, plus het antwoord
op de vraag of de FNO-laag zijn kosten waard is — plus, bij voldoende budget, het
benzeenbeen van de veld-tegen-graafvergelijking.

## §12.9 Waarom deze stap?

Benzeen is de brug tussen "dit werkt op een watermolecuul" en "dit zou ooit voor
PAK's kunnen werken". Het is de kleinste aromatische ring en dus het kleinste
molecuul met de gedelokaliseerde $\pi$-elektronen die het hele probleem
interessant maken.

Het is ook de zwaarste test van de veldvoorstelling. Bij water zijn er drie
trillingen en een handvol vrijheidsgraden; bij benzeen dertig trillingen en een
elektronenwolk die zich over een hele ring uitstrekt. Als het idee ergens
zichtbaar voordeel moet opleveren, dan hier.

## In het kort

- **Invoer:** benzeentensoren, streefgetal 5000 configuraties op $64^3$, extern gehost met DOI.
- **Bewerking:** twee identieke trainingen die alleen verschillen in de aan- of afwezigheid van de FNO-laag.
- **Uitvoer:** het vlaggenschipmodel plus het antwoord op de vraag of niet-plaatselijke menging loont.
- De NCA-laag is een 3D-convolutie en valt dus in de CNN-familie; dat moet in het verslag worden onderbouwd.
- Wat nieuw is, is de combinatie — niet de energiefunctionaal op zich; dat wordt eerlijk opgeschreven.
- De stelling van Teller maakt de plaatselijke functionaal riskant; daarom ligt er een escalatieladder klaar, en telt alleen een mislukking op trede 3 als negatief antwoord.
- De krimpladder voor rekentijd is vooraf opgeschreven, en dat hij in werking treedt is de verwachting, niet de uitzondering.
