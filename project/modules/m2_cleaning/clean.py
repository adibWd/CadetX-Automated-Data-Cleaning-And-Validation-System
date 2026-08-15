"""
MODULE 2 — DATA CLEANING
------------------------
Fix and improve the dataset after profiling.

FILE CONTRACT
  Input :  data/raw/<dataset>.csv  +  outputs/profiling_report.json
  Output:  data/processed/cleaned_data.csv
           outputs/cleaning_log.json   (what changed + before/after quality score)

WHAT WAS BUILT (Week 2)
  - impute missing values       (imputation.py — median/mode, type-aware)
  - detect & remove duplicates  (exact match; report before/after row count)
  - normalise formats           (currency-as-text -> float, mixed date shapes
                                  -> ISO date, inconsistent Yes/No-style
                                  categories -> one consistent label,
                                  clearly-invalid identifier values flagged
                                  instead of silently guessed at)
  - data-quality score          (computed BEFORE and AFTER, delta reported)
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import (write_json, read_json, CLEANED_DATA, CLEANING_LOG,
                    PROFILING_REPORT, RAW_DIR)  # noqa: E402

# reuse Module 2's own imputation engine instead of re-implementing it
from imputation import impute_missing as _impute_missing  # noqa: E402

# Same UK phone pattern Module 1 validates against, so "normalised enough to
# pass Module 3 validation" and "normalised here" agree with each other.
UK_PHONE_RE = re.compile(r"^(0|\+44)\d{10}$")
# characters that show up in "numeric_as_text" columns because of currency
# symbols / thousands separators, e.g. "£68.48" -> "68.48"
_CURRENCY_STRIP_RE = re.compile(r"[£$€,\s]")


def quality_score(df: pd.DataFrame, profile: dict | None = None) -> float:
    """A 0-100 dataset health score.

    Base (always computed): completeness + uniqueness.
    When Module 1's profiling report is supplied, also folds in
    format-validity for semantic columns (email/phone/postcode) -- the
    Week 3 refinement, extended in Week 7 to also cover postcode, so this
    matches Module 3's format-check coverage exactly (previously only
    email/phone here vs email/phone/postcode there -- an inconsistency,
    not a deliberate design choice). Backward compatible: quality_score(df)
    with no profile still returns exactly the old completeness/uniqueness-
    only score.

    Deliberately does NOT fold in identifier-uniqueness (Module 3's new
    Week 7 check) -- that's a stronger, more specific signal ("do two
    rows claim to be the same customer") that belongs in the validation
    report, not blended into a single cleaning-quality number.
    """
    completeness = 1 - df.isna().sum().sum() / df.size
    uniqueness = 1 - df.duplicated().sum() / len(df)

    if not profile:
        return round(100 * (0.7 * completeness + 0.3 * uniqueness), 2)

    format_patterns = {
        "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
        "phone": UK_PHONE_RE,
        "postcode": re.compile(r"^[A-Za-z]{1,2}\d[A-Za-z\d]?\s?\d[A-Za-z]{2}$"),
    }
    metadata = profile.get("metadata", {})
    validity_scores = []
    for col, meta in metadata.items():
        pattern = format_patterns.get(meta.get("semantic_type"))
        if pattern is None or col not in df.columns:
            continue
        non_null = df[col].dropna().astype(str)
        if len(non_null):
            validity_scores.append(non_null.str.match(pattern).mean())
    validity = sum(validity_scores) / len(validity_scores) if validity_scores else 1.0

    return round(100 * (0.5 * completeness + 0.2 * uniqueness + 0.3 * validity), 2)


def impute_missing(df: pd.DataFrame, report: dict | None = None):
    """Fill missing values using Module 2's own imputation engine."""
    cleaned, log = _impute_missing(df, report=report)
    return cleaned, log


