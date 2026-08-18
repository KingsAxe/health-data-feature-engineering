from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
EXAM_DATA_PATH = PROCESSED_DIR / "health_features_exam_cohort.csv"
QUALITY_REPORT_PATH = PROCESSED_DIR / "data_quality_report.csv"


def load_processed_data() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    if not EXAM_DATA_PATH.exists() or not QUALITY_REPORT_PATH.exists():
        return None, None
    return pd.read_csv(EXAM_DATA_PATH), pd.read_csv(QUALITY_REPORT_PATH)


def get_report_value(
    report_df: pd.DataFrame,
    section: str,
    metric: str,
    column: str | None = None,
    notes: str | None = None,
) -> str:
    mask = (report_df["section"] == section) & (report_df["metric"] == metric)
    if column is not None:
        mask &= report_df["column"] == column
    if notes is not None:
        mask &= report_df["notes"] == notes
    matches = report_df.loc[mask]
    if matches.empty:
        return ""
    row = matches.iloc[0]
    return row["value"] if row["value"] != "" else row["after_value"]


def decode_gender(series: pd.Series) -> pd.Series:
    return series.map({1.0: "Male", 2.0: "Female"}).fillna("Unknown")


def decode_race(series: pd.Series) -> pd.Series:
    mapping = {
        1.0: "Mexican American",
        2.0: "Other Hispanic",
        3.0: "Non-Hispanic White",
        4.0: "Non-Hispanic Black",
        5.0: "Other / Multiracial",
    }
    return series.map(mapping).fillna("Unknown")


