# Presentation Script — CadetX Final Demo

**Target length:** 8–10 minutes talk + `python demo.py` running live (~5s) + Q&A.
**Format:** live terminal demo (`demo.py`) + this script as speaker notes.
No slide deck needed for the demo itself — the terminal output IS the
visual. A short intro/close (2 slides max) covers what a terminal can't
show: the architecture diagram and the team-situation context.

---

## Slide 1 (optional, 30s) — What this is

> "Automated Data Cleaning & Validation System — a backend 'data
> gatekeeper' that profiles, cleans, and validates a dataset before
> anyone downstream trusts it. Four modules, each one reading the
> previous one's output as its input, so every stage is independently
> testable and runnable on its own."

Show the architecture diagram from `README.md` here (screenshot or open
the rendered GitHub page) — this is the one visual worth a static slide,
since the Mermaid diagram is the clearest single artifact for "how does
this fit together" and doesn't change turn to turn like the live numbers do.

**One honest line, said plainly, not dwelled on:**
> "The original plan was a 3-person team. That didn't happen after week
> one — I flagged it to CadetX support early and kept going solo with a
> modular design, so any part could be picked up if someone joined later.
> Everything from here on is my own work, end to end."

---

## Live demo — run `python demo.py` now

Let it run (~3–6 seconds). While it runs or right after each section
prints, narrate using the notes below. Don't read the terminal output
aloud verbatim — the audience can see it. Say what it *means*.

### STEP 1 — Pipeline runs
**Say:** "One command, three modules, real data — 1,000 customer rows
with deliberately planted quality problems."

### STEP 2 — What Module 1 found
**Say:** "Before touching anything, it profiles the raw data: flags PII
columns automatically, flags columns that look suspicious — mixed types,
very high cardinality — and flags exactly which columns have
inconsistent formats. This report is what every other module reads from,
not just this one printout."

### STEP 3 — What Module 2 fixed
**Say:** "Quality score before and after — that delta is the headline
number for this module. Behind it: 30 exact duplicate rows removed,
formats normalised across four columns, missing values imputed using
either statistics or a placeholder-and-flag for identifier columns like
email, never a fabricated value."

### STEP 4 — What Module 3 checked
**Say:** "A health score, an Isolation Forest anomaly scan across all
numeric columns jointly, and — this is the one I'd highlight if there's
time for only one — a check on whether `customer_id` is genuinely
unique. That's a different, stronger check than duplicate-row removal:
two rows can differ in every other column and still claim to be the same
customer. Confirmed clean on this dataset, but now it's *verified*, not
assumed."

### STEP 5 — Real bugs found
**This is the strongest part of the demo — spend the most time here.**
Five are listed; if time is short, pick **two**:

**Pick 1 (best technical story): the date-parsing corruption (Week 3).**
> "The obvious fix for UK dates is `dayfirst=True`. I tried that first.
> It's wrong — it fixes ambiguous dates like `03/04/2023`, but it *also*
> silently reinterprets already-unambiguous ISO dates the same way.
> `2024-12-05` — the 5th of December — got quietly corrupted to the 12th
> of May. I only caught this because I tested mixed-format columns
> directly, not because it looked wrong at a glance. The fix parses each
> date shape with its own explicit format instead of one global flag."

This one's worth leading with because it's a genuine "the obvious fix is
wrong" story — it shows testing methodology, not just a bug count.

**Pick 2 (best "silent failure is worse than a crash" story): Week 7.**
> "Module 1 crashing on an empty dataset was an easy bug to find — it's
> loud. The harder ones were in Modules 2 and 3: given the same bad
> input, they didn't crash. They exited successfully and reported
> `quality: nan -> nan`, or a health score of exactly 100 — which reads
> like a clean bill of health for data that was never actually checked
> at all. Those are worse than crashes because nothing flags them as
> wrong. Both now fail loudly instead."

**If there's time for a third:** the Week 9 `requirements.txt` finding —
"I actually built a fresh virtual environment and followed my own
README's setup instructions exactly, to check a new contributor's first
five minutes. It broke. Two dependencies I'd marked optional were
actually required." This one lands well because it shows verifying your
own documentation, not just your code.

---

## Closing (30s)

> "The full test suite is 63 tests across all four modules plus
> integration tests, all passing. Everything you just saw, you can run
> yourself with one command — `python demo.py` — no setup notes to
> maintain separately, because the README's own instructions are what
> the demo follows. Future work — an NLP-based semantic classifier, LOF
> anomaly detection, a couple of cross-column checks I investigated but
> didn't implement without more domain input — is documented in
> `docs/FUTURE_WORK.md` if anyone wants the detail."

---

## Anticipated Q&A

**"Why Isolation Forest and not something else for anomaly detection?"**
> Documented alternatives (LOF, Autoencoder, DBSCAN) in Future Work —
> short version: Isolation Forest needed no per-dataset tuning, which
> matters for staying dataset-agnostic; LOF is the next thing I'd add,
> it's a near drop-in replacement.

**"What would you do differently with more time?"**
> The `package`/`monthly_charges` tier-consistency check — I found real,
> tight price bands per package tier in the data, genuinely useful, but
> scoped it out because it needs one design decision I couldn't make
> unilaterally: hardcode today's price bands, or compute them fresh from
> whatever data comes in (so a legitimate future price change isn't
> flagged as an error).

**"How confident are you this generalises beyond this one dataset?"**
> Every rule is driven by Module 1's `semantic_type`/`inferred_type`
> metadata, never a hardcoded column name — verified this directly in
> Week 1 by running the same profiling code on an unrelated retail-sales
> dataset with zero changes. `modules/m1_profiling/demo.py` still runs
> that exact comparison if you want to see it live.

**"What was the hardest bug to track down?"**
> The date one (Week 3) — because the "obvious" fix looked completely
> correct until tested against a column with two different date shapes
> mixed together. It's the best example of why I test against the real
> planted-issue dataset instead of trusting a fix that looks right.