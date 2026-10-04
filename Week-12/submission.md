# Week 12 — Final Submission

**Sprint dates:** _12 Sep 2026 → 19 Sep 2026_
<br>
**Scrum Master this week:** Adib Hassan— AI

---

## What this project is

An Automated Data Cleaning & Validation System — four independently
runnable, independently testable modules, each reading the previous
one's output as its input:

```
Module 1 (Profile) -> Module 2 (Clean) -> Module 3 (Validate)
                            ^
                    Module 4 (Pipeline) orchestrates all three
```

Run it in one command:
```bash
python demo.py
```

---

## Final verified state (re-run today, from a clean checkout)

```
Pipeline:     M1 -> M2 -> M3, one command, ~5-7 seconds
Quality score: 97.84 -> 97.93
Health score:  97.35
Anomalies:     50 / 1000 rows flagged (Isolation Forest)
Tests:         63/63 passing
Coverage:      65% overall (modules/ scope)
```

---

## The 12 weeks, in one table

| Week | Delivered |
|---|---|
| 1 | Module 1 (profiling) built solo after the team didn't materialise; escalated to CadetX support |
| 2 | Module 2 (cleaning) built: imputation, dedup, normalisation, quality scoring |
| 3 | Addressed code-review feedback on Module 2 (two real bugs found in the process); built Module 3 (validation) |
| 4 | Module 4 (pipeline orchestration): one command runs M1→M2→M3, fail-fast between stages |
| 5 | Architecture diagram, per-module READMEs, a Makefile, hardened test coverage (42→49 tests) |
| 6 | Subprocess-level integration tests; found and fixed an empty-dataset crash in Module 1 |
| 7 | Expanded Module 3's rules (identifier uniqueness); audited and fixed the same empty-dataset bug class in Modules 2 and 3 |
| 8 | `docs/FUTURE_WORK.md` — ML and validation extensions investigated against the real data, not just brainstormed |
| 9 | Documentation accuracy pass: tested every command in every README literally, fixed 6 real issues |
| 10 | Built the final `demo.py` (full pipeline, not just Module 1); dry-ran it twice, caught a bug in the demo script itself |
| 11 | Presentation script, mapped to the demo, bugs ranked by presentation strength, Q&A prepared |
| 12 | This document; final re-verification; rehearsal (see below) |

---

## Every real bug found, in one place

Scattered across 12 weeks of submissions — consolidated here as the
single list a reviewer (or future me) would actually want:

1. **Week 3 — phone column miscoercion.** A phone column flagged
   `"numeric_as_text"` by Module 1 (most values look like digit strings)
   was getting coerced to float, destroying leading zeros. Fixed by
   requiring `semantic_type == "numeric"` before applying the
   currency-strip conversion that was meant for genuinely numeric columns.

2. **Week 3 — date-parsing corruption.** `dayfirst=True` fixes ambiguous
   UK slash-dates but silently corrupts unambiguous ISO dates in the same
   column (`"2024-12-05"` → wrongly became `"2024-05-12"`). Fixed with
   explicit per-date-shape parsing instead of one global flag.

3. **Week 6 — empty-dataset crash (Module 1).** A header-only CSV crashed
   with a raw `ZeroDivisionError` several calls deep. Fixed with a clear
   guard and a readable error message at the one public entry point.

4. **Week 7 — empty-dataset silent bad output (Modules 2 & 3).** Worse
   than a crash: given the same bad input, Module 2 silently reported
   `quality: nan -> nan` and exited 0; Module 3 silently reported a
   misleading `health score: 100.0`. Both now fail loudly instead.

5. **Week 9 — `requirements.txt` missing hard dependencies.** `seaborn`
   and `pytest` were marked "optional" but are actually required —
   confirmed by following the README's own setup instructions in a
   genuinely clean virtual environment and watching it fail.

6. **Week 10 — a bug in the demo script itself**, found by the dry run:
   `impute_missing`'s log entries are a list, not a dict like
   `normalise`'s — the demo's summary code assumed the wrong shape and
   crashed. Fixed, then re-verified clean twice from a fresh state.

**The throughline:** every one of these was caught by actually running
the code against real or adversarial input — the empty dataset, the
mixed-format column, the fresh virtual environment, the live dry run —
not by code review alone. That's the project's actual engineering story.

---

## Rehearsal (this week, before final submission)

Ran through `docs/PRESENTATION.md` out loud, against a timer, with
`python demo.py` running live:

- [ ] Full run timed — **[fill in actual time]**, against the 8–10
      minute target
- [ ] Adjusted if over: the script already marks which 2 of the 5 bug
      stories to cut first (keep #1 date-parsing and #2 empty-dataset
      silent-failure; drop #3 requirements.txt if short on time)
- [ ] Confirmed `python demo.py` still runs clean immediately before
      presenting (not just at some earlier point this week)

---

## Criteria checklist (from the original project brief)

| Criterion | Evidence |
|---|---|
| Consistency | 12 consecutive weekly submissions, this one included |
| Engineering quality | 63 passing tests, working modules, 6 real bugs found and fixed with regression tests for each |
| Collaboration | Real GitHub workflow throughout (branches, PRs, commit history) — solo after Week 1, documented honestly rather than overstated |
| Completeness | All 4 modules built, integrated, and orchestrated into one runnable pipeline |
| Documentation | Architecture diagram, per-module READMEs, Future Work, and a Week 9 pass that verified every documented command actually works |
| Final demo | `demo.py`, dry-run verified twice, presentation script ready |

---

## Closing note

The original plan assumed a 3-person team. That didn't happen past
Week 1. What's here instead is 12 weeks of solo, consistent delivery —
a complete pipeline, a real test suite, documentation that's been
checked rather than assumed, and a demo that's been run, not just
written. That's the project.