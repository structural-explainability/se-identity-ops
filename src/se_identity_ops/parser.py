"""parser.py - Parse IdentityOps text into a typed Program.

WHAT: A small line-oriented parser. A statement starts in column one and may
      continue on following lines that start with whitespace. `#` starts a comment.
WHY: The grammar is fixed and tiny, so a hand-written parser stays readable and
     needs no dependencies.
HOW: See SPEC.md, "Grammar", for every statement form.
OBS: The parser checks shape only. Names, kinds, and data are checked later.
"""

from dataclasses import dataclass
import re
from typing import Literal, cast

from .syntax import (
    Apply,
    CarrierDecl,
    Check,
    CheckKind,
    Classification,
    Explain,
    Judge,
    OperatorDecl,
    Polarity,
    Program,
    Propose,
    RegimeDecl,
    SourceDecl,
    Statement,
    SurfaceDecl,
)


class ParseError(Exception):
    """Raised when program text does not match the grammar."""

    def __init__(self, line: int, message: str) -> None:
        """Store the line number and message.

        Args:
            line: One-based line number where the problem starts.
            message: Description of the problem.
        """
        super().__init__(f"line {line}: {message}")
        self.line = line
        self.message = message


@dataclass(frozen=True, slots=True)
class Token:
    """One token of a statement.

    Attributes:
        kind: "string", "word", or "arrow".
        text: Token text without quotes for strings.
    """

    kind: Literal["string", "word", "arrow"]
    text: str


_TOKEN_PATTERN = re.compile(
    r"""
    \s+
    | (?P<comment>\#[^\n]*)
    | (?P<string>"(?:[^"\\]|\\.)*")
    | (?P<arrow>->)
    | (?P<word>[A-Za-z0-9_.:@/~+%-]+)
    """,
    re.VERBOSE,
)

_ESCAPE_PATTERN = re.compile(r"\\(.)")


def _unescape(raw: str) -> str:
    """Remove the quotes of a string token and resolve backslash escapes."""
    return _ESCAPE_PATTERN.sub(lambda match: match.group(1), raw[1:-1])


def tokenize(text: str, line: int) -> list[Token]:
    """Split one logical statement into tokens.

    Args:
        text: Statement text, possibly spanning several physical lines.
        line: Line number of the first physical line, for error messages.

    Returns:
        Tokens in order.

    Raises:
        ParseError: If a character cannot start any token.
    """
    tokens: list[Token] = []
    position = 0
    while position < len(text):
        match = _TOKEN_PATTERN.match(text, position)
        if match is None:
            raise ParseError(line, f"unexpected character {text[position]!r}")
        position = match.end()
        if match.group("string") is not None:
            tokens.append(Token("string", _unescape(match.group("string"))))
        elif match.group("arrow") is not None:
            tokens.append(Token("arrow", "->"))
        elif match.group("word") is not None:
            tokens.append(Token("word", match.group("word")))
    return tokens


class _Cursor:
    """Read tokens of one statement left to right."""

    def __init__(self, tokens: list[Token], line: int) -> None:
        """Start at the first token."""
        self.tokens = tokens
        self.line = line
        self.index = 0

    def at_end(self) -> bool:
        """Return whether every token has been read."""
        return self.index >= len(self.tokens)

    def peek_word(self) -> str:
        """Return the next word without reading it, or empty string."""
        if self.at_end():
            return ""
        token = self.tokens[self.index]
        return token.text if token.kind == "word" else ""

    def word(self, what: str) -> str:
        """Read one word token."""
        if self.at_end() or self.tokens[self.index].kind != "word":
            raise ParseError(self.line, f"expected {what}")
        text = self.tokens[self.index].text
        self.index += 1
        return text

    def keyword(self, expected: str) -> None:
        """Read one specific keyword."""
        if self.peek_word() != expected:
            raise ParseError(self.line, f"expected '{expected}'")
        self.index += 1

    def string(self, what: str) -> str:
        """Read one quoted string."""
        if self.at_end() or self.tokens[self.index].kind != "string":
            raise ParseError(self.line, f"expected {what} in double quotes")
        text = self.tokens[self.index].text
        self.index += 1
        return text

    def arrow(self) -> None:
        """Read the `->` token."""
        if self.at_end() or self.tokens[self.index].kind != "arrow":
            raise ParseError(self.line, "expected '->'")
        self.index += 1

    def finish(self) -> None:
        """Require that no tokens remain."""
        if not self.at_end():
            raise ParseError(self.line, f"unexpected extra input {self.tokens[self.index].text!r}")