def drop_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Remove exact duplicate rows. Returns (deduped_df, log_entry)."""
    n_before = len(df)
    deduped = df.drop_duplicates(keep="first").reset_index(drop=True)
    n_removed = n_before - len(deduped)
    return deduped, {"exact_duplicates_removed": n_removed, "rows_before": n_before,
                      "rows_after": len(deduped)}


def _fix_numeric_as_text(series: pd.Series) -> pd.Series:
    """'£68.48' / '29.32' -> 68.48 / 29.32 (float). Non-numeric leftovers -> NaN."""
    cleaned = series.astype(str).str.replace(_CURRENCY_STRIP_RE, "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def _fix_dates(series: pd.Series) -> pd.Series:
    """Parse mixed date shapes ('2024-12-05', '10/04/2020', 'Nov 2023')
    into one consistent datetime dtype.

    NOT a single pd.to_datetime(..., dayfirst=True) call. That was tried
    first and found to be WRONG: a global dayfirst flag applied to
    format="mixed" correctly fixes ambiguous UK slash-dates ("03/04/2023"
    -> 3 April, not 4 March) but then ALSO wrongly reinterprets already-
    unambiguous ISO dates ("2024-12-05", 5 Dec) as day-first, silently
    corrupting them to "2024-05-12" (12 May). Verified on the real dataset.

    Fix: detect each row's shape explicitly and parse it with its own
    unambiguous format string, so no shape's rule can bleed into another's.
    Unparseable/unrecognised values become NaT rather than a raw string.
    """
    s = series.astype(str).str.strip()
    result = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")

    iso_mask = s.str.match(r"^\d{4}-\d{2}-\d{2}$")
    result[iso_mask] = pd.to_datetime(s[iso_mask], format="%Y-%m-%d", errors="coerce")

    slash_mask = s.str.match(r"^\d{1,2}/\d{1,2}/\d{4}$")
    result[slash_mask] = pd.to_datetime(s[slash_mask], format="%d/%m/%Y", errors="coerce")  # UK day-first

    monyear_mask = s.str.match(r"^[A-Za-z]{3,9} \d{4}$")
    result[monyear_mask] = pd.to_datetime(s[monyear_mask], format="%b %Y", errors="coerce")

    # anything not matching a known shape: fall back to the generic parser
    # (dayfirst=True, since this is UK data) rather than leave it as NaT.
    remaining = ~(iso_mask | slash_mask | monyear_mask) & s.notna() & (s != "nan")
    if remaining.any():
        result[remaining] = pd.to_datetime(s[remaining], errors="coerce", dayfirst=True)

    return result


_YES_SET = {"yes", "y", "1", "true"}
_NO_SET = {"no", "n", "0", "false"}


def _fix_binary_categorical(series: pd.Series) -> pd.Series:
    """'Yes'/'yes'/'Y'/'1' -> 'Yes'; 'No'/'no'/'N'/'0' -> 'No'."""
    def _map(v):
        if pd.isna(v):
            return v
        v_low = str(v).strip().lower()
        if v_low in _YES_SET:
            return "Yes"
        if v_low in _NO_SET:
            return "No"
        return v
    return series.map(_map)


def normalise(df: pd.DataFrame, report: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """Standardise formats using Module 1's per-column findings.

    Driven by metadata[col]["inferred_type"] and value-set inspection —
    never by hardcoded column names — so this stays dataset-agnostic.
    """
    df = df.copy()
    changes = {}
    metadata = (report or {}).get("metadata", {})

    for col in df.columns:
        col_meta = metadata.get(col, {})
        inferred = col_meta.get("inferred_type")
        semantic = col_meta.get("semantic_type")

        # 1) numbers stored as text with currency symbols / commas.
        #    Only when genuinely numeric (semantic_type == "numeric").
        #    Columns like phone/postcode can ALSO get flagged
        #    "numeric_as_text" but must never be coerced to float --
        #    that would destroy leading zeros and identifier meaning.
        if inferred == "numeric_as_text" and semantic == "numeric":
            before_sample = df[col].dropna().astype(str).head(3).tolist()
            df[col] = _fix_numeric_as_text(df[col])
            changes[col] = {"action": "numeric_as_text -> float (stripped currency/commas)",
                             "before_sample": before_sample,
                             "after_sample": df[col].dropna().head(3).tolist()}
            continue

        # 2) date-ish columns with more than one shape
        date_issue = (report or {}).get("rules", {}).get("inconsistent_formats", {}).get(col, {})
        if date_issue.get("issue") == "multiple date formats present":
            df[col] = _fix_dates(df[col])
            changes[col] = {"action": "parsed mixed date formats -> datetime64",
                             "formats_found": date_issue.get("formats_found")}
            continue

        # 3) binary-ish categorical columns (Yes/yes/Y/1 style spellings)
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            distinct = set(str(v).strip().lower() for v in df[col].dropna().unique())
            if distinct and distinct.issubset(_YES_SET | _NO_SET):
                before_sample = sorted(df[col].dropna().unique().tolist())[:5]
                df[col] = _fix_binary_categorical(df[col])
                changes[col] = {"action": "unified Yes/No-style spellings",
                                 "distinct_before": before_sample}
                continue

        # 4) identifier-like columns with obviously-junk placeholder values
        #    (e.g. phone = "07xx"). Flagged, not guessed at.
        if semantic == "phone":
            is_invalid = ~df[col].astype(str).str.match(UK_PHONE_RE, na=False)
            n_invalid = int((is_invalid & df[col].notna()).sum())
            if n_invalid:
                df.loc[is_invalid & df[col].notna(), col] = "INVALID_PHONE"
                changes[col] = {"action": "flagged unparseable phone values (not guessed at)",
                                 "count": n_invalid}

    return df, changes


def main():
    parser = argparse.ArgumentParser(description="Module 2 — Data Cleaning")
    parser.add_argument("--input", required=False)
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else sorted(RAW_DIR.glob("*.csv"))[0]
    df = pd.read_csv(input_path)

    if df.empty:
        # Found during Week 7's audit: without this guard, an empty CSV
        # doesn't crash -- it silently exits 0 with "quality: nan -> nan",
        # which is worse than a crash (nothing flags it as wrong). Same
        # class of bug as Module 1's Week 6 fix, applied here too.
        print(f"✗ Cannot clean an empty dataset (0 rows): {input_path}")
        sys.exit(1)

    profile = read_json(PROFILING_REPORT)

    score_before = quality_score(df, profile=profile)
    actions = []

    df, dedup_log = drop_duplicates(df)
    actions.append({"step": "drop_duplicates", **dedup_log})

    df, normalise_log = normalise(df, report=profile)
    actions.append({"step": "normalise", "details": normalise_log})

    df, impute_log = impute_missing(df, report=profile)
    actions.append({"step": "impute_missing", "details": impute_log})

    score_after = quality_score(df, profile=profile)

    CLEANED_DATA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED_DATA, index=False)
    write_json(CLEANING_LOG, {
        "quality_score_before": score_before,
        "quality_score_after": score_after,
        "quality_delta": round(score_after - score_before, 2),
        "actions": actions,
        "used_profile_flags": profile.get("rules", {}),
    })
    print("[M2] Done.")
    print(f"  quality: {score_before} -> {score_after}  (delta {round(score_after - score_before, 2)})")


if __name__ == "__main__":
    main()