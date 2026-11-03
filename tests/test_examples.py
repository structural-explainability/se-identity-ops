"""Tests that re-run the experiments and compare with recorded expectations.

These tests run the committed programs on the committed data. They fail if an
actual outcome stops matching a recorded expectation, or if a run stops
reproducing the committed result file byte for byte.
"""

import json
from pathlib import Path

import pytest

from se_identity_ops import parse, run_program
from se_identity_ops.expectations import compare

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

PROGRAMS = {
    "chicago": ["program"],
    "persistence": ["program"],
    "purl_authorities": ["program"],
    "sbom": ["known_bad", "known_good"],
}


# Predictions that were recorded first and not met. They stay reported as not met; this
# pins the list so a change in either direction is noticed.
MISSED_PREDICTIONS = {
    "purl_authorities": {
        "n_diff_py_js",
        "n_diff_py_go",
        "n_diff_js_go",
        "n_diff_go_js",
        "R5_go_separates_at_least_as_many_sets_as_python",
    },
}


def run_to_json(folder: Path, name: str) -> str:
    """Run an example program and return its serialized result."""
    path = folder / f"{name}.ido"
    run = run_program(parse(path.read_text(encoding="utf-8"), path.name), folder)
    return (
        json.dumps(run.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    )


@pytest.mark.parametrize("experiment", sorted(PROGRAMS))
def test_every_recorded_expectation_is_met_or_reported(experiment: str) -> None:
    """Every expectation is met, except the recorded misses that are pinned by name."""
    folder = EXAMPLES / experiment
    run_files = []
    for name in PROGRAMS[experiment]:
        target = (
            folder / "results" / ("run.json" if name == "program" else f"{name}.json")
        )
        run_files.append(target)
    findings = compare(folder / "expected.toml", run_files)
    assert findings, experiment
    bad = {f.name for f in findings if f.status not in ("met", "holds")}
    assert bad == MISSED_PREDICTIONS.get(experiment, set()), bad


@pytest.mark.parametrize(
    ("experiment", "name", "result_name"),
    [
        ("chicago", "program", "run.json"),
        ("persistence", "program", "run.json"),
        ("purl_authorities", "program", "run.json"),
        ("purl_authorities", "posthoc_validity", "posthoc_validity.json"),
        ("sbom", "known_bad", "known_bad.json"),
        ("sbom", "known_good", "known_good.json"),
    ],
)
def test_rerun_reproduces_the_committed_result_file(
    experiment: str, name: str, result_name: str
) -> None:
    """Running again gives exactly the committed JSON."""
    folder = EXAMPLES / experiment
    committed = (folder / "results" / result_name).read_text(encoding="utf-8")
    assert run_to_json(folder, name) == committed


def test_expected_files_were_committed_before_results() -> None:
    """The recorded order is visible in git: expected.toml precedes its results."""
    import subprocess

    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if shallow == "true":
        pytest.skip("shallow clone: the git history this check needs is not present")

    for experiment in PROGRAMS:
        added = subprocess.run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--format=%H",
                "--",
                f"examples/{experiment}/expected.toml",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split()
        results = subprocess.run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--format=%H",
                "--",
                f"examples/{experiment}/results",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split()
        if not added or not results:
            pytest.skip(
                "repository history not available (shallow copy or uncommitted results)"
            )
        order = subprocess.run(
            ["git", "rev-list", "--topo-order", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        assert order.index(added[-1]) > order.index(results[-1]), experiment
