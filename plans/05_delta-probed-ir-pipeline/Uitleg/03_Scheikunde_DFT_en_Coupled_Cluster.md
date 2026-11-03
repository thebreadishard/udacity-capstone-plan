# Hoofdstuk 3 — Scheikunde: goedkope en dure berekeningen

> **In dit hoofdstuk leer je**
> – wat een kwantumchemische berekening eigenlijk uitrekent;
> – wat DFT is en waarom het goedkoop maar niet perfect is;
> – wat coupled cluster is en waarom het zo duur is;
> – hoe "lokale" coupled cluster de kosten drukt en welke prijs dat heeft;
> – wat "bevroren ruimtes" zijn en waarvoor ze bedacht zijn;
> – hoe de elf ankers van het project zijn berekend, en in welke basisset;
> – wat Δ, Δ₁, Δ₂ en ΔH precies zijn.

---

## §3.1 Wat er berekend wordt

Een molecuul is een verzameling atoomkernen met daaromheen elektronen. Voor een gegeven
stand van de kernen kun je de energie van de elektronen uitrekenen; doe je dat voor alle
standen in de buurt van het evenwicht, dan heb je het energielandschap waaruit de
Hessiaan (hoofdstuk 2) volgt.

Die energie exact uitrekenen is onmogelijk: de elektronen beïnvloeden elkaar allemaal
tegelijk. Alle rekenmethoden zijn benaderingen, en ze verschillen in hoe goed ze de
onderlinge beïnvloeding van elektronen ("correlatie") meenemen. Grofweg: hoe beter, hoe
duurder, en de kosten groeien als een hoge macht van de grootte van het molecuul.

## §3.2 DFT: de goedkope methode

**Dichtheidsfunctionaaltheorie** (DFT) rekent niet met alle elektronen afzonderlijk maar
met de **elektronendichtheid**: hoeveel elektron er gemiddeld op elke plek in de ruimte
zit. Dat is een enorme vereenvoudiging, en voor een groot deel van de scheikunde werkt
het verrassend goed. De prijs: DFT bevat een stuk "raden", de **functionaal**, waarvan
tientallen varianten bestaan. B3LYP is de bekendste in dit vakgebied en de goedkope invoer
van het project. ωB97X is de tweede functionaal, waarop het netwerk leert (de tussenstap,
hoofdstuk 5). Beide rekenen in de basisset 6-31G* (§3.7). Elke functionaal maakt eigen
systematische fouten.

Voor PAK's is één DFT-fout berucht: de **delokalisatiefout**. Elektronen in een
aromatische ring zijn over de hele ring "uitgesmeerd", en DFT smeert ze een beetje te veel
uit. Het gevolg zit precies in de C–C-strekfamilie die de sterrenkunde nodig heeft: de
berekende frequenties wijken daar systematisch af, en de afwijking groeit met de grootte
van het geconjugeerde systeem. Omdat de fout met het hele geconjugeerde systeem te maken
heeft, was de vraag of de correctie wel lokaal is. Dat is gemeten: van de coupled-clustercorrectie
op de B3LYP-Hessiaan van benzeen ligt 98 % in paren van coördinaten die dicht bij elkaar liggen,
tot twee bindingen uit elkaar (hoofdstuk 5, lokale coördinaten).

DFT geeft energie, gradiënt (de krachten op de atomen) en Hessiaan analytisch en snel: een
benzeen-Hessiaan in minuten op een laptop, coroneen in enkele uren. Analytisch betekent: met een
formule voor de afgeleide, niet door energieën of krachten bij verschoven standen te vergelijken
(eindige verschillen, hoofdstuk 4). Het project gebruikt voor de Hessianen van zijn corpus de
analytische route van het programma pyscf. Een Hessiaan uit eindige verschillen bleek te riskant:
die van benzeen met ωB97X zat tot 133 cm⁻¹ fout, door de ruis van het rekenrooster waarop DFT
zijn integralen uitrekent (besluit 50).

## §3.3 Coupled cluster: de dure methode

**Coupled cluster** (CC) is een methode die de correlatie tussen elektronen systematisch
opbouwt: eerst paren elektronen die samen "uitwijken" (singles en doubles, CCSD), dan een
correctie voor drietallen (de "(T)"). CCSD(T) staat bekend als de "gouden standaard" van
de kwantumchemie: voor kleine moleculen komen de resultaten binnen enkele cm⁻¹ overeen
met het lab, en er zit geen functionaal in die je moet kiezen.

