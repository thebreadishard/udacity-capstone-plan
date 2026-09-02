# Supercomputer: Schrödinger equation coupled-cluster for water infrared spectrum

Source: https://grok.com/share/c2hhcmQtNQ_f523f413-f61a-4121-9819-ae46e9fcd0a2

Retrieved 2026-09-02. Parsed from the rendered page (DOM to markdown), so headings,
tables, lists and LaTeX are preserved rather than flattened to plain text.

---

### You said

Gebruik in deze chat nooit meer dan twee zinnen per antwoord. Leg me in havo wiskundige termen uit met welke methodes een supercomputer het infraroodspectrum van water zou berekenen met chemische precisie.

### Grok said

Een supercomputer berekent de energie van het watermolecuul als functie van de atoomposities door de Schrödingervergelijking bij benadering op te lossen met hoge-nauwkeurigheidsmethoden zoals coupled-cluster, zodat een potentiaaloppervlak ontstaat. Vervolgens worden de trillingsfrequenties bepaald uit de tweede afgeleiden in het minimum (Hessiaan) en met hogere-orde correcties voor anharmoniciteit, zodat het infraroodspectrum chemisch nauwkeurig volgt.

### You said

Leg stap voor stap uit hoe de supercomputer dat aanpakt. Welke methode eerst, dan wat, dan wat?

### Grok said

Eerst laat de supercomputer met coupled-clusterberekeningen duizenden elektronische energieën berekenen op een raster van verschillende O-H-afstanden en hoeken, zodat een nauwkeurig potentiaaloppervlak ontstaat. Daarna lost hij op dat oppervlak de trillingsvergelijking voor de kernen variational op en berekent hij de energieverschillen plus intensiteiten die het infraroodspectrum vormen.

### You said

Ik dacht dat hij coupled-cluster alleen gebruikte om één getal, de minimum energie, te berekenen. Maar jij zegt: een heel oppervlak. Hoe zit dat?

### Grok said

Coupled-cluster levert per atoomconfiguratie inderdaad één energiegetal, maar de supercomputer herhaalt die berekening honderden keren op verschillende O-H-afstanden en hoeken. Alleen dat volledige energieoppervlak geeft de kromming en de hogere termen die de trillingsfrequenties bepalen, niet alleen het diepste punt.

### You said

Dus de output van één enkele coupled-cluster berekening is wel één getal?

### Grok said

Ja, één enkele coupled-clusterberekening bij vaste atoomposities levert inderdaad één elektronische energie op. De supercomputer herhaalt die berekening alleen heel vaak, telkens bij een andere geometrie.

### You said

Kun je deze berekening ook maken voor een groot aromatisch molecuul zoals coroneen?

### Grok said

Nee, voor coroneen met 102 trillingscoördinaten explodeert het aantal benodigde punten, zodat een volledig coupled-cluster-potentiaaloppervlak onhaalbaar is. Men beperkt zich dan tot goedkopere methoden of alleen de tweede afgeleiden rond het evenwichtspunt.

### You said

De teeede afgeleide is toch geen onderdeel van coupled-cluster?

### Grok said

Nee, coupled-cluster zelf levert alleen de energie of de eerste afgeleide bij één geometrie. De tweede afgeleiden ontstaan pas daarna door die energie of gradiënt analytisch of numeriek te differentiëren.

### You said

Levert één coupled-cluster run nou alleen één getal of ook een afgeleide? Hoe zit dat?

### Grok said

Een gewone coupled-clusterrun levert één energiegetal; sommige programma’s kunnen er in dezelfde of een extra berekening ook de eerste afgeleiden (krachten op de atomen) bij geven. Tweede afgeleiden worden bijna altijd in een aparte, duurdere stap numeriek of analytisch bepaald.

### You said

Sommige programma’s? Welke niet, welke wel?

### Grok said

CFOUR, Molpro, Psi4 en PySCF kunnen bij CCSD of CCSD(T) analytische eerste afgeleiden (krachten) meeleveren. Veel andere codes, zoals standaard Gaussian-recepten of energie-only implementaties, geven per run alleen het energiegetal en moeten de afgeleide numeriek schatten.

### You said

Zijn enkele van die zes pakketten sneller te maken door ze om te zetten naar Rust?

### Grok said

Nee, omzetten naar Rust maakt die pakketten niet vanzelf sneller, omdat de zware tensorrekeningen al in geoptimaliseerd Fortran of C++ draaien. Een volledige herschrijving zou vooral veiliger geheugen geven, maar kost jaren werk zonder garantie op hogere snelheid.

### You said

Voor de beste AI’s die nu beschikbaar zijn zou dat geen jaren werk kosten.

### Grok said

