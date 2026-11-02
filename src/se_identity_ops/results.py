"""results.py - Result and explanation types.

WHAT: The closed sets of outcomes and limitation causes, and the records the
      interpreter returns for each operation.
WHY: Every operation reports one explicit outcome. Unknown is never reported as
     false, and a failed obligation is kept apart from a violated one.
OBS: Outcome is shared by all operations; each operation's reading is given in
     SEMANTICS.md. `label` carries the operation-specific word.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class Outcome(StrEnum):
    """The three outcomes every operation reports.

    ESTABLISHED: the property holds, or the transformation is licensed.
    REFUTED: the property fails with a witness, or the transformation is blocked.
    UNDETERMINED: the declared inputs do not settle the question.
    """

    ESTABLISHED = "established"
    REFUTED = "refuted"
    UNDETERMINED = "undetermined"


class LimitationCause(StrEnum):
    """Why an operation could not settle a question.

    INSUFFICIENT_INFORMATION: no evidence, source, or declared criterion settles it.
    INAPPLICABILITY: the operator or criterion does not apply to the case.
    OPERATOR_UNDERDETERMINATION: the operator is classified identity-ignoring, so
        the classification alone neither licenses nor breaks continuation.
    """

    INSUFFICIENT_INFORMATION = "insufficient_information"
    INAPPLICABILITY = "inapplicability"
    OPERATOR_UNDERDETERMINATION = "operator_underdetermination"


class ExplanationKind(StrEnum):
    """The three kinds of explanation."""

    DERIVATION = "derivation"
    WITNESS = "witness"
    LIMITATION = "limitation"


@dataclass(frozen=True, slots=True)
class DerivationStep:
    """One link of a derivation chain.

    Attributes:
        first: Item at one end of the link.
        second: Item at the other end of the link.
        ground: "key" for a shared criterion value, "judgment" for a recorded
            same-judgment, or "step" for a licensed transformation.
        detail: Column and value, or the label of the judgment or step.
        source: Source name that grounds the link, or empty string.
    """

    first: str
    second: str
    ground: str
    detail: str
    source: str


@dataclass(frozen=True, slots=True)
class Explanation:
    """A deterministic, inspectable explanation of one operation.

    Attributes:
        subject: Label of the explained operation.
        kind: DERIVATION, WITNESS, or LIMITATION.
        summary: One-sentence description.
        steps: Derivation chains, one tuple per chain, when `kind` is DERIVATION
            or when a witness carries supporting chains.
        witness: Name/value pairs describing the witness, sorted by name.
        limitation: The limitation cause, or None.
        inputs: Names of the declarations and sources the explanation used.
        omitted: Count of further witnesses not listed.
    """

    subject: str
    kind: ExplanationKind
    summary: str
    steps: tuple[tuple[DerivationStep, ...], ...] = ()
    witness: tuple[tuple[str, str], ...] = ()
    limitation: LimitationCause | None = None
    inputs: tuple[str, ...] = ()
    omitted: int = 0


@dataclass(frozen=True, slots=True)
class OperationResult:
    """The result of one operation.

    Attributes:
        label: Operation label.
        operation: "judge", "propose", "apply", "check", or "explain".
        outcome: ESTABLISHED, REFUTED, or UNDETERMINED. Operations that do not
            judge anything (propose, explain) report ESTABLISHED when they succeed.
        word: Operation-specific word, for example "licensed" or "violated".
        detail: One-sentence description.
        counts: Name/value pairs of numbers, sorted by name.
        explanation: Explanation produced with the result, or None.
        snapshot: Index of the state snapshot after the operation.
    """

    label: str
    operation: str
    outcome: Outcome
    word: str
    detail: str
    counts: tuple[tuple[str, int], ...] = ()
    explanation: Explanation | None = None
    snapshot: int = 0


@dataclass(frozen=True, slots=True)
class Judgment:
    """A recorded same or distinct judgment.

    Attributes:
        label: Label of the recording operation.
        polarity: "same" or "distinct".
        first: First item.
        second: Second item.
        regime: Regime name.
        source: Source name, or empty string.
        scope: Scope text.
        conflicting: Whether recording it contradicted the commitments before it.
    """

    label: str
    polarity: str
    first: str
    second: str
    regime: str
    source: str
    scope: str
    conflicting: bool


@dataclass(frozen=True, slots=True)
class AppliedStep:
    """A transformation step recorded in the model state.

    Attributes:
        label: Label of the apply operation.
        operator: Operator name.
        first: Item before the step.
        second: Item after the step.
        regime: Regime name.
        source: Source name, or empty string.
        licensed: Whether the step was added to the same-commitments.
    """

    label: str
    operator: str
    first: str
    second: str
    regime: str
    source: str
    licensed: bool


@dataclass(frozen=True, slots=True)
class State:
    """One immutable snapshot of the model state.

    The state holds judgments and applied steps. It is a model of declared
    commitments. It is not a claim about real-world referents.

    Attributes:
        index: Snapshot number; the initial state is 0.
        judgments: Judgments in recording order.
        steps: Applied steps in application order.
        log: Pairs of (label, outcome word) in operation order.
    """

    index: int
    judgments: tuple[Judgment, ...] = ()
    steps: tuple[AppliedStep, ...] = ()
    log: tuple[tuple[str, str], ...] = field(default=())
