"""
MODULE 3 — DATA VALIDATION
==========================
Check the cleaned dataset for errors, anomalies, and rule violations.

FILE CONTRACT
  Input :  data/processed/cleaned_data.csv  +  outputs/profiling_report.json
  Output:  outputs/validation_report.json
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import write_json, read_json, CLEANED_DATA, VALIDATION_REPORT, PROFILING_REPORT  # noqa: E402

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
UK_PHONE_RE = re.compile(r"^(0|\+44)\d{10}$")
UK_POSTCODE_RE = re.compile(r"^[A-Za-z]{1,2}\d[A-Za-z\d]?\s?\d[A-Za-z]{2}$")

_FORMAT_CHECKS = {"email": EMAIL_RE, "phone": UK_PHONE_RE, "postcode": UK_POSTCODE_RE}


def check_format_column(series: pd.Series, pattern: re.Pattern, rule_name: str) -> dict:
    """How many non-null values match the expected format for this semantic type."""
    non_null = series.dropna().astype(str)
    valid = non_null.str.match(pattern)
    return {
        "rule": f"{rule_name}_format",
        "checked": int(valid.shape[0]),
        "valid": int(valid.sum()),
        "invalid": int((~valid).sum()),
    }


def check_numeric_range(series: pd.Series, col: str, profiled_stats: dict) -> dict:
    """Flag values outside the range Module 1 observed on the RAW data.

    Falls back to computing the range directly from THIS (cleaned) data
    when Module 1's profiling doesn't have numeric stats for the column --
    happens for columns that were "numeric_as_text" in the raw data (e.g.
    "£68.48") and only became genuinely numeric after Module 2 cleaned them.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return {"rule": f"{col}_range", "checked": 0, "valid": 0, "invalid": 0}

    lo, hi = (profiled_stats or {}).get("min"), (profiled_stats or {}).get("max")
    source = "profiling_report"
    if lo is None or hi is None:
        lo, hi = float(s.min()), float(s.max())
        source = "recomputed_from_cleaned_data"

    in_range = s.between(lo, hi)
    return {
        "rule": f"{col}_range",
        "checked": int(in_range.shape[0]),
        "valid": int(in_range.sum()),
        "invalid": int((~in_range).sum()),
        "expected_range": [lo, hi],
        "range_source": source,
    }


def check_unexpected_negatives(series: pd.Series, col: str, threshold_pct: float = 10.0) -> dict | None:
    """Flags numeric columns where negatives are a small MINORITY --
    likely data-entry errors, not a legitimately signed metric.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    n_negative = int((s < 0).sum())
    pct_negative = 100 * n_negative / len(s)
    if n_negative == 0 or pct_negative > threshold_pct:
        return None
    return {
        "rule": f"{col}_unexpected_negatives",
        "checked": int(len(s)),
        "valid": int(len(s) - n_negative),
        "invalid": n_negative,
        "pct_negative": round(pct_negative, 2),
    }


def check_categorical_membership(series: pd.Series, col: str, max_categories: int = 20) -> dict | None:
    """Records the allowed value set seen in the cleaned data, for
    low-cardinality columns -- useful for Module 4 validating new rows later.
    """
    non_null = series.dropna().astype(str)
    n_unique = non_null.nunique()
    if n_unique == 0 or n_unique > max_categories:
        return None
    return {
        "rule": f"{col}_categorical_membership",
        "checked": int(non_null.shape[0]),
        "valid": int(non_null.shape[0]),
        "invalid": 0,
        "allowed_values": sorted(non_null.unique().tolist()),
    }


def rule_based_checks(df: pd.DataFrame, profile: dict | None = None) -> dict:
    """Run format / range / categorical checks, driven by Module 1's
    metadata + distributions -- dataset-agnostic, no hardcoded column names.
    """
    metadata = (profile or {}).get("metadata", {})
    distributions = (profile or {}).get("profiling", {}).get("distributions", {})
    results = {}

    for col in df.columns:
        semantic = metadata.get(col, {}).get("semantic_type")

        if semantic in _FORMAT_CHECKS:
            results[col] = check_format_column(df[col], _FORMAT_CHECKS[semantic], semantic)
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            stats = distributions.get(col, {})
            results[col] = check_numeric_range(df[col], col, stats if stats.get("kind") == "numeric" else {})
            neg_check = check_unexpected_negatives(df[col], col)
            if neg_check:
                results[f"{col}__negatives"] = neg_check
            continue

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        cat_result = check_categorical_membership(df[col], col)
        if cat_result:
            results[col] = cat_result

    return results


def anomaly_detection(df: pd.DataFrame) -> dict:
    """Isolation Forest over numeric columns: flags rows that look
    statistically unusual across ALL numeric features jointly.
    """
    from sklearn.ensemble import IsolationForest

    numeric_df = df.select_dtypes("number").dropna()
    if numeric_df.empty or len(numeric_df) < 10:
        return {"anomalies": 0, "checked": int(len(numeric_df)), "note": "not enough numeric data"}

    model = IsolationForest(contamination=0.05, random_state=42)
    flags = model.fit_predict(numeric_df)
    n_anomalies = int((flags == -1).sum())
    return {
        "checked": int(len(numeric_df)),
        "anomalies": n_anomalies,
        "anomaly_pct": round(100 * n_anomalies / len(numeric_df), 2),
        "columns_used": numeric_df.columns.tolist(),
        "row_indices": numeric_df.index[flags == -1].tolist()[:50],
    }


def health_score(rules: dict, anomalies: dict) -> float:
    """Combine rule pass-rate + anomaly-free-rate into one 0-100 score."""
    total_checked = sum(r.get("checked", 0) for r in rules.values())
    total_valid = sum(r.get("valid", 0) for r in rules.values())
    rule_pass_rate = (total_valid / total_checked) if total_checked else 1.0

    checked = anomalies.get("checked", 0)
    anomaly_free_rate = 1 - (anomalies.get("anomalies", 0) / checked) if checked else 1.0

    return round(100 * (0.7 * rule_pass_rate + 0.3 * anomaly_free_rate), 2)


def main():
    parser = argparse.ArgumentParser(description="Module 3 — Validation")
    parser.add_argument("--input", default=str(CLEANED_DATA))
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    profile = read_json(PROFILING_REPORT) if PROFILING_REPORT.exists() else {}

    rules = rule_based_checks(df, profile=profile)
    anomalies = anomaly_detection(df)
    score = health_score(rules, anomalies)

    write_json(VALIDATION_REPORT, {
        "rule_based": rules,
        "anomaly_detection": anomalies,
        "health_score": score,
    })
    print("[M3] Done.")
    print(f"  health score: {score}")
    print(f"  anomalies flagged: {anomalies.get('anomalies')} / {anomalies.get('checked')} rows")


if __name__ == "__main__":
    main()