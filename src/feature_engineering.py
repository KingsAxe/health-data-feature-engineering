from __future__ import annotations

import numpy as np
import pandas as pd


DMDEDUC3_MAPPING = {
    0: "ELEMENTARY",
    1: "ELEMENTARY",
    2: "ELEMENTARY",
    3: "ELEMENTARY",
    4: "ELEMENTARY",
    5: "ELEMENTARY",
    6: "ELEMENTARY",
    7: "ELEMENTARY",
    8: "ELEMENTARY",
    9: "ELEMENTARY",
    10: "ELEMENTARY",
    11: "ELEMENTARY",
    12: "ELEMENTARY",
    13: "HIGHSCHOOL",
    14: "HIGHSCHOOL",
    15: "HIGHSCHOOL",
    55: "ELEMENTARY",
    66: "ELEMENTARY",
    77: "ELEMENTARY",
    99: "ELEMENTARY",
}

DMDEDUC2_MAPPING = {
    1: "ELEMENTARY",
    2: "ELEMENTARY",
    3: "HIGHSCHOOL",
    4: "HIGHSCHOOL",
    5: "COLLEGE",
    7: np.nan,
    9: np.nan,
}


def create_age_at_screening(df: pd.DataFrame) -> pd.Series:
    return df["RIDAGEMN"].fillna(df["RIDAGEYR"] * 12)


def create_age_at_exam(df: pd.DataFrame) -> pd.Series:
    # The notebook assumes a 1-month median gap from screening to exam.
    return df["RIDAGEEX"].fillna(df["AGE_AT_SCREENING"] + 1)


def create_highest_education(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EDUC_FROM_DMDEDUC3"] = df["DMDEDUC3"].map(DMDEDUC3_MAPPING)
    df["EDUC_FROM_DMDEDUC2"] = df["DMDEDUC2"].map(DMDEDUC2_MAPPING)
    df["HIGHEST_EDUCATION"] = df["EDUC_FROM_DMDEDUC3"].fillna(df["EDUC_FROM_DMDEDUC2"])

    missing_mask = df["HIGHEST_EDUCATION"].isna()
    df.loc[missing_mask & (df["RIDAGEYR"] <= 17), "HIGHEST_EDUCATION"] = "ELEMENTARY"
    df.loc[missing_mask & (df["RIDAGEYR"] > 17), "HIGHEST_EDUCATION"] = "HIGHSCHOOL"
    return df


def fill_retired(df: pd.DataFrame) -> pd.Series:
    retired = df["RETIRED"].copy()
    missing_mask = retired.isna()
    retired.loc[missing_mask] = np.where(df.loc[missing_mask, "RIDAGEYR"] >= 65, 1, 0)
    return retired


def fill_retired_for_exam_cohort(df: pd.DataFrame) -> pd.Series:
    """Preserve existing values and apply the notebook rule only within the exam cohort."""
    return fill_retired(df)
