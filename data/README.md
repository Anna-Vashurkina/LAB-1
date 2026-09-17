# Masked Hero Tracker — Synthetic NYC Geospatial Sightings Dataset

> All incidents, sightings, witness identities and behavioral records in this dataset are
> **synthetically generated** by a seeded simulation. None of it represents real crime victims,
> real eyewitnesses, or real private individuals. Geography is loosely inspired by New York City's
> shape but uses simplified, hand-drawn borough outlines — not official GIS boundaries.

## The story

Thousands of reports of a masked vigilante have been logged across a New York-inspired city over an
18-month period. Some are genuine. Some are honest mistakes. Some are deliberate hoaxes. A few appear
physically impossible. The tracker system that collected them assigns each one a confidence score —
but that score is imperfect, and sometimes wrong in both directions.

Somewhere in the data there's also a pattern nobody has pointed out to you.

## What's inside

This is a Dataset, not a Competition — there's no leaderboard and nothing to submit. Every file is
fully labeled; a `split` column marks a suggested train/test partition (stratified for
`sightings.csv`, temporal for `forecast_sequences.csv`) for anyone who wants a methodologically
fair held-out evaluation, but you're free to ignore it and split however you like.

| File | Rows (approx.) | What it is |
|---|---|---|
| `sightings.csv` | 86K | The main table — every sighting, fully labeled, with a suggested `split` column |
| `crime_incidents.csv` | 46K | Independent crime events across the city |
| `locations.csv` | ~50 | District-level descriptive scores (population, nightlife, commercial, patrol activity) |
| `weather.csv` | ~13K | Synthetic hourly weather, affects visibility and witness counts |
| `witnesses_public.csv` | 27K | Aggregate report history per witness (no future-outcome leakage) |
| `forecast_sequences.csv` | ~50K | Sliding-window sequences of verified sightings for Mission 03, target included |

Full column-by-column reference: `DATA_DICTIONARY.md`.

## Missions

**Mission 01 — Verify the Sighting.** Predict `is_verified` from the other columns in `sightings.csv`
(train on `split == "train"`, check yourself on `split == "test"` — the label's there either way,
this is just our suggested fair partition). Binary classification, metric: F1 (or ROC-AUC). A
baseline RandomForest on the published features scores ~0.86 F1 — there's real room to improve, and
no single column solves it.

**Mission 02 — Verification Status.** Harder multiclass version: predict `verification_status`
(`verified`, `mistaken_identity`, `impersonator`, `social_media_hoax`, `duplicate_report`,
`sensor_error`, `deliberate_fake`). Metric: macro F1. A baseline scores ~0.44 macro F1 — some
subtypes (sensor errors, hoax campaigns) are easy to spot, others are intentionally close to
`verified`.

**Mission 03 — Predict the Next Sighting.** Given a short history of verified sightings from
`forecast_sequences.csv`, predict the next location. Metric: mean Haversine distance (km) between
your prediction and the true next point. "Predict the last known location" is a real baseline
(~5.9 km mean error) — beating it by a meaningful margin takes actual modeling: crime responses
leave a short trail of 2-3 sightings moving in a consistent direction toward one destination, and
patrol movement has a mild directional persistence tick to tick.

**Mission 04 — Detect Impossible Reports.** No column tells you which reports are physically
impossible. A small number of `verified` sightings are paired with a genuinely impossible
transition — but a naive Haversine-speed check between consecutive verified sightings will also
flag plenty of ordinary reporting-delay noise (timestamps aren't perfectly ordered — witnesses
report late, sometimes out of order). The real anomalies concentrate at the extreme end (well
above a few hundred km/h); separating them from noise near the threshold is the actual task.

**Mission 05 — Infer the Hidden Operating Base.** The tracker never reveals where the hero operates
from. Sightings do carry weak clues (late-night location patterns, first/last sighting of the day,
travel times). No ground truth is published for this one — it's an open-ended geospatial puzzle, not
a scored leaderboard.

**Classified Mission — there may be patterns in this dataset that are not immediately obvious.**

## How this was built

Every row traces back to a single seeded Python simulation, not independent random draws. A hidden
state machine decides when the hero responds to a nearby crime (weighing severity, victim count,
distance, and police response time) and moves it around the city under real speed/altitude
constraints; witnesses then *observe* that hidden truth with realistic noise, missingness and
delay; six different fake-report subtypes are generated with their own distinct — but deliberately
overlapping, not perfectly separable — statistical signatures. The generator, full config, and
validation suite are documented in the project repository if you want to see exactly how a column
was produced or generate your own difficulty variant.

## Known limitations

- Borough polygons are simplified/hand-drawn, not official boundaries — expect them to look
  approximately, not exactly, like real NYC.
- `tracker_confidence` is a synthetic, intentionally imperfect score — don't treat it as ground truth.
- The forecasting task uses a wide (one row per sequence) format rather than long/tidy, to keep the
  baseline simple to get started with.
- Mission 05 has no scored answer key in this release; a solution notebook may follow in a later
  version.

## Version history

- **v1.0.0** — initial public release.
