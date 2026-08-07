"""
INTEGRATION TESTS — Week 6
===========================
Subprocess-level tests for each module's actual CLI (main()), the part
the per-module unit test files deliberately don't cover (see the
Testing section in the main README). These are slower (they spawn real
Python processes and touch real files under outputs/ and
data/processed/) but they're what actually proves "this runs as a
command", not just "these functions return the right values".

Run:  pytest tests/test_integration.py -v
"""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES = PROJECT_ROOT / "modules"
REAL_DATASET = PROJECT_ROOT / "data" / "raw" / "broadband_customers.csv"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


@pytest.mark.skipif(not REAL_DATASET.exists(), reason="committed dataset not found")
def test_full_pipeline_cli_succeeds_on_committed_dataset():
    """The actual command a user runs. If this fails, nothing else matters."""
    result = run(str(MODULES / "m4_pipeline" / "pipeline.py"), "--input", str(REAL_DATASET))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Pipeline complete" in result.stdout

    assert (PROJECT_ROOT / "outputs" / "profiling_report.json").exists()
    assert (PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv").exists()
    assert (PROJECT_ROOT / "outputs" / "cleaning_log.json").exists()
    assert (PROJECT_ROOT / "outputs" / "validation_report.json").exists()


@pytest.mark.skipif(not REAL_DATASET.exists(), reason="committed dataset not found")
def test_m2_cli_runs_standalone_after_m1(tmp_path):
    """Module 2 must be runnable on its own (not just via the M4 pipeline),
    as long as Module 1 has already produced profiling_report.json.
    """
    profile = run(str(MODULES / "m1_profiling" / "profiling_api.py"),
                   "--input", str(REAL_DATASET), "--no-figures")
    assert profile.returncode == 0, profile.stdout + profile.stderr

    result = run(str(MODULES / "m2_cleaning" / "clean.py"), "--input", str(REAL_DATASET))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[M2] Done." in result.stdout


@pytest.mark.skipif(not REAL_DATASET.exists(), reason="committed dataset not found")
def test_m3_cli_runs_standalone_after_m2():
    """Module 3 must be runnable on its own, as long as Module 2 has
    already produced cleaned_data.csv (defaults to that path itself).
    """
    result = run(str(MODULES / "m3_validation" / "validate.py"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[M3] Done." in result.stdout


def test_m1_cli_fails_cleanly_on_a_zero_row_csv(tmp_path):
    """Regression test for a real bug found during Week 6 robustness
    testing: profiling a header-only (zero-row) CSV used to crash deep
    inside profiling_engine.py with a bare ZeroDivisionError. It must now
    fail with ONE readable line and a non-zero exit code -- no traceback.
    """
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("customer_id,email,age\n")  # header only, 0 data rows

    result = run(str(MODULES / "m1_profiling" / "profiling_api.py"),
                 "--input", str(empty_csv), "--no-figures")

    assert result.returncode != 0
    assert "Traceback" not in result.stdout
    assert "empty dataset" in (result.stdout + result.stderr).lower()


def test_m4_pipeline_stops_at_stage_one_for_a_zero_row_csv(tmp_path):
    """The fail-fast contract from Module 4, exercised end-to-end: a
    stage-1 failure must stop the pipeline immediately -- M2 and M3
    should never even be attempted.
    """
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("customer_id,email,age\n")

    result = run(str(MODULES / "m4_pipeline" / "pipeline.py"), "--input", str(empty_csv))

    assert result.returncode != 0
    assert "M1 Profile failed" in result.stdout
    assert "M2 Clean" not in result.stdout  # never reached
    assert "M3 Validate" not in result.stdout  # never reached