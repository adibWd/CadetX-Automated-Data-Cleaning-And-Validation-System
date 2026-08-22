# Future Work

This project's core scope (Modules 1–4) is complete and tested. This
document records extensions that were considered, evaluated against the
real dataset where relevant, and deliberately scoped **out** of the
current build — either because a team of one, working to a 12-week
schedule, has to draw a line somewhere, or because they need a design
decision (not just an implementation) that the project doesn't have
enough information to make safely on its own.

Written in Week 8 in place of new code, per the project's rescoped plan
(the original brief's Week 8 slot was "optional ML method extensions" —
folded into this document instead of new features, given the solo team
situation).

---

## 1. ML-based anomaly detection beyond Isolation Forest

Module 3 currently uses **Isolation Forest** (`contamination=0.05`) as
its one anomaly-detection method. Candidates considered for extending it:

| Method | What it would add | Why it's not in the current build |
|---|---|---|
| **Local Outlier Factor (LOF)** | Density-based — flags points that are unusual *relative to their local neighbourhood*, not just globally. Would catch anomalies Isolation Forest misses in data with several distinct sub-populations (e.g. a `Fibre 900` customer billed like a `Fibre 100` customer might look "normal" globally but is a clear local outlier within its package tier). | Needs a decision on which columns to group by before running it (package? region?) — a design choice, not just a library swap. |
| **Autoencoder (small NN)** | Learns a compressed representation of "normal" rows and flags high reconstruction error. Can catch multi-column anomaly *patterns* that no single-column rule or tree-based method would (e.g. an unusual *combination* of otherwise-individually-plausible values). | Needs a training/validation split methodology and a much bigger runtime/dependency footprint (a deep learning framework) for a dataset this size — disproportionate for 1,000 rows. Worth it at real production scale, not here. |
| **DBSCAN clustering** | Would let anomalies be defined as "doesn't belong to any dense cluster" rather than needing a pre-set contamination rate. Removes the somewhat-arbitrary `contamination=0.05` assumption. | Needs `eps`/`min_samples` tuned per-dataset (no dataset-agnostic default) — conflicts with the project's dataset-agnostic design principle unless a robust auto-tuning step is added first. |

**Recommendation if this is picked up later:** LOF is the highest-value,
lowest-cost addition — it's a near-drop-in replacement for
`IsolationForest` in `anomaly_detection()` (same scikit-learn API shape)
and would specifically catch the "wrong price for this package tier"
class of anomaly noted in §3 below.

---

## 2. NLP-based semantic-type classifier for Module 1

Module 1 currently detects `semantic_type` (email/phone/postcode/
identifier/numeric/categorical/text) using **regex pattern-matching on
column values** (`metadata.py`). This works well for this dataset but has
a known limitation: it can't use the **column name** as a signal, and it
can't generalise beyond the specific patterns it's been given.

**What an NLP-based classifier would add:**
- Use column names as a feature (e.g. a column named `postal_code` with
  US-style ZIP values wouldn't match the current UK-postcode regex, but
  its *name* is an obvious hint)
- Generalise to semantic types not explicitly coded for (currency,
  country codes, IP addresses, etc.) via embedding similarity rather than
  a growing list of hand-written regexes
- Handle ambiguous cases with a confidence score instead of a hard
  yes/no match

**Why it's not in the current build:** this is a genuinely different
approach (a small classification model, however lightweight) rather than
an extension of the existing rule-based code — it needs its own training
data (or a pretrained model choice), its own evaluation methodology, and
a fallback story for when it disagrees with the regex approach. Right
scope for a dedicated module, not a Week 8 add-on to Module 1.

---

## 3. Cross-column consistency checks

Module 3 currently validates each column **independently** (format,
range, categorical membership, identifier uniqueness). It does not check
whether values that live in *different* columns are consistent with each
other. Two candidates were explored directly against the real dataset:

### a) `package` ↔ `monthly_charges` tier consistency

Each `package` tier has a real, tight expected price band once the
already-known negative-value bug (§ handled in Module 3's
`unexpected_negatives` check) is excluded:

| Package | Observed range (positive values only) |
|---|---|
| Fibre 100 | £28.03 – £34.93 |
| Fibre 300 | £43.00 – £49.99 |
| Fibre 500 | £52.99 – £59.95 |
| Fibre 900 | £63.05 – £69.97 |

This is a genuine, checkable business rule ("a `Fibre 100` customer
shouldn't be billed £55") that the current per-column range check can't
express, because it only knows one column's overall min/max, not a
range *conditional on another column's value*.

**Scoped out because:** this needs a design decision the project
shouldn't make unilaterally — are these tier bands fixed forever, or do
they change over time (price rises, promotions)? Hardcoding today's
observed bands as "the rule" risks flagging a legitimate future price
change as an error. The right implementation computes expected bands
*per package* from the data itself (e.g. IQR within each group) rather
than hardcoding today's numbers — straightforward to build, but it's new
scope, not a Week 8-sized addition.

### b) `churn` ↔ `tenure_months` plausibility

Investigated whether an implausible combination (e.g. "churned after 0
months" or "churned but tenure is 60+ months and still climbing") could
be a useful check. On the real data:

- 34 churned customers have `tenure_months` > 60
- 11 non-churned customers have `tenure_months` < 1

Both are **plausible in reality** (a long-tenured customer can still
churn; a brand-new customer can still be retained) — this is exactly why
this check is harder than it first looks. A naive rule here would
produce false positives on realistic data, not catch real errors.

**Scoped out because:** unlike the `package`/`monthly_charges` case,
there's no clean threshold to compute from the data — this needs
domain input (what tenure/churn combination is actually suspicious for
*this* business?) that the project doesn't have access to. Documented
here rather than implemented with a made-up threshold.

---

## Summary

| Idea | Verdict | Effort if picked up |
|---|---|---|
| LOF anomaly detection | Worth doing | Small — near drop-in |
| Autoencoder anomaly detection | Not worth it at this data scale | Large |
| DBSCAN anomaly detection | Interesting, needs auto-tuning first | Medium |
| NLP semantic-type classifier | Right idea, wrong scope for this project | Large (new subsystem) |
| `package`/`monthly_charges` tier check | Concretely useful, needs one design decision (fixed vs. data-derived bands) | Small–Medium |
| `churn`/`tenure_months` plausibility check | Investigated, genuinely ambiguous without domain input | N/A — needs a person, not just code |