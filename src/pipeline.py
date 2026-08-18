from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data_loader import get_processed_data_dir, load_blood_pressure_data, load_cholesterol_data, load_demo_data, load_retired_data
from .data_quality import (
    completeness_percentage_by_column,
    dataset_shape,
    duplicate_row_count,
    duplicate_seqn_count,
    engineered_feature_completeness,
    join_coverage,
    missing_values_by_column,
    total_respondents,
)
from .feature_engineering import (
    create_age_at_exam,
    create_age_at_screening,
    create_highest_education,
    fill_retired,
    fill_retired_for_exam_cohort,
)


ANALYSIS_READY_OUTPUT = "health_features_exam_cohort.csv"
NOTEBOOK_EQUIVALENT_OUTPUT = "health_features_notebook_equivalent.csv"
DATA_QUALITY_REPORT_OUTPUT = "data_quality_report.csv"
ENGINEERED_FEATURE_COLUMNS = ["AGE_AT_SCREENING", "AGE_AT_EXAM", "HIGHEST_EDUCATION", "RETIRED"]
SOURCE_QUALITY_COLUMNS = ["RIDAGEMN", "RIDAGEEX", "RIDAGEYR", "DMDEDUC3", "DMDEDUC2", "RETIRED"]
REQUIRED_ENGINEERED_COLUMNS = {
    "AGE_AT_SCREENING",
    "AGE_AT_EXAM",
    "EDUC_FROM_DMDEDUC3",
    "EDUC_FROM_DMDEDUC2",
    "HIGHEST_EDUCATION",
}


def validate_seqn_exists(df: pd.DataFrame, label: str) -> None:
    if "SEQN" not in df.columns:
        raise ValueError(f"{label} is missing required key column SEQN.")


def validate_engineered_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_ENGINEERED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Engineered dataset is missing expected columns: {missing}")


def validate_analysis_ready_dataset(df: pd.DataFrame) -> None:
    validate_seqn_exists(df, "Analysis-ready dataset")
    if duplicate_seqn_count(df) != 0:
        raise ValueError("Analysis-ready dataset contains duplicate SEQN values.")
    _ = engineered_feature_completeness(df, ENGINEERED_FEATURE_COLUMNS)


def load_raw_datasets() -> dict[str, pd.DataFrame]:
    datasets = {
        "demo": load_demo_data(),
        "bp": load_blood_pressure_data(),
        "chol": load_cholesterol_data(),
        "retired": load_retired_data(),
    }
    for label, df in datasets.items():
        validate_seqn_exists(df, label.upper())
    return datasets


def build_demo_bp_population(demo: pd.DataFrame, bp: pd.DataFrame) -> pd.DataFrame:
    return demo.merge(bp, on="SEQN", how="inner")


def build_exam_population(demo: pd.DataFrame, bp: pd.DataFrame, chol: pd.DataFrame) -> pd.DataFrame:
    demo_bp_df = build_demo_bp_population(demo, bp)
    exam_df = demo_bp_df.merge(chol, on="SEQN", how="inner")
    validate_seqn_exists(exam_df, "Exam cohort")
    return exam_df


def engineer_features(exam_df: pd.DataFrame) -> pd.DataFrame:
    validate_seqn_exists(exam_df, "Exam cohort")
    df = exam_df.copy()
    df["RIDAGEYR"] = df["RIDAGEYR"].astype("int64")
    df["AGE_AT_SCREENING"] = create_age_at_screening(df)
    df["AGE_AT_EXAM"] = create_age_at_exam(df)
    df = create_highest_education(df)
    validate_engineered_columns(df)
    return df


