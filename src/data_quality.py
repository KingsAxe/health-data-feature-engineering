from __future__ import annotations

from typing import Iterable

import pandas as pd


def dataset_shape(df: pd.DataFrame) -> dict[str, int]:
    return {"rows": int(df.shape[0]), "columns": int(df.shape[1])}


def total_respondents(df: pd.DataFrame, key: str = "SEQN") -> int:
    return int(df[key].nunique())


def duplicate_row_count(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())


def duplicate_seqn_count(df: pd.DataFrame, key: str = "SEQN") -> int:
    return int(df[key].duplicated().sum())


def missing_values_by_column(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum().astype(int)


def completeness_percentage_by_column(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(0.0, index=df.columns, dtype="float64")
    return ((1 - df.isna().mean()) * 100).round(2)


def engineered_feature_completeness(df: pd.DataFrame, columns: Iterable[str]) -> float:
    columns = list(columns)
    if not columns:
        raise ValueError("At least one engineered feature column is required.")
    total_cells = df.shape[0] * len(columns)
    if total_cells == 0:
        return 0.0
    non_missing_cells = int(df[columns].notna().sum().sum())
    return round((non_missing_cells / total_cells) * 100, 2)


def join_coverage(left: pd.DataFrame, right: pd.DataFrame, key: str = "SEQN") -> dict[str, int]:
    left_ids = set(left[key])
    right_ids = set(right[key])
    return {
        "left_total": len(left_ids),
        "right_total": len(right_ids),
        "matched": len(left_ids & right_ids),
        "left_only": len(left_ids - right_ids),
        "right_only": len(right_ids - left_ids),
    }
