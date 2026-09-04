# Hoofdstuk 6 — Datastructuren en de pijplijn

> **In dit hoofdstuk leer je**
> – de vijf soorten data die in dit project voorkomen (getal, lijst, record, tabel, tensor)
>   en in welke bestandsvormen ze worden opgeslagen;
> – de veertien objecten waaruit de pijplijn is opgebouwd, elk met zijn velden;
> – welk object door welke module wordt gemaakt en gelezen;
> – hoe de data van "molecuulnaam erin" naar "spectrum eruit" stroomt, in één schema;
> – drie regels over data die overal terugkomen: hash, verzegeling, en "geprint of niet bestaand".

Dit hoofdstuk is het naslagwerk voor deel B. Elk modulehoofdstuk verwijst bij "Invoer" en
"Uitvoer" naar de objecten die hier zijn gedefinieerd.

---

## §6.1 Vijf soorten data

In de informatica op school ken je de basistypen (getal, tekst, waar/onwaar) en de
samengestelde typen (lijst, dictionary, object). Dit project gebruikt er vijf, met de
namen die in de documenten voorkomen:

| Soort | Wat het is | Voorbeeld in dit project | Bestandsvorm |
|---|---|---|---|
| **Getal** | één waarde met eenheid | een energie in hartree; een bandpositie in cm⁻¹ | in een record of tabel |
| **Lijst / vector** | geordende rij getallen | een patroon p (3N getallen); een bandlijst | JSON-array; kolom van een tabel |
| **Record** | een verzameling benoemde velden (in Python een dictionary) | één kostenrecord; één certificaat | JSON-bestand |
| **Tabel** | rijen met dezelfde kolommen (in pandas een DataFrame) | de opponent-atlas; het scorebord | CSV of Parquet |
| **Tensor** | een blok getallen met twee of meer indices (matrix = 2 indices) | een Hessiaan (3N × 3N); Δ₂ (M × M) | NumPy `.npz` |

Twee vormen die je moet kennen. **JSON** is tekst met geneste haakjes: `{"rung": "R1",
"K": 96, "mode": "E"}`. Leesbaar voor mens en machine; geschikt voor records. **CSV** is
tekst met komma's: één regel per rij, één kolom per veld; geschikt voor tabellen. Grote
numerieke blokken (matrices) gaan als binair `.npz`, omdat tekst daar te traag en te groot
voor is.

## §6.2 De objecten van de pijplijn

Hieronder de veertien objecten die de documenten noemen, elk met zijn belangrijkste
velden. De veldnamen zijn beschrijvend, niet de definitieve programmanamen (er bestaat nog
geen code); het gaat om *wat* erin zit.

### O1 — Molecuulrecord

| Veld | Type | Betekenis |
|---|---|---|
| identifier | tekst | CAS-nummer of PAHdb-uid; de sleutel waarmee alles begint |
| formule, lading, aantal atomen N | tekst, geheel getal, geheel getal | benzeen C₆H₆, neutraal, 12 |
| rung | R0…R6 | bepaalt basisset, drempels en welke tests van toepassing zijn |
| geometrie | tensor N × 3 | de DFT-evenwichtsstand (ångström) |

Gemaakt in de R0-pilot en per rung; gelezen door alles.

### O2 — DFT-Hessiaan en modes

| Veld | Type | Betekenis |
|---|---|---|
| H_DFT | tensor 3N × 3N | de goedkope Hessiaan |
| modes | tensor M × 3N | de M normale modes (eigenvectoren) |
| frequenties | lijst M | in cm⁻¹ |
| families | lijst M | label per mode: CH-strek, CC-strek, CH-oop, … |
| dipoolafgeleiden | tensor | nodig voor intensiteiten (niet gescoord, wel berekend) |
| kubische en kwartische DFT-constanten | tensor | voor de resonantie-gesloten familieset plus de totaalsymmetrische modes |
| niveau, basisset, grid, drempels | tekst | vastgelegd in de deck-hash |

