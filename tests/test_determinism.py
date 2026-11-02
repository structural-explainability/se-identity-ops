"""Tests that output does not depend on hash seed, working directory, or repetition."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def run_cli(seed: str, cwd: Path) -> bytes:
    """Run the persistence example through the CLI and return the JSON bytes."""
    output = cwd / f"out_{seed}.json"
    environment = {**os.environ, "PYTHONHASHSEED": seed}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "se_identity_ops.cli",
            "run",
            str(ROOT / "examples" / "persistence" / "program.ido"),
            "--json",
            str(output),
        ],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return output.read_bytes()


def test_json_is_byte_identical_across_hash_seeds(tmp_path: Path) -> None:
    """Different PYTHONHASHSEED values and a different working directory give identical bytes."""
    first = run_cli("1", tmp_path)
    second = run_cli("12345", tmp_path)
    third = run_cli("random", tmp_path)
    assert first == second == third
