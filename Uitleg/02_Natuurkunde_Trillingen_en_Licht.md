# Hoofdstuk 2 — Natuurkunde: trillingen en licht

> **In dit hoofdstuk leer je**
> – hoe je de trillingsfrequentie van een chemische binding uitrekent;
> – wat een golfgetal is en waarom scheikundigen die eenheid gebruiken;
> – wat normaaltrillingen zijn en hoeveel een molecuul er heeft;
> – waarom sommige trillingen wél en andere géén infrarood licht absorberen;
> – waarom zwaarder waterstof (deuterium) het spectrum voorspelbaar verschuift.

---

## §2.1 Het massa-veersysteem

In de natuurkunde ken je het blokje aan een veer. Een veer met veerconstante $k$
oefent op een massa $m$ een kracht uit volgens de wet van Hooke:

$$F = -k\,x$$

waarin $x$ de uitwijking uit de evenwichtsstand is. Het minteken zegt dat de
kracht altijd tegengesteld is aan de uitwijking: de veer duwt terug. Dit levert
een **harmonische trilling** met frequentie

$$f = \frac{1}{2\pi}\sqrt{\frac{k}{m}}.$$

Een chemische binding gedraagt zich, voor kleine uitwijkingen, precies zo. De
"veer" is de binding, de veerconstante $k$ is een maat voor de sterkte van die
binding, en de massa's zijn die van de atomen.

## §2.2 Twee atomen aan één veer: de gereduceerde massa

Bij een blokje aan een veer zit één uiteinde vast aan de muur. Bij een molecuul
niet: beide atomen bewegen. Daarvoor bestaat een standaardtruc.

> **Definitie 2.1 — Gereduceerde massa**
> Voor twee massa's $m_1$ en $m_2$ die aan elkaar gekoppeld zijn, geldt
> $$\mu = \frac{m_1 m_2}{m_1 + m_2}.$$
> Het tweedeeltjesprobleem gedraagt zich dan als één deeltje met massa $\mu$ aan
> een vaste veer.

De trillingsfrequentie van een binding wordt dus

$$f = \frac{1}{2\pi}\sqrt{\frac{k}{\mu}}.$$

> **Voorbeeld 2.1**
> De O–H-binding in water heeft een veerconstante van ongeveer
> $k = 780\ \mathrm{N/m}$. Bereken de trillingsfrequentie.
> Gebruik $1\ \mathrm{u} = 1{,}6605 \times 10^{-27}\ \mathrm{kg}$,
> $m_\mathrm{O} = 16\ \mathrm{u}$ en $m_\mathrm{H} = 1\ \mathrm{u}$.
>
> *Uitwerking.*
> Eerst de gereduceerde massa:
> $$\mu = \frac{16 \times 1}{16 + 1} = 0{,}941\ \mathrm{u} = 1{,}563\times10^{-27}\ \mathrm{kg}.$$
> Dan de frequentie:
> $$f = \frac{1}{2\pi}\sqrt{\frac{780}{1{,}563\times10^{-27}}}
>      = \frac{1}{2\pi}\sqrt{4{,}99\times10^{29}}
>      = 0{,}1592 \times 7{,}06\times10^{14}
>      = 1{,}12\times10^{14}\ \mathrm{Hz}.$$
>
> Ter vergelijking: zichtbaar licht zit rond $5\times10^{14}\ \mathrm{Hz}$. Deze
> trilling zit er net onder — in het infrarood.

## §2.3 Het golfgetal

Scheikundigen werken zelden met hertz. Ze gebruiken het **golfgetal**.

> **Definitie 2.2 — Golfgetal**
> Het golfgetal $\tilde{\nu}$ is het aantal golflengtes dat in één centimeter past:
> $$\tilde{\nu} = \frac{1}{\lambda} = \frac{f}{c},\qquad
> \text{eenheid } \mathrm{cm^{-1}}\ (\text{"reciproke centimeter"}).$$
> Hierin is $c = 2{,}998\times10^{10}\ \mathrm{cm/s}$ de lichtsnelheid, uitgedrukt
> in centimeters per seconde.

Het golfgetal is recht evenredig met de energie van een foton
($E = hf = hc\tilde{\nu}$), en dat is de reden dat de eenheid zo populair is: je
kunt er direct energieverschillen mee aflezen.

