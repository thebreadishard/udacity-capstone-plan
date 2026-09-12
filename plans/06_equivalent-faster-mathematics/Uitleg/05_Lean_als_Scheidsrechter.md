# Hoofdstuk 5 — Lean als scheidsrechter

> **In dit hoofdstuk leer je**
> – wat een bewijsassistent is en waarin hij verschilt van een rekenprogramma;
> – wat Lean met de bibliotheek Mathlib vandaag kan, en wat niet;
> – waarom Lean in plan 06 scheidsrechter is en geen ontdekker;
> – wat het eerste, kleine formele doelwit zou zijn.

---

## §5.1 Een programma dat bewijzen controleert

Een gewoon rekenprogramma rekent getallen uit. Een **bewijsassistent** doet iets anders: je schrijft
een wiskundige bewering en een bewijs op in een formele taal, en het programma controleert regel voor
regel of het bewijs klopt. Als het programma "ja" zegt, staat de bewering vast met een zekerheid die
geen menselijke nakijker haalt. Als je een stap overslaat of een aanname vergeet, zegt het "nee" en
wijst het de plek aan.

**Lean 4** is zo'n taal en zo'n programma. **Mathlib** is de bibliotheek van wiskunde die er al in is
bewezen: getaltheorie, analyse, lineaire algebra, groepentheorie, combinatoriek — een groot deel van
de wiskunde van de eerste universiteitsjaren en meer.

## §5.2 Wat het kan, en wat niet

Kan: exacte uitspraken over eindig-dimensionale lineaire algebra (matrices, rang, symmetrische
vormen), over eindige groepen en hun werking op een ruimte, over grafen en kleuringen; met meer werk
ook het variatieprincipe van de kwantummechanica en de constructies van Hohenberg–Kohn en Levy in
een eindige basis.

Kan niet: rekenen met kommagetallen zoals een chemieprogramma dat doet (afrondingen zijn geen
wiskunde), kwantumchemie "doen", of — het belangrijkste — een snel algoritme *vinden*. Een
bewijsassistent verzint niets. Hij controleert wat jij (of een taalmodel) hem voorlegt.

## §5.3 Waarom dat precies is wat plan 06 nodig heeft

Kijk naar niveau E1 uit hoofdstuk 1: "identiek object, langs een andere weg". Een voorstel op dat
niveau is een stelling: "voor deze klasse geldt: als de amplitudes zó afvallen, dan is deze afkapping
exact tot ε." Zo'n uitspraak is waar of niet waar. Getallen van één molecuul kunnen hem niet
bewijzen; ze kunnen hem hoogstens onderuithalen. Lean kan hem wél afmaken — en dat is nodig, omdat
een voorsteller (mens of model) op een manier ongelijk kan hebben die een numerieke toets op benzeen
nooit laat zien.

Daarom heet dit hoofdstuk "scheidsrechter": Lean geeft geen snelheid. Hij geeft zekerheid over
*welke* kortere wegen niet fout kunnen zijn, zodat de zoektocht naar snelheid zich tot die wegen
beperkt.

Een eerlijke kanttekening over "de AI-tijd": modellen die met formele zoekmethoden werken, hebben
echte stellingen bewezen in smalle, goed geformaliseerde gebieden — olympiade-meetkunde is het
bekendste voorbeeld (Trinh en anderen, 2024). Dat is een aanmoediging voor de richtingen waar de
uitspraken schoon zijn (S1, S3, S5), en géén bewijs voor de richtingen waar de moeilijkheid numeriek
is (S2).

## §5.4 Het eerste formele doelwit

Klein, echt, en precies de algebra van plan 05's meetdeck: formaliseer een "meetoperator" als een
lineaire afbeelding van symmetrische M × M-matrices naar ℝ^q (q metingen), definieer het
kleuringsschema van Powell en Toint (1979), en bewijs dat het schema elke matrix met een gegeven
patroon van nullen exact terugwint. Dat is niveau E1 voor richting S5. Experiment X4 kijkt eerst na
wat Mathlib al heeft (grafen, kleuringen, symmetrische matrices), zonder nog iets te bewijzen.

Het ambitieuze doelwit — een klasse-beperkte lokaliteitsstelling voor correlatie-energieën — zou
nieuwe wiskunde zijn, met of zonder Lean. Formalisering zou daar het certificaat zijn, niet de
ontdekking.

## §5.4a Wat Mathlib al heeft (X4, nagekeken op 12 september 2026)

Experiment X4 is gedaan: we hebben de bibliotheek Mathlib doorzocht op wat er al bewezen is. De uitkomst
in één regel: **alles wat algebra is, staat erin; alles wat natuurkunde is, ontbreekt.** Aanwezig zijn
de spectraalstelling voor symmetrische matrices (eigenwaarden, gesorteerd, met een orthonormale basis van
eigenvectoren), de rang van een matrix met haar rekenregels, positieve operatoren en hun ordening, het
gelijktijdig diagonaliseren van commuterende symmetrische operatoren (precies de wiskunde achter de
symmetrie-blokken van plan 05), het variatieprincipe voor de laagste en hoogste eigenwaarde
(Rayleigh-quotiënt), en — verrassend — uitwendige machten met het inproduct dat chemici de
Slater-determinant-overlap noemen, inclusief de orthonormale basis van determinanten. Afwezig zijn de
min-max-stelling van Courant en Fischer voor de k-de eigenwaarde, de gulzige grafenkleuring die de telling
van experiment X1 nodig heeft, elke Hamiltoniaan, de Fock-ruimte, en de Schrödinger-operator zelf.

Gevolg: het kleine doelwit van §5.4 (het meetdeck van S5 exact bewijzen) is haalbaar met wat er is; een
E1-uitspraak in een eindige basis kan al *opgeschreven* worden; de lokaliteitsstelling kan nog niet eens
geformuleerd worden in Lean. Dezelfde avond is Lean met Mathlib geïnstalleerd (map `lean/`), en het eerste
stuk van het kleine doelwit is bewezen: een matrix met bekend nulpatroon wordt exact teruggewonnen uit één
matrix-vectorproduct per kleur van een geldige kleuring (stelling `recover_probe`, zonder `sorry`). Ook bewezen,
later dezelfde avond: de gulzige kleuringsgrens — een graaf met maximale graad Δ is met Δ+1 kleuren te
kleuren (die stelling zat niet in Mathlib) — en het gevolg dat Δ+1 metingen dus altijd genoeg zijn. En nog later
die avond ook de symmetrische verfijning: als een symmetrische matrix van elke kant gelezen mag worden, is
één leesbare kant per element genoeg. Het hele bestand bevat nu geen `sorry` (het Lean-woord voor "nog te
bewijzen") meer. Coleman en Moré (1984) is dezelfde avond gelezen: onze voorwaarde is woordelijk hun "symmetrisch
consistente partitie", en hun stelling 2.2 (geen tweekleurig pad van drie zijden) is het volgende Lean-doel.
Powell en Toint (1979) staat achter een betaalmuur en op de verzoeklijst voor de supervisor.

## §5.5 Eén zin om te onthouden

Lean vindt niets en versnelt niets; hij bewijst dat een voorgestelde kortere weg exact is, en dat is
in een ideeënplan waar modellen mogen voorstellen precies de rol die iemand moet spelen.
