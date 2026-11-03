# Hoofdstuk 6 — Datastructuren en de pijplijn

> **In dit hoofdstuk leer je**
> – de vijf soorten data die in dit project voorkomen (getal, lijst, record, tabel, tensor)
>   en in welke bestandsvormen ze worden opgeslagen;
> – de vijftien objecten waaruit de pijplijn en haar voorraad data bestaan, elk met zijn velden;
> – welk object door welke stap of module wordt gemaakt en gelezen;
> – hoe de data van "molecuul erin" naar "spectrum met certificaat eruit" stroomt, in één schema;
> – vier regels over data die overal terugkomen.

Dit hoofdstuk is het naslagwerk voor deel B. Elk modulehoofdstuk verwijst bij "Invoer" en
"Uitvoer" naar de objecten die hier zijn gedefinieerd. De veldnamen in dit hoofdstuk zijn de
echte namen uit de code en uit de opgeslagen bestanden. Ze zijn Engels, omdat de code Engels is.

---

## §6.1 Vijf soorten data

In de informatica op school ken je de basistypen (getal, tekst, waar/onwaar) en de
samengestelde typen (lijst, dictionary, object). Dit project gebruikt er vijf, met de
namen die in de documenten voorkomen:

| Soort | Wat het is | Voorbeeld in dit project | Bestandsvorm |
|---|---|---|---|
| **Getal** | één waarde met eenheid | een energie in hartree; een bandpositie in cm⁻¹ | veld in een record of tabel |
| **Lijst / vector** | geordende rij getallen | de 3N − 6 trillingsfrequenties van een molecuul; de bandlijst van een spectrum | JSON-array; kolom van een tabel |
| **Record** | een verzameling benoemde velden (in Python een dictionary) | het pijplijnrecord van één run; één certificaat | JSON-bestand |
| **Tabel** | rijen met dezelfde kolommen (in pandas een DataFrame) | de molecuullijst van het corpus; het lab-scorebord | CSV |
| **Tensor** | een blok getallen met twee of meer indices (een matrix heeft er twee) | een Hessiaan (3N × 3N); de APT (3 × 3N); de correcties van drie seeds (3 × 3N × 3N) | NumPy `.npz` |

Twee vormen moet je kennen. **JSON** is tekst met geneste haakjes, zoals
`{"basis": "6-31G*", "low_functional": "B3LYP", "high_functional": "wB97X"}`. Mens en machine
kunnen het lezen; het is geschikt voor records. **CSV** is tekst met komma's: één regel per rij,
één kolom per veld; het is geschikt voor tabellen. Grote numerieke blokken gaan als binair `.npz`.
Dat is een zip-bestand met benoemde NumPy-arrays. Een Hessiaan van een molecuul met 30 atomen
bevat 90 × 90 = 8.100 getallen; als tekst zou dat te traag en te groot zijn.

**Eenheden.** De rekenbestanden gebruiken atomaire eenheden. Een lengte staat in bohr
(1 bohr ≈ 0,529 Å), een energie in hartree (1 hartree ≈ 27,2 eV), een Hessiaan dus in
hartree/bohr². Frequenties en bandposities staan in cm⁻¹, bandhoogtes (intensiteiten) in km/mol.

**Vingerafdruk.** Een *hash* is een korte code die een programma uit de inhoud van een bestand
berekent. Dit project gebruikt SHA-256: 64 tekens die volledig veranderen als er één bit in het
bestand verandert. Vaak staan alleen de eerste zestien tekens in een record, onder de naam
`sha16`. Zo kan iedereen later controleren dat een record bij precies dát bestand hoort.

## §6.2 De objecten van de pijplijn

De objecten vallen in drie groepen. O1–O3 en O11 zijn de **voorraad**: het corpus van
doorgerekende moleculen en de vaste rekeninstellingen. O4–O7 en O13 ontstaan **per run** van de
pijplijn. O8–O10 en O12 zijn de **datasets van de andere modules**. O14 en O15 zijn de twee
**registers** die zeggen welke ankers en welke netwerken gebruikt mogen worden.