> **Voorbeeld 2.2**
> Zet de frequentie uit Voorbeeld 2.1 om in een golfgetal en in een golflengte.
>
> *Uitwerking.*
> $$\tilde{\nu} = \frac{1{,}12\times10^{14}}{2{,}998\times10^{10}} \approx 3750\ \mathrm{cm^{-1}}.$$
> $$\lambda = \frac{1}{3750}\ \mathrm{cm} = 2{,}67\times10^{-4}\ \mathrm{cm} = 2{,}67\ \mathrm{\mu m}.$$
>
> De gemeten waarde voor water is $3756\ \mathrm{cm^{-1}}$. Het eenvoudige
> veermodel zit er dus minder dan een kwart procent naast — voor deze ene band.

**Merk op.** De marges in dit project worden altijd in cm⁻¹ gegeven. De eis
"banden binnen 10 tot 15 cm⁻¹" betekent, bij een band rond 3750 cm⁻¹, een
relatieve nauwkeurigheid van ongeveer $15/3750 = 0{,}4\%$.

De belangrijke PAK-banden liggen bij 3,3 μm (ongeveer 3030 cm⁻¹, de C–H-strek),
bij 6 tot 9 μm (de ringtrillingen) en bij 11 tot 12 μm (het buigen van C–H uit
het vlak). Die drie gebieden heten in hoofdstuk 18 de **bandfamilies**.

## §2.4 Normaaltrillingen

Een molecuul met meer dan twee atomen trilt niet op één manier maar op meerdere
manieren tegelijk. Toch valt elke willekeurige trilling te ontleden in een klein
aantal "zuivere" grondtrillingen.

> **Definitie 2.3 — Normaaltrilling (normal mode)**
> Een normaaltrilling is een bewegingspatroon waarbij alle atomen met dezelfde
> frequentie en in fase bewegen. Elke mogelijke trilling van het molecuul is te
> schrijven als een som van normaaltrillingen.

Dit is hetzelfde idee als bij een snaar: elke beweging van een gitaarsnaar is een
som van de grondtoon en de boventonen.

> **Eigenschap 2.1 — Aantal normaaltrillingen**
> Een molecuul met $N$ atomen heeft $3N$ bewegingsvrijheden. Daarvan gaan er 3 op
> aan verplaatsing van het hele molecuul (translatie) en 3 aan draaiing (rotatie).
> Er blijven over:
> $$3N - 6 \quad\text{normaaltrillingen (niet-lineair molecuul)}$$
> $$3N - 5 \quad\text{normaaltrillingen (lineair molecuul; er is één rotatie minder)}$$

> **Voorbeeld 2.3**
> Bepaal het aantal normaaltrillingen van $\mathrm{H_2O}$, $\mathrm{CO_2}$ en
> $\mathrm{C_6H_6}$.
>
> *Uitwerking.*
> - Water is gebogen, $N = 3$: $3\cdot3 - 6 = \boxed{3}$ trillingen.
> - Koolstofdioxide is lineair, $N = 3$: $3\cdot3 - 5 = \boxed{4}$ trillingen.
> - Benzeen is niet-lineair, $N = 12$: $3\cdot12 - 6 = \boxed{30}$ trillingen.

Die 30 kom je in het plan letterlijk tegen: bij benzeen wordt de verandering van
het dipoolmoment "voor alle 30 trillingsmodes" berekend
([Distilled Plan §5.1](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)).

De drie trillingen van water hebben vaste namen die je overal terugziet:

| Naam | Beweging | Gemeten golfgetal |
|---|---|---|
| $\nu_1$ | symmetrisch strekken: beide O–H tegelijk langer en korter | 3657 cm⁻¹ |
| $\nu_2$ | buigen: de H–O–H-hoek wordt groter en kleiner | 1595 cm⁻¹ |
| $\nu_3$ | asymmetrisch strekken: de ene O–H langer terwijl de andere korter wordt | 3756 cm⁻¹ |

## §2.5 Wanneer absorbeert een trilling licht?

Niet elke trilling is zichtbaar in een infraroodspectrum. Er geldt een strenge
regel.

> **Definitie 2.4 — Dipoolmoment**
> Het dipoolmoment $\boldsymbol{\mu}$ van een molecuul is een vector die aangeeft
> hoe de positieve en negatieve lading uit elkaar liggen:
> $$\boldsymbol{\mu} = \int \mathbf{r}\,\big(\rho_{\text{kern}}(\mathbf r) - \rho_{\text{elektron}}(\mathbf r)\big)\,\mathrm{d}V.$$
> Bij een symmetrisch molecuul is $\boldsymbol{\mu} = \mathbf 0$.

