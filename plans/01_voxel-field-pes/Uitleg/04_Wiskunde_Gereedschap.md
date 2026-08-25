# Hoofdstuk 4 — Wiskundig gereedschap

> **In dit hoofdstuk leer je**
> – hoe je differentieert als er niet één maar honderden variabelen zijn;
> – wat het betekent dat een krachtenveld *conservatief* is, en waarom dat hier alles bepaalt;
> – drie manieren om een afgeleide te berekenen, en waarom er in dit project twee tegelijk worden gebruikt;
> – hoe een Fourier-transformatie van een beweging een spectrum maakt;
> – welke statistiek er nodig is om te bewijzen dat een resultaat geen toeval is.

---

## §4.1 Differentiëren met veel variabelen

Bij wiskunde B differentieer je functies $f(x)$ van één variabele. Het PES uit
hoofdstuk 3 is een functie van 9 variabelen (water) of 36 variabelen (benzeen:
$12 \times 3$ coördinaten). Het idee blijft hetzelfde.

> **Definitie 4.1 — Partiële afgeleide**
> De partiële afgeleide $\dfrac{\partial f}{\partial x_i}$ krijg je door te
> differentiëren naar $x_i$ en alle andere variabelen als constante te behandelen.

> **Definitie 4.2 — Gradiënt**
> De gradiënt is de vector van alle partiële afgeleiden:
> $$\nabla f = \left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \ldots, \frac{\partial f}{\partial x_n}\right).$$
> Hij wijst in de richting waarin $f$ het snelst toeneemt.

De kracht uit Eigenschap 3.1 is dus min de gradiënt van de energie. Voor benzeen
is dat een vector met 36 componenten: drie krachtcomponenten per atoom.

> **Voorbeeld 4.1**
> Neem een sterk vereenvoudigd PES van een tweeatomig molecuul:
> $E(x) = \tfrac12 k(x - x_0)^2$ met $k = 780\ \mathrm{N/m}$ en $x_0$ de
> evenwichtsafstand. Bepaal de kracht bij $x = x_0 + 0{,}01$ nm.
>
> *Uitwerking.*
> $$F = -\frac{\mathrm{d}E}{\mathrm{d}x} = -k(x - x_0) = -780 \times 1{,}0\times10^{-11} = -7{,}8\times10^{-9}\ \mathrm{N}.$$
> Het minteken betekent: de kracht wijst terug naar het evenwicht. Dat is de
> herstelkracht uit hoofdstuk 2.

## §4.2 De Hessiaan en de trillingsfrequenties

> **Definitie 4.3 — Hessiaan**
> De Hessiaan $\mathbf H$ is de matrix van alle tweede partiële afgeleiden:
> $$H_{ij} = \frac{\partial^2 E}{\partial x_i \partial x_j}.$$
> Voor benzeen is dat een $36 \times 36$-matrix.

De Hessiaan bevat alle veerconstanten tegelijk, ook de "kruisveren": hoeveel de
energie verandert als je twee atomen tegelijk verplaatst. Door de matrix te delen
door de wortels van de massa's en vervolgens de **eigenwaarden** te bepalen, krijg
je in één klap alle normaaltrillingen van hoofdstuk 2:

$$\tilde{\nu}_k = \frac{1}{2\pi c}\sqrt{\lambda_k},$$

waarin $\lambda_k$ de $k$-de eigenwaarde van de massagewogen Hessiaan is. Dit is de
snelle route naar een spectrum: één Hessiaan geeft alle bandposities. Het nadeel
is dat je zo alleen het *harmonische* antwoord krijgt (§2.8): de parabool-benadering,
die er enkele procenten naast zit.

## §4.3 Conservatieve krachtenvelden

Dit is het belangrijkste wiskundige begrip van het hele project.

> **Definitie 4.4 — Conservatief krachtenveld**
> Een krachtenveld $\mathbf F$ heet conservatief als de arbeid langs elke
> **gesloten** weg nul is:
> $$\oint \mathbf F \cdot \mathrm{d}\mathbf R = 0.$$
> Gelijkwaardig: $\nabla \times \mathbf F = \mathbf 0$, en gelijkwaardig: er
> bestaat een functie $E$ met $\mathbf F = -\nabla E$.

Bij natuurkunde ken je dit van de zwaartekracht: loop je een rondje en kom je
terug op je startpunt, dan heb je netto geen energie gewonnen of verloren.

**Waarom dat hier zo belangrijk is.** Stel je bouwt een computerprogramma dat
krachten voorspelt, maar dat die krachten *rechtstreeks* voorspelt in plaats van
ze uit een energie af te leiden. Dan is er geen enkele garantie dat
$\oint \mathbf F\cdot\mathrm{d}\mathbf R = 0$. Het molecuul kan dan langs een gesloten
baan energie winnen: een perpetuum mobile. In een simulatie van 50 picoseconde,
oftewel 100 000 tijdstappen, loopt zo'n foutje volledig uit de hand — het molecuul
warmt op of valt uiteen zonder fysische reden.

