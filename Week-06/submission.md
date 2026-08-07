# Week 06 — Submission

**Sprint dates:** _01 Aug 2026 → 08 Aug 2026_
<br>
**Scrum Master this week:** Adib Hassan— AI

## What I did this week

### 1. Subprocess-level integration tests (`tests/test_integration.py`)
The Week 5 README already documented that each module's `main()` /
CLI-argument-parsing code is deliberately exercised by the end-to-end
pipeline run rather than by unit tests. This week made that explicit and
verifiable: 5 new tests that actually spawn the real CLI as a subprocess
(not just call the Python functions directly), covering the part the
unit test files can't:

- Full pipeline (`pipeline.py`) succeeds on the real committed dataset
  and produces all four contract files
- Module 2's CLI runs standalone once Module 1 has produced
  `profiling_report.json`
- Module 3's CLI runs standalone once Module 2 has produced
  `cleaned_data.csv`
- Module 1's CLI fails cleanly (not with a traceback) on a malformed
  input — see the bug below
- The full pipeline's fail-fast contract holds end-to-end: a stage-1
  failure stops the run before Module 2 or 3 are ever attempted

### 2. Robustness testing against freshly regenerated / stress data
Per the plan, re-ran the pipeline against data that isn't just the one
CSV currently committed:

- Regenerated the committed dataset via `data/generate_dataset.py`
  (seeded, reproduces identically — confirms the generator itself is
  deterministic and trustworthy for a demo).
- Generated a **second, different** synthetic dataset (different random
  seed, different row count: 309 rows) to check the pipeline isn't
  quietly overfit to the one file that's always been used for testing.
  Ran clean.
- Stress-tested edge cases beyond what any single generator run happens
  to produce:
  - **5-row dataset** — below Module 3's anomaly-detection minimum
    (`< 10` rows). Handled gracefully already (0 anomalies, no crash) —
    no change needed, confirms the existing guard works.
  - **Near-total-duplicate dataset** (16 rows, 15 identical) — Module 2
    correctly deduped to 1 row; Module 3 handled the resulting tiny
    frame without crashing.
  - **Zero-row (header-only) CSV** — **found a real crash** (below).

### 3. Bug found and fixed: empty dataset crashes Module 1
A header-only CSV (valid columns, zero data rows) crashed Module 1 with
a raw `ZeroDivisionError` four calls deep inside
`profiling_engine.py::missing_value_analysis` (`n_missing / len(df)`,
and `total_missing / total_cells`, both zero when the frame is empty).
The traceback gave no indication of what was actually wrong.

**Fix:** added an explicit `df.empty` guard at `build_profiling_report()`
— Module 1's single public entry point, used by both the CLI and any
library caller — that raises a clear `ValueError` explaining the problem.
`profiling_api.py`'s `main()` catches it and prints one readable line
instead of a stack trace, still exiting non-zero so Module 4's fail-fast
check stops the pipeline correctly.

Scoped deliberately narrow: didn't add zero-row guards to every
downstream statistical function in `profiling_engine.py` /
`rule_engine.py` (a much larger change) since failing once, early, and
clearly at the entry point is sufficient — nothing downstream ever runs
on the empty frame.

Two new regression tests cover this: one for Module 1's CLI directly,
one for the full pipeline's fail-fast behaviour on the same input.

## Verified

```
54 tests passing (49 from Week 5 + 5 new integration tests)
Full pipeline: verified on the committed dataset, a second differently-
seeded dataset, a 5-row dataset, a near-total-duplicate dataset, and a
zero-row dataset (now fails cleanly instead of crashing).
```

## Progress against plan

- [x] Subprocess-level integration tests targeting the `main()` coverage
      gap, one (or more) per module
- [x] Re-ran the full suite against a freshly regenerated dataset
- [x] Stress-tested additional edge cases beyond the standard generator
      output (tiny dataset, near-total-duplicate dataset, empty dataset)
- [x] Found and fixed a real crash (empty dataset), with regression tests

## Blockers

None.

## Next week

- Per the rescoped plan, Week 7 = revisit `quality_score()` / expand
  validation rules further. Candidate: the same `df.empty` class of
  guard is worth a quick audit in Module 2 and Module 3's own entry
  points too, even though the pipeline never reaches them with an empty
  frame today (Module 1 stops it first) — cheap insurance if either
  module is ever called standalone on bad input directly.