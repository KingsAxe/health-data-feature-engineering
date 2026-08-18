# Project Overview

## Purpose

This project turns raw healthcare survey and examination data into a reproducible, analysis-ready dataset. The focus is on data quality, feature engineering, transparent transformation rules, and practical reporting rather than on predictive modeling.

## Problem Context

Healthcare and public-health datasets often contain overlapping fields, partial respondent coverage, and missing values across demographic and examination tables. Those issues make downstream analytics harder because analysts first need to answer basic questions:

- Which respondents are actually comparable across all required source files?
- Which fields are incomplete in the raw data?
- Which assumptions were used to derive analysis-ready features?
- Which outputs should be used for reporting versus lineage reproduction?

This repository addresses those questions directly.

## Source Datasets

The workflow uses four real source files:

- `DEMO_D.csv`
- `BPX_D.csv`
- `TCHOL_D.csv`
- `DEMO_RETIRED.CSV.xls`

The retirement file keeps its original filename for traceability, even though its contents are CSV-formatted text.

## Workflow

The project follows a reproducible sequence:

1. Load raw demographic, examination, cholesterol, and retirement files from `data/raw/`.
2. Construct the examination cohort using `SEQN` as the join key.
3. Engineer the approved age, education, and retirement features.
4. Generate two processed outputs:
   - an analysis-ready examination cohort
   - a notebook-equivalent lineage output
5. Generate a reusable data-quality report.
6. Present the results through a Streamlit dashboard.

## Examination Cohort

The project deliberately treats the 8,086-row examination cohort as the primary analytical population:

- `DEMO`: 10,348 respondents
- `DEMO + BPX`: 9,950 respondents
- `DEMO + BPX + TCHOL`: 8,086 respondents

Those 8,086 respondents are the subset with the demographic, blood-pressure, and cholesterol data needed for this workbench.

## Analysis-Ready vs Notebook-Equivalent Outputs

Two processed outputs are preserved for different purposes:

### Analysis-ready output

`health_features_exam_cohort.csv`

- 8,086 respondents
- primary source for the dashboard
- does not introduce respondents who lack the underlying examination data
- engineered features are fully complete in this cohort

### Notebook-equivalent output

`health_features_notebook_equivalent.csv`

- 10,348 respondents
- preserves the original notebook's outer retirement merge
- retained for lineage and reproducibility
- not the preferred dataset for dashboard analysis

## Dashboard Purpose

The dashboard, **Health Data Quality & Feature Engineering Workbench**, provides a readable view of:

- cohort size and completeness
- source-field versus engineered-field quality
- feature-engineering logic
- demographic and retirement distributions
- methodology and limitations

## What This Demonstrates

From a healthcare analytics and IT project-support perspective, the repository demonstrates:

- reproducible data loading
- explicit cohort definition
- documented feature engineering
- auditable transformation rules
- automated data-quality reporting
- stakeholder-friendly dashboard reporting

This makes the project suitable for portfolio review by both technical and non-technical audiences.
