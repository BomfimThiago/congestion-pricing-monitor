# 0002: Pivot away from NYC DOT real-time speed feed

**Date:** 2026-04-30
**Status:** Accepted
**Supersedes:** None
**Affects:** Pre-registration §4 (data sources), §5 (treatment units), §7 (outcome variables)

## Context

The pre-registration named NYC DOT Real-Time Traffic Speed
(socrata id4gi-tjb9) as the primary data source for RQ1.

Investigation on 2026-04-30 showed the feed retains only a
rolling ~33 days of history (earliest record: 2026-03-28).
The pre-registered pre-period of 2023-01-01 onward is
not retrievable from this source.

## Decision rationale

Selected NYC TLC Trip Record Data (yellow taxi, parquet files
on CloudFront CDN) for the following reasons:

1. Full historical depth: monthly files since 2009, with
   parquet format since May 2022. Covers the entire
   pre-registered analysis window (2023-01 onward).
2. Direct queryability via DuckDB over HTTPS. No local
   ingestion of raw bytes required; aggregation is pushed
   down to the storage layer.
3. Used as the canonical traffic dataset by NYU/Columbia
   researchers studying congestion pricing, providing
   benchmarks for sanity-checking estimates.
4. Two-month publication lag (vendor submission deadline)
   means analysis cutoff is always max_complete_month = today - 2.
   Documented and handled in pipeline.

## Consequences

- Outcome (RQ1) reformulated: from segment-level mean speed
  to trip-level mean duration / derived speed, aggregated
  by taxi zone × month.
- Treatment unit changed: from road segments to TLC taxi
  zones (PULocationID / DOLocationID). CBD zone set
  documented in config/cbd_zones.yaml as analyst judgment
  call (zones substantially south of 60th Street, excluding
  FDR / West Side Highway corridors).
- Spillover analysis (§10.5) now operates on adjacent zones
  rather than buffer rings.
- Yellow taxis only in v1.1; green and HVFHV deferred to
  v1.2 for tractability of initial analysis.
- New post-treatment indicator available: cbd_congestion_fee
  column (2025+). Used as robustness check for treatment
  classification, not as primary definition (column does
  not exist in pre-period).

## Pre-registration changes required

Pre-registration §4, §5, §7, §10.5 require updates.
Bump pre_registration.md to v1.1 in a separate commit
following this ADR.