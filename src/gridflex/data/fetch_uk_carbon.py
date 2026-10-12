from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

BASE = "https://api.carbonintensity.org.uk/intensity"
DAYS = 180
CHUNK_DAYS = 10


def fetch_range(start, end):
    url = f"{BASE}/{start:%Y-%m-%dT%H:%MZ}/{end:%Y-%m-%dT%H:%MZ}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    rows = []
    for item in response.json()["data"]:
        rows.append(
            {
                "time": item["from"],
                "forecast": item["intensity"]["forecast"],
                "actual": item["intensity"]["actual"],
                "index": item["intensity"]["index"],
            }
        )
    return rows


def main():
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=DAYS)
    rows = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=CHUNK_DAYS), end)
        rows.extend(fetch_range(cursor, chunk_end))
        print(f"fetched {cursor:%Y-%m-%d} to {chunk_end:%Y-%m-%d}")
        cursor = chunk_end

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.drop_duplicates("time").sort_values("time")

    out = Path("data/processed/uk_carbon.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(df.shape, "saved to", out)


if __name__ == "__main__":
    main()
