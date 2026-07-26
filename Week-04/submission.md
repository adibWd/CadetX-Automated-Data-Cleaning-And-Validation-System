# Week 04 — Submission

**Sprint dates:** _18 Jul 2026 → 25 Jul 2026_
**Scrum Master this week:** Adib Hassan— AI
## What I did this week

### 1. Built Module 4 — Pipeline Orchestration
Completed `modules/m4_pipeline/pipeline.py`, chaining Modules 1 → 2 → 3
into a single command:

```bash
python modules/m4_pipeline/pipeline.py --input data/raw/broadband_customers.csv
```

- Runs profiling → cleaning → validation in sequence via subprocess calls
  to each module's own CLI (no code duplication — each module stays
  independently runnable too).
- **Fail-fast checking**: after each stage, checks BOTH the subprocess
  exit code AND that the stage's contract file actually landed on disk.
  A stage that exits 0 without writing its output is treated as a
  failure, not a silent no-op — this stops the pipeline immediately with
  a readable message instead of letting the *next* stage crash several
  steps later with a confusing `FileNotFoundError`.
- Per-stage timing, printed in the final summary line.
- `--with-figures` flag to optionally generate Module 1's profiling plots
  (off by default, for speed — the pipeline runs in ~4-7s without them).

**Bug found and fixed:** the Week 4 scaffold still called
`m1_profiling/profile.py`, the filename from *before* the Week 1 rename
to `profiling_api.py` (the rename that fixed the standard-library
`profile` module shadowing issue). Running the scaffold as-is would have
failed immediately on stage 1. Fixed the reference.

**Second bug found while writing tests:** `run_stage`'s success-message
formatting called `path.relative_to(project_root)` unconditionally, which
raises `ValueError` for any output path outside the project root. Doesn't
affect normal runs (module outputs are always under the project root) but
made the function fragile and untestable in isolation. Fixed with a
try/except fallback.

**Verified end-to-end** on the real dataset, from a clean state (deleted
all generated `outputs/*.json` and `data/processed/*.csv` first, to
simulate a fresh checkout):

```
=== M1 Profile ===
✔ M1 Profile done in ~2-5s
=== M2 Clean ===
✔ M2 Clean done in ~0.4s
=== M3 Validate ===
✔ M3 Validate done in ~1-2s
✅ Pipeline complete in ~4-7s. Reports are in outputs/.
```

Also verified the fail-fast path: pointing `--input` at a non-existent
file exits immediately with a clear message, before any module runs.

### 2. Added `tests/test_module4.py`
4 tests, covering the orchestrator's own logic (not re-testing the
modules it calls, which already have their own test files):
- a failing subprocess stops the pipeline (`sys.exit`)
- a stage that exits 0 but never writes its contract file is still
  treated as a failure
- a stage that succeeds AND writes its file returns normally
- the CLI rejects a missing input file before invoking any module

### 3. Repo cleanup
Removed `tests/test_profiling.py` — a Week-1-era starter test file that
imported from `m1_profiling.profile` (the pre-rename module name) and was
fully superseded by `tests/test_module1.py` (12 tests, already covering
this ground). Kept as a deletion rather than a fix, since fixing it would
just duplicate `test_module1.py`.

## Progress against plan

- [x] Module 4 pipeline built: one command runs M1 → M2 → M3
- [x] Fail-fast error handling between stages
- [x] `tests/test_module4.py` added (4/4 passing)
- [x] Verified end-to-end from a clean state
- [x] Removed the stale `tests/test_profiling.py`
- [x] Dockerfile reviewed — no changes needed; documented the correct
      build context (must be run with `project/` as the build context,
      since the Dockerfile lives in `modules/m4_pipeline/`)

## Decision: negative `monthly_charges` / `tenure_months` (from last week)

Kept as a **Module 3 flag only**, not an auto-correction in Module 2.
Reasoning: "correcting" a negative charge or duration requires a business
rule this project doesn't have access to (Is it a sign-flip bug? A
legitimate refund/credit? A different unit?) — silently guessing would be
worse than surfacing it. `validation_report.json` continues to report
these for human review.

## Blockers

None.

## Next week

- Decide the total scope for the remaining weeks (5–12) given the team
  situation — likely: harden test coverage, polish documentation
  (architecture diagram, per-module READMEs), and build the final demo,
  per the original 12-week plan.
- Consider adding a `Makefile` or npm-style task runner so the common
  commands (profile / clean / validate / full pipeline / test) don't need
  to be remembered as raw `python3 modules/...` invocations.
