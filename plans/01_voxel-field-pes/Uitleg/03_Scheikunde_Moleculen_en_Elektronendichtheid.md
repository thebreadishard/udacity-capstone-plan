# Hoofdstuk 3 — Scheikunde: moleculen en elektronendichtheid

> **In dit hoofdstuk leer je**
> – wat een elektronendichtheid is en waarom scheikundigen daarmee rekenen;
> – wat de Born–Oppenheimer-benadering is en waarom die alles vereenvoudigt;
> – wat een potentiële-energie-oppervlak (PES) is;
> – wat CCSD(T)/cc-pVTZ betekent, letter voor letter;
> – waarom DFT in dit project verboden is, en waarom dat toch genuanceerd ligt;
> – wat "chemische nauwkeurigheid" betekent en hoe je die controleert.

---

## §3.1 Van bolletjes naar wolken

In de schoolscheikunde teken je een molecuul als bolletjes met staafjes ertussen.
Dat is een handig model, maar het is niet wat er werkelijk is.

Wat er werkelijk is: een klein aantal zware, positief geladen **atoomkernen**, en
daaromheen een wolk van lichte, negatief geladen **elektronen**. Die elektronen
hebben geen baan en geen vaste plaats. Volgens de kwantummechanica kun je
alleen zeggen hoe **waarschijnlijk** het is dat er op een bepaalde plaats een
elektron zit.

> **Definitie 3.1 — Elektronendichtheid**
> De elektronendichtheid $\rho(\mathbf r)$ geeft aan hoeveel elektronenlading er
> per volume-eenheid op plaats $\mathbf r$ zit. De eenheid is lading per volume.
> Er geldt altijd
> $$\int \rho(\mathbf r)\,\mathrm{d}V = N_e,$$
> waarin $N_e$ het totale aantal elektronen is.

Dat integraal is een **behoudswet**: de elektronen kunnen wel verschuiven, maar
ze verdwijnen niet. In dit project is die eigenschap een controlemiddel. In de
kwaliteitslijst staat de eis dat het uitgerekende aantal elektronen tijdens een
hele simulatie binnen 0,01% moet blijven kloppen
([Distilled Plan §8, punt 9](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)).

De dichtheid is een functie van drie variabelen ($x$, $y$, $z$) die een getal
oplevert. Zo'n object heet een **scalair veld**. Je kunt het je voorstellen als
een mistwolk: dicht bij de kernen dik en ondoorzichtig, verder weg ijl.

Bij de kernen is die wolk trouwens niet alleen dik maar ook *scherp*: de
dichtheid heeft daar een piek met een knik, een zogeheten **cusp**. Onthoud die
knik — in hoofdstuk 5 blijkt hij het lastigste technische probleem van het hele
project te zijn.

## §3.2 De Born–Oppenheimer-benadering

Een proton is ongeveer 1836 keer zo zwaar als een elektron. Voor een
koolstofkern is de verhouding meer dan 20 000. Daaruit volgt een enorme
vereenvoudiging.

> **Definitie 3.2 — Born–Oppenheimer-benadering**
> Omdat de kernen zoveel zwaarder zijn dan de elektronen, bewegen ze veel
> langzamer. Je mag daarom aannemen dat de elektronenwolk zich op elk moment
> **onmiddellijk** aanpast aan de stand van de kernen. Je rekent de elektronen dus
> uit bij *stilstaande* kernen.

Het gevolg: het probleem valt in twee stukken uiteen.

1. Zet de kernen op vaste plaatsen $\mathbf R$. Reken de energie van de
   elektronenwolk uit. Dat levert één getal: $E(\mathbf R)$.
2. Verschuif de kernen een beetje en herhaal.

Zo ontstaat een functie van de kernposities naar de energie.

## §3.3 Het energielandschap (PES)

> **Definitie 3.3 — Potentiële-energie-oppervlak (PES)**
> Het PES is de functie
> $$E : \mathbf R \longmapsto E(\mathbf R)$$
> die aan elke stand van de atoomkernen de bijbehorende energie toekent.

De naam "oppervlak" komt van het geval met twee variabelen: dan kun je $E$
tekenen als een heuvellandschap boven het $xy$-vlak. Bij meer variabelen kan dat
niet meer, maar de taal blijft.

Het PES is de **hoofdrolspeler van dit hele project**. Alles wat het model moet
leren, is dit ene oppervlak.

