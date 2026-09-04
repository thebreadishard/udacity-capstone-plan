# Hoofdstuk 15 — Project 08: alles aan elkaar knopen

> **In dit hoofdstuk leer je**
> – wat een "industriële inkadering" is en waarom die hier eerlijk moet blijven;
> – hoe de eindvergelijkingstabel eruitziet en hoe je die leest;
> – welke zes dingen dit project op tafel mag leggen — en welke niet;
> – waarom er in dit project niets voor het eerst mag gebeuren.

**Categorie in het plan:** (A) natuurlijke aansluiting, per constructie afhankelijk van 04 t/m 07.
**Positie in de keten:** het sluitstuk van de master.

---

## §15.1 Wat is de vraag?

De schoolopdracht: voeg minstens drie eerdere projecten samen tot één systeem met
een duidelijke inkadering vanuit de beroepspraktijk, en schrijf een reflectiepaper
van 1500 tot 2000 woorden waarin je aantoont hoe elk van die projecten het ontwerp
heeft beïnvloed.

De onderzoeksvraag eronder:

> Alle onderdelen bestaan nu. **Wat is het antwoord op de vraag uit hoofdstuk 1, en
> wat is het geheel waard als je het als één systeem bekijkt?**

## §15.2 De inkadering

> **De inkadering, letterlijk uit het plan**
> *"Reliability-gated spectral emulation for small molecules."*
> Betrouwbaarheidsgecontroleerde spectrale emulatie voor kleine moleculen.

Ontleed die zin:

| Woord | Betekenis |
|---|---|
| *spectrale emulatie* | Een snel model bootst na wat anders een peperdure kwantumberekening vergt |
| *betrouwbaarheidsgecontroleerd* | Het systeem weigert een antwoord te geven als de controles niet gehaald zijn |
| *voor kleine moleculen* | De eerlijke afbakening: water, zwaar water, koolstofdioxide, benzeen |

Wat er níét staat is even belangrijk. Er staat niet "PAK-identificatie". De
JWST-toepassing uit hoofdstuk 1 mag genoemd worden als **motivering** — als
antwoord op de vraag waarom iemand hier later belang bij zou hebben — maar niet
als iets wat gebouwd is.

Het plan schrijft die zin zelfs voor: *"An honest scope sentence: JWST /
large-PAH identification is why anyone would care later. It is not a capability
that was built."*

## §15.3 Invoer

| Bron | Wat het levert |
|---|---|
| Project 04 | Het eenvoudige ijkmodel |
| Project 05 | Het benzeenmodel |
| Project 06 | Het voorstelmechanisme |
| Project 07 | De betrouwbaarheidslaag |
| Werkstroom P1 | Het veldmodel op water en de twee vergelijkingsbenen |
| Werkstroom G1 | Het graafmodel op dezelfde splitsing |

Er zijn er minstens drie van de eerste vier nodig. De twee werkstromen zijn geen
schoolprojecten maar leveren wel de getallen die de wetenschappelijke bewering
dragen.

## §15.4 Wat er wordt samengesteld

Hier komt fase 4 tot uitvoering: de vergelijking waar het hele plan naartoe heeft
gewerkt.

**De hoofdtabel — gelijke leerstof, verschillende voorstelling:**

| Model | Voorstelling | Leerstof | Krachtfout op de achtergehouden trillingsfamilie |
|---|---|---|---|
| MACE-EF | Graaf | $E$ + krachten | gemiddelde ± spreiding over ≥ 3 startgetallen |
| Field-EF | Rooster | $E$ + krachten | gemiddelde ± spreiding over ≥ 3 startgetallen |

Daaruit volgt de verhouding $r$ en, via de vooraf vastgelegde regel uit §11.5, de
uitslag.

**De nevenvergelijking — gelijke voorstelling, verschillende leerstof:**

| Model | Verschil | Waarvoor |
|---|---|---|
| Field-EF | $\lambda_\rho = 0$ | referentie |
| Field-EFρ | $\lambda_\rho > 0$ | meet wat dichtheidsdata oplevert |

**De ruimere tabel — hoe goed is het geheel eigenlijk?**

| Been | Wat het is |
|---|---|
| Eenvoudig netwerk (04) | De ondergrens: hoe ver kom je zonder al deze techniek? |
| Harmonische CCSD(T)-Hessiaan | De klassieke rekenroute, zonder machine learning |
| Volledig productiemodel | Het beste *systeem*, met alle vijf verliestermen |

Verder komen in de tabel: de fout binnen het bekende gebied, de harmonische fout
tegen de ene CCSD(T)-Hessiaan, de stabiliteit van de simulaties, en de kosten in
rekentijd en parameters.

> **Waarschuwing bij het lezen**
> Het volledige productiemodel staat in een **aparte rij**, nooit in de bovenste
> tabel. Het kan namelijk het beste systeem zijn en toch niets zeggen over de vraag
> uit hoofdstuk 1, omdat het meer informatie heeft gehad (§11.3). De scheiding
> tussen "welk systeem werkt het best" en "welke voorstelling generaliseert beter"
> wordt tot het einde volgehouden.

## §15.5 De zes toegestane beweringen

[Overarching_Goal §5](../GoalGathering/Overarching_Goal.md) somt uitputtend op wat
dit project op tafel mag leggen:

1. **Een conservatief veld-PES** — P1 op water, project 05 op benzeen als de
   kostenmeting dat toeliet.
2. **Bandenveloppen uit simulatie met bevroren gewichten**, binnen de genoemde
   marge in cm⁻¹, zonder enige spectrale fitting.