### O1 — Molecuulrecord

Eén rij van de molecuullijst van het corpus (`manifest.csv` in de corpusmap van module 05).

| Veld | Type | Betekenis |
|---|---|---|
| id | tekst | laag plus tien tekens van een hash, bijvoorbeeld `A_8448043181` voor benzeen |
| layer | tekst | de laag: A (46 met de hand gekozen moedermoleculen), A2 (327 kinderen met zijgroepen), B (743 kleine kernen met zijgroepen), P3 (60 aza-vierringen en vijfringsystemen), P3c (60 kationen) |
| priority | tekst | de volledige hash; zijn volgorde is de vaste volgorde waarin deelverzamelingen worden getrokken |
| name, smiles | tekst | de naam en de SMILES-schrijfwijze van het molecuul |
| n_heavy, n_atoms | gehele getallen | aantal zware atomen (alles behalve waterstof) en aantal atomen |
| status, machine | tekst | klaar of niet; op welke computer het is gerekend |

Een **SMILES** is een regel tekst die een molecuul beschrijft: `c1ccccc1` is benzeen. Kleine
letters zijn aromatische atomen, cijfers sluiten een ring. Hetzelfde molecuul kan op meer
manieren worden geschreven. RDKit, een open scheikundebibliotheek, maakt er één vaste
schrijfwijze van: de **canonieke SMILES**. Die vaste schrijfwijze is de sleutel waarmee de
pijplijn een molecuul herkent.

### O2 — Corpusmap

Per molecuul één map onder `corpus/molecules/<id>/`, op 3 november 2026 1.236 mappen. Dit zijn
de bestanden die tellen:

| Bestand | Inhoud | Velden |
|---|---|---|
| `geometry.json` | de evenwichtsstand, geoptimaliseerd met B3LYP/6-31G* | `symbols` (element per atoom), `coords_bohr` (N × 3), `masses_amu`, `optimised_at` |
| `hessian_b3lyp_analytic.npz` | de goedkope Hessiaan, analytisch berekend met pyscf | `H_raw`, `H_projected` (3N × 3N), `freq_cm`, `energy`, `grid` (rekenrooster 99/590), `charge`, `spin`, `software` |
| `hessian_wb97x_analytic.npz` | de betere Hessiaan, ωB97X/6-31G*, op dezelfde geometrie | dezelfde velden |
| `dipole_b3lyp_cphf.npz` | de APT: hoe het dipoolmoment verandert als een atoom beweegt | `apt` (3 × 3N), `intensity_km_mol`, `route`, `passed` en de controles `sum_rule_max`, `cphf_residual_after` |
| `result.json` | het verslag van de rekenstap | `deck`, `timings_s`, `freq_b3lyp_cm`, `freq_wb97x_cm`, `n_imaginary_b3lyp`, `n_imaginary_wb97x`, `peak_rss_gb` |
| `analytic_check.json` | de twee routes naast elkaar | per functionaal de frequenties van pyscf en van psi4, en het grootste verschil tussen hun Hessianen (`dH_max`) |

Een Hessiaan is de matrix van tweede afgeleiden van de energie naar de atoomposities
(hoofdstuk 2 en 4). Uit de Hessiaan volgen de bandposities. De **APT** (*atomic polar tensor*)
geeft de bandhoogtes: een trilling absorbeert infrarood licht in de mate waarin ze het
dipoolmoment laat schommelen. `H_projected` is de Hessiaan waaruit verschuiving en draaiing van
het hele molecuul zijn verwijderd; dan blijven 3N − 6 echte trillingen over.

De map bevat ook de oudere Hessianen van het rekenprogramma psi4 (`hessian_b3lyp.npz`,
`hessian_wb97x.npz`), op een grover rekenrooster. Dat is de tweede route uit besluit 50: elk
getal dat ertoe doet, wordt langs twee wegen berekend. De labels waarop het netwerk leert, zijn
de analytische Hessianen van pyscf. Niet elke map is even ver. Alle 1.230 klaargemelde mappen
hebben het psi4-paar; 862 hebben ook het analytische pyscf-paar; 478 hebben een APT.