Het plan lost dit radicaal op. In [Distilled Plan §3](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
staat dat het netwerk **alleen een energie mag voorspellen**, nooit een kracht. De
kracht wordt daarna door de computer zelf afgeleid:

$$\mathbf F_A = -\frac{\partial E_\theta}{\partial \mathbf R_A}.$$

Omdat de kracht zo per constructie een gradiënt is, is
$\oint \mathbf F\cdot \mathrm{d}\mathbf R = 0$ **wiskundig gegarandeerd**, niet
gehoopt. In het plan heet dit "Route B" of "energy-first". Een eerdere versie van
het plan koos het omgekeerde ("Route A") en dat werd als de grootste
conceptuele fout van het hele ontwerp aangemerkt.

## §4.4 Afgeleiden numeriek benaderen

Soms heb je geen formule voor de afgeleide, maar kun je de functie wel op
willekeurige punten uitrekenen. Dan benader je.

> **Definitie 4.5 — Centrale differentie**
> $$f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}$$

De fout van deze benadering is van orde $h^2$: halveer je $h$, dan wordt de fout
vier keer zo klein. Maar je kunt $h$ niet onbeperkt verkleinen, want dan trek je
twee bijna gelijke getallen van elkaar af en verlies je nauwkeurigheid door
afrondingsfouten van de computer.

Daarom staat er in het plan overal dezelfde controle: reken de afgeleide uit bij
stap $h$ **én** bij stap $h/2$, en gebruik het verschil tussen die twee als
schatting van de numerieke onzekerheid. Die onzekerheid moet vervolgens kleiner
zijn dan één derde van de bijbehorende toetsingsdrempel. Dat is een nette,
controleerbare manier om te voorkomen dat een slordige afgeleide als "ruis in de
data" wordt weggeschreven.

## §4.5 Automatisch differentiëren

Er zijn drie manieren om aan een afgeleide te komen.

| Manier | Hoe | Nadeel |
|---|---|---|
| **Symbolisch** | Met de hand of via algebra de formule afleiden | Onmogelijk voor een netwerk met miljoenen parameters |
| **Numeriek** | Centrale differentie (§4.4) | Duur (twee berekeningen per variabele) en afrondingsgevoelig |
| **Automatisch** | De computer past de kettingregel toe op elke elementaire bewerking | Vereist dat de hele berekening als één keten is opgeschreven |

**Automatisch differentiëren** (in het plan: *autograd*) is exact, niet
benaderend. De computer onthoudt tijdens de berekening welke bewerkingen hij
uitvoert, en past daarna stap voor stap de kettingregel toe. Dat kost ongeveer
evenveel tijd als de berekening zelf, ongeacht het aantal variabelen.

In dit project worden numeriek en automatisch differentiëren allebei gebruikt, en
tegen elkaar afgezet. In de eisen voor fase 0 staat:

$$\lVert \mathbf F_{\text{autograd}} - \mathbf F_{\text{eindige differentie}} \rVert < 0{,}05\ \mathrm{meV/\text{Å}}$$

> **Let op — wat deze test wél en niet aantoont**
> Het plan waarschuwt uitdrukkelijk dat deze controle "blind" is voor een
> belangrijk probleem. Beide methoden lezen namelijk dezelfde, op een rooster
> gediscretiseerde energie. Als die energie zelf een systematische fout bevat,
> zullen beide methoden prachtig met elkaar overeenstemmen en allebei even fout
> zijn. De test controleert dus of de *afleiding* klopt, niet of de *energie*
> klopt.

Dat soort onderscheid — waar een test wel en niet gevoelig voor is — kom je in
deze repository voortdurend tegen.

## §4.6 Van beweging naar spectrum: Fourier

Een Fourier-transformatie ontleedt een signaal in tijd in de frequenties waaruit
het is opgebouwd. Je kent het idee van geluid: een akkoord ontleden in losse
tonen.

> **Definitie 4.6 — Fourier-transformatie**
> $$\hat{f}(\omega) = \int_{-\infty}^{\infty} f(t)\,e^{-i\omega t}\,\mathrm{d}t$$
> De uitkomst $\hat f(\omega)$ geeft aan hoe sterk frequentie $\omega$ in het
> signaal $f(t)$ aanwezig is.

In de praktijk meet je niet oneindig lang, maar gedurende een tijd $T$, en niet
continu maar met tussenstappen $\Delta t$. Dat legt twee grenzen op.

> **Eigenschap 4.1 — Resolutie**
> Meet je gedurende een tijd $T$, dan kun je twee frequenties alleen uit elkaar
> houden als ze meer dan $\Delta f = 1/T$ verschillen. In golfgetallen:
> $$\Delta\tilde\nu = \frac{1}{cT}.$$

