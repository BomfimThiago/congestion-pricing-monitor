# Pre-Registration: NYC Congestion Pricing Causal Impact Analysis

**Author** Thiago Bomfim
**Date registered:** 2026-04-29
**Status:** Registered, analysis not yet begun
**Version:** 1.0

Any change to this document after the "registered" commit must be
recorded as a new version with a dated rationale in
`docs/decisions/`. The git history is the source of truth.

## 1. Background and motivation
On January 5, 2025, New York City activated the first congestion
pricing program in the United States. Vehicles entering Manhattan
south of 60th Street are charged a toll, with the stated goals of
(a) reducing traffic congestion in the Central Business District,
(b) generating revenue for MTA capital projects, and (c) improving
air quality.

Comparable programs in London (2003), Stockholm (2006), and
Singapore (1975, modernized 1998) produced traffic reductions of
roughly 15–30% in the priced zones, with mixed effects on adjacent
areas and transit ridership. NYC's program differs in the maturity
of its transit alternatives and the political contestation
surrounding it, so prior estimates transfer imperfectly.

This analysis estimates the causal effect of the program on a set
of pre-specified outcomes using quasi-experimental methods.

## 2. Research questions

**Primary:**
RQ1. Did congestion pricing causally reduce vehicle travel times
within the Central Business District (CBD) relative to comparable
untreated areas?

**Secondary:**
RQ2. Did the program causally increase subway ridership at stations
serving the CBD?
RQ3. Did the program causally affect air quality (PM2.5, NO2)
within the CBD?

Secondary questions are exploratory and will be reported with
explicit acknowledgment that multiple-comparison corrections apply.

## 3. Hypotheses and directional predictions

H1. CBD vehicle travel speeds increase by 5–15% relative to
control areas. Direction: positive. Magnitude band based on
London (2003) and Stockholm (2006) post-implementation studies.

H2. Subway entries at CBD-adjacent stations increase by 2–8%
relative to control stations. Direction: positive. Magnitude band
reflects NYC's already-high transit mode share, leaving less room
for substitution than European precedents.

H3. PM2.5 in the CBD decreases by 0–10% relative to control areas.
Direction: negative or null. Wide band reflects high background
variance and contribution from non-traffic sources.

I commit to reporting all three even if results contradict the
hypothesized direction.

## 4. Data sources

| Source | Variable | Granularity | Provenance |
|---|---|---|---|
| NYC DOT Real-Time Traffic Speed | segment-level speed | per-segment, ~5 min | NYC Open Data |
| MTA Subway Origin-Destination | entries by station | daily | MTA Open Data |
| NYC TLC Trip Records | taxi/FHV trips | per-trip | NYC TLC |
| EPA AirNow | PM2.5, NO2 | hourly per monitor | EPA |
| NOAA GHCN | temperature, precipitation | daily | NOAA |

All sources are public. Exact API endpoints and pull dates are
recorded in `config/settings.yaml` and logged at ingestion time.

## 5. Treatment definition

**Treatment:** geographic units inside the Manhattan Congestion
Relief Zone (south of 60th Street, excluding FDR Drive and West
Side Highway as specified by MTA).

**Treatment date:** January 5, 2025 (program activation).

**Treatment units:**
- For RQ1: NYC DOT speed segments with both endpoints inside
  the zone polygon.
- For RQ2: subway stations with at least one entrance inside the
  zone.
- For RQ3: EPA monitors inside the zone, plus monitors within
  500m of the zone boundary classified separately.

Polygon boundaries are stored as a versioned GeoJSON in
`config/zones/` and are not modified after registration.

## 6. Control / comparison units

**For RQ1 (DiD):** speed segments in Manhattan north of 96th
Street and in the outer boroughs, weighted to match pre-period
distributions of segment type and average speed.

**For RQ2 (DiD):** subway stations in non-Manhattan boroughs at
similar distance from CBD, with similar pre-period ridership.

**For RQ3 (DiD):** EPA monitors in outer boroughs at comparable
distance from major roadways.

**For synthetic control (RQ1, robustness):** donor pool of
metropolitan areas with no congestion pricing — Boston, Chicago,
Philadelphia, San Francisco, Washington DC, Los Angeles, Seattle.

## 7. Outcome variables

**Primary outcome (RQ1):** mean weekday peak-hour (7–10am, 4–7pm)
travel speed by segment, in mph. Aggregated to monthly means.

