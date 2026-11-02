# Decisions

Design decisions, rejected designs, and failures during construction. Entries are
added; they are not rewritten.

## Decisions

### D-001. A standalone repository

IdentityOps lives in its own repository with its own language, semantics, interpreter,
tests, documentation, and Lean files. Reason: a language that is tested on three
domains should not be mistaken for a part of any one of them, and one-way layering over
the SE theory repositories keeps those unchanged.

### D-002. Five operations, kept where each is used

`judge`, `propose`, `apply`, `check`, `explain`. Each is used by at least one experiment.
`apply` is restricted to a model state and carries no authority over referents.
`propose` exists only so that `apply` can be gated and inspected before it runs.

### D-003. Declarations are separate from operations

`source`, `carrier`, `regime`, `surface`, `probe`, and `operator` bind names and never
change state. This replaces the first proposal's seven mixed constructs.

### D-004. Reuse Persistence, adapt Operational Identity

Persistence is imported (pinned release) for the commitment calculus. Operational
Identity is not imported because it has no release tag to pin; its `Faithful` is restated
with a docstring that says so. Neutral Substrate, Individuation, and Coreference are not
needed and are not imported.

### D-005. A key regime relates equal non-empty values only

An empty key places the item in no class. The criterion is silent about it; it is not
related to other empty-key items and not declared distinct.

### D-006. Nothing is distinct by default

Only a recorded `distinct` judgment forbids anything. Different keys are undetermined.

### D-007. Judgments are always recorded

A contradicting judgment is kept, marked conflicting, and makes the state inconsistent.
The interpreter does not choose a side.

### D-008. Every `apply` makes a snapshot

Including blocked and inapplicable ones, so the log records the attempt.

### D-009. Three limitation causes

Insufficient information, inapplicability, operator underdetermination. SE also
distinguishes semantic disagreement. No experiment reaches it, so it is not
implemented rather than defined and unused.

### D-010. A verdict needs a grounded regime

A `check` whose regime names no source returns `unwarranted`. A verdict from an ungrounded
criterion is not reported as a result.

### D-011. Expected results are committed first

For each experiment, `expected.toml` is committed before the results file, and a test
checks the order in git history.

### D-012. No `vcgen` in 0.1.0

`vcgen` is experimental in the Lean toolchain used, and its syntax has moved between
modules within months. The semantics is a pure function on a state, so properties are
proved directly.

#### How a weakest-precondition reading could support it later

Write `run` as a monadic program over `StateM (State C T)`, with one action per command.
Give each command a weakest-precondition specification as a `@[spec]` lemma (the
existing `step_propose`, `same_step_cases`, and `step_preserves_consistency` have the right
shape). State a postcondition such as `Consistent` and let `vcgen` generate the
verification conditions for a straight-line program, discharging them with the Persistence
lemmas. For a program with no `judge`, the generated condition is
`run_preserves_consistency`. This would prove properties of programs written in the monad
rather than of the Python interpreter.

## Rejected Designs

### R-001. The first seven-construct proposal

`carrier`, `regime`, `commit`, `observe`, `transition`, `audit`, `explain`. It dropped
`apply` (nothing executed or licensed a transition), mixed declarations with operations,
and used `surface` and `probe` in its examples without defining them.

### R-002. Programs that state their own disagreement

The first sketches asserted a "distinct" judgment and then observed equal normalized
names, so the expected witness was built into the input. Such a program is an interpreter
test. It is not evidence that the language found anything.

### R-003. A general merge engine

Soft rules, similarity, optimality, and local merges are LACE+ and ASPEN+ capabilities.
Re-implementing them as a contribution was rejected.

### R-004. Distinct by default for different keys

Rejected: it would invent certainty. See D-006.

### R-005. Chicago vendor names as the persistence dataset

Rejected for now: contract dates are not vendor-state dates. See
[examples/persistence/LIMITATION.md](./examples/persistence/LIMITATION.md).

### R-006. Pinning the pilot's recorded target digests

Rejected: they do not match the files. See UM-003.

## Failures During Construction

- The upstream `out/us_il_normalized_sample.csv` was first used as an oracle for the
  harness. It is a reviewed sheet with unaligned columns, so a row comparison failed
  (558 of 654 rows differed). The multiset comparison replaced it.
- A first test of empty-key behavior asserted a result its own program did not produce.
  The test was wrong and was rewritten.
- The first LACE class-pair count halved the number of atoms by mistake and disagreed
  with the interpreter. The count of ground atoms was first read before grounding and
  was zero. Both were fixed.
- A test expected three inexpressible persistence steps; there are four.
- `lake env lean` cannot resolve `SE.*` modules across packages because several packages
  share the `SE` root, and `leanchecker` cannot either. As in the other SE theory
  repositories, the axiom check falls back to a source scan, and axioms were
  printed with `lake lean`.