De prijs is de schaling. De rekentijd van CCSD(T) groeit ongeveer met de **zevende macht**
van de grootte van het molecuul: twee keer zo groot is 128 keer zo duur. Benzeen gaat nog
op een laptop; naftaleen wordt lastig; pyreen is er niet meer mee te doen zonder een
groot rekencluster. Het geheugen groeit ook explosief: een tussenresultaat van benzeen in
een goede basisset zit al tegen de 28 GB.

De ankers van het project zijn toch volledige (niet-lokale) CCSD(T)-Hessianen. Ze zijn met pyscf
berekend uit analytische CCSD(T)-gradiënten: één in de evenwichtsstand en één bij elk van 2 × 3N
verschoven standen, waarbij elk atoom 0,005 bohr (een bohr is ongeveer 0,53 ångström) heen en terug
gaat langs x, y en z. De Hessiaan volgt dan uit eindige verschillen van die gradiënten (hoofdstuk 4).
Zo zijn elf ankers berekend, van benzeen (12 atomen) tot antraceen (24 atomen); de grootste vroegen
dagen rekentijd op gehuurde servers. Elk anker krijgt twee tweede routes die iets anders controleren
(besluit 61). De vaste is de energieroute: de gradiënt wordt vergeleken met verschillen van de
opgeslagen energieën bij dezelfde verschoven standen.

## §3.4 Lokale coupled cluster: dezelfde kwaliteit, minder rekenwerk

De redding is een waarneming: elektronencorrelatie is grotendeels **lokaal**. Twee
elektronen aan tegenovergestelde kanten van een groot molecuul beïnvloeden elkaar
nauwelijks. **Lokale CC-methoden** (met namen als DLPNO-CCSD(T) en LNO-CCSD(T)) verdelen
de elektronen in gelokaliseerde groepjes, rekenen per groepje alleen de correlatie met
de buren uit, en gooien de verwaarloosbare rest weg. Daardoor groeit de rekentijd niet meer
met de zevende macht maar bijna lineair met de grootte.

De prijs zit in het "weggooien". Voor elk groepje elektronen kiest het programma een
beperkte verzameling **virtuele orbitalen** (de "ruimte" waarin de elektronen mogen
uitwijken) en houdt de rest buiten beschouwing. Welke orbitalen precies meedoen, hangt af
van drempelwaarden (in het plan: de presets TightPNO en NormalPNO). Die keuze is discreet:
een orbitaal doet mee of niet. In het project is lokale CC de route voor ankers boven ongeveer
26 atomen (besluit 60); de elf ankers zijn klein genoeg voor de volledige methode.

## §3.5 Waarom dat een probleem is voor trillingen, en wat "bevroren ruimtes" oplossen

Om een Hessiaan te bepalen moet je de energie vergelijken bij *iets verschillende*
atoomstanden. Maar als het programma bij elke stand opnieuw kiest welke orbitalen meedoen,
kan die keuze bij een kleine verplaatsing net omslaan: een orbitaal valt af of komt erbij.
De energie maakt dan een sprongetje van de orde van een miljoenste hartree (1 µE_h), en dat
sprongetje is, omgerekend, groter dan het effect dat je wilt meten. De energie als functie
van de atoomstanden is dan **niet glad**, en een tweede afgeleide van een niet-gladde
functie is ruis.

De oplossing van plan 05 heet **bevroren ruimtes**: kies de orbitaalruimtes één keer, in de
evenwichtsstand, en houd ze vast bij alle verplaatste standen. Preciezer: sla de
gekozen orbitalen op als vectoren, en breng ze bij een verplaatste stand over door
**projectie** (hoofdstuk 4): zoek in de nieuwe ruimte de vectoren die het dichtst bij de
opgeslagen vectoren liggen en maak ze weer netjes onderling loodrecht (Löwdin-
orthonormalisatie). Dat gebeurt voor beide helften: de bezette orbitalen én de virtuele
ruimtes per groepje. Er wordt bij een verplaatste stand *niets* opnieuw gekozen of
"toegewezen", want elke discrete keuze is een mogelijke sprong.

