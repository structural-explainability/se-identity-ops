# SE IdentityOps

[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-identity-ops)
[![Tooling](https://img.shields.io/badge/python-3.12%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-yellow.svg)](./LICENSE)

[![CI-Lean](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-lean.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-lean.yml)
[![CI](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-zensical.yml)
[![CI-Python-Versions](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-versions.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-identity-ops/actions/workflows/ci-python-versions.yml)

> A research experiment: a small language for specifying, executing, and auditing
> identity-relevant operations under declared criteria.

IdentityOps asks whether one small language can express the commitments an existing
system makes about sameness, compare them with a declared criterion, and run proposed
transformations against a model state, in three different settings. It is **not** an
entity-resolution engine and makes **no claim of novelty**: LACE, LACE+, and ASPEN+
already provide declarative merge rules, constraints, justifications, alternative
resolutions, and local and global merges. See [docs/en/prior-art.md](./docs/en/prior-art.md).

It reports commitments and differences between commitments. It does not certify
ground truth, and it does not say which identity criterion is correct.

## Read in This Order

1. [SPEC.md](./SPEC.md): purpose, scope, language, exclusions.
2. [SEMANTICS.md](./SEMANTICS.md): exact meaning of every construct.
3. [docs/en/prior-art.md](./docs/en/prior-art.md) and
   [docs/en/lace-attempts.md](./docs/en/lace-attempts.md): relation to LACE, LACE+, ASPEN+.
4. [DOUBTS.md](./DOUBTS.md): what is not established.
5. [DECISIONS.md](./DECISIONS.md): design decisions, rejected designs, failures.

## Status of Version 0.1.0

**Partial.** Each acceptance condition in [SPEC.md](./SPEC.md#acceptance) is met as it
is worded, but one is met only in the weakest sense, and that is why the version is
reported as partial.

Met:

- Declarations and the five operations have explicit semantics.
- The parser and interpreter execute real programs: the Chicago program on 20,000 real
  records, and the two SBOM cases.
- Available controls have expected and actual outcomes, committed in that order.
- Unknown and contradictory evidence stay visible.
- Meaningful Lean properties are proved (see below).
- Independent checks are reproducible.
- A prior-art comparison is documented.
- Unresolved questions are recorded in [DOUBTS.md](./DOUBTS.md).

Met only in the weak sense:

- **"The three contexts have been attempted."** Chicago and SBOM ran on real records.
  Persistence was attempted, and no adequate state-history dataset was found in the
  inspected repositories, so only synthetic interpreter controls ran. The language has
  not been tested on real persistence data. See
  [examples/persistence/LIMITATION.md](./examples/persistence/LIMITATION.md).

## What the Experiments Showed

- **A. Chicago vendor identity** ([examples/chicago](./examples/chicago/README.md)).
  Against a registration-level criterion (same Vendor ID), the US-IL localization step
  split two Vendor IDs' records (an ampersand against "and"; two different names under
  one ID) and merged records across Vendor IDs in 51 groups, which the criterion neither
  requires nor forbids. All ten recorded expectations were met. Two independent
  recomputations agreed. Not shown: that the localization is wrong, or anything about
  legal-entity identity.
- **B. SBOM and PURL** ([examples/sbom](./examples/sbom/README.md)). The known-bad
  conversion splits three hash-anchored components under the canonical PURL slot; reading
  any slot, none. The known-good conversion splits none. This reproduces the pilot's
  recorded verdicts. It is engineering validation of known cases, not evidence of
  generalization.
- **C. Persistence** (synthetic only). Fifteen expectations on invented items were met.
  This tests the interpreter, not the language on real data.

## What Is Proved in Lean

In [`SE/IdentityOps/`](./SE/IdentityOps/), building on Persistence's commitment
calculus, using only `propext`, `Classical.choice`, and `Quot.sound`, with no `sorry`:

- `propose`, `check`, and `explain` leave the state unchanged.
- The same-commitments change only by a same-judgment or a licensed preserving `apply`
  (`same_step_cases`).
- No program removes a commitment (`run_mono_same`, `run_mono_distinct`).
- A program with no `judge` keeps consistent commitments consistent
  (`run_preserves_consistency`): licensing never creates a contradiction.
- A pair's `status` is required, forbidden, or undetermined exactly as Persistence's
  admissible-relation reading says.
- Order matters (`licensing_order_matters`).

**This does not verify the Python interpreter.** The correspondence between them is an
obligation, checked by tests, described in [SEMANTICS.md](./SEMANTICS.md#correspondence).

## Layout

```text
SPEC.md  SEMANTICS.md  DOUBTS.md  DECISIONS.md  CHANGELOG.md  CITATION.cff
src/se_identity_ops/     parser, checker, interpreter, relation, results, loader, CLI
SE/IdentityOps/          Lean syntax, semantics, properties
SETest/IdentityOps/      Lean checks
examples/chicago/        Experiment A: program, expected, data, results, verification
examples/sbom/           Experiment B
examples/persistence/    Experiment C (synthetic) and the limitation
lace/                    LACE-style clingo encodings and their comparison
tests/                   unit tests, exhaustive oracle, order, examples, determinism, LACE
docs/en/                 prior art and LACE attempts
```

## Run

Needs [uv](https://docs.astral.sh/uv/) and, for Lean, [elan](https://github.com/leanprover/elan).

```shell
uv sync
uv run se-identity-ops run examples/chicago/program.ido --json examples/chicago/results/run.json
uv run se-identity-ops expect examples/chicago/expected.toml examples/chicago/results/run.json
uv run pytest
lake build --wfail
lake test
```

Windows PowerShell scripts: `sit.ps1` (get situated: environment, hooks, format, lint,
types, tests, docs), `rel.ps1` (Lean release checks), `shape.ps1` (project structure).

Rebuilding the observation data for Experiment A needs the Rust toolchain and the
upstream checkout; see [examples/chicago/README.md](./examples/chicago/README.md).

## Known Limitations

See [DOUBTS.md](./DOUBTS.md). The main ones:

- The Chicago criterion is registration-level, not legal-entity.
- Experiment B reproduces known cases only; Experiment C has no real data.
- The interpreter, programs, expectations, and encodings have one author.
- ASPEN and ASPEN+ were not run.
- No independent party has reviewed any of it.

## AI Use

See [AI_USE.md](./AI_USE.md).
