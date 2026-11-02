"""verify_independent.py - Recompute Experiment D's counts without the interpreter.

WHAT: Reads corpus.csv and the raw driver outputs in results/implementations.json,
      recomputes (1) how many declared spelling sets each implementation separates,
      (2) how many classes of one implementation another separates, and (3) which
      rows two implementations disagree on for validity, then compares (1) and (2)
      with results/run.json.
WHY: The IdentityOps counts should agree with a plain recomputation from the raw
     driver outputs, or the disagreement should be visible.
HOW: python examples/purl_authorities/verify_independent.py
OBS: Imports nothing from se_identity_ops. It does not use data/purl_authorities.csv,
     so a mistake in assembling that table would show up as a disagreement.
OBS: A rejected input is a singleton for a criterion and a shared marker only inside
     one declared set, as in run_drivers.py.
"""

import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).parent
IMPLEMENTATIONS = ("py", "js", "go")


def separated_classes(groups: dict[str, list[str]], value: dict[str, str]) -> int:
    """Return how many groups of two or more rows hold more than one value."""
    return sum(
        1
        for rows in groups.values()
        if len(rows) > 1 and len({value[row] for row in rows}) > 1
    )


def main() -> int:
    """Recompute, compare, and write the verification record."""
    with (HERE / "corpus.csv").open(encoding="utf-8", newline="") as handle:
        corpus = list(csv.DictReader(handle))
    report = json.loads(
        (HERE / "results/implementations.json").read_text(encoding="utf-8")
    )
    run = json.loads((HERE / "results/run.json").read_text(encoding="utf-8"))
    counts = {
        item["label"]: item["counts"]
        for item in run["results"]
        if item["operation"] == "check"
    }
    outputs = {
        name: {entry["row"]: entry[name] for entry in report["results"]}
        for name in IMPLEMENTATIONS
    }
    set_of = {record["row"]: record["set_id"] for record in corpus}
    sets: dict[str, list[str]] = {}
    for record in corpus:
        sets.setdefault(record["set_id"], []).append(record["row"])

    def set_value(name: str, row: str) -> str:
        result = outputs[name][row]
        return result["output"] if result["ok"] else f"REJECTED:{set_of[row]}"

    def row_value(name: str, row: str) -> str:
        result = outputs[name][row]
        return result["output"] if result["ok"] else f"REJECTED:{row}"

    comparisons = []
    for name in IMPLEMENTATIONS:
        values = {record["row"]: set_value(name, record["row"]) for record in corpus}
        mine = separated_classes(sets, values)
        comparisons.append(
            {
                "label": f"n_{name}_spec",
                "independent": mine,
                "interpreter": counts[f"n_{name}_spec"]["divergent_classes"],
            }
        )
    for first in IMPLEMENTATIONS:
        classes: dict[str, list[str]] = {}
        for record in corpus:
            classes.setdefault(row_value(first, record["row"]), []).append(
                record["row"]
            )
        for second in IMPLEMENTATIONS:
            if first == second:
                continue
            values = {
                record["row"]: row_value(second, record["row"]) for record in corpus
            }
            comparisons.append(
                {
                    "label": f"n_diff_{first}_{second}",
                    "independent": separated_classes(classes, values),
                    "interpreter": counts[f"n_diff_{first}_{second}"][
                        "divergent_classes"
                    ],
                }
            )
    validity = {}
    for index, first in enumerate(IMPLEMENTATIONS):
        for second in IMPLEMENTATIONS[index + 1 :]:
            validity[f"{first}_{second}"] = [
                record["row"]
                for record in corpus
                if outputs[first][record["row"]]["ok"]
                != outputs[second][record["row"]]["ok"]
            ]
    string_differences = [
        {
            "row": record["row"],
            "input": record["input"],
            **{
                name: outputs[name][record["row"]]["output"] for name in IMPLEMENTATIONS
            },
        }
        for record in corpus
        if len({outputs[name][record["row"]]["output"] for name in IMPLEMENTATIONS}) > 1
    ]
    agree = all(item["independent"] == item["interpreter"] for item in comparisons)
    record = {
        "all_counts_agree": agree,
        "comparisons": comparisons,
        "validity_disagreement_rows": validity,
        "rows_where_output_strings_differ": string_differences,
    }
    (HERE / "results/independent_verification.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    for item in comparisons:
        sys.stdout.write(
            f"{item['label']:14s} independent={item['independent']} interpreter={item['interpreter']}\n"
        )
    sys.stdout.write(f"validity disagreements {validity}\nall agree: {agree}\n")
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main())