> **Definitie 3.1 — Bevroren ruimte**
> De verzameling orbitaalvectoren die in de evenwichtsstand is bepaald en bij elke
> verplaatste stand door projectie en orthonormalisatie wordt overgebracht, zonder nieuwe
> lokalisatie of toewijzing. De correlatie-energie wordt in die overgebrachte ruimte
> uitgerekend. Het plan onderscheidt drie "armen": **A** = alles bevroren; **B** = bezette
> orbitalen overgebracht, virtuele ruimtes opnieuw opgebouwd; **C** = alles vers.

Of dit werkt was een meting, geen aanname. **Probe M1** controleerde of de gekozen software
dit kan (orbitalen opslaan, overbrengen, herladen) en of de energie langs een paar benzeenmodes
glad verloopt. Het gekozen pakket (pyscf-forge) accepteerde de bezette orbitalen wel als invoer,
maar bouwde de virtuele ruimtes bij elke aanroep opnieuw op; arm A vroeg dus een kleine aanpassing
van de code. Met die aanpassing slaagde M1: de ruimtes laten zich opslaan, overbrengen en herladen,
en de rondgang van stap 0 klopt tot 0,0002 µE_h.

Bevriezen heeft ook een nadeel: de bevroren ruimte is bij een verplaatste stand niet meer
de optimale ruimte. Dat geeft een systematische fout, de **bevriezingsbias**. Het ontwerp
meet die op benzeen door de bevroren berekening te vergelijken met een volledige (niet-lokale)
CCSD(T)-berekening, de enige referentie die zelf niet van het bevriezen afhangt: de "biaslijn".
De elf ankers zijn met de volledige methode berekend en hebben dus geen bevriezingsbias.

## §3.6 Δ, Δ₁, Δ₂ en ΔH

Nu kunnen de symbolen van het plan precies worden gedefinieerd. Neem de DFT-evenwichtsstand
als uitgangspunt en schrijf het verschil tussen de CC-energie en de DFT-energie als
machtreeks in de uitwijking:

ΔE(q) = Δ₁·q + ½ qᵀ Δ₂ q + …

- **Δ₁** is de eerste afgeleide: het verschil in *kracht* op de atomen in de DFT-stand. Het is
  niet nul, want het CC-evenwicht ligt op een iets andere plek dan het DFT-evenwicht
  (bindingslengtes verschillen een duizendste ångström). Δ₁ is per binding een paar keer
  zo groot als het Δ₂-signaal. Een paar metingen bij +p en −p streept Δ₁ weg (hoofdstuk 4,
  §4.2); de geometrieterm hieronder gebruikt Δ₁ juist.
- **Δ₂** is de tweede afgeleide: de correctie op de Hessiaan. Dit is de grootheid waar het
  project om draait. In het gebouwde product heet ze **ΔH**, en het netwerk van module 05
  voorspelt haar. Het netwerk leert op paren van twee DFT-methoden, ΔH = H(ωB97X) − H(B3LYP);
  de CCSD(T)-ankers bepalen wat "goed" is (besluit 60, hoofdstuk 5).
- Δ₃ en Δ₄ (kubisch en kwartisch) worden niet beloofd; zie hoofdstuk 2.

Een subtiel punt: omdat Δ₂ in de DFT-stand wordt gemeten en niet in het eigen minimum van het
gecorrigeerde landschap, hoort er een eerste-orde-correctie bij, de **geometrieterm**
(besluit 48): Δω_i = ½ Σ_k φ_iik ΔQ_k. Daarin is φ_iik een kubische krachtconstante van DFT
(hoofdstuk 2) en ΔQ_k de verschuiving van het minimum langs mode k. Er wordt geen atoom
verplaatst. De term is op 18 moleculen nagemeten tegen het eigen minimum van ωB97X: de frequenties
verschuiven daar 10,99 cm⁻¹ (rms), en na de term blijft 2,41 cm⁻¹ over. De pijplijn past de term
nog niet toe; hij hoort bij de anharmonische stap die in aanbouw is.

## §3.7 Basissets: hoe fijn je rekent

