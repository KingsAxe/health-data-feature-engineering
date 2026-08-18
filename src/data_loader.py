from __future__ import annotations

from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"


def get_repo_root() -> Path:
    return REPO_ROOT


def get_raw_data_dir() -> Path:
    return RAW_DATA_DIR


def get_processed_data_dir() -> Path:
    return PROCESSED_DATA_DIR


def _resolve_raw_file(filename: str) -> Path:
    path = RAW_DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")
    return path


def load_demo_data() -> pd.DataFrame:
    return pd.read_csv(_resolve_raw_file("DEMO_D.csv"))


def load_blood_pressure_data() -> pd.DataFrame:
    return pd.read_csv(_resolve_raw_file("BPX_D.csv"))


def load_cholesterol_data() -> pd.DataFrame:
    return pd.read_csv(_resolve_raw_file("TCHOL_D.csv"))


def load_retired_data() -> pd.DataFrame:
    # The file extension is misleading; the repository version contains CSV text.
    return pd.read_csv(_resolve_raw_file("DEMO_RETIRED.CSV.xls"))
