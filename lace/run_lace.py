"""run_lace.py - Attempt the IdentityOps experiments in LACE-style clingo encodings.

WHAT: Runs the encodings in this folder and compares their answers with the
      IdentityOps interpreter and with the recorded run output.
WHY: The related-work boundary requires trying equivalent formulations before
     claiming that IdentityOps does something LACE or ASPEN+ cannot. Each section
     below records what could be expressed, what needed an awkward encoding, and
     what could not be expressed.
HOW: python lace/run_lace.py        (needs the clingo package)
OBS: The encodings are my own plain-clingo versions of LACE-style semantics. They
     were NOT run on ASPEN or ASPEN+, which need a Python 3.9 environment, an
     asprin copy, and precomputed similarity facts (see docs/en/lace-attempts.md).
OBS: The comparison with the interpreter checks agreement on the cases run. It is
     not a proof that the two formalisms agree in general.
"""

from itertools import combinations, product
import json
from pathlib import Path
import sys
import time
from typing import Any

import clingo

from se_identity_ops import parse
from se_identity_ops.relation import DistinctPair, Relation, SamePair
from se_identity_ops.syntax import Apply, Judge, OperatorDecl, Propose

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = HERE / "results" / "lace_attempts.json"
TIMINGS = HERE / "results" / "timings.json"  # not committed: depends on the machine


TIMES: dict[str, float] = {}


def solve(control: clingo.Control) -> list[set[str]]:
    """Ground and solve; return the shown atoms of every reported model."""
    control.ground([("base", [])])
    models: list[set[str]] = []
    with control.solve(yield_=True) as handle:
        for model in handle:
            models.append({str(atom) for atom in model.symbols(shown=True)})
    return models


def lace_status(
    size: int, same: list[tuple[int, int]], distinct: list[tuple[int, int]]
) -> dict[tuple[int, int], str]:
    """Return pair statuses from cautious and brave reasoning over the open-world encoding."""
    program = (HERE / "open_world_status.lp").read_text(encoding="utf-8")
    facts = [f"item({n})." for n in range(size)]
    facts += [f"same({a},{b})." for a, b in same]
    facts += [f"distinct({a},{b})." for a, b in distinct]
    answers: dict[str, set[str]] = {}
    for mode in ("cautious", "brave"):
        control = clingo.Control([f"--enum-mode={mode}", "0", "--warn=none"])
        control.add("base", [], program + "\n".join(facts))
        models = solve(control)
        if not models:
            return {pair: "inconsistent" for pair in combinations(range(size), 2)}
        answers[mode] = models[-1]
    statuses: dict[tuple[int, int], str] = {}
    for a, b in combinations(range(size), 2):
        atom = f"eq({a},{b})"
        if atom in answers["cautious"]:
            statuses[(a, b)] = "required"
        elif atom not in answers["brave"]:
            statuses[(a, b)] = "forbidden"
        else:
            statuses[(a, b)] = "undetermined"
    return statuses


def section_status() -> dict[str, object]:
    """Compare the open-world LACE encoding with the interpreter's relation code."""
    compared = 0
    mismatches: list[str] = []
    for size in (3, 4):
        names = tuple(f"i{n}" for n in range(size))
        pairs = list(combinations(range(size), 2))
        for choice in product((0, 1, 2), repeat=len(pairs)):
            same = [pair for pair, mark in zip(pairs, choice, strict=True) if mark == 1]
            distinct = [
                pair for pair, mark in zip(pairs, choice, strict=True) if mark == 2
            ]
            relation = Relation(
                names,
                None,
                "",
                tuple(
                    SamePair(names[a], names[b], "judgment", "s", "") for a, b in same
                ),
                tuple(DistinctPair(names[a], names[b], "d", "") for a, b in distinct),
            )
            lace = lace_status(size, same, distinct)
            for a, b in pairs:
                compared += 1
                theirs = relation.status(names[a], names[b])
                if lace[(a, b)] != theirs:
                    mismatches.append(
                        f"n={size} same={same} distinct={distinct} pair={(a, b)} lace={lace[(a, b)]} interpreter={theirs}"
                    )
    return {
        "compared_pairs": compared,
        "mismatches": mismatches[:5],
        "mismatch_count": len(mismatches),
        "finding": (
            "With one soft rule offering every pair as a candidate merge, cautious/brave reasoning "
            "reproduces required/forbidden/undetermined on every assignment for 3 and 4 items. "
            "Without that quadratic soft rule, LACE-style derivation leaves unmerged pairs unmerged, "
            "so 'undetermined' and 'forbidden' cannot be told apart from 'not merged'."
        ),
    }


