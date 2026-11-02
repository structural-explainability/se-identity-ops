"""interpreter.py - The deterministic reference interpreter.

WHAT: Executes a checked program statement by statement against an immutable
      model state, and returns one result per operation plus every state snapshot.
WHY: This is the smallest interpreter that can run the three experiments. It is
     the executable reading of SEMANTICS.md.
OBS: `judge` and `apply` each create a new snapshot. `propose`, `check`, and
     `explain` never change state.
OBS: `apply` changes a model state only. It does not decide what any record or
     referent is in the world.
OBS: Output depends only on the program text and the verified source files. No
     clock, random number, or environment value is read.
"""

from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from pathlib import Path

from .checker import check_program
from .loader import SourceError, Table, load_table
from .relation import DistinctPair, Relation, SamePair
from .results import (
    AppliedStep,
    DerivationStep,
    Explanation,
    ExplanationKind,
    Judgment,
    LimitationCause,
    OperationResult,
    Outcome,
    State,
)
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

MAX_EXAMPLES = 20


class RunError(Exception):
    """Raised when a program cannot run: bad data, missing item, or ill-formed program."""


@dataclass(frozen=True, slots=True)
class Run:
    """The complete record of one program execution.

    Attributes:
        program: The executed program.
        tables: Triples of (source name, sha256, row count) for loaded sources.
        results: One result per operation, in order.
        states: Every state snapshot, starting with the initial state.
    """

    program: Program
    tables: tuple[tuple[str, str, int], ...]
    results: tuple[OperationResult, ...]
    states: tuple[State, ...]
    classes: tuple[tuple[str, tuple[tuple[str, ...], ...]], ...] = ()

    def same_classes(self, regime: str) -> frozenset[frozenset[str]]:
        """Return the generated same-classes of a regime in the final state.

        Every item appears in exactly one class; an item related to nothing is
        in a class by itself.

        Raises:
            KeyError: If the regime was not declared.
        """
        for name, groups in self.classes:
            if name == regime:
                return frozenset(frozenset(group) for group in groups)
        raise KeyError(regime)

    @property
    def final_state(self) -> State:
        """Return the last state snapshot."""
        return self.states[-1]

    def result(self, label: str, operation: str = "") -> OperationResult:
        """Return the result for a label, optionally for one operation kind.

        Raises:
            KeyError: If no result matches.
        """
        for found in self.results:
            if found.label == label and (not operation or found.operation == operation):
                return found
        raise KeyError(label)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-ready dictionary with a fixed key order and no timestamps."""
        return {
            "program": self.program.path,
            "sources": [
                {"name": name, "sha256": digest, "rows": rows}
                for name, digest, rows in self.tables
            ],
            "results": [_plain(result) for result in self.results],
            "final_state": _plain(self.final_state),
        }


def _plain(value: object) -> object:
    """Convert a result record to plain JSON types.

    Name/value pairs stored as tuples of tuples (`counts` and `witness`) become
    dictionaries so the JSON is easy to read.
    """
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple | list):
        return [_plain(entry) for entry in value]
    if isinstance(value, dict):
        return {key: _plain(entry) for key, entry in value.items()}
    if is_dataclass(value) and not isinstance(value, type):
        converted = {
            field.name: _plain(getattr(value, field.name)) for field in fields(value)
        }
        for name in ("counts", "witness"):
            pairs = converted.get(name)
            if isinstance(pairs, list):
                converted[name] = {pair[0]: pair[1] for pair in pairs}
        return converted
    return value


def _counts(**numbers: int) -> tuple[tuple[str, int], ...]:
    """Return counts sorted by name."""
    return tuple(sorted(numbers.items()))


def _pairs(**texts: str) -> tuple[tuple[str, str], ...]:
    """Return witness fields sorted by name."""
    return tuple(sorted(texts.items()))


class _Machine:
    """Mutable execution state. Only the interpreter module uses it."""

    def __init__(self, program: Program, base_dir: Path) -> None:
        """Prepare an empty machine."""
        self.program = program
        self.base_dir = base_dir
        self.tables: dict[str, Table] = {}
        self.carriers: dict[str, CarrierDecl] = {}
        self.carrier_items: dict[str, tuple[str, ...]] = {}
        self.carrier_index: dict[str, dict[str, int]] = {}
        self.regimes: dict[str, RegimeDecl] = {}
        self.surfaces: dict[str, SurfaceDecl] = {}
        self.operators: dict[str, OperatorDecl] = {}
        self.proposals: dict[str, Propose] = {}
        self.states: list[State] = [State(0)]
        self.results: list[OperationResult] = []
        self.labelled: dict[str, OperationResult] = {}
        self._relations: dict[tuple[str, int], Relation] = {}

    # ------------------------------------------------------------------
    # Declarations
    # ------------------------------------------------------------------

    def declare_source(self, stmt: SourceDecl) -> None:
        """Load and verify a source table."""
        try:
            self.tables[stmt.name] = load_table(stmt, self.base_dir)
        except SourceError as error:
            raise RunError(str(error)) from error

    def declare_carrier(self, stmt: CarrierDecl) -> None:
        """Build the item list of a carrier."""
        self.carriers[stmt.name] = stmt
        if stmt.source:
            try:
                items = self.tables[stmt.source].column(stmt.key_column)
            except SourceError as error:
                raise RunError(f"line {stmt.line}: {error}") from error
        else:
            items = stmt.inline_items
        index = {name: position for position, name in enumerate(items)}
        if len(index) != len(items):
            raise RunError(
                f"line {stmt.line}: carrier '{stmt.name}' has repeated item names"
            )
        self.carrier_items[stmt.name] = items
        self.carrier_index[stmt.name] = index

    def declare_regime(self, stmt: RegimeDecl) -> None:
        """Register a regime and verify its key column."""
        self.regimes[stmt.name] = stmt
        if stmt.kind == "key":
            self._column_values(stmt.carrier, stmt.column, stmt.line)

    def declare_surface(self, stmt: SurfaceDecl) -> None:
        """Register a surface or probe and verify its column."""
        self.surfaces[stmt.name] = stmt
        self._column_values(stmt.carrier, stmt.column, stmt.line)

    def declare_operator(self, stmt: OperatorDecl) -> None:
        """Register an operator classification."""
        self.operators[stmt.name] = stmt

    def _column_values(self, carrier: str, column: str, line: int) -> tuple[str, ...]:
        """Return one column of the table behind a carrier."""
        source = self.carriers[carrier].source
        try:
            return self.tables[source].column(column)
        except SourceError as error:
            raise RunError(f"line {line}: {error}") from error

    # ------------------------------------------------------------------
    # Relations
    # ------------------------------------------------------------------

    def relation(self, regime_name: str) -> Relation:
        """Return the commitments of a regime in the current state."""
        state = self.states[-1]
        cached = self._relations.get((regime_name, state.index))
        if cached is not None:
            return cached
        regime = self.regimes[regime_name]
        keys: tuple[str, ...] | None = None
        column = ""
        if regime.kind == "key":
            keys = self._column_values(regime.carrier, regime.column, regime.line)
            column = regime.column
        same: list[SamePair] = []
        distinct: list[DistinctPair] = []
        for judgment in state.judgments:
            if judgment.regime != regime_name:
                continue
            if judgment.polarity == "same":
                same.append(
                    SamePair(
                        judgment.first,
                        judgment.second,
                        "judgment",
                        judgment.label,
                        judgment.source,
                    )
                )
            else:
                distinct.append(
                    DistinctPair(
                        judgment.first, judgment.second, judgment.label, judgment.source
                    )
                )
        for step in state.steps:
            if step.regime == regime_name and step.licensed:
                same.append(
                    SamePair(step.first, step.second, "step", step.label, step.source)
                )
        built = Relation(
            self.carrier_items[regime.carrier],
            keys,
            column,
            tuple(same),
            tuple(distinct),
        )
        self._relations[(regime_name, state.index)] = built
        return built

    def _need_items(self, carrier: str, items: tuple[str, ...], line: int) -> None:
        """Require that every item belongs to the carrier."""
        index = self.carrier_index[carrier]
        for item in items:
            if item not in index:
                raise RunError(
                    f"line {line}: '{item}' is not an item of carrier '{carrier}'"
                )

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def _record(self, result: OperationResult) -> None:
        """Store a result."""
        self.results.append(result)
        self.labelled[result.label] = result

    def _push_state(self, state: State) -> None:
        """Append a new snapshot."""
        self.states.append(state)

    # ------------------------------------------------------------------
    # judge
    # ------------------------------------------------------------------

    def run_judge(self, stmt: Judge) -> None:
        """Record a same or distinct judgment. Evidence is never discarded."""
        regime = self.regimes[stmt.regime]
        self._need_items(regime.carrier, (stmt.first, stmt.second), stmt.line)
        before = self.relation(stmt.regime)
        was_consistent = before.consistent()
        if stmt.polarity == "same":
            already = before.required(stmt.first, stmt.second)
            contradicts = before.forbidden_by(stmt.first, stmt.second) is not None
        else:
            already = before.forbidden_by(stmt.first, stmt.second) is not None
            contradicts = before.required(stmt.first, stmt.second)
        if not was_consistent:
            outcome, word = Outcome.UNDETERMINED, "recorded_in_inconsistent_state"
        elif contradicts:
            outcome, word = Outcome.REFUTED, "conflicting"
        elif already:
            outcome, word = Outcome.ESTABLISHED, "redundant"
        else:
            outcome, word = Outcome.ESTABLISHED, "recorded"
        judgment = Judgment(
            stmt.label,
            stmt.polarity,
            stmt.first,
            stmt.second,
            stmt.regime,
            stmt.source,
            stmt.scope,
            contradicts and was_consistent,
        )
        previous = self.states[-1]
        new_state = State(
            previous.index + 1,
            previous.judgments + (judgment,),
            previous.steps,
            previous.log + ((stmt.label, word),),
        )
        self._push_state(new_state)
        explanation = self._explain_judgment(stmt, before, word, was_consistent)
        self._record(
            OperationResult(
                stmt.label,
                "judge",
                outcome,
                word,
                f"{stmt.polarity} judgment on {stmt.first}, {stmt.second} under {stmt.regime}: {word}",
                (),
                explanation,
                new_state.index,
            )
        )

    def _explain_judgment(
        self, stmt: Judge, before: Relation, word: str, was_consistent: bool
    ) -> Explanation:
        """Build the explanation of a judgment against the commitments before it."""
        inputs = tuple(name for name in (stmt.regime, stmt.source) if name)
        if not was_consistent:
            conflict = before.conflicts()[0]
            return self._conflict_explanation(stmt.label, before, conflict, inputs)
        if word == "conflicting":
            if stmt.polarity == "distinct":
                chain = before.path(stmt.first, stmt.second)
                return Explanation(
                    stmt.label,
                    ExplanationKind.WITNESS,
                    f"{stmt.first} and {stmt.second} are already required identical, "
                    "so this distinct judgment contradicts the commitments before it.",
                    (chain,),
                    _pairs(contradicts="required_identical", judgment=stmt.label),
                    None,
                    inputs,
                )
            forbidding = before.forbidden_by(stmt.first, stmt.second)
            if forbidding is None:
                raise RunError(
                    "internal: conflicting same judgment without a forbidding pair"
                )
            return self._forbidden_explanation(
                stmt.label, before, stmt.first, stmt.second, forbidding, inputs
            )
        if word == "redundant":
            if stmt.polarity == "same":
                chain = before.path(stmt.first, stmt.second)
                return Explanation(
                    stmt.label,
                    ExplanationKind.DERIVATION,
                    f"{stmt.first} and {stmt.second} were already required identical.",
                    (chain,),
                    (),
                    None,
                    inputs,
                )
            forbidding = before.forbidden_by(stmt.first, stmt.second)
            if forbidding is None:
                raise RunError(
                    "internal: redundant distinct judgment without a forbidding pair"
                )
            return self._forbidden_explanation(
                stmt.label, before, stmt.first, stmt.second, forbidding, inputs
            )
        step = DerivationStep(
            stmt.first, stmt.second, "judgment", stmt.label, stmt.source
        )
        return Explanation(
            stmt.label,
            ExplanationKind.DERIVATION,
            f"Recorded as a {stmt.polarity} judgment under {stmt.regime}"
            + (f" from {stmt.source}" if stmt.source else " with no source")
            + ".",
            ((step,),) if stmt.polarity == "same" else (),
            _pairs(polarity=stmt.polarity, scope=stmt.scope),
            None,
            inputs,
        )

    def _forbidden_explanation(
        self,
        label: str,
        relation: Relation,
        first: str,
        second: str,
        forbidding: DistinctPair,
        inputs: tuple[str, ...],
    ) -> Explanation:
        """Explain why identifying two items is forbidden by a distinct judgment."""
        if relation.class_of(forbidding.first) == relation.class_of(first):
            chain_a = relation.path(forbidding.first, first)
            chain_b = relation.path(forbidding.second, second)
        else:
            chain_a = relation.path(forbidding.first, second)
            chain_b = relation.path(forbidding.second, first)
        return Explanation(
            label,
            ExplanationKind.WITNESS,
            f"Identifying {first} and {second} would identify {forbidding.first} and "
            f"{forbidding.second}, which judgment {forbidding.label} asserts distinct.",
            (chain_a, chain_b),
            _pairs(
                distinct_first=forbidding.first,
                distinct_judgment=forbidding.label,
                distinct_second=forbidding.second,
            ),
            None,
            inputs,
        )

    def _conflict_explanation(
        self,
        label: str,
        relation: Relation,
        conflict: DistinctPair,
        inputs: tuple[str, ...],
    ) -> Explanation:
        """Explain an inconsistency: a distinct pair inside one generated class."""
        chain = relation.path(conflict.first, conflict.second)
        return Explanation(
            label,
            ExplanationKind.WITNESS,
            f"Judgment {conflict.label} asserts {conflict.first} and {conflict.second} distinct, "
            "but the same-commitments join them.",
            (chain,),
            _pairs(
                distinct_first=conflict.first,
                distinct_judgment=conflict.label,
                distinct_second=conflict.second,
            ),
            None,
            inputs,
        )

    # ------------------------------------------------------------------
    # propose and apply
    # ------------------------------------------------------------------

    def run_propose(self, stmt: Propose) -> None:
        """Construct a proposal. State is not changed."""
        regime = self.regimes[stmt.regime]
        self._need_items(regime.carrier, (stmt.first, stmt.second), stmt.line)
        self.proposals[stmt.label] = stmt
        classification = self.operators[stmt.operator].classification
        explanation = Explanation(
            stmt.label,
            ExplanationKind.DERIVATION,
            f"Proposed step {stmt.first} -> {stmt.second} by operator {stmt.operator}, "
            f"classified {classification} under {stmt.regime}. No state changed.",
            (),
            _pairs(classification=classification, operator=stmt.operator),
            None,
            tuple(name for name in (stmt.regime, stmt.operator, stmt.source) if name),
        )
        self._record(
            OperationResult(
                stmt.label,
                "propose",
                Outcome.ESTABLISHED,
                "proposed",
                f"{stmt.operator}: {stmt.first} -> {stmt.second} under {stmt.regime}; state unchanged",
                (),
                explanation,
                self.states[-1].index,
            )
        )

    def run_apply(self, stmt: Apply) -> None:
        """Apply a proposal to the model state when its conditions hold."""
        proposal = self.proposals[stmt.proposal]
        classification = self.operators[proposal.operator].classification
        relation = self.relation(proposal.regime)
        inputs = tuple(
            name
            for name in (proposal.regime, proposal.operator, proposal.source)
            if name
        )
        first, second = proposal.first, proposal.second
        record_step = False
        licensed = False
        explanation: Explanation
        if classification == "na":
            outcome, word = Outcome.UNDETERMINED, "inapplicable"
            explanation = self._limitation(
                stmt.label,
                LimitationCause.INAPPLICABILITY,
                f"Operator {proposal.operator} is inapplicable under {proposal.regime}; "
                "the step was not executed.",
                inputs,
            )
        elif classification == "ign":
            outcome, word = Outcome.UNDETERMINED, "ignoring"
            record_step = True
            explanation = self._limitation(
                stmt.label,
                LimitationCause.OPERATOR_UNDERDETERMINATION,
                f"Operator {proposal.operator} is identity-ignoring under {proposal.regime}; "
                "the step was recorded, but the classification alone neither licenses nor "
                "breaks continuation.",
                inputs,
            )
        elif classification == "brk":
            outcome, word = Outcome.REFUTED, "broken"
            record_step = True
            explanation = Explanation(
                stmt.label,
                ExplanationKind.WITNESS,
                f"Operator {proposal.operator} is identity-breaking under {proposal.regime}; "
                "the step was recorded and continuation is not licensed. Breaking does not "
                "assert that the two items are distinct.",
                (),
                _pairs(classification="brk", operator=proposal.operator),
                None,
                inputs,
            )
        elif not relation.consistent():
            outcome, word = Outcome.UNDETERMINED, "state_inconsistent"
            explanation = self._conflict_explanation(
                stmt.label, relation, relation.conflicts()[0], inputs
            )
        else:
            forbidding = relation.forbidden_by(first, second)
            if forbidding is not None:
                outcome, word = Outcome.REFUTED, "blocked"
                explanation = self._forbidden_explanation(
                    stmt.label, relation, first, second, forbidding, inputs
                )
            else:
                outcome, word = Outcome.ESTABLISHED, "licensed"
                record_step = True
                licensed = True
                already = relation.required(first, second)
                explanation = Explanation(
                    stmt.label,
                    ExplanationKind.DERIVATION,
                    f"Operator {proposal.operator} is preserving under {proposal.regime} and "
                    f"no distinct judgment forbids {first} and {second}; the step is licensed"
                    + (
                        " (the pair was already required identical)."
                        if already
                        else "."
                    ),
                    (
                        (
                            DerivationStep(
                                first, second, "step", stmt.label, proposal.source
                            ),
                        ),
                    ),
                    (),
                    None,
                    inputs,
                )
        previous = self.states[-1]
        steps = previous.steps
        if record_step:
            steps = steps + (
                AppliedStep(
                    stmt.label,
                    proposal.operator,
                    first,
                    second,
                    proposal.regime,
                    proposal.source,
                    licensed,
                ),
            )
        new_state = State(
            previous.index + 1,
            previous.judgments,
            steps,
            previous.log + ((stmt.label, word),),
        )
        self._push_state(new_state)
        self._record(
            OperationResult(
                stmt.label,
                "apply",
                outcome,
                word,
                f"apply {stmt.proposal} ({proposal.operator}: {first} -> {second}): {word}",
                (),
                explanation,
                new_state.index,
            )
        )

    @staticmethod
    def _limitation(
        label: str, cause: LimitationCause, summary: str, inputs: tuple[str, ...]
    ) -> Explanation:
        """Build a limitation explanation."""
        return Explanation(
            label, ExplanationKind.LIMITATION, summary, (), (), cause, inputs
        )

    # ------------------------------------------------------------------
    # check
    # ------------------------------------------------------------------

    def run_check(self, stmt: Check) -> None:
        """Evaluate one obligation."""
        if stmt.kind == "faithful":
            self._check_faithful(stmt)
        elif stmt.kind == "collisions":
            self._check_collisions(stmt)
        elif stmt.kind == "consistent":
            self._check_consistent(stmt)
        elif stmt.kind == "coverage":
            self._check_coverage(stmt)
        else:
            self._check_status(stmt)

    def _surface_values(self, surface: SurfaceDecl) -> tuple[str, ...]:
        """Return the observed value of every item of the surface's carrier."""
        return self._column_values(surface.carrier, surface.column, surface.line)

    def _unwarranted(self, regime: RegimeDecl, relation: Relation) -> str:
        """Return the reasons a check cannot be warranted, or empty string."""
        reasons: list[str] = []
        if not regime.source:
            reasons.append(f"regime {regime.name} names no source")
        if not relation.consistent():
            reasons.append("the commitments are inconsistent")
        return "; ".join(reasons)

    def _check_faithful(self, stmt: Check) -> None:
        """Check that the surface never separates items the regime relates."""
        regime = self.regimes[stmt.subject]
        surface = self.surfaces[stmt.object]
        relation = self.relation(regime.name)
        values = self._surface_values(surface)
        items = relation.items
        first_position: dict[int, int] = {}
        divergent_classes: dict[int, int] = {}
        divergent_items = 0
        related_classes: set[int] = set()
        for position, item in enumerate(items):
            class_number = relation.class_of(item)
            if class_number not in first_position:
                first_position[class_number] = position
                continue
            related_classes.add(class_number)
            anchor = first_position[class_number]
            if values[position] != values[anchor]:
                divergent_items += 1
                if class_number not in divergent_classes:
                    divergent_classes[class_number] = position
        reasons = self._unwarranted(regime, relation)
        inputs = tuple(
            name
            for name in (regime.name, surface.name, regime.source, surface.source)
            if name
        )
        counts = _counts(
            divergent_classes=len(divergent_classes),
            divergent_items=divergent_items,
            items=len(items),
            related_classes=len(related_classes),
        )
        witness_name = "divergence" if surface.role == "surface" else "incoherence"
        if divergent_classes:
            examples = sorted(divergent_classes.items())[:MAX_EXAMPLES]
            fields: dict[str, str] = {"kind": witness_name}
            chains: list[tuple[DerivationStep, ...]] = []
            for number, (class_number, position) in enumerate(examples, start=1):
                anchor = first_position[class_number]
                tag = f"example_{number:02d}"
                fields[f"{tag}.first"] = items[anchor]
                fields[f"{tag}.first_value"] = values[anchor]
                fields[f"{tag}.second"] = items[position]
                fields[f"{tag}.second_value"] = values[position]
                chains.append(relation.path(items[anchor], items[position]))
            omitted = len(divergent_classes) - len(examples)
            explanation = Explanation(
                stmt.label,
                ExplanationKind.WITNESS,
                f"{surface.name} gives different values to items that {regime.name} relates "
                f"({len(divergent_classes)} related classes affected).",
                tuple(chains),
                tuple(sorted(fields.items())),
                None,
                inputs,
                omitted,
            )
            if reasons:
                outcome, word = Outcome.UNDETERMINED, "unwarranted"
                explanation = self._limitation(
                    stmt.label,
                    LimitationCause.INSUFFICIENT_INFORMATION,
                    f"A {witness_name} was computed but the check is not warranted: {reasons}.",
                    inputs,
                )
            else:
                outcome, word = Outcome.REFUTED, "violated"
        elif reasons:
            outcome, word = Outcome.UNDETERMINED, "unwarranted"
            explanation = self._limitation(
                stmt.label,
                LimitationCause.INSUFFICIENT_INFORMATION,
                f"No {witness_name} was found but the check is not warranted: {reasons}.",
                inputs,
            )
        else:
            outcome, word = Outcome.ESTABLISHED, "satisfied"
            explanation = Explanation(
                stmt.label,
                ExplanationKind.DERIVATION,
                f"Every class related by {regime.name} has one value under {surface.name}.",
                (),
                (),
                None,
                inputs,
            )
        self._record(
            OperationResult(
                stmt.label,
                "check",
                outcome,
                word,
                f"faithful {regime.name} against {surface.name}: {word}",
                counts,
                explanation,
                self.states[-1].index,
            )
        )

    def _check_collisions(self, stmt: Check) -> None:
        """Check which merges a surface makes that the regime does not require."""
        surface = self.surfaces[stmt.subject]
        regime = self.regimes[stmt.object]
        relation = self.relation(regime.name)
        values = self._surface_values(surface)
        items = relation.items
        groups: dict[str, list[int]] = {}
        for position, value in enumerate(values):
            groups.setdefault(value, []).append(position)
        merging_groups = 0
        pure_groups = 0
        cross_groups: list[tuple[str, list[int], list[int]]] = []
        for value, positions in groups.items():
            if len(positions) < 2:
                continue
            merging_groups += 1
            class_numbers = sorted(
                {relation.class_of(items[position]) for position in positions}
            )
            if len(class_numbers) == 1:
                pure_groups += 1
            else:
                cross_groups.append((value, positions, class_numbers))
        cross_groups.sort(key=lambda entry: entry[1][0])
        cross_pairs = 0
        forbidden_pairs: set[tuple[int, int]] = set()
        for _value, _positions, class_numbers in cross_groups:
            size = len(class_numbers)
            cross_pairs += size * (size - 1) // 2
            member_set = set(class_numbers)
            for pair in relation.distinct_pairs:
                class_u = relation.class_of(pair.first)
                class_v = relation.class_of(pair.second)
                if (
                    class_u != class_v
                    and class_u in member_set
                    and class_v in member_set
                ):
                    forbidden_pairs.add((min(class_u, class_v), max(class_u, class_v)))
        unsupported_pairs = cross_pairs - len(forbidden_pairs)
        reasons = self._unwarranted(regime, relation)
        inputs = tuple(
            name
            for name in (surface.name, regime.name, surface.source, regime.source)
            if name
        )
        counts = _counts(
            cross_class_groups=len(cross_groups),
            cross_class_pairs=cross_pairs,
            forbidden_class_pairs=len(forbidden_pairs),
            merging_groups=merging_groups,
            required_groups=pure_groups,
            surface_values=len(groups),
            unsupported_class_pairs=unsupported_pairs,
        )
        fields: dict[str, str] = {}
        for number, (value, positions, class_numbers) in enumerate(
            cross_groups[:MAX_EXAMPLES], start=1
        ):
            tag = f"example_{number:02d}"
            by_class: dict[int, int] = {}
            for position in positions:
                by_class.setdefault(relation.class_of(items[position]), position)
            first_class, second_class = class_numbers[0], class_numbers[1]
            first_item = items[by_class[first_class]]
            second_item = items[by_class[second_class]]
            fields[f"{tag}.surface_value"] = value
            fields[f"{tag}.criterion_classes"] = str(len(class_numbers))
            fields[f"{tag}.first"] = first_item
            fields[f"{tag}.second"] = second_item
            if relation.keys is not None:
                fields[f"{tag}.first_key"] = relation.keys[relation.index[first_item]]
                fields[f"{tag}.second_key"] = relation.keys[relation.index[second_item]]
        omitted = max(0, len(cross_groups) - MAX_EXAMPLES)
        if reasons:
            outcome, word = Outcome.UNDETERMINED, "unwarranted"
            explanation = self._limitation(
                stmt.label,
                LimitationCause.INSUFFICIENT_INFORMATION,
                f"Collisions were computed but the check is not warranted: {reasons}.",
                inputs,
            )
        elif forbidden_pairs:
            outcome, word = Outcome.REFUTED, "contradicted"
            explanation = Explanation(
                stmt.label,
                ExplanationKind.WITNESS,
                f"{surface.name} merges items across {len(forbidden_pairs)} class pairs that "
                f"{regime.name} judgments assert distinct.",
                (),
                tuple(sorted(fields.items())),
                None,
                inputs,
                omitted,
            )
        elif cross_groups:
            outcome, word = Outcome.UNDETERMINED, "unsupported"
            explanation = Explanation(
                stmt.label,
                ExplanationKind.LIMITATION,
                f"{surface.name} merges items across {unsupported_pairs} class pairs that "
                f"{regime.name} neither requires nor forbids. The criterion is silent; the "
                "merges are commitments of the surface that the criterion does not support.",
                (),
                tuple(sorted(fields.items())),
                LimitationCause.INSUFFICIENT_INFORMATION,
                inputs,
                omitted,
            )
        else:
            outcome, word = Outcome.ESTABLISHED, "supported"
            explanation = Explanation(
                stmt.label,
                ExplanationKind.DERIVATION,
                f"Every merge made by {surface.name} lies inside one class of {regime.name}.",
                (),
                (),
                None,
                inputs,
            )
        self._record(
            OperationResult(
                stmt.label,
                "check",
                outcome,
                word,
                f"collisions {surface.name} against {regime.name}: {word}",
                counts,
                explanation,
                self.states[-1].index,
            )
        )

    def _check_consistent(self, stmt: Check) -> None:
        """Check that no distinct judgment lies inside a same-class."""
        regime = self.regimes[stmt.subject]
        relation = self.relation(regime.name)
        inputs = tuple(name for name in (regime.name, regime.source) if name)
        conflicts = relation.conflicts()
        counts = _counts(
            conflicts=len(conflicts),
            distinct_judgments=len(relation.distinct_pairs),
            same_judgments=len(relation.same_pairs),
        )
        if conflicts:
            outcome, word = Outcome.REFUTED, "inconsistent"
            explanation = self._conflict_explanation(
                stmt.label, relation, conflicts[0], inputs
            )
        else:
            outcome, word = Outcome.ESTABLISHED, "consistent"
            vacuous = not relation.distinct_pairs
            explanation = Explanation(
                stmt.label,
                ExplanationKind.DERIVATION,
                "No distinct judgment lies inside a same-class."
                + (
                    " There are no distinct judgments, so consistency is vacuous."
                    if vacuous
                    else ""
                ),
                (),
                (),
                None,
                inputs,
            )
        self._record(
            OperationResult(
                stmt.label,
                "check",
                outcome,
                word,
                f"consistent {regime.name}: {word}",
                counts,
                explanation,
                self.states[-1].index,
            )
        )

    def _check_coverage(self, stmt: Check) -> None:
        """Check that the regime places every item in some class with another item or key."""
        regime = self.regimes[stmt.subject]
        relation = self.relation(regime.name)
        mentioned: set[str] = set()
        for pair in relation.same_pairs:
            mentioned.add(pair.first)
            mentioned.add(pair.second)
        silent = [
            item
            for item in relation.items
            if not relation.has_key(item) and item not in mentioned
        ]
        inputs = tuple(name for name in (regime.name, regime.source) if name)
        counts = _counts(items=len(relation.items), silent_items=len(silent))
        if silent:
            outcome, word = Outcome.UNDETERMINED, "partial"
            fields = {
                f"silent_{number:02d}": item
                for number, item in enumerate(silent[:MAX_EXAMPLES], start=1)
            }
            explanation = Explanation(
                stmt.label,
                ExplanationKind.LIMITATION,
                f"{regime.name} says nothing about {len(silent)} items: they have no key value "
                "and appear in no same-commitment. They stay unanchored; they are not declared distinct.",
                (),
                tuple(sorted(fields.items())),
                LimitationCause.INSUFFICIENT_INFORMATION,
                inputs,
                max(0, len(silent) - MAX_EXAMPLES),
            )
        else:
            outcome, word = Outcome.ESTABLISHED, "complete"
            explanation = Explanation(
                stmt.label,
                ExplanationKind.DERIVATION,
                f"{regime.name} places every item in a class.",
                (),
                (),
                None,
                inputs,
            )
        self._record(
            OperationResult(
                stmt.label,
                "check",
                outcome,
                word,
                f"coverage {regime.name}: {word}",
                counts,
                explanation,
                self.states[-1].index,
            )
        )

    def _check_status(self, stmt: Check) -> None:
        """Report whether a pair is required, forbidden, or undetermined."""
        regime = self.regimes[stmt.subject]
        self._need_items(regime.carrier, (stmt.first, stmt.second), stmt.line)
        relation = self.relation(regime.name)
        inputs = tuple(name for name in (regime.name, regime.source) if name)
        status = relation.status(stmt.first, stmt.second)
        if status == "inconsistent":
            outcome, word = Outcome.UNDETERMINED, "inconsistent"
            explanation = self._conflict_explanation(
                stmt.label, relation, relation.conflicts()[0], inputs
            )
        elif status == "required":
            outcome, word = Outcome.ESTABLISHED, "required"
            explanation = Explanation(
                stmt.label,
                ExplanationKind.DERIVATION,
                f"{stmt.first} and {stmt.second} are joined by a chain of same-commitments.",
                (relation.path(stmt.first, stmt.second),),
                (),
                None,
                inputs,
            )
        elif status == "forbidden":
            forbidding = relation.forbidden_by(stmt.first, stmt.second)
            if forbidding is None:
                raise RunError("internal: forbidden status without a forbidding pair")
            outcome, word = Outcome.REFUTED, "forbidden"
            explanation = self._forbidden_explanation(
                stmt.label, relation, stmt.first, stmt.second, forbidding, inputs
            )
        else:
            outcome, word = Outcome.UNDETERMINED, "undetermined"
            explanation = self._limitation(
                stmt.label,
                LimitationCause.INSUFFICIENT_INFORMATION,
                f"Some admissible identity relation identifies {stmt.first} and {stmt.second} "
                "and some separates them. Not required is not the same as distinct.",
                inputs,
            )
        self._record(
            OperationResult(
                stmt.label,
                "check",
                outcome,
                word,
                f"status {stmt.first}, {stmt.second} under {regime.name}: {word}",
                (),
                explanation,
                self.states[-1].index,
            )
        )

    # ------------------------------------------------------------------
    # explain
    # ------------------------------------------------------------------

    def run_explain(self, stmt: Explain) -> None:
        """Return the explanation produced with a labeled operation."""
        target = self.labelled[stmt.target]
        explanation = target.explanation
        if explanation is None:
            explanation = Explanation(
                stmt.target,
                ExplanationKind.LIMITATION,
                "The operation produced no explanation.",
                (),
                (),
                LimitationCause.INSUFFICIENT_INFORMATION,
                (),
            )
        self.results.append(
            OperationResult(
                stmt.target,
                "explain",
                Outcome.ESTABLISHED,
                explanation.kind.value,
                explanation.summary,
                target.counts,
                explanation,
                self.states[-1].index,
            )
        )