### O3 — Deck

De vaste rekeninstellingen van het corpus: `corpus/decks/deck_v1.json`, met vingerafdruk
`9e27bf8e934893f3`. Voor kationen bestaat een eigen deck.

| Veld | Waarde in deck v1 |
|---|---|
| engine | psi4 1.11 |
| basis | 6-31G* |
| low_functional, high_functional | B3LYP, wB97X |
| optimise_at | B3LYP/6-31G* |
| hessian | analytisch, beide functionalen op dezelfde geometrie |
| dft_radial_points, dft_spherical_points | 75, 302 (het rekenrooster van psi4) |
| scf_type, e_convergence, d_convergence | df, 1e-8, 1e-8 |
| reference, charge, multiplicity | rhf, 0, 1 (neutraal, alle elektronen gepaard) |
| units_in_files | geometrie in bohr, Hessiaan in hartree/bohr², frequenties in cm⁻¹ |

Het deck verandert nooit. Een andere instelling is een nieuw deck met een nieuwe vingerafdruk.
Elk pijplijnrecord noemt de vingerafdruk van het deck waarmee het is gerekend.

### O4 — ΔH-correctie

Wat het netwerk per molecuul voorspelt: `correction.npz` in de resultaatmap van een run.

| Veld | Type | Betekenis |
|---|---|---|
| dH | tensor 3N × 3N | het gemiddelde van de drie seeds: de correctie die bij de B3LYP-Hessiaan wordt opgeteld |
| dH_seeds | tensor 3 × 3N × 3N | de correctie van elke seed apart |
| models | lijst van 3 | de bestandsnamen van de drie netwerken |

Een **seed** is één training van hetzelfde recept met een ander startgetal voor het toeval. Drie
seeds geven drie netwerken. Hun gemiddelde is de voorspelling; hun spreiding laat zien hoe zeker
die is. Het netwerk leest de geometrie en de B3LYP-Hessiaan en voorspelt een correctie per paar
interne coördinaten (bindingslengtes, hoeken). Daaruit wordt ΔH in gewone coördinaten gemaakt
(besluit 49; [hoofdstuk 5](05_De_Kern_Delta_Probing.md) en hoofdstuk 10).

### O5 — Pijplijnrecord

Het verslag van één run: `pipeline.json` in de resultaatmap. Dit zijn de blokken:

| Blok | Belangrijkste velden | Betekenis |
|---|---|---|
| pipeline_version, name | tekst | de versie van de pijplijn (nu 0.9) en de naam van de run |
| input | `smiles`, `xyz`, `xyz_atom_order` | wat de gebruiker gaf |
| admission | `smiles` (canoniek), `formula`, `elements`, `n_atoms`, `training_elements`, `training_atoms`, `models`, `inside_training_sizes` | de toelating: past het molecuul bij wat het netwerk heeft gezien? Per netwerk `path`, `sha16`, `network`, `version`, `status` |
| deck | `file`, `sha16` | het deck (O3) |
| optimisation | `e_opt`, `timings_s` | de energie in het minimum en de rekentijden |
| low_level | per functionaal `freq_analytic`, `energy`, `seconds`, `software` | de goedkope Hessiaan |
| reuse | `reused`, `source`, `order`, `start_rmsd_angstrom`, `sha256` | of stap 2–3 uit het corpus kwam, uit welke map, en de vingerafdruk van elk overgenomen bestand |
| seconds | per stap | de echte rekentijd op de laptop |
| spectra | `network` en `baseline`, elk met `sticks` (per band `omega_cm`, `km_mol`, bij het netwerk ook `seed_range_cm`), `broadening`, `method`; en `note` | de twee spectra; de noot zegt dat de posities harmonisch zijn |
| provenance | `timestamp_utc`, `host`, `python`, `numpy`, `command`, `commit`, `dirty` | waar, wanneer en met welke code de run startte |

Naast `pipeline.json` liggen de rekenbestanden van de run zelf: `geometry.json`,
`hessian_b3lyp_analytic.npz`, `dipole_b3lyp_cphf.npz` en `correction.npz`. Ze hebben dezelfde
vorm als in de corpusmap (O2) en bij O4.

