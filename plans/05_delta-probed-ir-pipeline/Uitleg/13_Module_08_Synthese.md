# Hoofdstuk 13 — Module 08: de pijplijn als geheel

*Udacity-module "Industry-Integrated AI Systems Synthesis". In de rubriek Project 7.*

---

## 1. Wat is de vraag?

Zet alles in elkaar tot één werkend programma — molecuul erin, spectrum met foutbudget,
kostenrecord en certificaat eruit, óf een weigering die zegt welke poort blokkeerde — en
schrijf het paper dat de keuzes verantwoordt.

## 2. Wat eist de school?

Een industriegericht, geïntegreerd artefact dat methoden of onderdelen uit **minstens
drie** eerdere modules combineert, met een architectuurbeschrijving of -diagram,
datastroom, aannames en afwegingen, en grenzen van wat het systeem kan. Het moet **nieuw
werk** zijn, geen herinzending. Een evaluatie in realistische scenario's (doelen gehaald?
sterktes, beperkingen, mislukkingen, afwegingen). Een reflectief synthesepaper van
1500–2000 woorden met: industriecontext, integratie-rationale, systeemontwerp, ethiek,
evaluatie en reflectie, professionele relevantie, referenties (minstens twee bronnen,
waarvan één wetenschappelijk). Een presentatie van 15 minuten met verdediging (module 09).

## 3. Invoer — de datastructuur in detail

Module 08 traint niets nieuws; het **integreert**. De invoer is de uitvoer van de anderen:

| Uit module | Object | Rol in de pijplijn |
|---|---|---|
| 02 | O8 opponent-atlas | lijn A in elke beat-vergelijking |
| 03 | O9 scorebord met u_band en matrixtolerantie | de waarheid en de beslisbaarheid per familie |
| 04 | gekalibreerde opponentkolom; onzekerheidslaag | de tweede tegenstander; het foutbudget op R4–R6 |
| 07 | de campagne-officier | draait de campagnes, print records, schrijft certificaten |
| 05 | de geleerde prior (als licentie verdiend) | het P3-experiment op R0–R3; dragend op R4–R6 |
| 06 | voorgestelde patronen | het patroonefficiëntie-experiment |
| infrastructuur | probe M1, de recovery-solver, de batchrunner, het deck | geen module-ML; het rekenhart |

Vier modules (02, 03, 04, 07) zijn op het beloofde pad; 05 en 06 zijn bonusrapporten,
precies zo gelabeld. Dat zijn er dus vier in de zin van de rubriek, met twee extra.

Daarnaast de **bevroren documenten** zelf: de Ladder (de regels), de pilotnotitie (de
getallen), de dry-run-uitkomsten (c, K_cap, w), en de tegenstanders met versienummer.

## 4. Bewerking — de stroom per molecuul

Voor een gegeven identifier (zie het schema in hoofdstuk 6, §6.4):

1. Molecuulrecord (O1) en rung bepalen; DFT-geometrie, Hessiaan, modes, families,
   anharmonische DFT-constanten voor de resonantie-gesloten set plus de totaalsymmetrische
   modes (O2).
2. Deck opstellen (O3): patronen, prior (structureel; of geleerd waar de licentie het
   toestaat), q_s, hold-out, paarlijst; hash vastzetten. Voorstellen van module 06 alleen
   vóór de hash.
3. De officier dient de batch in; de batchrunner rekent per paar CC (bevroren ruimtes) en
   DFT; antwoordrecords (O5).
4. Recovery: Δ₂, ρ-curve, K, K_off, c₀, Δ₁ (O6). De officier controleert de stopregel en
   de plafonds.
5. Licenties: Q6 op de grootteklasse, Q7 op R0–R1, Q8 op R1–R3; fragmentlicentie op
   R4–R6.
6. Spectrum: DFT-harmonisch + Δ₂ + de eerste-orde-geometrieterm; anharmonisch via GVPT2
   met de resonantieregels; CH-strek eventueel niet gescoord.
7. Score: per familie tegen atlas en gekalibreerde kolom, alleen waar het scorebord
   beslisbaar zegt; de Δ = 0-nulrij moet verliezen waar "beat" wordt geclaimd.
8. De officier print het kostenrecord (O7) en schrijft het certificaat (O13) of de
   weigering.

