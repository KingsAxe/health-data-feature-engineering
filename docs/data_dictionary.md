# Data Dictionary

This dictionary highlights the main source and engineered fields used in the project.

| Field | Source Dataset | Meaning | Role in This Project |
| --- | --- | --- | --- |
| `SEQN` | All source files | Respondent sequence number | Primary join key across all datasets |
| `RIDAGEMN` | `DEMO_D.csv` | Age in months at screening | Primary source for `AGE_AT_SCREENING` |
| `RIDAGEEX` | `DEMO_D.csv` | Age in months at examination | Primary source for `AGE_AT_EXAM` |
| `RIDAGEYR` | `DEMO_D.csv` | Age in years at screening | Fallback for age engineering and age-based logic |
| `RIAGENDR` | `DEMO_D.csv` | Respondent gender code | Used for demographic summaries |
| `RIDRETH1` | `DEMO_D.csv` | Race/ethnicity recode | Used for demographic segmentation |
| `DMDEDUC3` | `DEMO_D.csv` | Education field for younger respondents | Source input to `HIGHEST_EDUCATION` mapping |
| `DMDEDUC2` | `DEMO_D.csv` | Education field for adult respondents | Source input to `HIGHEST_EDUCATION` mapping |
| `DMDSCHOL` | `DEMO_D.csv` | School attendance status | Context field from demographics; preserved in analysis-ready data |
| `BPXCHR` | `BPX_D.csv` | Heart rate | Examination measure retained in the cohort |
| `BPQ150A` | `BPX_D.csv` | Had food in the past 30 minutes | Examination context field retained in the cohort |
| `LBXTC` | `TCHOL_D.csv` | Total cholesterol | Cholesterol measure retained in the cohort |
| `LBDTCSI` | `TCHOL_D.csv` | Converted/imputed cholesterol value | Cholesterol companion field retained in the cohort |
| `AGE_AT_SCREENING` | Engineered | Screening age in months | Completes age-at-screening values for the analysis-ready cohort |
| `AGE_AT_EXAM` | Engineered | Exam age in months | Completes age-at-exam values for the analysis-ready cohort |
| `HIGHEST_EDUCATION` | Engineered | Consolidated education category | Converts overlapping education fields into reporting-friendly categories |
| `RETIRED` | `DEMO_RETIRED.CSV.xls` plus engineering rule | Retirement indicator | Preserved directly in the exam cohort; legacy age-based fallback retained for notebook-equivalent lineage |

## Notes

- `DEMO_RETIRED.CSV.xls` is loaded as CSV content despite its file extension.
- The project does not assign clinical diagnoses or treatment meaning to these fields.
- Engineered features are documented in detail in `docs/transformation_rules.md`.
