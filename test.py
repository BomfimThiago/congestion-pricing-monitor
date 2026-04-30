import polars as pl
from pathlib import Path
import json

# Load whatever you have on disk so far
out_dir = Path("data/raw/nyc_dot_speed").glob("ingest_date=*")
latest_dir = sorted(out_dir)[-1]

all_records = []
for page_file in sorted(latest_dir.glob("page_*.json")):
    all_records.extend(json.loads(page_file.read_text()))

df = pl.DataFrame(all_records)
print(f"Total rows: {df.height:,}")
print(f"Pages on disk: {len(list(latest_dir.glob('page_*.json')))}")

# Question 1: what date range do we actually have?
df = df.with_columns(
    pl.col("data_as_of").str.to_datetime(strict=False)
)
print(df.select(
    pl.col("data_as_of").min().alias("earliest"),
    pl.col("data_as_of").max().alias("latest"),
    pl.col("link_id").n_unique().alias("unique_segments"),
))

# Question 2: how is the data distributed over time?
print(
    df.group_by(pl.col("data_as_of").dt.truncate("1mo").alias("month"))
      .agg(pl.len().alias("rows"))
      .sort("month")
)