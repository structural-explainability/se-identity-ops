"""Tests for the parser."""

import pytest

from se_identity_ops import ParseError, parse
from se_identity_ops.syntax import (
    Apply,
    CarrierDecl,
    Check,
    Explain,
    Judge,
    OperatorDecl,
    Propose,
    RegimeDecl,
    SourceDecl,
    SurfaceDecl,
)


def test_every_statement_form_parses() -> None:
    """Each of the eleven statement forms yields its typed node."""
    program = parse(
        """
# comment line
source s file "a.csv" sha256 "ABC" note "from the city"
carrier c from s key "row"
carrier d items x y z
regime r on c by "vid" source s meaning "registration-level"
regime e on d explicit
surface n on c column "name" source s
probe p on c column "name" source s
operator op classified prs under r
judge j1 same x y under e from s scope "unit test"
propose p1 op x -> y under r from s
apply a1 p1
check c1 faithful r against n
check c2 collisions n against r
check c3 consistent r
check c4 coverage r
check c5 status x y under e
explain c1
"""
    )
    kinds = [type(statement) for statement in program.statements]
    assert kinds == [
        SourceDecl,
        CarrierDecl,
        CarrierDecl,
        RegimeDecl,
        RegimeDecl,
        SurfaceDecl,
        SurfaceDecl,
        OperatorDecl,
        Judge,
        Propose,
        Apply,
        Check,
        Check,
        Check,
        Check,
        Check,
        Explain,
    ]


def test_sha256_digest_is_lowercased_and_note_kept() -> None:
    """A declared digest is normalized and the note is kept verbatim."""
    program = parse('source s file "a.csv" sha256 "AbC" note "city data"')
    source = program.statements[0]
    assert isinstance(source, SourceDecl)
    assert source.sha256 == "abc"
    assert source.note == "city data"


def test_continuation_lines_join_the_previous_statement() -> None:
    """Indented lines continue a statement."""
    program = parse('regime r on c by "vid"\n    source s\n    meaning "x"\n')
    regime = program.statements[0]
    assert isinstance(regime, RegimeDecl)
    assert regime.source == "s"
    assert regime.meaning == "x"


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("frobnicate x", "unknown statement keyword"),
        ("judge j1 maybe a b under r", "expected 'same' or 'distinct'"),
        ("operator o classified good under r", "classification must be"),
        ("check c1 faithful r", "expected 'against'"),
        ('regime r on c by "v" source s source s', "given twice"),
        ("carrier c items", "at least one item"),
        ("propose p1 o a b under r", "expected '->'"),
        ('source s file "a" sha256', "expected sha256 digest"),
        ("  indented first", "continuation line"),
        ("explain", "expected label"),
        ("check c1 sideways r", "check kind must be"),
        ('carrier c from s key "k" extra', "unexpected extra input"),
    ],
)
def test_malformed_statements_report_a_line_and_reason(text: str, fragment: str) -> None:
    """Malformed input raises ParseError naming the problem."""
    with pytest.raises(ParseError) as caught:
        parse(text)
    assert fragment in str(caught.value)
    assert str(caught.value).startswith("line ")


def test_comment_inside_a_string_is_not_a_comment() -> None:
    """A # inside quotes is part of the string."""
    program = parse('source s file "a#b.csv" sha256 "00"  # trailing comment')
    source = program.statements[0]
    assert isinstance(source, SourceDecl)
    assert source.file == "a#b.csv"
