# De referentie-Hessiaan: voldoet deze composiet?

Voor de supervisor, na het gesprek van 25 november 2026. Geschreven om zelf te lezen of om aan een AI te geven die het narekent.
Elk getal staat naast datgene waartegen het gemeten is. Wat niet gedaan is, staat erbij.

## De vraag en het hoofdpunt

Het neurale netwerk van dit project leert het verschil tussen een goedkope Hessiaan (B3LYP/6-31G*) en een betere. Die betere
is nu ωB97X/6-31G*, als voorlopige plaatsvervanger. Het doel is CCSD(T). Daarvoor gebruiken we geen volledige berekening in een
grote basis, maar een composiet: CCSD(T)/cc-pVDZ plus een basissetstap uit MP2, op de B3LYP-geometrie. Vóór we daar ongeveer
300 moleculen mee doorrekenen, willen we uw oordeel.

Het hoofdpunt, op benzeen, het enige molecuul waarvoor we het konden nagaan. Verschil met gepubliceerde harmonische
CCSD(T)/ano-pV5Z-frequenties (Semidalas en Martin, tabel 5), rms over de 20 verschillende trillingen, in cm⁻¹:

| | alle 20 | de 4 CH-strekken | de 6 uit het vlak | de 10 overige in het vlak |
|---|---|---|---|---|
| onze volledige CCSD(T)/cc-pVTZ | 20,6 | 34,3 | 23,8 | 6,2 |
| onze composiet | 19,6 | 29,9 | 23,9 | 8,0 |
| onze volledige CCSD(T)/cc-pVTZ, met geometriecorrectie | 15,5 | 3,7 | 27,0 | 6,1 |
| onze composiet, met geometriecorrectie | 18,0 | 7,6 | 30,2 | 8,9 |
| B3LYP/6-31G*, ongeschaald, op zijn eigen minimum | 13,2 | 4,6 | 9,6 | 16,9 |

Zonder correctie ligt onze referentie voor benzeen in de CH-strekken en in de trillingen uit het vlak verder van die
gepubliceerde waarden dan ongeschaalde B3LYP. Dat komt voor een deel doordat de Hessiaan op de B3LYP-geometrie staat en niet
op het CCSD(T)-minimum. De eerste-orde-correctie daarvoor hebben we op 25 november op benzeen toegepast (derde en vierde
regel van de tabel). Ze doet wat we verwachtten voor de CH-strekken: van 34 naar 3,7 cm⁻¹ voor de volledige cc-pVTZ, en van
30 naar 7,6 voor de composiet. **Maar de trillingen uit het vlak worden er slechter van: 27 en 30 cm⁻¹, tegen 9,6 voor
ongeschaalde B3LYP.** De correctie haalt een schijnbare versteviging weg die van de restkracht op de waterstofatomen kwam,
en legt daarmee bloot dat cc-pVTZ deze trillingen tientallen cm⁻¹ te laag geeft. Dat zijn de banden bij 11 tot 14 µm.

Onze eigen conclusie, die we graag door u getoetst zien: met cc-pVTZ als doel van de basissetstap is deze composiet goed
genoeg voor de CH-strekken en voor de gewone trillingen in het vlak (6 tot 9 cm⁻¹), en niet voor de trillingen uit het
vlak. Of een basis van atomaire natuurlijke orbitalen in de MP2-stap dat herstelt, is onze eerstvolgende proef; die raakt
alleen het goedkope deel.

## De vier vragen

1. Is CCSD(T)/cc-pVDZ met een MP2-stap naar cc-pVTZ voor u aanvaardbaar als referentie, als de geometriecorrectie erbij komt?
   En waartegen moet de 2 cm⁻¹ gelden die u noemde: harmonisch tegen CCSD(T) bij de basissetlimiet, of fundamentelen tegen
   experiment? Onze eigen cijfers zeggen dat de composiet 4,6 cm⁻¹ van de volledige cc-pVTZ ligt, en na de geometriecorrectie 8 tot 9
   van de gepubliceerde waarden in de CH-strekken en de gewone trillingen in het vlak; 2 cm⁻¹ haalt hij zo niet.