> **Voorbeeld 3.1**
> Hoeveel variabelen heeft het PES van water, en hoeveel dat van benzeen?
>
> *Uitwerking.*
> Water heeft 3 atomen, dus $3 \times 3 = 9$ coördinaten. Verplaatsing en draaiing
> van het hele molecuul veranderen de energie niet, dus daar gaan $3 + 3 = 6$
> vrijheidsgraden vanaf. Blijft over: **3 variabelen**. Je kunt die kiezen als de
> twee O–H-afstanden en de H–O–H-hoek.
>
> Benzeen heeft 12 atomen: $3\times12 - 6 = \boxed{30}$ variabelen.

Een functie van 30 variabelen kun je niet tabelleren. Zelfs met 10 waarden per
variabele zou je $10^{30}$ punten nodig hebben. Dít is de reden dat er machine
learning aan te pas komt: een neuraal netwerk kan een gladde functie van veel
variabelen benaderen uit relatief weinig voorbeelden.

Uit het PES volgen twee dingen die je nodig hebt:

> **Eigenschap 3.1 — Kracht uit energie**
> De kracht op atoom $A$ is min de gradiënt van de energie:
> $$\mathbf F_A = -\frac{\partial E}{\partial \mathbf R_A}.$$
> Dit is dezelfde regel als $F = -\mathrm{d}E_p/\mathrm{d}x$ bij natuurkunde.

> **Eigenschap 3.2 — Trillingsfrequenties uit energie**
> De veerconstanten uit hoofdstuk 2 zijn de tweede afgeleiden van $E$. De matrix
> van alle tweede afgeleiden heet de **Hessiaan**:
> $$H_{ij} = \frac{\partial^2 E}{\partial R_i\,\partial R_j}.$$
> Uit de Hessiaan volgen alle normaaltrillingen en hun frequenties in één keer.

## §3.4 De ladder van rekenmethoden

Hoe reken je $E(\mathbf R)$ nu daadwerkelijk uit? Er bestaat een ladder van
methoden: hoe hoger op de ladder, hoe nauwkeuriger én hoe duurder.

| Sport | Methode | Idee | Kosten |
|---|---|---|---|
| 1 | **Hartree–Fock (HF)** | Elk elektron voelt alleen het *gemiddelde* veld van alle andere | $\sim N^4$ |
| 2 | MP2 | Eerste correctie op HF | $\sim N^5$ |
| 3 | CCSD | Elektronen ontwijken elkaar per paar | $\sim N^6$ |
| 4 | **CCSD(T)** | CCSD plus een correctie voor drietallen | $\sim N^7$ |

De sprong van 1 naar 4 draait om één begrip.

> **Definitie 3.4 — Correlatie-energie**
> Elektronen stoten elkaar af en houden dus voortdurend rekening met elkaars
> positie: ze "ontwijken" elkaar. Hartree–Fock negeert dat. Het energieverschil
> tussen de werkelijkheid en Hartree–Fock heet de correlatie-energie:
> $$E_{\text{corr}} = E_{\text{exact}} - E_{\text{HF}}.$$

De correlatie-energie is klein in verhouding tot de totale energie, maar juist
groot in verhouding tot de energieverschillen die je wilt weten. Daarom is die
sport op de ladder cruciaal.

> **Definitie 3.5 — CCSD(T)**
> "Coupled Cluster with Single and Double excitations, and perturbative Triples."
> Dit is in de kwantumchemie de **gouden standaard**: voor moleculen in hun
> grondtoestand levert het resultaten die zo dicht bij de werkelijkheid liggen dat
> het verschil met het experiment vaak binnen de meetfout valt.

## §3.5 De basisset: cc-pVTZ

Naast de methode moet je ook kiezen hóe fijn je de elektronenwolk beschrijft. Dat
gebeurt met een **basisset**: een verzameling standaardfuncties waaruit de
elektronenwolk wordt opgebouwd, zoals je een geluid opbouwt uit sinussen.

> **Definitie 3.6 — cc-pVTZ**
> "correlation-consistent polarized Valence Triple Zeta." Lees het als: een
> basisset van middelhoge fijnheid, speciaal ontworpen om samen te werken met
> correlatiemethoden zoals CCSD(T). De opvolgers heten cc-pVQZ (Quadruple Zeta,
> fijner) en cc-pV5Z (nog fijner).

De letters T, Q, 5 vormen een reeks. Hoe verder je komt, hoe dichter je bij de
**volledige basislimiet** (CBS, Complete Basis Set) zit: het denkbeeldige
resultaat bij een oneindig fijne beschrijving.

