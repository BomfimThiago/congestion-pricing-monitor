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

## Decision

Replace the data source. Candidates evaluated below.
Pre-registration §4 will be updated to v1.1 with the new
source documented and this ADR linked.

## Candidates considered

- Uber Movement (archived, free, ceased updates 2024)
- NYC TLC Trip Records (free, monthly, full history)
- MTA Bridge & Tunnel counts (free, full history, coarser)
- INRIX / StreetLight (paid, not viable for this project)

## Decision rationale

[fill in after we discuss below]

## Consequences

- Outcome variable in §7 may need to change
  (e.g., taxi trip duration instead of segment speed)
- Treatment unit definition in §5 may shift from
  road segments to pickup/dropoff zones
- Pre-period and post-period definitions remain valid