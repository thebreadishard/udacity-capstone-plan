# Hoofdstuk 6 — Datastructuren en de pijplijn

> **In dit hoofdstuk leer je**
> – welke soorten databestanden er in dit project bestaan en hoe ze eruitzien;
> – wat een "configuratie" is en waarom die de basiseenheid van alles is;
> – hoe die configuraties worden verzonnen;
> – welke eenheden er worden gebruikt en hoe je ertussen omrekent;
> – hoe alle stappen op elkaar aansluiten, in één overzicht.

Dit hoofdstuk is het naslagwerk voor deel B. In de projecthoofdstukken wordt
telkens verwezen naar de vormen die hier worden gedefinieerd.

---

## §6.1 Waarom de vorm van data ertoe doet

In dit project is de vorm van de data geen bijzaak. Twee voorbeelden waaruit dat
blijkt:

- Project 04 mag alleen een **tabel** gebruiken, project 05 alleen een
  **driedimensionale tensor**. Een tabel opdringen aan project 05 zou de hele
  onderzoeksvraag onderuithalen.
- De schoolregels verbieden dat twee projecten dezelfde dataset gebruiken. Omdat
  water en benzeen uit dezelfde rekencampagne komen, moest er nauwkeurig worden
  vastgelegd wélk bestand bij welk project hoort.

## §6.2 De configuratie: de eenheid van alles

> **Definitie 6.1 — Configuratie**
> Eén configuratie is één momentopname van een molecuul: de posities van alle
> atoomkernen, plus alles wat daarbij hoort berekend is. Elke configuratie heeft
> een uniek nummer, het `config_id`.

Een configuratie is dus **geen** molecuul en **geen** simulatie, maar één
bevroren stand. Voor water zijn dat 9 getallen (3 atomen × 3 coördinaten), voor
benzeen 36.

Het `config_id` is de lijm van het hele project. Doordat elke stand een vast
nummer heeft, kun je later hard maken dat twee modellen echt precies dezelfde
leerstof hebben gekregen — een eis die in hoofdstuk 11 en 15 cruciaal wordt.

## §6.3 Hoe configuraties worden verzonnen

Je hebt er duizenden nodig. Waar komen ze vandaan? Uit drie bronnen
([Distilled Plan §5](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)):

| Manier | Wat er gebeurt | Kost dit een dure berekening? |
|---|---|---|
| **Normaalmodusverplaatsing** | Zet het molecuul uit langs één normaaltrilling (hoofdstuk 2), zowel met kleine als met grote amplitude | Ja |
| **Thermische verplaatsing** | Verschuif alle atomen willekeurig, met een grootte die past bij een temperatuur tussen 100 en 600 K | Ja |
| **Starre draaiing/verschuiving** | Draai of verplaats het hele molecuul, zonder de vorm te veranderen | **Nee** |

Die laatste rij is belangrijk. Draaien verandert de energie niet, dus je hoeft
niets opnieuw te berekenen: je hergebruikt de bekende energie bij een andere
oriëntatie. Zulke rijen heten **augmentatie** en tellen uitdrukkelijk **niet** mee
voor het budget van 2000 (water) of 5000 (benzeen) dure berekeningen. Dat is een
eerlijkheidsregel: anders zou je het aantal berekeningen kunnen opblazen zonder
één extra kwantumberekening te doen.

Nog een regel: de data wordt gesplitst **per configuratie**, nooit per willekeurig
punt uit een trajectorie. Punten die vlak na elkaar in dezelfde beweging liggen,
lijken namelijk sterk op elkaar; die over train en test verdelen zou de test
veel te makkelijk maken.

## §6.4 De zeven datavormen

### Vorm 1 — De tabel (CSV)

Een gewoon tekstbestand met rijen en kolommen, te openen in Excel.

```
config_id,r_OH1,r_OH2,theta_HOH,energy_hartree,fx_O,fy_O,fz_O,fx_H1,...
000001,0.9584,0.9584,104.51,-76.3412,0.0001,-0.0002,0.0000,...
000002,0.9721,0.9503,103.88,-76.3389,0.0143,-0.0087,0.0011,...
```

- **Eén rij = één configuratie.**
- De eerste kolommen beschrijven de **stand** (invoer voor een model).
- De volgende kolommen bevatten de **uitkomsten**: energie en krachten (de
  gewenste uitvoer van een model).

Wordt gebruikt in project 02, 03 en 04.

### Vorm 2 — De volumetrische tensor

Een `.npz`- of HDF5-bestand met een driedimensionale getallenrij: het rooster uit
hoofdstuk 5. Voor benzeen is dat een blok van $64 \times 64 \times 64$ getallen.

Niet te openen in Excel; wordt gelezen door een programma. Per configuratie zit
er in zo'n bestand:

- de kernposities (36 getallen voor benzeen);
- de doeldichtheid $\Delta\rho$ op het rooster ($64^3$ getallen);
- de energie (1 getal);
- de krachten of richtingsafgeleiden (36 getallen of minder);
- het dipoolmoment (3 getallen);
- soms een deel van de Hessiaan.

Wordt gebruikt in werkstroom P1 en project 05.

### Vorm 3 — Het manifest

Een tabel die als inhoudsopgave dient bij vorm 2, met per configuratie **de
herkomstgegevens**. Dit is het bestand waar de wetenschappelijke betrouwbaarheid
in zit. Het plan schrijft de kolommen letterlijk voor:

| Kolom | Betekenis |
|---|---|
| `theory_energy` | Met welke methode is de energie berekend? (CCSD(T)/cc-pVTZ) |
| `theory_density` | Met welke methode de dichtheid? (CCSD, gerelaxeerd of niet) |
| `derivative_kind` | Volledige gradiënt, eindige differentie, of richtingsafgeleide? |
| `derivative_theory` | Van welk energie-oppervlak komt die afgeleide? |
| `fd_step_bohr` | Welke stapgrootte $h$ is gebruikt? |
| `direction_seed`, `direction_vector` | Bij een richtingsafgeleide: welke richting precies? |
| `derivative_uncertainty` | Hoe onzeker is die afgeleide? |
| `dipole_theory`, `dipole_origin`, `dipole_x/y/z_e_bohr` | Het dipoolmoment en zijn oorsprongconventie |
| `rdm_relaxed\|unrelaxed` | Welke variant van de dichtheidsmatrix? |
| `pyscf_version`, `grid`, `ref_fit_id` | Welke programmaversie, welk rooster, welke atoomfit? |
| `wall_s`, `max_rss_gb` | Hoe lang duurde het en hoeveel geheugen kostte het? |

Het plan sluit af met een harde uitspraak: *"If the applicable fields are blank,
it is not a dataset."* Data zonder herkomst is geen data.

### Vorm 4 — Het splitsingsbestand

Een JSON-bestand, bijvoorbeeld `splits/h2o_v1.json`, met drie lijsten van
`config_id`s: train, validatie en test, plus welke trillingsfamilie is
achtergehouden.

Dit bestand moet **vastgelegd en van een controlegetal (hash) voorzien zijn
vóórdat er ook maar één model getraind wordt**. Elk later rapport moet dat
controlegetal vermelden. Zo kan achteraf niemand — ook de onderzoeker zelf niet —
stiekem opnieuw splitsen tot de uitkomst bevalt.

### Vorm 5 — De bevroren gewichten

Het getrainde model: een bestand met alle geleerde getallen. "Bevroren" betekent
dat het bestand na de training niet meer verandert. Alle spectra worden met
bevroren gewichten gemaakt.

### Vorm 6 — De trajectorie

De uitvoer van een simulatie: voor elke tijdstap de posities, de snelheden, de
energie en het dipoolmoment. Voor 50 ps met stappen van 0,5 fs zijn dat 100 000
regels. Uit de dipoolkolommen volgt via §4.7 het spectrum.

### Vorm 7 — Het spectrum en het toetsrapport

Het spectrum is simpel: twee kolommen, golfgetal en intensiteit.

Het **toetsrapport** (*gate report*) is minstens zo belangrijk. Daarin staat per
eis: de drempelwaarde, de gemeten waarde, en het oordeel GESLAAGD of GEZAKT.
Zonder gemeten waarde naast de drempel is een oordeel ongeldig — dat is de regel
die in hoofdstuk 14 de agent afdwingt.

## §6.5 De eenheden

| Grootheid | Eenheid | Omrekening |
|---|---|---|
| Lengte | ångström (Å) | $1\ \text{Å} = 10^{-10}$ m |
| Lengte (atomair) | bohr ($a_0$) | $1\ a_0 = 0{,}5292$ Å |
| Energie | hartree | $1\ \mathrm{Ha} = 627{,}5$ kcal/mol $= 27{,}211$ eV $= 219\,474$ cm⁻¹ |
| Energie (chemisch) | kcal/mol | $1$ kcal/mol $= 350$ cm⁻¹ |
| Kracht | meV/Å | $1$ meV/Å $= 1{,}95\times10^{-5}$ hartree/bohr |
| Golfgetal | cm⁻¹ | zie §2.3 |
| Dipoolmoment | $e\,a_0$ | $1\ e\,a_0 = 2{,}542$ debye (D) |