> **Voorbeeld 3.2**
> Waarom niet gewoon meteen cc-pV5Z gebruiken?
>
> *Uitwerking.*
> Het aantal basisfuncties $N$ groeit sterk met de fijnheid, en de rekentijd gaat
> als $N^7$. Voor benzeen is cc-pVTZ al $N = 264$; cc-pVQZ komt op ongeveer
> $N = 510$. Dat is een factor $(510/264)^7 \approx 1{,}6\times10^2$ duurder — meer
> dan honderd keer. Vandaar dat het plan cc-pVQZ voor benzeen alleen op een
> supercomputer en alleen voor **twaalf** geometrieën inzet, als controlemeting.

De term **frozen-core** die je in het plan tegenkomt, betekent: de binnenste
elektronen (die vlak bij de kern zitten en nauwelijks meedoen aan chemie) worden
bevroren en niet in de correlatieberekening meegenomen. Dat scheelt veel tijd en
kost weinig nauwkeurigheid — maar je moet het wél consequent doen, en dat is
precies waarom het plan het opschrijft als vaste afspraak.

## §3.6 Chemische nauwkeurigheid, en hoe je die aantoont

> **Definitie 3.7 — Chemische nauwkeurigheid**
> Een energieverschil is "chemisch nauwkeurig" als de fout kleiner is dan
> $1\ \mathrm{kcal/mol}$.

Handige omrekeningen, die je in het plan voortdurend tegenkomt:

$$1\ \mathrm{hartree} = 627{,}5\ \mathrm{kcal/mol} = 27{,}211\ \mathrm{eV} = 219\,474\ \mathrm{cm^{-1}}$$
$$1\ \mathrm{kcal/mol} = 1{,}59\times10^{-3}\ \mathrm{hartree} = 350\ \mathrm{cm^{-1}}$$

Nu komt het punt waarop het plan streng wordt. Zeggen "wij gebruiken CCSD(T)" is
géén bewijs dat je data chemisch nauwkeurig is. Het is alleen de naam van een
methode. Daarom is er een **audit** ingebouwd.

> **Stappenplan 3.1 — De nauwkeurigheidsaudit (Distilled Plan §5.1)**
>
> **Stap 1.** Kies vooraf een vaste, bevroren verzameling geometrieën: 19 voor
> water, 13 voor $\mathrm{CO_2}$ en 12 voor benzeen. Leg ze vast in een bestand,
> met hun coördinaten en een controlegetal, *voordat* er iets gerekend wordt.
>
> **Stap 2.** Reken voor elk van die geometrieën de energie uit met cc-pVTZ ($X=3$)
> én met de fijnere cc-pVQZ ($X=4$).
>
> **Stap 3.** Extrapoleer naar de volledige basislimiet met de standaardformule
> $$E_{\text{ref}} = E_{\mathrm{HF},Q} + \frac{4^{3}E_{\mathrm{corr},Q} - 3^{3}E_{\mathrm{corr},T}}{4^{3} - 3^{3}}
> = E_{\mathrm{HF},Q} + \frac{64\,E_{\mathrm{corr},Q} - 27\,E_{\mathrm{corr},T}}{37}.$$
>
> **Stap 4.** Vergelijk de goedkope productiedata met deze referentie. De vooraf
> vastgelegde slagingseisen zijn:
>
> | Grootheid | Eis |
> |---|---|
> | Relatieve energie | RMSE $\le 1{,}0$ kcal/mol én maximale fout $\le 2{,}0$ kcal/mol |
> | Richtingsafgeleide | RMSE $\le 1{,}0$ meV/Å |
> | Harmonische frequenties | verschuiving $\le 5$ cm⁻¹ |
>
> **Stap 5.** Kies op grond van de uitslag de toegestane bewoording. Slagen alle
> drie de eisen, dan mag je "chemisch nauwkeurig" schrijven. Slaagt alleen de
> energie-eis, dan geldt dat alleen voor energieën. Slaagt niets, of is de audit
> niet uitgevoerd, dan mag je alleen nog "op CCSD(T)/cc-pVTZ-niveau" schrijven.

Let op de laatste regel van stap 5: **ontbrekende data telt nooit als geslaagd**.
Dat is de kern van de werkwijze die je in dit hele project terugziet, en die in
hoofdstuk 14 een naam krijgt: *fail-closed*.

De formule in stap 3 is trouwens minder mysterieus dan hij oogt. De
correlatie-energie nadert de limiet ongeveer als $X^{-3}$. Als je twee punten van
zo'n kromme kent, kun je de limiet uitrekenen — precies zoals je bij wiskunde een
lijn door twee punten trekt om te extrapoleren.