2. Zou u in de MP2-stap een basis van atomaire natuurlijke orbitalen gebruiken (ano-pVTZ of ano-pVQZ), gezien de twee
   b2g-trillingen hieronder?
3. Aanvaardt u Hessianen op de B3LYP-geometrie met een eerste-orde-geometriecorrectie, of moet elk molecuul naar zijn eigen
   CCSD(T)-minimum?
4. Tegen welke gepubliceerde of gemeten waarden zou u de referentie toetsen voordat we er 300 moleculen mee doorrekenen?

Wat uw antwoord kost. Bij vraag 1: een grotere basis in het CCSD(T)-deel maakt elk molecuul vele malen duurder; een
naftaleen-Hessiaan kost nu 19 uur op 16 cores. Bij vraag 3: als u het eigen CCSD(T)-minimum eist, moeten alle
CCSD(T)-Hessianen die er nu zijn opnieuw, op de nieuwe geometrie, en komt er per molecuul een CCSD(T)-optimalisatie bij. Dat
besluit moet dus vóór de start vallen. Alleen vraag 2 kan ook daarna nog: de MP2-stap staat los van het CCSD(T)-deel.

## Wat de referentie is

Per molecuul één Hessiaan, in drie stappen.

1. **Geometrie.** Het minimum van B3LYP/6-31G*. Alle volgende berekeningen staan op die ene geometrie. Voor benzeen is daar
   C–C 1,3968 Å en C–H 1,0871 Å, en de grootste component van de CCSD(T)/cc-pVTZ-gradiënt 3,2 × 10⁻³ Eh/bohr. Het is dus geen
   stationair punt van de betere methode. De gepubliceerde CCSD(T)-evenwichtsafstanden hebben we er niet naast gelegd.
2. **CCSD(T)/cc-pVDZ.** De Hessiaan uit centrale verschillen van analytische gradiënten: elke symmetrie-unieke cartesische
   verplaatsing, heen en terug, stap 0,005 bohr. Daarna uitgebreid met de puntgroep, gesymmetriseerd, en de zes translaties en
   rotaties eruit geprojecteerd met de massagewogen projector. Bevroren kern: 1s voor C, N, O en F; 1s2s2p voor S en Cl.
   Gesloten schil, RHF-referentie. Programma: PySCF (2.15.1 voor de berekeningen van deze maand).
3. **De basissetstap uit MP2.** Dezelfde verplaatsingen, dezelfde stap en dezelfde bevroren kern, met de analytische gradiënt
   van DF-MP2 (dichtheidsfitting, psi4, hulpbases cc-pVXZ-JKFIT en cc-pVXZ-RI, sferische functies), in cc-pVDZ en in cc-pVTZ.

De composiet is de som van de cartesische Hessianen:

    H = H[CCSD(T)/cc-pVDZ] + ( H[MP2/cc-pVTZ] − H[MP2/cc-pVDZ] )

De aanname is dat de grotere basis het CCSD(T)-resultaat verandert zoals hij het MP2-resultaat verandert.

Twee dingen die u moet weten. Voor de zes eerste moleculen, benzeen inbegrepen, was de MP2-stap conventioneel MP2 in PySCF; de
toets op benzeen hieronder is dus met dat recept gedaan en niet met DF-MP2. De overstap is apart getoetst; dat getal staat niet
op deze pagina. En convergentiedrempels en de overige instellingen staan in de scripts die onderaan genoemd zijn, niet hier.

## Controles per berekening

- De analytische MP2-gradiënt is op elke rekenserver getoetst tegen vijfpunts eindige verschillen van de energie, op water:
  binnen 10⁻⁶ Eh/bohr in beide bases.
- De analytische CCSD(T)-gradiënt van de referentiegeometrie wordt nagerekend langs een tweede weg; de grens daarvoor staat in
  het script, niet hier.