De *baseline* is het B3LYP-spectrum, vermenigvuldigd met de vaste schaalfactoren die PAHdb per
gebied gebruikt. Het staat alleen ter vergelijking naast het spectrum van het netwerk.

### O6 — Voortgangsrecord

`progress.json`, bij elke stap van de run opnieuw geschreven. De pijplijnshow leest het om een
lopende run te volgen (hoofdstuk 13).

| Veld | Type | Betekenis |
|---|---|---|
| name, pipeline_version, molecule | tekst, record | welke run; `molecule` met `smiles`, `formula`, `n_atoms` |
| steps | record met zes stations | `molecule`, `geometry`, `optimise`, `hessian`, `network`, `spectrum` |
| steps.\<station\>.state | tekst | `pending`, `active`, `done` of `reused` |
| steps.\<station\>.seconds | getal | de tijd van een berekende stap; bij een overgenomen stap `seconds_then`, de tijd die het corpus er destijds over deed |
| finished, updated | waar/onwaar, tijd | klaar zodra het certificaat is geschreven |

### O7 — Kostenrecord

Twee plaatsen. In het corpus is het een rij van het grootboek `ledger.csv`: `id`, `machine`,
`start`, `end`, `seconds_total`, `seconds_optimise`, `seconds_hessian_b3lyp`,
`seconds_hessian_wb97x`, `peak_rss_gb` (het grootste geheugengebruik) en `status`. In het
certificaat is het het blok `cost`: `steps_s` (seconden per stap), `machine`, `machine_class`
(laptop of server), `seconds`, `hours`, `eur_ex_vat` (de prijs zonder btw) en `source`. Op de
laptop kost een run geen geld; een server heeft een gemeten uurprijs. Niemand schrijft een
kostenrecord met de hand.

### O8 — Opponent-atlas (module 02)

De berekende bibliotheek van NASA's PAHdb, versie 4.00, als tabel: 10.749 rijen (één per
molecuul in een bepaalde ladingstoestand) × 27 kolommen, met een bandtabel van 2,5 miljoen rijen ernaast. Dit is de bestaande
voorspelling waartegen het project zich meet. Details in hoofdstuk 7.

### O9 — Lab-scorebord (module 03)

`bands_lab.csv`: 4.218 rijen × 31 kolommen, één rij per gemeten band uit de experimentele
bibliotheek van PAHdb (versie 3.10) en acht gasfase-spectra van NIST. Module 03 leidt daaruit
per bandgebied de **labtolerantie** u_band af: hoe nauwkeurig het lab een band in dat gebied
kan vastleggen (`u_band_by_record_family.csv`). Het certificaat zet die tolerantie naast elke
band. Details in hoofdstuk 8.

### O10 — Gekoppelde theorie↔lab-tabel (module 04)

`training_table.csv`: 2.477 rijen × 28 kolommen, één rij per paar van een gemeten band en de
berekende band van hetzelfde molecuul, over 83 moleculen. Hierop leert module 04 de
gekalibreerde goedkope tegenstander. Details in hoofdstuk 9.

### O11 — ΔH-corpus (module 05)

Het corpus als trainingsset: de mappen van O2, gelezen door de trainer van module 05. Per
molecuul vormen de twee analytische Hessianen op dezelfde geometrie een paar; het verschil
H(ωB97X) − H(B3LYP) is wat het netwerk moet leren. Elke trilling krijgt een **familie**:
CH-strek, ring-ip (ringtrillingen in het vlak), CH-oop (C–H-buigingen uit het vlak) of 'other'
(de rest). Het gedragen netwerk v1.3 trainde op 750 moleculen uit de lagen A, A2 en B.

Twee groepen blijven buiten elke training: de **hold-outs**. Hold-out (a) bestaat nu uit acht
moleculen van laag A. Hold-out (b) bestaat uit 39 moleculen: alle gesubstitueerde moleculen van
twee kernen die het netwerk nooit zag. Alleen fouten op deze twee groepen tellen als maat voor
het netwerk. Details in hoofdstuk 10.

