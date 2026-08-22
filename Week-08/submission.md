# Week 08 — Submission

**Sprint dates:** _15 Aug 2026 → 22 Aug 2026_
**Maintainer this week:** [Your name] — solo

## What I did this week

Per the rescoped Week 5 plan, folded the original brief's Week 8 slot
("future work" ML extensions) into documentation rather than new code —
the honest call for a solo maintainer at this point in the schedule,
and it keeps every remaining week's scope realistic.

### `docs/FUTURE_WORK.md`

Three areas, each investigated against the real dataset rather than left
as vague ideas:

1. **ML-based anomaly detection beyond Isolation Forest** — evaluated LOF,
   Autoencoder, and DBSCAN as alternatives/additions. Recommendation: LOF
   is the highest-value, lowest-cost pickup (near drop-in for the current
   `anomaly_detection()` function) since it would specifically catch the
   package-tier billing anomaly described below, which a global method
   like Isolation Forest is less suited to.

2. **NLP-based semantic-type classifier for Module 1** — scoped as a
   genuinely separate subsystem (own training data / model choice / eval
   methodology), not a Week 8-sized addition to the existing regex-based
   `metadata.py`.

3. **Cross-column consistency checks** — investigated two concrete
   candidates directly against the cleaned dataset:
   - `package` ↔ `monthly_charges`: confirmed each package tier has a
     real, tight price band (e.g. Fibre 100: £28.03–£34.93) once the
     already-known negative-value bug is excluded. Genuinely useful,
     scoped out only because of one open design question (should the
     bands be hardcoded or computed per-group from the data, to avoid
     flagging legitimate future price changes as errors).
   - `churn` ↔ `tenure_months`: checked for implausible combinations
     (34 churned customers with 60+ months tenure, 11 non-churned with
     <1 month) — both are realistic, which is exactly why a naive
     threshold-based rule here would produce false positives without
     real domain input this project doesn't have access to.

### README update

Added a link to `docs/FUTURE_WORK.md` from the main README so it's
discoverable, not just sitting in `docs/` unreferenced.

## Progress against plan

- [x] Documented ML-based anomaly detection extensions (LOF/Autoencoder/
      DBSCAN), with a concrete recommendation
- [x] Documented the NLP semantic-type classifier idea and why it's
      out of scope for this project
- [x] Investigated (not just brainstormed) two cross-column consistency
      check candidates against the real data, with actual numbers
- [x] Linked from the main README

## Blockers

None.

## Next week

Week 9 (documentation polish / per-module write-ups) is largely already
done — per-module READMEs were pulled forward into Week 5. Week 9 will
instead focus on a pass over all documentation for accuracy (confirm
every command in every README still matches the actual current code
after 7 weeks of changes) and closing any remaining gaps before the
Week 10 demo build.