- Symmetrie-equivalente rijen van de MP2-Hessiaan worden vergeleken; voor indeen is de spreiding 3 × 10⁻⁵ Eh/bohr².
- Een composiet nemen we alleen in de set op als hij na projectie geen trilling onder −10 cm⁻¹ heeft.

## Wat er ligt

24 moleculen zijn klaar: benzeen (volledige CCSD(T)/cc-pVTZ en composiet), naftaleen, antraceen, azuleen, acenaftyleen, indeen,
pyridine, quinoline, isoquinoline, quinoxaline, quinazoline, indool, benzonitril, en elf met een substituent (F, Cl, OH of SH).
Zestien andere worden nu berekend.

## De cijfers in detail

### De composiet tegen onze eigen volledige CCSD(T)/cc-pVTZ, op benzeen

Over alle 30 trillingen wijkt de composiet 4,6 cm⁻¹ rms af, hoogstens 8,5 (de a2u-trilling). In onze eigen indeling in vier
soorten (CH-strek boven 2800 cm⁻¹; CH uit het vlak, 600 tot 1050; ring in het vlak, 950 tot 1750; overig): ring in het vlak
3,3, CH-strek 4,4, CH uit het vlak 7,3, overig 3,3. CCSD(T)/cc-pVDZ zonder de MP2-stap wijkt 72,9 af, vooral in de CH-strekken
(137,9): op deze vaste geometrie liggen die in cc-pVDZ bij 3271 tot 3311 cm⁻¹ en in cc-pVTZ bij 3133 tot 3173.

Dit is overeenstemming tussen twee cc-pVTZ-berekeningen op dezelfde geometrie, op het kleinste molecuul. Het zegt niets over
hoe dicht cc-pVTZ bij de basissetlimiet zit, en 4,6 is zelf al meer dan 2.

### Tegen gepubliceerde CCSD(T)/ano-pV5Z, per trilling

Wilson-nummering. De tweede kolom met getallen is gepubliceerd; de kolommen daarna zijn verschillen met die kolom, in cm⁻¹. De
kolom ano-pVTZ komt uit hetzelfde artikel. Onze twee CCSD(T)-kolommen staan op de B3LYP-geometrie; de gepubliceerde waarden
staan op het CCSD(T)-minimum. De B3LYP-kolom is onze eigen berekening op het B3LYP-minimum. Elke trilling is benoemd uit zijn
eigen vector (in of uit het vlak, even of oneven onder inversie, karakter onder de zesvoudige rotatie) en binnen een
symmetriesoort op volgorde gekoppeld; een ontaard paar telt één keer.

| trilling | symmetrie | CCSD(T)/ano-pV5Z, gepubliceerd | CCSD(T)/ano-pVTZ, gepubliceerd, − 5Z | onze CCSD(T)/cc-pVTZ − 5Z | onze composiet − 5Z | onze B3LYP/6-31G* − 5Z | uit het vlak |
|---|---|---|---|---|---|---|---|
| ω1 | a1g | 1006,6 | −3,3 | −0,3 | −1,1 | +13,4 |  |
| ω2 | a1g | 3204,3 | +5,6 | −31,2 | −26,8 | +5,8 |  |
| ω3 | a2g | 1380,5 | −5,6 | −2,8 | −7,9 | +6,6 |  |
| ω4 | b2g | 712,4 | −4,0 | −38,5 | −36,9 | +5,5 | ja |
| ω5 | b2g | 1012,4 | −5,6 | −31,0 | −35,9 | −1,4 | ja |
| ω6 | e2g | 611,5 | −1,2 | −2,5 | −5,4 | +10,4 |  |
| ω7 | e2g | 3179,6 | +5,0 | −35,4 | −31,0 | +4,1 |  |
| ω8 | e2g | 1639,3 | −2,3 | +2,4 | +0,7 | +16,0 |  |
| ω9 | e2g | 1191,8 | +0,5 | +5,4 | +1,9 | +15,9 |  |
| ω10 | e1g | 863,4 | +0,2 | +10,2 | +2,4 | +1,5 | ja |
| ω11 | a2u | 683,6 | +2,3 | +25,3 | +16,8 | +11,3 | ja |
| ω12 | b1u | 1024,6 | −5,2 | −14,6 | −18,3 | −4,8 |  |
| ω13 | b1u | 3169,9 | +4,5 | −37,2 | −32,8 | +4,1 |  |
| ω14 | b2u | 1328,6 | −0,3 | +7,0 | +12,7 | +27,0 |  |
| ω15 | b2u | 1158,4 | +2,1 | +8,1 | +5,9 | +27,1 |  |
| ω16 | e2u | 406,3 | −0,5 | −2,9 | −7,2 | +9,1 | ja |
| ω17 | e2u | 987,0 | −4,0 | −13,9 | −21,2 | −17,7 | ja |
| ω18 | e1u | 1057,2 | −2,4 | +2,2 | −0,5 | +11,6 |  |
| ω19 | e1u | 1511,3 | −4,7 | +1,0 | −2,0 | +19,8 |  |
| ω20 | e1u | 3195,1 | +5,6 | −33,0 | −28,6 | +4,3 |  |

