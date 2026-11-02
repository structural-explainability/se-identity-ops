# Experiment D: Substituting the Authority for Package URL Normalization

## Question

Experiment B delegates Package URL normalization to one library. If the authority is
replaced by another independently developed implementation, does the IdentityOps
program stay the same, and do the implementations make the same identity commitments
on the same inputs? Where they differ, what is the reproducible witness?

## Evidence Role

**Exploratory, on a synthetic corpus chosen to provoke differences.** The 37 inputs
were written by hand; they say nothing about how often these cases occur in real
SBOMs. The program and the language are unchanged from the other experiments.

## Inputs and Boundary

- `corpus.csv`: 37 inputs in 20 sets. A set groups spellings that the experimenter
  intends as one package (case, encoding, qualifier order, empty parts, slashes). This
  is a **stipulation**, not an authority's statement. Eight singletons include malformed
  inputs and two controls that must not merge with anything.
- Three implementations ([`adapter.toml`](./adapter.toml)): `packageurl-python` 0.17.6,
  `packageurl-js` 2.0.1, `packageurl-go` v0.1.7. `packageurl-java` was not run (Maven
  Central was unreachable).
- `run_drivers.py` calls each driver and writes `data/purl_authorities.csv` and
  `results/implementations.json`. It defines no normalization rules.

## Program and Order of Work

[`expected.toml`](./expected.toml) and the drivers were committed **before** any driver
was run on the corpus, and `program.ido` and the data table came after. The program
names no implementation: each implementation is a pair of columns. Two kinds of check:

- `n_<impl>_spec` and `n_<impl>_merge`: does the implementation keep the spellings in a
  declared set together, and does it merge across sets? (the synthetic criterion)
- `n_diff_<a>_<b>`: rows that `a` gives the same normalized form are the criterion; does
  `b` ever separate them? (no stipulation needed)

[`posthoc_validity.ido`](./posthoc_validity.ido) was written **after** the first run,
because partition checks cannot see an input that one implementation accepts and
another rejects when it stands alone. It has no recorded prediction.

## Results

Of 17 expectation entries, 13 were met and 4 were not met. Of 6 relations, 5 held and 1
failed. Missed predictions are kept as they were written.

- **Spelling sets.** `packageurl-python` separates 2 of 12 multi-spelling sets;
  `packageurl-js` and `packageurl-go` separate 1 each. No implementation merges
  spellings from different sets.
- **Python rejects an uppercase scheme.** `PKG:deb/debian/base-files@12.4` is rejected by
  Python and accepted by JS and Go, so Python separates that set.
- **A trailing slash.** `pkg:deb/debian/zlib@1.2/` keeps the slash unencoded in Python
  and writes `%2F` in JS and Go. All three separate it from `zlib@1.2`.
- **Python is the finest partition.** Using Python's classes as the criterion, neither JS
  nor Go separates anything. Using JS or Go as the criterion, Python separates 1 class
  (the uppercase scheme). JS and Go induce the same partition on this corpus.
- **The same partition can hide different strings.** JS leaves `+` unencoded in a version
  (`2025b-0+deb12u1`); Python and Go write `%2B`. JS gives the same value to the `+` and
  `%2B` spellings, so it makes the same commitment with different output text. Any check
  that compares a normalized string with a string fixed elsewhere depends on the
  implementation, even when the commitment does not.
- **Validity disagreements (post hoc).** `PKG:` scheme: Python rejects, JS and Go
  accept. `pkg:deb/debian/@1.0` (no name): Python accepts and drops the empty name,
  writing `pkg:deb/debian@1.0` (the namespace becomes the name); JS accepts and writes
  `pkg:deb/debian/%401.0`; Go rejects.

[`verify_independent.py`](./verify_independent.py) recomputes every count from the raw
driver outputs without the interpreter. All agreed.

## What Was Wrong in the Predictions

I expected `packageurl-go` to separate the most sets; it separated fewer than Python. I
expected the pairs of implementations to disagree in both directions; four of six
directions showed no separation, because Python is finer than JS and Go, which agree.

## What This Does Not Show

- It does not show which implementation is right. Each difference is a conformance
  question for the Package URL specification and its type definitions. Which edition
  and body now maintain them was not verified.
- It does not show how common any case is in real SBOMs.
- Nothing about `packageurl-java` or other implementations.
- It does not rerun Experiment B with another library; that experiment still uses
  Python only.
- The spelling sets are the experimenter's stipulation.

## Reproducing

Needs `node`, `go` and the locked dependencies: `npm ci` in `drivers/js`, and the Go
module already in the local cache (`go mod download` in `drivers/go`; see the
checksum-database note in `adapter.toml`). Then `python examples/purl_authorities/run_drivers.py`
and run `program.ido` and `posthoc_validity.ido`. The committed result files are
reproduced byte for byte by `tests/test_examples.py`; the drivers are not run in CI.
