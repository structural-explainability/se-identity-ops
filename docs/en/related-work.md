# Related Work

This analysis situates IdentityOps within existing research
on identity reasoning, declarative entity resolution, and formally specified operations.

IdentityOps defines a domain-neutral vocabulary for specifying, executing, and
auditing identity-relevant operations under declared criteria.
Domain adapters provide the authority, implementation, evidence, and
limitations needed to apply those operations in particular settings.

The analysis examines relevant foundations, overlapping capabilities, and
possible relationships between IdentityOps and existing systems.

The primary literature includes the LACE framework,
its LACE+ extension, and the ASPEN and ASPEN+ systems.
It is surveyed in
[Recent Advances in Logic-Based Entity Resolution](https://orca.cardiff.ac.uk/id/eprint/181984/)
(Bienvenu et al.).
Dedupalog, Swoosh, Cedar, and Catala are
related systems not analyzed on this page.

LACE-style encodings of Experiments A, B, and C
were written for this repository to compare recorded behavior.
They are documented in [LACE Attempts](./lace-attempts.md).
ASPEN and ASPEN+ were not run.

## Research Context

Identity-relevant operations occur in many settings, including entity resolution,
representation transformation, normalization, and persistence across state changes.

These settings require criteria for determining which records or states are related,
but they do not necessarily require the same domain vocabulary or operational mechanisms.

IdentityOps provides a common vocabulary for declaring identity commitments,
executing operations against model state, evaluating obligations,
and recording explanations and limitations.

Domain-specific interpretation is supplied through adapters
rather than incorporated into the operation vocabulary.

This separation permits the same IdentityOps program structure to be evaluated
using different external implementations and evidence sources.

Experiment D exercises this separation by substituting three independent Package URL
implementations while retaining the same IdentityOps language.

Declarative entity-resolution research provides important related foundations.
LACE, LACE+, ASPEN, and ASPEN+ address the construction and
evaluation of entity resolutions through rules, constraints, and solution semantics.

The relationship between these approaches and IdentityOps is therefore
a question of overlapping semantics, complementary functions, and possible interoperability.

## Architectural Distinction

### IdentityOps: Operation Vocabulary

IdentityOps specifies the operations used to express, execute, and audit identity commitments.

Its principal operations are:

- `judge`: Record an identity judgment under a declared criterion.
- `propose`: Construct a proposed transformation without changing model state.
- `apply`: Execute a licensed transformation against model state.
- `check`: Evaluate a declared obligation.
- `explain`: Produce the associated derivation, witness, or limitation.

The language defines the meaning and effects of these operations
independently of a particular application domain.

Its declarations identify the relevant records, criteria, observed mechanisms,
evidence, and operator classifications.

The interpreter evaluates the operations and produces explicit outcomes
while preserving unknown, contradictory, and insufficiently supported evidence.

### Domain Adapters: Interpretation and Evidence

Adapters connect the common operation vocabulary to domain-specific evidence and behavior.

They identify the applicable authority, implementation, operation, version,
inputs, outputs, and known limitations.

For example, Experiment D records separate adapters for Python,
JavaScript, and Go implementations of Package URL normalization.

Each implementation supplies observed normalization and validity results.
The IdentityOps language evaluates the consequences of those results under declared criteria.

Changing the implementation does not require changing the IdentityOps operation vocabulary.

The adapter boundary makes the source of domain-specific behavior
explicit and provides a basis for examining whether the same operations
retain their meaning when that behavior changes.

### LACE and Related Systems: Declarative Resolution

LACE is a general declarative framework for entity resolution.
It is not restricted to one application domain.

Its rules and constraints operate over application schemas and predicates
to determine admissible identity resolutions.

LACE+ extends LACE with local merges of values.
ASPEN is an answer set programming system for LACE.
ASPEN+ extends ASPEN with local merges and new optimality criteria.

IdentityOps and these systems therefore address overlapping identity concepts
through different primary tasks.

A resolution system determines or represents admissible merges under its rules.
IdentityOps specifies and audits identity-relevant operations
under declared criteria, including observations supplied by external mechanisms.

A LACE-based system could supply operational observations to an IdentityOps adapter,
subject to an appropriate interface and evidence record.
Such integration has not yet been implemented or evaluated.

The distinction is architectural and methodological.
It does not imply that the approaches have disjoint expressive capabilities.

## Sources and Comparison Method

### Primary Research

The principal reference is
[Recent Advances in Logic-Based Entity Resolution](https://orca.cardiff.ac.uk/id/eprint/181984/) (Bienvenu et al., SIGMOD Record, 2025).

The comparison also draws on the following publications:

- **LACE:** [Bienvenu, Cima, and Gutiérrez-Basulto, PODS 2022](https://www.labri.fr/perso/meghyn/papers/BieCimGut-PODS22.pdf)
- **LACE+:** [Combining Global and Local Merges, KR 2023](https://arxiv.org/abs/2305.16926)
- **ASPEN:** [ASPEN: ASP-Based System for Collective Entity Resolution, KR 2024](https://arxiv.org/abs/2408.06961)
- **ASPEN+:** [Advances in Logic-Based Entity Resolution: Enhancing ASPEN with Local Merges and Optimality Criteria, KR 2025](https://arxiv.org/abs/2508.10504)
- **ASPEN+ implementation:** [Published source code](https://github.com/zl-xiang/ASPEnP)

The survey was examined in full text.
The individual papers and published implementation materials
provide additional context for the capability comparison.

Secondary references include Dedupalog, Swoosh, research on
negative rules in entity resolution, Cedar, Catala, and the
Structural Explainability theories underlying IdentityOps.

### Experimental Comparison

Selected IdentityOps outcomes were reconstructed using
plain-clingo formulations of LACE-style semantics.

The purpose was to examine semantic overlap and identify
differences in operation semantics, evidentiary requirements,
execution behavior, and reporting.

The experiments included:

- Exhaustive small-state comparisons of required, forbidden, and undetermined identity status.
- Reproduction of Chicago vendor identity audit counts.
- Reproduction of SBOM representation-preservation audit counts.
- Simulation of licensed and blocked state transitions.
- Attempts to represent identity-ignoring, breaking, and inapplicable transformation operators.
- Measurement of grounding behavior for an open-world status encoding.

The experiments distinguish capabilities supplied by the
underlying declarative formalism from behavior supplied by
additional comparison rules or external driver logic.

For example, the Chicago and SBOM comparisons used rules
representing both the declared criterion and observed operational relationships.
Additional rules compared the two relations.

The persistence comparison used repeated solving to evaluate
some proposed transformations, while retaining the sequence of states in an external driver.

These distinctions identify which portions of the reported behavior
arise from the declarative reasoning system and which arise from the surrounding execution procedure.

The encodings and experimental results are documented in [LACE Attempts](./lace-attempts.md).

### Methodological Scope

The LACE-style formulations were developed by the author of the IdentityOps interpreter.
They provide implementation evidence for the tested semantic correspondences,
rather than independent scientific validation.

ASPEN and ASPEN+ were examined through their publications and available
implementation materials but were not executed.

At the time of inspection, the published implementation required
a Python 3.9 environment, a bundled `asprin` copy, Python schema configuration,
and precomputed similarity facts.
The inspected repository contained no license file.

The experimental results therefore concern the specified
LACE-style encodings rather than direct executions of ASPEN or ASPEN+.

Where a corresponding behavior was reproduced, the comparison
establishes that result for the tested formulation and inputs.
Where an encoding was unsuccessful, the result
documents the attempted formulation and its limitations.

The capability classifications below reflect these evidentiary distinctions.

## Capability Comparison

### Capabilities Established in Prior Work

LACE and its extensions provide a substantial foundation for declarative entity resolution.

The surveyed capabilities include:

- **Declarative merge rules:** Hard rules require merges when their conditions hold;
  soft rules support optional merges.
- **Denial constraints:** Constraints exclude inadmissible combinations of merges,
  generalizing database restrictions such as functional dependencies.
- **Dynamic merge semantics:** Rule bodies are evaluated over the instance
  produced by earlier merges, allowing derived merges to enable additional rules.
- **Solutions as equivalence relations:** Resolutions are constructed
  through applicable merge rules, with maximal solutions defined under set inclusion.
- **Justifications and proof trees:** Derived merges can be traced
  to the rules and applications supporting them.
- **Alternative resolutions:** Certain merges occur in every solution,
  while possible merges occur in at least one solution.
- **Optimality criteria:** ASPEN+ provides seven criteria for selecting preferred solutions.
- **Local and global merges:** LACE+ supports local merging of values
  in addition to global merging of object references.
- **Complexity results:** The research characterizes recognition,
  solution existence, and possible and certain merge problems.
- **Repair operations:** The Replace extension incorporates fact deletion.

The survey distinguishes dynamic resolution within a
computation from temporal evolution across historical stages.

Its evolving instance refers to changes during a resolution run.
Temporal persistence across independently recorded states is not addressed by that treatment.

The survey also identifies open questions involving explanations
across solution spaces, ontologies, scalability, and learning specifications.

These established capabilities provide context for interpreting
the corresponding IdentityOps constructs.

### Classification Method

The following analysis examines fourteen IdentityOps capabilities.

Each capability is assigned one of four classifications based
on the cited literature and experimental evidence.

- **Demonstrated in LACE:** The cited research explicitly establishes a corresponding capability.
- **Potentially expressible in LACE:** An encoding reproduced the corresponding behavior,
  or a plausible formulation was identified, although the cited work does not
  define the same operation or task.
- **Unclear or requiring further investigation:** The available evidence does not establish the relationship.
- **Outside the demonstrated scope examined:** The capability was not identified
  as a corresponding task in the cited work, and
  the attempted comparison did not establish a direct formulation.

These classifications identify semantic correspondences and
differences in the examined formulations.

The distinction between an operation defined in the IdentityOps language
and an equivalent result constructed using other mechanisms
is retained throughout the comparison.

### 1. Key Criterion as a Declared Relation

**Classification: Demonstrated in LACE.**

IdentityOps supports a regime defined by equality of a specified source column.
The corresponding relationship can be expressed using a hard merge rule
that joins records sharing the designated key.
This capability is established in the prior formalism.
The IdentityOps regime declaration additionally identifies the criterion
and its associated evidence within an executable audit program.

### 2. Same and Distinct Judgments with Consistency Checking

**Classification: Demonstrated in LACE.**

IdentityOps records explicit same and distinct judgments and
evaluates their consistency.
Same-judgments can be represented by hard merges or facts.
Distinct-judgments can be represented through denial constraints.
Consistency corresponds to the existence of an admissible solution.
The underlying consistency problem is therefore covered by
established declarative reasoning techniques.

### 3. Required, Forbidden, and Undetermined Status

**Classification: Potentially expressible in LACE.**

IdentityOps distinguishes relationships that are required, forbidden, or undetermined by recorded commitments.
Certain merges in LACE correspond to required relationships
and are already a defined task.
Distinguishing forbidden from undetermined relationships
requires additional consideration of possible merges.

The experimental encoding introduced a soft rule offering every pair as a candidate merge.
Under that construction, possible merges correspond to relationships that are not forbidden.
The experimental encoding reproduced the interpreter's three-valued status
through an additional soft rule offering candidate merges.
This establishes the correspondence for the tested cases while
introducing a quadratic grounding requirement.

The encoding, exhaustive comparisons, and measurements are documented in
[LACE Attempts](./lace-attempts.md).

### 4. Witnesses for Inconsistent Commitments

**Classification: Unclear or requiring further investigation.**

IdentityOps can report a conflicting distinct judgment together
with the chain of same-commitments relating its endpoints.
LACE can detect inconsistency through the absence of an admissible solution.
The surveyed explanations primarily concern justifications for merges.
The comparison did not establish whether LACE can produce an
equivalent localized explanation of an unsatisfiable commitment set.

The survey identifies explanations over the solution space as an open research area.
A direct comparison of conflict explanations would clarify the relationship.

### 5. Derivation of a Required Relationship

**Classification: Demonstrated in LACE.**

IdentityOps can explain a required relationship through a shortest chain of same-commitments.
LACE supports justifications and proof trees for derived merges.
The IdentityOps chain is a simpler form of this established explanatory capability.
The comparison establishes an overlap in explanatory function.

### 6. Audit of Operational Behavior Against a Declared Criterion

**Classification: Potentially expressible in LACE.**

IdentityOps provides a `faithful` check comparing a declared
identity criterion with an observed implementation mechanism.

The Chicago and SBOM audit outcomes were reproduced using
LACE-style encodings with separate relations for
declared criteria and observed operational behavior.
Additional rules compared those relations.
The encodings, results, and interpretation are documented in
[LACE Attempts](./lace-attempts.md).

The cited LACE work does not identify the comparison
as a separate first-class audit task.
The experiment demonstrates that the evaluated relationship
can be reconstructed using the tested LACE-style formulation.
IdentityOps incorporates the comparison as an operation over
declared criteria and observed mechanisms,
with associated evidence and outcome records.

### 7. Operational Merges Unsupported by a Criterion

**Classification: Potentially expressible in LACE.**

IdentityOps uses `collisions` to identify groups produced
by an implementation mechanism that are not required by the declared criterion.
The tested LACE-style formulation reproduced the collision counts
using separate relations for the declared criterion and observed operational groupings.
The comparison establishes a semantic correspondence
between the audit results and the declarative encoding.
The experimental details are recorded in
[LACE Attempts](./lace-attempts.md).

IdentityOps reports the result as a named audit operation under a specified regime.
A grouping that the regime does not require is
not automatically a grouping that the regime forbids.
That distinction is retained in the interpretation of the result.

### 8. Withholding an Unwarranted Verdict

**Classification: Outside the demonstrated scope examined.**

IdentityOps reports an `unwarranted` result when a criterion
or check lacks the required grounding source.
The cited LACE formulation does not establish an equivalent
source-grounding requirement for reporting a verdict.
This is primarily an evidence and reporting policy rather than a new logical reasoning capability.
An equivalent policy could potentially be incorporated into other systems.
Within IdentityOps, the policy is part of the operation's
declared evidentiary requirements and outcome interpretation.

### 9. Licensed State Changes and Retained Snapshots

**Classification: Outside the demonstrated scope examined.**

IdentityOps uses `apply` to perform a licensed change to model state
while retaining the resulting snapshot.
A LACE-style consistency gate reproduced the interpreter's
licensed and blocked outcomes for the six preserving steps
in the synthetic persistence experiment.
The surrounding driver managed sequential execution and retained state snapshots.
This identifies the correspondence in licensing decisions and
the different location of execution-state management.
The implementation and results are documented in
[LACE Attempts](./lace-attempts.md).
The distinction concerns the organization and semantics of operations over successive model states.

### 10. Identity-Ignoring, Breaking, and Inapplicable Operators

**Classification: Outside the demonstrated scope examined.**

IdentityOps explicitly classifies transformation operators as
preserving, breaking, ignoring, or inapplicable.
The classifications affect how a proposed transformation is interpreted and reported.
LACE merge rules express whether merges are required or permitted.

The attempted LACE-style formulation did not represent
four synthetic persistence steps classified as
identity-ignoring, breaking, or inapplicable.
The result identifies a limitation of that formulation and a difference in the explicit operation vocabulary.
The attempted encodings and unresolved cases are documented in [LACE Attempts](./lace-attempts.md).

The result also identifies operation classifications
that are explicit in IdentityOps and require further examination
when represented using resolution-oriented rules.

### 11. Lineage Distinguished from Identity

**Classification: Potentially expressible in LACE.**

IdentityOps distinguishes shared lineage from a required identity relationship.
Two successors of one state are not necessarily identical unless
the applicable commitments require that relationship.
A LACE encoding can leave the corresponding records unmerged by omitting a merge rule.
IdentityOps additionally reports that an identity-ignoring operator
occurred without establishing a new identity commitment.
The distinction therefore concerns explicit representation and
reporting of the transformation and its consequences.

### 12. Dependence on Operation Order

**Classification: Outside the demonstrated scope examined.**

IdentityOps programs are sequential.
The results of `judge` and `apply` can depend on their execution order.
LACE specifications are declarative, and their solutions are
not defined by the order of rule execution.
The approaches therefore have different execution semantics.
The distinction is relevant when representing identity-relevant operations
as an ordered history rather than as a declarative resolution problem.

### 13. Persistence Across Stages or Time

**Classification: Outside the demonstrated scope examined.**

The cited survey does not address temporal evolution across independent stages.
IdentityOps includes constructs for specifying transformations and
examining identity commitments across successive model states.
The persistence experiment exercised these constructs through synthetic controls
involving rekeying, forks, merges, and operator classifications.

A suitable real state-history dataset was not established.

The current evidence establishes interpreter behavior on the synthetic cases.
Empirical evaluation of persistence operations on documented
real state histories remains an open research task.

### 14. Named Causes of Indeterminate Outcomes

**Classification: Unclear or requiring further investigation.**

IdentityOps distinguishes several reasons for an unsettled result.
These include insufficient information, inapplicability, and operator underdetermination.
LACE reports certain merges, possible merges, and the absence of solutions.
The comparison did not establish whether the IdentityOps distinctions
represent additional reasoning capabilities or a more explicit reporting vocabulary.
Further analysis is required to determine their correspondence with the prior formalism.

## Differences Observed in the Tested Formulations

The experimental comparison identified four differences between IdentityOps
and the tested LACE-style formulations.
These concern the representation cost of undetermined relationships,
transformation operator vocabulary, evidentiary warrant, and sequential execution.
The findings characterize the tested formulations and identify questions relevant
to the design of an operation-oriented audit language.

### 1. Cost of Representing Undetermined Relationships

The tested open-world LACE-style encoding introduced
candidate relationships between every pair of items.
The resulting grounding size increased quadratically with the carrier size.

IdentityOps computed relationship status using equivalence closure
without materializing every possible pair as a candidate merge.
The experiment therefore identifies different computational representations
for required, forbidden, and undetermined relationships.

The measurements concern the particular encoding and workloads tested,
rather than a controlled performance comparison between implementations.
The grounding measurements and reproduction procedure are documented in
[LACE Attempts](./lace-attempts.md).

### 2. Vocabulary for Transformation Operators

IdentityOps explicitly represents preserving, breaking, ignoring, and
inapplicable transformation classifications.
The LACE-style comparison could express licensed and
blocked preserving steps through repeated solving.

Four steps involving other classifications in the synthetic persistence program
could not be represented by the attempted encoding.
This identifies a difference in the constructs and reporting vocabulary
of the tested formulations.

The classifications distinguish the identity consequences of a
transformation from whether a particular merge is required or permitted.
Further experiments could determine whether the explicit classifications
improve the specification or interpretation of real operational histories.

### 3. Warrant and Evidence Grounding

IdentityOps can withhold a verdict when a regime lacks a declared source.
The tested LACE-style formulation does not contain a
corresponding source-warrant requirement.
This creates an observable reporting difference.

The requirement is an evidence-policy decision that could be
incorporated into another reasoning system.
Within IdentityOps, the policy connects the operation outcome to the
evidence declared by the program and its domain adapter.
It distinguishes an evaluated obligation from one for which the
available declarations do not support a verdict.

### 4. Order-Dependent Execution

IdentityOps specifies sequential behavior for `judge` and `apply`.
The order of operations can change which transformations are
licensed and which commitments result.
LACE specifications are declarative and order-insensitive by design.
The approaches therefore represent different execution models.
Sequential execution is relevant to the IdentityOps persistence controls
because operations are evaluated against successive model states.
The interpretation of those states depends on the declared
operations, classifications, and commitments.

## Scope and Interpretation

The prior-art comparison establishes substantial overlap between
IdentityOps and existing declarative entity-resolution research.
Key-based identity criteria, same and distinct judgments,
consistency checking, required relationships, and derivations
have established counterparts in LACE.
The tested LACE-style encodings also reproduced the Chicago and SBOM audit counts.
These results demonstrate that several IdentityOps outcomes can
be obtained using established logical techniques.

The architectural contribution under investigation is
the organization of identity-relevant operations into
a common language with explicit semantics,
while domain-specific interpretation is supplied through adapters.

### Operation Vocabulary and Domain Adapters

IdentityOps defines the operations used to specify, execute,
and audit identity commitments.
The language establishes the semantics of judgments,
proposed transformations, licensed state changes, checks, and explanations.
Its outcome records distinguish established, refuted, and
undetermined results, together with operation-specific explanations and limitations.

Domain adapters supply the relevant external authorities,
implementations, observations, evidence, and constraints.
This separation permits different domain mechanisms to be
examined through the same operation vocabulary.

The language therefore provides a common basis for
comparing operational consequences without incorporating
each domain's implementation rules into its own semantics.

### Evidence from the Four Experiments

The four experiments examine different aspects of the proposed language.

#### Experiment A: Chicago vendor identity

The Chicago experiment compares a declared Vendor ID criterion
with the grouping behavior of an existing localization mechanism.
The program identifies differences between the criterion and
operational treatment, including required relationships
that the mechanism separates and cross-ID groupings
that the criterion neither requires nor forbids.
The findings demonstrate an audit against a declared criterion
using real records.

#### Experiment B: SBOM representation preservation

The SBOM experiment evaluates the consequences of transformations
between SPDX and CycloneDX representations.
The declared criterion associates components using SHA-256 content hashes,
while observations distinguish canonical Package URL preservation from preservation in other locations.
The results reproduce known conversion behavior and provide
engineering validation of the language on these cases.

#### Experiment C: Persistence

The persistence experiment exercises judgments and transformation operators
across successive synthetic model states.
The controls evaluate continuation, breakage, ignoring behavior,
inapplicability, and the consequences of forks and merges.
The results establish interpreter behavior on specified synthetic cases.
Empirical evaluation against real state histories remains outstanding.

#### Experiment D: Package URL authority substitution

The Package URL experiment compares three independently
developed normalization implementations over a common synthetic corpus.
The implementations supply different observed normalization
and validity behavior through recorded adapters.
The IdentityOps language and program structure remain unchanged.
The experiment records changes in induced identity partitions
and input acceptance while preserving the external source of each observation.
This provides initial evidence that the language can retain
its operation semantics while the domain implementation supplying observations changes.
Together, the experiments exercise operational identity,
representation preservation, persistence controls, and
substitution of external implementation authorities.

### Relationship to Resolution-Oriented Research

LACE, LACE+, ASPEN, and ASPEN+ provide established methods for
deriving, constraining, explaining, and selecting identity resolutions.

IdentityOps uses a different primary abstraction: operations performed
under declared identity criteria, together with their
state effects, evidence, and audit outcomes.
The current IdentityOps language does not include:

- Similarity predicates.
- Soft merge rules.
- Optimality criteria.
- Alternative and preferred resolutions.
- Local merges of values.
- Dynamic merge-rule semantics.
- Repair through fact deletion.

These capabilities remain relevant when the domain mechanism
being examined performs entity resolution.
For example, LACE+ local value merges may offer an alternative account
of the Chicago spelling variants examined in Experiment A.
The outputs of an entity-resolution system could also
provide observations to an IdentityOps adapter.

An adapter for a LACE-based implementation would identify the
applicable rules, implementation, evidence, resulting relationships, and interpretation limits.
The IdentityOps program could then evaluate those
observations against a separately declared criterion.
This integration is consistent with the adapter architecture and
provides a possible direction for subsequent experimentation.

### Scientific Interpretation

The comparison supplies evidence for distinguishing
mathematical correspondence, architectural organization, and practical utility.
The LACE-style experiments demonstrate that several IdentityOps results
can be reconstructed using established declarative techniques.
The operator classifications, evidence requirements,
sequential state transitions, and reporting conventions
characterize the IdentityOps language and execution model.

The four IdentityOps experiments provide evidence that a
common operation vocabulary can be executed in multiple settings
with separately recorded criteria and observations.
Further research is needed to establish how broadly this
architecture applies, which parts of its semantics remain
invariant across domains, and how its audit records compare
with explanations produced by other systems.

The present evidence provides a foundation for these investigations
through explicit semantics, reproducible programs, recorded predictions,
retained results, and independently checkable observations.

## Further Comparative Experiments

Additional investigations could clarify interoperability,
semantic correspondence, and the explanatory value of the
IdentityOps operation vocabulary.

### LACE as an External Operational Mechanism

A LACE-based implementation could provide observed identity relationships
through a domain adapter.
Such an adapter would record the implementation, version, rules,
input evidence, resolution outputs, and interpretation limits.
An IdentityOps program could then compare those outputs with a
separately declared identity criterion.
The experiment would evaluate whether the existing operation vocabulary
can audit an independently implemented resolution mechanism
without incorporating its resolution rules into the language.
It would also provide a direct test of the adapter boundary
in a domain mechanism other than Package URL normalization.

### ASPEN and ASPEN+ Execution

Direct execution of the published ASPEN and ASPEN+ implementations
on the Chicago data slice would provide additional comparative evidence.
Their resolutions, justifications, and proof trees could be
compared with the relationships and witnesses recorded by IdentityOps.
The comparison would distinguish the derivation of entity resolutions
from the evaluation of those resolutions under a declared criterion.
It would also identify the evidence and interface requirements
needed to use the resulting relationships as operational observations.

### LACE+ Local Value Merges

LACE+ local merge operations could be applied to the two
Chicago variants identified by Experiment A:

- The ampersand versus the word "and".
- The different names recorded under one Vendor ID.

The experiment would examine whether local value merging
provides an appropriate account of these cases.
The resulting relationships could then be compared with the
declared Vendor ID criterion and the existing localization behavior.
This would extend the comparative analysis to a domain mechanism
that explicitly transforms values during resolution.

### Audit Semantics and Explanations

A further comparison could examine how a LACE-style specification
represents an audit between a declared identity criterion
and observed implementation behavior.
The analysis would distinguish:

- Rules defining the criterion.
- Rules representing operational observations.
- Rules comparing the resulting relationships.
- Explanations supporting the comparison outcome.

The resulting justification could be compared with the derivations
and witnesses produced by IdentityOps.
This would clarify the correspondence between a named audit
operation and an audit assembled from existing declarative constructs.

### Inconsistent Commitment Explanations

Cases containing distinct judgments that contradict required
same-relationships could be used to examine conflict explanations.
The experiment would evaluate whether LACE can localize the
resulting unsatisfiability.
The explanation could then be compared with the IdentityOps
conflict witness and chain of same-commitments.
The comparison would examine explanatory structure, completeness,
and the evidence available to support the reported conflict.
These investigations would extend the current evidence concerning
semantic correspondence, domain adapters, operation execution,
and reproducible explanations.

## Additional Prior Art and Sources

### Dedupalog

Arasu, Ré, and Suciu, "Large-scale deduplication with
constraints using Dedupalog," ICDE 2009.

Dedupalog provides declarative deduplication using hard and soft rules.
The LACE papers identify Dedupalog as part of their research foundation.
Its relevance to IdentityOps lies in the established use of
declarative rules and constraints for identity-relevant relationships.

### Swoosh

Benjelloun, Garcia-Molina, Menestrina, Su, Whang, and Widom,
"Swoosh: a generic approach to entity resolution," VLDB Journal 18(1), 2009.

Swoosh treats matching and merging as black-box operations and
examines properties that permit efficient resolution.
IdentityOps similarly permits observation of an
external mechanism without reimplementing that mechanism.
The corresponding audit compares its recorded behavior with a
separately declared identity criterion.
This provides a useful conceptual connection to the adapter architecture.

### Negative Rules in Entity Resolution

[ER-N, VLDB Journal](https://vldb.org/vldb_journal/index.php/component/article_manager/article/1105)

Negative rules exclude combinations that would produce inconsistent resolutions.
This research is relevant to the interpretation of distinct judgments and admissible identity relations.
A detailed experimental comparison was not conducted.

### Cedar

[How We Built Cedar, 2024](https://arxiv.org/abs/2407.01688)

Cedar combines a formal Lean model, a production implementation, and differential testing between them.
IdentityOps uses a related verification architecture at a smaller scale.
Its comparison employs exhaustive small-state tests rather than random differential testing.

The Lean proofs establish properties of the formal model.
The Python implementation is checked separately through tests;
formal correspondence between the implementations remains an obligation.
Cedar provides relevant precedent for separating formal semantics,
implementation behavior, and evidence of correspondence.

### Catala

[Merigoux, Chataing, and Protzenko, ICFP 2021](https://arxiv.org/abs/2103.03198)

Catala provides a language with formal semantics and deliberately
limited computational expressiveness.
IdentityOps similarly uses a small language intended to make its
operations and interpretation explicit.
The relationship concerns language design, formal specification,
and the construction of interpretable execution semantics.

### Structural Explainability Theories

Two existing Structural Explainability theories directly support IdentityOps:

- [`se-theory-persistence`](https://github.com/structural-explainability/se-theory-persistence)
- [`se-theory-operational-identity`](https://github.com/structural-explainability/se-theory-operational-identity)

Persistence provides the commitment calculus and interpretation
of admissible identity relationships.
Operational Identity provides the theoretical treatment
of declared identity criteria and observed implementation behavior.
These are prior contributions within the
Structural Explainability research program.
IdentityOps provides an executable operation vocabulary and
interpreter built on these foundations.

### Sources

- Bienvenu et al., [Recent Advances in Logic-Based Entity Resolution](https://orca.cardiff.ac.uk/id/eprint/181984/).
- Bienvenu, Cima, and Gutiérrez-Basulto, [LACE](https://www.labri.fr/perso/meghyn/papers/BieCimGut-PODS22.pdf).
- Bienvenu, Cima, Gutiérrez-Basulto, and Ibáñez-García, [Combining Global and Local Merges](https://arxiv.org/abs/2305.16926).
- Xiang et al., [ASPEN](https://arxiv.org/abs/2408.06961).
- Xiang et al., [ASPEN+](https://arxiv.org/abs/2508.10504).
- [ASPEN+ Published Implementation](https://github.com/zl-xiang/ASPEnP).
- [How We Built Cedar](https://arxiv.org/abs/2407.01688).
- [Catala](https://arxiv.org/abs/2103.03198).
- [Negative Rules in Entity Resolution](https://vldb.org/vldb_journal/index.php/component/article_manager/article/1105).
