# Module 4 — Pipeline Orchestration

Chains Modules 1 → 2 → 3 into one runnable command, with fail-fast error
handling between stages.

**Output:** everything the three modules produce (`profiling_report.json`,
`cleaned_data.csv`, `cleaning_log.json`, `validation_report.json`), all in
one run.

**Scope note (kept from the original brief):** DVC, Git LFS, an NLP
classifier, and full CI are not implemented here — solo, "runs
end-to-end with one command" satisfies the rubric. Listed under future work.

---

## Files

| File | Responsibility |
|------|----------------|
| `pipeline.py` | **Public API** — runs M1 → M2 → M3 in sequence via subprocess calls to each module's own CLI |
| `Dockerfile` | Minimal container so the pipeline runs anywhere |

---

## How to run

```bash
# directly
python3 modules/m4_pipeline/pipeline.py --input data/raw/broadband_customers.csv

# with profiling plots too (slower)
python3 modules/m4_pipeline/pipeline.py --input data/raw/broadband_customers.csv --with-figures

# via the Makefile (see project root)
make pipeline
```

### Docker

The Dockerfile lives in `modules/m4_pipeline/` but must be built with
`project/` as the build **context** (it needs `requirements.txt` and the
rest of the codebase, which live one level up):

```bash
docker build -f modules/m4_pipeline/Dockerfile -t cadetx-pipeline .   # run from project/
docker run cadetx-pipeline --input data/raw/broadband_customers.csv
```

---

## Key function signatures

```python
run_stage(label: str, cmd: list[str], expect: Path) -> float   # timing, in seconds
```

---

## Design notes

- **Each module stays independently runnable.** `pipeline.py` calls each
  module's own CLI via `subprocess`, rather than importing and re-wiring
  their internals — no logic is duplicated, and `python3
  modules/m2_cleaning/clean.py` on its own still works exactly as before.
- **Fail-fast, on two conditions, not one.** After each stage, `run_stage`
  checks the subprocess's exit code AND that the stage's contract file
  actually landed on disk. A stage that exits 0 without writing its
  output is treated as a failure — this stops the pipeline immediately
  with a readable message, instead of letting the *next* stage crash
  several steps later with a confusing `FileNotFoundError` whose real
  cause is upstream.
- **A real bug this caught during Week 4:** the original scaffold called
  `m1_profiling/profile.py` — the filename from *before* the Week 1
  rename to `profiling_api.py` (done to stop shadowing Python's
  standard-library `profile` module). Running the scaffold as originally
  written would have failed on the very first stage.

---

> All project data is synthetic. No real customers.
