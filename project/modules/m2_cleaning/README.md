# Module 2 — Data Cleaning

Fixes the dataset after profiling: imputes missing values, removes exact
duplicates, normalises inconsistent formats, and scores data quality
before/after.

**Output:** `cleaned_data.csv` + `cleaning_log.json`
**Design:** driven by Module 1's `profiling_report.json` metadata
(`inferred_type`, `semantic_type`) — never hardcoded column names, so it
stays dataset-agnostic like Module 1.

---

## Files

| File | Responsibility |
|------|----------------|
| `imputation.py` | Missing-value imputation (median/mode, type-aware, identifier columns get a placeholder flag instead of a fabricated value) |
| `clean.py` | **Public API** — duplicate removal, format normalisation, quality scoring, wires everything into `cleaned_data.csv` + `cleaning_log.json` |

---

## How to run

```bash
# Run from the project ROOT (project/), not from inside this folder —
# --input is a relative path resolved against your current directory.
python3 modules/m2_cleaning/clean.py --input data/raw/broadband_customers.csv
```

```python
# As a library
import sys
sys.path.append("modules/m2_cleaning")
sys.path.append("modules")
import pandas as pd
from clean import drop_duplicates, normalise, impute_missing, quality_score
from common import read_json, PROFILING_REPORT

df = pd.read_csv("data/raw/broadband_customers.csv")
profiling_report = read_json(PROFILING_REPORT)   # Module 1 must have run first

df, _ = drop_duplicates(df)
df, _ = normalise(df, report=profiling_report)
df, _ = impute_missing(df, report=profiling_report)
```

---

## Key function signatures

```python
quality_score(df, profile=None) -> float          # completeness+uniqueness, +validity if profile given
drop_duplicates(df) -> (df, log_dict)
normalise(df, report=None) -> (df, log_dict)
impute_missing(df, report=None) -> (df, log_dict)  # thin wrapper around imputation.py
```

---

## What `normalise()` actually fixes

Driven by `metadata[col]["inferred_type"]` / `semantic_type`, not column names:

- **Currency-as-text → float** — only when `semantic_type == "numeric"`.
  A column can ALSO be flagged `"numeric_as_text"` for identifier-like
  data (e.g. `phone`) purely because most values look like digit strings
  — those are deliberately excluded, or coercing them to float would
  destroy leading zeros and identifier meaning.
- **Mixed date shapes → one `datetime64` dtype** — each shape (ISO /
  UK slash / `"Mon YYYY"`) is parsed with its own explicit format string.
  **Do not** switch this to a single `pd.to_datetime(..., dayfirst=True)`
  call — that was tried, and it silently corrupts unambiguous ISO dates
  when they appear alongside UK slash-dates in the same column (see
  `test_iso_dates_not_corrupted_when_mixed_with_uk_slash_dates`).
- **Yes/No-style spelling variants → one label** — detected by value-set
  inspection (a column whose distinct lowercased values are a subset of
  `{yes, y, 1, true, no, n, 0, false}`), not by column name.
- **Invalid identifier values → flagged, not guessed at** — e.g. a phone
  value that doesn't match `UK_PHONE_RE` becomes `"INVALID_PHONE"`, so it
  survives as a visible flag rather than being silently coerced or dropped.

---

## Integration instructions

- **Upstream (Module 1):** reads `profiling_report.json` — specifically
  `metadata` (per-column `inferred_type`/`semantic_type`) and
  `rules.inconsistent_formats` (which columns have mixed date shapes).
- **Downstream (Module 3 — Validation):** reads `cleaned_data.csv`.
  `cleaning_log.json`'s `quality_score_before`/`_after`/`_delta` are
  reported but not re-validated by Module 3 — Module 3 computes its own
  independent health score.
- **Known open item:** negative values found in `monthly_charges` and
  `tenure_months` are intentionally **not** auto-corrected here — that
  requires a business rule this module doesn't have (sign-flip bug?
  legitimate credit? wrong unit?). Module 3 surfaces them for review
  instead of this module silently guessing.

---

> All project data is synthetic. No real customers.