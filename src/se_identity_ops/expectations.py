"""expectations.py - Compare recorded expectations with actual run output.

WHAT: Reads an `expected.toml` and one or more run JSON files, and reports for
      each expectation whether the actual outcome met it.
WHY: Expected results are recorded before a run. This module only compares; it
     does not change an expectation, drop a failed one, or soften a word.
HOW: `se-identity-ops expect expected.toml run.json [run2.json ...] --out report.json`
OBS: An expectation that is not met is reported as not met. Nothing here treats
     a missed prediction as a success.
OBS: Relations are small comparisons such as `label.count <= label.count`. They
     are parsed with a fixed pattern; no text is evaluated as code.
"""

from dataclasses import dataclass
import json
from pathlib import Path
import re
import tomllib

_REFERENCE = re.compile(r"^(?:(?P<program>[A-Za-z0-9_]+)\.)?(?P<label>[A-Za-z0-9_]+)\.(?P<field>[A-Za-z0-9_]+)$")
_COMPARISON = re.compile(r"^\s*(?P<left>\S+)\s*(?P<op><=|>=|==)\s*(?P<right>\S+)\s*$")


@dataclass(frozen=True, slots=True)
class Finding:
    """One comparison of an expectation with the actual output.

    Attributes:
        name: Expectation label or relation name.
        kind: Kind recorded in the expectation.
        status: "met", "not_met", "holds", "fails", or "unresolved".
        expected: Expected value or statement.
        actual: Actual value or evaluated statement.
    """

    name: str
    kind: str
    status: str
    expected: str
    actual: str


def _load_runs(paths: list[Path]) -> dict[str, dict]:
    """Load run JSON files keyed by file stem."""
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in paths}


def _result(run: dict, label: str, operation: str = "check") -> dict | None:
    """Return the result record with a label and operation, or None."""
    for found in run["results"]:
        if found["label"] == label and found["operation"] == operation:
            return found
    return None


def _operation_result(run: dict, label: str) -> dict | None:
    """Return the first non-explain result with a label, or None."""
    for found in run["results"]:
        if found["label"] == label and found["operation"] != "explain":
            return found
    return None


def _number(text: str, runs: dict[str, dict]) -> int | None:
    """Resolve a literal integer or a `program.label.field` reference."""
    if text.lstrip("-").isdigit():
        return int(text)
    match = _REFERENCE.match(text)
    if match is None:
        return None
    program = match.group("program")
    if program is None:
        if len(runs) != 1:
            return None
        run = next(iter(runs.values()))
    else:
        run = runs.get(program)
        if run is None:
            return None
    result = _operation_result(run, match.group("label"))
    if result is None:
        return None
    value = result["counts"].get(match.group("field"))
    return int(value) if value is not None else None


def _evaluate_relation(statement: str, runs: dict[str, dict]) -> tuple[bool | None, str]:
    """Evaluate `a OP b [and a OP b ...]`; return (holds, rendered)."""
    parts = [part.strip() for part in statement.split(" and ")]
    rendered: list[str] = []
    holds = True
    for part in parts:
        match = _COMPARISON.match(part)
        if match is None:
            return None, statement
        left = _number(match.group("left"), runs)
        right = _number(match.group("right"), runs)
        if left is None or right is None:
            return None, statement
        operator = match.group("op")
        if operator == "<=":
            truth = left <= right
        elif operator == ">=":
            truth = left >= right
        else:
            truth = left == right
        rendered.append(f"{left} {operator} {right}")
        holds = holds and truth
    return holds, " and ".join(rendered)


def compare(expected_path: Path, run_paths: list[Path]) -> list[Finding]:
    """Compare an expected.toml with run JSON files.

    Args:
        expected_path: Path to the expectations file.
        run_paths: Paths to run JSON files; the file stem names the run.

    Returns:
        One finding per expectation and per relation, in file order.
    """
    expected = tomllib.loads(expected_path.read_text(encoding="utf-8"))
    runs = _load_runs(run_paths)
    findings: list[Finding] = []
    for entry in expected.get("expect", []):
        program = Path(entry.get("program", "")).stem
        run = runs.get(program) if program else (next(iter(runs.values())) if len(runs) == 1 else None)
        name = f"{program}.{entry['label']}" if program else entry["label"]
        wanted = f"{entry['outcome']}/{entry['word']}"
        result = _operation_result(run, entry["label"]) if run is not None else None
        if result is None:
            findings.append(Finding(name, entry["kind"], "unresolved", wanted, "no such result"))
            continue
        actual = f"{result['outcome']}/{result['word']}"
        findings.append(
            Finding(name, entry["kind"], "met" if actual == wanted else "not_met", wanted, actual)
        )
    for relation in expected.get("relation", []):
        holds, rendered = _evaluate_relation(relation["statement"], runs)
        status = "unresolved" if holds is None else ("holds" if holds else "fails")
        findings.append(
            Finding(relation["name"], "relation", status, relation["statement"], rendered)
        )
    return findings


def to_json(findings: list[Finding]) -> str:
    """Serialize findings as deterministic JSON."""
    return (
        json.dumps(
            [
                {
                    "name": found.name,
                    "kind": found.kind,
                    "status": found.status,
                    "expected": found.expected,
                    "actual": found.actual,
                }
                for found in findings
            ],
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