Elke berekening gebruikt een **basisset**: de verzameling wiskundige functies waaruit de
orbitalen worden opgebouwd. Meer functies is nauwkeuriger en duurder. Het project rekent in drie
basissets. De DFT-niveaus (B3LYP en ωB97X) rekenen in **6-31G***, een kleine basis die het hele
corpus betaalbaar maakt. De ankers rekenen in **cc-pVDZ** ("double zeta") en **cc-pVTZ** ("triple
zeta"); cc-pVTZ is nauwkeuriger en veel duurder.

De kleine basis cc-pVDZ bleek per familie anders uit te pakken. Op het naftaleenanker (lokale CC
in cc-pVTZ, vijftien energieën langs drie trillingen) lag vooraf de vraag vast of cc-pVDZ met een
vaste bijtelling uit benzeen volstaat (probe M3). Het antwoord kwam per familie: **verlies** voor
C–H uit het vlak (de bijtelling wisselt zelfs van teken), **winst** voor de C–H-buiging in het vlak
(+1,2 tegen +1,0 cm⁻¹), en **tussenin** voor de C–C-strek (−1,9 tegen −6,0 cm⁻¹: goede richting, te
ver af). De volledige CCSD(T)-Hessianen lieten hetzelfde zien. In cc-pVDZ krijgen aromaten
trillingen uit het vlak met een imaginaire frequentie, dat wil zeggen een negatieve veerconstante:
antraceen −51 cm⁻¹, benzonitril −87 en −82 cm⁻¹. Dat is een artefact van de kleine basis, geen
eigenschap van het molecuul.

Daarom heeft elk anker de vorm CCSD(T)/cc-pVDZ plus een **basisstap**: het verschil
MP2/cc-pVTZ − MP2/cc-pVDZ. MP2 is een correlatiemethode die veel goedkoper is dan CCSD(T). De
aanname is dat de stap van de kleine naar de grote basis bij MP2 ongeveer even groot is als bij
CCSD(T). Die aanname is getoetst op benzeen, het enige anker dat volledig in CCSD(T)/cc-pVTZ is
berekend: het samengestelde anker wijkt daarvan 4,6 cm⁻¹ af (rms over alle trillingen, hoogstens
8,5 cm⁻¹). Ook cc-pVTZ is niet de eindstand: met SCF naar cc-pV5Z en de MP2-correlatie naar
cc-pVQZ verschuiven drie gemeten benzeenmodes nog +2,8 / −5,2 / −11,1 cm⁻¹.

De regel die alles bij elkaar houdt: **één vergelijking gebruikt één niveau.** Het netwerk leert
op paren in dezelfde basis (6-31G*), en een lezing tegen de ankers gebruikt ankers van één niveau;
het ankerregister weigert een lezing die niveaus mengt, tenzij dat uitdrukkelijk wordt gevraagd en
vastgelegd (besluit 62).

## In het kort

DFT is goedkoop en bijna goed, met een bekende systematische fout op aromatische
ringmodes; het project gebruikt analytische DFT-Hessianen. Coupled cluster CCSD(T) is de
gouden standaard maar schaalt met de zevende macht. De elf ankers van het project zijn
volledige CCSD(T)-Hessianen uit eindige verschillen van gradiënten, in cc-pVDZ plus een
MP2-basisstap naar cc-pVTZ. Lokale varianten maken CC bijna lineair door verre correlatie weg
te gooien; dat weggooien is een discrete keuze die de energie ruw kan maken, en bevroren ruimtes
lossen dat op (probe M1 slaagde). Δ₂, het verschil in Hessiaan, is de grootheid waar het om
draait; in het product heet ze ΔH en voorspelt een netwerk haar. Δ₁, het verschil in kracht,
valt uit de ±-metingen weg en levert de geometrieterm.

*Bron: [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§3 (bevroren ruimtes, armen A/B/C, Δ₁-term), [Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§3, [Relevant_Scientific_Papers.md](../GoalGathering/Relevant_Scientific_Papers.md) items 48–49 en 51; besluiten 48, 50 en 60–62 in de
[README](../README.md); [ANCHORS.md](../modules/ANCHORS.md); `probes/e8_cc_hessian_fd.py`; de lezingen van probe M3
(`probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md`, `probes/results_m1/M3_TZ_MODE31_READING_2026-09-24.md`);
`probes/results_m1/BASIS_LINE_scf_mp2.md`; de geometrieterm in `../TASKS.md` (taak 156).*