### O12 — Kandidatenset (module 06)

Een bevroren set uit PubChem van 160.972 versmolten-aromatische moleculen, met de kolommen
`cid` (het PubChem-nummer), `smiles`, `formula`, `n_heavy` (zware atomen), `n_arom_rings`
(aromatische ringen) en `cores`. De code van module 06 splitst de set in training, validatie en
test per Murcko-skelet (het ringgeraamte zonder zijgroepen), zodat een skelet nooit in twee
delen tegelijk zit. Hierop leert de kandidatengenerator van module 06. Details in hoofdstuk 11.

### O13 — Certificaat (module 08)

Het certificaat van één run: `certificate.json`, met een leesbare versie `certificate.md`
ernaast. `m08/live_certificate.py` schrijft het uit de bestanden in de resultaatmap; het netwerk
wordt daarvoor niet opnieuw gedraaid.

| Blok | Belangrijkste velden | Betekenis |
|---|---|---|
| molecule | `name`, `smiles`, `formula`, `n_atoms`, `inside_training_sizes`, `listed`, `seen`, `truth` | het molecuul. `listed` is de rij in de catalogus van de Spectrum Atlas. `seen` zegt of het netwerk het molecuul kent: `trained`, `a` of `b` (in een hold-out), `catalogue` (alleen in de catalogus) of `unseen`. `truth` zet de ωB97X-waarheid naast het netwerk waar het corpus die heeft (`rms_by_rank_cm`, `overlap`) |
| network | `name`, `version`, `models`, `predicts` | het netwerk dat draaide, en het niveau waarnaar het corrigeert (ωB97X/6-31G*) |
| accuracy | per hold-out `readouts` (per familie `mean`, `seeds`, `target`, `within_target`) en `shape` | de gemeten fout van deze netwerkversie, gelezen uit haar eigen evaluatierecords |
| bands | per band `network_cm`, `km_mol`, `seed_range_cm`, `b3lyp_cm`, `baseline_cm`, `family`, `licensed`, `error_cm`, `lab_region`, `u_band_cm` | de kern: elke band met zijn positie, hoogte, spreiding over de seeds, familie, licentie, gemeten fout en labtolerantie |
| tolerance | `per_region`, `rule` | de labtoleranties uit O9 en de regel die banden in gebieden indeelt |
| licence | `statement`, `rule_source`, `licensed_families` | welke families zijn vrijgegeven (besluit 65) |
| cost | zie O7 | |
| provenance | `run_commit`, `certificate_commit`, `deck_sha16`, `low_level_software`, `reused_from`, `note` | de herkomst van elk getal |
| statement | tekst | één alinea die zegt wat het certificaat belooft en wat niet |

De `overlap` is de cosinusovereenkomst van twee verbrede spectra: 1 betekent dezelfde vorm,
0 geen gemeenschappelijke banden. `rms_by_rank_cm` vergelijkt de laagste band met de laagste,
de tweede met de tweede, enzovoort, en geeft de wortel van het gemiddelde kwadratische verschil.

### O14 — Ankerregister

Het register van alle coupled-cluster-Hessianen (CCSD(T), hoofdstuk 3):
`out/ANCHORS_STATUS.json` in module 05, met het overzicht `modules/ANCHORS.md` dat er
automatisch uit wordt gemaakt (besluit 62).

| Veld | Type | Betekenis |
|---|---|---|
| mol_id, name | tekst | het molecuul |
| path, sha16 | tekst | het bestand en zijn vingerafdruk |
| level, tier | tekst | het rekenniveau, bijvoorbeeld CCSD(T)/cc-pVDZ plus een MP2-basisstap naar cc-pVTZ; de laag (DZ of TZ) |
| status | tekst | `carried`, `superseded`, `invalid`, `imaginary` of `experimental` |
| date, checks, note | tekst | wanneer, welke controles, en waarom deze status |

