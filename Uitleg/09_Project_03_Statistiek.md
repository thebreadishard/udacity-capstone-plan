# Hoofdstuk 9 — Project 03: statistische toetsing van de rekenmachine

> **In dit hoofdstuk leer je**
> – wat fase 0a is en waarom die zonder kwantumchemie kan;
> – hoe je een proefopzet maakt met twee factoren tegelijk;
> – hoe je een hypothesetoets doet op een machine die geen toeval kent;
> – waarom in dit verslag het woord "geëlimineerd" verboden is.

**Categorie in het plan:** (A) natuurlijke aansluiting + (C) controleproject.
**Positie in de keten:** direct na fase 0a; hangt níét af van de kwantumchemie.

---

## §9.1 Wat is de vraag?

De schoolopdracht: beschrijvende statistiek plus minstens één hypothesetoets op
een eigen dataset, met minstens drie grafieken.

De onderzoeksvraag eronder:

> De rekenmachine uit hoofdstuk 5 maakt onvermijdelijk kunstmatige fouten, vooral
> het eierdooseffect (§5.4). Er is een knop om die fouten te onderdrukken: de
> uitsmeerbreedte $\sigma$ ten opzichte van de roosterafstand $\Delta x$.
> **Werkt die knop echt, en hoe hard?**

Merk op dat het antwoord niet vanzelf spreekt. Uitsmeren maakt de dichtheid
gladder — dat zou moeten helpen. Maar te veel uitsmeren maakt het molecuul wazig
en vervalst de natuurkunde. Ergens ligt een optimum, en dat wordt gemeten.

## §9.2 Fase 0a: de motor zonder brandstof

Voordat er data is, moet er een machine zijn. Fase 0a bouwt en test die machine.

Het slimme van deze fase is wat er **niet** in zit: er komt geen enkele
kwantumchemische berekening aan te pas. In plaats van een echte, dure
elektronendichtheid gebruikt fase 0a analytische testdichtheden — bijvoorbeeld
de bevroren atoomdichtheden uit §5.3, die immers gewoon uit Gauss-functies
bestaan.

Waarom dat belangrijk is, staat in
[Capstone_Mapping §8.4](../GoalGathering/Capstone_Mapping.md): het programma PySCF
draait niet onder Windows, dus daarvoor moet eerst Linux of WSL2 worden opgezet.
Door fase 0 in tweeën te splitsen (0a zonder kwantumchemie, 0b mét), kan het
tweede ingeleverde project doorgaan terwijl die omgeving nog wordt ingericht.
Dat is projectplanning, en het is bewust zo ontworpen.

## §9.3 Invoer

De invoer is de proefopzet zelf: een lijst van omstandigheden waaronder de motor
wordt doorgemeten.

> **Definitie 9.1 — De twee roosterknoppen**
> - $\Delta x$ is de ribbe van een voxel (§5.1). Kleiner = fijner = duurder.
> - $\sigma$ is de breedte waarmee een kern wordt uitgesmeerd (§5.5). Groter =
>   gladder = waziger.
> - De verhouding $\sigma/\Delta x$ zegt hoeveel voxels breed die uitsmering is.
>   Die verhouding, niet $\sigma$ zelf, is de zinvolle grootheid.

De opzet is **volledig factorieel** (§4.8):

| Factor | Waarden | Aantal |
|---|---|---|
| $\sigma/\Delta x$ | 1,0 · 1,5 · 2,0 · 2,5 · 3,0 | 5 |
| $\Delta x$ (Å) | 0,40 · 0,30 · 0,25 · 0,20 · 0,15 | 5 |
| Molecuul | $\mathrm{H_2O}$ · $\mathrm{C_6H_6}$ | 2 |

> **Voorbeeld 9.1**
> Bereken het aantal cellen en het aantal rijen bij 16 herhalingen per cel.
> Controleer of dat aan de schooleis van minstens 500 rijen voldoet.
>
> *Uitwerking.*
> $$5 \times 5 \times 2 = 50 \text{ cellen}$$
> $$50 \times 16 = 800 \text{ rijen}.$$
> Bij de ondergrens van 10 herhalingen: $50 \times 10 = 500$ rijen — precies de
> schooleis. De opzet heeft dus 60% speling.
>
> Deze rekensom is niet met de hand gemaakt maar uitgevoerd door
> [`probes/issue14_sweep_design.py`](../probes/issue14_sweep_design.py). Dat is geen
> overdreven voorzichtigheid: een eerdere versie van het plan beweerde 800 rijen
> terwijl de opzet er in werkelijkheid 1300 opleverde. Het getal dat als "eerlijk,
> niet opgeblazen" werd gepresenteerd, klopte simpelweg niet.

