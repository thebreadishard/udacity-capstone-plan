# Gemeten coupled-cluster-correcties op de harmonische krachtconstanten van PAK's, en een netwerk dat ze draagt

*Projectvoorstel, versie 30 september 2026 (vier pagina's). Dit vervangt de tekst van 26 september; oudere versies staan in de git-geschiedenis.
Wijzigingen komen voortaan in deze tekst zelf, met de datum in de kop. Student: Frederic Petrignani.*

## 1. Samenvatting

Infraroodbandposities van polycyclische aromatische koolwaterstoffen (PAK's) dragen de interpretatie van de aromatische infraroodbanden die
JWST nu oplost. De referentievoorspellingen, met PAHdb voorop, rusten op geschaalde harmonische DFT. Dit project bouwt één pijplijn: een
aromatisch molecuul erin, een infraroodspectrum eruit, waarvan de bandposities aantoonbaar nauwkeuriger zijn dan de beste beschikbare voorspelling
voor dat molecuul, overal waar laboratoriumdata dat kunnen beslissen. De kern is een **gemeten coupled-cluster-correctie op de harmonische
krachtconstanten** (ΔH = H_CC − H_DFT), gekocht met zo weinig mogelijk coupled-cluster-energieën, en een **netwerk** dat die correctie leert en
overdraagt naar moleculen waarvoor geen waarheid bestaat. Het mandaat: met een desktop en een klein beetje Snellius tot een getraind netwerk
komen dat voor een groot PAK de spectrumvorm geeft, in 2027. Wat er nu staat: een DFT-corpus van ruim vijfhonderd moleculen op twee niveaus, een
CCSD(T)-anker (benzeen) met een tweede (naftaleen) in de nacht van 29 op 30 september, vier ankers in aanbouw, en de eerste meting op echte
coupled-cluster-respons dat de geleerde meetvolgorde de kosten halveert.

## 2. De vraag

**Nauwkeurigheid.** Verbetert een per-molecuul-pijplijn (DFT-geometrie en -Hessian, anharmonische constanten, plus de gemeten CC-correctie) de
bandposities meetbaar ten opzichte van geschaalde harmonische DFT (PAHdb) en een eigen gekalibreerd-harmonische basislijn, per band tegen
laboratoriumspectra? **Kosten.** Hoeveel coupled-cluster-energieën heeft die correctie per molecuul nodig, en hoe groeit dat aantal met de
molecuulgrootte? **Bereik.** Kan het netwerk, getraind op die labels, voor een PAK van honderden atomen een spectrum met een uitgesproken
foutbudget geven, per bandfamilie toegelaten of geweigerd?

## 3. De architectuur zoals besloten

Acht stappen, elk met één gegevensobject (de bladen 3 tot en met 8 van `GoalGathering/architecture/`):

| # | stap | wat het oplevert | besloten vorm |
|---|---|---|---|
| 1 | **Corpus** | per molecuul een DFT-geometrie en twee Hessianen (B3LYP en ωB97X) | psi4-deck met een analytische pyscf-Hessian als tweede route; elke afgeleide grootheid krijgt twee routes of een symmetriecontrole (ruisprincipe) |
| 2 | **Labelfabriek** | ΔH per molecuul uit coupled-cluster-energieën in bevroren lokale ruimtes | de **brede kandidatenlijst** van alle modeparen, in een **geleerde volgorde**, met een **stopregel** op een uitgehouden set; het aantal gekochte energieën wordt per molecuul afgedrukt |
| 3 | **Ankers** | canonieke CCSD(T)-Hessianen waar dat betaalbaar is | de ijk van de labelfabriek: benzeen, naftaleen, benzonitril, fluorbenzeen, pyridine, benzeenkation; op elk anker wordt de lokaliteit van de correctie gemeten, niet aangenomen |
| 4 | **ΔH-model** | de correctie als blokobject (diagonaal plus koppelingen binnen een familie) in lokale coördinaten | equivariant netwerk op de DFT-Hessian; geen per-mode-labels (dat bleek slecht gesteld) |
| 5 | **Training** | een leercurve: fout op ongeziene moleculen tegen aantal labels | validatiesplit, vroeg stoppen, beste epoch vastgelegd; eerst op de DFT-proxy, dan op coupled-cluster-labels |
| 6 | **Toets en licentie** | per bandfamilie toegelaten of geweigerd | vooraf geregistreerde overdrachtstoetsen; bij weigering levert de pijplijn DFT met de reden erbij |
| 7 | **Spectrumpijplijn** | posities en intensiteiten | tweede-orde storingsrekening (GVPT2) met resonantiebehandeling op analytische Hessianen; hot-band-lijnen gerapporteerd, niet gescoord |
| 8 | **Certificaat en officier** | wat elke uitspraak waard is, en wat ze kostte | de certificaatladder (module 08) en de campagne-officier (module 07) die elke run tegen de incidentenlijst houdt |

Twee routes voor de grote moleculen: energieën in bevroren lokale ruimtes (gegarandeerd, kosten in het aantal koppelingen) en analytische
lokaal-CC-gradiënten (gewenst, drie-N responsen per patroon; een zijproject met eigen mijlpalen en een stopcriterium). Voor moleculen boven de
twee ringen wordt de correctie op afgedekte fragmenten gemeten, mits de lokaliteitsmeting op de middenrungen dat toestaat.

## 4. Waaraan succes wordt afgemeten

Elke meting van het project dient een van vijf vragen. De lijnen staan vooraf vast in pre-registraties; de stand is die van 29 september.

| vraag | meting | lijn | stand |
|---|---|---|---|
| Is een label betaalbaar? | energieën per molecuul tot ρ_off ≤ 0,3 op de brede lijst met geleerde volgorde en stopregel | ≥ 90 % van de evaluatiemoleculen binnen het budget, ≤ 5 % valse stops | benzeen op CC: geleerde volgorde 0,46 van de blinde volgorde (≈ 370 energieën), orakel 124; de stopregel wordt opnieuw geregistreerd (uitgehouden set uit de brede lijst, drempel gefit op validatie) |
| Reist het label mee? | het blok van benzeen op benzonitril, fluorbenzeen, pyridine; naftaleen tegen benzeen | gecorrigeerde frequenties ≤ 3,3 cm⁻¹, ringkoppelingsratio ≤ 0,5 | op de DFT-proxy slagen alle paren (0,8–2,0 cm⁻¹); de CC-getallen komen deze week |
| Leert het netwerk het juiste? | de leercurve op ongeziene moleculen | het geleerde ΔH verslaat de nulregel en het geschaalde krachtveld | proxy-curve loopt (600 moleculen, lezing 30 september); CC-curve met 40 ankers in oktober |
| Kan het groot? | prijs van een lokaal-CC-gradiënt op drie ringen | een label per molecuul binnen een dag op de desktop | nog niet gemeten; eerste meting op de PC in november |
| Klopt de vorm? | anharmonische stap tegen koude en warme laboratoriumspectra | beter dan de opponenten per band, met de gemeten bandonzekerheid als grens | de benzeen-desktest op B3LYP/6-31G* mat niets (ruis groter dan de constanten); de analytische route is aangetoond en wordt de standaard |

Twee bevindingen van deze week bepalen de richting: de veronderstelling dat belangrijke koppelingen binnen een frequentieband van 200 cm⁻¹ zitten
bleek op de echte CC-correctie van benzeen fout (4 % van de koppelingssterkte in band); de brede lijst met geleerde volgorde is daarom de enige
route. En elke lezing op coupled-cluster-niveau gebruikt de analytische DFT-Hessian als laag niveau, nooit de eindige-verschillenversie: de
proxyrij van benzeen bleek daardoor ruis, en de correctie is op record gezet.

## 5. Plan en mijlpalen

| wanneer | wat | wat het beslist |
|---|---|---|
| 30 september – 2 oktober | naftaleen-anker gelezen; benzonitril, fluorbenzeen, pyridine, benzeenkation op CCSD(T); stopregel-registratie twee | vragen 1 en 2 op CC-niveau; de eerste kationrij |
| oktober | desktop-PC (16 kernen, 128 GB); 40 één-ringankers en de eerste gesubstitueerde naftalenen; de CC-leercurve bij 10, 20 en 40 labels; een C-kernel voor de (T)-dichtheden (×3 per gradiënt, gemeten op benzeen) | vraag 3 op CC-niveau |
| november | de lokaal-CC-gradiëntprijs op antraceenformaat; gesprek met de supervisor | vraag 4 |
| december – voorjaar 2027 | schaal: netwerk op CC-labels, licentie per familie, spectrumpijplijn met intensiteiten en hot bands tegen de laboratoriumbronnen | vragen 3 en 5 samen: de mandaatzin |

## 6. Middelen en risico's

**Middelen.** Tot nu toe gehuurde rekentijd (Hetzner): ongeveer €375 in september, voor het corpus, de ankers en de kationprijzen. Vanaf oktober
een eigen werkstation (≈ €4.240; 16 kernen, 128 GB) dat ongeveer honderd één-ringankers of acht twee-ringankers per maand aankan zonder plafond.
Snellius: een kleine aanvraag volgt zodra de eerste CC-overdrachtsmeting is gelezen; daarvoor is er niets te vragen dat de desktop niet kan.

**Risico's, elk met zijn toets.** (1) Het geleerde ΔH draagt op CC-niveau niet over buiten de familie: de leercurve van oktober beslist; het
terugvalplan is het per molecuul gemeten label, waarvan de prijs in vraag 1 staat. (2) De lokaal-CC-gradiënt is voor drie ringen te duur: de
novembermeting beslist; het terugvalplan is de energieroute op fragmenten. (3) De anharmonische stap is te ruizig om de vorm te scoren: aangetoond
opgelost met analytische Hessianen; de eerste toets op hot bands (benzeen, één constante op hoger niveau) staat voor deze week.

## 7. Wat ik van u vraag, en hoe ik rapporteer

1. Een kritische lezing van deze vier pagina's, in het bijzonder van §3 en §4: daar houdt de discipline of niet.
2. Eén koude, opgeloste meting van pyreen, of een bron ervan: één sterke band per familie bij 6,2, 7,7, 8,6 en 11–13 µm met bandcentra tot
   ≤ 1 cm⁻¹. Daarmee wordt de pyreenrung beslisbaar; de gepubliceerde bronnen halen dat niet.
3. Het gesprek in november, met dan de CC-leercurve op tafel.

Ik rapporteer in berichten van ten hoogste 150 woorden, met de vraag voorop; het volledige logboek en de pre-registraties staan in het repo en zijn
op elk moment in te zien.

## Referenties (kern)

Ricca et al. 2026 (PAHdb, huidige versie); Mackie et al. 2015, 2016 en Maltseva et al. 2016 (anharmonische PAK-spectra, de vergelijkingslijn);
Esposito et al. 2024 (B3LYP/N07D-standaard); Mai et al. 2025 (ML-moleculaire dynamica voor PAK-IR); Pirali et al. 2009, Albert et al. 2011,
Brumfield et al. 2012 (opgeloste laboratoriumbanden van naftaleen en pyreen); Mata & Werner (bevroren domeinen voor numerieke Hessianen, de
prior art die het plan erkent); pyscf 2.14 en pyscf-forge (LNO-CCSD(T)); psi4 1.11. Volledige lijst in het repo.