def plot_missing_comparison(report_df: pd.DataFrame) -> go.Figure:
    rows = report_df[
        (report_df["section"].isin(["source_field_quality", "engineered_field_quality"]))
        & (report_df["metric"] == "missing_values")
    ].copy()
    rows = rows[rows["column"].isin(["RIDAGEMN", "RIDAGEEX", "DMDEDUC3", "DMDEDUC2", "AGE_AT_SCREENING", "AGE_AT_EXAM", "HIGHEST_EDUCATION", "RETIRED"])]
    rows["before_value"] = pd.to_numeric(rows["before_value"], errors="coerce").fillna(0)
    rows["after_value"] = pd.to_numeric(rows["after_value"], errors="coerce").fillna(0)

    fig = go.Figure()
    fig.add_bar(name="Before", x=rows["column"], y=rows["before_value"], marker_color="#93c5fd")
    fig.add_bar(name="After", x=rows["column"], y=rows["after_value"], marker_color="#34d399")
    fig.update_layout(
        barmode="group",
        title="Missing Values Before and After Feature Engineering",
        xaxis_title="Field",
        yaxis_title="Missing values",
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def plot_completeness_comparison(report_df: pd.DataFrame) -> go.Figure:
    rows = report_df[
        (report_df["section"].isin(["source_field_quality", "engineered_field_quality"]))
        & (report_df["metric"] == "completeness_pct")
    ].copy()
    rows = rows[rows["column"].isin(["RIDAGEMN", "RIDAGEEX", "DMDEDUC3", "DMDEDUC2", "AGE_AT_SCREENING", "AGE_AT_EXAM", "HIGHEST_EDUCATION", "RETIRED"])]
    rows["before_value"] = pd.to_numeric(rows["before_value"], errors="coerce").fillna(0)
    rows["after_value"] = pd.to_numeric(rows["after_value"], errors="coerce").fillna(0)

    fig = go.Figure()
    fig.add_bar(name="Before", x=rows["column"], y=rows["before_value"], marker_color="#60a5fa")
    fig.add_bar(name="After", x=rows["column"], y=rows["after_value"], marker_color="#10b981")
    fig.update_layout(
        barmode="group",
        title="Completeness Percentage Before and After Feature Engineering",
        xaxis_title="Field",
        yaxis_title="Completeness (%)",
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def plot_population_lineage(report_df: pd.DataFrame) -> go.Figure:
    rows = report_df[
        (report_df["section"] == "population_lineage")
        & (report_df["metric"] == "rows")
    ].copy()
    rows["value"] = pd.to_numeric(rows["value"], errors="coerce")
    fig = px.funnel(rows, x="value", y="notes", color_discrete_sequence=["#2563eb"])
    fig.update_layout(
        title="Population Lineage",
        xaxis_title="Rows",
        yaxis_title="Stage",
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )
    return fig


def metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label=label, value=value, help=help_text)


def render_overview(exam_df: pd.DataFrame, report_df: pd.DataFrame) -> None:
    st.subheader("Executive Overview")
    st.write(
        "This dashboard reflects the analysis-ready examination cohort. "
        "It uses the 8,086 respondents with demographic, blood pressure, and cholesterol data, "
        "then layers the approved feature-engineering outputs on top."
    )

    completeness_score = get_report_value(report_df, "engineered_summary", "engineered_feature_completeness_score")
    duplicate_seqn = get_report_value(report_df, "duplicates", "duplicate_seqn", "SEQN", "Analysis-ready exam cohort")

    row1 = st.columns(4)
    row2 = st.columns(4)

    with row1[0]:
        metric_card("Total Records", f"{len(exam_df):,}")
    with row1[1]:
        metric_card("Total Features", str(exam_df.shape[1]))
    with row1[2]:
        metric_card("Engineered Feature Completeness", f"{completeness_score}%")
    with row1[3]:
        metric_card("Duplicate Respondents", str(duplicate_seqn))

    with row2[0]:
        metric_card("Missing AGE_AT_SCREENING", str(int(exam_df["AGE_AT_SCREENING"].isna().sum())))
    with row2[1]:
        metric_card("Missing AGE_AT_EXAM", str(int(exam_df["AGE_AT_EXAM"].isna().sum())))
    with row2[2]:
        metric_card("Missing HIGHEST_EDUCATION", str(int(exam_df["HIGHEST_EDUCATION"].isna().sum())))
    with row2[3]:
        metric_card("Missing RETIRED", str(int(exam_df["RETIRED"].isna().sum())))


def render_data_quality(report_df: pd.DataFrame) -> None:
    st.subheader("Data Quality Monitor")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_missing_comparison(report_df), use_container_width=True)
    with col2:
        st.plotly_chart(plot_completeness_comparison(report_df), use_container_width=True)

    lineage_col, dup_col = st.columns([1.5, 1])
    with lineage_col:
        st.plotly_chart(plot_population_lineage(report_df), use_container_width=True)
    with dup_col:
        duplicate_rows = get_report_value(report_df, "duplicates", "duplicate_rows", "", "Analysis-ready exam cohort")
        duplicate_seqn = get_report_value(report_df, "duplicates", "duplicate_seqn", "SEQN", "Analysis-ready exam cohort")
        st.markdown("#### Integrity Checks")
        st.metric("Duplicate Rows", duplicate_rows)
        st.metric("Duplicate SEQN", duplicate_seqn)
        st.caption("The analysis-ready cohort remains unique at the respondent level.")

    st.markdown("#### Before vs After Completeness")
    comparison = report_df[
        report_df["section"].isin(["source_field_quality", "engineered_field_quality"])
    ][["section", "column", "metric", "before_value", "after_value"]].copy()
    st.dataframe(comparison, use_container_width=True, hide_index=True)


def render_feature_engineering(report_df: pd.DataFrame) -> None:
    st.subheader("Feature Engineering Summary")

    with st.expander("AGE_AT_SCREENING", expanded=True):
        st.write("`RIDAGEMN` when available, otherwise `RIDAGEYR × 12`.")

    with st.expander("AGE_AT_EXAM", expanded=True):
        st.write("`RIDAGEEX` when available, otherwise `AGE_AT_SCREENING + 1`.")
        st.caption("The `+1` month fallback is inherited from the original notebook's median time-gap assumption.")

    with st.expander("HIGHEST_EDUCATION", expanded=True):
        st.write(
            "The dashboard uses the notebook's existing consolidation of `DMDEDUC3` and `DMDEDUC2` "
            "into `ELEMENTARY`, `HIGHSCHOOL`, and `COLLEGE`."
        )

    with st.expander("RETIRED", expanded=True):
        imputations = get_report_value(report_df, "engineered_summary", "retired_imputations_in_exam_cohort", "RETIRED")
        st.write("Existing retirement values are preserved.")
        st.info(
            f"Important finding: all 8,086 examination respondents already have a valid retirement value, "
            f"so no retirement imputation was required in the analysis-ready cohort. "
            f"Current imputation count: {imputations}."
        )
        st.caption(
            "The age-65 fallback remains part of the notebook-equivalent lineage output, "
            "but it is not needed for the primary analytical cohort."
        )


