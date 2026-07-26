"""
MODULE 4 — TEST SUITE
======================
Tests for the pipeline orchestrator itself (not the modules it calls --
those have their own test files). Focus: does run_stage fail correctly
when a stage misbehaves, and does the CLI reject bad input up front.

Run:  pytest tests/test_module4.py -v
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "modules" / "m4_pipeline"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "modules"))

from pipeline import run_stage


def test_run_stage_exits_when_subprocess_fails(tmp_path, capsys):
    """A stage that returns a non-zero exit code must stop the pipeline
    immediately (sys.exit), not silently continue to the next stage.
    """
    fake_output = tmp_path / "never_created.json"
    with pytest.raises(SystemExit) as exc_info:
        run_stage("Fake stage", [sys.executable, "-c", "import sys; sys.exit(1)"], fake_output)
    assert exc_info.value.code == 1


def test_run_stage_exits_when_contract_file_missing(tmp_path):
    """A stage that exits 0 but never writes its contract file must also
    stop the pipeline -- a silent no-op is as dangerous as a crash.
    """
    fake_output = tmp_path / "never_created.json"
    with pytest.raises(SystemExit) as exc_info:
        run_stage("Fake stage", [sys.executable, "-c", "pass"], fake_output)
    assert exc_info.value.code == 1


def test_run_stage_succeeds_when_file_is_produced(tmp_path):
    """Sanity check: a stage that exits 0 AND produces its file should
    NOT raise/exit, and should return a timing float.
    """
    target = tmp_path / "output.json"
    elapsed = run_stage(
        "Fake stage",
        [sys.executable, "-c", f"open(r'{target}', 'w').write('{{}}')"],
        target,
    )
    assert target.exists()
    assert elapsed >= 0


def test_cli_rejects_missing_input_file():
    """Running the CLI directly against a non-existent CSV should fail
    fast (exit 1) before any module is even invoked.
    """
    pipeline_path = Path(__file__).resolve().parents[1] / "modules" / "m4_pipeline" / "pipeline.py"
    result = subprocess.run(
        [sys.executable, str(pipeline_path), "--input", "data/raw/does_not_exist.csv"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "not found" in result.stdout.lower()