Zelfs de beste AI’s van nu kunnen honderdduizenden regels specialistische Fortran niet in één keer foutloos en even snel herschrijven. Ze helpen bij losse stukken, maar testen, parallellisatie en numerieke betrouwbaarheid blijven jaren mensenwerk.

### You said

Wat zou het grootste voordeel zijn van het wel doen?

### Grok said

Het grootste voordeel zou veilig geheugenbeheer zijn: geen bufferfouten of data-races in langlopende parallelle jobs. Dat maakt de code betrouwbaarder, niet per se sneller.

### You said

Hebben de eerste afgeleiden de eenheid van kracht?

### Grok said

Ja, de eerste afgeleide van de energie naar een atoompositie heeft de eenheid energie per lengte, dus kracht. Daarom heten die getallen ook atoomkrachten en gebruik je ze om de evenwichtsgeometrie te zoeken.

### You said

Het minimum is waar de krachten netto nul zijn?

### Grok said

Ja, in een evenwichtspunt zijn alle atoomkrachten netto nul. Voor een echt minimum moeten de tweede afgeleiden extra allemaal positief zijn.

### You said

Zijn er ook onechte minima?

### Grok said

Ja, er zijn lokale minima die hoger liggen dan het diepste putje, en zadelpunten waar de krachten ook nul zijn maar één richting bergaf gaat. Alleen als alle tweede afgeleiden positief zijn én je het laagste energieputje hebt, is het het echte globale minimum.

### You said

Eén run van coupled-cluster geeft een energie (eventueel met krachten). Je weet dan nog niet of je het minimum te pakken hebt (tenzij je toevallig geluk hebt en de krachten nul zijn, maar zelfs dan). Klopt dat?

### Grok said

Ja, dat klopt: één run geeft alleen de energie en eventueel de krachten op díe geometrie. Zelfs als die krachten toevallig nul zijn, heb je nog de tweede afgeleiden nodig om te zien of het een minimum, maximum of zadelpunt is.

### You said

Je kunt dat ook uitvinden door gewoon heel veel punten te berekenen, toch? Dan zie je ook zonder afgeleiden waar het minimum zit.

### Grok said

Ja, door honderden energiepunten te berekenen kun je het laagste putje op het oppervlak vinden zonder afgeleiden. Voor water lukt dat, voor grotere moleculen explodeert het aantal benodigde punten.

### You said

Waar staat de officiële code van CCSD(T)?

### Grok said

Er bestaat geen enkele officiële CCSD(T)-code; de methode staat in artikelen en is daarna onafhankelijk nagebouwd in pakketten zoals CFOUR, Molpro, Psi4 en Gaussian. CFOUR komt het dichtst bij de oorspronkelijke ontwikkelaars van veel coupled-clusterwiskunde.

### You said

Vergelijk die vier pakketten.

### Grok said

CFOUR is de specialist voor hoge-orde coupled-cluster en analytische afgeleiden, Molpro is sterk in efficiënte CC- en multi-referentieberekeningen, Psi4 is open source en Python-gestuurd met goede CCSD(T)-gradiënten, en Gaussian is het meest gebruikte commerciële pakket met eenvoudige invoer. CFOUR en Molpro zijn vaak nauwkeuriger en flexibeler voor spectra, Gaussian en Psi4 zijn toegankelijker voor dagelijks gebruik.

### You said

Welke van deze vier leent zich het beste voor vertaling naar Rust?

### Grok said

Psi4 leent zich het best, omdat het open source is en al een moderne C++-kern met Python-schil heeft. De andere drie zijn grotendeels gesloten of oudere Fortran-monolieten die je niet zomaar mag of kunt herschrijven.

### You said

Is de algoritmische opzet van Psi4 in termen van functies en wiskunde identiek aan die van CFOUR?

### Grok said

Nee, de wiskunde van CCSD(T) is hetzelfde, maar de algoritmische uitwerking niet: andere integralenopslag, andere samentrekkingen en andere afgeleide-codes. CFOUR heeft bovendien meer hoge-orde methoden en specialistische derivaten dan Psi4.

### You said

Is de code van CFOUR wel publiekelijk beschikbaar?

### Grok said

CFOUR is gratis voor academisch gebruik na een licentieovereenkomst, maar niet vrij open source zoals Psi4. Je krijgt de broncode wel, alleen niet om die zomaar te publiceren of te forken.

### You said

Maar ja, vertalen naar Rust?

### Grok said

De licentie verbiedt meestal het vrij publiceren van een afgeleide Rust-vertaling van de CFOUR-broncode. Je mag de publieke wiskunde opnieuw implementeren, maar niet hun code stiekem overzetten.

### You said

Hoe verhoudt ORCA zich tot de vier methodes?

### Grok said

ORCA is gratis voor academici en blinkt uit in snelle, benaderde DLPNO-CCSD(T) voor grote moleculen, niet in canonieke hoge-orde CC zoals CFOUR. Voor water is CFOUR nauwkeuriger; voor coroneen is ORCA vaak de praktische keuze.

