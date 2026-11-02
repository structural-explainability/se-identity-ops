# Research Doubts and Open Questions

This document records the current research assessment,
known limitations, unresolved questions, and safeguards
against overclaiming for this experiment.

For the three research criteria, doubt classifications,
status definitions, and procedures, see the
[SE Research Doubts Standard](https://raw.githubusercontent.com/structural-explainability/.github/refs/heads/main/docs/en/research/doubts.md).

## Repository Summary

This assessment is a summary of the present evidence.

| Criterion                | Current assessment                                                                                                                                                                                                                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mathematical Correctness | The Lean files state the command semantics and prove properties of it, using only the standard axioms. The Python interpreter is checked against Persistence-level definitions by exhaustive small-state comparison, not by proof. Correspondence between Lean and Python is an open obligation. |
| Scientific Adequacy      | Open. The meaning of a Vendor ID is not established. The SBOM run reproduces known cases. The persistence experiment used only synthetic controls and has no real data.                                                                                                                           |
| Theoretical Contribution | None established. Each audit capability was reproduced by a LACE-style encoding. The differences demonstrated are of vocabulary and cost. See [Prior Art](./docs/en/prior-art.md).                                                                                                              |

The doubts below identify specific issues affecting these assessments.

---

<!-- markdownlint-disable MD024 -->

## Register 1. Doubts About Assumptions (Undermining Doubts)

These questions concern the premises of an argument.
Even if a result is correctly computed, can we establish the assumptions necessary to apply it?

### UM-001. (OPEN) Referential Meaning of Vendor ID Is Not Established

#### Research criterion

Scientific Adequacy

#### Concern

Experiment A compares the localization step with "same published Vendor ID".
Vendor ID is a source-provided identifier whose referential meaning has not yet been
independently established. The experiment does not claim it denotes a registration, a
legal entity, or anything else.

#### Current Knowledge

No documentation of what Vendor ID denotes was read: the City's data dictionary page
could not be fetched, and no such definition was found in the inspected repositories.
Different Vendor IDs are treated as undetermined, not distinct.

#### Remaining Work

Obtain the City's own statement of what Vendor ID denotes, and any independently
documented criterion for the entity of interest, then re-run the audit against it with
the expectations recorded first.

### UM-002. (OPEN) Observation Fidelity and Sample Selection

#### Research criterion

Scientific Adequacy

#### Concern

The mechanism was observed through a harness over a 20,000-row sample.

#### Current Knowledge

The harness calls the upstream function unmodified. It matched the multiset of
normalized values in the upstream's reviewed sheet except for three blanked cells. How the
20,000 rows were chosen from the full dataset (more than 182,000 rows) was not
examined.

#### Remaining Work

Run on the full dataset, and examine how the sample was drawn.

### UM-003. (OPEN) Recorded Digests of the Freeze 01 Targets

#### Research criterion

Mathematical Correctness

#### Concern

In the cloned pilot, the SHA-256 recorded in `metadata.toml` for each case's
`target.cdx.json` does not equal the file's digest, with either line-ending form. The
source's digest matches.

#### Current Knowledge

The pilot's tests check recorded hashes only for the sweeps. IdentityOps pins the digest of
the bytes it read. The cause is not known.

#### Remaining Work

Ask the pilot's author which bytes the recorded digests describe.

### UM-004. (OPEN) Surface and Probe Share One Computation

#### Research criterion

Mathematical Correctness

#### Concern

A surface (implementation mechanism) and a probe (read-only observation) are separate
declarations but are evaluated identically. If the roles differ in meaning, the
interpreter does not yet express the difference.

#### Current Knowledge

The only difference is the name of the witness: divergence or incoherence.

#### Remaining Work

Decide whether a probe needs a different check, such as probe sensitivity of a regime,
or whether the roles should merge.

### UM-005. (OPEN CHECK) Lean-to-Python Correspondence

#### Research criterion

Mathematical Correctness

#### Concern

The Lean files are not a proof about the Python code. The obligation stated in
[SEMANTICS.md](./SEMANTICS.md) is checked only by tests and by exhaustive comparison on
carriers of 3 to 6 items.

#### Current Knowledge

Lean's state has no log and no snapshot index. Blocked steps leave the Lean state
unchanged but add a log entry and a snapshot in Python.

#### Remaining Work

State the correspondence per command as a differential test against a compiled Lean
executable, in the style of Cedar, or reduce the claim.

### UM-006. (OPEN) Single Author

#### Research criterion

Scientific Adequacy

#### Concern

The interpreter, the programs, the expectations, and the LACE-style encodings were
written by the same author. Agreement among them is a consistency check.

#### Current Knowledge

Expectations were committed before results, and two independent recomputations plus the
pilot's recorded results were used where available.

#### Remaining Work

Independent review by someone who did not write the interpreter.

### UM-007. (OPEN) LACE Encodings Are Not ASPEN+

#### Research criterion

Theoretical Contribution

#### Concern

The comparison with LACE rests on my plain-clingo encodings. ASPEN and ASPEN+ were not
run.

#### Current Knowledge

See [LACE Attempts](./docs/en/lace-attempts.md).

#### Remaining Work

Run ASPEN+ on the Chicago slice and compare explanations.

### UM-008. (OPEN) PURL Normalization Is Delegated to a Library, Tested on Few Cases

#### Research criterion

Mathematical Correctness

#### Concern

Normalization is now delegated to `packageurl-python` (version recorded in
`examples/sbom/adapter.toml`). That removes a script-local approximation, but the
result depends on the library's behavior and version, and on whether the library
matches the intended specification. It was exercised on 9 PURL occurrences, all
`pkg:deb` with an `arch` qualifier.

#### Current Knowledge

The earlier script-local canonicalizer and the library gave identical output on all 9
occurrences, so no value in the tables or the results changed; only the evidence
columns (`original_purl`, `purl_errors`) and the pinned input digests did. Other types,
namespaces, and qualifiers are untested. Which body now maintains the specification
was not verified.

#### Remaining Work

Confirm the specification's current edition and the library's conformance to it.
Compare the library with the pilot's frozen module under its freeze. Test other types.

## Register 2. Doubts About Conclusions (Rebutting Doubts)

These questions concern whether a claimed conclusion is false.

### RB-001. (OPEN CHECK) Counts of Unsupported Merges Depend on the Criterion

#### Research criterion

Scientific Adequacy

#### Concern

The 51 localized cross-class groups are "unsupported" only relative to the
declared Vendor ID criterion. A different criterion could require some of them or
forbid some. The class-pair count (55) sums pairs per group, so a class pair meeting in two
groups is counted twice.

#### Current Knowledge

The count of distinct class pairs agrees with the interpreter's sum on the localized name
(55) and on the raw name (16) in the sample; that equality is not guaranteed in general.

#### Remaining Work

Report distinct class pairs as well as the sum.

### RB-002. (OPEN) Meaning of "All Expectations Were Met"

#### Research criterion

Scientific Adequacy

#### Concern

Several expectations are controls whose answers follow from the table layout, and several
Experiment B and C expectations are engineering validation or synthetic. Meeting them shows the
interpreter behaves as specified, not that the language is useful.

#### Current Knowledge

Only the Chicago predictions were informed guesses about real data; all four held.

#### Remaining Work

Predictions about data not yet seen, recorded before they are seen.

## Register 3. Doubts About What Our Results Mean (Undercutting Doubts)

These questions concern the connection between a result and the scientific claim made about it.

### UC-001. (STANDING RULES) Model State Versus Real-World Identity

#### Research criterion

Scientific Adequacy

#### Concern

A reader might take a licensed `apply`, or a class of the generated relation, as identity
of real-world referents.

#### Standing Rules

1. Describe a class as generated by the declared criterion, judgments, and licensed steps.
2. `apply` changes a model state. It does not resolve a referent and does not imply
   authority to.
3. Report commitments and differences. Do not say which regime is correct.

### UC-002. (STANDING RULES) Unsupported Is Not Wrong

#### Research criterion

Scientific Adequacy

#### Concern

An `unsupported` collision may be read as an error in the audited mechanism.

#### Standing Rules

1. State that the criterion neither requires nor forbids the merge.
2. Do not call the mechanism wrong on the basis of an `unsupported` result.

### UC-003. (STANDING RULES) Reproducing a Known Case Is Not Generalization

#### Research criterion

Scientific Adequacy

#### Concern

Experiment B reproduces cases that were known when the pilot was designed.

#### Standing Rules

1. Describe them as engineering validation.
2. Do not use them as evidence of generalization.
3. Do not open Freeze 02 material to extend them.

### UC-004. (STANDING RULES) Execution Is Not Novelty

#### Research criterion

Theoretical Contribution

#### Concern

That programs run and pass their tests may be read as a contribution.

#### Standing Rules

1. Call a capability different from LACE, LACE+, or ASPEN+ only where a specific
   difference was demonstrated, and say whether it is vocabulary, cost, or power.
2. Do not infer a contribution from successful execution.
