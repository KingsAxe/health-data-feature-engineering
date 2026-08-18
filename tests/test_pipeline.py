from pathlib import Path

from src.data_loader import load_blood_pressure_data, load_cholesterol_data, load_demo_data, load_retired_data
from src.pipeline import (
    ANALYSIS_READY_OUTPUT,
    DATA_QUALITY_REPORT_OUTPUT,
    NOTEBOOK_EQUIVALENT_OUTPUT,
    build_analysis_ready_exam_cohort,
    build_demo_bp_population,
    build_exam_population,
    build_pipeline_outputs,
    engineer_features,
)


def test_required_raw_datasets_load():
    demo = load_demo_data()
    bp = load_blood_pressure_data()
    chol = load_cholesterol_data()
    retired = load_retired_data()

    assert not demo.empty
    assert not bp.empty
    assert not chol.empty
    assert not retired.empty
    assert "SEQN" in demo.columns
    assert "SEQN" in bp.columns
    assert "SEQN" in chol.columns
    assert "SEQN" in retired.columns


def test_exam_cohort_can_be_created():
    demo = load_demo_data()
    bp = load_blood_pressure_data()
    chol = load_cholesterol_data()

    demo_bp = build_demo_bp_population(demo, bp)
    exam = build_exam_population(demo, bp, chol)

    assert len(demo_bp) == 9950
    assert len(exam) == 8086
    assert exam["SEQN"].duplicated().sum() == 0


def test_engineered_features_exist_and_are_complete():
    demo = load_demo_data()
    bp = load_blood_pressure_data()
    chol = load_cholesterol_data()
    retired = load_retired_data()

    exam = build_exam_population(demo, bp, chol)
    features = engineer_features(exam)
    analysis_ready, _ = build_analysis_ready_exam_cohort(features, retired)

    for column in ["AGE_AT_SCREENING", "AGE_AT_EXAM", "HIGHEST_EDUCATION", "RETIRED"]:
        assert column in analysis_ready.columns
        assert analysis_ready[column].isna().sum() == 0


def test_pipeline_runs_and_writes_outputs():
    outputs = build_pipeline_outputs()
    analysis_ready = outputs["analysis_ready"]
    notebook_equivalent = outputs["notebook_equivalent"]

    assert analysis_ready["SEQN"].duplicated().sum() == 0
    assert len(analysis_ready) == 8086
    assert len(notebook_equivalent) == 10348

    processed_dir = Path("data/processed")
    assert (processed_dir / ANALYSIS_READY_OUTPUT).exists()
    assert (processed_dir / NOTEBOOK_EQUIVALENT_OUTPUT).exists()
    assert (processed_dir / DATA_QUALITY_REPORT_OUTPUT).exists()