> **Eigenschap 4.2 — Nyquist-grens**
> Met tijdstap $\Delta t$ kun je alleen frequenties tot $f_{\max} = 1/(2\Delta t)$
> correct waarnemen.

> **Voorbeeld 4.2 — Waarom de simulatie 50 ps duurt**
> Bereken de resolutie bij een simulatieduur van 1 ps en van 50 ps.
>
> *Uitwerking.*
> Voor $T = 1\ \mathrm{ps} = 1\times10^{-12}\ \mathrm{s}$:
> $$\Delta\tilde\nu = \frac{1}{2{,}998\times10^{10} \times 1\times10^{-12}} = 33\ \mathrm{cm^{-1}}.$$
> Voor $T = 50\ \mathrm{ps}$:
> $$\Delta\tilde\nu = \frac{1}{2{,}998\times10^{10} \times 5\times10^{-11}} = 0{,}67\ \mathrm{cm^{-1}}.$$
>
> **Conclusie.** Een simulatie van 1 ps geeft een resolutie van 33 cm⁻¹. Daarmee
> kun je onmogelijk beweren dat een band binnen 10 tot 15 cm⁻¹ klopt: je meetlat
> is grover dan de bewering. Bij 50 ps is de resolutie 0,67 cm⁻¹ en is de meetlat
> ruim fijn genoeg.
>
> Dit was een van de 23 punten van kritiek waarmee het oorspronkelijke plan werd
> afgeschoten. De simulatieduur is daarna van 0,5–1 ps naar 20–50 ps verhoogd.

> **Voorbeeld 4.3 — Waarom de tijdstap 0,5 fs is**
> De C–H-strektrilling zit rond $3030\ \mathrm{cm^{-1}}$. Hoeveel meetpunten per
> trillingsperiode levert een tijdstap van $0{,}5\ \mathrm{fs}$?
>
> *Uitwerking.*
> $$f = c\tilde\nu = 2{,}998\times10^{10}\times3030 = 9{,}1\times10^{13}\ \mathrm{Hz}
> \quad\Rightarrow\quad T_{\text{trilling}} = \frac{1}{f} = 1{,}1\times10^{-14}\ \mathrm{s} = 11\ \mathrm{fs}.$$
> Met $\Delta t = 0{,}5\ \mathrm{fs}$ zijn dat $11 / 0{,}5 \approx 22$ punten per
> periode. Ruim boven de Nyquist-grens van 2 punten, dus de snelste trilling in
> het molecuul wordt netjes bemonsterd.

## §4.7 Autocorrelatie

De laatste wiskundige schakel: hoe kom je van een simulatie naar een spectrum?

> **Definitie 4.7 — Autocorrelatiefunctie**
> $$C(t) = \langle \boldsymbol\mu(0)\cdot\boldsymbol\mu(t)\rangle$$
> Dit is het gemiddelde over de hele trajectorie van het inproduct van het
> dipoolmoment nu en het dipoolmoment $t$ later. Het is een maat voor: hoe goed
> "onthoudt" het dipoolmoment zijn eigen richting na verloop van tijd?

Als het molecuul netjes trilt met frequentie $f$, dan komt het dipoolmoment elke
periode $1/f$ ongeveer terug in dezelfde stand. De autocorrelatiefunctie vertoont
dan dezelfde periodiciteit. De Fourier-transformatie daarvan laat dus precies bij
die frequentie een piek zien.

> **Eigenschap 4.3 — Het spectrum uit een simulatie**
> $$I(\omega) \propto \omega \tanh\!\left(\frac{\beta\hbar\omega}{2}\right)\int_{-\infty}^{\infty}\langle\boldsymbol\mu(0)\cdot\boldsymbol\mu(t)\rangle\,e^{-i\omega t}\,\mathrm{d}t$$

De factor $\omega\tanh(\beta\hbar\omega/2)$ heet de **kwantumcorrectiefactor**.
Die is nodig omdat de simulatie klassiek is (Newton) terwijl echte moleculen
kwantummechanisch trillen. Het is een standaardcorrectie, geen uitvinding van dit
project.

Deze route heeft een groot voordeel dat je goed moet vasthouden: de trillingen
komen er **vanzelf** uit. Niemand vertelt het model welke frequenties het moet
produceren. Je laat het molecuul los in het geleerde energielandschap, kijkt hoe
het beweegt, en leest achteraf af welke frequenties in die beweging zaten. In het
plan heet dat een **emergent** resultaat.

## §4.8 De statistiek die je nodig hebt

Voor project 03 (hoofdstuk 9) en voor de eindvergelijking in project 08
(hoofdstuk 15) heb je een paar statistische begrippen nodig.

