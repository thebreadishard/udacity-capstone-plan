"""Derive the small band-level inputs the notebook needs from the parser's 51 MB band table (22 September 2026).

`out/theoretical_4.00/bands.csv.gz` (2,517,399 rows, 51 MB) is produced by `build_opponent_atlas.py` from the PAHdb XML and is
too large for the repository, so a fresh clone could not run the notebook (found by the fresh-environment check of 22 September).
This script writes, into `notebook/bands_derived/`, exactly what the notebook's cells compute from that table — the same numbers,
the same random samples (same seed and grouping), the same histograms — so the notebook runs from the repository alone:

- `summary.json`            total rows, rows with non-positive frequency, rows with negative intensity
- `scale_summary.csv`       per stored scale factor: min, max and count of the scaled frequency (all scale values)
- `fig2_samples.csv`        the 4,000-band samples of the unscaled frequency for the six most frequent scale factors (random_state 0)
- `neutral_intensity_hist.csv`  neutral species: summed intensity per 10 cm⁻¹ bin of the scaled position (bins 0–3400)
- `neutral_family_intensity.csv` neutral species: summed intensity per family label
- `uid617_bands.csv`        every band of C384H48 (uid 617)

Run from the module folder after `build_opponent_atlas.py`:  python notebook/make_bands_derived.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out" / "theoretical_4.00"
DER = HERE / "bands_derived"
DER.mkdir(exist_ok=True)

bands = pd.read_csv(OUT / "bands.csv.gz", dtype={"uid": str, "charge": str})
json.dump({"n_rows": int(len(bands)), "n_nonpositive_frequency": int((bands.frequency_cm <= 0).sum()),
           "n_negative_intensity": int((bands.intensity_km_mol < 0).sum()), "source": "out/theoretical_4.00/bands.csv.gz"},
          open(DER / "summary.json", "w"), indent=1)

sc = bands.groupby("scale").frequency_cm.agg(["min", "max", "count"]).sort_values("count", ascending=False)
sc.to_csv(DER / "scale_summary.csv")

sub = bands[bands.scale.isin(sc.head(6).index)]
parts = []
for s_, g in sub.groupby("scale"):
    smp = g.frequency_unscaled_cm.sample(min(len(g), 4000), random_state=0)
    parts.append(pd.DataFrame({"scale": s_, "n_bands": len(g), "frequency_unscaled_cm": smp.to_numpy()}))
pd.concat(parts, ignore_index=True).to_csv(DER / "fig2_samples.csv", index=False)

neutral = bands[bands.charge == "0"]
edges = np.arange(0, 3400, 10)
h, _ = np.histogram(neutral.frequency_cm, bins=edges, weights=neutral.intensity_km_mol)
pd.DataFrame({"bin_left_cm": edges[:-1], "bin_right_cm": edges[1:], "summed_intensity_km_mol": h}).to_csv(DER / "neutral_intensity_hist.csv", index=False)
neutral.groupby("family").intensity_km_mol.sum().sort_values().rename("summed_intensity_km_mol").to_csv(DER / "neutral_family_intensity.csv")

bands[bands.uid == "617"].to_csv(DER / "uid617_bands.csv", index=False)
print("bands_derived written:", sorted(p.name for p in DER.iterdir()), "| rows", len(bands))
