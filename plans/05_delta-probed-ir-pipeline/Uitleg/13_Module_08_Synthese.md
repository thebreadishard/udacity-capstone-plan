# Hoofdstuk 13 — Module 08: de pijplijn als geheel

*Udacity-module "Industry-Integrated AI Systems Synthesis". In de rubriek Project 7.*

---

## 1. Wat is de vraag?

Zet de onderdelen in elkaar tot één werkend programma: een molecuul erin, zijn infraroodspectrum
eruit, met een certificaat dat per band zegt hoe goed die bekend is. Laat zien dat het werkt, en
schrijf het paper dat de keuzes verantwoordt.

## 2. Wat eist de school?

De rubriek vraagt vier dingen.

- **Een geïntegreerd artefact voor een bedrijfstak.** Het lost een echt probleem op en combineert
  methoden of onderdelen uit **minstens drie** eerdere modules. De samenhang moet bedoeld zijn:
  een losse verzameling onderdelen telt niet. Code, notebooks, diagrammen en ontwerpbestanden
  die nodig zijn om het te begrijpen, horen erbij. Het moet nieuw werk zijn.
- **Een reflectief synthesepaper** als PDF van 1.500–2.000 woorden, met vaste secties:
  bedrijfscontext en probleem, overzicht van de oplossing, integratie van eerdere projecten,
  technische keuzes en afwegingen, ethiek en verantwoord gebruik, grenzen en risico's,
  professionele relevantie, uitbreidingen, en referenties. Er staan minstens drie geloofwaardige
  bronnen in, waarvan minstens één wetenschappelijk. (De beoordelingstabel van de rubriek noemt
  twee bronnen; de checklist volgt de strengste eis.)
- **Een presentatie van 15 minuten met verdediging** bij de mentor (hoofdstuk 14).
- **Documentatie**: wie het artefact wil draaien, moet weten hoe de onderdelen samenwerken, en
  een `requirements.txt` gemaakt met `pip freeze` in de werkomgeving.

## 3. Invoer — de datastructuur in detail

De pijplijn krijgt één molecuul: een **SMILES** of een **xyz-bestand** (een lijst atomen met
hun coördinaten). De objecten O1–O15 staan in hoofdstuk 6. Wat de andere modules leveren:

| Uit | Object | Rol in module 08 |
|---|---|---|
| 05 | het ΔH-netwerk v1.3, drie seeds (O15, status `carried`) | pijplijnstap 4: de correctie op de B3LYP-Hessiaan |
| 05 | het corpus (O2) | hergebruik van stap 2–3 waar het corpus het molecuul al rekende; de ωB97X-waarheid naast het netwerk |
| 05 | de evaluatierecords van v1.3 op hold-out (a) en (b) | de gemeten fout per familie in het certificaat, en daarmee de licentie |
| 03 | de labtolerantie u_band per bandgebied (O9) en de regel die banden in gebieden indeelt | de kolom `u_band_cm` bij elke band |
| 04 | de lezing van de gekalibreerde goedkope tegenstander | het certificaat van de aanvraagdienst voor de goedkope trede |
| 06 | een kandidaat uit de getrainde SMILES-generator, met een vast startgetal | een molecuul buiten het corpus; één kandidaat is door de pijplijn gegaan |
| 07 | het schema en de poort van de campagne-officier, met zijn tabel van 32 regels | een rekenopdracht van de aanvraagdienst mag alleen door die poort starten |
| Atlas | de export van de Spectrum Atlas (`website/export/out`) | de catalogusrij van het molecuul (`listed` in het certificaat) |

Modules 03, 04, 05, 06 en 07 dragen dus elk in code bij. Dat zijn er vijf, waar de rubriek er
drie vraagt.

## 4. Bewerking — de stroom per molecuul

### De pijplijn, versie 0.9

De pijplijn is `m08/pipeline.py`. Ze heeft een eigen versienummer naast dat van het netwerk
(`modules/PIPELINE.md`). Een gewijzigde stap verhoogt het getal achter de punt. Een nieuwe
netwerkversie is ook een nieuwe pijplijnversie. Versie 1.0 wordt de versie die met module 08
wordt ingeleverd.

