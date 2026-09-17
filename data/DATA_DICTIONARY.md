# Data Dictionary

## sightings.csv

One row per aggregated sighting (all witness reports of the same underlying event, real or fake,
already merged). Fully labeled — every row has `verification_status` and `is_verified`, whether
`split` says `train` or `test`. This is a Dataset, not a Competition: there's no backend to hide an
answer key behind, so `split` is a suggested, methodologically fair (stratified) partition for your
own held-out evaluation, not a withheld label. Use it or ignore it.

| Column | Type | Description | Range / Notes |
|---|---|---|---|
| `sighting_id` | string | Unique ID | `SPY_########` |
| `split` | string | Suggested train/test partition, stratified on `verification_status` | `train` or `test` |
| `timestamp` | datetime | Time of the *earliest witness report* of this sighting (not necessarily the exact true event time — realistic reporting delay is baked in) | |
| `latitude`, `longitude` | float | Averaged, noise-including reported location | Always inside the labeled borough's polygon |
| `borough`, `district` | string | Administrative area | 5 boroughs, ~50 districts total |
| `h3_cell` | string | H3 resolution-8 cell ID | |
| `report_type` | string | Claimed activity | `street`, `stationary`, `rooftop`, `swinging`, `rescue`, `crime_response`, `pursuit` |
| `witness_count` | int | Number of individual reports aggregated into this sighting | ≥ 0 |
| `unique_source_count` | int | Number of distinct witnesses | ≤ `witness_count` |
| `tracker_confidence` | float | Tracker system's own imperfect confidence score | 0–1. **Not the label** — deliberately noisy, can be outperformed |
| `photo_evidence`, `video_evidence`, `audio_evidence` | bool | Any report of this sighting included that evidence type | |
| `mean_photo_quality` | float | Mean photo quality across reports with a photo | 0–1, `NaN` when `photo_evidence` is false |
| `web_residue_found` | bool | Online trace of this sighting exists | |
| `police_report_linked` | bool | A police report references this sighting | |
| `crime_nearby` | bool | A crime was found within ~3 km / 90 min of this sighting | |
| `nearest_crime_id` | string | ID into `crime_incidents.csv` | `NaN` if none found — *not necessarily the true cause* of the sighting, just the nearest match |
| `distance_to_nearest_crime_m` | float | Distance to that crime | meters |
| `minutes_from_nearest_crime` | float | Sighting time minus crime time | can be **negative** (sighting logged before the crime — see Classified Mission) |
| `estimated_speed_kmh` | float | Mean witness-estimated speed | `NaN` when activity is `stationary` |
| `estimated_altitude_m` | float | Mean witness-estimated altitude | `NaN` for `street`/`stationary` |
| `movement_direction` | string | Compass direction | `N`,`NE`,`E`,`SE`,`S`,`SW`,`W`,`NW` |
| `weather_condition` | string | `clear`,`cloudy`,`rain`,`storm`,`snow`,`fog` | |
| `visibility_m` | float | Synthetic weather visibility | |
| `crowd_density_score` | float | District-level exposure proxy | 0–1 |
| `report_source` | string | Most common channel among this sighting's reports | `mobile_app`,`police_scanner`,`camera_network`,`anonymous_tip`,`social_media`,`news_report` |
| `location_spread_m` | float | How much individual reports disagreed on location | meters |
| `median_report_delay_s` | float | Median seconds between event and report | |
| `verification_status` | string | **Target (multiclass).** `verified`, `mistaken_identity`, `impersonator`, `social_media_hoax`, `duplicate_report`, `sensor_error`, `deliberate_fake` | published for every row |
| `is_verified` | int | **Target (binary).** 1 if `verification_status == verified` | published for every row |

## crime_incidents.csv

| Column | Type | Description |
|---|---|---|
| `crime_id` | string | Unique ID (`CRM_########`) |
| `timestamp`, `date`, `hour`, `time_of_day` | | When it happened |
| `latitude`, `longitude`, `borough`, `district`, `h3_cell` | | Where |
| `crime_type` | string | `robbery`, `assault`, `vehicle_theft`, `burglary`, `armed_robbery`, `pursuit`, `property_damage`, `suspicious_activity`, `major_incident` |
| `severity_score` | float | 1–10 |
| `victim_count` | int | ≥ 0 |
| `weapon_reported` | bool | |
| `police_called` | bool | |
| `estimated_police_eta_min` | float | |
| `public_visibility_score` | float | 0–1 |
| `is_decoy_event` | bool | Internal simulation flag (never a hero-response candidate); not required for any published mission |

## locations.csv

One row per district. `zone_id`, `borough`, `district`, `h3_cell`, `centroid_lat`, `centroid_lon`,
and five 0–1 scores: `population_density_score`, `nightlife_score`, `commercial_score`,
`residential_score`, `patrol_activity_score`.

## weather.csv

Synthetic hourly weather, one row per (date, hour): `weather_id`, `date`, `hour`, `temperature_c`,
`precipitation_mm`, `wind_kmh`, `visibility_m`, `cloud_cover`, `condition`.

## witnesses_public.csv

One row per witness who filed at least one report: `witness_id`, `home_borough`, `total_reports`,
`reports_with_photo`, `avg_statement_certainty`, `preferred_report_channel`. Deliberately excludes
any "later verified/rejected" outcome statistic — even a same-day cumulative version of that field
is a label-leakage trap for the classification challenge.

## forecast_sequences.csv

Wide-format sliding windows over **verified** sightings only, ordered by time. Each row is one
sequence of 5 historical points plus the target next point — published for every row, same
reasoning as `sightings.csv`'s `split` column above.

| Column pattern | Description |
|---|---|
| `sequence_id` | Unique ID (`SEQ_#######`) |
| `split` | Suggested train/test partition — **temporal**, not random: every `train` row's target timestamp is before every `test` row's. Sequences whose target falls in the last ~20% of the timeline are `test`. |
| `hist_t-5_lat`, `hist_t-5_lon`, `hist_t-5_hours_before_target` | Oldest point in the window |
| ... | ... (`t-4` through `t-1`, most recent) |
| `target_timestamp`, `target_latitude`, `target_longitude` | The point to predict — published for every row |