## §9.4 Het ruismodel: de belangrijkste vondst

Hier zit het eigenlijke intellectuele werk van dit project.

**Het probleem.** Een hypothesetoets vraagt om spreiding. Maar de rekenmachine is
volstrekt deterministisch: dezelfde invoer geeft altijd bit voor bit dezelfde
uitvoer. Zestien keer dezelfde som maken levert zestien identieke rijen op. Een
$t$-toets daarop is niet zomaar zwak — het is een **categoriefout**, een toets die
niets kan betekenen.

**De oplossing.** Laat de toevalligheid niet in de meting zitten maar in de
**omstandigheden**. Elke rij is een onafhankelijke trekking van:

| Kolom | Wat er wordt geloot |
|---|---|
| `pose_rotation_deg` | Onder welke hoek het molecuul ten opzichte van het rooster ligt |
| `subvoxel_offset_frac` | Waar binnen een roostercel het molecuul precies staat |
| `geometry_temperature_k` | Hoe sterk het molecuul thermisch is vervormd |

Dat is een **fysisch** ruismodel, geen kunstgreep. Precies dit gebeurt namelijk in
een echte simulatie ook: een bewegend molecuul komt in willekeurige standen en op
willekeurige plaatsen ten opzichte van het rooster terecht. En het spiegelt de
werkwijze in een echt laboratorium: het meetinstrument is nauwkeurig, maar het
monster ligt elke keer net iets anders.

De verplichte zin in het verslag verwoordt dat zo
([Capstone_Mapping §5.5](../GoalGathering/Capstone_Mapping.md)):

> Deze tabel is de gemeten uitvoer van een deterministische klassieke
> natuurkundemotor, geen door AI gegenereerde dataset. De toevalligheid zit in de
> **experimentele omstandigheden** — de stand en de vorm van het molecuul worden
> geloot, net zoals de plaatsing van een monster in een instrument varieert —
> terwijl de gemeten respons deterministische natuurkunde is. De lotingsgetallen
> zijn gepubliceerd, dus elke rij is reproduceerbaar.

## §9.5 De uitvoer: de sweep-tabel

Eén CSV-bestand, 800 rijen, 15 kolommen.

| Kolom | Rol | Betekenis |
|---|---|---|
| `trial_id` | identificatie | Volgnummer van de meting |
| `molecule` | **categorische factor** | `H2O` of `C6H6` |
| `sigma_over_dx` | **categorische factor** | 1,0 / 1,5 / 2,0 / 2,5 / 3,0 |
| `delta_x_angstrom` | numerieke factor | De roosterafstand |
| `seed` | reproduceerbaarheid | Startgetal van de loting |
| `pose_rotation_deg` | ruismodel | De gelote oriëntatie |
| `subvoxel_offset_frac` | ruismodel | De gelote plaats binnen de cel |
| `geometry_temperature_k` | ruismodel | De gelote thermische vervorming |
| `box_pad_factor` | covariabele | Hoeveel lege ruimte er om het molecuul zit |
| `egg_box_amplitude_hartree` | respons | Het eierdooseffect in energie-eenheden |
| `egg_box_force_mev_per_ang` | **hoofdrespons** | Hetzelfde, in krachteenheden |
| `net_force_mev_per_ang` | respons | $\lVert\sum_A\mathbf F_A\rVert$: de translatiefout |
| `torque_force_equiv_mev_per_ang` | respons | De rotatiefout, $\tau_{\max}/r_{\max}$ |
| `charge_integral_error` | respons | Afwijking in het elektronenaantal (§3.1) |
| `wall_s` | kosten | Rekentijd in seconden |

Twee dingen zijn hier bewust gedaan.

**De hoofdrespons staat in krachteenheden.** Dat is de les uit §5.4: een
energiefout is een krachtfout in vermomming, en pas na omrekening kun je hem
vergelijken met de eis die er werkelijk toe doet.

**De tabel draagt meer dan één antwoord.** Naast het eierdooseffect staan ook de
translatiefout, de rotatiefout en de ladingsfout in dezelfde rijen. Daardoor is
deze ene tabel tegelijk het huiswerk voor de school **en** het bewijsmateriaal
voor de toetsingseisen van fase 0a. Er is geen apart, alleen-voor-school-gemaakt
bestand.