def section_growth() -> list[dict[str, object]]:
    """Measure ground size and time of the open-world encoding as the carrier grows."""
    program = (HERE / "open_world_status.lp").read_text(encoding="utf-8")
    rows: list[dict[str, object]] = []
    for size in (10, 20, 40, 80):
        control = clingo.Control(["--warn=none"])
        control.add("base", [], program + "\n".join(f"item({n})." for n in range(size)))
        started = time.perf_counter()
        control.ground([("base", [])])
        elapsed = time.perf_counter() - started
        TIMES[f"grounding_{size}_items"] = round(elapsed, 3)
        rows.append({"items": size, "ground_atoms": len(list(control.symbolic_atoms))})
    return rows


def audit(rows: list[tuple[str, str, str]]) -> dict[str, int]:
    """Run audit_two_rules.lp on (item, key, value) rows; return counts."""
    program = (HERE / "audit_two_rules.lp").read_text(encoding="utf-8")
    control = clingo.Control(["--warn=none"])
    control.add("base", [], program)
    with control.backend() as backend:
        for item, key, value in rows:
            symbol = clingo.Function(
                "rec", [clingo.String(item), clingo.String(key), clingo.String(value)]
            )
            backend.add_rule([backend.add_atom(symbol)])
    models = solve(control)
    shown = models[0]
    return {
        "divergent_items": sum(1 for atom in shown if atom.startswith("div_item(")),
        "divergent_classes": sum(1 for atom in shown if atom.startswith("div_class(")),
        "cross_class_pairs_distinct": sum(
            1 for atom in shown if atom.startswith("cross(")
        ),
    }


def read_csv(
    path: Path, key_column: str, value_column: str, item_column: str
) -> list[tuple[str, str, str]]:
    """Read (item, key, value) rows from a CSV."""
    import csv

    with path.open(newline="", encoding="utf-8") as handle:
        return [
            (row[item_column], row[key_column], row[value_column])
            for row in csv.DictReader(handle)
        ]


def distinct_cross_pairs(rows: list[tuple[str, str, str]]) -> int:
    """Count distinct pairs of declared classes that share a surface value (plain Python)."""
    classes_by_value: dict[str, set[str]] = {}
    for _item, key, value in rows:
        if key:
            classes_by_value.setdefault(value, set()).add(key)
    pairs: set[tuple[str, str]] = set()
    for classes in classes_by_value.values():
        ordered = sorted(classes)
        for left, right in combinations(ordered, 2):
            pairs.add((left, right))
    return len(pairs)


def section_chicago() -> dict[str, object]:
    """Run the Chicago audit as two LACE-style hard-rule sets."""
    path = ROOT / "examples" / "chicago" / "data" / "vendors_20k_observed.csv"
    run = json.loads(
        (ROOT / "examples" / "chicago" / "results" / "run.json").read_text(
            encoding="utf-8"
        )
    )
    result: dict[str, object] = {}
    for label, column in (
        ("localized_name", "a_faithful_localized"),
        ("vendor_name", "a_faithful_raw"),
    ):
        rows = read_csv(path, "vendor_id", label, "row")
        started = time.perf_counter()
        counts = audit(rows)
        TIMES[f"chicago_audit_{label}"] = round(time.perf_counter() - started, 2)
        reported = next(
            r
            for r in run["results"]
            if r["label"] == column and r["operation"] == "check"
        )["counts"]
        expected_pairs = distinct_cross_pairs(rows)
        result[label] = {
            "lace": counts,
            "interpreter": {
                k: reported[k] for k in ("divergent_classes", "divergent_items")
            },
            "distinct_class_pairs_by_plain_python": expected_pairs,
            "agree": (
                counts["divergent_classes"] == reported["divergent_classes"]
                and counts["divergent_items"] == reported["divergent_items"]
                and counts["cross_class_pairs_distinct"] == expected_pairs
            ),
        }
    return result