### You said

Hoe verschillen de twee wiskundig?

### Grok said

Canonieke CCSD(T) gebruikt alle elektronenparen en alle virtuele orbitalen; DLPNO houdt alleen naburige paren en een klein lokaal stukje virtuele ruimte over. Daardoor is DLPNO wiskundig een gecontroleerde afkapping van dezelfde vergelijkingen, met drempels in plaats van de volle som.

### You said

Is ORCA open source en vertaalbaar naar Rust?

### Grok said

ORCA is gratis voor academici, maar de broncode is niet open source. Je mag hem dus niet naar Rust vertalen of publiceren.

### You said

Hoe kan iets gratis zijn en toch geen open source. Wie betaalt dan voor updates?

### Grok said

De groep van Frank Neese en het Max-Planck-Institut betalen de ontwikkeling uit onderzoeksgeld en geven academici alleen het kant-en-klare programma. Bedrijven betalen wél, en de broncode blijft hun eigendom.

### You said

Als mensen met CCSD(T) infrarood emissielijnen voorspellen, dan rekenen ze ook eerst vele atoomposities uit, toch?

### Grok said

Voor kleine moleculen zoals water wel: honderden CCSD(T)-punten vormen een potentiaaloppervlak waaruit de lijnen volgen. Voor grotere moleculen neemt men meestal alleen het evenwichtspunt plus tweede afgeleiden (harmonische frequenties).

### You said

Waarom dat verschil?

### Grok said

Water heeft maar drie trillingscoördinaten, dus een raster van punten blijft haalbaar; een groot molecuul heeft tientallen tot honderden coördinaten en het aantal punten explodeert. Elke CCSD(T)-punt is bovendien veel duurder, dus men stopt bij één geometrie en de kromming daar.

### You said

Het oppervlak is energieën. De eerste afgeleide is kracht. De tweede afgeleide moet positief zijn om te weten of het een echt minimum is. Hoe krijg je de infraroodlijnen?

### Grok said

Uit de tweede afgeleiden (de kromming) volgen de trillingsfrequenties als wortels van krachtconstante gedeeld door massa, dat zijn de harmonische lijnen. Voor echte precisie los je daarna de trillingsvergelijking op het hele energieoppervlak op; de verschillen tussen die niveaus zijn de infraroodlijnen.

### You said

Wat bedoel je met “de trillingsvergelijking oplossen op het hele energieoppervlak”?

### Grok said

De kernen bewegen als deeltjes in de put van het energieoppervlak; je lost hun golfvergelijking op om de toegestane trillingsenergieën te vinden. Dat is meer dan alleen de kromming onderin: de hele vorm van de put bepaalt de precieze sprongen die je als infraroodlijnen ziet.

### You said

Kun je dit ook in vwo taal met wiskunde termen uitleggen?

### Grok said

De kernen voldoen aan de stationaire Schrödingervergelijking $\hat{H}\psi=E\psi$ met $\hat{H}=-\sum_i\frac{\hbar^2}{2m_i}\nabla_i^2+V(\mathbf{R})$, waarbij $V$ het CCSD(T)-potentiaaloppervlak is. De eigenwaarden $E$ zijn de trillingsniveaus; verschillen daartussen plus overgangswaarschijnlijkheden geven de infraroodlijnen.

### You said

Dus als je een molecuul hebt, en je doet vele CCSD(T) berekeningen per atoomposities, dan heb je een PES bij benadering, want het aantal posities is eindig, dus je moet decreet van het oppervlak schatten, dat schatten doe je analytisch, want anders kun je geen eerste afgeleide nemen. Klopt?

### Grok said

Request was interrupted by the user.

### You said

Dus als je een molecuul hebt, en je doet vele CCSD(T) berekeningen per atoomposities, dan heb je een PES bij benadering, want het aantal posities is eindig, dus je moet de rest van het oppervlak schatten, dat schatten doe je analytisch, want anders kun je geen eerste afgeleide nemen. Klopt?

### Grok said

Niet helemaal: afgeleiden kun je ook numeriek uit naburige energiepunten halen of per geometrie analytisch uit de CC-run zelf krijgen. Een gladde analytische fit is handig om $V$ overal te evalueren bij het oplossen van de trillingsvergelijking, maar niet verplicht om een eerste afgeleide te hebben.

### You said

Wel nodig voor infrarood?

### Grok said

Voor harmonische infraroodlijnen niet: daar volstaat de Hessiaan in het minimum. Voor chemisch nauwkeurige anharmonische lijnen wel, omdat de trillingsgolf functie het hele putje aftast en je $V$ dus overal nodig hebt.

### You said