Gemaakt per molecuul (module 08 / de probes); gelezen door het deck, de recovery en de
spectrumstap.

### O3 — Deck

Het vooraf vastgelegde plan van één rung.

| Veld | Type | Betekenis |
|---|---|---|
| deck_hash | tekst | vingerafdruk van alles hieronder |
| niveaus | record | DFT-functionaal, CC-methode en code met commit, basisset, drempels, CPS-veld, DFT-grid |
| frozen_space_hash | tekst | vingerafdruk van de opgeslagen orbitaalvectoren (probe M1) |
| patronen | lijst van records | elk: index, de vector p (3N), het paar ±, soort (enkelvoudig / meervoudig / tweemodes / q₂), hold-out ja/nee |
| q_s | getal | de patroonamplitude (uit de Q6-grid; verwacht 1,0) |
| hold-out zaadje en f_h | getal, getal | de regel die de achtergehouden paren aanwijst |
| prior | record | bandbreedte w en strafgewichten (structureel) of "geleerd" met modelhash |
| paarlijst voor directe koppelingen | lijst | atoomparen per afstandsklasse, met stap h |
| K_cap, n_min(G) | getallen | de plafonds uit de pilotnotitie |

Gemaakt vóór de eerste probe van een rung; daarna onveranderlijk. Gelezen door de
batchrunner, de recovery, en de campagne-officier (die de hash controleert).

### O4 — Patroon

Eén element van de deck-lijst: `{index, p, paar_id, soort, holdout}`. Het paar ±p deelt
één index; de hold-out-markering hoort bij het paar.

### O5 — Antwoordrecord (response record)

Eén rij per uitgevoerd patroonpaar.

| Veld | Type | Betekenis |
|---|---|---|
| deck_hash, paar_id | tekst, getal | koppeling aan het deck |
| E_CC(+p), E_CC(−p), E_DFT(+p), E_DFT(−p) | getallen | de vier energieën (mode E) |
| E_CC(0), E_DFT(0) | getallen | de gedeelde referentie |
| R_s, R_a | getallen | de symmetrische en antisymmetrische combinatie |
| gradiënten | tensoren 3N (optioneel) | alleen in mode G |
| rekentijd, machine, datum | getal, tekst, tekst | voor het kostenrecord |
| convergentiestatus | tekst | geslaagd / niet geconvergeerd |

Gemaakt door de batchrunner; gelezen door de recovery en de kostenclassificatie. De
antwoordrecords van de **dry run** (DFT tegen DFT) zijn de trainingsdata van module 06.

### O6 — Recoveryresultaat

| Veld | Type | Betekenis |
|---|---|---|
| Δ₂ | tensor M × M | de teruggevonden correctie, in de DFT-modebasis |
| ρ-curve | lijst van (n, ρ) | de achtergehouden fout na elk paar; bewaard, niet alleen het eindpunt |
| K, K_off | gehele getallen | in energieën |
| c₀ | getal | de afgetrokken referentiecorrectie |
| Δ₁ | lijst | per totaalsymmetrische mode, uit R_a |
| prior | tekst | structureel / geleerd |
| status | tekst | teruggevonden / niet binnen K_cap / op ruisniveau |

### O7 — Kostenrecord

Het vaste formaat uit Ladder §1, één per rung en per mode: K, 2M, K_off, K_off bij de
gemeenschappelijke drempel, rung, mode, prior, σ, c₀, q₂-blok, RMS_resp, ρ_noise, c, ρ*,
ρ(K), extrapolatie, rekentijd per probe, machine, script. Wordt door de campagne-officier
uitgegeven en door niemand met de hand geschreven.

### O8 — Opponent-atlas (module 02)

Tabel, één rij per berekende band: `uid, formule, lading, N, bandpositie, intensiteit,
schaalfactor, basisset, familie`. Bron: PAHdb v4.00 (NASA). Ruim 10⁵ rijen.