**Toelating, vóór elke berekening.** De pijplijn weigert een molecuul met een netto lading, met
ongepaarde elektronen (een radicaal), zonder aromatische ring, of met een element dat het
netwerk nooit zag. Het netwerk kent C, H, N, O, F, S en Cl. De pijplijn weigert ook als een
netwerk niet `carried` is, of als de uitvoermap al iets bevat: een resultaat wordt nooit
overschreven. Elke weigering noemt haar reden. De pijplijn schat bovendien hoe lang de run op de
laptop duurt, uit haar eigen eerdere runs. Een half uur komt overeen met ongeveer 170
basisfuncties in 6-31G* (de bouwstenen van de orbitalen, hoofdstuk 3).

**Stap 1 — startgeometrie.** RDKit bouwt uit de canonieke SMILES een eerste 3D-structuur (de
methoden ETKDG en MMFF, met vast startgetal 0). Bij een xyz-bestand blijven de coördinaten van
het bestand, maar de atomen worden in dezelfde volgorde gezet als bij de SMILES-route. Die vaste
volgorde is een les uit een meting. Twee schrijfwijzen van fenantreen gaven banden die tot
2,9 cm⁻¹ verschilden: het antwoord van netwerk v1.3 hangt af van de volgorde van de atomen.
Daarom bereikt nu elke schrijfwijze van een molecuul het netwerk in één volgorde. De
afhankelijkheid zelf zit nog in het netwerk; een volgende netwerkversie moet haar wegnemen.

**Hergebruik uit het corpus.** Heeft het corpus dit molecuul al gerekend met precies deze
instellingen, dan neemt de pijplijn de geoptimaliseerde geometrie, de B3LYP-Hessiaan en de APT
daaruit over en slaat stap 2 en 3 over. De controle is streng: hetzelfde deck, het rekenrooster
99/590, neutraal en gesloten schil, geen imaginaire trilling, een APT binnen de controlegrenzen,
en dezelfde startgeometrie. Van de 1.230 klaargemelde corpusmoleculen voldoen er 395. Het record
noemt de map en de vingerafdruk van elk overgenomen bestand. Voor benzeen verschilt een
overgenomen antwoord 0,00026 cm⁻¹ van een berekend antwoord.

**Stap 2 — optimalisatie.** psi4 1.11 zoekt het energieminimum met B3LYP/6-31G* en deck v1.

**Stap 3 — de goedkope Hessiaan.** pyscf 2.14 berekent de analytische B3LYP-Hessiaan en de APT.
Dit draait in WSL, de Linux-omgeving binnen Windows, met een vaste geheugengrens. Dit is
verreweg de langste stap.

**Stap 4 — de correctie.** De drie seeds van het ΔH-netwerk voorspellen elk een ΔH. Hun
gemiddelde wordt bij de B3LYP-Hessiaan opgeteld. Elke seed apart blijft bewaard.

**Stap 5 — spectrum en certificaat.** De bandposities volgen uit de gecorrigeerde Hessiaan. De
bandhoogtes volgen uit de B3LYP-APT. Dat heet de *dubbel-harmonische* benadering: de
potentiaal is een parabool en het dipoolmoment verandert lineair met de uitwijking. Elke band
wordt verbreed tot een Lorentz-piek van 10 cm⁻¹ breed op halve hoogte. Ter vergelijking staat
de *baseline* ernaast: het B3LYP-spectrum met de schaalfactoren van PAHdb. Daarna schrijft
`m08/live_certificate.py` het certificaat.

Bij elke stap schrijft de pijplijn `progress.json` (O6). De posities zijn harmonisch. De
anharmonische verschuiving zit nog niet in de pijplijn, en het record zegt dat.

### Het certificaat en de licentie

Het certificaat (O13) zet bij elke band de positie, de hoogte, de spreiding over de drie seeds,
de B3LYP-positie, de baseline, de familie, de gemeten fout van die familie en de labtolerantie
van het gebied. Het zegt ook of het netwerk het molecuul kent: getraind, in hold-out (a) of
(b), alleen in de catalogus, of nooit gezien. Waar het corpus de ωB97X-Hessiaan heeft, staat de
waarheid ernaast. Voor benzeen, een molecuul uit hold-out (a), is dat een afwijking van
1,27 cm⁻¹ en een overlap van 0,985.

