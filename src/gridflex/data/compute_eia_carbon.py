from pathlib import Path

import pandas as pd

# Lifecycle emission factors in gCO2/kWh (IPCC-style median values)
FACTORS = {
    "COL": 820,
    "NG": 490,
    "OIL": 650,
    "NUC": 12,
    "SUN": 45,
    "WND": 11,
    "WAT": 24,
    "GEO": 38,
}
RENEWABLE = ["SUN", "WND", "WAT", "GEO"]

df = pd.read_parquet("data/processed/eia_fuel.parquet")
df = df[df["fuel"].isin(FACTORS)].copy()
df["generation_mwh"] = df["generation_mwh"].clip(lower=0)
df["emissions"] = df["generation_mwh"] * df["fuel"].map(FACTORS)
df["renewable"] = df["generation_mwh"].where(df["fuel"].isin(RENEWABLE), 0)

grouped = (
    df.groupby(["region", "time"])
    .agg(
        emissions=("emissions", "sum"),
        generation=("generation_mwh", "sum"),
        renewable=("renewable", "sum"),
    )
    .reset_index()
)
grouped = grouped[grouped["generation"] > 0]
grouped["carbon_intensity"] = grouped["emissions"] / grouped["generation"]
grouped["renewable_share"] = grouped["renewable"] / grouped["generation"]

demand = pd.read_parquet("data/processed/eia_demand.parquet")
out_df = grouped.merge(demand, on=["region", "time"], how="inner")
out_df = out_df[["time", "region", "carbon_intensity", "renewable_share", "demand_mwh"]]

out = Path("data/processed/eia_carbon.parquet")
out_df.to_parquet(out, index=False)
print(out_df.shape, "saved to", out)
print(out_df.groupby("region")[["carbon_intensity", "renewable_share"]].describe().T)
