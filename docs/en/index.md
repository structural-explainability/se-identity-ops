# IdentityOps

> A declarative language for specifying, executing, and auditing
> identity-relevant operations under declared criteria.

IdentityOps provides a common language for expressing identity commitments,
examining their consequences, and comparing them with observed operational behavior.

The research investigates whether identity-relevant operations can be
represented consistently across domains while retaining the criteria,
evidence, and limitations that give those operations meaning.

Four experiments examine its behavior using
Chicago vendor records,
SBOM transformations,
synthetic persistence controls, and
alternative Package URL implementations.

## Research Motivation

Many information systems depend on judgments about whether records,
representations, or successive states refer to the same entity.

Those judgments influence data integration, record linkage,
software supply-chain analysis, and the interpretation of changes
over time.

Different systems may use different identifiers, normalization rules,
matching procedures, or assumptions about identity.
Consequently, the same records can be grouped differently,
even when each system operates according to its own declared rules.

A comparison of the resulting values or groups can identify differences.
A meaningful interpretation also requires the criteria under which
those differences matter.

For example, two vendor records may share a published identifier
while their names are represented differently.
A software component may retain its Package URL during conversion
but move that identifier to a different location.
Two Package URL implementations may normalize the same input
differently while inducing equivalent groupings.

These situations involve related questions about identity commitments,
but they do not necessarily share the same identity criterion.

IdentityOps provides a way to express those criteria and
evaluate their operational consequences within a common framework.

## IdentityOps Language

The language separates declared identity criteria from the
operational mechanisms and observations used to evaluate them.

An IdentityOps program specifies the records under examination,
the applicable identity criterion, the evidence supporting that
criterion, and the behavior to be evaluated.

The interpreter executes the program and produces explicit results,
including evidence of agreement, divergence, and indeterminacy.

### Declarations

Six declarations establish the interpretation of a program.

- `source` identifies evidence and records its SHA-256 digest.
- `carrier` identifies the records or items under examination.
- `regime` declares an identity criterion over a carrier.
- `surface` describes observed operational grouping behavior.
- `probe` provides observations used to evaluate an obligation.
- `operator` classifies a transformation with respect to identity preservation.

A regime may derive relationships from a specified source column
or use explicit judgments recorded during execution.

The distinction between evidence and identity is important.
Equal identifiers or normalized values may support a declared criterion,
but equality of those values does not independently establish
real-world identity.

### Operations

Five operations express and evaluate identity-relevant activity.

- `judge` records a same or distinct judgment under a declared regime.
- `propose` constructs a proposed transformation without changing model state.
- `apply` executes a licensed transformation against model state.
- `check` evaluates an obligation under the declared interpretation.
- `explain` provides the associated explanation, derivation, or witness.

The available checks examine faithfulness, collisions,
consistency, status, and coverage.

A faithfulness check can identify records related by a criterion
that an operational mechanism separates.

A collision check can identify records grouped by a mechanism
whose relationship is not required by the declared criterion.

These are different observations.
A grouping that the criterion does not require is not
automatically a violation of that criterion.

The language also distinguishes required, forbidden,
and undetermined relationships.
Unknown or contradictory evidence remains visible rather than
being silently resolved.