De **licentie** volgt besluit 65. Een familie is vrijgegeven als de gemiddelde fout van de drie
seeds op beide hold-outs binnen 3 cm⁻¹ blijft. De fouten van v1.3, in cm⁻¹:

| Familie | hold-out (a), 8 moleculen | hold-out (b), 39 moleculen | Vrijgegeven? |
|---|---|---|---|
| ring-ip | 1,77 | 2,12 | ja |
| CH-strek | 1,19 | 2,50 | ja |
| CH-oop | 2,17 | 2,70 | ja |
| other | 3,62 | 3,89 | nee |

De fout is gemeten tegen ωB97X/6-31G*, het DFT-niveau waarop het netwerk leerde. De licentie
geldt dus op dat niveau. Op coupled-cluster-niveau bestaat geen licentie, en elk certificaat
zegt dat. De vorm van het spectrum verbetert sterk: op hold-out (a) stijgt de overlap met de
waarheid van 0,277 (B3LYP) naar 0,979 (gecorrigeerd), op hold-out (b) van 0,366 naar 0,967.

### De aanvraagdienst

Naast de pijplijn staat de aanvraagdienst (`m08/officer.py`). Een aanvraag bestaat uit een
molecuul, de gewenste trede, een budget en vrije tekst. De dienst antwoordt met een
certificaat, met een weigering die de poort of het plafond en de prijs van de ontbrekende stap
noemt, of met een rekenopdracht die pas mag starten na de poort van module 07. Elk antwoord
toont de trap van treden: in de lijst · goedkope berekening klaar · correctie voorspeld ·
spectrum voorspeld · verankerd · gevalideerd. Acht vooraf vastgelegde scenario's (S1–S8)
toetsen de dienst. Ze lopen van "molecuul verankerd" via "boven het budget" en "een verborgen
instructie in de aanvraag" tot "de mislukking getoond". Alle acht slagen. Voor een
gecorrigeerd spectrum verwijst de dienst nu naar de pijplijn.

### De pijplijnshow

De show (`m08/show.py`) is één webpagina voor een groot scherm. Links kies je een molecuul,
gesorteerd op aantal koolstofatomen. In het midden staat de pijplijn als metrokaart met zes
stations: molecuul, startgeometrie, optimalisatie, Hessiaan + APT, ΔH-netwerk, en spectrum +
certificaat. Rechts verschijnen het spectrum en het certificaat.

De kaart heeft twee lijnen. Op de **hoofdlijn** is elke stap berekend. De **corpuslijn** buigt
af bij optimalisatie en Hessiaan + APT, omdat die twee stappen uit het corpus kwamen. Het
bolletje dat het molecuul voorstelt, volgt de lijn die de run echt nam.

In de **replay** rijdt het bolletje in een vast tempo langs de stations. Elk station toont
daarna de tijd die de stap echt kostte, gelezen uit het record. Bij een berekende stap is dat de
tijd op de laptop. Cinnoline (16 atomen) kostte 53 seconden voor de optimalisatie, 20 minuten
voor Hessiaan + APT en 1 seconde voor netwerk en spectrum. Bij een overgenomen stap toont het
station de tijd die het corpus er destijds over deed. Een overgenomen run duurt op de laptop
minder dan 3 seconden. De pagina typt zelf geen enkel getal in: alles komt uit `pipeline.json`,
`certificate.json` en de opgeslagen arrays.

In de **live-modus** volgt de pagina een run terwijl hij rekent. `m08/show_live.py` start
daarvoor een kleine webserver die alleen op de eigen computer bereikbaar is (127.0.0.1). De
pagina leest elke seconde het `progress.json` van de nieuwste run en laat het station oplichten
dat bezig is. De pagina start zelf geen run: een run start zoals elke run, vanaf de
opdrachtregel.

De show staat openbaar op de Spectrum Atlas, op
https://thebreadishard.github.io/spectrum-atlas/pipeline/, met 42 runs. Acht daarvan zijn de
moleculen van hold-out (a). Dertig zijn moleculen die het netwerk nooit heeft getraind, via
hergebruik uit het corpus.

