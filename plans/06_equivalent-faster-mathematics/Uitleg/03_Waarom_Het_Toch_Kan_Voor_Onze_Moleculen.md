# Hoofdstuk 3 — Waarom het tóch kan voor onze moleculen

> **In dit hoofdstuk leer je**
> – wat "bijziendheid" van elektronen is en wat Prodan en Kohn erover bewezen;
> – waarom de bandkloof de sleutel is, en waarom aromaten daar juist lastig zijn;
> – wat plan 05's lokale methode bij naftaleen werkelijk weggooit (het eerste eigen getal, X3a);
> – wat "de klasse karakteriseren" concreet betekent.

---

## §3.1 Bijziende elektronen

Stel je een groot molecuul voor en kijk naar één plek erin: de elektronendichtheid vlak bij één
koolstofatoom. Nu verander je iets ver weg, aan de andere kant van het molecuul — je zet er een
willekeurig sterke storing neer. Hoeveel verandert de dichtheid bij jouw atoom?

Walter Kohn noemde het antwoord "nearsightedness of electronic matter", de bijziendheid van
elektronen: verrassend weinig, en steeds minder naarmate de storing verder weg staat. Prodan en Kohn
(2005) maakten dat kwantitatief. Voor systemen met een **bandkloof** — een energieverschil tussen de
hoogste bezette en de laagste onbezette toestand, zoals isolatoren en gesloten-schilmoleculen — valt
het effect **exponentieel** af met de afstand: elke vaste extra afstand deelt het effect door
hetzelfde getal. De afvalsnelheid wordt bepaald door de kloof: een grote kloof geeft een snel
afvallend, kort bereik; een kleine kloof een lang bereik. Voor metalen (geen kloof) valt het maar
langzaam af, als een macht van de afstand.

Belangrijk detail dat in de leesnotitie staat: het bewijs geldt voor niet-wisselwerkende fermionen
en gaat over de dichtheid. Dat correlatie-*energieën* net zo bijziend zijn, is de werkaanname van
elke lokale coupled-cluster-methode; de literatuur controleert dat numeriek, niet met een bewijs.

## §3.2 Waarom dit de reden is dat lokale methoden werken

Plan 05 gebruikt LNO-CCSD(T): een lokale variant die het molecuul in fragmenten knipt en per fragment
alleen de orbitalen meeneemt die er echt toe doen. Dat werkt omdat elektronen bijziend zijn. Hoe
sneller het effect afvalt, hoe kleiner elk fragment kan zijn en hoe minder de berekening kost als het
molecuul groeit.

En hier zit de adder: **aromaten hebben een kleine kloof.** De π-elektronen van benzeen, naftaleen en
grotere platte koolstofvlokken zijn juist de elektronen met de kleinste kloof en dus het langste
bereik. Voor een verzadigd molecuul (alkaan) begint lokaliteit snel te lonen; voor een aromaat pas
later. De klasse waar plan 05 voor gebouwd is, is dus precies de klasse waar lokaliteit het traagst
werkt.

## §3.3 Het eerste eigen getal: X3a

Dat is geen vermoeden meer, want plan 05 heeft het al gemeten zonder het te weten. In de log van de
naftaleen-timing (11 september 2026) staat per fragment hoeveel orbitalen de lokale methode bewaarde
bij de strengste instelling ("tight"):

| wat | bewaard per fragment |
|---|---|
| actieve bezette orbitalen (24 in totaal) | 22 tot 24, dus 92 tot 100 % |
| virtuele orbitalen (378 in totaal) | 44 tot 84 %, gemiddeld 56 % |

Lees dat zo: bij naftaleen ziet elk fragment nog vrijwel het hele molecuul in de bezette ruimte.
Lokaliteit heeft daar nog niet eens *begonnen* te betalen; alleen de virtuele ruimte wordt ongeveer
gehalveerd. De energie van 11,5 uur is de prijs van een molecuul dat nog geen voordeel heeft van
zijn eigen bijziendheid. Dat klopt precies met wat de kleine π-kloof voorspelt.

## §3.4 De klasse karakteriseren

"Voor onze klasse" is pas een bruikbare uitspraak als je zegt wat de klasse *is*. Uit hoofdstuk 2 en
dit hoofdstuk volgen de parameters:

- de **bandkloof** en de daaruit volgende **afvalconstante** (hoeveel ångström per factor e);
- de **nauwkeurigheid**: een constante, gezet door plan 05's foutbudget, niet iets dat meegroeit;
- de **geometrie**: vlak, geconjugeerd, gesloten-schil, bij evenwicht.