Er worden geen rijen gewist: een betere versie wordt een nieuwe rij en de oude krijgt
`superseded`. Per molecuul is precies één rij `carried`. Nu zijn dat er elf: acenaftyleen,
antraceen, azuleen, benzeen, benzonitril, fluorbenzeen, isochinoline, naftaleen, pyridine,
chinoline en chinoxaline. De standaard is CCSD(T)/cc-pVDZ met een MP2-basisstap naar cc-pVTZ;
benzeen heeft een volledige CCSD(T)/cc-pVTZ-Hessiaan.

### O15 — Modelregister

Het register van alle getrainde netwerken: `out/MODELS_STATUS.json` in module 05, met de
overzichten `modules/MODELS.md` en `modules/05_support_predictor/MODELS.md` die er automatisch
uit worden gemaakt. Per opgeslagen netwerk (een *checkpoint*): `status`, `network`, `version`,
`chain` (de trainingsrun) en `note`. De status is `carried`, `superseded`, `candidate`,
`experimental`, `smoke`, `pretrained` of `invalid`. Alleen een `carried` netwerk mag werk doen
(besluit 55); de laadfuncties weigeren de andere. Het ΔH-netwerk heeft 83 checkpoints, waarvan
drie `carried`: de drie seeds van v1.3. Een versienummer 1.x betekent: in gebruik in de
pijplijn; 0.x betekent: buiten gebruik (besluit 59).

## §6.3 Wie maakt wat, wie leest wat

| Object | Gemaakt door | Gelezen door |
|---|---|---|
| O1 molecuulrecord | de corpusfabriek van module 05 | de rekenjobs, de trainer, de Atlas-export |
| O2 corpusmap | psi4 en pyscf, via de corpusfabriek | de trainer (O11), de pijplijn bij hergebruik, het certificaat (`truth`), de Atlas |
| O3 deck | vastgelegd vóór de eerste corpusrun | elke rekenjob, de pijplijn, de hergebruikcontrole |
| O4 ΔH-correctie | pijplijnstap 4 | stap 5, het certificaat, de show |
| O5 pijplijnrecord | de pijplijn | het certificaat, de show |
| O6 voortgangsrecord | de pijplijn, bij elke stap | de live-modus van de show |
| O7 kostenrecord | de corpusfabriek (grootboek); het certificaat (blok `cost`) | het certificaat, de prijzentabel van module 08 |
| O8 opponent-atlas | module 02 | module 04, het paper |
| O9 lab-scorebord | module 03 | module 04, het certificaat (u_band) |
| O10 koppeltabel | module 04 | het model van module 04 |
| O11 ΔH-corpus | de corpusfabriek | de trainer van module 05 |
| O12 kandidatenset | PubChem, bevroren door module 06 | de generator van module 06 |
| O13 certificaat | `m08/live_certificate.py` | de lezer, de show, de Spectrum Atlas, module 09 |
| O14 ankerregister | `m05/anchor_registry.py` | de leesscripts van module 05, de Atlas |
| O15 modelregister | `m05/model_registry.py` | de pijplijn (alleen `carried`), de trainer, het certificaat |

## §6.4 De stroom in één schema

```
SMILES of xyz-bestand
      │
      ▼
toelating: neutraal? gesloten schil? aromatische ring? elementen gezien?   ──► weigering met de reden
netwerken 'carried' in O15?                                                    (vóór elke berekening)
      │
      ▼
1  startgeometrie (RDKit, atomen in de canonieke volgorde)
      │
      ├── heeft het corpus dit molecuul zo gerekend? ── ja ──► O2: geometrie, B3LYP-Hessiaan, APT
      │                                                          (stap 2 en 3 overgeslagen)
      ▼ nee                                                                 │
2  optimalisatie: psi4, B3LYP/6-31G*, deck O3                               │
      ▼                                                                     │
3  analytische B3LYP-Hessiaan en APT: pyscf                                 │
      │◄────────────────────────────────────────────────────────────────────┘
      ▼
4  ΔH-netwerk v1.3, drie seeds ──► O4 correction.npz
      ▼
5  spectrum: posities uit H_B3LYP + ΔH, hoogtes uit de B3LYP-APT
      ▼
certificaat O13 ◄── fout per familie uit de evaluatierecords (hold-outs a en b)
                ◄── licentie per familie (besluit 65)
                ◄── labtolerantie u_band (O9)
                ◄── catalogusrij en 'gezien?' (O1, O11, O15)

ernaast: O5 pipeline.json · O6 progress.json (voor de show) · O7 kosten
```

