from pathlib import Path

import pandas as pd
import pytest

PATH = Path("data/processed/grid_hourly.parquet")
pytestmark = pytest.mark.skipif(not PATH.exists(), reason="dataset not built")


def test_regions_present():
    df = pd.read_parquet(PATH)
    assert set(df["region"]) == {"UK", "CISO", "ERCO"}


def test_no_duplicates():
    df = pd.read_parquet(PATH)
    assert not df.duplicated(["time", "region"]).any()


def test_carbon_range():
    df = pd.read_parquet(PATH)
    assert df["carbon_intensity"].between(0, 1000).all()