def run_program(program: Program, base_dir: Path) -> Run:
    """Check and execute a program.

    Args:
        program: Parsed program.
        base_dir: Directory that source paths are relative to.

    Returns:
        The complete record of the run.

    Raises:
        RunError: If the program is ill formed, a source file is missing or
            altered, or an item or column does not exist.
    """
    diagnostics = check_program(program)
    if diagnostics:
        raise RunError("; ".join(str(diagnostic) for diagnostic in diagnostics))
    machine = _Machine(program, base_dir)
    for stmt in program.statements:
        if isinstance(stmt, SourceDecl):
            machine.declare_source(stmt)
        elif isinstance(stmt, CarrierDecl):
            machine.declare_carrier(stmt)
        elif isinstance(stmt, RegimeDecl):
            machine.declare_regime(stmt)
        elif isinstance(stmt, SurfaceDecl):
            machine.declare_surface(stmt)
        elif isinstance(stmt, OperatorDecl):
            machine.declare_operator(stmt)
        elif isinstance(stmt, Judge):
            machine.run_judge(stmt)
        elif isinstance(stmt, Propose):
            machine.run_propose(stmt)
        elif isinstance(stmt, Apply):
            machine.run_apply(stmt)
        elif isinstance(stmt, Check):
            machine.run_check(stmt)
        else:
            machine.run_explain(stmt)
    tables = tuple(
        (name, table.sha256, len(table.rows)) for name, table in machine.tables.items()
    )
    classes: list[tuple[str, tuple[tuple[str, ...], ...]]] = []
    for regime_name in machine.regimes:
        relation = machine.relation(regime_name)
        grouped: dict[int, list[str]] = {}
        for item in relation.items:
            grouped.setdefault(relation.class_of(item), []).append(item)
        classes.append(
            (
                regime_name,
                tuple(tuple(group) for _number, group in sorted(grouped.items())),
            )
        )
    return Run(
        program, tables, tuple(machine.results), tuple(machine.states), tuple(classes)
    )