def _optional_clauses(cursor: _Cursor, allowed: dict[str, bool]) -> dict[str, str]:
    """Read optional trailing `name value` clauses in any order.

    Args:
        cursor: Token cursor positioned after the required part.
        allowed: Clause name mapped to whether its value is a quoted string
            (True) or a word (False).

    Returns:
        Clause name mapped to value, for the clauses that were present.

    Raises:
        ParseError: If a clause name repeats or is not allowed.
    """
    found: dict[str, str] = {}
    while not cursor.at_end():
        name = cursor.peek_word()
        if name not in allowed:
            raise ParseError(cursor.line, f"unexpected input {cursor.tokens[cursor.index].text!r}")
        if name in found:
            raise ParseError(cursor.line, f"clause '{name}' given twice")
        cursor.keyword(name)
        found[name] = cursor.string(name) if allowed[name] else cursor.word(name)
    return found


def _parse_source(cursor: _Cursor) -> Statement:
    """Parse: source NAME file STR sha256 STR [note STR]."""
    name = cursor.word("source name")
    cursor.keyword("file")
    file = cursor.string("file path")
    cursor.keyword("sha256")
    digest = cursor.string("sha256 digest")
    extra = _optional_clauses(cursor, {"note": True})
    return SourceDecl(name, file, digest.lower(), extra.get("note", ""), cursor.line)


def _parse_carrier(cursor: _Cursor) -> Statement:
    """Parse: carrier NAME from SRC key STR | carrier NAME items WORD+."""
    name = cursor.word("carrier name")
    if cursor.peek_word() == "from":
        cursor.keyword("from")
        source = cursor.word("source name")
        cursor.keyword("key")
        key_column = cursor.string("key column")
        cursor.finish()
        return CarrierDecl(name, source, key_column, (), cursor.line)
    cursor.keyword("items")
    items: list[str] = []
    while not cursor.at_end():
        items.append(cursor.word("item name"))
    if not items:
        raise ParseError(cursor.line, "a carrier needs at least one item")
    return CarrierDecl(name, "", "", tuple(items), cursor.line)


def _parse_regime(cursor: _Cursor) -> Statement:
    """Parse: regime NAME on CARRIER (by STR | explicit) [source SRC] [meaning STR]."""
    name = cursor.word("regime name")
    cursor.keyword("on")
    carrier = cursor.word("carrier name")
    if cursor.peek_word() == "by":
        cursor.keyword("by")
        column = cursor.string("key column")
        kind: Literal["key", "explicit"] = "key"
    else:
        cursor.keyword("explicit")
        column = ""
        kind = "explicit"
    found = _read_regime_clauses(cursor)
    return RegimeDecl(
        name, carrier, kind, column, found.get("source", ""), found.get("meaning", ""), cursor.line
    )


def _read_regime_clauses(cursor: _Cursor) -> dict[str, str]:
    """Read `source WORD` and `meaning STR` clauses in any order."""
    found: dict[str, str] = {}
    while not cursor.at_end():
        clause = cursor.peek_word()
        if clause not in ("source", "meaning"):
            raise ParseError(cursor.line, f"unexpected input {cursor.tokens[cursor.index].text!r}")
        if clause in found:
            raise ParseError(cursor.line, f"clause '{clause}' given twice")
        cursor.keyword(clause)
        found[clause] = cursor.word("source name") if clause == "source" else cursor.string("meaning")
    return found


def _parse_surface(cursor: _Cursor, role: Literal["surface", "probe"]) -> Statement:
    """Parse: surface|probe NAME on CARRIER column STR source SRC."""
    name = cursor.word(f"{role} name")
    cursor.keyword("on")
    carrier = cursor.word("carrier name")
    cursor.keyword("column")
    column = cursor.string("column name")
    cursor.keyword("source")
    source = cursor.word("source name")
    cursor.finish()
    return SurfaceDecl(name, carrier, role, column, source, cursor.line)


def _parse_operator(cursor: _Cursor) -> Statement:
    """Parse: operator NAME classified (prs|brk|ign|na) under REGIME."""
    name = cursor.word("operator name")
    cursor.keyword("classified")
    classification = cursor.word("classification")
    if classification not in ("prs", "brk", "ign", "na"):
        raise ParseError(cursor.line, "classification must be prs, brk, ign, or na")
    cursor.keyword("under")
    regime = cursor.word("regime name")
    cursor.finish()
    return OperatorDecl(name, cast("Classification", classification), regime, cursor.line)


def _parse_judge(cursor: _Cursor) -> Statement:
    """Parse: judge LABEL (same|distinct) ITEM ITEM under REGIME [from SRC] [scope STR]."""
    label = cursor.word("label")
    polarity = cursor.word("'same' or 'distinct'")
    if polarity not in ("same", "distinct"):
        raise ParseError(cursor.line, "expected 'same' or 'distinct'")
    first = cursor.word("first item")
    second = cursor.word("second item")
    cursor.keyword("under")
    regime = cursor.word("regime name")
    found: dict[str, str] = {}
    while not cursor.at_end():
        clause = cursor.peek_word()
        if clause not in ("from", "scope"):
            raise ParseError(cursor.line, f"unexpected input {cursor.tokens[cursor.index].text!r}")
        if clause in found:
            raise ParseError(cursor.line, f"clause '{clause}' given twice")
        cursor.keyword(clause)
        found[clause] = cursor.word("source name") if clause == "from" else cursor.string("scope")
    return Judge(
        label,
        cast("Polarity", polarity),
        first,
        second,
        regime,
        found.get("from", ""),
        found.get("scope", ""),
        cursor.line,
    )