> **Eigenschap 2.2 — Selectieregel voor infrarood**
> Een normaaltrilling absorbeert alleen infrarood licht als het dipoolmoment
> tijdens die trilling **verandert**. In formule: de trilling is IR-actief als
> $$\frac{\mathrm{d}\boldsymbol{\mu}}{\mathrm{d}Q} \neq \mathbf 0,$$
> waarin $Q$ de uitwijking langs die normaaltrilling is.

De reden is dat licht een oscillerend elektrisch veld is. Zo'n veld kan alleen
energie overdragen aan iets dat er als een antenne op reageert — en een
veranderende ladingsscheiding *is* zo'n antenne.

> **Voorbeeld 2.4 — De verboden trilling van CO₂**
> Koolstofdioxide is lineair en symmetrisch: O=C=O. Bij de symmetrische strek
> ($\nu_1$) gaan beide zuurstofatomen tegelijk naar buiten en tegelijk naar
> binnen. Leg uit waarom deze trilling geen infrarood absorbeert.
>
> *Uitwerking.*
> Door de symmetrie blijft de ladingsverdeling links en rechts van het
> koolstofatoom op elk moment elkaars spiegelbeeld. Het dipoolmoment blijft dus
> gedurende de hele trilling exact nul:
> $\mathrm{d}\boldsymbol{\mu}/\mathrm{d}Q = \mathbf 0$. De trilling is
> **IR-inactief**, oftewel "verboden".
> De asymmetrische strek $\nu_3$ en de buiging $\nu_2$ zijn wél actief, want daar
> gaat de symmetrie verloren.

Deze verboden trilling is in dit project een **toets**. Als het geleerde model
$\mathrm{CO_2}$ correct heeft begrepen, moet die piek vanzelf bijna verdwijnen —
zonder dat iemand dat aan het model heeft verteld. De eis in het plan luidt:

$$\frac{I(\nu_1)}{I(\nu_3)} < 10^{-2}.$$

Precies nul kan het niet worden, omdat het rekenrooster (hoofdstuk 5) de
symmetrie van het molecuul een beetje breekt. Dat is een eerlijke erkenning die
in het plan expliciet wordt gemaakt.

## §2.6 Hoe sterk is een band?

De selectieregel zegt of een band bestaat. Hoe *sterk* de band is, volgt uit
dezelfde grootheid:

> **Eigenschap 2.3 — Intensiteit**
> $$I \propto \left|\frac{\mathrm{d}\boldsymbol{\mu}}{\mathrm{d}Q}\right|^{2}$$

Het kwadraat heeft een praktisch gevolg dat je in het plan terugziet.

> **Voorbeeld 2.5**
> Het plan eist dat de relatieve intensiteiten op ongeveer 10% kloppen. Hoe
> nauwkeurig moet $\mathrm{d}\boldsymbol{\mu}/\mathrm{d}Q$ dan zijn?
>
> *Uitwerking.*
> Als $I \propto x^2$, dan geldt voor kleine fouten
> $$\frac{\Delta I}{I} = 2\,\frac{\Delta x}{x}.$$
> Voor $\Delta I / I = 10\%$ volgt $\Delta x / x = 5\%$.
>
> En dat is precies de eis die in het plan staat: "relatieve fout in
> $\mathrm{d}\boldsymbol{\mu}/\mathrm{d}\mathbf{R}$ kleiner dan 5%". Het getal is
> dus niet uit de lucht gegrepen maar teruggerekend uit de gewenste
> eindnauwkeurigheid.

## §2.7 Het isotoopeffect

Vervang je in water beide waterstofatomen door **deuterium** (waterstof met een
extra neutron in de kern, symbool D of $^2$H), dan krijg je zwaar water
$\mathrm{D_2O}$. Chemisch is dat vrijwel hetzelfde molecuul: de elektronenwolk
verandert nauwelijks, dus de veerconstante $k$ blijft gelijk. Alleen de massa
verandert.