> **Voorbeeld 6.1**
> De eis voor het dipoolmoment luidt: fout kleiner dan $0{,}01\ e\,a_0$. Water
> heeft een dipoolmoment van $1{,}85$ D. Hoe streng is die eis relatief?
>
> *Uitwerking.*
> $$0{,}01\ e\,a_0 = 0{,}01 \times 2{,}542 = 0{,}025\ \mathrm{D}$$
> $$\frac{0{,}025}{1{,}85} = 0{,}0137 \approx 1{,}4\%.$$
>
> De eis is dus ongeveer anderhalve procent. Dat komt exact overeen met wat er in
> het plan staat, en het laat zien waarom er in $e\,a_0$ wordt gerekend: pas na
> omrekening zie je hoe streng de eis eigenlijk is.

> **Voorbeeld 6.2**
> Reken de machinefoutgrens van $0{,}1$ meV/Å om in atomaire eenheden.
>
> *Uitwerking.*
> $$0{,}1 \times 1{,}95\times10^{-5} = 1{,}95\times10^{-6}\ \text{a.u.}$$
> In het plan staat $1{,}9\times10^{-6}$ a.u. — dezelfde waarde.

## §6.6 De pijplijn in één tabel

Dit is de kern van deel B, vooruit samengevat. Lees elke rij als: *deze stap
krijgt dit binnen en levert dit af.*

| Stap | Invoer | Uitvoer |
|---|---|---|
| **Fase 0a** — motor bouwen | Analytische testdichtheden; geen kwantumchemie | Werkende rekenmachine + sweep-CSV (800 rijen) |
| **Project 03** | Die sweep-CSV | Statistisch rapport: hangt de eierdoosfout af van $\sigma/\Delta x$? |
| **Fase 0b** — proefdraaien | 1 en 10 geometrieën van water en benzeen | Gemeten kostentabel; keuze van de rekenroute; nauwkeurigheidsoordeel |
| **Campagne water** | ~2000 waterstanden | Descriptor-CSV (project 04) **en** volumetrische tensoren (P1) |
| **Project 02** | Openbare QM9-tabel | Verkennend rapport: waarom bestaande data niet volstaat |
| **Project 04** | Descriptor-CSV | Eenvoudig ijkmodel + foutmaten |
| **Werkstroom P1** | Volumetrische tensoren water | Bevroren veldmodel + toetsrapport |
| **Werkstroom G1** | Dezelfde `config_id`s, alleen $E$ en krachten | Bevroren graafmodel (MACE) + toetsrapport |
| **Campagne benzeen** | ~5000 benzeenstanden | Volumetrische tensoren + manifest (project 05) |
| **Project 05** | Die tensoren | Vlaggenschipmodel + vergelijking met/zonder FNO |
| **Project 06** | Goedkope geometrieën van 5–8 aromaten | VAE + gegenereerde voorbeeldstructuren |
| **Fase 2/3** | Bevroren P1-gewichten | Trajectorieën → spectra van H₂O, D₂O, CO₂ |
| **Project 07** | Alle bovenstaande logbestanden | Agent die GESLAAGD/GEZAKT uitspreekt met bewijs |
| **Project 08** | Minstens 3 eerdere projecten + G1-rapport | Geïntegreerd systeem + reflectiepaper |
| **Project 09** | Project 08 | Mondelinge verdediging |
| **Projecten 10–12** | Alles hierboven | De horizon: grote PAK's, echte spectra, identificatie |

## §6.7 Twee regels die overal gelden

**Regel 1 — Publicatie vóór bewering.**
Voordat een verslag mag schrijven "deze dataset komt van X", moet die dataset
publiek en citeerbaar zijn, met een DOI (een permanent identificatienummer, hier
via het archief Zenodo). Geen belofte achteraf.

**Regel 2 — Deze data is niet door AI verzonnen.**
De schoolregels verbieden "synthetische of door AI gegenereerde" datasets. De
data in dit project is berekend met een deterministisch natuurkundeprogramma, wat
iets heel anders is. Elk verslag moet daarom één zin bevatten die dat
verduidelijkt, bijvoorbeeld: *"Berekend met PySCF via ab-initio coupled-cluster
kwantumchemie — een eerste-principesmethode, geen door AI gegenereerde
synthetische dataset."*

Het plan voegt daar een praktisch advies aan toe: ga hierover niet in discussie
met de beoordelaar, maar zorg dat de link naar de openbare dataset gewoon werkt.

## In het kort

- De basiseenheid is de **configuratie**: één stand van een molecuul, met een uniek `config_id`.
- Configuraties ontstaan uit normaalmodusverplaatsing, thermische verstoring en (gratis) starre draaiing.
- Er zijn zeven datavormen: tabel, tensor, manifest, splitsingsbestand, gewichten, trajectorie en spectrum/toetsrapport.
- Het manifest bevat de herkomst; ontbreekt die, dan is het geen dataset.
- De splitsing wordt vastgelegd en gehasht vóórdat er getraind wordt.
- Twee vaste regels: publiceer vóór je een bron claimt, en leg uit dat berekende data geen AI-data is.