def render_demographic_insights(exam_df: pd.DataFrame) -> None:
    st.subheader("Health / Demographic Insights")

    age_fig = px.histogram(
        exam_df,
        x="RIDAGEYR",
        nbins=30,
        color_discrete_sequence=["#2563eb"],
        title="Age Distribution",
    )
    age_fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), xaxis_title="Age in years", yaxis_title="Respondents")

    edu_counts = exam_df["HIGHEST_EDUCATION"].value_counts().reset_index()
    edu_counts.columns = ["HIGHEST_EDUCATION", "count"]
    edu_fig = px.bar(
        edu_counts,
        x="HIGHEST_EDUCATION",
        y="count",
        color="HIGHEST_EDUCATION",
        color_discrete_sequence=["#10b981", "#60a5fa", "#0f766e"],
        title="Highest Education Distribution",
    )
    edu_fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=60, b=20))

    retired_counts = exam_df["RETIRED"].map({0.0: "Not Retired", 1.0: "Retired"}).value_counts().reset_index()
    retired_counts.columns = ["RETIRED_STATUS", "count"]
    retired_fig = px.pie(
        retired_counts,
        names="RETIRED_STATUS",
        values="count",
        color="RETIRED_STATUS",
        color_discrete_map={"Not Retired": "#93c5fd", "Retired": "#34d399"},
        title="Retired Distribution",
    )
    retired_fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))

    gender_edu = exam_df.copy()
    gender_edu["Gender"] = decode_gender(gender_edu["RIAGENDR"])
    gender_edu_fig = px.histogram(
        gender_edu,
        x="Gender",
        color="HIGHEST_EDUCATION",
        barmode="group",
        color_discrete_sequence=["#10b981", "#60a5fa", "#0f766e"],
        title="Education Distribution by Gender",
    )
    gender_edu_fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), yaxis_title="Respondents")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(age_fig, use_container_width=True)
    with col2:
        st.plotly_chart(edu_fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(retired_fig, use_container_width=True)
    with col4:
        st.plotly_chart(gender_edu_fig, use_container_width=True)


def render_methodology(report_df: pd.DataFrame) -> None:
    st.subheader("Methodology & Limitations")

    lineage_rows = report_df[
        (report_df["section"] == "population_lineage") & (report_df["metric"] == "rows")
    ][["notes", "value"]].copy()
    lineage_rows["value"] = pd.to_numeric(lineage_rows["value"], errors="coerce").astype("Int64")

    st.write(
        "The dashboard uses `SEQN` as the respondent join key and treats the 8,086-row examination cohort "
        "as the primary analytical population because those are the respondents with the combined demographic, "
        "blood pressure, and cholesterol data required for this project."
    )
    st.dataframe(lineage_rows, use_container_width=True, hide_index=True)

    st.markdown(
        """
        **Known methodological assumptions**

        - Missing `RIDAGEMN` is filled with `RIDAGEYR × 12`.
        - Missing `RIDAGEEX` is filled with `AGE_AT_SCREENING + 1 month`.
        - The education mapping is inherited from the original notebook.
        - One `DMDEDUC3 = 99` record is currently treated as `ELEMENTARY` under the preserved notebook logic.
        - The notebook-equivalent retirement outer merge is retained separately for lineage and reproducibility.
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Health Data Quality & Feature Engineering Workbench",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Health Data Quality & Feature Engineering Workbench")

    exam_df, report_df = load_processed_data()
    if exam_df is None or report_df is None:
        st.error(
            "Processed outputs are missing. Run `python -m src.pipeline` from the repository root before starting the dashboard."
        )
        st.stop()

    with st.sidebar:
        st.header("Navigation")
        section = st.radio(
            "Go to",
            [
                "Overview",
                "Data Quality",
                "Feature Engineering",
                "Demographic Insights",
                "Methodology",
            ],
        )
        st.caption("Primary analytical source: `health_features_exam_cohort.csv`")

    if section == "Overview":
        render_overview(exam_df, report_df)
    elif section == "Data Quality":
        render_data_quality(report_df)
    elif section == "Feature Engineering":
        render_feature_engineering(report_df)
    elif section == "Demographic Insights":
        render_demographic_insights(exam_df)
    elif section == "Methodology":
        render_methodology(report_df)


if __name__ == "__main__":
    main()
