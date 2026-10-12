from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

uk = pd.read_parquet("data/processed/uk_carbon.parquet")
uk = uk.set_index("time")["actual"].resample("1h").mean().rename("carbon_intensity")
uk = uk.reset_index()
uk["region"] = "UK"

us = pd.read_parquet("data/processed/eia_carbon.parquet")
us = us[["time", "region", "carbon_intensity"]]

df = pd.concat([uk, us])
df["hour"] = df["time"].dt.hour
hourly = df.groupby(["region", "hour"])["carbon_intensity"].mean().unstack(0)

ax = hourly.plot(figsize=(10, 5), marker="o")
ax.set_title("Average carbon intensity by hour of day (UTC), three regions")
ax.set_xlabel("hour (UTC)")
ax.set_ylabel("gCO2/kWh")
ax.grid(alpha=0.3)

Path("docs").mkdir(exist_ok=True)
plt.tight_layout()
plt.savefig("docs/region_comparison.png", dpi=150)
plt.show()
