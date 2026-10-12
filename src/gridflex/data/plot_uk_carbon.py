from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_parquet("data/processed/uk_carbon.parquet")
df["hour"] = df["time"].dt.hour

last_week = df.tail(48 * 7)
hourly = df.groupby("hour")["actual"].mean()

fig, axes = plt.subplots(2, 1, figsize=(11, 8))

axes[0].plot(last_week["time"], last_week["actual"], label="actual")
axes[0].plot(last_week["time"], last_week["forecast"], label="NESO forecast", alpha=0.7)
axes[0].set_title("UK carbon intensity, last 7 days")
axes[0].set_ylabel("gCO2/kWh")
axes[0].legend()

axes[1].bar(hourly.index, hourly.values)
axes[1].set_title("Average carbon intensity by hour of day (UTC)")
axes[1].set_xlabel("hour")
axes[1].set_ylabel("gCO2/kWh")

plt.tight_layout()
Path("docs").mkdir(exist_ok=True)
plt.savefig("docs/uk_carbon_overview.png", dpi=150)
plt.show()
