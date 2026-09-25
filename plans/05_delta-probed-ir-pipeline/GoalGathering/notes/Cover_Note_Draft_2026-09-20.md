# Concept begeleidend bericht bij het voorstel (20 september 2026, voor het gesprek van maandag 28 september) — voor de student om aan te passen en te versturen

*Concept, Nederlands. Vervangt het concept van 12 september (dat blijft staan als geschiedenis). Niets hierin is nieuw ten
opzichte van het voorstel en zijn gedateerde notities; het wijst alleen de weg erin. Elk getal staat in de leeskopie of in een
resultaatbestand van de repository.*

---

Beste [naam],

Dank voor de elf artikelen van vandaag; ze zijn allemaal gelezen en verwerkt, en twee ervan hebben één zin in het voorstel
veranderd (zie hieronder). Hierbij, voor ons gesprek van maandag 28 september, het projectvoorstel voor de Udacity capstone.
Het is één document van ongeveer dertig pagina's.

Wat je aan het eind krijgt, als het plan doet wat het belooft: een pijplijn die van elk afzonderlijk aromatisch molecuul een
infraroodspectrum maakt met een coupled-cluster-anker — een klein aantal dure, nauwkeurige energieën dat de goedkope
DFT-berekening corrigeert — met bij elk spectrum een foutenbudget per bandfamilie dat zegt of het te vertrouwen is en wat het
heeft gekost. Het doel daarvan is niet het spectrum van naftaleen. De ambitie daarachter — bewust niet beloofd, zie §6 — is een
bron van trainingsdata voor een neuraal netwerk dat de correctie per bandfamilie voorspelt voor de PAK's waarvoor geen
laboratoriumspectrum bestaat. Jouw groep sloot in 2016 af met de hoop dat de anharmonische effecten zich over de PAK-familie
laten generaliseren zonder voor elk molecuul een volledig krachtveld te rekenen (Mackie et al. 2016, slotparagraaf); dit plan is
één antwoord op die hoop, met de kanttekening dat het netwerk in §6 een voorwaardelijk doel is en de gemeten correctie het
beloofde product.

Kort hoe het werkt. De coupled-cluster-correctie op de harmonische krachtconstanten reken ik niet uit maar *meet* ik, met zo
weinig mogelijk dure energieën: lokale coupled-cluster-berekeningen (LNO-CCSD(T)) waarvan ik de orbitaalruimtes één keer kies
en daarna naar elke vervorming meeneem, zodat de energieverschillen glad zijn. Het bevriezen van zulke ruimtes is een bekend
recept — Mata & Werner beschrijven het in 2006 als de standaardremedie voor numerieke Hessianen; die zin staat sinds vandaag zo
in §3.1. Wat van mij is: LNO-ruimtes hebben geen atoomlijst die je kunt bevriezen, dus ik transporteer ze en meet wat dat kost.
Het aantal energieën per molecuul staat naast elk spectrum, en de nauwkeurigheid wordt gescoord tegen laboratoriumdata en
tegen de bestaande voorspellingen, waaronder die van jouw eigen groep; de getallen van Mackie 2015 en 2016 staan nu als
"lijn B" in de meetlat.

Wat er sinds het concept van 12 september gemeten is. Het anker — naftaleen op cc-pVTZ, vijftien energieën van negen tot twaalf uur op
mijn laptop — liep van 16 tot 24 september en is nu voor alle drie de bandfamilies uitgelezen (bijgewerkt 25 september). De vooraf vastgelegde vraag was
of een goedkopere basis (cc-pVDZ, factor tien per energie) de correctie per familie draagt met een constante uit benzeen. Voor
de C–H-uit-het-vlak-familie is het antwoord nee: het increment wisselt van teken (−8,1 tegen +7,9 cm⁻¹), omdat MP2 in een
dubbel-zeta-basis juist die bewegingen te slap maakt. Voor die familie blijft het anker dus cc-pVTZ. De C–H-buiging in het vlak
won (increment +1,2 tegen +1,0 cm⁻¹, 23 september) en de C–C-strek viel ertussenin (−1,9 tegen −6,0, 24 september): de goedkope basis is
per familie vrijgegeven voor één van de drie, de andere twee blijven op cc-pVTZ met hun gemeten increment in de foutbegroting. Daarnaast draait sinds gisteren op vier gehuurde machines een corpus van
DFT-paren (45 moleculen klaar, 200 in aanmaak, 868 gepland) waarop de eerste leercurves zijn gemeten: de C–H-families leren
snel, de ringfamilie niet, en de reden bleek dat een label per modus daar slecht gedefinieerd is — sindsdien is het doelobject
het hele familieblok. Dat is de stand; niets ervan is een oordeel over het netwerk.