def _parse_propose(cursor: _Cursor) -> Statement:
    """Parse: propose LABEL OPERATOR ITEM -> ITEM under REGIME [from SRC]."""
    label = cursor.word("label")
    operator = cursor.word("operator name")
    first = cursor.word("first item")
    cursor.arrow()
    second = cursor.word("second item")
    cursor.keyword("under")
    regime = cursor.word("regime name")
    source = ""
    if cursor.peek_word() == "from":
        cursor.keyword("from")
        source = cursor.word("source name")
    cursor.finish()
    return Propose(label, operator, first, second, regime, source, cursor.line)


def _parse_apply(cursor: _Cursor) -> Statement:
    """Parse: apply LABEL PROPOSAL."""
    label = cursor.word("label")
    proposal = cursor.word("proposal label")
    cursor.finish()
    return Apply(label, proposal, cursor.line)


def _parse_check(cursor: _Cursor) -> Statement:
    """Parse the five check forms."""
    label = cursor.word("label")
    kind = cursor.word("check kind")
    if kind == "faithful":
        subject = cursor.word("regime name")
        cursor.keyword("against")
        obj = cursor.word("surface or probe name")
        cursor.finish()
        return Check(label, "faithful", subject, obj, "", "", cursor.line)
    if kind == "collisions":
        subject = cursor.word("surface name")
        cursor.keyword("against")
        obj = cursor.word("regime name")
        cursor.finish()
        return Check(label, "collisions", subject, obj, "", "", cursor.line)
    if kind in ("consistent", "coverage"):
        subject = cursor.word("regime name")
        cursor.finish()
        return Check(label, cast("CheckKind", kind), subject, "", "", "", cursor.line)
    if kind == "status":
        first = cursor.word("first item")
        second = cursor.word("second item")
        cursor.keyword("under")
        regime = cursor.word("regime name")
        cursor.finish()
        return Check(label, "status", regime, "", first, second, cursor.line)
    raise ParseError(
        cursor.line, "check kind must be faithful, collisions, consistent, coverage, or status"
    )


def _parse_explain(cursor: _Cursor) -> Statement:
    """Parse: explain LABEL."""
    target = cursor.word("label")
    cursor.finish()
    return Explain(target, cursor.line)


def _split_statements(text: str) -> list[tuple[int, str]]:
    """Group physical lines into logical statements.

    Returns:
        Pairs of (first line number, statement text).
    """
    statements: list[tuple[int, str]] = []
    current_line = 0
    current: list[str] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in " \t":
            if not current:
                raise ParseError(number, "continuation line with no statement to continue")
            current.append(raw)
            continue
        if current:
            statements.append((current_line, "\n".join(current)))
        current_line = number
        current = [raw]
    if current:
        statements.append((current_line, "\n".join(current)))
    return statements


def parse(text: str, path: str = "") -> Program:
    """Parse program text.

    Args:
        text: Full program text.
        path: Path the text came from, kept on the Program.

    Returns:
        The parsed Program.

    Raises:
        ParseError: If any statement does not match the grammar.
    """
    statements: list[Statement] = []
    for line, statement_text in _split_statements(text):
        tokens = tokenize(statement_text, line)
        if not tokens or tokens[0].kind != "word":
            raise ParseError(line, "a statement must start with a keyword")
        cursor = _Cursor(tokens, line)
        keyword = cursor.word("keyword")
        if keyword == "source":
            statements.append(_parse_source(cursor))
        elif keyword == "carrier":
            statements.append(_parse_carrier(cursor))
        elif keyword == "regime":
            statements.append(_parse_regime(cursor))
        elif keyword == "surface":
            statements.append(_parse_surface(cursor, "surface"))
        elif keyword == "probe":
            statements.append(_parse_surface(cursor, "probe"))
        elif keyword == "operator":
            statements.append(_parse_operator(cursor))
        elif keyword == "judge":
            statements.append(_parse_judge(cursor))
        elif keyword == "propose":
            statements.append(_parse_propose(cursor))
        elif keyword == "apply":
            statements.append(_parse_apply(cursor))
        elif keyword == "check":
            statements.append(_parse_check(cursor))
        elif keyword == "explain":
            statements.append(_parse_explain(cursor))
        else:
            raise ParseError(line, f"unknown statement keyword {keyword!r}")
    return Program(tuple(statements), path)