### De Spectrum Atlas

De Atlas (https://thebreadishard.github.io/spectrum-atlas/, broncode in `website/` in de
hoofdmap van de repository) is de openbare catalogus van het project. Hij lijst 14.248
moleculen. Daarvan zijn er 1.230 doorgerekend en hebben er 11 een coupled-cluster-anker. Een
moleculepagina toont het B3LYP-spectrum (de invoer van de pijplijn), het CC-anker waar dat
bestaat, en de gemeten nauwkeurigheid en licentie van het netwerk. Het gecorrigeerde spectrum
van het netwerk staat niet op de moleculepagina: dat is de uitvoer van de pijplijn, en die is
te zien in de show. Een moleculepagina met een opgenomen run linkt naar die run in de show. De
toegankelijkheidstoets (scenario S6: contrast, toetsenbordbediening, telefoonweergave) slaagt
op de gepubliceerde site. De Atlas wordt alleen gepubliceerd als de gebruiker dat zegt.

## 5. Uitvoer — de datastructuur in detail

**Per run** een resultaatmap met:

- `pipeline.json` (O5): invoer, toelating, deck, rekentijden, hergebruik, beide spectra,
  herkomst;
- `progress.json` (O6): de zes stations met hun toestand en tijd;
- `correction.npz` (O4): de gemiddelde ΔH en die van elke seed;
- `certificate.json` en `certificate.md` (O13): elke band met familie, licentie, fout en
  tolerantie, en één slotzin met wat het certificaat belooft;
- de rekenbestanden `geometry.json`, `hessian_b3lyp_analytic.npz`, `dipole_b3lyp_cphf.npz`,
  en bij een berekende run de logboeken van psi4 en pyscf.

De slotzin van een certificaat zegt bijvoorbeeld: het harmonische infraroodspectrum van
ΔH-netwerk v1.3 (drie seeds), B3LYP/6-31G* gecorrigeerd naar ωB97X/6-31G*, met de fout gemeten
op moleculen die het netwerk nooit zag; vrijgegeven voor ring-ip, CH-strek en CH-oop; op
coupled-cluster-niveau niet gemeten.

**Voor de module** in `modules/08_industry_synthesis/`: de code `m08/` met tests, de scenario's
en hun uitslagen, het notebook `integrated_system.ipynb`, het paper
`Reflective_Synthesis_Paper.pdf` (1.852 woorden, vier bronnen), `requirements.txt`,
`PROVENANCE.md` en de rubriekchecklist. De show staat als `out/pipeline_show.html` in de map en
als openbare pagina op de Atlas.

**De demonstratie.** Op de afspraak met de begeleider (gepland op woensdag 25 november 2026)
wordt de pijplijn getoond zoals hij dan is (besluit 64). Eerst de architectuur. Dan kiest de
begeleider een molecuul dat het netwerk niet heeft gezien en dat binnen een half uur rekent.
Terwijl het rekent, volgt de live-modus de run. Aan het eind van het uur wordt het certificaat
gelezen. De losse momentopname voor de inlevering komt in de schrijffase.

## 6. Waarom deze module?

Dit is het eindproduct; alle eerdere modules bestaan ervoor. Volgens besluit 63 eindigt de
capstone met het *proxybewijs*: de pijplijn staat, de correctie per familie is geleerd en
getoetst met twee DFT-niveaus (B3LYP naar ωB97X) op hold-outs, en de bestaande CCSD(T)-ankers
vormen de brug naar het betere niveau. Module 08 is het deel van dat bewijs dat je kunt
aanraken. Wat hier nieuw is, bestaat in geen eerdere module: de pijplijn als één programma, het
certificaat per band met zijn licentie, het hergebruik uit het corpus, en de show.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Paper en notebook lopen achter.** Beide beschrijven nog de licentieregel van vóór het
  ΔH-netwerk, waarin geen enkele familie was vrijgegeven. Controleer vóór de inlevering dat ze
  besluit 65 en de getallen van de tabel in §4 gebruiken.
- **Het niveau van de belofte.** De licentie geldt op ωB97X-niveau. Controleer dat paper,
  presentatie en Atlas nergens een coupled-cluster-nauwkeurigheid claimen voor v1.3, en dat
  'other' als niet vrijgegeven staat.
