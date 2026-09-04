# Hoofdstuk 5 — De motor: hoe het model in elkaar zit

> **In dit hoofdstuk leer je**
> – hoe je een elektronenwolk in een computer stopt;
> – waarom dat op de meest voor de hand liggende manier faliekant misgaat;
> – wat het "eierdooseffect" is en hoe je het meet;
> – hoe de energieformule van dit project is opgebouwd, stuk voor stuk;
> – wat er precies geleerd wordt en wat er is vastgelegd;
> – hoe uit dat alles een bewegend molecuul ontstaat.

Dit is het technische hart van het project. Neem er de tijd voor.

---

## §5.1 De elektronenwolk op een rooster

Een elektronendichtheid $\rho(\mathbf r)$ is een continue functie: op elke plaats
in de ruimte heeft ze een waarde. Een computer kan geen continue functie
opslaan, dus je legt er een rooster overheen en slaat op elk roosterpunt één
getal op.

> **Definitie 5.1 — Voxelrooster**
> Verdeel een kubusvormige doos in $N \times N \times N$ even grote blokjes met
> ribbe $\Delta x$. Elk blokje heet een **voxel** (van *volume element*, het
> driedimensionale broertje van de pixel). Sla per voxel één getal op: de
> gemiddelde dichtheid daar.

Let op wat er *niet* op het rooster staat: de kernen. Die houden hun eigen,
continue coördinaten $\mathbf R_A$ en bewegen dwars door de voxels heen. Het
rooster draagt als toestand uitsluitend elektronendichtheid — en na §5.3 alleen
nog het gladde deel daarvan. De kernen verschijnen er hooguit indirect, als een
potentiaal die bij elke berekening opnieuw uit $\mathbf R$ wordt gegenereerd
(§5.5).

In dit project:

| Molecuul | Rooster | $\Delta x$ | Doosribbe | Aantal voxels | Geheugen per configuratie |
|---|---|---|---|---|---|
| $\mathrm{H_2O}$ | $32^3$ | 0,20 Å | 6,4 Å | 32 768 | ongeveer 0,13 MB |
| $\mathrm{C_6H_6}$ | $64^3$ | 0,20 Å | 12,8 Å | 262 144 | ongeveer 1,0 MB |

> **Voorbeeld 5.1**
> Het plan wil circa 5000 benzeenconfiguraties opslaan. Hoeveel opslagruimte kost
> dat, als elk getal 4 bytes inneemt?
>
> *Uitwerking.*
> $$64^3 = 262\,144 \text{ voxels} \times 4\ \mathrm{byte} = 1{,}05\ \mathrm{MB}$$
> $$5000 \times 1{,}05\ \mathrm{MB} \approx 5{,}2\ \mathrm{GB}.$$
>
> Dat past nog op een gewone schijf. Het probleem van benzeen is dan ook niet de
> opslag maar de rekentijd om die 5000 configuraties überhaupt te bepalen
> (Voorbeeld 1.1).

## §5.2 Waarom het naïeve plan faalt

De voor de hand liggende aanpak is: zet de hele dichtheid $\rho$ op het rooster.
Dat werkt niet, en dat is gemeten in plaats van beweerd. Het programma
[`probes/issue07_grid_representability.py`](../probes/issue07_grid_representability.py)
rekent het na op een modeldichtheid van water.

De reden is de **cusp** uit §3.1: bij de kern is de dichtheid extreem scherp
gepiekt. Een rooster van 0,20 Å is veel te grof om zo'n piek te vangen. Het is
alsof je een naald fotografeert met pixels van een centimeter.

| Gemeten grootheid | Volledige $\rho$ op het rooster | Alleen de deformatie $\Delta\rho$ |
|---|---|---|
| Fout in het elektronenaantal | 11 % (eis: 0,01 %) | $3\times10^{-10}\ e$ |
| Energiesprong bij verschuiving over één cel | 3,8 hartree | $1{,}2\times10^{-9}$ hartree |
| Kunstmatige kracht | ongeveer $10^{6}$ meV/Å | $1{,}7\times10^{-3}$ meV/Å |

