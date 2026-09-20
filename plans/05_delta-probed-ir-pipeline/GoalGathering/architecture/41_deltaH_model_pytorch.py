"""41 — Het ΔH-model in PyTorch: de definitie van het netwerk (blad 4a in code).

Dit bestand definieert alleen het netwerk: invoerlaag, verborgen lagen, uitvoerlagen en wat er
standaard omheen hoort (configuratie, maskering, initialisatie, verliesfuncties, ensemble,
parametertelling, rooktest). Training (blad 3) en test en licentie (blad 3b) staan er niet in; die komen in
`modules/05_support_predictor/` zodra de labels er zijn.

Naamgeving (afspraak 20 september 2026): het geheel is **het ΔH-model**; embedding + self-attention
vormen de **backbone**; **blokkop** en **paarkop** zijn de koppen; exemplaren met verschillende seeds
zijn de **leden** van het **ensemble**; de eenvoudige regels (familiemediaan) zijn de **baseline**.

Getallen komen uit de desk-notitie van 18 september (§1): twee encoderlagen, vier attention-heads,
breedte 64, dropout 0.1, orde 10⁵ parameters; AdamW, lr 1e-3, batch 32 moleculen. Het doelobject is
sinds de RECIPE-wijziging van 19 september het **familieblok** (diagonaal én koppelingen), niet de
losse verschuiving per modus (E4).

Invoer per molecuul (één rij in de batch):
  tokens   (B, M, d_in)  één token per DFT-normaalmodus: [ω/1000, familie one-hot, irrep one-hot,
                          massagewogen aandeel C/H/N/O, lokalisatie-index, omgevingsklassen]
  family   (B, M)        familie-index per modus (voor het blokmasker)
  charge   (B,)          lading van het molecuul (geheel getal)
  mult     (B,)          spinmultipliciteit (1 = singlet, 2 = doublet, …)
  mask     (B, M)        True waar een modus echt is (moleculen hebben 30–100 modi; de rest is opvulling)
Lading en multipliciteit zijn molecuul-tokens die vóór de modustokens worden gezet, zodat kationen
later zonder architectuurwijziging kunnen instromen (P26 §4).

Uitvoer:
  block        (B, M, M)  symmetrisch; ΔH-blok in de modusbasis, alleen gevuld binnen een familie:
                          diagonaal K_ii (verschuiving) en koppelingen K_ij (i ≠ j); eenheid cm⁻¹
  pair_logits  (B, M, M)  logit dat het paar (i, j) tot de steun van ΔH hoort (steunlabel, RECIPE)
Het ensemble geeft daarbovenop per element het gemiddelde en de spreiding over de leden.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import torch
import torch.nn as nn
import torch.nn.functional as F


# ----------------------------------------------------------------------------------------------
# Configuratie
# ----------------------------------------------------------------------------------------------
@dataclass
class DeltaHConfig:
    # invoer
    n_families: int = 5          # C–H strek, C–H oop, C–H in-vlak / ring in-vlak, ring-adem, overig
    n_irreps: int = 8            # one-hot van de irrep binnen de puntgroep (opgevuld tot 8)
    n_elements: int = 4          # massagewogen aandeel van C, H, N, O in de beweging
    n_env: int = 0               # omgevingsklassen (H solo/duo/trio/quartet/substituent; C fused/edge/…); 0 = uit
    max_charge: int = 2          # |lading| ≤ 2 → 5 klassen (−2 … +2)
    max_mult: int = 4            # multipliciteit 1 … 4
    # backbone
    d_model: int = 64
    n_heads: int = 4
    n_layers: int = 2
    d_ff: int = 256              # 4 × d_model, de gebruikelijke verhouding
    dropout: float = 0.1
    # koppen
    d_pair: int = 64             # breedte van het paarnetwerk
    # opleiding (hier alleen vastgelegd; de lus staat in modules/05_support_predictor/)
    lr: float = 1e-3
    weight_decay: float = 1e-2
    batch_molecules: int = 32
    seeds: tuple[int, ...] = field(default_factory=lambda: (0, 1, 2))

    @property
    def d_in(self) -> int:
        # ω/1000 (1) + familie + irrep + elementaandelen + lokalisatie (1) + omgevingsklassen
        return 1 + self.n_families + self.n_irreps + self.n_elements + 1 + self.n_env


# ----------------------------------------------------------------------------------------------
# Invoerlaag: embedding van de modustokens en de twee molecuul-tokens
# ----------------------------------------------------------------------------------------------
class TokenEmbedding(nn.Module):
    """Modustoken (d_in scalars) → vector in R^d_model; lading en multipliciteit → elk één vector.

    Geen positionele codering: de modi van een molecuul zijn een verzameling, geen volgorde; de
    frequentie zit al in het token. De invoer wordt eerst genormaliseerd met vaste schaal (ω/1000,
    aandelen in [0, 1]) en dan door een tweelaags MLP gehaald; een lineaire laag alleen bleek in E0
    te weinig (ridge 17.6 cm⁻¹ op de ringfamilie).
    """

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        self.mode_mlp = nn.Sequential(
            nn.Linear(cfg.d_in, cfg.d_model), nn.GELU(), nn.Linear(cfg.d_model, cfg.d_model)
        )
        self.charge_emb = nn.Embedding(2 * cfg.max_charge + 1, cfg.d_model)   # index = lading + max_charge
        self.mult_emb = nn.Embedding(cfg.max_mult + 1, cfg.d_model)           # index = multipliciteit
        self.type_emb = nn.Embedding(3, cfg.d_model)                          # 0 = modus, 1 = lading, 2 = multipliciteit
        self.max_charge = cfg.max_charge
        self.norm = nn.LayerNorm(cfg.d_model)
        self.drop = nn.Dropout(cfg.dropout)

    def forward(self, tokens, charge, mult, mask):
        B, M, _ = tokens.shape
        h_modes = self.mode_mlp(tokens) + self.type_emb.weight[0]                       # (B, M, d)
        h_charge = (self.charge_emb(charge + self.max_charge) + self.type_emb.weight[1])[:, None]  # (B, 1, d)
        h_mult = (self.mult_emb(mult) + self.type_emb.weight[2])[:, None]              # (B, 1, d)
        h = torch.cat([h_charge, h_mult, h_modes], dim=1)                              # (B, 2 + M, d)
        full_mask = torch.cat([torch.ones(B, 2, dtype=torch.bool, device=mask.device), mask], dim=1)
        return self.drop(self.norm(h)), full_mask


# ----------------------------------------------------------------------------------------------
# Verborgen lagen: self-attention over de modi (de backbone)
# ----------------------------------------------------------------------------------------------
class Backbone(nn.Module):
    """Transformer-encoder: n_layers × (multi-head self-attention → feed-forward), pre-LayerNorm.

    Elke modus kijkt naar elke andere modus van hetzelfde molecuul (en naar de twee molecuul-tokens);
    zo kan een ringmodus 'weten' welke andere ringmodi er zijn en hoe ver ze in frequentie liggen —
    precies de informatie die de koppelingen in het familieblok bepalen.
    """

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        layer = nn.TransformerEncoderLayer(
            d_model=cfg.d_model, nhead=cfg.n_heads, dim_feedforward=cfg.d_ff, dropout=cfg.dropout,
            activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=cfg.n_layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(cfg.d_model)

    def forward(self, h, full_mask):
        h = self.encoder(h, src_key_padding_mask=~full_mask)  # PyTorch maskeert True = negeren
        return self.norm(h)                                    # (B, 2 + M, d): contextvectoren


# ----------------------------------------------------------------------------------------------
# Uitvoerlagen: blokkop en paarkop
# ----------------------------------------------------------------------------------------------
def pair_features(h, omega):
    """Symmetrische paarkenmerken [h_i + h_j, |h_i − h_j|, h_i ⊙ h_j, |ω_i − ω_j|/1000] → (B, M, M, 3d + 1)."""
    hi, hj = h[:, :, None, :], h[:, None, :, :]
    d_omega = (omega[:, :, None] - omega[:, None, :]).abs()[..., None]
    return torch.cat([hi + hj, (hi - hj).abs(), hi * hj, d_omega], dim=-1)


class BlockHead(nn.Module):
    """ΔH-blok per familie in de modusbasis: K_ii uit de contextvector van modus i, K_ij (i ≠ j) uit
    de symmetrische paarkenmerken; buiten de familie en buiten het molecuul nul.

    De symmetrische paarkenmerken (h_i + h_j, |h_i − h_j|, h_i ⊙ h_j) maken K_ij = K_ji in eval-modus;
    met dropout aan verschillen de maskers van (i, j) en (j, i), daarom wordt het blok expliciet gesymmetriseerd. Het blok is het doelobject van de RECIPE-wijziging van 19 september: de loss
    vergelijkt het hele blok met het label, niet alleen de diagonaal (E4).
    """

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        d = cfg.d_model
        self.diag = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Dropout(cfg.dropout), nn.Linear(d, 1))
        self.offdiag = nn.Sequential(nn.Linear(3 * d + 1, cfg.d_pair), nn.GELU(), nn.Dropout(cfg.dropout), nn.Linear(cfg.d_pair, 1))

    def forward(self, h, omega, family, mask):
        diag = self.diag(h).squeeze(-1)                                       # (B, M)
        off = self.offdiag(pair_features(h, omega)).squeeze(-1)               # (B, M, M)
        off = 0.5 * (off + off.transpose(1, 2))                               # exact symmetrisch, ook met dropout aan
        same_family = family[:, :, None] == family[:, None, :]
        valid = mask[:, :, None] & mask[:, None, :]
        eye = torch.eye(h.shape[1], dtype=torch.bool, device=h.device)[None]
        block = torch.where(eye, torch.diag_embed(diag), off)
        return block * (same_family & valid)                                  # (B, M, M), symmetrisch


class PairHead(nn.Module):
    """Steunlabel per moduspaar: logit dat (i, j) een koppeling draagt die de VPT2-band verplaatst.
    Verklaarde baseline (RECIPE): de resonantie-noemerregel van P25, 1/|ω_i² − ω_j²| binnen een irrep."""

    def __init__(self, cfg: DeltaHConfig):
        super().__init__()
        d = cfg.d_model
        self.mlp = nn.Sequential(nn.Linear(3 * d + 1, cfg.d_pair), nn.GELU(), nn.Dropout(cfg.dropout), nn.Linear(cfg.d_pair, 1))

    def forward(self, h, omega, mask):
        logits = self.mlp(pair_features(h, omega)).squeeze(-1)                # (B, M, M)
        valid = mask[:, :, None] & mask[:, None, :]
        return logits.masked_fill(~valid, -1e4)


# ----------------------------------------------------------------------------------------------
# Het ΔH-model: invoerlaag → backbone → twee koppen
# ----------------------------------------------------------------------------------------------
class DeltaHModel(nn.Module):
    def __init__(self, cfg: DeltaHConfig | None = None):
        super().__init__()
        self.cfg = cfg or DeltaHConfig()
        self.embed = TokenEmbedding(self.cfg)
        self.backbone = Backbone(self.cfg)
        self.block_head = BlockHead(self.cfg)
        self.pair_head = PairHead(self.cfg)
        self.apply(self._init)

    @staticmethod
    def _init(m):
        # standaard: Xavier voor lineaire lagen, nul-bias; embeddings klein normaal
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, std=0.02)

    def forward(self, tokens, family, charge, mult, mask):
        omega = tokens[..., 0]                                               # ω/1000 staat vooraan in het token
        h, full_mask = self.embed(tokens, charge, mult, mask)                # invoerlaag
        ctx = self.backbone(h, full_mask)                                    # verborgen lagen
        ctx_modes = ctx[:, 2:]                                               # de molecuul-tokens hebben hun werk gedaan
        return {
            "block": self.block_head(ctx_modes, omega, family, mask),        # uitvoerlaag 1
            "pair_logits": self.pair_head(ctx_modes, omega, mask),           # uitvoerlaag 2
            "context": ctx_modes,                                            # voor diagnose en E-serie-achtige toetsen
        }

    def n_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ----------------------------------------------------------------------------------------------
# Verliesfuncties (de vorm ligt vast; de wegingen per familie komen uit het foutbudget van blad 1)
# ----------------------------------------------------------------------------------------------
def block_loss(pred_block, target_block, family, mask, family_weight=None):
    """Gemiddelde kwadratische fout over de gevulde blokelementen (binnen familie, binnen molecuul),
    optioneel gewogen per familie met 1/marge² uit het foutbudget. Diagonaal en koppelingen tellen
    beide mee: dat is de blokregel van 19 september."""
    same = (family[:, :, None] == family[:, None, :]) & mask[:, :, None] & mask[:, None, :]
    w = same.float()
    if family_weight is not None:                                            # (n_families,) → per element
        w = w * family_weight[family][:, :, None]
    return (w * (pred_block - target_block) ** 2).sum() / w.sum().clamp_min(1.0)


def pair_loss(pair_logits, support, mask, pos_weight):
    """Binaire kruisentropie op de paren, klassegewogen naar de prevalentie in de trainingsset
    (les van E5: ongewogen leert het netwerk alleen de bias, omdat 98 % van de paren nul is)."""
    valid = mask[:, :, None] & mask[:, None, :]
    loss = F.binary_cross_entropy_with_logits(pair_logits, support.float(), pos_weight=pos_weight, reduction="none")
    return (loss * valid).sum() / valid.sum().clamp_min(1.0)


# ----------------------------------------------------------------------------------------------
# Ensemble: leden met verschillende seeds; gemiddelde en spreiding per element
# ----------------------------------------------------------------------------------------------
class DeltaHEnsemble(nn.Module):
    """Bundel van getrainde leden. Geeft per blokelement het gemiddelde (de voorspelling) en de
    standaardafwijking over de leden (de ruwe onzekerheid; de kalibratie van blad 3 schaalt die)."""

    def __init__(self, members: list[DeltaHModel]):
        super().__init__()
        self.members = nn.ModuleList(members)

    @torch.no_grad()
    def forward(self, tokens, family, charge, mult, mask):
        outs = [m(tokens, family, charge, mult, mask) for m in self.members]
        blocks = torch.stack([o["block"] for o in outs])                     # (E, B, M, M)
        probs = torch.stack([torch.sigmoid(o["pair_logits"]) for o in outs])
        return {
            "block_mean": blocks.mean(0), "block_std": blocks.std(0, unbiased=False),
            "pair_prob": probs.mean(0), "pair_prob_std": probs.std(0, unbiased=False),
        }


def make_ensemble(cfg: DeltaHConfig | None = None) -> DeltaHEnsemble:
    cfg = cfg or DeltaHConfig()
    members = []
    for s in cfg.seeds:
        torch.manual_seed(s)
        members.append(DeltaHModel(cfg))
    return DeltaHEnsemble(members)


# ----------------------------------------------------------------------------------------------
# Rooktest: vormen en parametertelling op willekeurige invoer (geen data, geen training)
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    torch.set_num_threads(1)
    cfg = DeltaHConfig()
    model = DeltaHModel(cfg)
    B, M = 2, 48                                                             # twee moleculen, opgevuld tot 48 modi (naftaleen)
    tokens = torch.rand(B, M, cfg.d_in); tokens[..., 0] = torch.rand(B, M) * 3.2  # ω/1000 in [0, 3.2]
    family = torch.randint(0, cfg.n_families, (B, M))
    charge = torch.tensor([0, 1]); mult = torch.tensor([1, 2])                # neutraal singlet, kation doublet
    mask = torch.ones(B, M, dtype=torch.bool); mask[0, 30:] = False           # molecuul 0 heeft 30 modi (benzeen)
    out = model(tokens, family, charge, mult, mask)
    blk = out["block"]
    assert blk.shape == (B, M, M) and torch.allclose(blk, blk.transpose(1, 2), atol=1e-6), "blok niet symmetrisch"
    assert blk[0, 30:].abs().sum() == 0 and blk[0, :, 30:].abs().sum() == 0, "opvulling lekt in het blok"
    same = family[:, :, None] == family[:, None, :]
    assert (blk * ~same).abs().sum() == 0, "koppeling buiten de familie"
    target = torch.zeros_like(blk); support = torch.zeros(B, M, M, dtype=torch.bool)
    l1 = block_loss(blk, target, family, mask); l2 = pair_loss(out["pair_logits"], support, mask, pos_weight=torch.tensor(50.0))
    (l1 + l2).backward()
    ens = make_ensemble(cfg); eo = ens(tokens, family, charge, mult, mask)
    print(f"ΔH-model: {model.n_parameters():,} parameters (d_in {cfg.d_in}, d_model {cfg.d_model}, "
          f"{cfg.n_layers} lagen, {cfg.n_heads} heads); block {tuple(blk.shape)}, pair {tuple(out['pair_logits'].shape)}; "
          f"ensemble van {len(ens.members)}: block_mean {tuple(eo['block_mean'].shape)}, block_std mean {eo['block_std'].mean():.3f}; "
          f"loss blok {l1.item():.3f}, paar {l2.item():.3f}; backward ok")