def section_sbom() -> dict[str, object]:
    """Run the same audit encoding on the two SBOM tables."""
    result: dict[str, object] = {}
    for case in ("known_bad", "known_good"):
        path = ROOT / "examples" / "sbom" / "data" / f"components_{case}.csv"
        run = json.loads(
            (ROOT / "examples" / "sbom" / "results" / f"{case}.json").read_text(
                encoding="utf-8"
            )
        )
        reported = next(
            r
            for r in run["results"]
            if r["label"] == "b_canonical" and r["operation"] == "check"
        )["counts"]
        rows = read_csv(path, "anchor_hash", "canonical_purl", "frame")
        counts = audit(rows)
        result[case] = {
            "lace": counts,
            "interpreter": {
                k: reported[k] for k in ("divergent_classes", "divergent_items")
            },
            "agree": (
                counts["divergent_classes"] == reported["divergent_classes"]
                and counts["divergent_items"] == reported["divergent_items"]
            ),
        }
    return result


def section_persistence() -> dict[str, object]:
    """Replay the synthetic persistence program's apply steps with a LACE gate driver."""
    program = parse(
        (ROOT / "examples" / "persistence" / "program.ido").read_text(encoding="utf-8")
    )
    run = json.loads(
        (ROOT / "examples" / "persistence" / "results" / "run.json").read_text(
            encoding="utf-8"
        )
    )
    gate = (HERE / "licensing_gate.lp").read_text(encoding="utf-8")
    classification = {
        s.name: s.classification
        for s in program.statements
        if isinstance(s, OperatorDecl)
    }
    proposals = {s.label: s for s in program.statements if isinstance(s, Propose)}
    licensed: list[tuple[str, str]] = []
    distinct: list[tuple[str, str]] = []
    rows = []
    for statement in program.statements:
        if isinstance(statement, Judge) and statement.polarity == "distinct":
            distinct.append((statement.first, statement.second))
        if not isinstance(statement, Apply):
            continue
        proposal = proposals[statement.proposal]
        kind = classification[proposal.operator]
        interpreter_word = next(
            r
            for r in run["results"]
            if r["label"] == statement.label and r["operation"] == "apply"
        )["word"]
        if kind != "prs":
            rows.append(
                {
                    "step": statement.label,
                    "lace": "not expressible",
                    "interpreter": interpreter_word,
                    "agree": None,
                    "note": f"operator classified {kind}; LACE has no ignoring, breaking, or inapplicable steps",
                }
            )
            continue
        trial = [*licensed, (proposal.first, proposal.second)]
        facts = "\n".join(f'licensed("{a}","{b}").' for a, b in trial)
        facts += "\n" + "\n".join(f'distinct("{a}","{b}").' for a, b in distinct)
        control = clingo.Control(["--warn=none"])
        control.add("base", [], gate + facts)
        satisfiable = bool(solve(control))
        if satisfiable:
            licensed.append((proposal.first, proposal.second))
        lace_word = "licensed" if satisfiable else "blocked"
        rows.append(
            {
                "step": statement.label,
                "lace": lace_word,
                "interpreter": interpreter_word,
                "agree": lace_word == interpreter_word,
                "note": "",
            }
        )
    return {
        "steps": rows,
        "all_expressible_steps_agree": all(
            r["agree"] for r in rows if r["agree"] is not None
        ),
    }


def main() -> int:
    """Run every section and write the results."""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "clingo": clingo.__version__,
        "status_open_world": section_status(),
        "grounding_growth": section_growth(),
        "chicago_audit": section_chicago(),
        "sbom_audit": section_sbom(),
        "persistence_gate": section_persistence(),
    }
    OUT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    TIMINGS.write_text(
        json.dumps(TIMES, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    status = report["status_open_world"]
    sys.stdout.write(
        f"status: compared {status['compared_pairs']} pairs, mismatches {status['mismatch_count']}\n"
    )  # type: ignore[index]
    sys.stdout.write(f"growth: {report['grounding_growth']}\n")
    for name in ("chicago_audit", "sbom_audit"):
        for case, body in report[name].items():  # type: ignore[union-attr]
            sys.stdout.write(
                f"{name} {case}: agree={body['agree']} lace={body['lace']}\n"
            )
    sys.stdout.write(
        f"persistence: all expressible steps agree = {report['persistence_gate']['all_expressible_steps_agree']}\n"
    )  # type: ignore[index]
    return 0


if __name__ == "__main__":
    sys.exit(main())
