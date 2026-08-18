# Transformation Rules

## Join Sequence and Population Counts

The project uses `SEQN` as the respondent join key.

Population lineage:

- `DEMO`: 10,348 respondents
- `DEMO + BPX` via inner join on `SEQN`: 9,950 respondents
- `DEMO + BPX + TCHOL` via inner join on `SEQN`: 8,086 respondents

This 8,086-row examination cohort is the primary analytical population.

The notebook-equivalent lineage output also preserves the original retirement outer merge, which expands the result to 10,348 rows.

## AGE_AT_SCREENING

Rule:

- use `RIDAGEMN` when available
- otherwise use `RIDAGEYR × 12`

Meaning:

- produces age at screening in months
- preserves the original notebook methodology exactly

## AGE_AT_EXAM

Rule:

- use `RIDAGEEX` when available
- otherwise use `AGE_AT_SCREENING + 1`

Meaning:

- produces age at examination in months
- the `+1 month` fallback comes directly from the notebook's median screening-to-exam gap assumption

## HIGHEST_EDUCATION

### DMDEDUC3 mapping

- `0–12`, `55`, `66`, `77`, `99` → `ELEMENTARY`
- `13`, `14`, `15` → `HIGHSCHOOL`

### DMDEDUC2 mapping

- `1`, `2` → `ELEMENTARY`
- `3`, `4` → `HIGHSCHOOL`
- `5` → `COLLEGE`
- `7`, `9` → missing

### Combination rule

The project combines the two mapped fields using:

`EDUC_FROM_DMDEDUC3.fillna(EDUC_FROM_DMDEDUC2)`

### Age fallback

If the combined education value is still missing:

- `RIDAGEYR <= 17` → `ELEMENTARY`
- `RIDAGEYR > 17` → `HIGHSCHOOL`

This preserves the original notebook methodology and does not correct the inherited mapping assumptions during this stage.

## RETIRED

### Analysis-ready exam cohort

- existing retirement values are preserved
- no retirement imputation is required in the 8,086-row examination cohort
- every examination respondent already has a non-missing `RETIRED` value

### Notebook-equivalent output

The notebook-equivalent lineage output preserves the original rule:

- keep existing `RETIRED` values
- if missing and `RIDAGEYR >= 65`, set `RETIRED = 1`
- otherwise set `RETIRED = 0`

### Important finding

The 2,262 respondents with missing `RETIRED` values are exactly the same 2,262 respondents outside the examination cohort. That is why the analysis-ready exam cohort requires no retirement imputation while the notebook-equivalent output preserves the original fallback behavior for lineage.