### O9 — Lab-scorebord (module 03)

Tabel, één rij per gemeten band: `bron (PAHdb-experimenteel / NIST / PNNL), uid of CAS,
molecuul, fase (gas / matrix), bronklasse (cel / dampcel / GC-IR), temperatuur, opgegeven
resolutie, bandpositie, centroïde-precisie, temperatuurterm u_T, u_band, familie, oordeel
(gas-beslisbaar / matrix-gegated / onbeslisbaar door constructie)`. Plus per familie de
gemeten matrix–gas-verschuiving met haar toets.

### O10 — Gekoppelde theorie↔lab-tabel (module 04)

Tabel: per band een rij die O8 aan O9 koppelt: `molecuul, familie, harmonische
DFT-positie (geschaald), labpositie, verschil, kenmerken van molecuul en band`. Eigen
uitgave met DOI vóór module 04 begint.

### O11 — Δ₂-corpus (module 05)

Per molecuul uit de QM9-deelverzameling: `tokens (M DFT-modes met kenmerken:
frequentie, samenstelling, atoomomgeving), label (M × M steunmatrix: welke elementen groot
zijn), Δ₂ = ωB97x − B3LYP (tensor M × M)`. Gesplitst per molecuul met hash. Eigen uitgave
met DOI vóór module 05 begint.

### O12 — Patroon-antwoordcorpus (module 06)

De antwoordrecords (O5) van de QM9-dry-runs, met per molecuul de modestructuur:
`molecuul, modes, patroon p, R_s, ρ-winst van dit patroon`. Nieuwe splits-hash; de
PAK-dry-run-tensoren zitten er niet in (die zijn de testset van module 05).

### O13 — Certificaat (module 08)

| Veld | Type | Betekenis |
|---|---|---|
| molecuul, rung | tekst | |
| spectrum | lijst van (positie, familie, foutbudget) | de beloofde uitvoer |
| foutbudget per band | record | DFT-niveau, ρ, ruisvloer, bevriezingsbias, eerste-orde-geometrieterm, verre aandeel, matrix–gas-verschuiving |
| beat-uitslag per familie | tekst | beat / verloren / onbeslisbaar (met u_band) |
| kostenrecord(s) | O7 | |
| licenties | record | Q6, Q7, Q8, fragmentlicentie (a)(b)(b′)(c), geleerde prior: verdiend / gespendeerd |
| hashes | lijst | deck, pilotnotitie, modelversies |
| **of:** weigering | tekst | de poort, het plafond of de rung die blokkeerde |

### O14 — Pilotnotitie

Een gedateerd tekstbestand met de dertien bevroren onderdelen van Ladder §4: bandlijsten,
marges per familie, P-poortgetallen, matrixtolerantie, P3-effectgrootte, M04-recept,
resonantiebehandeling, c per mode, K_cap en n_min(G), f_h en zaadje, τ₇ en d₇, de
Q8-getallen en paarlijsten, de Q6-getallen met q_s. Gecommit vóór de eerste lokale-CC-Δ₂;
zijn commit-hash is de sleutel die de verzegelde bestanden opent.

## §6.3 Wie maakt wat, wie leest wat

| Object | Gemaakt door | Gelezen door |
|---|---|---|
| O1 molecuulrecord | R0-pilot / per rung | alles |
| O2 DFT-Hessiaan | probes, M08 | deck, recovery, spectrumstap, M05-corpus (DFT-kant) |
| O3 deck | probes vóór de rung; M06 mag patronen toevoegen vóór de hash | batchrunner, recovery, M07 |
| O5 antwoordrecords | batchrunner | recovery, M07 (classificatie), M06 (dry-run-versie als corpus) |
| O6 recovery | recovery-solver (infrastructuur, geen module-ML) | spectrumstap, Q7/Q8, M07 |
| O7 kostenrecord | M07 | M08, het paper |
| O8 atlas | M02 | M04 (koppeltabel), M08 (opponentkolom) |
| O9 scorebord | M03 | pilotnotitie item 1/2/4, M04, M08 (score), M07 (weigering zonder u_band) |
| O10 koppeltabel | M04 | M04-model; M08 (gekalibreerde kolom, onzekerheidslaag) |
| O11 Δ₂-corpus | M05 (uit dry runs) | M05-model; de geleerde prior in O3 |
| O12 patroon-antwoordcorpus | M06 (uit dry runs) | M06-model; voorstellen gaan het deck in vóór de hash |
| O13 certificaat | M08 via M07 | de lezer, het paper, module 09 |
| O14 pilotnotitie | de student, na de voornotitieprobes | M07 (elke weigering verwijst ernaar), alles |

