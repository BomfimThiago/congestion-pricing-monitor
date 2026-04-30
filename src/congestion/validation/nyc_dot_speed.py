"""Validation rules for NYC DOT speed data.

A validation failure stops the pipeline. Better to refuse to run
than to produce a wrong answer silently. Every rule has a reason
documented in the comment.
"""

from datetime import datetime, timedelta, timezone

import polars as pl

from congestion.logging import logger


class ValidationError(Exception):
    """Raised when raw data violates an invariant we depend on."""


def validate_nyc_dot_speed(df: pl.DataFrame) -> None:
    """Check structural and semantic invariants.

    Raises ValidationError on first failure, with a message that
    identifies the rule and a sample of offending rows when useful.
    """
    # Rule 1: non-empty. An empty fetch is almost always a bug
    # (auth failure, endpoint change) masquerading as success.
    if df.is_empty():
        raise ValidationError("nyc_dot_speed: empty dataframe")

    # Rule 2: required columns present. The Socrata endpoint can
    # change shape; we depend on these specific fields downstream.
    required = {"id", "speed", "travel_time", "data_as_of", "link_id"}
    missing = required - set(df.columns)
    if missing:
        raise ValidationError(f"nyc_dot_speed: missing columns {missing}")

    # Rule 3: speed is within physically plausible bounds.
    # NYC speeds outside [0, 80] mph indicate sensor errors or
    # unit confusion (km/h sneaking in).
    speeds = df.select(pl.col("speed").cast(pl.Float64, strict=False))
    bad = speeds.filter((pl.col("speed") < 0) | (pl.col("speed") > 80))
    if bad.height > 0:
        sample = bad.head(3).to_dicts()
        raise ValidationError(
            f"nyc_dot_speed: {bad.height} rows with implausible "
            f"speeds. Sample: {sample}"
        )

    # Rule 4: data freshness. If the most recent timestamp is more
    # than 7 days old, the upstream feed is stale and downstream
    # analysis would be reasoning about old data without knowing it.
    most_recent = df.select(pl.col("data_as_of").str.to_datetime(strict=False)).max().item()
    if most_recent is None:
        raise ValidationError("nyc_dot_speed: could not parse data_as_of")
    age = datetime.now(timezone.utc) - most_recent.replace(tzinfo=timezone.utc)
    if age > timedelta(days=7):
        raise ValidationError(
            f"nyc_dot_speed: feed is stale, most recent record is " f"{age.days} days old"
        )

    logger.info(
        "nyc_dot_speed validation passed: rows={} most_recent={}",
        df.height,
        most_recent,
    )
