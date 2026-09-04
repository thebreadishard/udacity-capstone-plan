# Hoofdstuk 3 — Scheikunde: goedkope en dure berekeningen

> **In dit hoofdstuk leer je**
> – wat een kwantumchemische berekening eigenlijk uitrekent;
> – wat DFT is en waarom het goedkoop maar niet perfect is;
> – wat coupled cluster is en waarom het zo duur is;
> – hoe "lokale" coupled cluster de kosten drukt en welke prijs dat heeft;
> – wat "bevroren ruimtes" zijn en waarom het plan ze nodig heeft;
> – wat Δ, Δ₁ en Δ₂ precies zijn.

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
tientallen varianten bestaan (B3LYP is de bekendste in dit vakgebied; ωB97x en BHLYP
komen in dit plan ook voor). Elke functionaal maakt eigen systematische fouten.

Voor PAK's is één DFT-fout berucht: de **delokalisatiefout**. Elektronen in een
aromatische ring zijn over de hele ring "uitgesmeerd", en DFT smeert ze een beetje te veel
uit. Het gevolg zit precies in de C–C-strekfamilie die de sterrenkunde nodig heeft: de
berekende frequenties wijken daar systematisch af, en de afwijking groeit met de grootte
van het geconjugeerde systeem. Dat is de reden dat de correctie Δ het meest zal moeten
doen op de ringmodes, en dat het plan een aparte controle heeft op de vraag of de correctie
op de C–C-modes wel lokaal is (hoofdstuk 5).

DFT geeft energie, gradiënt (de krachten op de atomen) en Hessiaan analytisch en snel: een
benzeen-Hessiaan in een paar minuten op een laptop, coroneen in een uur of wat.

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
een orbitaal doet mee of niet.

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

Of dit werkt is een meting, geen aanname. Het eerste dat het plan doet, **probe M1**, is
controleren of de gekozen software dit überhaupt kan (orbitalen opslaan, overbrengen,
herladen) en of de energie langs een paar benzeenmodes glad verloopt. Mislukt M1, dan stopt
het plan bij zijn eerste stopvoorwaarde en zegt precies welk programma-onderdeel ontbrak.
De reviewer die de software opende, vond dat het gekozen pakket (pyscf-forge) de bezette
orbitalen wel als invoer accepteert maar de virtuele ruimtes bij elke aanroep opnieuw
opbouwt; arm A vraagt dus een kleine aanpassing van de code, die met een vaste versie
wordt vastgelegd.

Bevriezen heeft ook een nadeel: de bevroren ruimte is bij een verplaatste stand niet meer
de optimale ruimte. Dat geeft een systematische fout, de **bevriezingsbias**. Het plan meet
die op benzeen door de bevroren berekening te vergelijken met een volledige (niet-lokale)
CCSD(T)-berekening, de enige referentie die zelf niet van het bevriezen afhangt. Dat is de
"biaslijn" van hoofdstuk 5.

## §3.6 Δ, Δ₁ en Δ₂

Nu kunnen de symbolen van het plan precies worden gedefinieerd. Neem de DFT-evenwichtsstand
als uitgangspunt en schrijf het verschil tussen de CC-energie en de DFT-energie als
machtreeks in de uitwijking:

ΔE(q) = Δ₁·q + ½ qᵀ Δ₂ q + …

- **Δ₁** is de eerste afgeleide: het verschil in *kracht* op de atomen in de DFT-stand. Het is
  niet nul, want het CC-evenwicht ligt op een iets andere plek dan het DFT-evenwicht
  (bindingslengtes verschillen een duizendste ångström). Δ₁ is per binding een paar keer
  zo groot als het Δ₂-signaal; hoofdstuk 5 legt uit hoe het plan Δ₁ uit de metingen
  wegstreept én toch gebruikt.
- **Δ₂** is de tweede afgeleide: de correctie op de Hessiaan. Dit is het enige dat het plan
  belooft.
- Δ₃ en Δ₄ (kubisch en kwartisch) worden niet beloofd; zie hoofdstuk 2.

Een subtiel punt dat de laatste review naar voren bracht: omdat Δ₂ in de DFT-stand wordt
gemeten en niet in het eigen minimum van het gecorrigeerde landschap, hoort er een kleine
eerste-orde-correctie bij (de kubische DFT-constanten maal de verschuiving van het
minimum). Het plan past die toe en print haar per band; er wordt geen atoom verplaatst.

## §3.7 Basissets: hoe fijn je rekent

Elke berekening gebruikt een **basisset**: de verzameling wiskundige functies waaruit de
orbitalen worden opgebouwd. Meer functies is nauwkeuriger en duurder. Het plan legt per
rung één basisset vast en gebruikt op de kleine rungs cc-pVTZ ("triple zeta"); als een
volledige CCSD(T)-berekening van benzeen daarin niet op de laptop past, valt het terug op
het kleinere cc-pVDZ, met een label dat de biasmeting dan een ondergrens is. De regel die
alles bij elkaar houdt: **beide kanten van elke vergelijking in dezelfde basisset.**

## In het kort

DFT is goedkoop en bijna goed, met een bekende systematische fout op aromatische
ringmodes. Coupled cluster CCSD(T) is de gouden standaard maar schaalt met de zevende
macht; lokale varianten maken het bijna lineair door verre elektronencorrelatie weg te
gooien. Dat weggooien is een discrete keuze die bij kleine verplaatsingen kan omslaan en de
energie ruw maakt; plan 05 bevriest daarom de gekozen orbitaalruimtes en brengt ze door
projectie over, en meet eerst (probe M1) of dat werkt en (biaslijn) wat het kost. Δ₂, het
verschil in Hessiaan tussen CC en DFT, is de enige beloofde grootheid; Δ₁, het verschil in
kracht, wordt uit de metingen weggestreept maar apart gemeten en als kleine correctie
toegepast.

*Bron: [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§3 (bevroren ruimtes, armen A/B/C, anchor basis, Δ₁-term), [Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§3, [Relevant_Scientific_Papers.md](../GoalGathering/Relevant_Scientific_Papers.md) items 48–49 en 51.*