De afvalconstante is een eigenschap van de klasse, niet van één molecuul. Wie hem eenmaal meet op
kleine aromaten, weet iets over de hele ladder van plan 05. Dat is experiment X3b: de
correlatie-energie per *paar* gelokaliseerde orbitalen uitzetten tegen hun afstand, een rechte lijn
fitten op logaritmische schaal, en de helling aflezen. Het script staat klaar en draait zodra de
laptop vrij is.

## §3.4a Toevoeging 12 september 2026 (avond): de stellingen achter de bijziendheid, en wat ze over onze ladder zeggen

De bijziendheid van §3.1 is niet alleen een natuurkundig principe; voor matrices is het een bewezen
stelling. In het overzichtsartikel van Benzi, Boito en Razouk (2013, gelezen in de open versie) staat
het zo: neem een Hamiltoniaan die alleen buren koppelt (een "dunne" matrix, met een graaf waarin elk
atoom hooguit een vast aantal buren heeft), met een bandkloof die niet dichtgaat, en neem er een nette
functie van — bijvoorbeeld de dichtheidsmatrix, die zegt waar de elektronen zitten. Dan vallen de
elementen van die functie **exponentieel af met de grafafstand**: het aantal bindingen dat je moet
volgen om van het ene atoom bij het andere te komen. De constanten hangen niet van de grootte van het
molecuul af, en de afvalsnelheid is in eerste benadering **evenredig met de bandkloof**. Het bewijs is
verrassend elementair: een nette functie is goed te benaderen door een polynoom (stelling van
Bernstein), en een polynoom van graad k in een matrix die alleen buren koppelt, koppelt alleen atomen
die hooguit k bindingen uit elkaar liggen.

Drie dingen volgen daaruit voor plan 06.

1. **Grafafstand, niet ångström.** Experiment X5 vond de benzeenring "vlak": meta- en para-paren even
   groot als gebonden paren. In bindingen geteld zijn dat afstanden 2 en 3 — kleine getallen, precies
   waar de stelling nog weinig afval voorspelt. De vlakke ring is geen tegenvoorbeeld voor lokaliteit;
   het is lokaliteit gemeten in de verkeerde maat. Naftaleen (grafafstand tot 5) is het eerste molecuul
   dat een helling kan laten zien.
2. **De kloof krimpt langs onze eigen ladder.** Grote PAK's hebben een kleinere bandkloof dan benzeen;
   dus wordt de bijziendheid *zwakker* juist richting de grote moleculen waar plan 05 hem het hardst
   nodig heeft, en de stelling zegt ook hoe snel: evenredig met de kloof. Bij een kloof die naar nul
   gaat (een metaal) blijft er alleen een machtswet over. Experiment X7 (afvalconstante tegen kloof
   voor benzeen, naftaleen, pyreen) toetst die voorspelling.
3. **Het vermoeden T3, en waarom het niet genoeg is.** T3 zegt: onder deze aannames vallen de
   atoompaar-blokken van onze correctie Δ₂ exponentieel af met de grafafstand. Een bewijsplan is
   geschreven (notitie van 12 september): welke aannames wij vervullen (buren: ja; een kloof die niet
   dichtgaat: nee, niet langs de hele ladder), welke stappen stelling zijn en welke nieuw (de stap
   van de dichtheidsmatrix naar de correlatie-energie, en van de energie naar haar tweede afgeleide,
   zijn voor coupled cluster door niemand opgeschreven). Maar er is een addertje: T3 zegt alleen dat
   *beide* Hessianen (CC en DFT) afvallen, en dus ook hun verschil. Waar plan 05 iets aan zou hebben,
   is de sterkere uitspraak **T3′: de correctie valt sneller af dan elk van de twee**, omdat het
   langeafstandsdeel (elektrostatisch, gemiddeld-veld) in het verschil wegvalt. Daar is nog geen enkel
   getal voor; experiment X9 (minuten, op de bestaande benzeen-data) zet de blokprofielen van de
   DFT-Hessiaan en van de correctie naast elkaar.

## §3.5 Eén zin om te onthouden

Elektronen zijn bijziend, met een bereik dat door de bandkloof wordt gezet; aromaten hebben een
kleine kloof en dus een lang bereik, en bij naftaleen betaalt lokaliteit zich nog nauwelijks uit —
de snelheid waarmee dat verandert is het eerste getal dat plan 06 zelf gaat meten.
