"""se_identity_ops - IdentityOps v0.1.0 reference interpreter.

WHAT: A small language for specifying, executing, and auditing identity-relevant
      operations under declared criteria, with a deterministic reference interpreter.
WHY: See SPEC.md. The package is an experiment; novelty is not claimed.
OBS: The Lean files in SE/IdentityOps/ state the intended meaning. This package
     is not verified by them; the correspondence is an explicit obligation.
"""

from .checker import Diagnostic, check_program
from .interpreter import Run, RunError, run_program
from .parser import ParseError, parse
from .results import (
    Explanation,
    ExplanationKind,
    LimitationCause,
    OperationResult,
    Outcome,
    State,
)

__all__ = [
    "Diagnostic",
    "Explanation",
    "ExplanationKind",
    "LimitationCause",
    "OperationResult",
    "Outcome",
    "ParseError",
    "Run",
    "RunError",
    "State",
    "check_program",
    "parse",
    "run_program",
]
