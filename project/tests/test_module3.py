"""
MODULE 3 — TEST SUITE
======================
Known-answer tests for the validation module.

Run:  pytest tests/test_module3.py -v
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "modules" / "m3_validation"))

from validate import (check_format_column, check_numeric_range,
                       check_unexpected_negatives, check_categorical_membership,
                       check_identifier_uniqueness,
                       rule_based_checks, anomaly_detection, health_score,
                       EMAIL_RE, UK_PHONE_RE, UK_POSTCODE_RE)


def test_email_format_check_counts_valid_and_invalid():
    s = pd.Series(["a@b.com", "not-an-email", "c@d.co.uk"])
    result = check_format_column(s, EMAIL_RE, "email")
    assert result["checked"] == 3
    assert result["valid"] == 2
    assert result["invalid"] == 1


def test_phone_format_matches_uk_pattern_exactly_10_digits():
    s = pd.Series(["07973832060", "0797383206", "INVALID_PHONE"])
    result = check_format_column(s, UK_PHONE_RE, "phone")
    assert result["valid"] == 1
    assert result["invalid"] == 2


def test_postcode_format_check():
    s = pd.Series(["SO31 8JT", "12345", "ABCDE"])
    result = check_format_column(s, UK_POSTCODE_RE, "postcode")
    assert result["valid"] == 1
    assert result["invalid"] == 2


def test_range_check_uses_profiled_stats_when_available():
    s = pd.Series([10, 20, 150])
    result = check_numeric_range(s, "age", {"kind": "numeric", "min": 0, "max": 100})
    assert result["valid"] == 2
    assert result["invalid"] == 1
    assert result["range_source"] == "profiling_report"


def test_range_check_falls_back_to_recomputed_stats_when_profile_missing():
    """Regression test: a column that was 'numeric_as_text' in the raw data
    (e.g. currency-as-text) has no numeric stats in Module 1's profiling
    report. The range check must still run, using the cleaned data's own
    min/max, instead of silently skipping the column -- this is exactly
    what happened to monthly_charges before this fallback was added.
    """
    s = pd.Series([10.0, 20.0, 30.0])
    result = check_numeric_range(s, "monthly_charges", {})
    assert result["checked"] == 3
    assert result["invalid"] == 0
    assert result["range_source"] == "recomputed_from_cleaned_data"


def test_unexpected_negatives_flagged_when_rare():
    s = pd.Series([10, 20, 30, -5, 40, 50, 60, 70, 80, 90])
    result = check_unexpected_negatives(s, "monthly_charges", threshold_pct=10.0)
    assert result is not None
    assert result["invalid"] == 1


def test_unexpected_negatives_skipped_when_common():
    """A column where negatives are common (e.g. profit/loss) is more
    likely genuinely signed than a data-entry error, so it's not flagged.
    """
    s = pd.Series([10, -10, 20, -20, 30, -30])
    result = check_unexpected_negatives(s, "profit", threshold_pct=10.0)
    assert result is None


def test_unexpected_negatives_none_when_no_negatives_present():
    s = pd.Series([10, 20, 30])
    assert check_unexpected_negatives(s, "age") is None


def test_categorical_membership_records_allowed_set():
    s = pd.Series(["Yes", "No", "Yes", "Yes", "No"])
    result = check_categorical_membership(s, "churn")
    assert result["allowed_values"] == ["No", "Yes"]
    assert result["invalid"] == 0


def test_categorical_membership_skipped_for_high_cardinality():
    s = pd.Series([f"id_{i}" for i in range(50)])
    result = check_categorical_membership(s, "customer_id", max_categories=20)
    assert result is None


def test_rule_based_checks_routes_columns_by_semantic_type():
    df = pd.DataFrame({
        "email": ["a@b.com", "bad-email"],
        "age": [25, 40],
    })
    profile = {
        "metadata": {"email": {"semantic_type": "email"}, "age": {}},
        "profiling": {"distributions": {"age": {"kind": "numeric", "min": 0, "max": 120}}},
    }
    results = rule_based_checks(df, profile=profile)
    assert results["email"]["rule"] == "email_format"
    assert results["age"]["rule"] == "age_range"


def test_anomaly_detection_returns_a_bounded_count():
    df = pd.DataFrame({"a": list(range(100)), "b": list(range(100, 200))})
    result = anomaly_detection(df)
    assert 0 <= result["anomalies"] <= result["checked"]


def test_anomaly_detection_handles_too_little_data_gracefully():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = anomaly_detection(df)
    assert result["anomalies"] == 0
    assert "note" in result


def test_health_score_is_100_when_everything_passes():
    rules = {"a": {"checked": 10, "valid": 10}}
    anomalies = {"checked": 10, "anomalies": 0}
    assert health_score(rules, anomalies) == 100.0


def test_health_score_drops_when_rules_fail():
    rules = {"a": {"checked": 10, "valid": 5}}
    anomalies = {"checked": 10, "anomalies": 0}
    assert health_score(rules, anomalies) < 100.0


# ---------------- Week 5 hardening: edge cases ----------------

def test_categorical_membership_all_null_returns_none():
    """A column that's entirely missing has nothing to record as an
    'allowed set' -- must return None, not crash on nunique() of nothing.
    """
    s = pd.Series([None, None, None])
    assert check_categorical_membership(s, "some_col") is None


def test_rule_based_checks_handles_completely_empty_profile():
    """rule_based_checks(df, profile={}) -- no metadata, no distributions
    at all -- must still run (falls back to categorical/dtype-based
    routing for every column) rather than raising a KeyError.
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    results = rule_based_checks(df, profile={})
    assert "a" in results
    assert "b" in results


def test_anomaly_detection_with_single_numeric_column():
    """Isolation Forest needs at least one feature column -- confirm a
    single-column numeric frame doesn't error out.
    """
    df = pd.DataFrame({"a": list(range(50))})
    result = anomaly_detection(df)
    assert result["checked"] == 50
    assert 0 <= result["anomalies"] <= 50


# ---------------- Week 7: identifier-uniqueness check ----------------

def test_identifier_uniqueness_flags_duplicate_ids():
    """Two rows sharing the same customer_id must be flagged, even if
    every OTHER column differs -- this is stronger than Module 2's
    exact-row duplicate removal, which would never catch this case.
    """
    s = pd.Series([101, 102, 102, 103])
    result = check_identifier_uniqueness(s, "customer_id")
    assert result["checked"] == 4
    assert result["invalid"] == 1
    assert result["valid"] == 3


def test_identifier_uniqueness_all_unique_passes():
    s = pd.Series([101, 102, 103])
    result = check_identifier_uniqueness(s, "customer_id")
    assert result["invalid"] == 0


def test_rule_based_checks_routes_identifier_columns():
    """rule_based_checks() must route semantic_type == 'identifier' to
    the uniqueness check, not fall through to the generic numeric checks
    (which would miss the duplicate-ID problem entirely).
    """
    df = pd.DataFrame({"customer_id": [1, 2, 2, 3]})
    profile = {"metadata": {"customer_id": {"semantic_type": "identifier"}}}
    results = rule_based_checks(df, profile=profile)
    assert results["customer_id"]["rule"] == "customer_id_identifier_uniqueness"
    assert results["customer_id"]["invalid"] == 1