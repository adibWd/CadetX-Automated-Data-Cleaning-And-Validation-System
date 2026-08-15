"""
MODULE 2 — TEST SUITE
----------------------
Known-answer tests for the cleaning module.

Run:  pytest tests/test_module2.py -v
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "modules" / "m2_cleaning"))

from clean import (quality_score, drop_duplicates, normalise, impute_missing,
                    _fix_numeric_as_text, _fix_binary_categorical, _fix_dates,
                    UK_PHONE_RE)


def test_perfect_dataset_scores_100():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    assert quality_score(df) == 100.0


def test_quality_score_backward_compatible_without_profile():
    """quality_score(df) with no profile must behave exactly as before
    the Week 7 refinement -- completeness + uniqueness only.
    """
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    assert quality_score(df) == quality_score(df, profile=None)


def test_quality_score_folds_in_format_validity_when_profile_given():
    """With a profiling report supplied, invalid emails should pull the
    score down even when there are no missing values or duplicates.
    """
    df = pd.DataFrame({"email": ["a@b.com", "not-an-email", "c@d.com"]})
    profile = {"metadata": {"email": {"semantic_type": "email"}}}
    score_with_profile = quality_score(df, profile=profile)
    score_without_profile = quality_score(df)
    assert score_with_profile < score_without_profile


def test_quality_score_now_also_checks_postcode_validity():
    """Week 7: postcode was added to quality_score's format-validity
    check to match Module 3's coverage (previously only email/phone here).
    """
    df = pd.DataFrame({"postcode": ["SO31 8JT", "not a postcode"]})
    profile = {"metadata": {"postcode": {"semantic_type": "postcode"}}}
    score_with_profile = quality_score(df, profile=profile)
    score_without_profile = quality_score(df)
    assert score_with_profile < score_without_profile


def test_missing_and_duplicates_lower_the_score():
    df = pd.DataFrame({"a": [1, 1, None], "b": ["x", "x", "z"]})
    assert quality_score(df) < 100.0


def test_exact_duplicates_removed():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    cleaned, log = drop_duplicates(df)
    assert len(cleaned) == 2
    assert log["exact_duplicates_removed"] == 1


def test_currency_symbols_stripped_to_float():
    s = pd.Series(["£29.99", "44.99", "£54.99"])
    out = _fix_numeric_as_text(s)
    assert out.tolist() == [29.99, 44.99, 54.99]


def test_normalise_does_not_touch_phone_even_if_numeric_as_text():
    df = pd.DataFrame({"phone": ["07123456789", "07xx", "07234567890"]})
    report = {
        "metadata": {
            "phone": {"inferred_type": "numeric_as_text", "semantic_type": "phone"}
        },
        "rules": {"inconsistent_formats": {}},
    }
    cleaned, changes = normalise(df, report=report)
    assert not pd.api.types.is_float_dtype(cleaned["phone"])
    assert (cleaned["phone"] == "INVALID_PHONE").sum() == 1
    assert changes["phone"]["count"] == 1


def test_yes_no_style_spellings_unified():
    s = pd.Series(["Yes", "yes", "Y", "1", "No", "no", "N", "0"])
    out = _fix_binary_categorical(s)
    assert out.tolist() == ["Yes", "Yes", "Yes", "Yes", "No", "No", "No", "No"]


def test_impute_missing_fills_all_nulls():
    df = pd.DataFrame({"a": [1.0, None, 3.0], "b": ["x", None, "x"]})
    cleaned, log = impute_missing(df)
    assert cleaned.isna().sum().sum() == 0
    assert len(log) == 2


def test_ambiguous_uk_date_parsed_dayfirst():
    s = pd.Series(["03/04/2023"])
    result = _fix_dates(s)
    assert result.iloc[0].day == 3
    assert result.iloc[0].month == 4


def test_unambiguous_date_still_correct():
    s = pd.Series(["25/12/2023"])
    result = _fix_dates(s)
    assert result.iloc[0].day == 25
    assert result.iloc[0].month == 12


def test_iso_dates_not_corrupted_when_mixed_with_uk_slash_dates():
    """Regression test: a naive dayfirst=True flag fixes ambiguous UK
    slash-dates but ALSO wrongly re-reads unambiguous ISO dates as
    day-first -- "2024-12-05" was silently corrupted to "2024-05-12"
    when both shapes appeared in the same column.
    """
    s = pd.Series(["2024-12-05", "03/04/2023"])
    result = _fix_dates(s)
    assert result.iloc[0] == pd.Timestamp("2024-12-05")
    assert result.iloc[1] == pd.Timestamp("2023-04-03")


def test_uk_phone_regex_rejects_nine_digits():
    assert UK_PHONE_RE.match("0712345678") is None


def test_uk_phone_regex_accepts_ten_digits():
    assert UK_PHONE_RE.match("07123456789") is not None


# ---------------- Week 5 hardening: edge cases ----------------

def test_normalise_handles_missing_profile_gracefully():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cleaned, changes = normalise(df, report=None)
    assert cleaned.equals(df)
    assert changes == {}


def test_fix_numeric_as_text_all_unparseable_returns_nan_not_crash():
    s = pd.Series(["not a number", "also junk", ""])
    out = _fix_numeric_as_text(s)
    assert out.isna().all()


def test_drop_duplicates_on_empty_dataframe_does_not_crash():
    df = pd.DataFrame({"a": [], "b": []})
    cleaned, log = drop_duplicates(df)
    assert len(cleaned) == 0
    assert log["exact_duplicates_removed"] == 0