**Secondary outcomes:**
- RQ2: mean weekday subway entries per station, monthly.
- RQ3: monthly mean PM2.5 (μg/m³) and NO2 (ppb) per monitor.

**Pre-period:** January 2023 – December 2024 (24 months).
**Post-period:** January 2025 – present.

The choice of 2023 as the pre-period start is to mitigate
COVID-recovery contamination. This is a defensible but not the
only possible choice; sensitivity to a 2022 start is in §10.

## 8. Statistical methods

**Primary (RQ1, RQ2, RQ3):** two-way fixed-effects difference-in-
differences, estimated via OLS with unit and time fixed effects:

  Y_it = α_i + γ_t + β · (Treated_i × Post_t) + ε_it

β is the average treatment effect on the treated (ATT) under the
parallel-trends assumption. Standard errors clustered at the unit
level. Estimation via `linearmodels.PanelOLS`.

**Robustness (RQ1):** synthetic control on Manhattan-wide aggregate
travel speed, donor pool as in §6, fitted on 2023–2024 monthly
data, predictor-importance weights cross-validated on a 2024 holdout.
Estimation via `pysyncon`.

**Pre-trends test:** event-study specification with leads and lags:

  Y_it = α_i + γ_t + Σ_k β_k · 1[t = treatment + k] · Treated_i + ε_it

for k ∈ [−12, +12] months, k = −1 omitted as reference.
Joint F-test on β_k for k < 0 must fail to reject parallel trends
at α = 0.10 for the DiD estimate to be reported as primary;
otherwise it moves to "exploratory" status with explicit caveat.

## 9. Inference and decision rules

- α = 0.05 for primary hypothesis (RQ1, two-sided).
- α = 0.05 with Bonferroni correction across the two secondary
  outcomes for RQ2 and RQ3.
- Report point estimates, 95% CIs, and exact p-values regardless
  of significance.
- "Effect detected" requires both statistical significance and
  point estimate inside the pre-registered magnitude band (§3).
  An estimate that is significant but outside the band is reported
  as "directionally consistent, magnitude inconsistent."

## 10. Robustness checks

Run all of these and report all results, not only those that agree
with the primary estimate:

1. Alternative pre-period start: 2022-01-01 instead of 2023-01-01.
2. Alternative control group: outer-borough segments only, excluding
   upper Manhattan (which may be partially treated via spillover).
3. Alternative outcome aggregation: median instead of mean.
4. Placebo treatment date: January 5, 2024 (one year before actual);
   estimated effect should be near zero.
5. Spatial spillover check: estimate effect on a buffer ring 0–500m
   outside the zone; large negative effects there suggest traffic
   diversion.
6. Synthetic control as primary, DiD as robustness (role reversal).

## 11. Threats to validity

Documented in advance so I cannot claim "I always knew" later:

- **Concurrent shocks.** Other January 2025 events (weather, fuel
  prices, employer return-to-office mandates) can confound. I will
  document the macro environment qualitatively and use the placebo
  test (§10.4) as the main quantitative defense.
- **Anticipation effects.** Behavior may have shifted before
  January 5 in expectation. Event study (§8) inspects December 2024.
- **Spatial spillovers.** Traffic may divert to control areas,
  biasing the DiD downward. Buffer-ring analysis (§10.5) addresses.
- **Measurement changes.** Sensor coverage, MTA reporting cadence,
  or EPA monitor calibration may have changed. Validation layer
  flags discontinuities.
- **Selection into treatment is fixed (geographic).** This is a
  strength versus typical observational settings.

## 12. What would change my mind

I commit, before seeing results, that I will revise my belief that
the program "worked" if:

- The placebo test (§10.4) shows an effect of similar magnitude.
- The pre-trends test (§8) rejects parallel trends.
- DiD and synthetic control disagree by more than 50% in magnitude.
- The buffer-ring analysis shows spillovers larger than the
  primary effect.

If any of these occurs, the writeup leads with the failure, not
with the headline estimate.

## 13. Deliverables

1. This pre-registration (frozen on commit).
2. Reproducible pipeline: `make data && make analysis`.
3. Public dashboard updated monthly via GitHub Actions.
4. Final writeup in `docs/findings.md`, structured as:
   decision → recommendation → estimate → method → limitations.

## 14. What I am NOT doing

Stated explicitly to prevent scope creep:

- No predictive modeling. This is a causal project.
- No individual-level data. Aggregates only.
- No policy recommendations beyond what the estimates support.
- No claims about welfare, equity, or distribution without the
  microdata required to support them.