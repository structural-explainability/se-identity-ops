"""Tests for the reference interpreter's semantics."""

from pathlib import Path

import pytest

from se_identity_ops import (
    ExplanationKind,
    LimitationCause,
    Outcome,
    RunError,
    parse,
    run_program,
)

from .helpers import VENDOR_PRELUDE, VENDORS, run_text

TABLES = {"vendors": VENDORS}


def run(tmp_path: Path, body: str):  # noqa: ANN201
    """Run VENDOR_PRELUDE plus body."""
    return run_text(tmp_path, VENDOR_PRELUDE + body, TABLES)


# ----------------------------------------------------------------------
# status: unknown is not false
# ----------------------------------------------------------------------


def test_records_with_equal_key_are_required_identical(tmp_path: Path) -> None:
    """The criterion's own key relates r1 and r3."""
    result = run(tmp_path, "check c1 status r1 r3 under reg\n").result("c1")
    assert (result.outcome, result.word) == (Outcome.ESTABLISHED, "required")
    assert result.explanation is not None
    assert result.explanation.kind is ExplanationKind.DERIVATION
    assert result.explanation.steps[0][0].ground == "key"
    assert result.explanation.steps[0][0].detail.startswith("vid=V1")


def test_different_keys_are_undetermined_not_distinct(tmp_path: Path) -> None:
    """A criterion that is silent about a pair does not declare it distinct."""
    result = run(tmp_path, "check c1 status r1 r2 under reg\n").result("c1")
    assert (result.outcome, result.word) == (Outcome.UNDETERMINED, "undetermined")
    assert result.explanation is not None
    assert result.explanation.kind is ExplanationKind.LIMITATION
    assert result.explanation.limitation is LimitationCause.INSUFFICIENT_INFORMATION


def test_empty_key_places_an_item_in_no_class(tmp_path: Path) -> None:
    """An item with an empty key is related to nothing until a judgment mentions it."""
    body = """
check c1 status r4 r6 under reg
judge j1 same r4 r5 under reg from s scope "unit test"
check c2 status r4 r6 under reg
check c3 coverage reg
"""
    result = run(tmp_path, body)
    assert result.result("c1").word == "undetermined"
    assert result.result("c2").word == "undetermined"
    coverage = result.result("c3")
    assert (coverage.outcome, coverage.word) == (Outcome.ESTABLISHED, "complete")


def test_coverage_lists_unanchored_items(tmp_path: Path) -> None:
    """r4 has no key value and no same-judgment, so the criterion is silent about it."""
    result = run(tmp_path, "check c1 coverage reg\n").result("c1")
    assert result.outcome is Outcome.UNDETERMINED
    assert dict(result.counts)["silent_items"] == 1
    assert result.explanation is not None
    assert dict(result.explanation.witness)["silent_01"] == "r4"


# ----------------------------------------------------------------------
# judge: evidence is kept; contradictions are visible
# ----------------------------------------------------------------------


def test_distinct_judgment_forbids_a_merge(tmp_path: Path) -> None:
    """After judging r1 and r2 distinct, the pair is forbidden."""
    body = """
judge j1 distinct r1 r2 under reg from s scope "unit test"
check c1 status r1 r2 under reg
check c2 status r3 r2 under reg
"""
    result = run(tmp_path, body)
    assert result.result("j1").word == "recorded"
    assert result.result("c1").word == "forbidden"
    forced = result.result("c2")
    assert forced.word == "forbidden"
    assert forced.explanation is not None
    assert len(forced.explanation.steps) == 2


def test_contradicting_judgment_is_recorded_and_flagged(tmp_path: Path) -> None:
    """A distinct judgment inside a same-class is kept, marked conflicting, and refuted."""
    body = """
judge j1 distinct r1 r3 under reg from s scope "unit test"
check c1 consistent reg
"""
    result = run(tmp_path, body)
    judgment = result.result("j1")
    assert (judgment.outcome, judgment.word) == (Outcome.REFUTED, "conflicting")
    assert result.final_state.judgments[0].conflicting is True
    consistent = result.result("c1")
    assert (consistent.outcome, consistent.word) == (Outcome.REFUTED, "inconsistent")
    assert consistent.explanation is not None
    assert consistent.explanation.kind is ExplanationKind.WITNESS


def test_status_in_an_inconsistent_state_is_not_reported_as_a_status(tmp_path: Path) -> None:
    """Required, forbidden, and undetermined are defined only for consistent commitments."""
    body = """
judge j1 distinct r1 r3 under reg from s scope "unit test"
check c1 status r1 r6 under reg
"""
    result = run(tmp_path, body).result("c1")
    assert (result.outcome, result.word) == (Outcome.UNDETERMINED, "inconsistent")


