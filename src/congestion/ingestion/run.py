"""End-to-end ingestion entrypoint.

Run with: uv run python -m congestion.ingestion.run
"""
import json

import polars as pl

from congestion.config import load_settings
from congestion.ingestion.nyc_dot_speed import fetch_all
from congestion.logging import configure_logging, logger
from congestion.validation.nyc_dot_speed import validate_nyc_dot_speed

def run_nyc_dot_speed() -> None:
    settings = load_settings()
    source = settings.sources["nyc_dot_speed"]

    out_dir = fetch_all(
        source,
        settings.paths.raw,
        since=settings.project.pre_period_start.isoformat(),
    )

    # Concatenate all page files
    all_records = []
    for page_file in sorted(out_dir.glob("page_*.json")):
        all_records.extend(json.loads(page_file.read_text()))

    df = pl.DataFrame(all_records)
    logger.info("loaded {} records from {} pages", df.height, len(list(out_dir.glob("page_*.json"))))

    validate_nyc_dot_speed(df)

    interim_dir = settings.paths.interim / "nyc_dot_speed"
    interim_dir.mkdir(parents=True, exist_ok=True)
    interim_path = interim_dir / "latest.parquet"
    df.write_parquet(interim_path)
    logger.info("wrote interim parquet to {}", interim_path)


if __name__ == "__main__":
    configure_logging()
    run_nyc_dot_speed()