### De geometriecorrectie, toegepast op benzeen (25 november)

De correctie is Δω_i = ½ Σ_k φ_iik Δq_k. Daarin is φ het kubische krachtveld van B3LYP/6-31G* in gereduceerde
normaalcoördinaten, en Δq de Newton-stap van de B3LYP-geometrie naar het minimum van de betere methode, uit de opgeslagen
CCSD(T)/cc-pVTZ-gradiënt en de Hessiaan die gecorrigeerd wordt. Voor benzeen is die stap klein: de grootste
atoomverplaatsing is 0,0033 Å, vrijwel geheel langs de symmetrische CH-strek (Δq = −0,09; de C–H-binding wordt korter) en
een weinig langs de ringademhaling (+0,02). Voor beide kolommen is de cc-pVTZ-gradiënt gebruikt; voor de andere moleculen,
waar geen volledige cc-pVTZ bestaat, moet dat de gradiënt van de composiet worden. De kubische constanten van B3LYP staan
hier voor die van CCSD(T): dat is een benadering.

Controles: de ongecorrigeerde kolommen hieronder zijn dezelfde getallen als in de tabel hierboven, langs een andere
rekenweg; en het krachtveld en de Hessianen staan op twee B3LYP-geometrieën uit twee programma's, die 0,0003 bohr van
elkaar liggen en waarvan de B3LYP-frequenties hoogstens 2,6 cm⁻¹ verschillen.

| trilling | symmetrie | CCSD(T)/ano-pV5Z, gepubliceerd | onze cc-pVTZ, ruw − 5Z | onze cc-pVTZ, gecorrigeerd − 5Z | onze composiet, ruw − 5Z | onze composiet, gecorrigeerd − 5Z |
|---|---|---|---|---|---|---|
| ω1 | a1g | 1006,6 | −0,3 | −2,0 | −1,1 | −2,8 |
| ω2 | a1g | 3204,3 | −31,2 | +5,7 | −26,8 | +10,0 |
| ω3 | a2g | 1380,5 | −2,8 | −10,7 | −7,9 | −15,8 |
| ω4 | b2g | 712,4 | −38,5 | −38,3 | −36,9 | −36,7 |
| ω5 | b2g | 1012,4 | −31,0 | −45,1 | −35,9 | −49,9 |
| ω6 | e2g | 611,5 | −2,5 | −4,3 | −5,4 | −7,2 |
| ω7 | e2g | 3179,6 | −35,4 | +2,1 | −31,0 | +6,3 |
| ω8 | e2g | 1639,3 | +2,4 | −2,1 | +0,7 | −3,8 |
| ω9 | e2g | 1191,8 | +5,4 | −1,5 | +1,9 | −5,1 |
| ω10 | e1g | 863,4 | +10,2 | −7,4 | +2,4 | −15,1 |
| ω11 | a2u | 683,6 | +25,3 | +1,1 | +16,8 | −7,4 |
| ω12 | b1u | 1024,6 | −14,6 | −14,1 | −18,3 | −17,8 |
| ω13 | b1u | 3169,9 | −37,2 | +0,4 | −32,8 | +4,7 |
| ω14 | b2u | 1328,6 | +7,0 | +0,4 | +12,7 | +6,1 |
| ω15 | b2u | 1158,4 | +8,1 | −0,3 | +5,9 | −2,5 |
| ω16 | e2u | 406,3 | −2,9 | −5,1 | −7,2 | −9,5 |
| ω17 | e2u | 987,0 | −13,9 | −28,3 | −21,2 | −35,6 |
| ω18 | e1u | 1057,2 | +2,2 | −3,0 | −0,5 | −5,7 |
| ω19 | e1u | 1511,3 | +1,0 | −4,5 | −2,0 | −7,5 |
| ω20 | e1u | 3195,1 | −33,0 | +4,2 | −28,6 | +8,4 |