The complete language specification is available in
[SPEC.md](https://github.com/structural-explainability/se-identity-ops/blob/main/SPEC.md).

Formal definitions of the constructs and their execution semantics
are available in
[SEMANTICS.md](https://github.com/structural-explainability/se-identity-ops/blob/main/SEMANTICS.md).

## Theoretical Foundations

IdentityOps builds on Structural Explainability research
in persistence and operational identity.

### Persistence

The
[Persistence theory](https://github.com/structural-explainability/se-theory-persistence)
provides a commitment calculus for interpreting identity
relationships and their evolution.

Identity commitments constrain which relationships are
admissible under a declared interpretation.

The calculus distinguishes relationships that are required,
forbidden, or undetermined by the recorded commitments.

It also provides the foundation for evaluating continuation,
breakage, and the consequences of transformations.

### Operational Identity

[Operational Identity](https://github.com/structural-explainability/se-theory-operational-identity)
examines the relationship between declared identity criteria
and the identity treatment induced by operational mechanisms.

The distinction permits analysis of whether observed behavior
agrees with the relationships required by a declared criterion
or introduces additional identifications.

IdentityOps provides an executable language for expressing
and examining such commitments and comparisons.

### Related Research

Declarative approaches to identity and entity resolution
have substantial existing foundations.

The LACE framework, its LACE+ extension, and the ASPEN and ASPEN+ systems
provide related capabilities involving
merge rules, constraints, justifications, alternative resolutions,
and local or global merging behavior.

IdentityOps sits outside these systems.
LACE-style encodings of Experiments A, B, and C serve as a comparison.

The relationship between these approaches and IdentityOps
requires comparison of their respective semantics,
expressiveness, execution models, and evidence.

The research includes a
[related-work analysis](./related-work.md)
and a record of the
[LACE-style encodings](./lace-attempts.md).

## Experimental Method

The experiments evaluate whether the same language can express
and execute identity-relevant comparisons across different settings.

The experimental process separates design, prediction,
execution, and verification.

### Design and Evidence

Each experiment identifies the source material,
the applicable identity criterion, the operational behavior,
and the expected interpretation of the results.

Source references and content digests preserve the connection
between declared evidence and the data examined during execution.

The four experiments have distinct evidentiary roles.

- **Experiment A:** Exploratory evaluation of operational identity using real Chicago vendor records.
- **Experiment B:** Engineering validation of representation preservation using known SBOM conversion cases.
- **Experiment C:** Synthetic controls for persistence operations and interpreter semantics.
- **Experiment D:** Exploratory comparison of Package URL implementations using a deliberately constructed corpus.

These roles determine the scientific interpretation
supported by each experiment.

### Predictions and Execution

The experimental records include controls, predictions,
and relations among expected outcomes.

Each experiment's `expected.toml` was committed before
the corresponding results were recorded.

The interpreter then executed the declared programs
and produced JSON result files.

The original predictions are retained alongside the observed outcomes,
including predictions that were not met.

Experiment D also includes a separately identified post-hoc analysis
introduced after its initial execution.

### Independent Verification

The completed experiments include procedures for checking
the recorded results independently of the original execution.

The verification methods include byte-for-byte reproduction,
comparison with recorded expectations, independent recomputation,
and formal verification of selected mathematical properties.

The repository's Git history also provides evidence of the
temporal ordering between predictions and results.

The [repository README](https://github.com/structural-explainability/se-identity-ops)
documents the complete experimental sequence, execution commands,
preserved evidence, and procedures for additional reproduction.

## Experimental Findings

### Experiment A: Chicago Vendor Identity

The Chicago experiment examines how an existing US-IL
localization mechanism groups vendor records relative to
the declared criterion of equal published Vendor IDs.

The experiment uses 20,000 real records.

The localization mechanism separated records belonging
to two published Vendor ID classes.

One separation involved an ampersand and the word "and".
Another involved different vendor names recorded
under the same Vendor ID.

The mechanism also grouped records across different
Vendor IDs in 51 groups.

Those additional groupings are not required by the
declared criterion, but the criterion does not forbid them.

All ten recorded expectations were met,
and all seven recorded relations held.

Independent calculations using plain Python and SQLite
agreed with the recorded interpreter results.

The findings provide concrete examples of differences
between a declared identity criterion and operational grouping behavior.

[Experiment A: Design, predictions, and results](https://github.com/structural-explainability/se-identity-ops/blob/main/examples/chicago/README.md)

### Experiment B: SBOM and Package URL Preservation

The SBOM experiment examines the preservation of
Package URL information during conversion from SPDX to CycloneDX.

Source and target components are associated through
a declared SHA-256 content-hash criterion.

Two historical conversion cases are evaluated:
one known-bad conversion and one known-good conversion.

In the known-bad conversion, three hash-anchored components
lose their Package URLs from the canonical CycloneDX location.

The corresponding PURLs remain available elsewhere
in the target representation.

The known-good conversion preserves the canonical PURL
for all three anchored components.

All ten recorded expectations were met,
and both recorded relations held.

An independent comparison agreed with the original
SBOM pilot's recorded preservation verdicts.

The experiment demonstrates that IdentityOps can express
the relevant preservation distinctions in these known cases.

The evidence supports engineering validation of the language
against previously established conversion behavior.

[Experiment B: Design, predictions, and results](https://github.com/structural-explainability/se-identity-ops/blob/main/examples/sbom/README.md)

### Experiment C: Persistence

The persistence experiment evaluates identity-relevant
operations across successive model states.

The synthetic controls include rekeying,
preserving and breaking transformations,
forks, merges, recorded distinctions,
and operations that leave identity undetermined.

The controls examine whether transformations are licensed
and which identity commitments follow from their execution.

All fifteen recorded expectations were met.

The results demonstrate the interpreter's behavior
on explicitly constructed cases whose outcomes can
be derived from the declared semantics.

A suitable real state-history dataset was not established.
The experiment therefore provides synthetic verification
rather than an empirical persistence case study.

[Experiment C: Persistence limitation and controls](https://github.com/structural-explainability/se-identity-ops/blob/main/examples/persistence/LIMITATION.md)

### Experiment D: Package URL Authority Substitution

The fourth experiment examines whether different
Package URL implementations induce the same identity
commitments over a shared corpus.

Three independently developed implementations were evaluated:

- `packageurl-python` 0.17.6
- `packageurl-js` 2.0.1
- `packageurl-go` v0.1.7

The experiment contains 37 inputs arranged into
20 declared spelling sets.

The comparison separates the external normalization
implementations from the IdentityOps language used
to evaluate their results.

Python separated two of the twelve multi-spelling sets.
JavaScript and Go each separated one.

JavaScript and Go induced the same partition on the corpus,
while Python induced a finer partition.

The experiment also identified differences in accepted inputs
and serialized Package URL strings.

Of seventeen recorded expectation entries,
thirteen were met and four were not met.
Five of six recorded relations held.

The unmet predictions remain part of the experimental record.

The findings demonstrate that substituting an external
normalization implementation can change the observed
identity commitments without changing the language
used to examine them.

The corpus is synthetic and was selected to expose
potential differences among implementations.

[Experiment D: Design, predictions, and results](https://github.com/structural-explainability/se-identity-ops/blob/main/examples/purl_authorities/README.md)

## Formal Verification

A Lean 4 formalization provides mathematically checked
properties of the IdentityOps model.

The formalization builds on the Persistence commitment
calculus and establishes properties of program execution,
state changes, and recorded identity commitments.

The proved properties include:

- `propose`, `check`, and `explain` leave the model state unchanged.
- Same-commitments change only through the specified judgment or licensed preservation operations.
- Programs do not remove recorded commitments.
- Programs without `judge` preserve consistency.
- Identity status follows the admissible-relation interpretation of recorded commitments.
- The order of operations can affect the resulting commitments.

The formal checks use `propext`, `Classical.choice`,
and `Quot.sound`, with no `sorry`.

These are results about the Lean formal model.
Correspondence between that model and the Python interpreter
is a separate verification obligation addressed through tests.

The formal source and associated checks are available in
[SE/IdentityOps](https://github.com/structural-explainability/se-identity-ops/tree/main/SE/IdentityOps)
and
[SETest/IdentityOps](https://github.com/structural-explainability/se-identity-ops/tree/main/SETest/IdentityOps).

## Research Status and Open Questions

The four experiments have been completed and their
recorded evidence is preserved.

The current research status is **partial** under
the acceptance conditions in the language specification.

The Chicago and SBOM experiments exercise the language
using real records.

The persistence experiment establishes synthetic
interpreter behavior, but a suitable real state-history
dataset has not yet been evaluated.

The Package URL comparison identifies differences
among implementations on a constructed corpus.
Determining which implementation conforms to an
applicable external specification requires separate analysis.

The Chicago results depend on the declared Vendor ID criterion.
The referential meaning of Vendor ID has not been
independently established.

The Lean formalization and Python implementation
are supported by separate verification procedures.
Formal correspondence between them remains an obligation.

Independent human evaluation of the research design,
experimental interpretation, and relationship to related work
also remains important.

These questions are maintained in the research records:

- [DOUBTS.md](https://github.com/structural-explainability/se-identity-ops/blob/main/DOUBTS.md)
- [DECISIONS.md](https://github.com/structural-explainability/se-identity-ops/blob/main/DECISIONS.md)

## Research Resources

The research materials provide the definitions,
implementation, experimental evidence, and supporting analysis.

- [Specification](https://github.com/structural-explainability/se-identity-ops/blob/main/SPEC.md)
- [Formal Semantics](https://github.com/structural-explainability/se-identity-ops/blob/main/SEMANTICS.md)
- [Related Work](./related-work.md)
- [LACE Attempts](./lace-attempts.md)
- [Research Doubts](https://github.com/structural-explainability/se-identity-ops/blob/main/DOUBTS.md)
- [Research Decisions](https://github.com/structural-explainability/se-identity-ops/blob/main/DECISIONS.md)
- [Repository and Reproduction Procedures](https://github.com/structural-explainability/se-identity-ops)
- [Citation Metadata](https://github.com/structural-explainability/se-identity-ops/blob/main/CITATION.cff)
