"""NYC DOT Real-Time Traffic Speed ingestion.

Source: https://data.cityofnewyork.us/Transportation/.../i4gi-tjb9
The endpoint serves rolling real-time data via Socrata's SODA API.
We page through with $limit and $offset and store raw JSON
partitioned by ingestion date.
"""

from datetime import datetime, timezone
from pathlib import Path
import json

import logging
import requests

from congestion.config import SourceConfig
from congestion.logging import logger

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

# tenacity uses stdlib logging, not loguru, so we bridge them
_stdlib_logger = logging.getLogger(__name__)

@retry(
    retry=retry_if_exception_type(
        (requests.Timeout, requests.ConnectionError, requests.HTTPError)
    ),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(_stdlib_logger, logging.WARNING),
    reraise=True,
)
def fetch_page(
    source: SourceConfig,
    offset: int,
    where_clause: str | None = None,
) -> list[dict]:
    """Fetch one page from the SODA endpoint.

    Retries up to 5 times with exponential backoff (2s, 4s, 8s, ...)
    on transient network errors. After 5 failures, the original
    exception is re-raised so the caller can decide what to do.
    """
    params: dict[str, str | int] = {
        "$limit": source.page_size,
        "$offset": offset,
        "$order": "data_as_of DESC",
    }
    if where_clause:
        params["$where"] = where_clause

    logger.info(
        "fetching nyc_dot_speed page offset={} limit={}",
        offset, source.page_size,
    )
    response = requests.get(
        source.url,
        params=params,
        timeout=source.timeout_seconds,
    )
    response.raise_for_status()
    return response.json()

def fetch_all(
    source: SourceConfig,
    raw_dir: Path,
    since: str,
    max_pages: int = 200,
) -> Path:
    """Stream pages to disk as they arrive.

    Each page becomes its own JSON file. If the run dies, pages
    already written are preserved. Re-running skips offsets that
    already have a file on disk (idempotent resume).
    """
    today = datetime.now(timezone.utc).date().isoformat()
    out_dir = raw_dir / "nyc_dot_speed" / f"ingest_date={today}"
    out_dir.mkdir(parents=True, exist_ok=True)

    where_clause = f"data_as_of >= '{since}T00:00:00'"
    logger.info("fetching with filter: {}", where_clause)

    for page in range(max_pages):
        offset = page * source.page_size
        page_path = out_dir / f"page_{offset:09d}.json"

        # Resume: skip pages already on disk
        if page_path.exists():
            logger.info("page already on disk, skipping: {}", page_path.name)
            continue

        records = fetch_page(source, offset, where_clause=where_clause)
        if not records:
            logger.info("no more records at offset={}, stopping", offset)
            break

        # Write immediately, before fetching the next page
        page_path.write_text(json.dumps(records))
        logger.info(
            "wrote page offset={} rows={} to {}",
            offset, len(records), page_path.name,
        )

    return out_dir