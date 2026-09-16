"""
FINAL DEMO — END-TO-END WALKTHROUGH
====================================
Runs the full pipeline (M1 -> M2 -> M3) on the real dataset and prints a
presentation-friendly summary: what went in, what came out, and the real
bugs this project found along the way.

Run:  python demo.py
(from the project root — same place you'd run `make pipeline`)

This supersedes the Week-1 demo.py (relocated to
modules/m1_profiling/demo.py, still runnable on its own), which only
demonstrated Module 1 on tiny hand-written sample data. This demo runs
the REAL dataset through the REAL pipeline and reports REAL numbers —
nothing here is staged.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DATA = ROOT / "data" / "raw" / "broadband_customers.csv"
OUTPUTS = ROOT / "outputs"


def section(title: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


def run_pipeline() -> None:
    section("STEP 1 — Run the full pipeline (one command)")
    print(f"$ python modules/m4_pipeline/pipeline.py --input {RAW_DATA.relative_to(ROOT)}\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "modules" / "m4_pipeline" / "pipeline.py"),
         "--input", str(RAW_DATA)],
    )
    if result.returncode != 0:
        print("\n✗ Pipeline failed — stopping demo.")
        sys.exit(1)


def load(name: str) -> dict:
    with open(OUTPUTS / name, encoding="utf-8") as f:
        return json.load(f)


def show_profiling_summary() -> None:
    section("STEP 2 — What Module 1 found in the raw data")
    report = load("profiling_report.json")
    print(f"Rows profiled:        {report['dataset']['rows']}")
    print(f"PII columns flagged:  {list(report['rules']['potential_pii'].keys())}")
    print(f"Suspicious columns:   {report['rules']['suspicious_columns']}")
    print(f"Inconsistent formats: {list(report['rules']['inconsistent_formats'].keys())}")


def show_cleaning_summary() -> None:
    section("STEP 3 — What Module 2 fixed")
    log = load("cleaning_log.json")
    print(f"Quality score: {log['quality_score_before']} -> {log['quality_score_after']} "
          f"(delta {log['quality_delta']})")
    for action in log["actions"]:
        if action["step"] == "drop_duplicates":
            print(f"  - Removed {action['exact_duplicates_removed']} exact duplicate rows")
        elif action["step"] == "normalise":
            changed_cols = list(action["details"].keys())
            print(f"  - Normalised formats in: {changed_cols}")
        elif action["step"] == "impute_missing":
            imputed_cols = [entry["column"] for entry in action["details"]]
            print(f"  - Imputed missing values in: {imputed_cols}")


def show_validation_summary() -> None:
    section("STEP 4 — What Module 3 checked and found")
    report = load("validation_report.json")
    print(f"Health score: {report['health_score']}")
    anomalies = report["anomaly_detection"]
    print(f"Anomalies flagged: {anomalies['anomalies']} / {anomalies['checked']} rows "
          f"({anomalies.get('anomaly_pct')}%)")

    print("\nNotable rule results:")
    rules = report["rule_based"]
    for col in ("monthly_charges__negatives", "tenure_months__negatives", "customer_id"):
        if col in rules:
            r = rules[col]
            print(f"  - {r['rule']}: {r['invalid']} / {r['checked']} flagged")


def show_bugs_found() -> None:
    section("STEP 5 — Real bugs this project found (the actual story)")
    bugs = [
        ("Week 3", "phone/numeric_as_text miscoercion",
         "A phone column got flagged 'numeric_as_text' by Module 1 (most "
         "values look like digit strings) alongside its real semantic_type "
         "'phone'. Naive handling coerced phone numbers to float, "
         "destroying leading zeros. Fixed by requiring semantic_type == "
         "'numeric' before applying currency-strip conversion."),
        ("Week 3", "date-parsing corruption",
         "pd.to_datetime(..., dayfirst=True) fixes ambiguous UK slash-dates "
         "but silently corrupts unambiguous ISO dates when both shapes "
         "appear in the same column ('2024-12-05' -> wrongly became "
         "'2024-05-12'). Fixed with explicit per-shape parsing."),
        ("Week 6", "empty-dataset crash (Module 1)",
         "A header-only CSV crashed with a raw ZeroDivisionError deep "
         "inside profiling_engine.py. Fixed with a clear guard and message."),
        ("Week 7", "empty-dataset silent bad output (Modules 2 & 3)",
         "Worse than a crash: Module 2 silently reported "
         "'quality: nan -> nan' and exited 0; Module 3 silently reported "
         "a misleading 'health score: 100.0' for zero rows checked. "
         "Both now fail loudly instead."),
        ("Week 9", "requirements.txt missing hard dependencies",
         "seaborn and pytest were listed as 'optional' but are actually "
         "required — verified in a genuinely clean virtual environment "
         "that a new contributor following the README exactly would hit "
         "ModuleNotFoundError on their first run."),
    ]
    for week, title, desc in bugs:
        print(f"\n[{week}] {title}")
        print(f"  {desc}")


def main():
    if not RAW_DATA.exists():
        print(f"✗ Dataset not found: {RAW_DATA}")
        sys.exit(1)

    run_pipeline()
    show_profiling_summary()
    show_cleaning_summary()
    show_validation_summary()
    show_bugs_found()

    section("DONE")
    print("Full reports are in outputs/. See README.md for the complete")
    print("architecture, and docs/FUTURE_WORK.md for what's next.")


if __name__ == "__main__":
    main()