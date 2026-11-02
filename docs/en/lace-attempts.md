# LACE Attempts

Before claiming that IdentityOps does anything LACE or ASPEN+ cannot, each of the
three experiments was attempted in a LACE-style formulation. This page records what
was expressible, what needed an awkward encoding, and what stayed unresolved.

## What Was and Was Not Run

- **Run:** my own plain-clingo encodings of LACE-style semantics, in
  [`lace/`](https://github.com/structural-explainability/se-identity-ops/tree/main/lace),
  driven by `lace/run_lace.py`. Hard rules, a soft rule, denial constraints, and
  equivalence closure are written as clingo rules, following the predicate
  conventions of the published ASPEN+ example encodings (`eqo`, `activeo`).
- **Not run:** ASPEN and ASPEN+ themselves. Their repository
  ([zl-xiang/ASPEnP](https://github.com/zl-xiang/ASPEnP)) was read for its input
  conventions. Running it needs a Python 3.9 environment, a bundled asprin copy, a
  Python schema configuration for each dataset, and precomputed similarity facts. The
  repository carries no license file.
- **Independence:** the encodings were written by the author of the interpreter, so
  agreement between them is a consistency check, not independent confirmation.

## Experiment A: Chicago Vendor Records

**Expressible, with an awkward encoding.** The declared criterion (same Vendor ID) and
the mechanism (same localized name) are two hard-rule sets over one record
predicate, `eqd` and `eqs`. The comparison is ordinary rules over both:
`div_item`, `div_class`, and `cross`. LACE does not define such a comparison between
two rule sets; it is meta-level.

Result: on the 20,000-row sample the encoding found the same divergent classes (2),
divergent items (3), and distinct cross-class pairs (55) for the localized name, and
(4), (7), and (16) for the raw name, as the interpreter and as an independent
recomputation. It ran in a few seconds.

**Awkward:** the comparison needs two copies of every merge predicate, because one
LACE specification has one set of merge rules. The class-pair count had to be
defined as distinct pairs; the interpreter sums pairs per group.

**Unresolved:**

- Whether LACE+ **local merges of values** would treat the observed spelling variants
  better than a global criterion. Two were found: the ampersand against the word
  "and" under one Vendor ID, and one Vendor ID shared by two different names.
- What ASPEN+ explanations (xclingo proof trees) say about the same cases.

## Experiment B: SBOM and PURL

**Expressible.** The same audit encoding, with the content hash as the key and the PURL
as the value, reproduced both cases: three divergent classes and three divergent items
for the known-bad conversion, none for the known-good one.

**Awkward:** the "relocated rather than missing" reading uses a second probe, which is
a second run of the same encoding.

**Unresolved:** the pilot's own verdict vocabulary (preserved, relocated, dropped,
altered, unsupported, underdetermined, unanchorable, not applicable) is richer than
what either formulation reports. No attempt was made to reproduce it.

## Experiment C: Persistence

**Partly expressible.** A driver around a LACE-style gate (licensed steps as hard
merges, distinctions as denial constraints) decided, for every preserving step in the
synthetic program, whether adding it leaves a solution. It reproduced the
interpreter's licensed and blocked outcomes for all six preserving steps.

**Not expressible:** four steps are classified identity-ignoring, identity-breaking,
or inapplicable. A LACE rule either merges or does not, so there is no encoding of
"recorded, joins nothing, and reported as ignoring". The sequence of states and the
retained snapshots live in the driver.

**Unresolved:** whether real state-history data would show differences. None was used.

## Open-World Status

IdentityOps reports a pair as required, forbidden, or undetermined. In LACE terms,
required is a certain merge, a defined task. Telling forbidden from undetermined
needs one soft rule offering every pair as a candidate merge. With that rule,
cautious and brave reasoning reproduced the interpreter's status on all 4,455 pairs
of all assignments of same, distinct, and nothing for 3 and 4 items. The cost is
quadratic in the carrier at grounding, measured at 100, 400, 1,600, and 6,400 ground
atoms for 10, 20, 40, and 80 items.

## How to Reproduce

```shell
uv run python lace/run_lace.py
```

The results are written to `lace/results/lace_attempts.json`. The test
`tests/test_lace.py` runs the script and requires zero mismatches.