Kijk goed naar die eerste kolom. Een fout van 3,8 hartree is ruim 2000 kcal/mol.
De gewenste nauwkeurigheid was 1 kcal/mol. De methode zit er dus een factor
duizend naast — puur door de manier waarop de data is opgeslagen, nog voordat er
één neuron heeft leren rekenen.

En het gekke: fijner maken helpt nauwelijks. Bij $\Delta x = 0{,}05$ Å — zestien
keer zoveel voxels — zit je nog altijd 17 keer boven de norm, en het gedrag is
niet eens netjes dalend, maar springerig door een verschijnsel dat **aliasing**
heet.

## §5.3 De oplossing: de referentiesplitsing

De oplossing is elegant en volgt uit één observatie: het scherpe deel van de
dichtheid is **bekend en verandert nauwelijks**. Rondom een koolstofkern ziet de
elektronenwolk er vrijwel hetzelfde uit, of dat koolstofatoom nu in benzeen zit
of in methaan. Wat per molecuul verschilt, is alleen de zachte "lijm" tussen de
atomen: de bindingen.

> **Definitie 5.2 — Referentiesplitsing**
> Splits de dichtheid in twee stukken:
> $$\rho_{\text{tot}}(\mathbf r;\mathbf R) = \underbrace{\rho_{\text{ref}}(\mathbf r;\mathbf R)}_{\text{bekend, scherp}} + \underbrace{\Delta\rho_\theta(\mathbf r;\mathbf R)}_{\text{geleerd, glad}}$$
> waarin
> $$\rho_{\text{ref}}(\mathbf r;\mathbf R) = \sum_A \rho^{\text{atoom}}_{Z_A}\big(|\mathbf r - \mathbf R_A|\big)$$
> de **promoleculaire** dichtheid is: gewoon de dichtheden van losse, bolvormige
> atomen bij elkaar opgeteld. $\Delta\rho$ heet de **deformatiedichtheid**.

De promoleculaire dichtheid wordt niet op het rooster gezet. Elk atoom wordt
beschreven als een som van Gauss-functies:

$$\rho^{\text{atoom}}_{Z}(u) = \sum_k c_{Z,k}\left(\frac{\alpha_{Z,k}}{\pi}\right)^{3/2}e^{-\alpha_{Z,k}u^{2}}$$

en van Gauss-functies zijn alle benodigde integralen **exact** uit te rekenen met
een formule. Er komt geen rooster aan te pas, dus ook geen roosterfout.

De coëfficiënten $c_{Z,k}$ en $\alpha_{Z,k}$ worden één keer per element bepaald,
vastgelegd en daarna nooit meer veranderd. De eis is dat de fit het echte
atoom benadert met
$\int|\rho^{\text{fit}}_Z - \rho^{\text{atoom}}_Z|\,\mathrm{d}V / Z < 10^{-3}$.

**Wat blijft er over voor het rooster?** Alleen $\Delta\rho$: het verschil tussen
de echte moleculaire wolk en die stapel losse atomen. Dat verschil is glad —
geen cusps — en klein. Precies wat een rooster van 0,20 Å wél aankan.

Twee eigenschappen van $\Delta\rho$ die je moet onthouden:

1. **Ze mag negatief zijn.** Op plaatsen waar het molecuul minder lading heeft dan
   de losse atomen samen, is $\Delta\rho < 0$. Een eerdere versie van het plan
   dwong positiviteit af met een zogeheten softplus-functie; dat is geschrapt,
   want het duwde kernlading naar de verkeerde plek.
2. **Ze integreert exact tot nul:** $\int \Delta\rho\,\mathrm{d}V = 0$. Het molecuul
   heeft immers evenveel elektronen als de losse atomen samen. Dit wordt bij elke
   berekening afgedwongen door het gemiddelde af te trekken.

