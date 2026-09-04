# Hoofdstuk 11 — Module 06: de generatieve patroonvoorsteller

*Udacity-module "Generative AI Applications". In de rubriek Project 5.*

---

## 1. Wat is de vraag?

Kan een generatief model betere meetpatronen voorstellen dan het vaste recept, zodat er
minder dure metingen nodig zijn om Δ₂ terug te vinden — zonder dat er één extra
coupled-clusterberekening voor nodig is?

## 2. Wat eist de school?

Een klein generatief systeem: een taak en dataset kiezen; een **GAN, VAE of
Transformer-generator** implementeren en trainen (diffusie hoeft niet); voorbeelden
genereren; de kwaliteit **kwalitatief** beoordelen met sterke en zwakke gevallen uit eigen
uitvoer; een rapport met minstens één ethische overweging die aan *deze* data en *dit*
model is gebonden. De dataset moet openbaar of duidelijk gedocumenteerd zijn, niet
synthetisch of AI-gegenereerd als dataset, en niet hergebruikt uit een eerdere module.
Gegenereerde uitvoer telt nooit als dataset.

## 3. Invoer — de datastructuur in detail

**Het patroon-antwoordcorpus, object O12.** De antwoordrecords (O5) van de
DFT-tegen-DFT-dry-runs op de QM9-deelverzameling, per molecuul aangevuld met zijn
modestructuur:

| Veld | Type | Betekenis |
|---|---|---|
| molecuul | tekst | sleutel |
| modes, frequenties | tensor M × 3N, lijst | uit O2 |
| patroon p | vector 3N | het meervoudige of tweemodes-patroon |
| R_s | getal | het antwoord (DFT-tegen-DFT) |
| ρ-winst | getal | hoeveel de achtergehouden fout daalde toen dit patroon werd toegevoegd |
| splits-hash | tekst | **nieuw** zaadje, anders dan dat van module 05 |

Het verschil met het corpus van module 05: dat bevat *Hessianen en steunlabels per
molecuul*; dit bevat *antwoorden per patroon*. Andere grootheid, andere hash. En de
PAK-dry-run-tensoren, die de testset van module 05 zijn, zitten **niet** in deze
trainingsdata.

**Wat het model leert genereren.** Een tweemodes-verplaatsingspatroon, geconditioneerd op de
modestructuur van het molecuul: gegeven "dit molecuul heeft deze M modes met deze
frequenties en samenstellingen", stel een patroon p voor. Bevroren keuze: een **VAE**
(variationele autoencoder) over de ruimte van patronen.

**Publicatie vooraf.** Eigen Zenodo-uitgave vóór de module begint.

## 4. Bewerking

1. Corpus bouwen uit de dry-run-records; splitsen met nieuw zaadje; publiceren.
2. VAE trainen: encoder van patroon plus molecuulconditie naar een latente code, decoder
   terug naar een patroon; verliescurves loggen.
3. Genereren: voor een molecuul kandidaatpatronen trekken uit de latente ruimte.
4. **Acquisitieregel** (vooraf vastgelegd): elk kandidaatpatroon krijgt een score gelijk
   aan de verwachte daling van ρ onder de structurele prior; de beste kandidaten worden
   voorgesteld.
5. **Weergave en kwalitatieve beoordeling** (rubriek-taak 4). Een patroon is geen plaatje en
   geen zin; het notebook tekent gegenereerde patronen als verplaatsingspijlen op het
   molecuulskelet, naast patronen uit het vaste deck, en beoordeelt ze op drie vooraf
   genoemde criteria: symmetrie-consistentie met de puntgroep van het molecuul; lokaliteit
   (de bewogen atomen liggen binnen r_max van elkaar); geen redundantie met patronen die al
   in het deck zitten. Mislukte gevallen worden getoond: een patroon dat het deck dupliceert,
   of atomen beweegt zonder gedeelde familiemode.
