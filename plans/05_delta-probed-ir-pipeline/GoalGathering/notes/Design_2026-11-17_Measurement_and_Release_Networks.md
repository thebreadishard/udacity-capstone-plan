# Measurement networks and release networks (decision 66, 17 November 2026)

**The user, 17 November 2026:** 'Als ik een netwerk zou maken voor de IR-lijnen van aromatische moleculen, zou ik dat trainen op
benzeen. Maken we een denkfout door het molecuul uit de trainingsset te houden?' — and, to the proposal below: 'Ja, goed idee. Aromir
krijgt een netwerk dat getraind is op alle data. Behoud wel een taak om het signaal van vannacht verder uit te zoeken.'

## 1. The fault

Until today one set of networks did two jobs. It was the instrument that measures the error — so ten parent molecules (hold-out
(a), set aside on 19 September, benzene among them) and two scaffolds (hold-out (b)) never train — and it was the product: the same
three checkpoints go into the pipeline and into aromir. The product is therefore weakest exactly where it need not be: on benzene,
biphenyl, phenanthrene, fluorene, fluoranthene and the rest, which every reader tries first, and which we hold labels for.
CLAUDE.md's rule is that the network trains on the most correct molecules we have. Measuring and delivering are two aims.

## 2. Two kinds of network, one recipe

- **Measurement networks** — as now: the pool without the hold-outs (and without their twins), three seeds. Every error bar, every
  licence (decision 65 as amended) and every promotion is read on them. They are never shipped as the product.
- **Release networks** — the same recipe, the same seeds, the same early-stopping rule, trained on **everything with labels of the
  carried kind**: the pool, hold-out (a), hold-out (b), the twins. They go into the pipeline and into aromir.

A version is the pair. It is promoted on its measurement networks by the registered rule; its release networks are trained only
after that, and are released only if the checks of §4 pass.

## 3. What a certificate says

One sentence, on every certificate and on the card, in place of today's 'with the error measured on molecules the network never saw':

> The spectrum is made by the release networks of version X, trained on all N molecules with labels: each of the 3 networks is
> fitted on a random 85 % of them and stopped on the other 15 %, a different 15 % per seed, so a molecule is fitted by most of the
> networks and not by every one (rarely by none). Its error bars were measured on the measurement networks of the same version —
> the same recipe trained without the hold-out molecules — on molecules those networks never saw; the release networks themselves
> have seen every molecule we hold labels for, so they have no held-out error of their own.

(Amended the same day after the review: 'trained on' is 'fitted or stopped on'. The recipe's inner validation keeps 15 % of the
pool out of each seed's fit, the hold-out molecules included; for three seeds 0.15³ of the molecules, about four of 1,132, are
fitted by no network. The release checks' record says, for benzene, how many release networks fitted it.)

Per molecule the 'seen' line then reads, for a molecule that is in the training data of the release networks (benzene, every
hold-out molecule, every pool molecule): 'in the release networks' training data: the error bars are not an out-of-sample error for
this molecule; expect it to be smaller'. For any other molecule: as now.

The licence keeps its meaning: a family is licensed where the measurement networks' error is within the line on both hold-outs.
It is a statement about the recipe on unseen molecules, which is what a user's new molecule is.

## 4. What must hold before release networks are shipped

Stated before any exists. Each is a check with its number, in the release's record:

1. **Same recipe**: the release training's command differs from the measurement training's only in the molecules it may train on;
   pinned by a test.
2. **No surprise on the pool**: on a fixed sample of pool molecules that both kinds trained on, the release networks' answer differs
   from the measurement networks' by no more than the measurement networks differ among their own seeds (reported per family).
3. **The hold-out molecules are learnt, not broken**: on hold-outs (a) and (b) the release networks' error is below the measurement
   networks' in every family (it is in-sample now; a higher error would mean something is wrong).
4. **Early stopping**: the best epoch is not at the cap (decision 51), as for any training.
5. **Benzene, by name**: its bands are reported for both kinds and against the previous version's release (TASKS 253's signal).

A release that fails a check is not shipped; the measurement networks are then the product, as today, and the certificate says so.

## 5. What it costs and what it does not solve

- One more training of three seeds per release, about six to seven laptop hours.
- The shipped weights are not themselves tested on unseen molecules; only their recipe is. That is the accepted practice, and the
  sentence of §3 says it in plain words.
- A demonstration on 'benzene, never seen' is a statement about the measurement networks. The demo of 25 November can show both.
- It does not explain why the recipe on the larger pool reads benzene worse (17 November: CH-oop 8.70 / 4.10 / 2.94 over three seeds
  against the carried version's 3.00 / 2.19 / 1.48). That signal is about extrapolation to a small, unsubstituted, highly symmetric
  parent — the kind of molecule a user may bring that we do not hold. TASKS 253 keeps it.

## 6. What has to be built

1. The trainer: one explicit, validated setting for 'train on the hold-outs too' (refused together with any option that reads a
   hold-out as a test), a record that says which kind it is, and the loaders' refusal to read a release network's error on a
   hold-out as a measurement (`rungC_eval_saved.py`, `promotion_read`, `m08/accuracy.py`).
2. The registry: a network's kind (measurement / release) beside its version; 'carried' names the pair.
3. The pipeline and aromir: load the release networks, print §3's sentence, take error bars and licence from the measurement
   networks' records; aromir's release folder carries both records and says which weights it ships.
4. §4's checks as one script with its record.
5. README decision 65's text and the promotion design note: 'the carried network' becomes 'the carried version's measurement
   networks' wherever an error is read.

Order: after the question of which version is carried is settled (TASKS 129) — the first release networks are that version's.
