"""Tests that each adapter record matches what the experiments actually used.

An adapter record (adapter.toml) names an external authority, its version, and the
evidence it produced. These tests make that record checkable: a changed library
version, a changed pin, or a table that no longer follows the library fails here.
"""

import csv
from importlib.metadata import version
import json
from pathlib import Path
import re
import tomllib

from packageurl import PackageURL

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
REQUIRED = {
    "id",
    "authority",
    "implementation",
    "version",
    "operation",
    "input_evidence",
    "output_evidence",
    "limitations",
}


def adapters(experiment: str) -> list[dict]:
    """Return the adapter records of one experiment."""
    path = EXAMPLES / experiment / "adapter.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))["adapter"]


def test_every_adapter_record_is_complete() -> None:
    """Each record names authority, implementation, version, operation, evidence, limits."""
    for experiment in ("sbom", "chicago", "purl_authorities"):
        for record in adapters(experiment):
            assert not REQUIRED - set(record), (experiment, record["id"])
            assert record["limitations"], (experiment, record["id"])


def test_recorded_purl_library_version_is_the_installed_one() -> None:
    """The version in adapter.toml is the version that normalized the tables."""
    (record,) = adapters("sbom")
    assert record["implementation"] == "packageurl-python"
    assert record["version"] == version("packageurl-python")


def test_purl_tables_follow_the_library() -> None:
    """canonical_purl is the library's output for original_purl; none was rejected."""
    for case in ("known_bad", "known_good"):
        path = EXAMPLES / "sbom" / "data" / f"components_{case}.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        for row in rows:
            assert row["purl_errors"] == "", (case, row["frame"])
            originals = [p for p in row["original_purl"].split("|") if p]
            expected = sorted(
                {PackageURL.from_string(p).to_string() for p in originals}
            )
            # any_slot_purl covers the slot and the properties, i.e. every original.
            assert [p for p in row["any_slot_purl"].split("|") if p] == expected


def test_chicago_adapter_input_pin_matches_the_program() -> None:
    """The data digest in the adapter record is the digest the program pins."""
    program = (EXAMPLES / "chicago" / "program.ido").read_text(encoding="utf-8")
    pinned = re.search(r'sha256 "([0-9a-f]{64})"', program)
    assert pinned
    vendor = next(a for a in adapters("chicago") if a["id"] == "vendor_id")
    assert pinned.group(1) in vendor["input_evidence"]


def test_purl_authorities_records_match_the_runs() -> None:
    """The versions in adapter.toml are the versions the committed run recorded."""
    records = {a["id"]: a for a in adapters("purl_authorities")}
    assert records["purl_python"]["version"] == version("packageurl-python")
    recorded = json.loads(
        (EXAMPLES / "purl_authorities/results/implementations.json").read_text(
            encoding="utf-8"
        )
    )["versions"]
    assert recorded == {
        "py": f"packageurl-python {records['purl_python']['version']}",
        "js": f"packageurl-js {records['purl_js']['version']}",
        "go": f"packageurl-go {records['purl_go']['version']}",
    }
    lock = json.loads(
        (EXAMPLES / "purl_authorities/drivers/js/package-lock.json").read_text(
            encoding="utf-8"
        )
    )["packages"]["node_modules/packageurl-js"]
    assert lock["version"] == records["purl_js"]["version"]
    assert lock["integrity"] == records["purl_js"]["integrity"]
    go_sum = (EXAMPLES / "purl_authorities/drivers/go/go.sum").read_text(
        encoding="utf-8"
    )
    assert records["purl_go"]["go_sum_h1"] in go_sum


def test_purl_authorities_program_pins_the_table() -> None:
    """Both programs pin the digest of the table that run_drivers.py wrote."""
    import hashlib

    folder = EXAMPLES / "purl_authorities"
    digest = hashlib.sha256(
        (folder / "data/purl_authorities.csv").read_bytes()
    ).hexdigest()
    for name in ("program.ido", "posthoc_validity.ido"):
        assert digest in (folder / name).read_text(encoding="utf-8")


def test_purl_authorities_program_names_no_implementation() -> None:
    """The substitution is a change of columns: the program has no library names in statements."""
    program = (EXAMPLES / "purl_authorities/program.ido").read_text(encoding="utf-8")
    code = [
        line
        for line in program.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "meaning", "note"))
    ]
    assert not [line for line in code if "packageurl" in line]