Op mijn eigen laptop is het plan haalbaar tot en met benzeen: het proefdek van 448 energieën kost ruim drie weken. Naftaleen is
de eerste trede die de laptop niet meer kan: één energie op de instellingen van het anker kost daar 38 uur (gemeten 14 september),
het dek van 291 energieën dus ruim een jaar laptoptijd; op vier Snellius-knooppunten is dat naar schatting een maand. Daarom
staat de clusteraanvraag in §12 en §13.

Eén ding uit de afgelopen dagen laat zien hoe het plan werkt als iets misgaat. Een eerste anharmonische berekening van benzeen
(B3LYP, VPT2) gaf onbruikbare getallen. In plaats van de software te vertrouwen heb ik elke anharmonische constante langs twee
onafhankelijke routes berekend; het verschil bleek tot 1.265 cm⁻¹ terwijl het pakket "geen inconsistenties" meldde. De oorzaak — een
eindige differentie bovenop een eindige differentie — heb ik vooraf als voorspelling opgeschreven en daarna met twee tests bevestigd:
met analytische Hessianen op dezelfde geometrieën zakt het verschil naar 0,1 cm⁻¹ en landen de drie testbanden van benzeen op
851, 1004 en 1324 cm⁻¹ tegen 847, 993 en 1309 gemeten in de gasfase (Goodman, Ozkabak & Thakur 1991). De controle is sindsdien een vaste stap in de labelfabriek, en de drie
verbeteringen aan de gebruikte pakketten zijn als pull requests ingediend. De notitie met voorspelling en uitkomst zit als bijlage bij
dit bericht.

Een tweede les van dezelfde week. Het eerste coupled-cluster dek (44 energieën langs de 20 trillingen van benzeen) gaf voor de in-vlak-trillingen
gecorrigeerde harmonische frequenties binnen 7 cm⁻¹ van de literatuur-CCSD(T), maar zette de C–H-strekkingen 45 cm⁻¹ te laag. Niet de
lokale afkap was de oorzaak (tien keer strengere drempels veranderden niets), maar de plek waar je meet: het dek meet elke methode op de
B3LYP-geometrie, de literatuur op het eigen minimum. Die geometrieterm blijkt voorspelbaar uit één gradiënt op het dure niveau en onze eigen
kubische constanten (op Hartree–Fock getoetst voor zes trillingen, binnen tien procent); met de term erbij landen de C–H-strekkingen op
7 tot 23 cm⁻¹ van CCSD(T). Hij zit nu als vaste stap in labelfabriek en pijplijn; de tabel met alle twintig trillingen, inclusief de twee die
nog open staan, breng ik mee.

Een derde les, van 23 september. De geleerde laag leerde de verschuiving van elke trilling vanaf de eerste dag, maar de koppelingen tussen trillingen
bij geen enkele datahoeveelheid: een vooraf vastgelegde leercurve (45, 100, 175 moleculen) bleef vlak. De oorzaak zat in wat we vroegen: in de basis van
normaaltrillingen wisselt een koppeling van teken met een willekeurige tekenkeuze die geen enkel kenmerk per trilling kan zien, en de correctie is daar een
dichte kluwen. In bindingen en hoeken is dezelfde correctie dun en lokaal: een parametervrije projectie legt driekwart ervan in de interactieconstanten
tussen bindingen binnen een ring plus paren die een atoom delen. Gevraagd naar dát object leert hetzelfde netwerk de koppelingen uit dezelfde 175 moleculen,
ook op ringskeletten die het nooit zag (fout 0,43 en 0,47 van de nulregel, gecorrigeerde frequenties binnen 5 cm⁻¹ tegen 23 zonder correctie). Eén molecuul
bleef achter tot een tweede, analytische berekening liet zien dat zijn opgeslagen Hessiaan fout was; de guard staat nu in het corpus. Of de coupled-cluster-
correctie in hetzelfde patroon leeft, is op 24 september gemeten (E8, benzeen, CCSD(T)/cc-pVDZ, 72 gradiënten): ja — 92 % van de correctie
zit in dat patroon en 98 % zodra paren twee bindingen uit elkaar meetellen; pas dan kloppen ook de ringkoppelingen. De dure correctie is dus
lokaal zoals de goedkope plaatsvervanger, één binding verder. Het paarmodel krijgt daarmee één paarklasse extra; verder verandert er niets aan
het idee. Wat de meting ook prijsgaf: één coupled-cluster-gradiënt van naftaleen kost uren, geen minuten; symmetrie brengt naftaleen van 108
naar 30 gradiënten (op benzeen bewezen: 12 in plaats van 72, tot 0,03 cm⁻¹ gelijk), maar gesubstitueerde moleculen hebben die symmetrie niet.
Daarom blijft de labelroute LNO-CC-energieën, en staat de kostentabel van deze brief daar eerlijk over.