> **Voorbeeld 5.2 — Een onverwacht cadeau**
> Laat zien dat het dipoolmoment na deze splitsing veel eenvoudiger wordt.
>
> *Uitwerking.*
> Een stapel *neutrale, bolvormige* atomen heeft per atoom geen ladingsscheiding
> en dus per definitie dipoolmoment nul. In de formule
> $\boldsymbol\mu = \int \mathbf r(\rho_{\text{kern}} - \rho_{\text{tot}})\,\mathrm{d}V$
> vallen de kernbijdrage en de bijdrage van $\rho_{\text{ref}}$ dus exact tegen
> elkaar weg, en blijft over:
> $$\boldsymbol\mu = -\int \mathbf r\,\Delta\rho\,\mathrm{d}V.$$
>
> Het dipoolmoment — de grootheid waar het hele infraroodspectrum aan hangt — is
> dus een **rechtstreekse integraal over precies datgene wat het netwerk leert**.
> Onder de oude aanpak was het het verschil van twee veel grotere getallen (een
> factor 7 wegstreping bij water), en erger nog: het rooster droeg daar een
> netto lading van $+1{,}14\ e$, waardoor de uitkomst niet eens onafhankelijk was
> van waar je de oorsprong legde. Nagerekend in
> [`probes/issue11_12_observable_and_invariance.py`](../probes/issue11_12_observable_and_invariance.py).

## §5.4 Het eierdooseffect

Een rooster hangt stil in de ruimte; een molecuul niet. Schuif je een molecuul
langzaam over het rooster, dan liggen de kernen soms precies op een roosterpunt
en soms er precies tussenin. De berekende energie schommelt daardoor een beetje
mee, met de periode van het rooster.

> **Definitie 5.3 — Eierdooseffect (egg-box effect)**
> De kunstmatige, periodieke variatie van de berekende energie wanneer een
> molecuul stijf over het rooster wordt verschoven. De naam komt van het
> golvende oppervlak van een eierdoos.

Dit is puur een rekenfout: fysisch verandert er niets als je een vrij zwevend
molecuul een centimeter naar links schuift. Maar de computer denkt van wel, en
een energie die van plaats afhangt levert een **kracht** op — een kracht die er
niet hoort te zijn.

> **Voorbeeld 5.3 — Van energieschommeling naar kunstmatige kracht**
> Stel de schommeling is ongeveer sinusvormig met periode $\Delta x$ en met een
> piek-tot-piekamplitude $A$:
> $$E(\delta) \approx \frac{A}{2}\cos\!\left(\frac{2\pi\delta}{\Delta x}\right).$$
> Bepaal de grootste kunstmatige kracht.
>
> *Uitwerking.*
> $$F = -\frac{\mathrm{d}E}{\mathrm{d}\delta} = \frac{A}{2}\cdot\frac{2\pi}{\Delta x}\sin\!\left(\frac{2\pi\delta}{\Delta x}\right)
> \quad\Rightarrow\quad F_{\max} = \frac{\pi A}{\Delta x}.$$

Die eenvoudige formule heeft in dit project een fout van twee ordes van grootte
aan het licht gebracht.

> **Voorbeeld 5.4 — Waarom de oude eis onbruikbaar was**
> De oorspronkelijke eis luidde: eierdoosamplitude kleiner dan $10^{-4}$ hartree.
> Reken uit wat dat in krachteenheden betekent bij $\Delta x = 0{,}20$ Å.
> Gebruik $1\ \mathrm{hartree} = 27\,211\ \mathrm{meV}$.
>
> *Uitwerking.*
> $$F_{\max} = \frac{\pi \times 10^{-4}}{0{,}20}\ \frac{\mathrm{hartree}}{\text{Å}}
> = 1{,}57\times10^{-3}\ \frac{\mathrm{hartree}}{\text{Å}}
> = 1{,}57\times10^{-3}\times27\,211 \approx 43\ \mathrm{meV/\text{Å}}.$$
>
> De acceptatiedrempel voor het model was echter 1 meV/Å. De rekenmachine mocht
> zich dus 43 keer slechter gedragen dan het model dat erop getraind wordt. En
> omdat die machinefout in de oude opzet meetelde als "ruisniveau" waarboven de
> drempel gelegd mocht worden, werd de effectieve eis zelfs 128 meV/Å — meer dan
> honderd keer losser dan bedoeld. Nagerekend in
> [`probes/issue08_gate_consistency.py`](../probes/issue08_gate_consistency.py).

