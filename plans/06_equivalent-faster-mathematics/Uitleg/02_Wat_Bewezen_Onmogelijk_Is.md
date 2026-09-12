# Hoofdstuk 2 — Wat bewezen onmogelijk is

> **In dit hoofdstuk leer je**
> – wat de complexiteitsklassen P, NP en QMA betekenen, in gewone taal;
> – wat de drie artikelen van leesnotitie X0 precies bewijzen;
> – waarom die bewijzen de deur voor "in het algemeen" sluiten;
> – waarom ze de deur voor "voor onze moleculen" juist openlaten;
> – een ijkpunt: Hartree–Fock is al "hard" en toch routine.

---

## §2.1 Moeilijk, en moeilijk te controleren

In de informatica is een probleem "makkelijk" (klasse **P**) als een computer het in een tijd kan
oplossen die netjes meegroeit met de grootte van de invoer: twee keer zo'n groot molecuul, hooguit
een vast aantal keer zo lang rekenen. Een probleem zit in **NP** als je een *voorgestelde oplossing*
snel kunt controleren, ook al kun je hem misschien niet snel *vinden*. Sudoku is het schoolvoorbeeld:
een ingevulde sudoku controleren is makkelijk; hem oplossen is dat niet per se.

**QMA** is de kwantumversie van NP: een probleem waarvan een voorgestelde oplossing snel te
controleren is door een *kwantumcomputer*. De klasse is vermoedelijk nog groter en nog moeilijker
dan NP. Een probleem heet **QMA-compleet** als het tot de allermoeilijkste van die klasse hoort: kun je
dat ene probleem snel oplossen, dan kun je álles in QMA snel oplossen. Bijna niemand gelooft dat dat
kan.

## §2.2 De drie artikelen

**Kempe, Kitaev en Regev (2006).** Neem een systeem van n "qubits" (kwantumbits) met een
energiefunctie die een som is van stukjes die elk maar op twee qubits werken. Vraag: is de laagste
energie kleiner dan a of groter dan b? Zij bewijzen dat al dit "2-lokale" probleem QMA-compleet is.
Let op wat er staat: het gaat om *alle* zulke energiefuncties tegelijk, en om een nauwkeurigheid die
steeds fijner wordt naarmate het systeem groter is.

**Schuch en Verstraete (2009).** Zij brengen die hardheid over naar de echte
Schrödingervergelijking van elektronen. Hoe? Door een heel speciale "uitwendige potentiaal" te
bouwen — een rooster van deltafuncties met precies afgestemde magneetvelden — waarin de elektronen
zich gedragen als een bekend QMA-compleet model (het Hubbard-model). Gevolg: de "universele
functionaal" van de dichtheidsfunctionaaltheorie (DFT), die in theorie exact is, is QMA-hard om uit
te rekenen. Zij voegen er zelf aan toe dat dit DFT in de praktijk niet raakt, omdat daar een
*constante* nauwkeurigheid volstaat. In een appendix bewijzen ze nog iets: zelfs de veel eenvoudigere
Hartree–Fock-methode is al NP-compleet.

**Prodan en Kohn (2005)** hoort niet bij de onmogelijkheidsbewijzen; het is het artikel dat de deur
openzet. Dat komt in hoofdstuk 3.

## §2.3 Wat er nu precies dicht is

Een methode die voor **elke** uitwendige potentiaal (dus elk denkbaar molecuul en elk denkbaar
rooster) de grondtoestandsenergie geeft, in een tijd die netjes meegroeit, met een nauwkeurigheid
die steeds fijner wordt met de grootte — die bestaat niet, tenzij QMA gelijk is aan P. Niemand
verwacht dat. Plan 06 mag dus nooit beweren: "wij hebben een snellere exacte oplosser van de
Schrödingervergelijking." Wie dat beweert, heeft ongelijk voordat er getoetst is.

## §2.4 Wat er open blijft

Kijk nog eens naar de constructie van Schuch en Verstraete: een *ontworpen* potentiaal die een
berekening codeert. Geen enkel echt molecuul heeft zo'n potentiaal. De kernen van benzeen staan waar
de scheikunde ze zet, niet waar een informaticus ze zet om een sudoku in te bouwen. En de
nauwkeurigheid die plan 05 nodig heeft is een *constante* (een fractie van een golfgetal in de
kromming), niet iets dat steeds fijner moet met de grootte.

De stellingen gaan dus over het slechtste geval in een familie. Over de *klasse* van gapped,
gesloten-schil, aromatische moleculen bij evenwicht zeggen ze niets. Voor zo'n klasse kán een
methode bestaan die exact is (of exact tot een bewezen grens) en snel. Of die bestaat, is de open
vraag van plan 06.

## §2.5 Het ijkpunt: Hartree–Fock

Hartree–Fock is de eenvoudigste kwantumchemische methode en wordt elke dag op duizenden moleculen
gedraaid, in seconden tot minuten. Toch is hij in het slechtste geval NP-compleet. Dat leert iets
belangrijks: **slechtste-gevalcomplexiteit is niet wat de prijs van een echte berekening bepaalt.** De
prijs wordt bepaald door de constanten van de klasse waar je molecuul in zit. Die constanten zijn
meetbaar. Daar gaat hoofdstuk 3 over.

## §2.6 Eén zin om te onthouden

De wiskunde heeft bewezen dat "snel en exact voor alles" niet bestaat; ze heeft niets bewezen over
"snel en exact voor onze moleculen", en het voorbeeld van Hartree–Fock laat zien dat het verschil
tussen die twee in de praktijk enorm is.