def test_redundant_judgment_is_reported(tmp_path: Path) -> None:
    """Judging a pair that is already required is redundant, not new evidence of anything else."""
    result = run(tmp_path, "judge j1 same r1 r3 under reg from s scope \"x\"\n").result("j1")
    assert (result.outcome, result.word) == (Outcome.ESTABLISHED, "redundant")


def test_unsourced_judgment_is_recorded_with_no_source(tmp_path: Path) -> None:
    """Missing evidence is kept visible in the explanation."""
    result = run(tmp_path, "judge j1 same r1 r2 under reg\n").result("j1")
    assert result.explanation is not None
    assert "no source" in result.explanation.summary


def test_same_judgment_joins_classes_through_a_chain(tmp_path: Path) -> None:
    """A same judgment plus the key relation gives a derivation through both."""
    body = """
judge j1 same r3 r2 under reg from s scope "unit test"
check c1 status r1 r2 under reg
"""
    result = run(tmp_path, body).result("c1")
    assert result.word == "required"
    assert result.explanation is not None
    grounds = [step.ground for step in result.explanation.steps[0]]
    assert "key" in grounds
    assert "judgment" in grounds


# ----------------------------------------------------------------------
# propose and apply
# ----------------------------------------------------------------------

OPERATORS = """
operator rekey classified prs under reg
operator relabel classified ign under reg
operator split classified brk under reg
operator reorder classified na under reg
"""


def test_propose_does_not_change_state(tmp_path: Path) -> None:
    """A proposal leaves every judgment, step, and snapshot as it was."""
    body = OPERATORS + "propose p1 rekey r1 -> r6 under reg\n"
    result = run(tmp_path, body)
    assert result.result("p1").word == "proposed"
    assert len(result.states) == 1
    assert result.final_state.judgments == ()
    assert result.final_state.steps == ()


def test_apply_licenses_a_preserving_step(tmp_path: Path) -> None:
    """A preserving step with no forbidding judgment is licensed and joins the classes."""
    body = OPERATORS + """
propose p1 rekey r1 -> r6 under reg
apply a1 p1
check c1 status r3 r6 under reg
"""
    result = run(tmp_path, body)
    applied = result.result("a1")
    assert (applied.outcome, applied.word) == (Outcome.ESTABLISHED, "licensed")
    assert result.result("c1").word == "required"
    assert result.final_state.steps[0].licensed is True


def test_apply_is_blocked_by_a_distinct_judgment(tmp_path: Path) -> None:
    """A step that would join classes asserted distinct is blocked and changes nothing but the log."""
    body = OPERATORS + """
judge j1 distinct r1 r6 under reg from s scope "unit test"
propose p1 rekey r1 -> r6 under reg
apply a1 p1
"""
    result = run(tmp_path, body)
    blocked = result.result("a1")
    assert (blocked.outcome, blocked.word) == (Outcome.REFUTED, "blocked")
    assert result.final_state.steps == ()
    assert result.final_state.log[-1] == ("a1", "blocked")
    assert blocked.explanation is not None
    assert blocked.explanation.kind is ExplanationKind.WITNESS


def test_ignoring_operator_does_not_license_identity(tmp_path: Path) -> None:
    """An identity-ignoring step is recorded but neither licensed nor broken."""
    body = OPERATORS + """
propose p1 relabel r1 -> r6 under reg
apply a1 p1
check c1 status r1 r6 under reg
"""
    result = run(tmp_path, body)
    applied = result.result("a1")
    assert (applied.outcome, applied.word) == (Outcome.UNDETERMINED, "ignoring")
    assert applied.explanation is not None
    assert applied.explanation.limitation is LimitationCause.OPERATOR_UNDERDETERMINATION
    assert result.final_state.steps[0].licensed is False
    assert result.result("c1").word == "undetermined"


def test_breaking_operator_is_recorded_but_does_not_assert_distinctness(tmp_path: Path) -> None:
    """A breaking step refutes continuation but leaves the pair undetermined, not forbidden."""
    body = OPERATORS + """
propose p1 split r1 -> r6 under reg
apply a1 p1
check c1 status r1 r6 under reg
"""
    result = run(tmp_path, body)
    assert (result.result("a1").outcome, result.result("a1").word) == (Outcome.REFUTED, "broken")
    assert result.result("c1").word == "undetermined"


def test_inapplicable_operator_is_not_executed(tmp_path: Path) -> None:
    """An inapplicable operator leaves no step in the state."""
    body = OPERATORS + "propose p1 reorder r1 -> r6 under reg\napply a1 p1\n"
    result = run(tmp_path, body)
    applied = result.result("a1")
    assert (applied.outcome, applied.word) == (Outcome.UNDETERMINED, "inapplicable")
    assert applied.explanation is not None
    assert applied.explanation.limitation is LimitationCause.INAPPLICABILITY
    assert result.final_state.steps == ()