De runs die het plan belooft: R0–R1 onvoorwaardelijk (verwacht) op kamertemperatuurbronnen;
R2–R3 per familie onder de beslisbaarheidsregel en de Q6-ruispoort per mode; R6 in
fragmenten onder de vierdelige licentie, of de gemeten weigering. Emissie-nabewerking
(hoe een hete PAK in de ruimte straalt) via het gepubliceerde cascademodel, gelabeld als
overgenomen.

## 5. Uitvoer — de datastructuur in detail

**Het artefact: een kleine opdrachtregel-tool of dienst.**

- Invoer: `identifier` (CAS of PAHdb-uid), optioneel `rung`.
- Uitvoer bij succes: het certificaat (O13) — spectrum als lijst van (positie, familie,
  foutbudget), beat-uitslag per familie, kostenrecord(s), licentiestatus, hashes.
- Uitvoer bij weigering: `{rung, poort of plafond, verwijzing}`.

**Het paper.** Industrieframe zoals de Goal het stelt (de beheerder van een
spectrendatabank die een soort wil prijzen en scoren); de scheiding
nauwkeurigheid/bereik; de tabel van kostenrecords over de rungs, met de numerieke
grootte-zin als die verdiend is; verliezen en onbeslisbare families als zodanig gemeld; de
sporen naar de geïntegreerde modules expliciet.

**De evaluatie.** De R0–R3-vergelijkingen zijn de evaluatie in realistische scenario's; de
weigeringen en de fail-closed-zinnen van hoofdstuk 5 zijn de mislukkingsgevallen.

## 6. Waarom deze module?

Dit *is* het doel; alles ervoor bestaat hiervoor. Het onderscheid met een gewone
herinzending: de integratie zelf (deck, officier, licenties, certificaat) bestaat in geen
eerdere module, en de vergelijkingen op R0–R3 zijn nieuwe metingen.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **"Minstens drie" traceerbaar.** Het paper moet per geïntegreerde module zeggen wat ze
  bijdraagt en waar in de stroom (de tabel van §3 is het sjabloon). Controleer dat 05 en 06
  als bonus gelabeld staan en niet als dragend, behalve 05 op R4–R6 als de licentie is
  verdiend.
- **Nieuw werk.** Het artefact moet aantoonbaar meer zijn dan de som van de notebooks: de
  CLI, het certificaat, de weigeringen.
- **Woordenaantal en bronnen.** 1500–2000 woorden; minstens twee bronnen waarvan één
  wetenschappelijk — bij dit plan is dat geen probleem, de bibliografie telt zestig items.
- **Eerlijk verliezen.** De rubriek beloont een evaluatie met mislukkingen. Het plan heeft
  vooraf geschreven zinnen voor elke mislukking; controleer dat het paper ze gebruikt in
  plaats van verliezen te verzachten.
- **Geen kostenbijvoeglijknaamwoord in het paper.** Ook hier draait het tekstfilter van de
  officier.
- **Deadlines zijn administratief.** Een module mag een eerlijke fail-closed-toestand
  inleveren om zijn datum te halen; de wetenschap gaat daarna door. Dat staat zo in de
  mapping; controleer dat het paper die mogelijkheid benoemt als ze zich voordoet.
- **De R6-uitkomst.** "R6 niet bereikt, om deze gemeten reden" is een geldig
  module-08-resultaat. Controleer dat de weigering, als ze komt, in het paper staat met de
  getallen van de fragmentlicentie erbij.

## 8. In het kort

Module 08 bouwt de pijplijn als één programma dat de atlas, het scorebord, de
gekalibreerde tegenstander en de campagne-officier integreert (met de steunvoorspeller en
de patroonvoorsteller als gelabelde experimenten), draait de beloofde vergelijkingen op
R0–R3 en de fragmentroute op R6, en levert per molecuul een certificaat met spectrum,
foutbudget en kostenrecord, of een weigering die de blokkerende poort noemt. Het paper
verantwoordt de keuzes en meldt verliezen als verliezen.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §3 (Module 08) en §6,
[Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) (industrieframe, methode-skelet),
[Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§8–§9, [Rubrics/08](../../../Rubrics/08_Industry_Integrated_AI_Systems_Synthesis.md).*