## §3.7 De verhouding tot DFT

Er is één methode die je in de praktijk overal tegenkomt en die hier niet gebruikt
mag worden.

> **Definitie 3.8 — DFT (dichtheidsfunctionaaltheorie)**
> DFT rekent de energie niet uit alle elektronenposities maar uit de
> elektronendichtheid $\rho(\mathbf r)$ alleen. Dat is dankzij de stelling van
> Hohenberg en Kohn in principe exact — maar het exacte verband tussen $\rho$ en
> $E$ is onbekend. In de praktijk gebruikt men benaderde formules, zogeheten
> **functionalen**, met namen als B3LYP, PBE en M06-2X.

DFT is goedkoop ($\sim N^3$) en werkt vaak goed. Maar de gekozen functionaal is
een keuze, en verschillende functionalen geven verschillende antwoorden. Voor
precies de effecten die bij PAK's het belangrijkst zijn — de gedelokaliseerde
$\pi$-elektronen boven en onder het ringvlak, en zwakke dispersiekrachten —
maken de gangbare functionalen **systematische** fouten. Systematisch betekent:
niet uit te middelen door meer data.

Daarom staat er in [Distilled Plan §4](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
dat er geen DFT-data in de pijplijn komt. Toch is er een subtiliteit die je moet
begrijpen, want zonder die nuance snap je hoofdstuk 5 niet:

> **Belangrijke nuance**
> Wat verboden is, zijn (a) bestaande, uit een bibliotheek geplukte functionalen
> zoals B3LYP, en (b) data van DFT-kwaliteit als leerstof. Wat *niet* verboden is,
> is de **vorm** $E = \mathcal{E}[\rho]$: energie als functie van de dichtheid.
> Sterker nog, dat is precies wat dit project bouwt. Het project bouwt dus zijn
> eigen dichtheidsfunctionaal, maar traint hem op CCSD(T)-data in plaats van hem
> te ontlenen aan de literatuur.

Het plan waarschuwt letterlijk dat de leus "NOT DFT" bij de mondelinge
verdediging (hoofdstuk 16) tegen de student gebruikt kan worden als hij de nuance
niet paraat heeft. Deze familie van methoden heet **orbital-free DFT** en bestaat
al vijftien jaar; hoofdstuk 12 gaat in op wat er dan nog wél nieuw is.

## §3.8 Wat is precies "de dichtheid" bij CCSD(T)?

Nog een subtiliteit, die het plan expliciet maakt omdat ze makkelijk te
verdoezelen is.

CCSD(T) levert een uitstekende **energie**, maar levert niet zonder meer een
eenduidige **dichtheid**. Het "(T)"-deel is een storingscorrectie op de energie;
er hoort geen simpele elektronenwolk bij. Wat de rekenprogramma's wel kunnen
leveren, is de dichtheid op het niveau eronder, CCSD.

Het plan lost dat op door het gewoon op te schrijven:

- energie: CCSD(T);
- dichtheid: de zogeheten **gerelaxeerde CCSD 1-RDM** (1-deeltjes-dichtheidsmatrix),
  en als die niet beschikbaar is, de ongerelaxeerde variant — met vermelding in
  het gegevensbestand welke van de twee het is;
- verboden bewoording: "exacte CCSD(T)-dichtheid", tenzij het rekenprogramma die
  aantoonbaar heeft geleverd.

Dit heet in het plan een "gedocumenteerd gat op dichtheidsniveau". Het is een
mooi voorbeeld van de stijl van deze repository: liever een oneffenheid
opschrijven dan hem wegpoetsen.

## In het kort

- Elektronen vormen een wolk met dichtheid $\rho(\mathbf r)$, waarvoor $\int\rho\,\mathrm{d}V = N_e$.
- Born–Oppenheimer: kernen staan stil terwijl je de elektronen uitrekent; zo ontstaat het PES $E(\mathbf R)$.
- Uit het PES volgen krachten (eerste afgeleide) en trillingsfrequenties (tweede afgeleide, de Hessiaan).
- CCSD(T)/cc-pVTZ is de gouden standaard; hij kost $\sim N^7$.
- "Chemisch nauwkeurig" betekent een fout onder 1 kcal/mol en moet worden **aangetoond** met een CBS-audit, niet beweerd.
- DFT is verboden als bron van data en als kant-en-klare functionaal, maar de vórm $E = \mathcal{E}[\rho]$ is juist het onderwerp van dit project.
- De dichtheid komt van CCSD, de energie van CCSD(T); dat verschil wordt eerlijk vermeld in plaats van verzwegen.