3. **Een fail-closed betrouwbaarheidslaag** (project 07). Haalde P1 zijn eisen
   niet, dan zegt project 08 dat de veldbewering onvolledig is.
4. **Bewijs dat het veld de moeite waard was** — project 04 plus de vooraf
   geregistreerde vergelijking en de dichtheidsablatie.
5. **Een voorstelmechanisme** (project 06), uitdrukkelijk geen databron.
6. **Een eerlijke afbakeningszin** over JWST.

En de vier toegestane eindconclusies, letterlijk vooraf vastgelegd:

| Uitkomst | Conclusie |
|---|---|
| Field-EF wint | Steun voor de veldhypothese bij gelijke supervisie |
| Field-EF wint niet, Field-EFρ wel | De dichtheidsgesuperviseerde pijplijn wint; over de voorstelling niets aangetoond |
| Geen van beide | Geen aangetoond voordeel boven het graafmodel |
| Binnen de marge | Niet vast te stellen |

## §15.6 De regel: hier begint niets

Dit is misschien wel de strengste regel van het hele plan.

> **Regel — *Nothing debuts in Module 08.***
> In dit project mag geen enkel model voor het eerst worden getraind, geen enkele
> dataset voor het eerst worden gemaakt en geen enkele meting voor het eerst worden
> gedaan. Alles wat hier staat, bestond al.

De reden is te zien in het faalscenario. Zou MACE hier voor het eerst getraind
worden, dan zou dat gebeuren in de laatste weken van de opleiding, onder tijdsdruk,
zonder gelijke afsteltijd — en dan is de vergelijking waardeloos. Vandaar
werkstroom G1, die dat werk maanden eerder doet, op dezelfde splitsing, met
dezelfde zorg.

Ontbreekt een been, dan geldt:

- Project 08 meldt de vergelijking als **onvolledig**;
- het model van project 04 wordt **niet** in de plaats van MACE gezet;
- er wordt niet stilzwijgend iets anders ingevuld.

## §15.7 De taalregels

Uit [Capstone_Mapping §5.2](../GoalGathering/Capstone_Mapping.md), en ze zijn hard:

| Verboden | Toegestaan |
|---|---|
| "chemisch nauwkeurige spectraallijnen" | "bandposities en relatieve enveloppen binnen een genoemde marge in cm⁻¹" |
| "nauwkeurigheid onder één golfgetal" | "10 tot 15 cm⁻¹, zoals vooraf vastgelegd" |
| "willekeurig grote PAK's" | "vooruitblik; zie de projecten 10 t/m 12" |
| "wij hebben PAK's geïdentificeerd" | "dit is waarom het later zou uitmaken" |
| naftaleen als slagen-of-zakken-criterium | naftaleen als verkennende bespreking |

Die laatste rij verdient toelichting. Naftaleen — twee ringen — is het volgende
logische molecuul. Het plan staat toe dat het model er zonder enige training op
wordt losgelaten, puur uit nieuwsgierigheid. Maar de uitkomst mag **nooit** als
slagen of zakken worden gepresenteerd, want het model heeft nooit twee gekoppelde
ringen gezien en de $\pi$-elektronen gedragen zich daar wezenlijk anders.

## §15.8 Uitvoer

| Bestand | Inhoud |
|---|---|
| Geïntegreerd artefact | Het samengestelde systeem met diagrammen |
| `Reflective_Synthesis_Paper.pdf` | 1500 tot 2000 woorden, met minstens drie bronnen |
| Presentatie voor de mentor | 15 minuten |

De reflectiepaper moet aantoonbaar maken hoe elk van de gebruikte projecten het
ontwerp heeft beïnvloed. Dat is hier eenvoudiger dan gebruikelijk, omdat het
gewoon waar is: project 04 leverde het ijkpunt, project 07 de betrouwbaarheidslaag,
project 05 de motor, project 06 het voorstelmechanisme. Er hoeft geen verband te
worden verzonnen.

## §15.9 Waarom deze stap?

Omdat losse onderdelen geen antwoord zijn. Er zijn nu een eenvoudig model, een
veldmodel, een graafmodel, een generator en een controle-agent. De vraag uit
hoofdstuk 1 wordt pas beantwoord als die getallen náást elkaar in één tabel staan,
gemeten onder afspraken die maanden eerder zijn vastgelegd.

En er is een tweede reden, die met de beroepspraktijk te maken heeft. Een systeem
dat een antwoord geeft is makkelijk. Een systeem dat weet wanneer het geen antwoord
mag geven, is zeldzaam en waardevol. Dat is wat de inkadering
"betrouwbaarheidsgecontroleerd" werkelijk betekent, en het is de verdedigbaarste
bewering die dit project kan doen.

## In het kort

- **Invoer:** minstens drie van de projecten 04 t/m 07, plus de toetsrapporten van P1 en G1.
- **Bewerking:** de vooraf vastgelegde vergelijkingstabellen invullen en de conclusie aflezen volgens de regel die maanden eerder is opgeschreven.
- **Uitvoer:** een geïntegreerd systeem, een reflectiepaper en een presentatie.
- De inkadering is "betrouwbaarheidsgecontroleerde spectrale emulatie voor kleine moleculen" — JWST is motivering, geen gebouwde functie.
- Hier begint niets; alles bestond al. Ontbreekt een been, dan heet de bewering onvolledig.
- Er gelden vaste taalregels: banden en enveloppen mogen, lijnen en "willekeurige grootte" niet.