def build_analysis_ready_exam_cohort(feature_df: pd.DataFrame, retired_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    analysis_ready = feature_df.merge(retired_df, on="SEQN", how="left")
    validate_seqn_exists(analysis_ready, "Analysis-ready merge")
    missing_before_fill = int(analysis_ready["RETIRED"].isna().sum())
    analysis_ready["RETIRED"] = fill_retired_for_exam_cohort(analysis_ready)
    validate_analysis_ready_dataset(analysis_ready)
    return analysis_ready, missing_before_fill


def build_notebook_equivalent_dataset(feature_df: pd.DataFrame, retired_df: pd.DataFrame) -> pd.DataFrame:
    # Notebook-equivalent output retained for lineage and reproducibility.
    notebook_df = feature_df.merge(retired_df, on="SEQN", how="outer")
    notebook_df["RETIRED"] = fill_retired(notebook_df)
    return notebook_df


def calculate_retirement_relationship(demo_df: pd.DataFrame, exam_df: pd.DataFrame, retired_df: pd.DataFrame) -> dict[str, object]:
    demo_ids = set(demo_df["SEQN"])
    exam_ids = set(exam_df["SEQN"])
    retired_missing_ids = set(retired_df.loc[retired_df["RETIRED"].isna(), "SEQN"])
    non_exam_ids = demo_ids - exam_ids
    non_missing_retired_ids = set(retired_df.loc[retired_df["RETIRED"].notna(), "SEQN"])

    return {
        "missing_retired_respondents": len(retired_missing_ids),
        "respondents_absent_from_exam_cohort": len(non_exam_ids),
        "intersection_missing_retired_and_non_exam": len(retired_missing_ids & non_exam_ids),
        "missing_retired_present_in_exam_cohort": len(retired_missing_ids & exam_ids),
        "non_exam_with_non_missing_retired": len(non_missing_retired_ids & non_exam_ids),
        "missing_retired_set_equals_non_exam_set": retired_missing_ids == non_exam_ids,
    }


def write_output(df: pd.DataFrame, filename: str) -> Path:
    output_path = get_processed_data_dir() / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    if not output_path.exists():
        raise FileNotFoundError(f"Expected output file was not written: {output_path}")
    return output_path


def _report_row(
    section: str,
    metric: str,
    column: str,
    before_value: object = "",
    after_value: object = "",
    value: object = "",
    notes: str = "",
) -> dict[str, object]:
    return {
        "section": section,
        "metric": metric,
        "column": column,
        "before_value": before_value,
        "after_value": after_value,
        "value": value,
        "notes": notes,
    }


def build_data_quality_report(
    raw: dict[str, pd.DataFrame],
    demo_bp_df: pd.DataFrame,
    exam_df: pd.DataFrame,
    analysis_ready_df: pd.DataFrame,
    notebook_df: pd.DataFrame,
    exam_retired_imputations: int,
    relationship: dict[str, object],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    lineage = [
        ("DEMO", raw["demo"]),
        ("DEMO + BPX", demo_bp_df),
        ("DEMO + BPX + TCHOL", exam_df),
        ("Analysis-ready exam cohort + RETIRED", analysis_ready_df),
        ("Notebook-equivalent outer merge", notebook_df),
    ]
    for label, df in lineage:
        shape = dataset_shape(df)
        rows.append(_report_row("population_lineage", "rows", "", value=shape["rows"], notes=label))
        rows.append(_report_row("population_lineage", "columns", "", value=shape["columns"], notes=label))
        rows.append(_report_row("population_lineage", "respondents", "SEQN", value=total_respondents(df), notes=label))

    join_pairs = [
        ("DEMO vs BPX", raw["demo"], raw["bp"]),
        ("DEMO+BPX vs TCHOL", demo_bp_df, raw["chol"]),
        ("Exam cohort vs RETIRED", exam_df, raw["retired"]),
    ]
    for label, left, right in join_pairs:
        coverage = join_coverage(left, right)
        rows.append(_report_row("join_coverage", "matched_seqn", "SEQN", value=coverage["matched"], notes=label))
        rows.append(_report_row("join_coverage", "left_only_seqn", "SEQN", value=coverage["left_only"], notes=label))
        rows.append(_report_row("join_coverage", "right_only_seqn", "SEQN", value=coverage["right_only"], notes=label))

    duplicate_targets = [
        ("DEMO_D.csv", raw["demo"]),
        ("BPX_D.csv", raw["bp"]),
        ("TCHOL_D.csv", raw["chol"]),
        ("DEMO_RETIRED.CSV.xls", raw["retired"]),
        ("DEMO + BPX", demo_bp_df),
        ("DEMO + BPX + TCHOL", exam_df),
        ("Analysis-ready exam cohort", analysis_ready_df),
        ("Notebook-equivalent output", notebook_df),
    ]
    for label, df in duplicate_targets:
        rows.append(_report_row("duplicates", "duplicate_rows", "", value=duplicate_row_count(df), notes=label))
        rows.append(_report_row("duplicates", "duplicate_seqn", "SEQN", value=duplicate_seqn_count(df), notes=label))

    source_before = exam_df.merge(raw["retired"], on="SEQN", how="left")
    source_missing = missing_values_by_column(source_before[SOURCE_QUALITY_COLUMNS])
    source_complete = completeness_percentage_by_column(source_before[SOURCE_QUALITY_COLUMNS])
    engineered_missing = missing_values_by_column(analysis_ready_df[ENGINEERED_FEATURE_COLUMNS])
    engineered_complete = completeness_percentage_by_column(analysis_ready_df[ENGINEERED_FEATURE_COLUMNS])

    for column in SOURCE_QUALITY_COLUMNS:
        after_missing = int(engineered_missing[column]) if column == "RETIRED" else ""
        after_pct = float(engineered_complete[column]) if column == "RETIRED" else ""
        rows.append(
            _report_row(
                "source_field_quality",
                "missing_values",
                column,
                before_value=int(source_missing[column]),
                after_value=after_missing,
                notes="Analysis-ready exam cohort source fields before/after transformation",
            )
        )
        rows.append(
            _report_row(
                "source_field_quality",
                "completeness_pct",
                column,
                before_value=float(source_complete[column]),
                after_value=after_pct,
                notes="Analysis-ready exam cohort source field completeness",
            )
        )

    for column in ENGINEERED_FEATURE_COLUMNS:
        before_missing = int(source_missing[column]) if column == "RETIRED" else ""
        before_pct = float(source_complete[column]) if column == "RETIRED" else ""
        rows.append(
            _report_row(
                "engineered_field_quality",
                "missing_values",
                column,
                before_value=before_missing,
                after_value=int(engineered_missing[column]),
                notes="Analysis-ready exam cohort engineered feature quality",
            )
        )
        rows.append(
            _report_row(
                "engineered_field_quality",
                "completeness_pct",
                column,
                before_value=before_pct,
                after_value=float(engineered_complete[column]),
                notes="Analysis-ready exam cohort engineered feature completeness",
            )
        )

    rows.append(
        _report_row(
            "engineered_summary",
            "engineered_feature_completeness_score",
            "",
            value=engineered_feature_completeness(analysis_ready_df, ENGINEERED_FEATURE_COLUMNS),
            notes="Non-missing engineered-feature cells divided by total engineered-feature cells",
        )
    )
    rows.append(
        _report_row(
            "engineered_summary",
            "retired_imputations_in_exam_cohort",
            "RETIRED",
            value=exam_retired_imputations,
            notes="Age-65 rule applied only within the analysis-ready exam cohort",
        )
    )

    for metric, value in relationship.items():
        rows.append(
            _report_row(
                "retirement_relationship",
                metric,
                "SEQN",
                value=value,
                notes="Comparison between missing RETIRED respondents and respondents excluded from the exam cohort",
            )
        )

    return pd.DataFrame(rows)


def build_pipeline_outputs() -> dict[str, object]:
    raw = load_raw_datasets()
    demo_bp_df = build_demo_bp_population(raw["demo"], raw["bp"])
    exam_df = build_exam_population(raw["demo"], raw["bp"], raw["chol"])
    feature_df = engineer_features(exam_df)
    analysis_ready_df, exam_retired_imputations = build_analysis_ready_exam_cohort(feature_df, raw["retired"])
    notebook_df = build_notebook_equivalent_dataset(feature_df, raw["retired"])
    relationship = calculate_retirement_relationship(raw["demo"], exam_df, raw["retired"])
    report_df = build_data_quality_report(
        raw=raw,
        demo_bp_df=demo_bp_df,
        exam_df=exam_df,
        analysis_ready_df=analysis_ready_df,
        notebook_df=notebook_df,
        exam_retired_imputations=exam_retired_imputations,
        relationship=relationship,
    )

    analysis_ready_path = write_output(analysis_ready_df, ANALYSIS_READY_OUTPUT)
    notebook_path = write_output(notebook_df, NOTEBOOK_EQUIVALENT_OUTPUT)
    report_path = write_output(report_df, DATA_QUALITY_REPORT_OUTPUT)

    return {
        "raw": raw,
        "demo_bp": demo_bp_df,
        "exam": exam_df,
        "analysis_ready": analysis_ready_df,
        "notebook_equivalent": notebook_df,
        "report": report_df,
        "relationship": relationship,
        "analysis_ready_retired_imputations": exam_retired_imputations,
        "output_paths": {
            "analysis_ready": analysis_ready_path,
            "notebook_equivalent": notebook_path,
            "data_quality_report": report_path,
        },
    }


def main() -> None:
    outputs = build_pipeline_outputs()
    print(f"demo_shape={outputs['raw']['demo'].shape}")
    print(f"demo_bp_shape={outputs['demo_bp'].shape}")
    print(f"exam_population_shape={outputs['exam'].shape}")
    print(f"analysis_ready_shape={outputs['analysis_ready'].shape}")
    print(f"notebook_equivalent_shape={outputs['notebook_equivalent'].shape}")
    print(f"analysis_ready_retired_imputations={outputs['analysis_ready_retired_imputations']}")
    for name, path in outputs["output_paths"].items():
        print(f"{name}_output={path}")


if __name__ == "__main__":
    main()