Wat we hieruit lezen.

**De CH-strekken komen goed.** Van 31 tot 37 cm⁻¹ te laag naar 0,4 tot 5,7 te hoog voor de volledige cc-pVTZ; voor de
composiet 4,7 tot 10,0 te hoog. De hypothese over de geometrie klopt hier.

**De a2u-trilling ook, en om dezelfde reden gaan de andere CH-trillingen uit het vlak omlaag.** a2u gaat van +25 naar +1
(cc-pVTZ). Op de B3LYP-geometrie trekt de CCSD(T)-kracht elk waterstofatoom naar zijn koolstofatoom; die restkracht maakt
elke beweging loodrecht op de binding schijnbaar stijver. De correctie haalt dat weg, bij a2u en evenzeer bij de CH-wip ω5
(b2g, −14), bij ω10 (e1g, −18) en bij ω17 (e2u, −14).

**Wat overblijft is de basisset, en die is erger dan de ruwe getallen lieten zien.** Na correctie liggen in onze volledige
cc-pVTZ te laag: de ringplooiing ω4 (b2g) 38 cm⁻¹, de CH-wip ω5 (b2g) 45, en ω17 (e2u) 28. De composiet volgt dat (37, 50
en 36); het gebrek zit dus in cc-pVTZ zelf en niet in de MP2-stap. Dit zijn precies de drie trillingen die Martin, Taylor en Lee (1997) beschrijven als pathologisch gevoelig voor de
basisset, door basisset-superpositie: ω4 en ω5, en in mindere mate ω17. Hun CCSD(T)-waarden op het eigen minimum zijn,
voor cc-pVTZ en voor een ANO-basis van dezelfde grootte: ω4 677 en 709, ω5 972 en 1009. Onze gecorrigeerde cc-pVTZ geeft
674 en 967, en ook voor ω10, ω11, ω12 en ω16 liggen we binnen 3 cm⁻¹ van hun cc-pVTZ-waarden. Dat is een onafhankelijke
bevestiging van onze Hessiaan en van de geometriecorrectie, en het laat zien dat een ANO-basis het op CCSD(T)-niveau
herstelt.
In het artikel van 2023 liggen ω4 en ω5 met ano-pVTZ nog 4,0 en 5,6 te laag, en met een expliciet gecorreleerde
triple-zeta-basis 17 en 14. Een F12-basis van triple-zeta-kwaliteit lost het dus niet op; daarom vragen we in vraag 2 alleen
naar ANO. Moran en collega's (2006) beschrijven hetzelfde verschijnsel voor gecorreleerde methoden in kleine bases, tot en
met imaginaire frequenties voor vlakke aromaten.

**Niet verklaard.** In het vlak blijven twee trillingen meer dan 10 cm⁻¹ te laag, ook na correctie: ω12 (b1u), 14 en 18,
en ω3 (a2g), 11 en 16.

**Antraceen, als waarschuwing.** De CCSD(T)/cc-pVDZ-Hessiaan van antraceen heeft een imaginaire trilling uit het vlak: de zes
laagste zijn −51, 7, 180, 209, 224 en 332 cm⁻¹. Met de MP2-stap worden ze 86, 115, 227, 229, 261 en 373; B3LYP geeft 92, 124,
235, 238, 273 en 388. De composiet is dus reëel, maar het cc-pVDZ-oppervlak is daar kwalitatief fout, en de aanname van de
composiet wordt er getoetst waar ze het zwakst is. MP2 heeft dit artefact zelf ook. Een foutschatting voor die laagste
trillingen hebben we niet.