*Toegevoegd 25 september.* Drie proxy-toetsen van 24 en 25 september zeggen hoe ver die lokaliteit draagt, elk met een vooraf vastgelegde leesregel.
De correctie van een gesubstitueerd molecuul is het blok van zijn moederkern plus de Hessiaan-kolommen binnen twee bindingen van de substituent:
een kwart van de kolommen geeft de gecorrigeerde frequenties tot 1,7 cm⁻¹ terug, tegen 23 zonder correctie (E9, 182 moleculen). Dat buurtblok kan
voor elf van de vijftien substituenttypen één keer gemeten worden, op de kleinste drager, en overgezet (E10; de draaibare groepen CH₃, OCH₃, SH en
CONH₂ niet). En een model dat alleen moleculen tot 26 atomen zag, voorspelt de grotere (27–34 atomen) op 0,59 van de nulregel voor de koppelingen,
tegen 0,36 binnen dezelfde grootte. Daartegenover staat één harde prijs: één LNO-CCSD(T)/cc-pVDZ-energie van een molecuul van 25 atomen op de
instellingen van het anker kost meer dan negen uur op acht draden (L2, 25 september); voor gesubstitueerde moleculen is een goedkopere
correlatietrap nodig, waarvan de nauwkeurigheid op benzeen tegen canoniek CCSD(T) gemeten wordt vóór hij labels levert. Het bewijs dat het netwerk
leert — het criterium van dit ontwerp — is gedeeltelijk: diagonaal ja, koppelingen ja op ongeziene skeletten én op de kale kernen met een dalende
curve (0,47 → 0,43 bij 45 → 175 moleculen, met benzeens gecorrigeerde doel; gecorrigeerd 09:0x — een eerdere versie van deze alinea zei "kale kernen nog vlak" op grond van een
achterhaald bestand); wat nog ontbreekt is de helling over een decade aan data. De beslissende leercurve is vooraf vastgelegd en draait sinds 25 september: laag B van het corpus, 100 tot 1.200 kleine moleculen, drie
hold-outs (kale kernen, ongeziene skeletten, grotere moleculen), leesregel op papier vóór de eerste tabel.

Wat ik van je vraag staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7, de plekken waar de discipline
van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde spectra kent van pyreen, chryseen en trifenyleen in het
6–15 µm-gebied die mijn zoektocht van 5 september heeft gemist, want die maken de C–C-families op de pyreentrede beslisbaar; en
(5) of je een Snellius-aanvraag wilt steunen, gedimensioneerd op de gemeten tijden, en of er binnen jouw netwerk een geschikte
machine is. Twee kleine vragen kwamen uit de artikelen van vandaag: (14) of de naftaleen-QFF op CCSD(T)/cc-pVTZ die het artikel
van 2015 als "net haalbaar, in bewerking" noemt ooit is gepubliceerd — dat zou mijn enige coupled-cluster-referentie boven
benzeen zijn; en (18) welke referentie jij vertrouwt voor de kationen: het artikel van Esposito e.a. uit 2024 rekent fenantreen⁺,
pyreen⁺ en pentaceen⁺ met dezelfde machinerie, maar zegt niets over spincontaminatie van de open-schil-referentie, en mijn
kationlabels hangen daaraan. De overige genummerde vragen zijn voor het gesprek; ze veranderen geen regel, ze leveren een getal
of een bron.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat in de repository:
https://github.com/thebreadishard/udacity-capstone-plan, met een openbaar labjournaal in blogvorm.

Groetjes,
Frederic

---

*Checklist voor het versturen:* de datum in de kop van de leeskopie is 28 september; het B1-verdict van vrijdag is ingevuld op de
plek van de marker in §3.5 (de eerste familie staat er al als gedateerde notitie); instelling en rol in de kop ingevuld; de pdf of
het md-bestand als bijlage; de repository-link alleen als de student dat wil.

*Wat dit concept toevoegt ten opzichte van 12 september:* de dank voor de artikelen en de zin over Mata & Werner (§3.1 herschreven
20 september); de stand van het anker met de eerste familie (20 september 18:43) en van het corpus; de vragen 14 en 18 in concrete
vorm; het dek van 291 in plaats van 474 energieën (besluit 37). Plan 06 en zijn annex worden in de brief niet genoemd (de gebruiker, 20 september).
*Bijgewerkt 25 september 08:3x:* het anker uitgelezen (drie families: verlies / winst / tussenin), de alinea over E9, E10, grootte-extrapolatie, L2 en de
laag-B-leercurve; bronnen `PreRegistration_2026-09-24_E9_*`, `_E10_*`, `_L2_*`, `2026-09-25_Size_Extrapolation_*`, `2026-09-25_Proof_of_Learning_Layer_B.md`
en `Note_2026-09-25_Growing_Asset_and_Proof_of_Learning.md` (de twee horizonten, voor het gesprek zelf).