De reparatie draait de redenering om. Eerst leg je de eis aan het model vast
(1 meV/Å). Dan eis je dat de machine daar een factor 10 onder zit
(0,1 meV/Å). Pas daarna reken je met dezelfde formule terug wat dat betekent
voor de amplitude:

$$A = \frac{F_{\max}\,\Delta x}{\pi} = \frac{0{,}1/27\,211 \times 0{,}20}{\pi} \approx 2{,}3\times10^{-7}\ \mathrm{hartree}.$$

Dat is 427 keer strenger dan de oude eis, en het is alleen haalbaar dankzij de
referentiesplitsing uit §5.3, die 57 keer speelruimte overhoudt.

> **Kernbegrip — machinefout versus datafout**
> Het plan maakt een onderscheid dat je moet vasthouden:
>
> | Soort fout | Voorbeeld | Status |
> |---|---|---|
> | **Machinefout** | Eierdoos, Poisson-randfout, integratiefout | Een **bug met een plafond**. Repareren. Mag de drempel nooit verruimen. |
> | **Datafout** | Numerieke onzekerheid van een eindige differentie | Onvermijdelijk. **Alleen dit** mag de drempel verruimen. |
>
> De oude opzet gooide beide op één hoop. Het gevolg was pervers: een slechtere
> rekenmachine leverde een soepeler eindeis op.

## §5.5 De energieformule

Nu kunnen we de centrale formule van het project lezen:

$$E_\theta(\mathbf R) = \underbrace{\sum_A E^{\text{atoom}}_{Z_A}}_{\text{constant}} + \underbrace{E_{\text{es}}\big[\rho_{\text{ref}} + \Delta\rho_\theta, \mathbf R\big]}_{\text{vaste natuurkunde}} + \underbrace{\int \varepsilon_\theta\,\mathrm{d}V}_{\text{geleerd}}$$

Drie termen:

1. **De atomen apart.** Een constante per element; verandert niet als het molecuul
   beweegt en beïnvloedt de krachten dus niet.
2. **De elektrostatica $E_{\text{es}}$.** Aantrekking en afstoting van ladingen —
   de wet van Coulomb. Dit is bekende natuurkunde en wordt **niet geleerd**.
3. **De rest $\int\varepsilon_\theta\,\mathrm{d}V$.** Alles wat de klassieke
   elektrostatica niet vangt: kwantumeffecten zoals uitwisseling en correlatie.
   Dit is het enige stuk energie dat door het netwerk wordt geleerd.

Term 2 valt uiteen in zes stukjes, en elk stukje wordt daar uitgerekend waar het
nauwkeurig is:

| Stukje | Hoe berekend | Waarom daar |
|---|---|---|
| $E_{nn}$ (kern–kern) | Exact analytisch, $\sum_{A<B} Z_AZ_B/R_{AB}$ | Exact en gratis |
| $\rho_{\text{ref}}$ ↔ kernen | Analytisch | Grootste en scherpste term; nooit op een rooster |
| $\Delta\rho_\theta$ ↔ kernen | Op het rooster, tegen een uitgesmeerde kernpotentiaal | Glad × glad |
| $\rho_{\text{ref}}$ ↔ $\rho_{\text{ref}}$ | Analytisch | Dominante afstotingsterm |
| $\rho_{\text{ref}}$ ↔ $\Delta\rho_\theta$ | Op het rooster, tegen een analytische potentiaal | Glad × glad |
| $\Delta\rho_\theta$ ↔ $\Delta\rho_\theta$ | Hockney–Eastwood-oplosser | De enige term die een echte oplosser nodig heeft |

Let op de derde rij. Om de wisselwerking van $\Delta\rho$ met een puntlading op
een rooster uit te rekenen zou je moeten delen door $r$, en bij $r = 0$ gaat dat
mis. Daarom wordt de kern voor dít doel uitgesmeerd tot een Gauss-verdeling met
breedte $\sigma \ge 1{,}5\,\Delta x$:

$$V^{\sigma}_{\text{nucl}}(\mathbf r) = -\sum_A Z_A \frac{\operatorname{erf}\big(|\mathbf r - \mathbf R_A|/\sqrt2\sigma\big)}{|\mathbf r - \mathbf R_A|}$$

Deze functie is netjes eindig bij $r = 0$. Belangrijk detail: de kern–kernterm
$E_{nn}$ gebruikt deze uitgesmeerde vorm **niet**, want dan zou je er ongeveer
0,1 hartree naast zitten — een fout die het netwerk daarna zou moeten
"repareren", wat je nooit moet willen.

## §5.6 Waarom een speciale Poisson-oplosser

Voor de laatste rij in de tabel moet je uitrekenen hoe een ladingsverdeling met
zichzelf wisselwerkt. Dat is het oplossen van de vergelijking van Poisson, en dat
doe je snel met een Fourier-transformatie.

Maar de standaardaanpak veronderstelt dat de ruimte **periodiek** is: dat de doos
zich oneindig herhaalt, als een behangpatroon. Voor een kristal klopt dat. Voor
één zwevend molecuul niet: je molecuul zou dan een kunstmatige aantrekking
voelen tot oneindig veel kopieën van zichzelf.

> **Definitie 5.4 — Hockney–Eastwood-methode**
> Plaats de doos van $N^3$ voxels in een dubbel zo grote doos van $(2N)^3$ die
> verder met nullen is gevuld, en kap de Coulomb-kern af op de straal van de
> oorspronkelijke doos. Zo levert de snelle Fourier-methode toch het antwoord
> voor een **geïsoleerd** systeem.

Er is nog een meevaller. Omdat $\int\Delta\rho\,\mathrm{d}V = 0$ (§5.3), is de
ladingsverdeling die aan de oplosser wordt aangeboden netto neutraal. Het veld
eromheen dooft daardoor veel sneller uit dan bij een geladen verdeling, en er is
dus minder opvulruimte nodig. De reparatie van §5.3 maakt deze stap dus ook nog
goedkoper.

## §5.7 Wat wordt er eigenlijk geleerd?

Er zijn precies twee geleerde onderdelen.

**(a) De dichtheidscodeerder: $\mathbf R \to \Delta\rho_\theta$.**
Krijgt de standen van de kernen en produceert de deformatiedichtheid op het
rooster.

**(b) De energiedichtheid $\varepsilon_\theta$.**
Een piepklein netwerkje dat per voxel een energiedichtheid teruggeeft, die
vervolgens over de doos wordt geïntegreerd.

Bij (b) hoort een verbodslijst die het begrijpen waard is. $\varepsilon_\theta$
mag **uitsluitend** kijken naar plaatselijke, uit de dichtheid afgeleide getallen:
$\rho_{\text{ref}}$, $\Delta\rho_\theta$ en $|\nabla\Delta\rho_\theta|$. Verboden zijn:

- de kernlading $Z_A$ en het soort atoom;
- de lijst van bindingen;
- de ruwe kernposities $\mathbf R$;
- de elektrostatische potentiaal $\Phi$ en $V_{\text{nucl}}$.

Waarom die laatste? Omdat $\Phi$ vlak bij een kern vrijwel gelijk is aan
$Z_A / |\mathbf r - \mathbf R_A|$. Wie $\Phi$ mag zien, kan dus indirect aflezen
wélk atoom daar zit en waar het staat — en dan kan het netwerk de energie leren
zónder ooit naar de dichtheid te kijken. Dat is precies de sluiproute die de
onderzoeksvraag uit hoofdstuk 1 zinloos zou maken.

Om die sluiproute af te sluiten is er een verplichte controle: geef het model een
opzettelijk **verkeerde** dichtheid en kijk of de voorspelde energie inderdaad
verslechtert. Doet ze dat niet, dan gebruikt het model de dichtheid blijkbaar
niet echt.

## §5.8 NCA en FNO

De dichtheidscodeerder heeft twee soorten lagen.