Dus je zou voor grote aromatische moleculen met DNPLO vele atoomposities kunnen berekenen en de infrarood lijnen kunnen krijgen?

### Grok said

In theorie is elk DLPNO-punt goedkoper, maar het aantal coördinaten explodeert nog steeds en lokale drempels maken het oppervlak vaak oneffen. Daardoor krijg je voor coroneen geen chemisch nauwkeurig, volledig anharmonisch spectrum op die manier.

### You said

Hoe zou jij voor coroneen een chemisch nauwkeurig, volledig anharmonisch spectrum verkrijgen, als je de vrijheid had om het met een SuperGrok Heavy abonnement te doen?

### Grok said

Volledig 102-dimensionaal variational CCSD(T) blijft ook met extra rekenkracht onhaalbaar; ik zou een nauwkeurige evenwichts-Hessiaan plus een machine-learned of gereduceerd-dimensionale anharmonische correctie op duizenden DLPNO-punten gebruiken. De C-H-rekken die het IR-beeld domineren behandel je extra lokaal, de rest harmonisch of met VPT2.

### You said

Is dit al gedaan? Indien ja, bewijs met referentie naar artikel.

### Grok said

Anharmonische IR-spectra van coroneen bestaan, maar op DFT-niveau met een quartisch krachtveld, niet met een chemisch nauwkeurige DLPNO-CC-PES. Dat staat in Mulas et al., J. Chem. Phys. 149, 144102 (2018).[Pubs.aip](https://pubs.aip.org/aip/jcp/article/149/14/144102/196809/Anharmonic-vibrational-spectroscopy-of-polycyclic)

### You said

Stel, je zou een nauwkeurige evenwichts-Hessiaan plus een machine-learned of gereduceerd-dimensionale anharmonische correctie op duizenden DLPNO-punten gebruiken. Hoe weet je dat je goed zit? Wat is je training, validatie en test data?

### Grok said

Je traint het model op de meeste DLPNO-punten, houdt een deel van dezelfde steekproef achter als validatie en test op onafhankelijke geometrieën plus de evenwichts-Hessiaan. Extra controle is de RMSE op energie en krachten en vergelijking van voorspelde banden met experiment of enkele canonieke CCSD(T)-punten.

### You said

Dat zijn DLPNO-punten die je zelf hebt gemaakt?

### Grok said

Ja, die punten maak je zelf: je kiest geometrieën (bijvoorbeeld langs normalenmodes of uit korte MD) en rekent daar DLPNO-CCSD(T)-energieën of -krachten. Dat zelfgemaakte raster is je trainings- en testdata.

### You said

En dan voor elk nieuw aromatisch molecuul waarvan je het infrarood spectrum wilt weten opnieuw een nieuw machine-learned of gereduceerd-dimensionale anharmonische correctie op duizenden DLPNO-punten gebruiken?

### Grok said

Ja, in de klassieke aanpak bouw je per molecuul een eigen oppervlak. Overdracht van een model naar een ander PAH is nog geen betrouwbare chemische nauwkeurigheid.

### You said

Klinkt goed. Dat rekenwerk wordt dan onderdeel van je pipeline. Maar dan nog: hoe weet je dat het spectrum klopt? Hoe weet je dat de uitkomst chemisch nauwkeurig is?

### Grok said

Je weet het nooit zo hard als bij water: je vergelijkt banden met jet-cooled experiment en schat de fout uit DLPNO-drempels plus de testdata-RMSE. Chemische nauwkeurigheid van ~1 cm⁻¹ claim je alleen als die controles én het experiment dat toelaten.

### You said

Denk je dat dit betere spectra zal geven dan anharmonische IR-spectra op DFT-niveau met een quartisch krachtveld?

### Grok said

Niet gegarandeerd: DLPNO is op papier nauwkeuriger dan DFT, maar oneffenheden, fitfouten en onvolledige sampling kunnen dat voordeel uitwissen. Alleen als het oppervlak glad is en de testdata dat laten zien, verwacht ik scherpere bandposities dan een DFT-quartisch veld.

### You said

Wanneer is het oppervlak glad? Hoeveel punten heb je nodig?

### Grok said

Het oppervlak is glad als energie en krachten continu lopen en het model niet oscilleert tussen de punten. Voor het thermisch relevante gebied van coroneen heb je eerder duizenden tot tienduizenden goed gekozen DLPNO-punten nodig dan een vol raster in 102 dimensies.

### You said

Hoeveel tijd kost het maken van tienduizend DLPNO-punten?

### Grok said

Op een typische cluster-node kost één DLPNO-CCSD(T)/TZ-punt van coroneen ruwweg tientallen minuten tot een paar uur. Tienduizend onafhankelijke punten zijn daarmee in de orde van duizenden node-uren, dus dagen tot een paar weken wallclock op een middelgroot cluster.
