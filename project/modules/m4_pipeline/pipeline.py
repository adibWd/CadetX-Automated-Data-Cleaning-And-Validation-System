"""
MODULE 4 — PIPELINE ORCHESTRATION
---------------------------------
Chain Modules 1 -> 2 -> 3 into ONE runnable pipeline.

  python modules/m4_pipeline/pipeline.py --input data/raw/broadband_customers.csv

WHAT WAS BUILT (Week 4)
  - runs profiling -> cleaning -> validation in sequence, one CLI command
  - clear per-stage console logging + timing
  - fails fast with a readable error if a stage doesn't produce its
    contract file, instead of letting the NEXT stage crash later with a
    confusing FileNotFoundError several steps downstream
  - a minimal Dockerfile so "it runs anywhere" (see modules/m4_pipeline/Dockerfile)

Scope note (kept from the original brief): DVC, Git LFS, an NLP
classifier, and full CI are NOT implemented here -- solo, "runs
end-to-end with one command" satisfies the rubric. Noted as future work.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

MODULES = Path(__file__).resolve().parents[1]
sys.path.append(str(MODULES))
from common import PROFILING_REPORT, CLEANED_DATA, VALIDATION_REPORT  # noqa: E402


def run_stage(label: str, cmd: list[str], expect: Path) -> float:
    """Run one module as a subprocess.

    Checks the module's OWN exit code first, then checks that its
    contract file actually landed on disk -- a script can exit 0 without
    writing anything if, say, an argument was silently ignored. Fails
    fast and readably here rather than letting the next stage's
    FileNotFoundError be the first sign something went wrong.
    """
    print(f"\n=== {label} ===")
    print("  $ " + " ".join(cmd))
    start = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"✗ {label} failed (exit code {result.returncode}) after {elapsed:.1f}s")
        sys.exit(result.returncode)

    if not expect.exists():
        print(f"✗ {label} exited cleanly but never produced {expect}")
        sys.exit(1)

    try:
        shown_path = expect.relative_to(MODULES.parent)
    except ValueError:
        shown_path = expect  # not under the project root (e.g. in a test) -- show it as-is
    print(f"✔ {label} done in {elapsed:.1f}s -> {shown_path}")
    return elapsed


def main():
    parser = argparse.ArgumentParser(description="End-to-end data-quality pipeline (M1 -> M2 -> M3)")
    parser.add_argument("--input", required=True, help="Path to the raw CSV")
    parser.add_argument("--with-figures", action="store_true",
                         help="Also generate Module 1's profiling plots (slower, off by default)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"✗ Input file not found: {args.input}")
        sys.exit(1)

    py = sys.executable
    total_start = time.time()
    timings = {}

    profile_cmd = [py, str(MODULES / "m1_profiling" / "profiling_api.py"), "--input", args.input]
    if not args.with_figures:
        profile_cmd.append("--no-figures")
    timings["profile"] = run_stage("M1 Profile", profile_cmd, PROFILING_REPORT)

    clean_cmd = [py, str(MODULES / "m2_cleaning" / "clean.py"), "--input", args.input]
    timings["clean"] = run_stage("M2 Clean", clean_cmd, CLEANED_DATA)

    validate_cmd = [py, str(MODULES / "m3_validation" / "validate.py")]
    timings["validate"] = run_stage("M3 Validate", validate_cmd, VALIDATION_REPORT)

    total = time.time() - total_start
    print(f"\n✅ Pipeline complete in {total:.1f}s "
          f"(profile {timings['profile']:.1f}s, clean {timings['clean']:.1f}s, "
          f"validate {timings['validate']:.1f}s). Reports are in outputs/.")


if __name__ == "__main__":
    main()
