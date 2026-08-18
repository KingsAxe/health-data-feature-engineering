# Assumptions and Limitations

## Age precision

- `RIDAGEYR × 12` is less precise than a true month-level age value.
- It is used only as a fallback when `RIDAGEMN` is missing.

## Exam timing assumption

- `AGE_AT_EXAM = AGE_AT_SCREENING + 1` when `RIDAGEEX` is missing.
- This assumption is inherited from the original notebook methodology and is not independently re-estimated here.

## Education mapping inheritance

- The project preserves the notebook's current education mapping.
- `DMDEDUC3 = 99` is currently treated as `ELEMENTARY`.
- One examination-cohort record is affected by that inherited rule.

## Age-based education fallback

- If education remains missing after combining the mapped source fields, age is used as a fallback:
  - `RIDAGEYR <= 17` → `ELEMENTARY`
  - `RIDAGEYR > 17` → `HIGHSCHOOL`

## Retirement fallback scope

- The age-65 retirement fallback is retained for legacy/notebook reproducibility.
- It is not required in the 8,086-row analysis-ready examination cohort because those respondents already have non-missing retirement values.

## Population choice

- The notebook-equivalent outer merge is preserved for traceability.
- It is not the primary analytical population because it includes respondents who do not have the full examination data used by the project.

## Project scope

- This repository is a data-quality and feature-engineering workbench.
- It does not perform clinical diagnosis, predictive medicine, treatment recommendation, or patient-level outcome inference.
