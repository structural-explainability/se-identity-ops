"""Tests of operation order.

SEMANTICS.md, "Order": program meaning depends on statement order only through
`judge` and `apply`. These tests do not assume that independent operations
commute. They run both orders and compare, and they show a case where the order
changes the outcome.
"""

from itertools import permutations
from pathlib import Path

from se_identity_ops import Run, parse, run_program

from .helpers import write_table

PRELUDE = """
source s file "evidence.csv" sha256 "@SHA@"
carrier c items a b x y z
regime r on c explicit source s meaning "unit test"
operator rekey classified prs under r
"""


def run_in_order(statements: list[str], tmp_path: Path) -> Run:
    """Run PRELUDE plus statements in the given order."""
    digest = write_table(tmp_path, "evidence", ["note"], [["unit test evidence"]])
    text = PRELUDE.replace("@SHA@", digest) + "\n".join(statements) + "\n"
    return run_program(parse(text), tmp_path)


def classes(run: Run) -> frozenset[frozenset[str]]:
    """Return the same-classes after a run."""
    return run.same_classes("r")


def test_judgments_on_disjoint_pairs_commute(tmp_path: Path) -> None:
    """Two same-judgments on disjoint pairs give the same classes and the same outcomes in either order."""
    j1 = 'judge j1 same a b under r from s scope "t"'
    j2 = 'judge j2 same x y under r from s scope "t"'
    first = run_in_order([j1, j2], tmp_path)
    second = run_in_order([j2, j1], tmp_path)
    assert classes(first) == classes(second)
    assert {(r.label, r.word) for r in first.results} == {
        (r.label, r.word) for r in second.results
    }


def test_checks_and_proposals_do_not_change_what_later_operations_do(
    tmp_path: Path,
) -> None:
    """Inserting check, propose, or explain anywhere leaves judge and apply outcomes unchanged."""
    core = [
        'judge j1 distinct a b under r from s scope "t"',
        "propose p1 rekey a -> b under r",
        "apply a1 p1",
    ]
    baseline = {(r.label, r.word) for r in run_in_order(core, tmp_path).results}
    padded = [
        "check c0 consistent r",
        core[0],
        "check c1 status a b under r",
        core[1],
        "explain j1",
        core[2],
        "check c2 consistent r",
    ]
    with_extras = {(r.label, r.word) for r in run_in_order(padded, tmp_path).results}
    assert baseline <= with_extras


def test_licensing_order_changes_the_outcome(tmp_path: Path) -> None:
    """Applying a->b first, then judging a and b distinct, differs from the reverse order."""
    apply_first = run_in_order(
        [
            "propose p1 rekey a -> b under r",
            "apply a1 p1",
            'judge j1 distinct a b under r from s scope "t"',
        ],
        tmp_path,
    )
    judge_first = run_in_order(
        [
            'judge j1 distinct a b under r from s scope "t"',
            "propose p1 rekey a -> b under r",
            "apply a1 p1",
        ],
        tmp_path,
    )
    assert apply_first.result("a1").word == "licensed"
    assert apply_first.result("j1").word == "conflicting"
    assert judge_first.result("j1").word == "recorded"
    assert judge_first.result("a1").word == "blocked"
    assert classes(apply_first) != classes(judge_first)


def test_which_branch_is_licensed_depends_on_order(tmp_path: Path) -> None:
    """With a and z asserted distinct, a->b then b->z licenses the first and blocks the second; the reverse swaps them."""
    prelude = [
        'judge d distinct a z under r from s scope "t"',
        "propose p1 rekey a -> b under r",
        "propose p2 rekey b -> z under r",
    ]
    forward = run_in_order([*prelude, "apply a1 p1", "apply a2 p2"], tmp_path)
    backward = run_in_order([*prelude, "apply a2 p2", "apply a1 p1"], tmp_path)
    assert (forward.result("a1").word, forward.result("a2").word) == (
        "licensed",
        "blocked",
    )
    assert (backward.result("a2").word, backward.result("a1").word) == (
        "licensed",
        "blocked",
    )
    assert classes(forward) != classes(backward)


def test_every_order_of_four_operations_is_classified_not_assumed(
    tmp_path: Path,
) -> None:
    """Over all 24 orders, record which final class structures occur; more than one must occur."""
    operations = [
        'judge j1 same a b under r from s scope "t"',
        'judge j2 distinct b x under r from s scope "t"',
        "propose p1 rekey a -> x under r",
        "apply a1 p1",
    ]
    outcomes = set()
    for order in permutations(operations):
        statements = list(order)
        proposal = statements.index(operations[2])
        application = statements.index(operations[3])
        if application < proposal:
            continue
        run = run_in_order(statements, tmp_path)
        outcomes.add((classes(run), run.result("a1").word))
    assert len({word for _classes, word in outcomes}) > 1