6. **De vooraf vastgelegde succesmaat**: op het dry-run-corpus, K_off om ρ* te halen mét
   VAE-voorstellen in het deck tegen het vaste deck alleen, al het andere gelijk. Wint de VAE
   niet, dan is dát de gepubliceerde uitkomst.

## 5. Uitvoer — de datastructuur in detail

- **Voorgestelde patronen** voor een rung: een lijst van vectoren p met hun
  acquisitiescore. Die gaan het deck (O3) in als gewone patronen — **vóór de hash**. Daarna
  zijn ze niet meer te onderscheiden van andere patronen en worden ze gewoon met een echte
  berekening geëvalueerd.
- **Het getrainde model** met versiehash.
- **De efficiëntievergelijking**: K_off met en zonder voorstellen, op het corpus.
- **Figuren**: de pijldiagrammen naast deck-patronen, met de drie criteria en de mislukte
  gevallen.
- Notebook, `requirements.txt`, rapport met ethiekparagraaf.

Wat er uitdrukkelijk **niet** uitkomt: data. Gegenereerde patronen zijn modeluitvoer en
worden nooit als dataset uitgegeven; alleen hun berekende antwoorden zijn data.

## 6. Waarom deze module?

K_off is het schaarse getal van het hele plan, en het vaste deck (O1NumHess-achtige
volledigheidspatronen plus de door de dry run aangewezen tweemodes-patronen) is de
beloofde manier om het uit te geven. Een voorsteller die slimmere patronen aandraagt, is de
enige hefboom op K_off die geen enkele CC-energie kost. Valt module 06 weg, dan stopt de
patroonefficiëntie bij het vaste deck; de beloofde rungs draaien nog steeds. Dat is een
zwakkere vorm van "dragend" dan bij module 02–04 en 07–08, en het plan zegt dat hardop.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Het lek dat de hash voorkomt.** Een voorgesteld patroon mag nooit in een deck komen
  nadat er voor die rung één antwoord bekend is. Dat zou pre-registratie breken. De
  hashregel maakt het onmogelijk; de campagne-officier controleert de hash. Dit is ook de
  eerste ethische overweging van het rapport, gebonden aan dit systeem.
- **Een voorstel is geen meting.** Het model zegt "dit patroon is waarschijnlijk nuttig";
  de waarde van het antwoord komt altijd uit een echte berekening. Controleer dat nergens
  een gegenereerd getal als meting wordt gebruikt.
- **Distinctheid tegenover module 05.** Andere grootheid (antwoorden versus Hessianen),
  nieuwe splits-hash, PAK-tensoren uitgesloten. Controleer alle drie in de
  provenance-paragraaf.
- **De weergave-eis.** De rubriek verwacht "voorbeelden tonen"; voor patronen moet dat de
  pijldiagram-oplossing zijn met de drie criteria. Controleer dat de mislukte gevallen er
  echt staan.
- **De energiekosten van het voorstellen** tegenover de bespaarde rekenuren: een eerlijke
  ethische afweging die het rapport moet maken.
- **Volgorde.** Module 06 wacht op de dry-run-corpusuitgave; op beloofde rungs mag het model
  pas patronen aandragen nadat het op het corpus is beoordeeld.

## 8. In het kort

Module 06 traint een VAE die, gegeven de modestructuur van een molecuul,
verplaatsingspatronen voorstelt; een vaste acquisitieregel kiest de beste, die vóór de
hash in het deck gaan en daarna als gewone patronen worden berekend. De succesmaat is
K_off met tegen zonder voorstellen, op een eigen corpus van dry-run-antwoorden; de
beoordeling van de uitvoer gebeurt met pijldiagrammen en drie criteria. Wint het model
niet, dan is dat het resultaat.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §3 (Module 06) en §4,
[Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§3 (patronen) en §6, [Rubrics/06](../../../Rubrics/06_Generative_AI_Applications.md).*
