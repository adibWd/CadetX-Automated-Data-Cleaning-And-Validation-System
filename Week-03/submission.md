# Week 03 — Submission

**Sprint dates:** _11 Jul 2026 → 18 Jul 2026_
**Scrum Master this week:** Adib Hassan — AI

## What I did this week

### 1. Addressed Module 2 code-review feedback
The reviewer flagged three issues on the Module 2 PR. All three are fixed
and covered by new regression tests:

- **`_fix_dates` needed `dayfirst=True`** — confirmed: without it,
  `"03/04/2023"` parsed as 4 March instead of 3 April.
- **Applying `dayfirst=True` globally was itself a bug** — found while
  fixing the above: `pd.to_datetime(..., format="mixed", dayfirst=True)`
  fixes ambiguous UK slash-dates but then *also* wrongly re-reads
  unambiguous ISO dates (`"2024-12-05"`, 5 Dec) as day-first, silently
  corrupting them to `"2024-05-12"` (12 May). Rewrote `_fix_dates` to
  detect each date shape (ISO / UK slash / "Mon YYYY") and parse it with
  its own explicit format string instead of one global flag.
- **`UK_PHONE_RE` was `{9,10}`, should be `{10}`** — fixed; verified the
  looser pattern wasn't actually matching any real value in the dataset,
  but the tighter pattern is correct going forward.

New tests added: `test_iso_dates_not_corrupted_when_mixed_with_uk_slash_dates`
(the exact regression), plus the reviewer-requested phone-length test.

### 2. Refined `quality_score()` per the Week 7 note (pulled forward)
`quality_score()` now optionally folds in **format-validity** (email/phone
conformance, via Module 1's `semantic_type` metadata) alongside completeness
and uniqueness, when a profiling report is supplied:

```
no profile:  100 × (0.7 × completeness + 0.3 × uniqueness)          [unchanged]
with profile: 100 × (0.5 × completeness + 0.2 × uniqueness + 0.3 × validity)
```

Backward compatible — `quality_score(df)` alone still returns the original
score. `main()` now passes the profile to both the before and after score,
so the reported delta reflects format-validity too.

### 3. Built Module 3 — Validation (rule-based + anomaly detection)
Completed the Week 3 scope end-to-end, consuming `cleaned_data.csv` from
Module 2:

- **Format checks** — email / phone / postcode, routed by Module 1's
  `semantic_type` (no hardcoded column names).
- **Range checks** — numeric columns checked against the min/max Module 1
  observed on the raw data. Falls back to recomputing the range from the
  cleaned data itself when M1 never had numeric stats for a column (see
  bug #1 below).
- **Unexpected-negatives check** (new, beyond the original brief) — flags
  numeric columns where negatives are a small minority, catching two real
  planted issues (see below).
- **Categorical membership** — records the allowed value set for
  low-cardinality columns, for Module 4 to validate new incoming rows
  against later.
- **Anomaly detection** — Isolation Forest over numeric columns.
- **Health score** — 0.7 × rule pass-rate + 0.3 × anomaly-free rate.

**Two real bugs found while building this, both fixed:**

1. `monthly_charges` was silently skipped by the range check. Module 1
   profiled the *raw* data, where this column was still `"£68.48"`-style
   text and got classified `"kind": "categorical"`. After Module 2 cleaned
   it to a real float column, Module 3 was still trusting M1's stale
   classification and never checked it. Fixed by driving numeric-check
   eligibility off the *cleaned* data's actual dtype, with recomputed
   min/max as a fallback when M1 has no numeric stats.
2. Once fixed, the new range/negatives checks surfaced genuine data
   problems: **20 rows with negative `monthly_charges`** (`-£10.00`,
   `-£29.99`) and **20 rows with negative `tenure_months`** (`-1`, `-5`) —
   neither should logically be negative. Neither is auto-corrected (that's
   a business-logic decision above this module's scope); both are now
   surfaced in `validation_report.json` for review.

**Verified end-to-end** on the real dataset (1,000 rows after dedup):

| | Value |
|---|---|
| Health score | 97.35 |
| Anomalies flagged (Isolation Forest) | 50 / 1,000 (5.0%) |
| Emails failing format check | 99 / 1,000 |
| Phones failing format check | 30 / 1,000 |
| Postcodes failing format check | 78 / 1,000 |
| Negative `monthly_charges` rows | 20 |
| Negative `tenure_months` rows | 20 |

`tests/test_module3.py` — 15 tests, all passing. Full suite
(`test_module1.py` + `test_module2.py` + `test_module3.py`) — 41 tests,
all passing together.

## Progress against plan

- [x] Addressed all Module 2 review feedback (dayfirst bug, phone regex,
      plus a second bug found while fixing the first)
- [x] Refined `quality_score()` to fold in format-validity (pulled the
      Week 7 note forward since the review already had me in this code)
- [x] Built Module 3 rule-based checks + Isolation Forest anomaly detection
- [x] `tests/test_module3.py` added (15 tests)
- [x] Ran the full M1 → M2 → M3 pipeline end-to-end and confirmed results

## Blockers

- None currently blocking. Noting for the record: `tests/test_profiling.py`
  (pre-dating this work, from Module 1) still fails on import
  (`ModuleNotFoundError: m1_profiling.profile` — a leftover from the
  `profile.py` → `profiling_api.py` rename in Week 1). Left untouched this
  week since it's outside Module 2/3 scope; flagging to clean up or remove
  now that the repo has a single maintainer.

## Next week

- Module 4 — Pipeline: wire M1 → M2 → M3 into one configurable,
  single-command run (CLI + Docker), per the original 12-week plan.
- Clean up `tests/test_profiling.py` (see Blockers).
- Consider whether the negative `monthly_charges`/`tenure_months` rows
  found this week warrant a business-logic correction rule in Module 2,
  or should stay a Module 3-only flag for human review.