De voorraad links van dit schema wordt apart gemaakt. De corpusfabriek rekent de mappen (O2).
De trainer leert daarop het netwerk en schrijft het in het modelregister (O15). De ankers (O14)
liggen naast het corpus als ijkpunten op coupled-cluster-niveau. De pijplijn gebruikt ze in
versie 0.9 nog niet: voor netwerk v1.3 is geen meting op coupled-cluster-niveau gedaan, en het
certificaat zegt dat.

## §6.5 Vier regels over data

1. **Vingerafdruk of het telt niet.** Het deck, elk netwerk en elk overgenomen corpusbestand
   staan met hun vingerafdruk in het record. Het record noemt ook de commit van de code (de
   versie in git) en of er onbewaarde wijzigingen waren (`dirty`). Een resultaat waarvan de
   herkomst niet vaststaat, is geen resultaat.
2. **Eén gedragen versie.** De registers wissen niets. Per molecuul is één anker `carried`, per
   netwerk één versie. De laadfuncties weigeren al het andere. Zo kan een oud of mislukt bestand
   niet per ongeluk een uitkomst bepalen.
3. **De hold-outs en het lab blijven buiten de training.** Een molecuul in een hold-out mag niet
   in de training zitten, ook niet onder een andere naam. Die regel bleek moeilijker dan hij
   klinkt. Twee moleculen van hold-out (a), 2-naftoëzuur en benzonitril, zaten ook in laag B,
   met een ander id. Het netwerk had ze dus gezien. Een controle op canonieke SMILES vond dit.
   Nu laat de trainer zulke tweelingen standaard weg, en het certificaat leest hold-out (a)
   zonder die twee. De fouten werden 0,04 tot 0,27 cm⁻¹ groter; de licentie veranderde voor
   geen enkele familie. De labdata zijn nooit trainings-, validatie- of stopinvoer.
4. **Geprint of niet bestaand.** Een getal in een document komt uit een record dat een script
   heeft geschreven, en dat record noemt zijn bron. Een record wordt eerst naar een tijdelijk
   bestand geschreven en pas daarna over het oude gezet. Een afgebroken run laat dan geen half
   bestand achter.

## In het kort

Het project gebruikt getallen, lijsten, records (JSON), tabellen (CSV) en tensoren (`.npz`).
De voorraad is het corpus: per molecuul een map met de geometrie, twee analytische Hessianen
(B3LYP en ωB97X) en de APT, gerekend met één vast deck. Een run van de pijplijn maakt een
correctie (O4), een pijplijnrecord (O5), een voortgangsrecord (O6) en een certificaat (O13) dat
per band zegt hoe goed die bekend is. Twee registers bepalen welke ankers en welke netwerken
mogen meedoen. Alles draagt een vingerafdruk, de hold-outs blijven buiten de training, en
niets telt dat niet door een script is geschreven.

*Bron: de code `modules/08_industry_synthesis/m08/pipeline.py`, `m08/live_certificate.py`,
`m08/progress.py` en `m05/rungC_infer.py`; de records van de runs
`probes/results_m1/pipeline_rehearsal_2026-10-30/cinnoline/` en
`probes/results_m1/pipeline_benzene_reuse_2026-11-03/benzene/`; de corpusmap
`modules/05_support_predictor/corpus/` (`manifest.csv`, `ledger.csv`, `decks/deck_v1.json`,
`molecules/A_8448043181/`); [PIPELINE.md](../modules/PIPELINE.md),
[ANCHORS.md](../modules/ANCHORS.md), [MODELS.md](../modules/MODELS.md); de README's van de
modules 02, 03, 04 en 06; [TASKS_closed.md](../TASKS_closed.md) rij 157 (de tweelingen in
hold-out (a)).*
