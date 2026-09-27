# Begeleidend bericht bij het voorstel (27 september 2026, voor het gesprek van maandag 28 september) — voor de student om aan te passen en te versturen

*Concept, Nederlands. De brief zegt hoe het werkt en wat tot nu toe bewezen is; de getallen staan in het voorstel en zijn gedateerde
notities, waar elk ervan door een script is afgedrukt. Eerdere versies van dit bericht bestaan alleen in de git-geschiedenis.*

---

Beste [naam],

Dank voor de elf artikelen van 20 september; ze zijn gelezen en verwerkt, en twee ervan hebben één zin in het voorstel veranderd.
Hierbij, voor ons gesprek van maandag 28 september, het projectvoorstel voor de Udacity capstone: één document van ongeveer
dertig pagina's. Ernaast staan twee openbare vensters op het werk: de Spectrum Atlas (https://thebreadishard.github.io/spectrum-atlas/),
een catalogus van elk molecuul dat de pijplijn heeft aangeraakt met zijn status en de herkomst van elk getal, en het labjournaal
in blogvorm (https://thebreadishard.github.io/).

**Wat het plan belooft.** Een pijplijn die van elk afzonderlijk aromatisch molecuul een infraroodspectrum maakt met een
coupled-cluster-anker — een klein aantal dure, nauwkeurige energieën dat de goedkope DFT-berekening corrigeert — met bij elk
spectrum een foutenbudget per bandfamilie dat zegt of het te vertrouwen is en wat het heeft gekost. De ambitie daarachter, bewust
niet beloofd (§6), is een bron van trainingsdata voor een netwerk dat die correctie voorspelt voor de PAK's waarvoor geen
laboratoriumspectrum bestaat. Jouw groep sloot in 2016 af met de hoop dat de anharmonische effecten zich over de PAK-familie laten
generaliseren zonder voor elk molecuul een volledig krachtveld te rekenen (Mackie et al. 2016, slotparagraaf); dit plan is één
antwoord op die hoop.

**Hoe het werkt.** De coupled-cluster-correctie op de harmonische krachtconstanten reken ik niet uit maar *meet* ik, met zo weinig
mogelijk dure energieën: lokale coupled-cluster-berekeningen waarvan ik de orbitaalruimtes één keer kies en daarna naar elke
vervorming meeneem, zodat de energieverschillen glad zijn. Het bevriezen van zulke ruimtes is een bekend recept (Mata & Werner
2006, sinds 20 september zo in §3.1); wat van mij is, is het transporteren van LNO-ruimtes, die geen atoomlijst hebben die je kunt
bevriezen, en het meten van wat dat kost. Het aantal energieën per molecuul staat naast elk spectrum; de nauwkeurigheid wordt
gescoord tegen laboratoriumdata en tegen de bestaande voorspellingen, waaronder die van jouw groep ("lijn B" in de meetlat).

**Wat tot nu toe bewezen is.** Vier dingen, elk met een vooraf opgeschreven leesregel; de getallen staan in §3.5 en §5.2.

1. *De labels zijn te maken en zijn schoon.* Het anker — naftaleen op cc-pVTZ, negentien energieën op mijn laptop — is voor drie
   bandfamilies uitgelezen: de goedkope basis draagt de correctie voor één van de drie, de andere twee blijven duur, met hun
   gemeten increment in de foutbegroting. De punten liggen glad op een curve tot ver onder wat het meetplan als ruis verdraagt, en
   de twee kationen hebben nu een gemeten prijs.
2. *Het plan vangt zijn eigen fouten.* Elke afgeleide grootheid krijgt een tweede route. Zo bleek een eerste anharmonische
   berekening ruis (het pakket meldde niets), en zo werd later een foute Hessiaan in het corpus gevonden. Beide zijn een vaste
   controle geworden; de verbeteringen aan de pakketten zijn als pull requests ingediend.
3. *De correctie is lokaal, en het netwerk leert haar.* In de basis van normaaltrillingen zijn de koppelingen onleerbaar; in
   bindingen en hoeken is dezelfde correctie dun en lokaal, en daar leert het netwerk haar uit 175 moleculen, ook op ringskeletten
   die het nooit zag. De coupled-cluster-correctie van benzeen leeft in datzelfde patroon, één binding verder; de meting voor
   naftaleen is dit weekend afgerond. De lokaliteit draagt over naar gesubstitueerde en naar grotere moleculen (drie proxy-toetsen).
4. *Het meetplan is toetsbaar zonder nieuwe kwantumchemie.* Op het corpus, waar de volledige koppelingstabel bekend is, blijkt dat
   het dek van het voorstel buiten de band moet kijken en dat een geleerde meetvolgorde metingen bespaart; de verbreding en een
   stopregel zijn voorgeregistreerd voor na ons gesprek. Het dek in het voorstel staat nog zoals het was.

**Wat nog niet bewezen is.** Of het netwerk *genoeg* leert. Dat beslist de vooraf vastgelegde leercurve op de kleine-moleculenlaag
van het corpus (100 tot 1.200 moleculen, drie hold-outs), waarvan het derde punt zondagavond is gelezen en in §3.5 staat, en daarna
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
