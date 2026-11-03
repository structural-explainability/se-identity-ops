# se-identity-ops

[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-identity-ops/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-identity-ops)
[![Tooling](https://img.shields.io/badge/python-3.12%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-yellow.svg)](./LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23926679.svg)](https://doi.org/10.5281/zenodo.23926679)

[![CI-Lean](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-lean.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-lean.yml)
[![CI](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-zensical.yml)
[![CI-Python-Versions](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-versions.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-versions.yml)
[![Docs](https://github.com/structural-explainability/se-identity-ops/actions/workflows/deploy-zensical-lean.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/deploy-zensical-lean.yml)
[![Links](https://github.com/structural-explainability/se-identity-ops/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/links.yml)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-brightgreen.svg)](https://github.com/structural-explainability/se-identity-ops/security)

> A research experiment in specifying, executing, and auditing
> identity-relevant operations under declared criteria.

This research evaluates whether a small declarative language
can specify, execute, and audit identity-relevant operations
under explicitly declared criteria.

The repository contains the IdentityOps language and interpreter,
a Lean formalization, experimental programs, recorded predictions,
preserved results, and independent verification procedures.

Four experiments examine its behavior using
Chicago vendor records,
SBOM transformations,
synthetic persistence controls, and
alternative Package URL implementations.

The experiments distinguish recorded predictions from observed results,
retain disagreements and limitations, and support independent verification.

## SE IdentityOps

IdentityOps provides a language and interpreter for expressing identity
commitments across different domains, comparing those commitments with
operational behavior, and producing reproducible evidence of agreement,
divergence, and indeterminacy.

The language distinguishes declared identity criteria from the mechanisms
that operate on records or representations.
This permits comparison of what a criterion requires with how an
implementation actually treats the relevant records.

A program identifies the evidence sources, the records under examination,
the applicable identity criterion, and the operational behavior being evaluated.
The interpreter executes the program and produces explicit outcomes,
including supporting evidence and witnesses of divergence.

### Language Constructs

The language includes six declaration types:

- `source`: identifies evidence and records its SHA-256 digest.
- `carrier`: identifies the records under examination.
- `regime`: declares an identity criterion over those records.
- `surface`: represents an observed mechanism that groups records.
- `probe`: supplies observations of operational behavior.
- `operator`: declares the identity-preservation classification of a transformation.

A regime may be defined using a source column or explicit judgments.
A shared source value is evidence under the selected criterion;
it does not independently establish the identity of real-world referents.

The language provides five operations:

- `judge`: records a same or distinct judgment with evidence and scope.
- `propose`: constructs a proposed transformation without changing state.
- `apply`: executes a licensed transformation against model state.
- `check`: evaluates a declared obligation.
- `explain`: produces the associated explanation or evidence.

The available checks examine faithfulness, collisions, consistency,
status, and coverage.

The model preserves unknown and contradictory evidence.
A distinction between what is required, forbidden, or undetermined
is maintained throughout execution.

The language specification and exact operation semantics are documented in:

- [SPEC.md](./SPEC.md)
- [SEMANTICS.md](./SEMANTICS.md)

## Research Context

IdentityOps builds on Structural Explainability research in persistence
and operational identity.

The Persistence commitment calculus provides the underlying interpretation
of identity commitments and admissible identity relations.
Operational Identity addresses the relationship between declared identity
criteria and the behavior induced by implementations.

Related research includes the LACE framework and its LACE+ extension,
and the ASPEN and ASPEN+ systems
([Bienvenu et al., Recent Advances in Logic-Based Entity Resolution](https://orca.cardiff.ac.uk/id/eprint/181984/)).
These provide declarative approaches to entity resolution,
constraints, justifications, alternative resolutions,
and local and global merge operations.

IdentityOps sits outside these systems.
It uses LACE-style encodings of the experimental cases as a comparison.
It investigates a language and execution model for expressing
and auditing **identity-relevant commitments** across different domains.

The relationship to existing approaches is documented in:

- [Related Work](./docs/en/related-work.md)
- [LACE Attempts](./docs/en/lace-attempts.md)

## Experimental Design and Sequence

The research separates four activities:

1. Experimental design and predictions.
2. Execution against declared inputs.
3. Preservation of results.
4. Independent verification and interpretation.

This separation distinguishes expectations recorded before observation
from conclusions developed after examining results.

### 1. Design and Source Preparation

The language specification, semantics, domain adapters,
and experimental programs establish the conditions of each experiment.

Each experiment identifies its evidence sources, declared identity criterion,
operational mechanism, and applicable limitations.

The experiments have different evidence roles:

- **A. Chicago:** Exploratory evaluation using real vendor records.
- **B. SBOM:** Engineering validation against previously known conversion behavior.
- **C. Persistence:** Synthetic interpreter controls.
- **D. PURL authorities:** Exploratory comparison of independent implementations using a synthetic corpus.

These distinctions are retained when interpreting the results.

### 2. Record Predictions

Each experiment contains an `expected.toml` file.

The files record applicable positive controls, negative controls,
indeterminate outcomes, predictions, and relations among expected counts.

Predictions include their stated basis and, where applicable,
confidence or interpretation constraints.

The repository history records the expectation files before
the corresponding experimental result files.
This historical ordering is checked by the test suite when the complete
Git history is available.

Experiment D has an additional distinction.
Its predictions and drivers were committed before the drivers were
first executed on the experimental corpus.
The IdentityOps program and assembled observation table followed.
A separate validity analysis was introduced after the initial results
and is explicitly identified as post hoc.

### 3. Execute the Experiments

The interpreter executes programs written in the IdentityOps language.

Each experimental program reads its declared data and evaluates
the specified operations.
Execution produces deterministic JSON results.

The results of the completed experiments are preserved under:

- `examples/chicago/results/`
- `examples/sbom/results/`
- `examples/persistence/results/`
- `examples/purl_authorities/results/`

The result directories contain execution records,
expectation comparisons, and available independent verification records.

These committed files constitute the historical experimental evidence.

### 4. Verify and Interpret the Results

The repository provides several forms of verification:

- Re-execution of committed programs against committed inputs.
- Byte-for-byte comparison with recorded JSON results.
- Comparison of observed results against recorded expectations.
- Independent recomputation of selected results.
- Tests of interpreter behavior and deterministic execution.
- Lean verification of specified mathematical properties.
- Git-history checks of the order in which predictions and results were recorded.

Independent checks are intended to expose disagreements.
They do not modify the interpretation rules to accommodate an observed result.

Predictions that were not met remain in the experimental record.
Post-hoc observations are identified separately.

The verification commands and procedures for conducting additional
reproductions are documented below.

## Experiments and Results

### A. Chicago Vendor Identity

**Evidence role:** Exploratory evaluation using real records.

The experiment examines the existing US-IL localization mechanism
against the declared criterion of equal published Vendor IDs.

The source contains 20,000 Chicago vendor records.
The operational mechanism applies the US-IL localization function
to vendor names and records its output.

The criterion relates records that share a published Vendor ID.
Different Vendor IDs are not automatically declared distinct.

The experiment compares the criterion with both raw vendor names
and their localized forms.
Positive, negative, and indeterminate controls are included.

**Experimental records:**

- [Design, provenance, and interpretation](./examples/chicago/README.md)
- [Program](./examples/chicago/program.ido)
- [Predictions and controls](./examples/chicago/expected.toml)
- [Recorded execution](./examples/chicago/results/run.json)
- [Expectation comparison](./examples/chicago/results/expectations.json)
- [Independent verification](./examples/chicago/results/independent_verification.json)

**Findings:**

The localization step separated records belonging to two
published Vendor ID classes.

One separation involved the distinction between an ampersand
and the word "and".
Another involved two different vendor names recorded under one Vendor ID.

The localized names also grouped records belonging to different
Vendor IDs in 51 groups.
The declared criterion neither requires nor forbids those cross-ID groupings.

All ten recorded expectations were met.
All seven recorded relations held.

Two independent recomputations, using plain Python and SQLite,
agreed with the interpreter's recorded counts.
The LACE-style encoding also reproduced the divergent counts
and distinct class-pair counts.

A post-hoc breakdown identified 16 cross-ID groups with the same raw name
and 35 groups joining different raw names.
That breakdown was not part of the original predictions.

The findings identify specific differences between declared identity
commitments and operational grouping behavior.
Their interpretation depends on the declared Vendor ID criterion
and the documented source semantics.

### B. SBOM and Package URL Identity

**Evidence role:** Engineering validation of previously known cases.

The experiment evaluates identity-relevant information preserved
during conversion from SPDX to CycloneDX.

The declared criterion associates source packages and target components
using SHA-256 content hashes.
The program then examines Package URL information in the target representation.

Two previously recorded conversion cases are evaluated:

- A known-bad conversion using CycloneDX CLI 0.31.0.
- A known-good conversion using CycloneDX CLI 0.32.0.

The inputs come from the Structural Explainability
software supply-chain preservation pilot.

Package URL normalization is delegated to `packageurl-python`,
with the implementation and version documented in the adapter record.

**Experimental records:**

- [Design and authorized evidence](./examples/sbom/README.md)
- [Known-bad program](./examples/sbom/known_bad.ido)
- [Known-good program](./examples/sbom/known_good.ido)
- [Predictions and controls](./examples/sbom/expected.toml)
- [Known-bad results](./examples/sbom/results/known_bad.json)
- [Known-good results](./examples/sbom/results/known_good.json)
- [Expectation comparison](./examples/sbom/results/expectations.json)
- [Independent verification](./examples/sbom/results/independent_verification.json)

**Findings:**

In the known-bad conversion, the canonical CycloneDX PURL slot
separates three hash-anchored components:
`base-files`, `netbase`, and `tzdata`.

When PURL values in other target locations are considered,
none of those anchored component pairs is separated.

The known-good conversion separates none of the anchored pairs
under either observation procedure.

Eight of the fourteen component frames lack a SHA-256 anchor.
Their identity relationship remains undetermined under the
declared content-hash criterion.

All ten recorded expectations were met.
Both recorded relations held.

The independent verification compared the observed results with
the pilot's recorded preservation verdicts.
All six anchored comparisons agreed.

The experiment reproduces the pilot's known preservation behavior
using IdentityOps declarations and operations.
The experiment's evidence role remains engineering validation.

### C. Persistence

**Evidence role:** Synthetic interpreter controls.

The experiment evaluates the execution semantics of
identity-relevant transformations and judgments across model states.

The controls examine:

- Rekeying under a preserving operator.
- Forks with identity-ignoring operators.
- Forks with preserving operators and explicit distinctions.
- Forks without recorded distinctions.
- Merges involving distinct predecessors.
- Breaking and inapplicable operators.
- Consequences of operation ordering.

The programs evaluate the licensing and resulting identity
commitments associated with these operations.

**Experimental records:**

- [Persistence limitation and design](./examples/persistence/LIMITATION.md)
- [Program](./examples/persistence/program.ido)
- [Predictions and controls](./examples/persistence/expected.toml)
- [Recorded execution](./examples/persistence/results/run.json)
- [Expectation comparison](./examples/persistence/results/expectations.json)

**Findings:**

All fifteen synthetic expectations were met.

The controls exercise explicit continuation, blocked transformations,
undetermined outcomes, and the consequences of recorded distinctions.

The experiment demonstrates interpreter behavior on specified
model states whose expected outcomes can be derived independently.

An adequate real state-history dataset was not established.
The search and resulting limitation are recorded in
[Experiment C's limitation record](./examples/persistence/LIMITATION.md).

### D. Package URL Authority Substitution

**Evidence role:** Exploratory comparison using a synthetic corpus.

The experiment evaluates the identity commitments induced by
three independently developed Package URL implementations:

- `packageurl-python` 0.17.6
- `packageurl-js` 2.0.1
- `packageurl-go` v0.1.7

The corpus contains 37 inputs organized into 20 declared sets.
Twelve sets contain multiple spellings.
Eight are singletons, including malformed inputs and controls.

The sets represent stipulated expectations about equivalent spellings.
The comparison also examines the partitions induced by the
implementations themselves, independently of those stipulations.

The same IdentityOps language expresses the comparison.
Each implementation supplies its own observed normalization results.

The experiment records both normalized values and rejected inputs.
The driver implementations provide the external normalization behavior.

**Experimental records:**

- [Design, adapters, and interpretation](./examples/purl_authorities/README.md)
- [Corpus](./examples/purl_authorities/corpus.csv)
- [Program](./examples/purl_authorities/program.ido)
- [Predictions and controls](./examples/purl_authorities/expected.toml)
- [Recorded driver outputs](./examples/purl_authorities/results/implementations.json)
- [Recorded execution](./examples/purl_authorities/results/run.json)
- [Expectation comparison](./examples/purl_authorities/results/expectations.json)
- [Independent verification](./examples/purl_authorities/results/independent_verification.json)
- [Post-hoc validity program](./examples/purl_authorities/posthoc_validity.ido)
- [Post-hoc validity results](./examples/purl_authorities/results/posthoc_validity.json)

**Findings:**

Python separates two of the twelve declared multi-spelling sets.
JavaScript and Go each separate one.

JavaScript and Go induce the same partition on the experimental corpus.
Python induces a finer partition.

One difference concerns an uppercase `PKG:` scheme.
Python rejects the input while JavaScript and Go accept it.

Another concerns a trailing slash in a Package URL.
Python retains the slash in its serialized output,
while JavaScript and Go encode it.

The implementations also differ in the textual encoding of `+`
within a version string.
Equal partitions can therefore be represented by different
normalized strings.

The initial comparison contained seventeen expectation entries.
Thirteen were met and four were not met.
Five of six recorded relations held.

**Four predicted outcomes and one relation were not met.**
The original expectations remain unchanged.

The subsequent validity analysis was conducted after the initial results.
It records disagreements in input acceptance that are not fully
represented by partition comparisons alone.
These observations are reported separately from the original predictions.

Independent recomputation agreed with the recorded interpreter counts.

The experiment establishes reproducible differences among the
tested implementations on the declared corpus.
It also demonstrates that substituting an external normalization
authority can change observed identity commitments without
changing the IdentityOps language.

## Formal Verification with Lean

The Lean formalization is located in
[`SE/IdentityOps/`](./SE/IdentityOps/).

The formal model builds on the Persistence commitment calculus
and defines the semantics of IdentityOps operations and their
effects on commitment state.

The following properties are proved:

- `propose`, `check`, and `explain` leave state unchanged.
- Same-commitments change only through a same-judgment or licensed preserving `apply` (`same_step_cases`).
- No program removes a commitment (`run_mono_same`, `run_mono_distinct`).
- Programs without `judge` preserve consistency (`run_preserves_consistency`).
- A pair's `status` is required, forbidden, or undetermined according to the Persistence admissible-relation interpretation.
- Operation order can affect outcomes (`licensing_order_matters`).

The proof checks use only
`propext`, `Classical.choice`, and `Quot.sound`,
with no `sorry`.

The formalization establishes these properties for the Lean model.
Correspondence between the Lean semantics and the Python interpreter
is a separate verification obligation.

The repository includes interpreter tests that exercise this correspondence.
The relationship and remaining obligations are documented in
[SEMANTICS.md](./SEMANTICS.md#correspondence).

## Research Status and Limitations

**Status: Partial.**

The acceptance conditions recorded in
[SPEC.md](./SPEC.md#acceptance)
have been met as worded.
One condition is satisfied only in the weakest stated sense,
which is why the overall research status remains partial.

### Completed Work

- The declarations and five operations have explicit semantics.
- The Python parser and interpreter execute experimental programs.
- Chicago and SBOM programs have been executed against real records.
- Synthetic persistence controls have been executed.
- Three Package URL implementations have been compared through Experiment D.
- Experimental expectations and results are preserved separately.
- The restored Git history records expectations before experimental results.
- Positive, negative, and indeterminate controls have recorded outcomes.
- Unknown and contradictory evidence remain visible.
- Independent verification procedures have been implemented.
- Mathematical properties have been proved in Lean.
- Related related work and LACE-style encodings are documented.
- Remaining scientific questions are recorded in [DOUBTS.md](./DOUBTS.md).

### Scientific Scope and Remaining Obligations

#### Identity criteria and ground truth

IdentityOps evaluates consequences of declared identity criteria.
It does not independently determine which criterion correctly identifies
real-world referents.

For Experiment A, Vendor ID is a source-provided identifier whose
referential meaning has not been independently established.
The experiment therefore evaluates the published-ID criterion
without assuming that Vendor ID denotes a particular legal entity.

#### Generalization

Experiment B uses conversion cases known during development.
Its results constitute engineering validation rather than
held-out generalization evidence.

The SBOM pilot's Freeze 02 generalization experiment is a separate study.
The IdentityOps experiment uses only the authorized
historical validation cases.

#### Persistence

Experiment C establishes the behavior of synthetic interpreter controls.
A suitable real dataset containing independently documented
state histories, transitions, forks, or merges was not established.
Consequently, the persistence research target has not been
evaluated using real state-history evidence.

#### Package URL authorities

Experiment D uses a synthetic corpus selected to expose differences
among normalization implementations.
The corpus does not support prevalence estimates for real SBOMs.

The experiment records implementation differences without independently
determining which implementation conforms to the authoritative
Package URL specification in each case.

`packageurl-java` was not run because its required Maven artifact
could not be obtained during the experiment.

#### Interpreter correspondence

The Lean proofs apply to the formal model.
The Python interpreter is checked by tests,
but formal equivalence between the two implementations
has not been established.

#### Independent research validation

The interpreter, experimental programs, recorded expectations,
and LACE-style encodings share an author.
Independent human assessment remains an important research obligation.

The independent computations strengthen engineering confidence
but do not replace independent scientific validation.

#### Related work and novelty

IdentityOps is a language and interpreter for studying
identity-relevant commitments and operational behavior.
It is not a general-purpose entity-resolution or merge engine.

Declarative merge rules, constraints, justifications,
alternative resolutions, and merge operations are established
in related research, notably the LACE family of systems.
No claim of novelty is made for those capabilities.

The specific relationship between IdentityOps and related systems
requires evaluation of their respective semantics, expressiveness,
execution models, and evidence.

The LACE-style encodings were written by the author of the interpreter.
They serve as a consistency comparison.
They are not the LACE authors' implementations.
ASPEN and ASPEN+ were not executed.

Additional discussion is available in:

- [DOUBTS.md](./DOUBTS.md)
- [DECISIONS.md](./DECISIONS.md)
- [Related Work](./docs/en/related-work.md)
- [LACE Attempts](./docs/en/lace-attempts.md)

## Verification and Reproduction

The committed inputs, programs, expectations, and results
form the preserved experimental record.

Verification checks that the recorded programs and inputs
continue to reproduce the committed results.
Additional executions can be performed separately without
changing the original evidence.

### Requirements

The Python project requires:

- [uv](https://docs.astral.sh/uv/)
- Python 3.12 or later

The Lean formalization requires:

- [elan](https://github.com/leanprover/elan)

The PowerShell commands require PowerShell 7 (`pwsh`).

Regenerating external observations may require additional tools:

- Experiment A: Rust and the upstream Civic Interconnect checkout.
- Experiment B: The specified SBOM pilot checkout.
- Experiment D: Node.js, Go, and the declared Package URL implementations.

The committed `uv.lock` records the Python dependency resolution.
Ordinary experimental verification does not update dependencies.

### Verify the Committed Results

The following commands run from the repository root.

```powershell
uv sync --locked

uv run --frozen python -m pytest

lake build --wfail
lake test
```

The Python tests re-execute the six committed IdentityOps
program-result pairs in memory and compare the serialized output
with the recorded JSON files byte for byte.

The test suite also verifies recorded expectations,
including the known unmet predictions from Experiment D.

A history check confirms that each experiment's expectation file
precedes its corresponding result files in the full Git history.
That check is skipped when the required history is unavailable
in a shallow clone.

The Lean commands build and check the formal definitions,
theorems, and associated Lean tests.

These verification operations preserve the committed
experimental result files.

### Original Experiment Execution and Result Recording

The original experiments were conducted using the IdentityOps
command-line interface.

Three commands provide the principal operations:

- `check` parses a program and reports static diagnostics.
- `run` executes a program and can write the complete result as JSON.
- `expect` compares recorded expectations with one or more run results.

The `--json` option supplies an output path for `run`.
The `--out` option supplies an output path for the
expectation comparison.

A successful `run` or `expect` command means the operation completed.
It does not mean that all checks were satisfied or that all
predictions were correct.

The following commands document the CLI invocations and output locations
for the preserved experimental records.

**These are historical record-creation commands.**
They are provided to document the procedure and original file locations.
They should not be used to overwrite the committed evidence.

```powershell
# A. Chicago vendor identity

uv run --frozen se-identity-ops run examples/chicago/program.ido --json examples/chicago/results/run.json

uv run --frozen se-identity-ops expect examples/chicago/expected.toml examples/chicago/results/run.json --out examples/chicago/results/expectations.json


# B. SBOM and PURL

uv run --frozen se-identity-ops run examples/sbom/known_bad.ido --json examples/sbom/results/known_bad.json

uv run --frozen se-identity-ops run examples/sbom/known_good.ido --json examples/sbom/results/known_good.json

uv run --frozen se-identity-ops expect examples/sbom/expected.toml examples/sbom/results/known_bad.json examples/sbom/results/known_good.json --out examples/sbom/results/expectations.json


# C. Synthetic persistence controls

uv run --frozen se-identity-ops run examples/persistence/program.ido --json examples/persistence/results/run.json

uv run --frozen se-identity-ops expect examples/persistence/expected.toml examples/persistence/results/run.json --out examples/persistence/results/expectations.json


# D. Package URL authority substitution

uv run --frozen se-identity-ops run examples/purl_authorities/program.ido --json examples/purl_authorities/results/run.json

uv run --frozen se-identity-ops expect examples/purl_authorities/expected.toml examples/purl_authorities/results/run.json --out examples/purl_authorities/results/expectations.json


# D. Separate post-hoc validity analysis

uv run --frozen se-identity-ops run examples/purl_authorities/posthoc_validity.ido --json examples/purl_authorities/results/posthoc_validity.json
```

The original `results/` directories also retain independent
verification reports where applicable.

The independent verification scripts may write files within
those result directories.
They should be executed in a separate checkout when
regeneration of those reports is required.

### Reproduce the Experiments Without Overwriting Results

The committed programs can be executed again using the
same committed input tables.

New outputs should be written under `tmp/identityops/`
rather than the original `examples/*/results/` directories.

The following PowerShell commands reproduce all six program-result
pairs and generate new expectation comparisons.

```powershell
# Run from the repository root.
# Use the committed dependency resolution.

uv sync --locked

# Prepare separate reproduction directories.

$Experiments = @(
    "chicago"
    "sbom"
    "persistence"
    "purl_authorities"
)

foreach ($Experiment in $Experiments) {
    New-Item -ItemType Directory -Force `
        -Path "tmp/identityops/$Experiment" | Out-Null
}

# ============================================================
# Experiment A: Chicago
# ============================================================

uv run --frozen se-identity-ops check examples/chicago/program.ido

uv run --frozen se-identity-ops run examples/chicago/program.ido --json tmp/identityops/chicago/run.json

uv run --frozen se-identity-ops expect examples/chicago/expected.toml tmp/identityops/chicago/run.json --out tmp/identityops/chicago/expectations.json


# ============================================================
# Experiment B: SBOM and PURL
# ============================================================

uv run --frozen se-identity-ops check examples/sbom/known_bad.ido

uv run --frozen se-identity-ops check examples/sbom/known_good.ido

uv run --frozen se-identity-ops run examples/sbom/known_bad.ido --json tmp/identityops/sbom/known_bad.json

uv run --frozen se-identity-ops run examples/sbom/known_good.ido --json tmp/identityops/sbom/known_good.json

uv run --frozen se-identity-ops expect examples/sbom/expected.toml tmp/identityops/sbom/known_bad.json tmp/identityops/sbom/known_good.json --out tmp/identityops/sbom/expectations.json


# ============================================================
# Experiment C: Persistence controls
# ============================================================

uv run --frozen se-identity-ops check examples/persistence/program.ido

uv run --frozen se-identity-ops run examples/persistence/program.ido --json tmp/identityops/persistence/run.json

uv run --frozen se-identity-ops expect examples/persistence/expected.toml tmp/identityops/persistence/run.json --out tmp/identityops/persistence/expectations.json


# ============================================================
# Experiment D: Package URL authorities
# ============================================================

uv run --frozen se-identity-ops check examples/purl_authorities/program.ido

uv run --frozen se-identity-ops run examples/purl_authorities/program.ido --json tmp/identityops/purl_authorities/run.json

uv run --frozen se-identity-ops expect examples/purl_authorities/expected.toml tmp/identityops/purl_authorities/run.json --out tmp/identityops/purl_authorities/expectations.json

# Separately reproduce the post-hoc validity analysis.

uv run --frozen se-identity-ops check examples/purl_authorities/posthoc_validity.ido

uv run --frozen se-identity-ops run examples/purl_authorities/posthoc_validity.ido --json tmp/identityops/purl_authorities/posthoc_validity.json
```

These commands use the original committed data,
programs, and expectations.

They create new result files without modifying the
historical experimental records.

### Compare Reproduced Results with the Original Record

SHA-256 hashes can be used to compare the reproduced
JSON files with the committed results.

The following commands check all six program-result pairs.

```powershell
$Programs = @(
    @{ Experiment = "chicago"; File = "run.json" }
    @{ Experiment = "sbom"; File = "known_bad.json" }
    @{ Experiment = "sbom"; File = "known_good.json" }
    @{ Experiment = "persistence"; File = "run.json" }
    @{ Experiment = "purl_authorities"; File = "run.json" }
    @{ Experiment = "purl_authorities"; File = "posthoc_validity.json" }
)

foreach ($Item in $Programs) {
    $Experiment = $Item.Experiment
    $File = $Item.File

    $Original = "examples/$Experiment/results/$File"
    $Reproduced = "tmp/identityops/$Experiment/$File"

    $OriginalHash = (Get-FileHash -Algorithm SHA256 $Original).Hash
    $ReproducedHash = (Get-FileHash -Algorithm SHA256 $Reproduced).Hash

    if ($OriginalHash -ne $ReproducedHash) {
        throw "REPRODUCTION DIFFERS: $Experiment/$File"
    }

    Write-Host "MATCH: $Experiment/$File"
}
```

A matching hash establishes that the reproduced file
is byte-identical to its committed counterpart.

It does not establish that the original scientific
interpretation is correct.

The four expectation comparison files can be checked
using the same procedure if their original and reproduced
JSON serialization is identical.

The `tmp/` directory is for local,
uncommitted reproduction artifacts and is excluded by `.gitignore`.

### Regenerate Source Observations

Re-executing the IdentityOps programs is distinct from
regenerating the observations supplied by external mechanisms.

The observation-generation procedures require additional
source material, tools, and dependencies.

The original observation tables are retained as
part of the experimental record.
Regenerated tables should be written to separate locations
and compared with the preserved inputs.

#### Experiment A: Chicago Localization

The observation-generation script uses the original
Chicago vendor sample and a compiled Rust harness
calling the US-IL localization function.

The upstream source revision, sample digest,
harness construction, and output provenance are documented in
[Experiment A](./examples/chicago/README.md).

After preparing the specified upstream checkout and harness,
a new table can be written to `tmp/`.

```powershell
$Sample = "PATH_TO_CHICAGO_SAMPLE.csv"
$Harness = "PATH_TO_BUILT_HARNESS.exe"

uv run --frozen python examples/chicago/prepare_observations.py `
    --sample $Sample `
    --harness $Harness `
    --output tmp/identityops/chicago/vendors_20k_observed.csv
```

The resulting table can be compared with the committed
`examples/chicago/data/vendors_20k_observed.csv`.

A differing table is retained as a separate observation.
It does not replace the historical input.

#### Experiment B: SBOM Component Extraction

The SBOM extraction script reads only the authorized
historical validation cases from the pilot repository.

The original experiment used the source and known-bad and
known-good targets at the revision documented in
[Experiment B](./examples/sbom/README.md).

The script supports a separate output directory.

```powershell
$Pilot = "PATH_TO_SBOM_PILOT_CHECKOUT"

uv run --frozen python examples/sbom/extract_components.py `
    --pilot $Pilot `
    --output tmp/identityops/sbom/data
```

This generates new component observation tables without
replacing the committed tables.

The supplied pilot checkout should be at the documented
experimental revision.
The extraction procedure does not require examining
the pilot's Freeze 02 generalization material.

#### Experiment D: External Package URL Drivers

The original driver script invokes the three external
Package URL implementations and assembles the
experimental observation table.

As currently implemented, `run_drivers.py` writes to:

- `examples/purl_authorities/data/purl_authorities.csv`
- `examples/purl_authorities/results/implementations.json`

Consequently, direct execution in the primary checkout
would overwrite committed experimental files.

A separate local clone under `tmp/` permits driver
regeneration without changing the primary repository.

The procedure requires Node.js, Go, and the dependency
versions recorded in the experiment.

```powershell
# Run from the primary repository root.
# Create a separate checkout for driver regeneration.

$RunDirectory = "tmp/identityops/driver-rerun-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

git clone --no-local . $RunDirectory

Push-Location $RunDirectory

try {
    uv sync --locked

    # Install the declared JavaScript dependencies.

    Push-Location examples/purl_authorities/drivers/js
    try {
        npm ci
    }
    finally {
        Pop-Location
    }

    # Obtain the declared Go dependencies.
    # The documented driver uses an offline Go module cache.

    Push-Location examples/purl_authorities/drivers/go
    try {
        go mod download
    }
    finally {
        Pop-Location
    }

    # Regenerate the observation table and raw driver outputs
    # inside the separate checkout.

    uv run --frozen python examples/purl_authorities/run_drivers.py

    # Execute the IdentityOps program against those observations.

    uv run --frozen se-identity-ops run examples/purl_authorities/program.ido --json examples/purl_authorities/results/run.json

    uv run --frozen se-identity-ops expect examples/purl_authorities/expected.toml examples/purl_authorities/results/run.json --out examples/purl_authorities/results/expectations.json

    # Reproduce the separate post-hoc validity analysis.

    uv run --frozen se-identity-ops run examples/purl_authorities/posthoc_validity.ido --json examples/purl_authorities/results/posthoc_validity.json
}
finally {
    Pop-Location
}
```

The resulting records remain inside the separate
`tmp/identityops/driver-rerun-*` checkout.

The original repository's evidence is unchanged.

The driver requires the Go dependencies to be available
under the environment constraints documented in
[adapter.toml](./examples/purl_authorities/adapter.toml).
An unavailable dependency is a reproduction limitation
rather than a reason to change the original result.

### Independent Verification

Experiments A, B, and D include independent verification scripts.

These scripts recompute selected quantities without importing
the IdentityOps interpreter.

- [Chicago independent verification](./examples/chicago/verify_independent.py)
- [SBOM independent verification](./examples/sbom/verify_independent.py)
- [PURL authority independent verification](./examples/purl_authorities/verify_independent.py)

Experiment A uses plain Python and SQLite recomputation.
Experiment B compares direct readings of the authorized SBOM
documents with both the IdentityOps results and the pilot records.
Experiment D recomputes normalization-partition statistics
from the raw driver outputs.

The independent scripts can write verification reports under
the original `results/` directories.
For this reason, regenerating those reports should be performed
in a separate checkout, with the original committed files
retained for comparison.

The ordinary `pytest` verification described earlier
does not require regeneration of those reports.

## Repository Layout

```text
SPEC.md
SEMANTICS.md
DOUBTS.md
DECISIONS.md
CHANGELOG.md
CITATION.cff
SE_MANIFEST.toml

src/se_identity_ops/
    parser, checker, interpreter, relation,
    results, loader, command-line interface

SE/IdentityOps/
    Lean syntax, semantics, and properties

SETest/IdentityOps/
    Lean checks

examples/chicago/
    Experiment A
    program, expectations, observations,
    results, independent verification

examples/sbom/
    Experiment B
    known-bad and known-good programs,
    expectations, component observations,
    results, independent verification

examples/persistence/
    Experiment C
    synthetic persistence controls,
    expectations, results, limitation record

examples/purl_authorities/
    Experiment D
    experimental corpus, three drivers,
    programs, expectations, observations,
    results, independent verification

lace/
    LACE-style clingo encodings and comparison

tests/
    unit tests, exhaustive oracle,
    execution ordering, examples,
    determinism, LACE comparisons

docs/en/
    research documentation, related work,
    LACE attempts

tmp/
    optional local reproduction artifacts
    excluded from version control
```

## Research Documentation and Maintenance

The principal research records provide complementary detail:

- [SPEC.md](./SPEC.md): Language scope, research targets, constructs, and acceptance conditions.
- [SEMANTICS.md](./SEMANTICS.md): Exact semantics of declarations and operations.
- [DOUBTS.md](./DOUBTS.md): Unresolved scientific questions and limitations.
- [DECISIONS.md](./DECISIONS.md): Design decisions, rejected approaches, corrections, and revisions.
- [Related Work](./docs/en/related-work.md): Relationship to related research.
- [LACE Attempts](./docs/en/lace-attempts.md): LACE-style encodings and comparative findings.

The repository includes three PowerShell maintenance scripts:

- `sit.ps1`: Environment, hooks, formatting, linting, type checking, tests, and documentation.
- `rel.ps1`: Lean release verification.
- `shape.ps1`: Project structure report.

Dependency and hook updates are disabled in `sit.ps1`
during the research freeze.

The locked Python dependency versions are retained in `uv.lock`.
The reasons and procedure for deliberate updates are documented
in the RESEARCH-FREEZE notes in `sit.ps1`.

## Changelog

[CHANGELOG.md](./CHANGELOG.md)

## Citation

[CITATION.cff](./CITATION.cff)

## Documentation

[Documentation](https://structural-explainability.github.io/se-identity-ops/en/)

## License

[Apache 2.0](./LICENSE)

## Repository Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
