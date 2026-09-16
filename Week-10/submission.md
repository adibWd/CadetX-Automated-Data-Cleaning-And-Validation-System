# Week 10 — Submission

**Sprint dates:** _29 Aug 2026 → 05 Sep 2026_
<br>
**Scrum Master this week:** Adib Hassan— AI

## What I did this week

### 1. Built a proper end-to-end demo (`demo.py`)

The existing `demo.py` (from Week 1) only demonstrated Module 1, on tiny
hand-written sample data — not representative of the finished, four-
module project. Relocated it to `modules/m1_profiling/demo.py` (still
fully runnable on its own, fixed its internal `sys.path` for the new
location) and wrote a new project-root `demo.py` that:

- Runs the real dataset through the real, full pipeline (M1 → M2 → M3)
  via a single subprocess call to `modules/m4_pipeline/pipeline.py` —
  same code path anyone running `make pipeline` gets, not a special
  demo-only version
- Prints a presentation-friendly walkthrough: what Module 1 found, what
  Module 2 fixed (with real before/after quality numbers), what Module 3
  flagged (health score, anomaly count, the negative-value and
  identifier-uniqueness findings), and finishes with a "real bugs this
  project found" section pulling together the actual Week 3/6/7/9
  discoveries as the narrative

### 2. Did an actual dry run — twice

Ran `demo.py` end-to-end from a clean state (`make clean-outputs` first,
so it's a true fresh-checkout simulation), exactly as it would run live
in front of an audience.

**First run caught a real bug in the demo script itself**:
`show_cleaning_summary()` assumed `impute_missing`'s log entries were a
dict (like `normalise`'s), but `imputation.py` actually logs them as a
list of per-column dicts — crashed with `AttributeError: 'list' object
has no attribute 'keys'`. Fixed, then ran the full dry run again from a
clean state to confirm.

**Second run: clean end-to-end, twice in a row** — confirming the
crash was fixed and the demo is reliably reproducible, not a
one-off pass. Also re-ran the full test suite afterward (63/63 still
passing) to confirm the demo script fix didn't touch anything it
shouldn't have.

### 3. Linked the demo from the main README

Added a short "Want the guided walkthrough instead?" pointer in the
"How to run" section so `python demo.py` is discoverable alongside the
raw pipeline commands, not just something you'd stumble on in the file
tree.

## Verified

```
Dry run 1: crashed (AttributeError in demo.py's own summary logic) — bug found and fixed
Dry run 2: clean, end-to-end, twice in a row
Full test suite after the fix: 63/63 passing
```

## Progress against plan

- [x] Built a real, presentation-ready end-to-end demo (not the old
      Module-1-only sample-data version)
- [x] Relocated and fixed the Week 1 demo rather than deleting it
- [x] Actually dry-ran it (twice) rather than assuming it would work —
      caught and fixed a real bug in the process
- [x] Linked from the main README

## Blockers

None.

## Next week

Week 11 per the plan: presentation prep. The demo script itself is the
backbone of the presentation now — next week is about the narrative
around it (what to say while `demo.py` runs, which of the "real bugs
found" section's five stories to spend the most time on, and a slide or
two on the architecture diagram already in the README).