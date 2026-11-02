"""Tests that run the LACE-style clingo encodings and check their agreement.

The encodings are my own plain-clingo versions of LACE-style semantics. They are
not ASPEN or ASPEN+. These tests check that the encodings and the interpreter
agree on the cases in lace/run_lace.py; they do not establish that LACE and
IdentityOps agree in general.
"""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def test_lace_encodings_agree_with_the_interpreter_on_every_case_run() -> None:
    """Run lace/run_lace.py and require zero mismatches and agreement everywhere."""
    completed = subprocess.run(
        [sys.executable, str(ROOT / "lace" / "run_lace.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads((ROOT / "lace" / "results" / "lace_attempts.json").read_text(encoding="utf-8"))
    assert report["status_open_world"]["mismatch_count"] == 0
    assert report["status_open_world"]["compared_pairs"] == 27 * 3 + 729 * 6
    for body in report["chicago_audit"].values():
        assert body["agree"] is True
    for body in report["sbom_audit"].values():
        assert body["agree"] is True
    assert report["persistence_gate"]["all_expressible_steps_agree"] is True
    inexpressible = [s for s in report["persistence_gate"]["steps"] if s["agree"] is None]
    assert len(inexpressible) == 4  # a_f1, a_f2 (ign), a_split (brk), a_reorder (na)
