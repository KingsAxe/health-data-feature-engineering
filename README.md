**Health Data Feature Engineering**

Overview
This project focuses on transforming raw healthcare survey datasets into clean, production-ready features suitable for predictive modeling and analytics. The goal is to handle missing values, consolidate overlapping categories, and engineer features that accurately represent respondents’ demographics and statuses.

**Key Tasks and Approaches**

1. AGE_AT_SCREENING & AGE_AT_EXAM

Problem: The existing features RIDAGEMN (age in months at screening) and RIDAGEEX (age at examination) contain missing values.

**Approach:
**
AGE_AT_SCREENING: Use RIDAGEMN when available; for 148 missing cases, convert RIDAGEYR (years) to months (RIDAGEYR * 12) for precision.

AGE_AT_EXAM: Use actual exam age when available; for missing values, impute using the median 1-month gap between screening and exams based on time gap analysis.

Outcome: Generated complete, precise age features for all respondents.

2. HIGHEST_EDUCATION

Problem: Overlapping categorical features (DMDEDUC3, DMDEDUC2) complicated educational level representation.

Approach:

Consolidated categories into ELEMENTARY, HIGHSCHOOL, COLLEGE based on definitions.

Treated ambiguous or missing cases conservatively and used age-based imputation to fill missing values, leveraging the correlation between age and education level.

Outcome: Created a reliable, simplified education feature suitable for modeling.

3. RETIRED

Problem: Binary RETIRED feature has missing values.

Approach:

Used an age-threshold strategy: <65 → not retired, ≥65 → retired, supported by exploratory analysis of valid records.

Analysis confirmed retirement status is strongly age-dependent, minimizing classification error.

Outcome: Completed a high-quality retirement feature aligned with real-world patterns.

**Key Skills & Takeaways**

Data Cleaning & Preprocessing (Python, Pandas)

Missing Data Imputation Strategies (median, transformation, age-based thresholds)

Categorical Feature Consolidation & Mapping

Problem Framing & Critical Thinking

Real-world Data Handling & Feature Engineering

**Next Steps / Applications**

Use these cleaned features for predictive modeling (e.g., diabetes risk, retirement risk analysis).

Serve as a template for high-grade healthcare data reconciliation projects.