> **Definitie 5.5 — NCA (neuraal cellulair automaat)**
> Elk voxel wordt herhaaldelijk bijgewerkt op grond van zijn eigen waarde en die
> van zijn 26 directe buren (een blokje van $3\times3\times3$). De regel is voor
> alle voxels dezelfde en wordt geleerd. Vergelijk het met Conway's *Game of
> Life*, maar dan met een regel die niet is bedacht maar getraind, en in drie
> dimensies.

Het aantrekkelijke van een NCA is dat het dezelfde regel overal toepast — net als
een natuurwet. Maar er is een probleem: informatie verplaatst zich per stap
slechts één voxel.

> **Voorbeeld 5.5**
> Een benzeenring is inclusief waterstofatomen ongeveer 5 Å breed. Hoeveel
> NCA-stappen zijn er minimaal nodig voordat het ene uiteinde van de ring "weet"
> wat er aan de andere kant gebeurt, en weer terug?
>
> *Uitwerking.*
> $$\frac{5\ \text{Å}}{0{,}20\ \text{Å per stap}} = 25\ \text{stappen heen}.$$
> Voor een wederzijdse aanpassing moet die informatie ook weer terug: ruim 50
> stappen. Het plan noemt daarom "60 stappen of meer" — te veel om nog fatsoenlijk
> te kunnen trainen.

Vandaar de tweede laag:

> **Definitie 5.6 — FNO (Fourier Neural Operator)**
> Een laag die het hele rooster in één keer naar het frequentiedomein
> transformeert, daar de componenten met geleerde gewichten vermenigvuldigt, en
> terugtransformeert. Omdat elke frequentiecomponent het hele rooster beslaat,
> koppelt één FNO-laag onmiddellijk alle voxels aan elkaar.

**Een veelgemaakte verwarring, die het plan expliciet uitsluit.** De FNO en de
Hockney–Eastwood-oplosser gebruiken allebei Fourier-transformaties, maar ze doen
iets totaal verschillends:

| | Hockney–Eastwood | FNO |
|---|---|---|
| Wat | Lost de vergelijking van Poisson op | Mengt informatie over het rooster |
| Vastgelegd of geleerd | Vastgelegd, natuurkunde | Geleerd |
| Waar | In de energieformule | In de dichtheidscodeerder |
| Mag de ander vervangen? | Nee | Nee |

De FNO is dus **geen geleerde Poisson-oplosser**. Zou je dat wel doen, dan zou je
in fase 0 iets valideren wat later stilletjes wordt vervangen.

## §5.9 De volledige voorwaartse berekening

Alles bij elkaar ziet één berekening er zo uit.

> **Stappenplan 5.1 — Van kernposities naar energie en krachten**
>
> **Invoer:** de posities $\mathbf R$ van alle atoomkernen en hun kernladingen $Z_A$.
>
> **Stap 1.** Plaats op elke kernpositie de bevroren, analytische atoomdichtheid.
> Dit levert $\rho_{\text{ref}}$. Er komt geen rooster aan te pas.
>
> **Stap 2.** Laat de codeerder (NCA, eventueel met FNO) de deformatiedichtheid
> $\Delta\rho_\theta$ op het rooster produceren. Trek het gemiddelde af, zodat
> $\int\Delta\rho_\theta\,\mathrm{d}V = 0$.
>
> **Stap 3.** Reken de zes elektrostatische stukjes uit §5.5 uit: vier
> analytisch, twee op het rooster, één daarvan met Hockney–Eastwood.
>
> **Stap 4.** Laat $\varepsilon_\theta$ per voxel een energiedichtheid teruggeven
> en integreer die over de doos.
>
> **Stap 5.** Tel alles op: dit is $E_\theta(\mathbf R)$, één getal.
>
> **Stap 6.** Laat de computer automatisch differentiëren (§4.5) om
> $\mathbf F_A = -\partial E_\theta / \partial \mathbf R_A$ te krijgen. Dit gaat
> door álles heen: door stap 1, 2, 3 én 4.
>
> **Uitvoer:** één energie (een getal) en één krachtvector per atoom (drie getallen
> per atoom).

