# Week 05 — Submission

**Sprint dates:** _25 Jul 2026 → 01 Aug 2026_
<br>
**Scrum Master this week:** Adib Hassan— AI

## Scope decision for the remaining weeks (5–12)

The original 12-week plan assumed a 3-person team; this project has been
solo since Week 1. Rescoped the remaining weeks to what's realistic and
still meets every rubric criterion (consistency, engineering quality,
completeness, documentation, final demo):

| Week | Original plan | Rescoped |
|---|---|---|
| 5 | README, architecture diagram, tests | *(this week, as planned)* |
| 6 | End-to-end testing + bug fixing | As planned |
| 7 | Refine quality-scoring; expand validation rules | As planned (quality_score refinement was already pulled forward into Week 3) |
| 8 | "Future work" extensions (optional ML methods) | Trimmed to a documented "Future Work" section rather than new ML code — solo, time is better spent hardening what exists |
| 9 | Documentation polish; per-module write-ups | Per-module READMEs completed this week (Week 5), ahead of schedule |
| 10 | Final demo build + dry run | As planned |
| 11 | Presentation prep | As planned |
| 12 | Final presentation + submission | As planned |

Net effect: Week 8's scope is folded into "Future Work" documentation
instead of new code, and Week 9's per-module READMEs were pulled forward
into this week since Module 4 was already fresh in mind. This keeps every
remaining week achievable solo without dropping any rubric criterion.

## What I did this week

### 1. Architecture diagram
Added a Mermaid flowchart to the top-level `README.md` (renders natively
on GitHub — no external image file to keep in sync). Shows the file-
contract flow between all four modules and where Module 4 orchestrates
the other three.

### 2. Per-module READMEs
Added `README.md` to `modules/m2_cleaning/`, `modules/m3_validation/`,
and `modules/m4_pipeline/`, matching the style/depth of Module 1's
existing README (files table, how to run, key function signatures,
integration instructions). `modules/m1_profiling/README.md` was already
in place from Week 1 — left untouched.

Each README documents not just *what* the module does but the specific
bugs found while building it (the phone/numeric_as_text miscoercion, the
dayfirst ISO-date corruption, the stale-`"kind"` range-check gap) so the
reasoning is preserved alongside the code, not just in old PR
descriptions.

### 3. Makefile
Added a `Makefile` at the project root with targets for every common
command, so `profile`/`clean`/`validate`/`pipeline`/`test` don't need to
be remembered as raw `python3 modules/...` invocations:

```bash
make pipeline          # full M1 -> M2 -> M3 run
make test               # run the test suite
make test-cov           # run tests with a coverage report
make clean-outputs       # delete generated reports (simulate a fresh checkout)
make all                 # clean-outputs + pipeline + test
```

The dataset path is overridable (`make pipeline DATA=...`) so this isn't
hardcoded to one CSV.

### 4. Hardened test coverage
Added `pytest-cov` and ran a baseline coverage report:

```
TOTAL   655 statements   69% covered   49 tests passing
```

Added 7 new edge-case tests targeting realistic failure modes rather than
chasing raw coverage percentage for its own sake:

- `normalise()` / `_fix_numeric_as_text()` / `drop_duplicates()` with
  missing profiles, all-junk values, and empty dataframes (Module 2)
- `check_categorical_membership()` on an all-null column, `rule_based_checks()`
  with a completely empty profile dict, `anomaly_detection()` with only
  one numeric column (Module 3)
- CLI `--help` sanity check (Module 4)

**Noted, not chased:** the remaining coverage gap is consistently each
module's own `main()` / argparse wiring. This is exercised by the
end-to-end pipeline run rather than by unit tests — documented as a
deliberate choice in the README's Testing section, not a gap to close.

## Progress against plan

- [x] Decided and documented the rescoped plan for weeks 5–12
- [x] Architecture diagram (Mermaid, in main README)
- [x] Per-module READMEs for M2, M3, M4
- [x] Makefile with 8 targets, all tested
- [x] Test coverage: 42 → 49 tests, baseline coverage measured (69%)
- [x] Verified `make all` runs clean-outputs → pipeline → test successfully
      end-to-end

## Blockers

None.

## Next week

- Week 6 per the (rescoped, same-as-original) plan: broader end-to-end
  testing and bug fixing — likely targeting the `main()` coverage gap
  with a couple of thin subprocess-level integration tests per module,
  and re-running the full suite against the dataset regenerator
  (`data/generate_dataset.py`) to confirm the pipeline is robust to a
  freshly regenerated dataset, not just the one currently committed.