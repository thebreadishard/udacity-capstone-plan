# Begeleidend bericht bij het voorstel (27 september 2026, voor het gesprek van maandag 28 september) — voor de student om aan te passen en te versturen

*Concept, Nederlands. De brief zegt hoe het werkt en wat tot nu toe bewezen is; de getallen staan in het voorstel en zijn gedateerde
notities, waar elk ervan door een script is afgedrukt. Eerdere versies van dit bericht bestaan alleen in de git-geschiedenis.*

---

Beste [naam],

Dank voor de elf artikelen van 20 september; ze zijn gelezen en verwerkt, en twee ervan hebben één zin in het voorstel veranderd.
Hierbij, voor ons gesprek van maandag 28 september, het projectvoorstel voor de Udacity capstone: één lang document (ruim dertigduizend
woorden) met bovenaan een leeswijzer van twintig minuten. Ernaast staan twee openbare vensters op het werk: de Spectrum Atlas (https://thebreadishard.github.io/spectrum-atlas/),
een catalogus van de moleculen die de pijplijn kent, elk met zijn trede op de statusladder en de herkomst van elk getal, en het labjournaal
in blogvorm (https://thebreadishard.github.io/).

**Wat het plan belooft.** Een pijplijn die van een afzonderlijk aromatisch molecuul een infraroodspectrum maakt met een
coupled-cluster-anker — een klein aantal dure, nauwkeurige energieën en gradiënten dat de goedkope DFT-berekening corrigeert — met bij elk
spectrum een foutenbudget per bandfamilie dat zegt of het te vertrouwen is en wat het heeft gekost. De tweede belofte (§3.5) is een
netwerk dat op die labels wordt getraind en per bandfamilie wordt vrijgegeven of geweigerd, voor de PAK's waarvoor geen
laboratoriumspectrum bestaat. Jouw groep sloot in 2016 af met de hoop dat de anharmonische effecten zich over de PAK-familie laten
generaliseren zonder voor elk molecuul een volledig krachtveld te rekenen (Mackie et al. 2016, slotparagraaf); dit plan is één
antwoord op die hoop, voor het harmonische deel van het probleem.

**Hoe het werkt.** De coupled-cluster-correctie op de harmonische krachtconstanten reken ik niet volledig uit, maar schat ik uit een
klein aantal gerichte vervormingen van het molecuul, zoals je een curve uit een handvol meetpunten haalt. Bij elke vervorming hoort
één lokale coupled-cluster-berekening, waarvan ik de orbitaalruimtes één keer kies en daarna naar elke vervorming meeneem, zodat de
energieverschillen glad zijn. Het bevriezen van zulke ruimtes is een bekend recept (Mata & Werner
2006, sinds 20 september zo in §3.1); wat van mij is, is het transporteren van LNO-ruimtes, die geen atoomlijst hebben die je kunt
bevriezen, en het meten van wat dat kost. Het aantal energieën en gradiënten per molecuul staat naast elk spectrum; de nauwkeurigheid wordt
gescoord tegen laboratoriumdata en tegen de bestaande voorspellingen, waaronder die van jouw groep ("lijn B" in de meetlat).

**Wat tot nu toe bewezen is.** Vier dingen, elk met een vooraf opgeschreven leesregel; de getallen staan in §3.3, §3.5, §5.2 en §7.

1. *De labels zijn te maken en zijn schoon.* Het anker — naftaleen op cc-pVTZ, negentien energieën op mijn laptop — is voor drie
   bandfamilies uitgelezen: de goedkope basis draagt de correctie voor één van de drie, de andere twee blijven duur, met hun
   gemeten increment in de foutbegroting. De punten liggen glad op een curve tot ver onder wat het meetplan als ruis verdraagt, en
   de twee kationen hebben nu een gemeten prijs.
2. *Het plan vangt zijn eigen fouten.* Elke afgeleide grootheid krijgt een tweede route. Zo bleek een eerste anharmonische
   berekening ruis (het pakket meldde niets), en zo werd later een foute Hessiaan in het corpus gevonden. Beide zijn een vaste
   controle geworden; de verbeteringen aan de pakketten liggen als pull requests klaar en gaan pas de deur uit na een kwaliteitscontrole.
3. *De correctie is lokaal in de taal van bindingen en hoeken, en daar leert het netwerk haar.* In de basis van normaaltrillingen zijn
   de koppelingen onleerbaar; in bindingen en hoeken is dezelfde correctie dun en kort van bereik, tot ongeveer twee bindingen ver, en
   daar leert het netwerk haar uit 175 moleculen, ook op ringskeletten die het nooit zag. De coupled-cluster-correctie van benzeen
   leeft in datzelfde patroon, één binding verder dan de DFT-plaatsvervanger; de meting voor naftaleen loopt dit weekend af. In de
   taal van frequenties is de correctie juist níét lokaal (punt 4), en of "twee bindingen" bij grote moleculen klein is, meten de
   overdrachtstoetsen van het plan; van drie proxy-toetsen op gesubstitueerde en grotere moleculen slaagden er twee en bleef één
   halverwege steken, bij draaibare zijgroepen.
4. *Het meetplan is toetsbaar zonder nieuwe kwantumchemie.* Op het corpus, waar de volledige koppelingstabel bekend is, blijkt dat
   het dek van het voorstel buiten de band moet kijken en dat een geleerde meetvolgorde metingen bespaart; de verbreding en een
   stopregel zijn voorgeregistreerd voor na ons gesprek. Het dek in het voorstel staat nog zoals het was.

**Wat nog niet bewezen is.** Of het netwerk *genoeg* leert. Dat beslist de vooraf vastgelegde leercurve op de kleine-moleculenlaag
van het corpus (100 tot 1.200 moleculen, drie hold-outs), waarvan een eerste tussenstand zondagavond is gelezen en in §3.5 staat, en daarna
de echte coupled-cluster-labels. Een geleerde molecuulrepresentatie staat naast het paarmodel klaar met een vooraf vastgelegde
vergelijking; een eerlijke-kans-regel verbiedt een negatieve zin over welk model dan ook voordat de geregistreerde zoektocht is
doorlopen.

**Wat het kost.** Op mijn laptop is het plan haalbaar tot en met benzeen; naftaleen is de eerste trede die de laptop niet meer kan,
en gesubstitueerde moleculen vragen een goedkopere correlatietrap die eerst op benzeen gemeten wordt. De gemeten tijden staan in
§8; daarom staat de clusteraanvraag in §12 en §13.

**Wat ik van je vraag** staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7, de plekken waar de discipline
van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde spectra kent van pyreen, chryseen en trifenyleen in het
6–15 µm-gebied die mijn zoektocht heeft gemist; en (5) of je een Snellius-aanvraag wilt steunen, gedimensioneerd op de gemeten
tijden. Uit de artikelen kwamen twee kleine vragen: (14) of de naftaleen-QFF op CCSD(T)/cc-pVTZ uit het artikel van 2015 ooit is
gepubliceerd, en (18) welke referentie jij vertrouwt voor de kationen, gezien de spincontaminatie van de open-schil-referentie.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat in de repository:
https://github.com/thebreadishard/udacity-capstone-plan; de atlas en het labjournaal lezen uit dezelfde bestanden.

Groetjes,
Frederic

---

*Checklist voor het versturen:* de laag-B-lezing van zondagavond en het E8-naftaleenresultaat staan in §3.5 van de leeskopie;
instelling en rol in de kop ingevuld; de pdf of het md-bestand als bijlage; de repository-link alleen als de student dat wil.