## Wat niet gedaan is

- Een ANO-basis in de MP2-stap proberen (ano-pVTZ of ano-pVQZ), op benzeen, tegen de gepubliceerde waarden. Dit is het
  eerstvolgende; het vraagt alleen MP2-berekeningen.
- De geometriecorrectie op een ander molecuul dan benzeen, met de gradiënt van de composiet in plaats van die van de
  volledige cc-pVTZ. Ze vraagt per molecuul een kubisch B3LYP-krachtveld; dat hebben we nu voor 37 moleculen.
- De correctie inbouwen in de rekenketen, zodat ze ook voor een nieuw molecuul wordt gemaakt.
- Dezelfde vergelijking voor een tweede molecuul. Boese en Martin geven CCSD(T)-frequenties voor benzeen en s-tetrazine, voor
  pyridine alleen DFT en gemeten fundamentelen; een gepubliceerd harmonisch CCSD(T)-krachtveld voor pyridine of naftaleen hebben
  we met een korte zoektocht niet gevonden.
- Een vergelijking met gemeten gasfasespectra van wat de referentie plus een anharmonische stap oplevert.
- Een referentie voor een kation.
- Nagaan of we de MP2-gradiënt van de referentiegeometrie bij elke Hessiaan bewaren; de CCSD(T)-gradiënt bewaren we.

Wat na de Hessiaan komt, en waarom dit ertoe doet: het netwerk leert het verschil met deze referentie, dus een systematische
fout van de referentie komt in elk voorspeld spectrum terecht. De anharmonische verschuiving komt er daarna apart bij, op
DFT-niveau; die staat los van deze vraag.

## Waar het staat

In de repository `thebreadishard/udacity-capstone-plan`, onder `plans/05_delta-probed-ir-pipeline/`:

- de lijst van referenties: `modules/05_support_predictor/out/ANCHORS_STATUS.json`, en leesbaar in `modules/ANCHORS.md`;
- de CCSD(T)-Hessiaan: `probes/e8_cc_hessian_fd.py`;
- de MP2-stap: `probes/dfmp2_rows.py`;
- de opbouw van de composiet en de toets tegen volledige CCSD(T)/cc-pVTZ: `probes/cc_composite_full_check.py`;
- de uitkomst van die toets op benzeen: `modules/05_support_predictor/out/composite_test2_benzene_2026-10-06.md`.

De Hessianen zelf en het script van de tabel (`benzene_table.py`, onder `probes/results_m1/supervisor_chat_2026-11-25/`) staan
in de openbare gegevensrepository `thebreadishard/capstone-data`, die elke nacht wordt bijgewerkt.

## Literatuur

- Semidalas en Martin, "Can G4-like composite ab initio methods accurately predict vibrational harmonic frequencies?",
  Mol. Phys. 122 (online 2023): [doi.org/10.1080/00268976.2023.2263593](https://doi.org/10.1080/00268976.2023.2263593)
- Martin, Taylor en Lee, "The harmonic frequencies of benzene. A case for atomic natural orbital basis sets",
  Chem. Phys. Lett. 275, 414 (1997): [doi.org/10.1016/s0009-2614(97)00735-5](https://doi.org/10.1016/s0009-2614(97)00735-5)
- Moran en collega's, "Popular theoretical methods predict benzene and arenes to be nonplanar", J. Am. Chem. Soc. 128, 9342
  (2006): [doi.org/10.1021/ja0630285](https://doi.org/10.1021/ja0630285)
- Boese en Martin, "Vibrational spectra of the azabenzenes revisited: anharmonic force fields", J. Phys. Chem. A 108, 3085
  (2004): [doi.org/10.1021/jp0369589](https://doi.org/10.1021/jp0369589)