def test_fork_siblings_become_identical_and_a_distinction_blocks_the_second_branch(
    tmp_path: Path,
) -> None:
    """Two licensed successors of one state are identical; a distinction blocks the second."""
    body = OPERATORS + """
propose p1 rekey r6 -> r4 under reg
propose p2 rekey r6 -> r5 under reg
apply a1 p1
judge j1 distinct r4 r5 under reg from s scope "unit test"
apply a2 p2
check c1 status r4 r5 under reg
"""
    result = run(tmp_path, body)
    assert result.result("a1").word == "licensed"
    assert result.result("a2").word == "blocked"
    assert result.result("c1").word == "forbidden"


def test_fork_without_a_distinction_makes_the_branches_identical(tmp_path: Path) -> None:
    """Without a distinction, licensing both branches makes the successors identical."""
    body = OPERATORS + """
propose p1 rekey r6 -> r4 under reg
propose p2 rekey r6 -> r5 under reg
apply a1 p1
apply a2 p2
check c1 status r4 r5 under reg
"""
    result = run(tmp_path, body)
    assert result.result("c1").word == "required"


# ----------------------------------------------------------------------
# faithful and collisions
# ----------------------------------------------------------------------


def test_faithful_violation_has_a_reproducible_witness(tmp_path: Path) -> None:
    """r1 and r3 share vid V1 but norm gives 'acme' and 'acme corp'."""
    result = run(tmp_path, "check c1 faithful reg against norm\n").result("c1")
    assert (result.outcome, result.word) == (Outcome.REFUTED, "violated")
    assert result.explanation is not None
    witness = dict(result.explanation.witness)
    assert witness["kind"] == "divergence"
    assert (witness["example_01.first"], witness["example_01.second"]) == ("r1", "r3")
    assert (witness["example_01.first_value"], witness["example_01.second_value"]) == (
        "acme",
        "acme corp",
    )
    assert result.explanation.steps[0][0].ground == "key"


def test_probe_witness_is_called_incoherence(tmp_path: Path) -> None:
    """A probe reports an incoherence witness, a surface reports a divergence witness."""
    result = run(tmp_path, "check c1 faithful reg against seen\n").result("c1")
    assert result.explanation is not None
    assert dict(result.explanation.witness)["kind"] == "incoherence"


def test_faithful_satisfied_when_surface_does_not_split_a_class(tmp_path: Path) -> None:
    """A surface that never splits a class is faithful, even if it merges classes."""
    body = """
source t file "pairs.csv" sha256 "@SHA:pairs@"
carrier ps from t key "row"
regime g on ps by "grp" source t
surface same_name on ps column "name" source t
check c1 faithful g against same_name
"""
    tables = {"pairs": (["row", "grp", "name"], [["a", "1", "x"], ["b", "1", "x"], ["c", "2", "x"]])}
    result = run_text(tmp_path, body, tables).result("c1")
    assert (result.outcome, result.word) == (Outcome.ESTABLISHED, "satisfied")


def test_check_without_a_regime_source_is_unwarranted(tmp_path: Path) -> None:
    """A regime that names no source cannot warrant a verdict, whatever the numbers say."""
    body = """
source s file "vendors.csv" sha256 "@SHA:vendors@"
carrier recs from s key "row"
regime loose on recs by "vid"
surface norm on recs column "name" source s
check c1 faithful loose against norm
"""
    result = run_text(tmp_path, body, TABLES).result("c1")
    assert (result.outcome, result.word) == (Outcome.UNDETERMINED, "unwarranted")
    assert result.explanation is not None
    assert result.explanation.limitation is LimitationCause.INSUFFICIENT_INFORMATION
    assert dict(result.counts)["divergent_classes"] == 1


def test_collisions_are_unsupported_not_contradicted_without_distinct_judgments(
    tmp_path: Path,
) -> None:
    """norm merges r1 (V1) with r2 (V2): the criterion neither requires nor forbids it."""
    result = run(tmp_path, "check c1 collisions norm against reg\n").result("c1")
    assert (result.outcome, result.word) == (Outcome.UNDETERMINED, "unsupported")
    counts = dict(result.counts)
    assert counts["cross_class_groups"] == 2
    assert counts["forbidden_class_pairs"] == 0
    assert counts["unsupported_class_pairs"] == 2
    assert result.explanation is not None
    assert result.explanation.kind is ExplanationKind.LIMITATION
    witness = dict(result.explanation.witness)
    assert witness["example_01.surface_value"] == "acme"
    assert witness["example_01.first_key"] == "V1"
    assert witness["example_01.second_key"] == "V2"


