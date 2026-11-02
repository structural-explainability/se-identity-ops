# IdentityOps Specification

This document says what the IdentityOps language is for, what it contains, and what it
leaves out. [SEMANTICS.md](./SEMANTICS.md) says exactly what each construct means.
[docs/en/prior-art.md](./docs/en/prior-art.md) says how it relates to existing work.

## Status

IdentityOps is a research experiment, not a product and not a claim of novelty.

The question under test is whether one small language can specify, execute, and
audit identity-relevant operations under declared criteria in three different
settings, and where it fails. Version 0.1.0 is acceptable only as an honest
record of that test. See [Acceptance](#acceptance).

Sections marked **Proposed** were designed before the experiments and may be
revised by their results. Sections marked **Implemented** are in the reference
interpreter and are exercised by tests.

## What IdentityOps Is

IdentityOps is a language for **specifying, executing, and auditing
identity-relevant operations under declared criteria**.

- *Specifying*: declaring a criterion of identity, an implementation behavior
  that is claimed to respect it, and the evidence that grounds each.
- *Executing*: running judgments and proposed transformations against a model
  state, with explicit outcomes and immutable snapshots.
- *Auditing*: comparing declared commitments with observed treatment, and
  returning a derivation, a witness, or an explicit limitation.

## What IdentityOps Is Not

- It is not an entity-resolution or merge engine. It has no similarity function, no
  soft rules, no optimality criteria, and no search for a best set of merges.
  [LACE, LACE+, and ASPEN+](./docs/en/prior-art.md) already provide declarative
  merge rules, denial constraints, dynamic merge semantics, justifications,
  alternative resolutions, and local and global merges. IdentityOps does not
  reimplement them and does not claim them.
- It is not a decision procedure for what things really are. It reports
  commitments, differences between commitments, and the consequences of
  commitments. It does not certify ground truth and does not say which regime
  is correct.
- It is not a new foundational theory. The commitment calculus is
  [`se-theory-persistence`](https://github.com/structural-explainability/se-theory-persistence).
  The comparison of a declared relation with implementation treatment is
  [`se-theory-operational-identity`](https://github.com/structural-explainability/se-theory-operational-identity).
  IdentityOps is a language and interpreter over those ideas.

## Research Targets

Three targets define what the experiments must exercise. A construct that serves
none of them does not belong in version 0.1.0.

1. **Operational identity.** Identify the commitments induced by existing
   implementation behavior, and compare them with a declared criterion.
   Experiment A (Chicago vendor records).
2. **Representation preservation.** Evaluate the identity-relevant consequences
   of a transformation between two representations. Experiment B (SBOM and PURL).
3. **Persistence.** Characterize identity continuation, breakage, and uncertainty
   across state transitions, including forks and merges. Experiment C.

## Commitments

Three commitments hold for every construct. Each is tested.

1. **No forced identity.** Two records are not the same because their identifiers
   or normalized values match. A shared value is evidence that a declared
   criterion may use; it is never the criterion itself.
2. **No silent changes.** Every identity-relevant operation has an explicit
   criterion, scope, and traceable result. State changes only through `judge` and
   `apply`, and every state is kept as a snapshot.
3. **No invented certainty.** Unknown, conflicting, or insufficiently supported
   judgments stay visible. Not required is not distinct. A missing source makes a
   check unwarranted. A contradiction is recorded and reported, never resolved
   by dropping one side.

## Language

### Declarations (Implemented)

Declarations say what is being discussed. They do not change state.

- **source**: a data file, its SHA-256, and a note. Every observation and criterion
  traces to a source. A digest mismatch stops the run.
- **carrier**: the items under discussion, loaded from a source column or listed
  inline. Items are records. There is no referent type.
- **regime**: a declared identity criterion over a carrier. Two kinds:
  - `by "column"` relates items with the same non-empty value in that column.
    An empty value places an item in no class: the criterion is silent about it.
  - `explicit` relates items only through `judge` and `apply`.
- **surface**: an observed implementation mechanism over a carrier, read from one
  source column. Two items are treated the same when the surface gives them the
  same value.
- **probe**: a read-only observation of implementation output over a carrier, read
  from one source column.
- **operator**: how a regime classifies a transformation operator: `prs`
  (preserving), `brk` (breaking), `ign` (ignoring), or `na` (inapplicable).

### Operations (Implemented)

The five operations are retained because each is used by at least one experiment.
Nothing is included for completeness.

- **judge**: record a same or distinct judgment under a regime, with a source and
  a scope. A judgment is evidence, not ground truth. It is recorded even when it
  contradicts earlier judgments, and the contradiction is reported.
  Used by: all three targets.
- **propose**: construct a transformation step without changing state.
  Used by: persistence.
- **apply**: execute a proposed step against the **model state**. Licensed only
  when the operator is classified preserving and no recorded distinction forbids
  it. `apply` changes a model of declared commitments. It does **not** resolve a
  real-world referent and does not imply authority to do so.
  Used by: persistence.
- **check**: evaluate an obligation. Five kinds:
  - `faithful R against S`: the surface or probe never separates items that the
    regime relates.
  - `collisions S against R`: which merges the surface makes that the regime does
    not require.
  - `consistent R`: no distinct judgment lies inside a same-class.
  - `status X Y under R`: required, forbidden, or undetermined.
  - `coverage R`: every item is placed in some class.
  Used by: all three targets.
- **explain**: return the deterministic explanation produced with an operation: a
  derivation, a witness, or an explicit limitation.
  Used by: all three targets.

### Grammar (Implemented)

Every statement starts in column one. Indented lines continue the statement. `#`
starts a comment outside quotes. Words are names or item names; quoted text is a
string.

```text
source NAME file "PATH" sha256 "HEX" [note "TEXT"]
carrier NAME from SOURCE key "COLUMN"
carrier NAME items ITEM ITEM ...
regime NAME on CARRIER by "COLUMN" [source SOURCE] [meaning "TEXT"]
regime NAME on CARRIER explicit [source SOURCE] [meaning "TEXT"]
surface NAME on CARRIER column "COLUMN" source SOURCE
probe NAME on CARRIER column "COLUMN" source SOURCE
operator NAME classified prs|brk|ign|na under REGIME
judge LABEL same|distinct ITEM ITEM under REGIME [from SOURCE] [scope "TEXT"]
propose LABEL OPERATOR ITEM -> ITEM under REGIME [from SOURCE]
apply LABEL PROPOSAL
check LABEL faithful REGIME against SURFACE_OR_PROBE
check LABEL collisions SURFACE against REGIME
check LABEL consistent REGIME
check LABEL coverage REGIME
check LABEL status ITEM ITEM under REGIME
explain LABEL
```

## Distinctions

The language is meant to keep apart the things that identity-resolution systems
tend to run together. For each, this section says how the distinction is kept in
version 0.1.0 and whether the language enforces it or only follows a convention.

- **Records and referents.** Enforced by absence: only records exist. No
  construct turns a record match into a referent claim. Whether a criterion
  identifies referents is outside the language and is recorded as a doubt.
- **Presentations and the things presented.** Convention only. A presentation is
  an item (an SBOM component in one format). The language has no type for the
  thing presented. A regime may relate presentations that are claimed to present
  the same thing.
- **Stages and persistent objects.** Convention only. A stage is an item. A
  persistent object is a class of the regime's generated relation. It is not a
  first-class construct.
- **Declared identity and observed treatment.** Enforced: `regime` and
  `surface` or `probe` are different declarations and `check` takes one of each.
- **Evidence and conclusions.** Partly enforced: `judge` records a source and a
  scope, and a regime or check with no source is unwarranted. Whether the source
  supports the judgment is not checked.
- **Identity and lineage.** Enforced: a step of an identity-ignoring operator is
  recorded in the step log and joins no pair. Common ancestry alone gives no
  identity.
- **Unknown and false.** Enforced: a pair that is neither required nor forbidden
  is undetermined. Only a recorded distinct judgment forbids anything.
- **A failed obligation and a violated obligation.** Enforced:
  - *violated* means the obligation was evaluated, and a witness shows it fails
    (outcome `refuted`);
  - *failed* means the obligation could not be discharged because its inputs do
    not warrant a verdict (outcome `undetermined`, with a limitation cause).
  A failed obligation is not evidence of a violation.

## Results

Every operation reports one of three outcomes (Implemented).

- **established**: the property holds or the step is licensed.
- **refuted**: the property fails with a witness, or the step is blocked.
- **undetermined**: the declared inputs do not settle the question.

Each result also carries an operation-specific word (for example `licensed`,
`blocked`, `violated`, `unsupported`, `unwarranted`) and counts. When a result is
`undetermined`, its explanation names a limitation cause from a closed set:
`insufficient_information`, `inapplicability`, `operator_underdetermination`.
SE also distinguishes semantic disagreement; no experiment reaches it in
version 0.1.0, so it is not implemented (see [DECISIONS.md](./DECISIONS.md)).

## Experiments

Each experiment records, before it runs: a research question, input provenance,
declared criteria, positive controls, negative controls, an indeterminate case,
and expected results. Expected results are committed before the first run on the
real data. A disagreement that is typed into a program is a unit test, not a
discovery.

- **A. Chicago vendor identity** (operational identity). Compares the
  criterion "same published Vendor ID" (a source-provided identifier whose referential
  meaning has not yet been independently established) with the existing US-IL
  localization step. See [examples/chicago](./examples/chicago/README.md).
- **B. SBOM and PURL** (representation preservation). Reads the two
  authorized Freeze 01 validation cases. These are engineering validation, not
  evidence of generalization. See [examples/sbom](./examples/sbom/README.md).
- **C. Persistence.** No adequate state-history dataset was found in the
  inspected repositories, so only synthetic interpreter controls were run. They
  do not test whether the language handles real persistence data. See
  [examples/persistence](./examples/persistence/LIMITATION.md).
- **D. Substituting the authority** (domain neutrality). Runs one program over the
  outputs of three independently developed Package URL implementations and reports where
  their identity commitments and validity decisions differ. Exploratory, on a synthetic
  corpus. See [examples/purl_authorities](./examples/purl_authorities/README.md).

## Novelty

No claim of novelty is made. A capability is called different from LACE, LACE+,
or ASPEN+ only where a specific difference was demonstrated by comparison, and
even then the difference may be one of vocabulary or cost rather than of
expressive power. See [docs/en/prior-art.md](./docs/en/prior-art.md).

## Three Kinds of Evidence

Documentation distinguishes these and states what exists and what does not.

1. **Mathematical correctness.** The Lean files state the intended meaning and
   prove properties of it. The Python interpreter is checked against that
   meaning by tests and an exhaustive small-state comparison, not by proof.
2. **Scientific adequacy.** Whether the criteria and mechanisms modeled in the
   experiments are the right ones is not established. See
   [DOUBTS.md](./DOUBTS.md).
3. **Theoretical contribution.** Not established. Successful execution does not
   show novelty.

## Acceptance

Version 0.1.0 is acceptable only when all of these hold; otherwise it is
reported as partial.

- The declarations and five operations have explicit semantics.
- The parser and interpreter execute real programs.
- The three contexts have been attempted.
- Available controls have expected and actual outcomes.
- Unknown and contradictory evidence remain visible.
- At least one meaningful Lean property is proved.
- Independent checks are reproducible.
- A prior-art comparison is documented.
- Unresolved questions are recorded and not presented as successes.

Whether each condition holds is stated in [README.md](./README.md).
