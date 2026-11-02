"""checker.py - Static semantic checks for IdentityOps programs.

WHAT: Resolves every name to a declaration, checks that each reference has the
      right kind, and rejects cross-category operations before any data is read.
WHY: The language separates records from referents, surfaces from probes, and
     regimes from each other. Most mistakes of that kind are visible in the
     program text alone.
OBS: The checker never reads data files. Existence of items in a loaded carrier
     and of columns in a table is checked by the interpreter when it loads data.
OBS: A diagnostic is a rejection of the program. It is not an operation outcome.
"""

from dataclasses import dataclass

from .syntax import (
    Apply,
    CarrierDecl,
    Check,
    Explain,
    Judge,
    OperatorDecl,
    Program,
    Propose,
    RegimeDecl,
    SourceDecl,
    SurfaceDecl,
)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One static problem found in a program.

    Attributes:
        line: One-based line number of the offending statement.
        message: Description of the problem.
    """

    line: int
    message: str

    def __str__(self) -> str:
        """Format as `line N: message`."""
        return f"line {self.line}: {self.message}"


class _Scope:
    """Declarations seen so far, by kind."""

    def __init__(self) -> None:
        """Start with no declarations."""
        self.sources: dict[str, SourceDecl] = {}
        self.carriers: dict[str, CarrierDecl] = {}
        self.regimes: dict[str, RegimeDecl] = {}
        self.surfaces: dict[str, SurfaceDecl] = {}
        self.operators: dict[str, OperatorDecl] = {}
        self.labels: dict[str, str] = {}
        self.proposals: dict[str, Propose] = {}
        self.applied: set[str] = set()


def _declare_once(
    table: dict[str, object], name: str, value: object, kind: str, line: int, out: list[Diagnostic]
) -> None:
    """Record a declaration or report a duplicate."""
    if name in table:
        out.append(Diagnostic(line, f"{kind} '{name}' is already declared"))
    else:
        table[name] = value


def _need_source(scope: _Scope, name: str, line: int, out: list[Diagnostic]) -> None:
    """Report an unknown source name when a source is named."""
    if name and name not in scope.sources:
        out.append(Diagnostic(line, f"unknown source '{name}'"))


def _check_carrier(scope: _Scope, stmt: CarrierDecl, out: list[Diagnostic]) -> None:
    """Check a carrier declaration."""
    _declare_once(scope.carriers, stmt.name, stmt, "carrier", stmt.line, out)
    if stmt.source:
        _need_source(scope, stmt.source, stmt.line, out)
    if len(set(stmt.inline_items)) != len(stmt.inline_items):
        out.append(Diagnostic(stmt.line, f"carrier '{stmt.name}' lists an item twice"))


def _check_regime(scope: _Scope, stmt: RegimeDecl, out: list[Diagnostic]) -> None:
    """Check a regime declaration."""
    _declare_once(scope.regimes, stmt.name, stmt, "regime", stmt.line, out)
    carrier = scope.carriers.get(stmt.carrier)
    if carrier is None:
        out.append(Diagnostic(stmt.line, f"unknown carrier '{stmt.carrier}'"))
    elif stmt.kind == "key" and not carrier.source:
        out.append(
            Diagnostic(stmt.line, f"key regime '{stmt.name}' needs a carrier loaded from a source")
        )
    _need_source(scope, stmt.source, stmt.line, out)


def _check_surface(scope: _Scope, stmt: SurfaceDecl, out: list[Diagnostic]) -> None:
    """Check a surface or probe declaration."""
    _declare_once(scope.surfaces, stmt.name, stmt, stmt.role, stmt.line, out)
    carrier = scope.carriers.get(stmt.carrier)
    if carrier is None:
        out.append(Diagnostic(stmt.line, f"unknown carrier '{stmt.carrier}'"))
    elif not carrier.source:
        out.append(
            Diagnostic(stmt.line, f"{stmt.role} '{stmt.name}' needs a carrier loaded from a source")
        )
    elif carrier.source != stmt.source:
        out.append(
            Diagnostic(
                stmt.line,
                f"{stmt.role} '{stmt.name}' reads source '{stmt.source}' but carrier "
                f"'{stmt.carrier}' is loaded from '{carrier.source}'",
            )
        )
    _need_source(scope, stmt.source, stmt.line, out)


def _check_operator(scope: _Scope, stmt: OperatorDecl, out: list[Diagnostic]) -> None:
    """Check an operator declaration."""
    _declare_once(scope.operators, stmt.name, stmt, "operator", stmt.line, out)
    if stmt.regime not in scope.regimes:
        out.append(Diagnostic(stmt.line, f"unknown regime '{stmt.regime}'"))


def _claim_label(scope: _Scope, label: str, kind: str, line: int, out: list[Diagnostic]) -> None:
    """Record an operation label or report a duplicate."""
    if label in scope.labels:
        out.append(Diagnostic(line, f"label '{label}' is already used"))
    else:
        scope.labels[label] = kind


def _check_item_inline(
    scope: _Scope, regime_name: str, items: tuple[str, ...], line: int, out: list[Diagnostic]
) -> None:
    """Check item names against an inline carrier when the carrier is inline."""
    regime = scope.regimes.get(regime_name)
    if regime is None:
        return
    carrier = scope.carriers.get(regime.carrier)
    if carrier is None or carrier.source:
        return
    for item in items:
        if item not in carrier.inline_items:
            out.append(Diagnostic(line, f"'{item}' is not an item of carrier '{carrier.name}'"))


def _check_judge(scope: _Scope, stmt: Judge, out: list[Diagnostic]) -> None:
    """Check a judge statement."""
    _claim_label(scope, stmt.label, "judge", stmt.line, out)
    if stmt.regime not in scope.regimes:
        out.append(Diagnostic(stmt.line, f"unknown regime '{stmt.regime}'"))
    _need_source(scope, stmt.source, stmt.line, out)
    if stmt.first == stmt.second:
        out.append(Diagnostic(stmt.line, "a judgment needs two different items"))
    _check_item_inline(scope, stmt.regime, (stmt.first, stmt.second), stmt.line, out)


def _check_propose(scope: _Scope, stmt: Propose, out: list[Diagnostic]) -> None:
    """Check a propose statement."""
    _claim_label(scope, stmt.label, "propose", stmt.line, out)
    operator = scope.operators.get(stmt.operator)
    if operator is None:
        out.append(Diagnostic(stmt.line, f"unknown operator '{stmt.operator}'"))
    elif operator.regime != stmt.regime:
        out.append(
            Diagnostic(
                stmt.line,
                f"operator '{stmt.operator}' is classified under regime '{operator.regime}', "
                f"not '{stmt.regime}'",
            )
        )
    if stmt.regime not in scope.regimes:
        out.append(Diagnostic(stmt.line, f"unknown regime '{stmt.regime}'"))
    _need_source(scope, stmt.source, stmt.line, out)
    if stmt.first == stmt.second:
        out.append(Diagnostic(stmt.line, "a proposed step needs two different items"))
    _check_item_inline(scope, stmt.regime, (stmt.first, stmt.second), stmt.line, out)
    scope.proposals[stmt.label] = stmt


def _check_apply(scope: _Scope, stmt: Apply, out: list[Diagnostic]) -> None:
    """Check an apply statement."""
    _claim_label(scope, stmt.label, "apply", stmt.line, out)
    if stmt.proposal not in scope.proposals:
        out.append(Diagnostic(stmt.line, f"unknown proposal '{stmt.proposal}'"))
    elif stmt.proposal in scope.applied:
        out.append(Diagnostic(stmt.line, f"proposal '{stmt.proposal}' is already applied"))
    else:
        scope.applied.add(stmt.proposal)


def _check_check(scope: _Scope, stmt: Check, out: list[Diagnostic]) -> None:
    """Check a check statement."""
    _claim_label(scope, stmt.label, "check", stmt.line, out)
    if stmt.kind == "faithful":
        regime = scope.regimes.get(stmt.subject)
        surface = scope.surfaces.get(stmt.object)
        if regime is None:
            out.append(Diagnostic(stmt.line, f"unknown regime '{stmt.subject}'"))
        if surface is None:
            out.append(Diagnostic(stmt.line, f"unknown surface or probe '{stmt.object}'"))
        if regime is not None and surface is not None and regime.carrier != surface.carrier:
            out.append(
                Diagnostic(
                    stmt.line,
                    f"regime '{regime.name}' is on carrier '{regime.carrier}' but "
                    f"'{surface.name}' is on carrier '{surface.carrier}'",
                )
            )
    elif stmt.kind == "collisions":
        surface = scope.surfaces.get(stmt.subject)
        regime = scope.regimes.get(stmt.object)
        if surface is None:
            out.append(Diagnostic(stmt.line, f"unknown surface '{stmt.subject}'"))
        elif surface.role != "surface":
            out.append(
                Diagnostic(stmt.line, f"'{surface.name}' is a probe; collisions applies to surfaces")
            )
        if regime is None:
            out.append(Diagnostic(stmt.line, f"unknown regime '{stmt.object}'"))
        if regime is not None and surface is not None and regime.carrier != surface.carrier:
            out.append(
                Diagnostic(
                    stmt.line,
                    f"surface '{surface.name}' is on carrier '{surface.carrier}' but "
                    f"regime '{regime.name}' is on carrier '{regime.carrier}'",
                )
            )
    else:
        if stmt.subject not in scope.regimes:
            out.append(Diagnostic(stmt.line, f"unknown regime '{stmt.subject}'"))
        if stmt.kind == "status":
            _check_item_inline(scope, stmt.subject, (stmt.first, stmt.second), stmt.line, out)


def _check_explain(scope: _Scope, stmt: Explain, out: list[Diagnostic]) -> None:
    """Check an explain statement."""
    if stmt.target not in scope.labels:
        out.append(Diagnostic(stmt.line, f"unknown label '{stmt.target}'"))


def check_program(program: Program) -> tuple[Diagnostic, ...]:
    """Check a program without reading any data.

    Args:
        program: Parsed program.

    Returns:
        Diagnostics in source order. An empty tuple means the program is well formed.
    """
    scope = _Scope()
    out: list[Diagnostic] = []
    for stmt in program.statements:
        if isinstance(stmt, SourceDecl):
            _declare_once(scope.sources, stmt.name, stmt, "source", stmt.line, out)
        elif isinstance(stmt, CarrierDecl):
            _check_carrier(scope, stmt, out)
        elif isinstance(stmt, RegimeDecl):
            _check_regime(scope, stmt, out)
        elif isinstance(stmt, SurfaceDecl):
            _check_surface(scope, stmt, out)
        elif isinstance(stmt, OperatorDecl):
            _check_operator(scope, stmt, out)
        elif isinstance(stmt, Judge):
            _check_judge(scope, stmt, out)
        elif isinstance(stmt, Propose):
            _check_propose(scope, stmt, out)
        elif isinstance(stmt, Apply):
            _check_apply(scope, stmt, out)
        elif isinstance(stmt, Check):
            _check_check(scope, stmt, out)
        else:
            _check_explain(scope, stmt, out)
    return tuple(out)