def test_collisions_are_contradicted_when_a_distinct_judgment_covers_them(tmp_path: Path) -> None:
    """A distinct judgment between the merged classes turns 'unsupported' into 'contradicted'."""
    body = """
judge j1 distinct r1 r2 under reg from s scope "unit test"
check c1 collisions norm against reg
"""
    result = run(tmp_path, body).result("c1")
    assert (result.outcome, result.word) == (Outcome.REFUTED, "contradicted")
    assert dict(result.counts)["forbidden_class_pairs"] == 1


def test_collisions_supported_when_every_merge_lies_in_one_class(tmp_path: Path) -> None:
    """If every surface group sits inside one criterion class, the merges are required."""
    body = """
source t file "pairs.csv" sha256 "@SHA:pairs@"
carrier ps from t key "row"
regime g on ps by "grp" source t
surface by_name on ps column "name" source t
check c1 collisions by_name against g
"""
    tables = {"pairs": (["row", "grp", "name"], [["a", "1", "x"], ["b", "1", "x"], ["c", "2", "y"]])}
    result = run_text(tmp_path, body, tables).result("c1")
    assert (result.outcome, result.word) == (Outcome.ESTABLISHED, "supported")


# ----------------------------------------------------------------------
# state, snapshots, determinism, explain
# ----------------------------------------------------------------------


def test_snapshots_are_never_modified_by_later_operations(tmp_path: Path) -> None:
    """Each judge or apply adds a snapshot; earlier snapshots keep their contents."""
    body = OPERATORS + """
judge j1 same r6 r4 under reg from s scope "unit test"
propose p1 rekey r1 -> r6 under reg
apply a1 p1
judge j2 distinct r2 r5 under reg from s scope "unit test"
"""
    result = run(tmp_path, body)
    assert [state.index for state in result.states] == [0, 1, 2, 3]
    assert result.states[0].judgments == ()
    assert [j.label for j in result.states[1].judgments] == ["j1"]
    assert result.states[1].steps == ()
    assert [j.label for j in result.states[2].judgments] == ["j1"]
    assert [s.label for s in result.states[2].steps] == ["a1"]
    assert [j.label for j in result.states[3].judgments] == ["j1", "j2"]


def test_explain_returns_the_explanation_of_the_labeled_operation(tmp_path: Path) -> None:
    """Explain repeats the explanation that was produced with the operation."""
    body = "check c1 faithful reg against norm\nexplain c1\n"
    result = run(tmp_path, body)
    explained = [item for item in result.results if item.operation == "explain"][0]
    assert explained.explanation == result.result("c1", "check").explanation


def test_identical_programs_give_identical_json(tmp_path: Path) -> None:
    """Running twice gives byte-identical serialized results."""
    body = OPERATORS + """
judge j1 distinct r1 r2 under reg from s scope "unit test"
check c1 faithful reg against norm
check c2 collisions norm against reg
propose p1 rekey r6 -> r4 under reg
apply a1 p1
explain c2
"""
    first = run(tmp_path, body).to_dict()
    second = run(tmp_path, body).to_dict()
    assert first == second


# ----------------------------------------------------------------------
# data errors stop the run
# ----------------------------------------------------------------------


def test_altered_source_file_stops_the_run(tmp_path: Path) -> None:
    """A digest mismatch is an error, not a result."""
    run_text(tmp_path, VENDOR_PRELUDE, TABLES)
    csv_path = tmp_path / "vendors.csv"
    csv_path.write_text(csv_path.read_text(encoding="utf-8") + "r7,V9,extra\n", encoding="utf-8")
    text = VENDOR_PRELUDE.replace("@SHA:vendors@", "0" * 64)
    with pytest.raises(RunError, match="sha256"):
        run_program(parse(text), tmp_path)


def test_unknown_item_stops_the_run(tmp_path: Path) -> None:
    """Judging an item that is not in the loaded carrier is an error."""
    with pytest.raises(RunError, match="'r99' is not an item"):
        run(tmp_path, "judge j1 same r1 r99 under reg\n")


def test_unknown_column_stops_the_run(tmp_path: Path) -> None:
    """Reading a column the table lacks is an error."""
    text = VENDOR_PRELUDE + 'surface bad on recs column "nosuch" source s\n'
    with pytest.raises(RunError, match="no column 'nosuch'"):
        run_text(tmp_path, text, TABLES)


def test_ill_formed_program_is_rejected_before_running(tmp_path: Path) -> None:
    """The static checker's diagnostics stop the run."""
    with pytest.raises(RunError, match="unknown regime"):
        run_text(tmp_path, "check c1 consistent nosuch\n")