> **Voorbeeld 2.6**
> Bereken hoeveel de O–H-strek verschuift bij vervanging door O–D.
>
> *Uitwerking.*
> $$\mu_{\mathrm{OH}} = \frac{16\cdot1}{17} = 0{,}941\ \mathrm{u},\qquad
> \mu_{\mathrm{OD}} = \frac{16\cdot2}{18} = 1{,}778\ \mathrm{u}.$$
> Omdat $k$ gelijk blijft en $f \propto 1/\sqrt{\mu}$:
> $$\frac{f_{\mathrm{OH}}}{f_{\mathrm{OD}}} = \sqrt{\frac{\mu_{\mathrm{OD}}}{\mu_{\mathrm{OH}}}}
> = \sqrt{\frac{1{,}778}{0{,}941}} = \sqrt{1{,}890} \approx 1{,}37.$$
>
> De band verschuift dus van ongeveer 3750 cm⁻¹ naar ongeveer
> $3750 / 1{,}37 \approx 2730\ \mathrm{cm^{-1}}$: een **roodverschuiving**.

Dit is een van de mooiste controles in het hele plan, en wel om deze reden: in het
computermodel komt de massa van een atoom **nergens in het neurale netwerk voor**.
Het netwerk leert alleen de energie als functie van de standen van de kernen. De
massa komt pas later binnen, bij het toepassen van de tweede wet van Newton
($\mathbf a = \mathbf F / m$).

Verander je dus alleen het getal voor de massa van 1 u naar 2 u en verander je
verder helemaal niets — geen hertraining, geen nieuwe data — dan hoort de
verschuiving met factor 1,37 er vanzelf uit te komen. Het plan noemt als
acceptabele band 1,35 tot 1,39.

**Let op.** Het plan noemt deze test uitdrukkelijk *niet* het hoofdbewijs, maar een
"gezondheidscontrole". Bijna elk redelijk model haalt hem, dus hem halen bewijst
weinig; hem *niet* halen bewijst wel dat er iets fundamenteel mis is.

## §2.8 Waarom de veer niet helemaal klopt

Het veermodel uit §2.1 is een benadering. Een echte binding gedraagt zich als een
veer die makkelijker uitrekt dan indrukt, en die uiteindelijk breekt. De
bijbehorende energiekromme heet de **Morse-potentiaal**.

| Harmonisch model | Werkelijkheid (anharmonisch) |
|---|---|
| $E = \tfrac12 k x^2$, een perfecte parabool | Asymmetrisch, vlakt af bij grote uitrekking |
| Energieniveaus liggen op gelijke afstand | Niveaus komen bij hogere energie steeds dichter bij elkaar |
| Alleen de grondtoon is zichtbaar | Ook zwakke boventonen en combinatiebanden |
| Voorspelt frequenties enkele procenten te hoog | — |

Enkele procenten van 3750 cm⁻¹ is ruim 100 cm⁻¹ — veel meer dan de gewenste
marge van 10 tot 15 cm⁻¹. **Anharmoniciteit is dus niet verwaarloosbaar.**

Dat verklaart een keuze die anders raadselachtig zou zijn. In plaats van alleen
de veerconstante uit te rekenen, laat dit project het molecuul echt *bewegen* in
een simulatie (hoofdstuk 4 en 5). Een simulatie van de werkelijke beweging bevat
de anharmoniciteit automatisch, want ze rekent gewoon met het echte
energielandschap in plaats van met een parabool.

In project 11 (hoofdstuk 18) gaat men nog een stap verder en gebruikt men een
kwantummechanische methode voor de kernbeweging, GVPT2. Dat is nodig omdat een
klassieke simulatie de anharmoniciteit wel meeneemt, maar niet de
kwantumeigenschappen van de trilling zelf.

## In het kort

- Een binding trilt als een veer: $f = \frac{1}{2\pi}\sqrt{k/\mu}$, met $\mu$ de gereduceerde massa.
- Scheikundigen drukken frequenties uit in golfgetallen: $\tilde\nu = f/c$ in cm⁻¹.
- Een molecuul met $N$ atomen heeft $3N-6$ normaaltrillingen ($3N-5$ als het lineair is).
- Een trilling is IR-actief als het dipoolmoment erdoor verandert; de intensiteit is evenredig met $|\mathrm{d}\boldsymbol\mu/\mathrm{d}Q|^2$.
- Daaruit volgt: 10% nauwkeurigheid in intensiteit vraagt 5% nauwkeurigheid in $\mathrm{d}\boldsymbol\mu/\mathrm{d}Q$.
- Zwaar water verschuift de O–H-band met factor $\sqrt{\mu_{\mathrm{OD}}/\mu_{\mathrm{OH}}} \approx 1{,}37$; dat is een gratis controle op het model.
- Echte bindingen zijn anharmonisch; daarom wordt er gesimuleerd in plaats van alleen een veerconstante berekend.