> **Toelichting bij de rotatiekolom**
> Waarom staat er zowel een translatie- als een rotatiekolom? Omdat een voxelrooster
> een kubus is, en een kubus is niet in alle richtingen hetzelfde. Draai je een
> molecuul, dan verandert de berekende energie een beetje — er ontstaat een
> kunstmatig **draaimoment**.
>
> Het plan merkt op dat de translatiefout $\lVert\sum_A\mathbf F_A\rVert$ eigenlijk
> hetzelfde is als het eierdooseffect (het is immers min de afgeleide naar een
> starre verschuiving), en dus geen aparte eis nodig heeft. De rotatiefout is dat
> níét, en krijgt daarom een eigen meting. Dat is belangrijk voor hoofdstuk 15,
> want het concurrerende model uit werkstroom G1 is per constructie exact
> rotatie-invariant. Zonder deze kolom zou je later niet kunnen onderscheiden
> tussen "de veldvoorstelling is slechter" en "onze discretisatie brak een
> symmetrie die de tegenstander gratis krijgt".

## §9.6 De statistiek

> **Stappenplan 9.1 — De analyse**
>
> **Stap 1 — Beschrijven.** Bepaal per cel het gemiddelde en de standaarddeviatie
> van `egg_box_force_mev_per_ang`.
>
> **Stap 2 — Hypothesen formuleren.**
> - $H_0$: het gemiddelde eierdooseffect is onafhankelijk van $\sigma/\Delta x$.
> - $H_1$: er is wél een verband.
>
> **Stap 3 — Toetsen.** Voer een twee-weg-variantieanalyse uit met de factoren
> $\sigma/\Delta x$ en `molecule`, en toets ook op **interactie**: werkt de knop
> even goed voor water als voor benzeen?
>
> **Stap 4 — Visualiseren.** Bijvoorbeeld: eierdooskracht tegen $\sigma/\Delta x$
> (met foutbalken), eierdooskracht tegen $\Delta x$ op logaritmische schaal, en een
> boxplot per molecuul.
>
> **Stap 5 — Interpreteren**, in gewone taal, plus een paragraaf over de
> beperkingen.

De interactietoets in stap 3 is inhoudelijk de interessantste. Als het effect van
de knop bij benzeen anders is dan bij water, dan is het geen universele instelling
en moet er per molecuul gekozen worden — een resultaat met directe gevolgen voor
de rest van het project.

## §9.7 De verboden en de verplichte woorden

Uit [Distilled Plan §4](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md):

> **NOT claiming elimination of the egg-box effect, only its control.**

In het verslag mag dus staan dat het eierdooseffect *verminderd* of *beheerst* is,
en met welke factor. Er mag niet staan dat het *weg* is. Het is namelijk niet weg;
het is teruggebracht tot onder een plafond, en dat plafond wordt genoemd:
0,1 meV/Å.

Verder gelden de gebruikelijke publicatie-eisen: de CSV krijgt een DOI vóór het
notitieboek beweert waar de data vandaan komt, en er ligt ook een kopie in de
inlevermap.

Het plan voegt er een waarschuwing aan toe die je serieus moet nemen: *"Do not
replace this with a UCI toy table."* Het zou verleidelijk zijn om voor dit
schoolproject snel een kant-en-klare oefendataset te pakken. Dan is de opdracht
gehaald, maar is de kwaliteitscontrole van fase 0a niet gedaan — en die is
verderop nodig.

## §9.8 Waarom deze stap?

**Rubriek.** Echte hypothesetoets, eigen dataset, meer dan 500 rijen, meer dan 6
kolommen, groeperingsvariabele aanwezig, publieke DOI.

**Wetenschap.** Dit is de kwaliteitscontrole die [Distilled Plan §8](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
sowieso eist, maar dan statistisch onderbouwd in plaats van met het oog
beoordeeld. Het verschil: "het lijkt beter te worden bij grotere $\sigma$" wordt
"het effect is significant met $p < 0{,}001$ en de grootte is X".

**Planning.** Doordat fase 0a geen kwantumchemie nodig heeft, staat het tweede
ingeleverde project niet in de wachtrij achter de zwaarste infrastructuur van het
hele plan. Dat was een expliciet gesignaleerd risico voor het diploma.

## In het kort

- **Invoer:** een volledig factoriële proefopzet, 5 × 5 × 2 = 50 cellen, 16 herhalingen per cel.
- **Bewerking:** de motor doormeten onder gelote omstandigheden (stand, plaats in de cel, thermische vervorming), daarna twee-weg-ANOVA.
- **Uitvoer:** een CSV van 800 rijen en 15 kolommen, plus een analyse-notitieboek en een verslag.
- Het ruismodel is fysisch: de omstandigheden worden geloot, de meting zelf is deterministisch.
- De hoofdrespons staat in krachteenheden, zodat hij vergelijkbaar is met de eindeis.
- Dezelfde tabel dient als schoolopdracht én als bewijsmateriaal voor de toetsingseisen van fase 0a.
- Verboden woord: "geëlimineerd". Toegestaan: "beheerst tot onder 0,1 meV/Å".