> **Definitie 4.8 — RMSE**
> De *root mean squared error* meet hoe ver voorspellingen $\hat y_i$ van de
> werkelijke waarden $y_i$ af liggen:
> $$\mathrm{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(\hat y_i - y_i)^2}.$$
> Het kwadraat zorgt ervoor dat grote fouten zwaarder tellen dan kleine, en dat
> plus- en minfouten elkaar niet opheffen. De eenheid is die van $y$ zelf.

> **Definitie 4.9 — Hypothesetoets**
> Je formuleert twee uitspraken:
> - $H_0$ (nulhypothese): er is géén effect;
> - $H_1$ (alternatieve hypothese): er is wél een effect.
>
> Je berekent vervolgens de kans $p$ dat je de waargenomen data zou zien *als $H_0$
> waar was*. Is die kans klein (gebruikelijk: $p < 0{,}05$), dan verwerp je $H_0$.

**Een valkuil die het plan zelf blootlegt.** Een hypothesetoets veronderstelt dat
je metingen ruis bevatten. De rekenmachine in dit project is echter volledig
**deterministisch**: dezelfde invoer geeft altijd exact dezelfde uitvoer. Twee keer
hetzelfde berekenen levert dus twee identieke rijen op, en daarop een
hypothesetoets loslaten is zinloos.

De oplossing die het plan koos, staat in
[`probes/issue14_sweep_design.py`](../probes/issue14_sweep_design.py): laat de
toevalligheid niet in de *meting* zitten maar in de **experimentele
omstandigheden**. Bij elke rij wordt het molecuul in een willekeurige stand
gedraaid, op een willekeurige plaats binnen een roostercel gezet en een
willekeurige thermische verbuiging gegeven. Dat is precies wat er in een echt
laboratorium ook gebeurt: het monster ligt elke keer net iets anders. De respons
is deterministisch, de omstandigheden zijn dat niet, en daarmee heeft de uitkomst
een echte verdeling.

> **Definitie 4.10 — Volledig factorieel ontwerp**
> Je onderzoekt meerdere factoren tegelijk en meet bij **alle** combinaties.
> Met 5 waarden voor factor A, 5 voor factor B en 2 voor factor C zijn dat
> $5 \times 5 \times 2 = 50$ combinaties, ook wel cellen genoemd.

Met zo'n ontwerp kun je een **twee-weg-variantieanalyse (ANOVA)** doen, waarmee je
niet alleen kunt toetsen of elke factor afzonderlijk effect heeft, maar ook of ze
elkaar **beïnvloeden** (interactie).

## §4.9 Overfitting en de driedeling van de data

Tot slot een begrip uit de machine learning dat overal terugkomt.

> **Definitie 4.11 — Overfitting**
> Een model dat de trainingsvoorbeelden uit het hoofd leert in plaats van het
> onderliggende patroon. Het presteert uitstekend op wat het gezien heeft en
> slecht op alles daarbuiten.

De standaardbescherming is de data in drieën splitsen:

| Deel | Waarvoor | Hoe vaak gebruikt |
|---|---|---|
| **Train** | Het model leert hiervan | Voortdurend |
| **Validatie** | Keuzes maken (welke instellingen zijn het best?) | Vaak |
| **Test** | De eindbeoordeling | **Precies één keer** |

Die laatste regel is in dit project keihard gemaakt. In
[Distilled Plan §7.1](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
staat: "The test set is touched once." Kijk je vaker, dan ga je — zelfs onbewust —
je keuzes aanpassen aan de test, en dan meet de test niets meer.

Dit project gaat nog een stap verder met de **leave-one-mode-out**-splitsing: één
hele familie trillingen wordt uit de trainingsdata gehouden. Het model heeft die
beweging dus nooit gezien. Dat is een veel strengere test dan een willekeurige
splitsing, want willekeurige punten uit dezelfde beweging lijken sterk op elkaar.

## In het kort

- Gradiënt = vector van alle partiële afgeleiden; kracht = min de gradiënt van de energie.
- De Hessiaan (tweede afgeleiden) geeft via zijn eigenwaarden alle harmonische trillingsfrequenties.
- Een krachtenveld dat uit een energie is afgeleid, is automatisch conservatief; daarom voorspelt het netwerk alleen energie.
- Numeriek differentiëren doe je met een centrale differentie, altijd gecontroleerd bij $h$ én $h/2$; automatisch differentiëren is exact en wordt ertegen afgezet.
- Fourier-resolutie is $1/(cT)$: 50 ps geeft 0,67 cm⁻¹, 1 ps slechts 33 cm⁻¹.
- Het spectrum volgt uit de Fourier-transformatie van de dipoolautocorrelatie, met een kwantumcorrectiefactor.
- Een hypothesetoets op een deterministische machine vraagt om ruis in de *omstandigheden*, niet in de meting.
- De testverzameling wordt precies één keer gebruikt.