## §6.4 De stroom in één schema

```
molecuul-identifier
      │
      ▼
[O1] molecuulrecord ──► DFT-geometrie, Hessiaan, modes, families [O2]
      │                                   │
      │                                   ▼
      │                          deck opstellen [O3]  ◄── prior (structureel, of geleerd uit M05)
      │                                   │            ◄── patronen uit M06 (vóór de hash)
      │                                   ▼  (hash vastgezet)
      │                     batchrunner: per paar CC + DFT ──► antwoordrecords [O5]
      │                                   │
      │                                   ▼
      │                 recovery: Δ₂, ρ-curve, K, K_off, c₀, Δ₁ [O6]
      │                                   │
      │              ┌────────────────────┼─────────────────────┐
      │              ▼                    ▼                     ▼
      │        Q6 ankerlicentie    Q7 probinglicentie     Q8 lokaliteit/verzadiging
      │              └────────────────────┼─────────────────────┘
      │                                   ▼
      │        spectrum: DFT + Δ₂ + eerste-orde-geometrieterm, anharmonisch via GVPT2
      │                                   │
      ▼                                   ▼
[O9] scorebord ──► beat-vergelijking per familie ◄── [O8] atlas, [O10] gekalibreerde kolom (M04)
                                          │
                                          ▼
                  M07 campagne-officier: kostenrecord [O7], certificaat of weigering [O13]
```

Alles rechts van "hash vastgezet" mag het deck niet meer veranderen. Alles boven de
beat-vergelijking mag het scorebord niet zien: het lab is nooit trainings-, validatie- of
stopinvoer.

## §6.5 Drie regels over data

1. **Hash of het bestaat niet.** Deck, orbitalen, pilotnotitie en modelversies hebben een
   vingerafdruk; elk resultaat vermeldt die. Een batch met een verkeerde hash wordt
   geweigerd.
2. **Verzegeld tot de sleutel er is.** De fitcoëfficiënten van de gladheidsprobe en de
   ruwe energieën van probe M1 bevatten Δ₂-informatie en gaan in een verzegeld bestand dat
   pas opengaat als de pilotnotitie een commit-hash heeft.
3. **Geprint of niet bestaand.** Een getal dat niet door een script in `probes/` is
   uitgeprint, is geen resultaat. Elk kostenrecord noemt het script dat het printte.

## In het kort

Het project gebruikt getallen, lijsten, records (JSON), tabellen (CSV) en tensoren
(`.npz`). Veertien objecten dragen de pijplijn: van molecuulrecord en DFT-Hessiaan via
deck, patronen en antwoordrecords naar recoveryresultaat, kostenrecord en certificaat; de
modules 02–06 leveren elk hun eigen tabel of corpus (atlas, scorebord, koppeltabel,
Δ₂-corpus, patroon-antwoordcorpus). Het deck is onveranderlijk na zijn hash, het lab is
onzichtbaar voor de recovery, en niets telt dat niet is geprint.

*Bron: [Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§3 (Q0-deck, patronen, antwoorden, recovery) en §5–§6; [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§1 (kostenrecord) en §4 (pilotnotitie); [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md)
§2–§4 (de module-datasets); [probes/README.md](../probes/README.md).*
