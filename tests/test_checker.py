"""Tests for the static semantic checker."""

import pytest

from se_identity_ops import check_program, parse

BASE = """
source s file "a.csv" sha256 "00"
carrier recs from s key "row"
carrier small items a b c
regime reg on recs by "vid" source s
regime ex on small explicit
surface norm on recs column "name" source s
probe seen on recs column "name" source s
operator rekey classified prs under ex
"""


def diagnostics(extra: str) -> list[str]:
    """Return diagnostic messages for BASE plus extra statements."""
    return [str(item) for item in check_program(parse(BASE + extra))]


def test_a_well_formed_program_has_no_diagnostics() -> None:
    """The base program is clean."""
    assert diagnostics("") == []


@pytest.mark.parametrize(
    ("extra", "fragment"),
    [
        ("carrier x from nosuch key \"k\"\n", "unknown source 'nosuch'"),
        ("regime r2 on nosuch explicit\n", "unknown carrier 'nosuch'"),
        ("regime reg on small explicit\n", "regime 'reg' is already declared"),
        ('regime k on small by "v" source s\n', "needs a carrier loaded from a source"),
        ('surface z on small column "n" source s\n', "needs a carrier loaded from a source"),
        ("operator o classified prs under nosuch\n", "unknown regime 'nosuch'"),
        ("judge j1 same a a under ex\n", "two different items"),
        ("judge j1 same a q under ex\n", "'q' is not an item of carrier 'small'"),
        ("judge j1 same a b under nosuch\n", "unknown regime 'nosuch'"),
        ("judge j1 same a b under ex\njudge j1 same b c under ex\n", "label 'j1' is already used"),
        ("propose p1 rekey a -> b under reg\n", "classified under regime 'ex', not 'reg'"),
        ("propose p1 nosuch a -> b under ex\n", "unknown operator 'nosuch'"),
        ("propose p1 rekey a -> a under ex\n", "two different items"),
        ("apply a1 nosuch\n", "unknown proposal 'nosuch'"),
        (
            "propose p1 rekey a -> b under ex\napply a1 p1\napply a2 p1\n",
            "proposal 'p1' is already applied",
        ),
        ("check c1 faithful ex against norm\n", "regime 'ex' is on carrier 'small'"),
        ("check c1 collisions seen against reg\n", "'seen' is a probe; collisions applies to surfaces"),
        ("check c1 faithful nosuch against norm\n", "unknown regime 'nosuch'"),
        ("explain nosuch\n", "unknown label 'nosuch'"),
    ],
)
def test_ill_formed_programs_are_rejected_with_a_reason(extra: str, fragment: str) -> None:
    """Each cross-category or unresolved reference is rejected."""
    found = diagnostics(extra)
    assert any(fragment in message for message in found), found


def test_use_before_declaration_is_rejected() -> None:
    """A name must be declared before it is used."""
    found = [str(item) for item in check_program(parse("check c1 consistent r\n"))]
    assert any("unknown regime 'r'" in message for message in found)
