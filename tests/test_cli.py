"""Tests for the command line interface."""

import json
from pathlib import Path

import pytest

from se_identity_ops.cli import main

ROOT = Path(__file__).resolve().parent.parent
PERSISTENCE = ROOT / "examples" / "persistence"


def test_check_accepts_a_well_formed_program(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`check` reports statements and no diagnostics, and exits 0."""
    assert main(["check", str(PERSISTENCE / "program.ido")]) == 0
    assert "no diagnostics" in capsys.readouterr().out


def test_run_prints_one_line_per_operation_and_writes_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`run` prints each operation and writes deterministic JSON."""
    out = tmp_path / "run.json"
    assert main(["run", str(PERSISTENCE / "program.ido"), "--json", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "apply    a_g2" in printed
    assert "blocked" in printed
    assert json.loads(out.read_text(encoding="utf-8"))["program"] == "program.ido"


def test_expect_compares_and_writes_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`expect` prints each finding and writes them as JSON."""
    out = tmp_path / "findings.json"
    arguments = [
        "expect",
        str(PERSISTENCE / "expected.toml"),
        str(PERSISTENCE / "results" / "run.json"),
        "--out",
        str(out),
    ]
    assert main(arguments) == 0
    assert "not_met" not in capsys.readouterr().out
    assert json.loads(out.read_text(encoding="utf-8"))


def test_parse_errors_exit_with_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A parse error is reported on stderr with a line number and exit code 1."""
    bad = tmp_path / "bad.ido"
    bad.write_text("frobnicate x\n", encoding="utf-8")
    assert main(["check", str(bad)]) == 1
    assert "line 1" in capsys.readouterr().err


def test_static_diagnostics_exit_with_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A static diagnostic is reported and stops `run`."""
    bad = tmp_path / "bad.ido"
    bad.write_text("check c1 consistent nosuch\n", encoding="utf-8")
    assert main(["run", str(bad)]) == 1
    assert "unknown regime" in capsys.readouterr().err


def test_run_errors_exit_with_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing source file is a run error, not a result."""
    program = tmp_path / "p.ido"
    program.write_text(
        'source s file "missing.csv" sha256 "00"\ncarrier c from s key "row"\n',
        encoding="utf-8",
    )
    assert main(["run", str(program)]) == 1
    assert "source file not found" in capsys.readouterr().err