- **Harmonische posities.** De anharmonische verschuiving zit niet in de pijplijn. Een
  vergelijking met labspectra moet dat vermelden.
- **Bereik.** Het netwerk trainde op moleculen van 8 tot 30 atomen. Een groter molecuul wordt
  wel gerekend, maar het certificaat zegt dat het buiten die grootte valt. Kationen en
  radicalen worden geweigerd.
- **Volgorde van de atomen.** De pijplijn kiest één vaste volgorde, maar netwerk v1.3 blijft
  gevoelig voor de volgorde. Dat hoort in het paper bij de grenzen.
- **Schone hold-outs.** Een fout op een hold-out telt alleen als het netwerk dat molecuul nooit
  zag, ook niet onder een andere naam (hoofdstuk 6, §6.5). Controleer dat het certificaat de
  schone hold-out (a) leest.
- **Eerlijk verliezen.** De rubriek beloont een evaluatie die ook mislukkingen toont. Het plan
  heeft voor elke mislukking een vooraf geschreven zin
  ([hoofdstuk 5](05_De_Kern_Delta_Probing.md), §5.9 "Eerlijk verliezen"), en scenario S8 toont
  een mislukking op benzeen. Controleer dat het paper die zinnen gebruikt en een verlies, zoals
  de familie 'other', niet verzacht.
- **Minstens drie, traceerbaar.** Het paper moet per geïntegreerde module zeggen wat ze bijdraagt
  en waar in de stroom. De tabel van §3 is het sjabloon.
- **Woorden en bronnen.** 1.500–2.000 woorden; het script dat het paper bouwt, weigert daarbuiten.
  Minstens drie bronnen, waarvan één wetenschappelijk.
- **Eén versie op de pagina.** De show toont elk molecuul bij de pijplijnversie die het rekende.
  Vóór de demonstratie wordt de show opnieuw gebouwd op de versie van dat moment.

## 8. In het kort

Module 08 bouwt de pijplijn als één programma: een molecuul erin, zijn harmonische
infraroodspectrum eruit, in vijf stappen (startgeometrie, optimalisatie, B3LYP-Hessiaan en APT,
de ΔH-correctie van drie seeds, spectrum). Waar het corpus het molecuul al rekende, neemt de
pijplijn stap 2 en 3 over. Het certificaat zegt per band hoe goed die bekend is. Drie families
zijn vrijgegeven op ωB97X-niveau; 'other' niet; op coupled-cluster-niveau is niets beloofd. De
aanvraagdienst beantwoordt aanvragen met een certificaat, een weigering of een rekenopdracht
achter de poort van module 07. De pijplijnshow laat runs zien als een rit over een metrokaart,
met de echte rekentijden of live, en staat openbaar op de Spectrum Atlas.

*Bron: [PIPELINE.md](../modules/PIPELINE.md) (versies 0.1–0.9);
[README](../modules/08_industry_synthesis/README.md),
[RUBRIC_CHECKLIST_2026-09-28.md](../modules/08_industry_synthesis/RUBRIC_CHECKLIST_2026-09-28.md),
[PIPELINE_BACKLOG.md](../modules/08_industry_synthesis/PIPELINE_BACKLOG.md) en
[PIPELINE_BUILD_NOTE_2026-10-29.md](../modules/08_industry_synthesis/PIPELINE_BUILD_NOTE_2026-10-29.md)
van module 08; de code `m08/pipeline.py`, `m08/live_certificate.py`, `m08/show.py`,
`m08/show_template.html` en `m08/show_live.py`; de records in
`probes/results_m1/pipeline_rehearsal_2026-10-30/cinnoline/` en
`probes/results_m1/pipeline_benzene_reuse_2026-11-03/benzene/`; de samenvatting
`probes/results_m1/pipeline_show_summary_2026-11-02.md`; de export van de Atlas
(`website/export/out`, gebouwd 2 november 2026); [TASKS.md](../TASKS.md) rijen 146 en 154;
README-besluiten 63–65; [Rubrics/08](../../../Rubrics/08_Industry_Integrated_AI_Systems_Synthesis.md).*