Stap 6 verdient nadruk. Er wordt níét afgesneden bij $\Delta\rho$: de
afhankelijkheid van de dichtheid van de kernposities telt volledig mee. Dat is
wiskundig noodzakelijk, omdat de klassieke stelling van Hellmann en Feynman
(die zegt dat je die term mag verwaarlozen) alleen geldt voor een exacte
golffunctie — en niet voor een geleerde benadering.

## §5.10 Van krachten naar beweging

Heb je krachten, dan heb je beweging, via de tweede wet van Newton
$\mathbf a = \mathbf F/m$. De standaardmethode heet **velocity-Verlet**.

> **Stappenplan 5.2 — Eén tijdstap moleculaire dynamica**
> Met tijdstap $\Delta t = 0{,}5$ fs:
> 1. $\mathbf v(t + \tfrac12\Delta t) = \mathbf v(t) + \tfrac{\mathbf F(t)}{2m}\Delta t$
> 2. $\mathbf R(t + \Delta t) = \mathbf R(t) + \mathbf v(t+\tfrac12\Delta t)\,\Delta t$
> 3. Bereken $\mathbf F(t+\Delta t)$ met Stappenplan 5.1 op de nieuwe posities.
> 4. $\mathbf v(t + \Delta t) = \mathbf v(t+\tfrac12\Delta t) + \tfrac{\mathbf F(t+\Delta t)}{2m}\Delta t$

Deze methode is populair omdat ze de totale energie over lange tijd goed
behoudt — mits de krachten conservatief zijn (§4.3).

Het simulatieprotocol:

| Onderdeel | Waarde | Waarom |
|---|---|---|
| Tijdstap | 0,5 fs | 22 punten per snelste trilling (Voorbeeld 4.3) |
| Duur | 20–50 ps | Resolutie 0,67 cm⁻¹ (Voorbeeld 4.2) |
| Aantal trajectorieën | 5 tot 10, onafhankelijk | Eén trajectorie is geen experiment |
| Opwarmen | eerst NVT bij 300 K | Realistische beginsnelheden |
| Meten | daarna NVE | Behoud van energie is dan een controle |
| Aantal stappen | 40 000 tot 100 000 per trajectorie | $50\ \mathrm{ps}/0{,}5\ \mathrm{fs} = 10^5$ |

Tijdens die 100 000 stappen worden de netwerkgewichten **niet** aangepast. Ze
liggen vast ("frozen weights"). Het model heeft nooit een spectrum gezien en
wordt nooit op een spectrum bijgesteld; het spectrum is een gevolg, geen doel.

De energiedrift over de hele trajectorie moet onder 1% van $(3N-6)k_BT$ blijven —
de totale trillingsenergie die het molecuul geacht wordt vast te houden. Voor
water over 50 ps komt dat neer op $6\times10^{-7}$ hartree/ps. De oude eis van
$10^{-5}$ hartree/ps zou hebben toegestaan dat 18% van de trillingsenergie
onderweg verdampte.

## In het kort

- De elektronenwolk komt op een voxelrooster met $\Delta x = 0{,}20$ Å: $32^3$ voor water, $64^3$ voor benzeen.
- De volledige dichtheid past daar niet op: 11% fout in het elektronenaantal en 3,8 hartree kunstmatige energiesprong.
- Oplossing: splits in een bevroren, analytisch promolecuul plus een gladde deformatiedichtheid, en zet alleen die laatste op het rooster.
- Bijvangst: het dipoolmoment wordt exact $-\int\mathbf r\,\Delta\rho\,\mathrm{d}V$.
- Het eierdooseffect vertaalt zich naar kracht via $F_{\max} = \pi A/\Delta x$; de eis wordt teruggerekend uit de gewenste eindnauwkeurigheid, niet andersom.
- De energie bestaat uit een constante, vaste elektrostatica en één geleerde restterm; het netwerk mag alleen naar de dichtheid kijken.
- NCA werkt plaatselijk, FNO mengt globaal; de FNO is nadrukkelijk geen geleerde Poisson-oplosser.
- Krachten volgen via automatisch differentiëren, en daarmee is behoud van energie gegarandeerd.
