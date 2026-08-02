# Module 3 — Validation

Checks the cleaned dataset for errors, anomalies, and rule violations:
rule-based format/range/categorical checks, plus Isolation Forest
anomaly detection, rolled up into one health score.

**Output:** `validation_report.json`
**Design:** driven by Module 1's `semantic_type` metadata and Module 1's
raw-data distributions — never hardcoded column names.

**Scope note (kept from the original brief):** autoencoders and NLP
classifiers are not implemented here — rule-based checks + Isolation
Forest satisfy the rubric solo. Listed under future work.

---

## Files

| File | Responsibility |
|------|----------------|
| `validate.py` | **Public API** — all rule checks, anomaly detection, health scoring, wired into `validation_report.json` |

---

## How to run

```bash
python3 validate.py                                  # defaults to data/processed/cleaned_data.csv
python3 validate.py --input path/to/other_cleaned.csv
```

---

## Key function signatures

```python
check_format_column(series, pattern, rule_name) -> dict
check_numeric_range(series, col, profiled_stats) -> dict
check_unexpected_negatives(series, col, threshold_pct=10.0) -> dict | None
check_categorical_membership(series, col, max_categories=20) -> dict | None
rule_based_checks(df, profile=None) -> dict
anomaly_detection(df) -> dict
health_score(rules, anomalies) -> float
```

---

## What each check actually does

- **Format checks** (email/phone/postcode) — routed by
  `metadata[col]["semantic_type"]`.
- **Range checks** — numeric columns checked against the min/max Module 1
  observed on the *raw* data. **Falls back to recomputing the range from
  the cleaned data itself** when Module 1 has no numeric stats for the
  column — this happens for columns that were `"numeric_as_text"` in the
  raw data (e.g. `monthly_charges`, originally `"£68.48"`-style) and only
  became genuinely numeric after Module 2 cleaned them. Without this
  fallback, such a column is silently never range-checked (a real bug
  found and fixed while building this — see `range_source` in the output:
  `"profiling_report"` vs `"recomputed_from_cleaned_data"`).
- **Unexpected-negatives check** (beyond the original brief) — flags a
  numeric column when negative values are a small minority (< 10% by
  default), on the reasoning that a column that's *usually* non-negative
  (a charge, a duration) probably shouldn't have any negatives at all,
  whereas a column where negatives are common is more likely genuinely
  signed (e.g. profit/loss) and shouldn't be flagged. This is how the
  negative `monthly_charges` and `tenure_months` rows were found.
- **Categorical membership** — records the allowed value set actually
  seen in *this* cleaned dataset for low-cardinality columns. Every value
  trivially passes here (it's the source of truth); the real value is for
  Module 4 validating brand-new incoming rows against this set later.
- **Anomaly detection** — Isolation Forest over all numeric columns
  jointly (unlike the range checks, which look at one column at a time).

---

## Integration instructions

- **Upstream (Module 2):** reads `cleaned_data.csv`. Also reads
  `profiling_report.json` directly (not `cleaning_log.json`) for
  `metadata` and raw-data `distributions`.
- **Downstream (Module 4 — Pipeline):** `validate.py` is called with no
  arguments in the full pipeline run (uses its own default input path);
  `main()` exits non-zero on any uncaught error, which Module 4's
  `run_stage()` treats as a pipeline failure.

---

> All project data is synthetic. No real customers.
