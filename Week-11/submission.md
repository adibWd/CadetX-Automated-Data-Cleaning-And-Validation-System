# Week 11 — Submission

**Sprint dates:** _05 Sep 2026 → 12 Sep 2026_
<br>
**Scrum Master this week:** Adib Hassan— AI

## What I did this week

### `docs/PRESENTATION.md` — the presentation script

Per Week 10's plan, this week is the narrative around `demo.py`, not new
code. Wrote a full speaker-notes document structured around the demo's
five printed sections, so the terminal output does the visual work and
the talking is about *what it means*, not reading the screen aloud:

- **Opening** — one slide (the README's existing architecture diagram,
  no new visual needed) plus one honest, brief line about the solo-team
  situation, stated plainly and moved past rather than dwelled on.
- **Live demo narration** — a short talking point for each of
  `demo.py`'s five sections (pipeline run, profiling findings, cleaning
  results, validation results).
- **Bug highlight reel** — of the five real bugs `demo.py` already lists,
  picked and ranked which ones to actually tell if time is short:
  1. The date-parsing corruption (Week 3) — leads, because "the obvious
     fix is wrong" is the strongest technical story, not just a bug count.
  2. The empty-dataset silent-failure bugs (Week 7) — second choice,
     because "worse than crashing" is a distinct, memorable point about
     silent bad output vs. loud failure.
  3. The `requirements.txt` gap (Week 9) — third if there's time, because
     it demonstrates verifying your own documentation, not just your code.
- **Closing** — test count, one-command reproducibility, pointer to
  Future Work.
- **Anticipated Q&A** — four questions I could plausibly be asked
  (anomaly-method choice, what I'd do with more time, dataset-agnostic
  claim, hardest bug), each with a real answer grounded in already-done
  work, not improvised on the spot.

### Timing target

Scoped to 8–10 minutes of talking plus the ~5-second live run, leaving
room for Q&A within a typical short slot. Marked which bug stories to
cut first if running long (three ranked, not five to force through).

## Progress against plan

- [x] Presentation script written, mapped directly to `demo.py`'s
      actual output structure (no drift between what's said and what's
      shown)
- [x] Bug stories ranked by strength, not just listed, with a stated
      reason for the ranking
- [x] Anticipated Q&A prepared with grounded answers, not left to
      improvise
- [x] Timing scoped realistically for a short presentation slot

## Blockers

None.

## Next week

Week 12 per the plan: final presentation + submission. With the script
written this week, next week is rehearsal (say it out loud against a
timer at least once) and the final submission writeup tying all 12 weeks
together.