# Week 07 — Submission

**Sprint dates:** _08 Aug 2026 → 15 Aug 2026_
**Maintainer this week:** [Your name] — solo

## What I did this week

### 1. Audited Module 2 and Module 3 for the same empty-dataframe class of bug as Week 6

Week 6 fixed a crash when Module 1 was given a zero-row CSV. This week
audited whether Module 2 and Module 3 have the same problem when run
**standalone** (bypassing Module 1's guard entirely — e.g. someone runs
`clean.py` directly against a bad file, or `validate.py` against a
`cleaned_data.csv` that ended up empty for some other reason).

**Found two real bugs, both worse than a crash — silent bad output:**

- **Module 2**, given an empty CSV, didn't crash — it exited 0 and
  printed `quality: nan -> nan (delta nan)`, with `RuntimeWarning`s
  buried above it that are easy to miss in a longer log.
- **Module 3**, given an empty `cleaned_data.csv`, didn't crash either —
  it exited 0 and reported `health score: 100.0, anomalies: 0/0`, which
  reads exactly like a dataset that passed every check, not like a
  dataset that was never actually checked at all.

**Fix:** added the same `df.empty` guard pattern from Module 1's Week 6
fix to both modules' `main()` — a clear message, non-zero exit, no
`NaN`/misleadingly-perfect output. Two new regression tests in
`tests/test_integration.py` cover this (`test_m2_cli_fails_cleanly_on_a_zero_row_csv`,
`test_m3_cli_fails_cleanly_on_a_zero_row_csv`).

### 2. Expanded Module 3's validation rules — identifier uniqueness

Added `check_identifier_uniqueness()`, routed via
`semantic_type == "identifier"`. This is a genuinely different check from
Module 2's exact-row duplicate removal: two rows can differ in every
other column and still share the same `customer_id` — row-level dedup
would never catch that, but it still means two records claim to be the
same real-world customer. Ran against the real dataset: `customer_id` is
confirmed 100% unique post-cleaning (1000/1000), now regression-tested
rather than just assumed.

### 3. Revisited `quality_score()` — closed a coverage gap

`quality_score()`'s format-validity component only checked email/phone,
while Module 3's format checks cover email/phone/**postcode**. Not a
deliberate design choice — just drift between the two modules. Added
postcode to `quality_score()`'s pattern set so both modules check the
same set of formats. On the real dataset this moved the score slightly
(`97.8 → 97.93` instead of `97.8 → 98.06`, since postcode format issues
now count against it too).

Deliberately did **not** fold identifier-uniqueness into `quality_score()`
— documented the reasoning in the docstring: it's a stronger, more
specific signal that belongs in the validation report, not blended into
one cleaning-quality number.

### 4. Housekeeping: reconciled a regression in `test_module2.py`

While rebuilding the test suite for this week's work, found that the
Week 5 file swap had accidentally **dropped 3 tests** that existed after
Week 3/4 (`test_quality_score_backward_compatible_without_profile`,
`test_quality_score_folds_in_format_validity_when_profile_given`,
`test_iso_dates_not_corrupted_when_mixed_with_uk_slash_dates`) — a
full-file replacement overwrote the working copy with a stale local
version that predated those tests. Restored them. Flagging this
transparently rather than quietly folding it into "added tests" — worth
being extra careful with full-file replacements going forward; a diff
review before overwriting would have caught this at the time.

## Verified

```
63 tests passing (was 54 last week: +6 module2/3 tests for the new
checks, +2 integration regression tests, +3 restored from the Week 5
regression above -- 54 - 3 lost + 12 new = 63)

Full pipeline re-verified on the real dataset:
  quality: 97.8 -> 97.93
  health score: 97.35
  customer_id: 1000/1000 unique
```

## Progress against plan

- [x] Audited Module 2 and Module 3 for the empty-dataframe class of bug
      — found and fixed two real (silent, non-crashing) bugs
- [x] Expanded validation rules: identifier uniqueness
- [x] Revisited `quality_score()`: added postcode, documented why
      identifier-uniqueness is deliberately excluded
- [x] Found and fixed a test-suite regression from Week 5's file swap

## Blockers

None.

## Next week

- Per the rescoped plan, Week 8 folds into documented "Future Work"
  rather than new ML code. Candidate content: optional ML-based anomaly
  methods beyond Isolation Forest, an NLP-based semantic-type classifier
  for Module 1, and a note that further validation rules (e.g.
  cross-column consistency checks — a `churn`/`tenure_months`
  relationship, say) were considered but scoped out for time.