"""verify_independent.py - Recompute Experiment A without the interpreter.

WHAT: Recomputes every count the interpreter reported for Experiment A in two
      independent ways (plain Python dictionaries and an in-memory SQLite
      database), compares both with results/run.json, and replays every example
      the interpreter reported.
WHY: The interpreter should not be the only evidence for its own output.
HOW: python examples/chicago/verify_independent.py
OBS: This script imports nothing from se_identity_ops. It reads only the
     observation CSV and the run JSON.
OBS: It also writes a post-hoc breakdown of the cross-class groups. That
     breakdown was not among the recorded expectations; it is exploratory.
"""

import csv
from collections import defaultdict
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

HERE = Path(__file__).parent
DATA = HERE / "data" / "vendors_20k_observed.csv"
RUN = HERE / "results" / "run.json"
OUT = HERE / "results" / "independent_verification.json"

SURFACES = {
    "a_faithful_localized": "localized_name",
    "a_faithful_raw": "vendor_name",
    "c_pos_faithful": "vendor_id",
    "c_neg_faithful": "row",
}
COLLISIONS = {
    "a_collisions_localized": "localized_name",
    "a_collisions_raw": "vendor_name",
    "c_pos_collisions": "vendor_id",
}


def read_rows() -> list[dict[str, str]]:
    """Read the observation CSV in file order."""
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def faithful_counts_python(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    """Count related classes and classes split by a column, by plain Python."""
    first_value: dict[str, str] = {}
    size: dict[str, int] = defaultdict(int)
    split: set[str] = set()
    divergent_items = 0
    for row in rows:
        key = row["vendor_id"]
        size[key] += 1
        if key not in first_value:
            first_value[key] = row[column]
        elif row[column] != first_value[key]:
            divergent_items += 1
            split.add(key)
    return {
        "divergent_classes": len(split),
        "divergent_items": divergent_items,
        "items": len(rows),
        "related_classes": sum(1 for count in size.values() if count >= 2),
    }


def collision_counts_python(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    """Count surface groups and cross-class groups, by plain Python."""
    members: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        members[row[column]].append(row["vendor_id"])
    merging = [ids for ids in members.values() if len(ids) >= 2]
    cross = [len(set(ids)) for ids in merging if len(set(ids)) > 1]
    return {
        "cross_class_groups": len(cross),
        "cross_class_pairs": sum(k * (k - 1) // 2 for k in cross),
        "merging_groups": len(merging),
        "required_groups": len(merging) - len(cross),
        "surface_values": len(members),
    }


def build_database(rows: list[dict[str, str]]) -> sqlite3.Connection:
    """Load the rows into an in-memory SQLite table."""
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE v (n INTEGER PRIMARY KEY, row TEXT, vendor_id TEXT, vendor_name TEXT, localized_name TEXT)"
    )
    connection.executemany(
        "INSERT INTO v (n, row, vendor_id, vendor_name, localized_name) VALUES (?, ?, ?, ?, ?)",
        [
            (number, row["row"], row["vendor_id"], row["vendor_name"], row["localized_name"])
            for number, row in enumerate(rows, start=1)
        ],
    )
    return connection


def faithful_counts_sql(connection: sqlite3.Connection, column: str) -> dict[str, int]:
    """Count related classes and classes split by a column, by SQL."""
    divergent_items = connection.execute(
        f"""
        SELECT COUNT(*) FROM v
        JOIN (SELECT vendor_id AS id, MIN(n) AS first_n FROM v GROUP BY vendor_id) f
          ON v.vendor_id = f.id AND v.n > f.first_n
        JOIN v AS anchor ON anchor.n = f.first_n
        WHERE v.{column} <> anchor.{column}
        """
    ).fetchone()[0]
    divergent_classes = connection.execute(
        f"""
        SELECT COUNT(DISTINCT v.vendor_id) FROM v
        JOIN (SELECT vendor_id AS id, MIN(n) AS first_n FROM v GROUP BY vendor_id) f
          ON v.vendor_id = f.id AND v.n > f.first_n
        JOIN v AS anchor ON anchor.n = f.first_n
        WHERE v.{column} <> anchor.{column}
        """
    ).fetchone()[0]
    related = connection.execute(
        "SELECT COUNT(*) FROM (SELECT vendor_id FROM v GROUP BY vendor_id HAVING COUNT(*) >= 2)"
    ).fetchone()[0]
    items = connection.execute("SELECT COUNT(*) FROM v").fetchone()[0]
    return {
        "divergent_classes": divergent_classes,
        "divergent_items": divergent_items,
        "items": items,
        "related_classes": related,
    }


def collision_counts_sql(connection: sqlite3.Connection, column: str) -> dict[str, int]:
    """Count surface groups and cross-class groups, by SQL."""
    surface_values = connection.execute(f"SELECT COUNT(DISTINCT {column}) FROM v").fetchone()[0]
    merging = connection.execute(
        f"SELECT COUNT(*) FROM (SELECT {column} FROM v GROUP BY {column} HAVING COUNT(*) >= 2)"
    ).fetchone()[0]
    per_group = connection.execute(
        f"""
        SELECT COUNT(DISTINCT vendor_id) FROM v
        GROUP BY {column} HAVING COUNT(*) >= 2 AND COUNT(DISTINCT vendor_id) > 1
        """
    ).fetchall()
    cross = [entry[0] for entry in per_group]
    return {
        "cross_class_groups": len(cross),
        "cross_class_pairs": sum(k * (k - 1) // 2 for k in cross),
        "merging_groups": merging,
        "required_groups": merging - len(cross),
        "surface_values": surface_values,
    }


def result_counts(run: dict, label: str) -> dict[str, int]:
    """Return the counts the interpreter reported for a check label."""
    for result in run["results"]:
        if result["label"] == label and result["operation"] == "check":
            return result["counts"]
    raise KeyError(label)


def result_witness(run: dict, label: str) -> dict[str, str]:
    """Return the witness fields the interpreter reported for a check label."""
    for result in run["results"]:
        if result["label"] == label and result["operation"] == "check":
            return result["explanation"]["witness"]
    raise KeyError(label)


def replay_faithful(rows_by_key: dict[str, dict[str, str]], witness: dict[str, str], column: str) -> list[str]:
    """Check each reported divergence example against the rows; return problems."""
    problems: list[str] = []
    for tag in sorted({name.split(".")[0] for name in witness if name.startswith("example_")}):
        first = rows_by_key[witness[f"{tag}.first"]]
        second = rows_by_key[witness[f"{tag}.second"]]
        if first["vendor_id"] != second["vendor_id"]:
            problems.append(f"{tag}: items do not share a Vendor ID")
        if first[column] != witness[f"{tag}.first_value"] or second[column] != witness[f"{tag}.second_value"]:
            problems.append(f"{tag}: reported values differ from the data")
        if first[column] == second[column]:
            problems.append(f"{tag}: values are equal, so this is not a divergence")
    return problems


def replay_collisions(rows_by_key: dict[str, dict[str, str]], witness: dict[str, str], column: str) -> list[str]:
    """Check each reported collision example against the rows; return problems."""
    problems: list[str] = []
    for tag in sorted({name.split(".")[0] for name in witness if name.startswith("example_")}):
        first = rows_by_key[witness[f"{tag}.first"]]
        second = rows_by_key[witness[f"{tag}.second"]]
        if first[column] != second[column] or first[column] != witness[f"{tag}.surface_value"]:
            problems.append(f"{tag}: surface values are not equal to the reported value")
        if first["vendor_id"] == second["vendor_id"]:
            problems.append(f"{tag}: items share a Vendor ID, so this is not a cross-class merge")
        if (first["vendor_id"], second["vendor_id"]) != (witness[f"{tag}.first_key"], witness[f"{tag}.second_key"]):
            problems.append(f"{tag}: reported keys differ from the data")
    return problems


def breakdown(rows: list[dict[str, str]]) -> dict[str, object]:
    """Classify localized cross-class groups by whether raw names already agree.

    A group is `raw_equal` when every row in it has the same raw vendor name
    across at least two Vendor IDs (the same raw name is published under several
    IDs). It is `localization_induced` when at least two different raw names in
    the group map to one localized name across different Vendor IDs.
    """
    members: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in rows:
        members[row["localized_name"]].append((row["vendor_id"], row["vendor_name"]))
    raw_equal = 0
    induced = 0
    induced_examples: list[dict[str, object]] = []
    for localized, entries in sorted(members.items()):
        ids = {vendor_id for vendor_id, _name in entries}
        if len(entries) < 2 or len(ids) < 2:
            continue
        by_id: dict[str, set[str]] = defaultdict(set)
        for vendor_id, name in entries:
            by_id[vendor_id].add(name)
        raw_names = {name for names in by_id.values() for name in names}
        if len(raw_names) == 1:
            raw_equal += 1
        else:
            induced += 1
            if len(induced_examples) < 8:
                induced_examples.append(
                    {"localized": localized, "raw_names": sorted(raw_names), "vendor_ids": sorted(ids)}
                )
    return {
        "cross_class_groups": raw_equal + induced,
        "localization_induced": induced,
        "raw_equal": raw_equal,
        "induced_examples": induced_examples,
    }


def git_order() -> dict[str, str]:
    """Report which commit added expected.toml and whether results are committed yet."""
    root = HERE.parent.parent
    added = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", "examples/chicago/expected.toml"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "examples/chicago/results/run.json"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "expected_added_in_commit": added or "not committed",
        "results_already_committed": "yes" if tracked.returncode == 0 else "no (committed after verification)",
    }


def main() -> int:
    """Run all comparisons and write the verification report."""
    rows = read_rows()
    rows_by_key = {row["row"]: row for row in rows}
    run = json.loads(RUN.read_text(encoding="utf-8"))
    connection = build_database(rows)
    report: dict[str, object] = {"rows": len(rows), "comparisons": [], "replay_problems": [], "git": git_order()}
    comparisons: list[dict[str, object]] = []
    for label, column in SURFACES.items():
        python_counts = faithful_counts_python(rows, column)
        sql_counts = faithful_counts_sql(connection, column)
        reported = {name: result_counts(run, label)[name] for name in python_counts}
        comparisons.append(
            {
                "label": label,
                "python": python_counts,
                "sql": sql_counts,
                "interpreter": reported,
                "agree": python_counts == sql_counts == reported,
            }
        )
    for label, column in COLLISIONS.items():
        python_counts = collision_counts_python(rows, column)
        sql_counts = collision_counts_sql(connection, column)
        reported = {name: result_counts(run, label)[name] for name in python_counts}
        comparisons.append(
            {
                "label": label,
                "python": python_counts,
                "sql": sql_counts,
                "interpreter": reported,
                "agree": python_counts == sql_counts == reported,
            }
        )
    report["comparisons"] = comparisons
    problems: list[str] = []
    problems += replay_faithful(rows_by_key, result_witness(run, "a_faithful_localized"), "localized_name")
    problems += replay_faithful(rows_by_key, result_witness(run, "a_faithful_raw"), "vendor_name")
    problems += replay_collisions(rows_by_key, result_witness(run, "a_collisions_localized"), "localized_name")
    problems += replay_collisions(rows_by_key, result_witness(run, "a_collisions_raw"), "vendor_name")
    report["replay_problems"] = problems
    report["post_hoc_breakdown_not_a_recorded_expectation"] = breakdown(rows)
    report["all_agree"] = all(item["agree"] for item in comparisons) and not problems
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in comparisons:
        sys.stdout.write(f"{item['label']:26} {'agree' if item['agree'] else 'DISAGREE'}\n")
    sys.stdout.write(f"replay problems: {len(problems)}\n")
    sys.stdout.write(f"git: {report['git']}\n")
    sys.stdout.write(f"all agree: {report['all_agree']}\n")
    return 0 if report["all_agree"] else 1


if __name__ == "__main__":
    sys.exit(main())
