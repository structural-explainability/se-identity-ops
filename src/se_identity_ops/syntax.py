"""syntax.py - Typed abstract syntax for IdentityOps programs.

WHAT: Frozen dataclasses for the five declarations and the five operations.
WHY: Parsing, static checking, and interpretation all work on these types, so
     each statement kind has exactly one shape.
OBS: A program is a tuple of statements in source order. Source order is part
     of the meaning of a program (see SEMANTICS.md, "Order").
OBS: Item names are plain strings. A name is a record, never a referent. The
     interpreter never turns a record name into a referent claim.
"""

from dataclasses import dataclass
from typing import Literal

Classification = Literal["prs", "brk", "ign", "na"]
Polarity = Literal["same", "distinct"]
CheckKind = Literal["faithful", "collisions", "consistent", "status", "coverage"]
SurfaceRole = Literal["surface", "probe"]


@dataclass(frozen=True, slots=True)
class SourceDecl:
    """Declare a data file and its expected SHA-256 digest.

    Attributes:
        name: Source name used in `from` and `source` clauses.
        file: Path relative to the program file.
        sha256: Expected lowercase hex digest of the file bytes.
        note: Free-text provenance note.
        line: One-based line number of the declaration.
    """

    name: str
    file: str
    sha256: str
    note: str
    line: int


@dataclass(frozen=True, slots=True)
class CarrierDecl:
    """Declare the kind of objects under discussion.

    A carrier is either loaded from a source table (`key_column` names a column
    whose values are unique item names) or given inline as a finite list.

    Attributes:
        name: Carrier name.
        source: Source name, or empty string for an inline carrier.
        key_column: Column holding item names, or empty string when inline.
        inline_items: Item names of an inline carrier, in declaration order.
        line: One-based line number of the declaration.
    """

    name: str
    source: str
    key_column: str
    inline_items: tuple[str, ...]
    line: int


@dataclass(frozen=True, slots=True)
class RegimeDecl:
    """Declare an identity criterion over a carrier.

    A `key` regime relates two items when they have the same non-empty value in
    `column`. An `explicit` regime relates items only through `judge` and `apply`.
    An empty key value places an item in no class: the criterion is silent about it.

    Attributes:
        name: Regime name.
        carrier: Carrier name.
        kind: "key" or "explicit".
        column: Column name for a key regime, else empty string.
        source: Source name that grounds the criterion, or empty string.
        meaning: Free text saying what the criterion claims and does not claim.
        line: One-based line number of the declaration.
    """

    name: str
    carrier: str
    kind: Literal["key", "explicit"]
    column: str
    source: str
    meaning: str
    line: int


@dataclass(frozen=True, slots=True)
class SurfaceDecl:
    """Declare an observed implementation behavior over a carrier.

    A surface (role "surface") is an implementation mechanism whose output
    determines treatment. A probe (role "probe") is a read-only observation of
    implementation output. Both read one column of a source table.

    Attributes:
        name: Surface or probe name.
        carrier: Carrier name.
        role: "surface" or "probe".
        column: Source column holding the observed value for each item.
        source: Source name that grounds the observation.
        line: One-based line number of the declaration.
    """

    name: str
    carrier: str
    role: SurfaceRole
    column: str
    source: str
    line: int


@dataclass(frozen=True, slots=True)
class OperatorDecl:
    """Declare how a regime classifies an operator.

    Attributes:
        name: Operator name.
        classification: "prs" (preserving), "brk" (breaking), "ign" (ignoring),
            or "na" (inapplicable).
        regime: Regime name the classification is relative to.
        line: One-based line number of the declaration.
    """

    name: str
    classification: Classification
    regime: str
    line: int


@dataclass(frozen=True, slots=True)
class Judge:
    """Record a same or distinct judgment under a regime.

    Attributes:
        label: Label used by `explain`.
        polarity: "same" or "distinct".
        first: First item name.
        second: Second item name.
        regime: Regime name.
        source: Source name for the evidence, or empty string.
        scope: Free text saying what the judgment covers.
        line: One-based line number of the statement.
    """

    label: str
    polarity: Polarity
    first: str
    second: str
    regime: str
    source: str
    scope: str
    line: int


@dataclass(frozen=True, slots=True)
class Propose:
    """Construct a transformation proposal without changing state.

    Attributes:
        label: Proposal label used by `apply`.
        operator: Operator name.
        first: Item name before the step.
        second: Item name after the step.
        regime: Regime name.
        source: Source name for the evidence, or empty string.
        line: One-based line number of the statement.
    """

    label: str
    operator: str
    first: str
    second: str
    regime: str
    source: str
    line: int


@dataclass(frozen=True, slots=True)
class Apply:
    """Apply a proposal to the model state if its conditions hold.

    Attributes:
        label: Label used by `explain`.
        proposal: Label of the proposal to apply.
        line: One-based line number of the statement.
    """

    label: str
    proposal: str
    line: int


@dataclass(frozen=True, slots=True)
class Check:
    """Evaluate a declared obligation.

    Which fields are used depends on `kind`:

    - faithful: `subject` is a regime, `object` is a surface or probe.
    - collisions: `subject` is a surface, `object` is a regime.
    - consistent: `subject` is a regime.
    - coverage: `subject` is a regime.
    - status: `subject` is a regime; `first` and `second` are items.

    Attributes:
        label: Label used by `explain`.
        kind: Check kind.
        subject: First named declaration.
        object: Second named declaration, or empty string.
        first: First item name for `status`, else empty string.
        second: Second item name for `status`, else empty string.
        line: One-based line number of the statement.
    """

    label: str
    kind: CheckKind
    subject: str
    object: str
    first: str
    second: str
    line: int


@dataclass(frozen=True, slots=True)
class Explain:
    """Produce an explanation for a labeled operation.

    Attributes:
        target: Label of the operation to explain.
        line: One-based line number of the statement.
    """

    target: str
    line: int


Statement = (
    SourceDecl
    | CarrierDecl
    | RegimeDecl
    | SurfaceDecl
    | OperatorDecl
    | Judge
    | Propose
    | Apply
    | Check
    | Explain
)


@dataclass(frozen=True, slots=True)
class Program:
    """A parsed IdentityOps program.

    Attributes:
        statements: Statements in source order.
        path: Path the program was read from, or empty string.
    """

    statements: tuple[Statement, ...]
    path: str
