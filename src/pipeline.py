from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data_loader import (
    get_processed_data_dir,
    load_blood_pressure_data,
    load_cholesterol_data,
    load_demo_data,
    load_retired_data,
)
from .feature_engineering import (
    create_age_at_exam,
    create_age_at_screening,
    create_highest_education,
    fill_retired,
)


OUTPUT_FILENAME = "health_features.csv"


def build_exam_population() -> pd.DataFrame:
    demo = load_demo_data()
    bp = load_blood_pressure_data()
    chol = load_cholesterol_data()

    exam_df = demo.merge(bp, on="SEQN", how="inner")
    exam_df = exam_df.merge(chol, on="SEQN", how="inner")
    return exam_df


def engineer_features(exam_df: pd.DataFrame) -> pd.DataFrame:
    df = exam_df.copy()
    df["RIDAGEYR"] = df["RIDAGEYR"].astype("int64")
    df["AGE_AT_SCREENING"] = create_age_at_screening(df)
    df["AGE_AT_EXAM"] = create_age_at_exam(df)
    df = create_highest_education(df)
    return df


def merge_retired_data(df: pd.DataFrame) -> pd.DataFrame:
    retired_df = load_retired_data()

    # This preserves the notebook's outer join, which expands the population
    # beyond the examination cohort and introduces rows missing exam features.
    merged_df = df.merge(retired_df, on="SEQN", how="outer")
    merged_df["RETIRED"] = fill_retired(merged_df)
    return merged_df


def build_pipeline_dataset() -> pd.DataFrame:
    exam_df = build_exam_population()
    feature_df = engineer_features(exam_df)
    return merge_retired_data(feature_df)


def write_processed_dataset(df: pd.DataFrame, output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = get_processed_data_dir() / OUTPUT_FILENAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    dataset = build_pipeline_dataset()
    output_path = write_processed_dataset(dataset)
    print(f"exam_population_shape={build_exam_population().shape}")
    print(f"processed_dataset_shape={dataset.shape}")
    print(f"output_path={output_path}")


if __name__ == "__main__":
    main()
