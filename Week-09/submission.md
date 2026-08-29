# Week 09 — Submission

**Sprint dates:** _22 Aug 2026 → 29 Aug 2026_
**Maintainer this week:** [Your name] — solo

## What I did this week

Per the Week 8 plan, this week was a **documentation accuracy pass** —
every command in every README, tested literally as written, not just
read for plausibility. Found more real problems than expected. All
fixed and re-verified.

### 1. `requirements.txt` was missing two hard dependencies

`seaborn` and `pytest`/`pytest-cov` were listed as commented-out
"optional" suggestions, but `visualisations.py` hard-imports `seaborn`
(used by Module 1 whenever figures are generated) and the README's own
documented `pytest tests/ -v` command needs `pytest` installed. Followed
the README's exact documented setup (`python -m venv venv` → `pip
install -r requirements.txt`) in a genuinely clean virtual environment to
confirm: **both were missing**, meaning a brand-new contributor following
the README exactly would hit a `ModuleNotFoundError` on their first run.
Fixed `requirements.txt`; re-verified the exact same clean-venv setup
now works end-to-end (profiling with figures + full test suite).

### 2. Module 1 and Module 2 READMEs had broken "How to run" commands

Both documented their CLI as if run from *inside* the module's own
folder (`python profiling_api.py --input data/raw/...`), but `--input`
is a relative path resolved against the current working directory, not
the script's location — running it exactly as documented produces
`FileNotFoundError`. Tested literally, confirmed both fail. Fixed both
to instruct running from the project root with the correct path
(matching how Module 3 and Module 4's READMEs already correctly
documented it — this was an inconsistency between modules' docs, not a
project-wide pattern).

### 3. A dead link: `modules/m1_profiling/README.md` linked to a `schema.json` that was never created

Searched the whole repo — no such file exists, in this location or any
other. Removed the dead link (two references) rather than leave a
promise the repo doesn't keep; documented the report structure inline
instead.

### 4. Module 3's README was missing the Week 7 `check_identifier_uniqueness()` addition

The function signature list and the "what each check does" narrative
both predated Week 7's identifier-uniqueness check — a real
code/documentation drift. Added both.

### 5. Both "as a library" Python examples in Module 1 and Module 2's READMEs failed as written

Neither included the `sys.path.append(...)` needed to import the
module's internal files from outside its own folder — tested both
literally from the project root (where the rest of each README now
correctly says to run from), both raised `ModuleNotFoundError`. Fixed
both, re-verified they run end-to-end.

### 6. Stale numbers and status in the main README

- Test count: said 49, actual is 63 (post Weeks 6–7)
- Coverage: said 69%, actual is 68% (recalculated fresh)
- Status section still said "🚧 In progress" — updated to reflect the
  actual current state (core pipeline complete, in the
  hardening/documentation phase)
- `nps_score (0–10)` read as a hard fact; the raw data actually contains
  a planted out-of-range value (99) — reworded to avoid a reader
  mistaking that for an undiscovered bug

## Verified

Every fix in this list was confirmed by actually running the command as
newly documented, not just re-read for plausibility:

```
- Clean venv + requirements.txt -> figures generate, pytest runs: OK
- M1 CLI command (from project root): OK
- M1 library example (from project root, with sys.path fix): OK
- M2 CLI command (from project root): OK
- M2 library example (from project root, with sys.path fix): OK
- M3 CLI command (unchanged, was already correct): OK
- M4 CLI + --with-figures + all Makefile targets: OK
- Full suite: 63/63 passing
```

## Progress against plan

- [x] Every command in every README tested literally, not just reviewed
- [x] Fixed 6 categories of real inaccuracy (dependencies, 2 broken CLI
      examples, a dead link, a missing function's documentation, 2 broken
      library examples, stale numbers/status)
- [x] Re-verified the complete fixed state end-to-end, including a
      genuinely clean virtual environment

## Blockers

None.

## Next week

Week 10 per the plan: final demo build + dry run. With documentation now
verified accurate, the demo can follow the README's own "How to run"
section directly rather than needing separately-maintained demo notes.