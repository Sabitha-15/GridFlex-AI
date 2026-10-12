import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
REGIONS = ["CISO", "ERCO"]
DAYS = 180
PAGE = 5000


def fetch_region(region, start, end):
    rows = []
    offset = 0
    while True:
        params = {
            "api_key": os.getenv("EIA_API_KEY"),
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": region,
            "start": start,
            "end": end,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": PAGE,
        }
        response = requests.get(URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()["response"]["data"]
        rows.extend(data)
        print(region, "fetched", len(rows), "rows so far")
        if len(data) < PAGE:
            break
        offset += PAGE
    return rows


def main():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS)
    start_str = f"{start:%Y-%m-%dT%H}"
    end_str = f"{end:%Y-%m-%dT%H}"

    frames = []
    for region in REGIONS:
        df = pd.DataFrame(fetch_region(region, start_str, end_str))
        df["time"] = pd.to_datetime(df["period"], format="%Y-%m-%dT%H", utc=True)
        df["generation_mwh"] = pd.to_numeric(df["value"])
        df["region"] = region
        df = df.rename(columns={"fueltype": "fuel"})
        frames.append(df[["time", "region", "fuel", "generation_mwh"]])

    out_df = pd.concat(frames).drop_duplicates(["time", "region", "fuel"])
    out_df = out_df.sort_values(["region", "fuel", "time"])
    out = Path("data/processed/eia_fuel.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(out, index=False)
    print(out_df.shape, "saved to", out)


if __name__ == "__main__":
    main()