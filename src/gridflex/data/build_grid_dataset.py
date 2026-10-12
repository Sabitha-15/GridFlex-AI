from pathlib import Path

import pandas as pd

uk = pd.read_parquet("data/processed/uk_carbon.parquet")
uk = uk.set_index("time")["actual"].resample("1h").mean().rename("carbon_intensity")
uk = uk.reset_index()
uk["region"] = "UK"
uk["renewable_share"] = float("nan")
uk["demand_mwh"] = float("nan")

us = pd.read_parquet("data/processed/eia_carbon.parquet")

cols = ["time", "region", "carbon_intensity", "renewable_share", "demand_mwh"]
df = pd.concat([uk[cols], us[cols]], ignore_index=True)
df = df.dropna(subset=["carbon_intensity"]).sort_values(["region", "time"])

out = Path("data/processed/grid_hourly.parquet")
df.to_parquet(out, index=False)
print(df.shape, "saved to", out)
print(df.groupby("region")["time"].agg(["count", "min", "max"]))
