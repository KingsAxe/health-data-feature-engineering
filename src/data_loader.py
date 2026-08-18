from __future__ import annotations

from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = REPO_ROOT / "data" / "processed"
REQUIRED_RAW_COLUMNS = {
    "DEMO_D.csv": {
        "SEQN",
        "RIDAGEMN",
        "RIDAGEEX",
        "RIDAGEYR",
        "DMDEDUC3",
        "DMDEDUC2",
    },
    "BPX_D.csv": {"SEQN", "PEASCST1", "PEASCTM1", "PEASCCT1", "BPXCHR", "BPQ150A"},
    "TCHOL_D.csv": {"SEQN", "LBXTC", "LBDTCSI"},
    "DEMO_RETIRED.CSV.xls": {"SEQN", "RETIRED"},
}


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


def validate_required_columns(df: pd.DataFrame, filename: str) -> None:
    required = REQUIRED_RAW_COLUMNS[filename]
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns in {filename}: {missing}")


def _load_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(_resolve_raw_file(filename))
    validate_required_columns(df, filename)
    return df


def load_demo_data() -> pd.DataFrame:
    return _load_csv("DEMO_D.csv")


def load_blood_pressure_data() -> pd.DataFrame:
    return _load_csv("BPX_D.csv")


def load_cholesterol_data() -> pd.DataFrame:
    return _load_csv("TCHOL_D.csv")


def load_retired_data() -> pd.DataFrame:
    # The file extension is misleading; the repository version contains CSV text.
    return _load_csv("DEMO_RETIRED.CSV.xls")
