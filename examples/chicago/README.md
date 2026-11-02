# Experiment A: Chicago Vendor Identity

## Question

Where does the existing US-IL localization step treat vendor records as the same
although a declared criterion does not require it, and where does it separate
records the criterion relates?

## Evidence Role

Exploratory run on real records. It is not held-out and it is not engineering
validation of a known result. No earlier result for this mechanism and criterion
pair is claimed.

## Inputs and Provenance

- **Records.** 20,000 rows of
  `data/identity/chicago_contracts_vendors_sample_20k.csv` in
  `civic-interconnect/civic-data-identity-us-il`, at commit
  `ef04dc182d90f21e828a3d187ebe32cf80392baa`. SHA-256 of that file:
  `836257c0dee85d4b5bb54cde99fb6be291c7fb4e63ea8dd2dbe59a9e4aef3f65`.
  The file is a sample of the City of Chicago Contracts dataset (public domain).
- **Mechanism.** The function
  `cep_core::common::localization::apply_localization_name(name, "US-IL")` in
  `civic-interconnect/civic-interconnect` at commit
  `93b7e282e3958b7dc4b6051276de2cebf4fc6e51`. It is the first step of the US-IL
  vendor adapter in that repository's Python package. That repository's Python package calls this
  Rust function through an extension module, which the PyPI release I tried did not
  include, so a small Rust harness ([`harness/`](./harness/)) calls the function
  directly. The mechanism was
  built from the upstream source and was not modified or reimplemented.
- **Observation file.** [`data/vendors_20k_observed.csv`](./data/vendors_20k_observed.csv)
  has one row per input row: `row` (r00001 ...), `vendor_id`, `vendor_name`,
  `localized_name`. SHA-256:
  `6a821da98aaedc2011f011d4c8ecb05786eed9256eda295f7510129660a618f5`. It was written
  by [`prepare_observations.py`](./prepare_observations.py).

The harness was checked against `out/us_il_normalized_sample.csv`, committed in the
upstream repository. That file is a manually reviewed sheet whose two name columns
are not row-aligned, so it cannot be compared row by row. As multisets, 651 of its
654 normalized values equal the harness output; the other three are blank cells in
the sheet.

## Declared Criterion

`city_vendor_registration`: two records are the same when the City publishes the same
**Vendor ID**. This is a **registration-level** criterion. It is **not** a legal-entity
criterion: one legal entity may hold more than one Vendor ID, and one Vendor ID may be
reused for a renamed vendor. No documented legal-entity criterion was found in the
inspected repositories, so none was written. See [DOUBTS.md](../../DOUBTS.md).

Different Vendor IDs are **not** declared distinct. The criterion is silent about them.

## Program and Expectations

- [`program.ido`](./program.ido): the program.
- [`expected.toml`](./expected.toml): expected results, committed before the first run
  on this data. It lists the controls, the predictions with stated confidence, and
  arithmetic relations among counts.

Controls:

- *Positive:* a surface that is the Vendor ID itself (must be faithful and supported);
  coverage; consistency.
- *Negative:* a surface that is the unique row key (must split every related class).
- *Indeterminate:* the same criterion with no named source (must be unwarranted).

## Results

Recorded in [`results/run.json`](./results/run.json); regenerate with:

```shell
uv run se-identity-ops run examples/chicago/program.ido --json examples/chicago/results/run.json
uv run se-identity-ops expect examples/chicago/expected.toml examples/chicago/results/run.json
```

All ten expectations were met and all seven relations held. Every prediction was
correct in outcome. Numbers below are for this sample and these two columns only.

- **Coverage:** complete. All 20,000 rows have a Vendor ID. 2,073 Vendor IDs occur on
  two or more rows.
- **Faithfulness of the localized name:** violated. Two related classes (a Vendor ID)
  are split, 3 items in all:
  - Vendor ID `105503486X`: `ABOVE & BEYOND FAMILY RECOVERY CENTER` becomes
    `above & beyond family recovery center`; `Above and Beyond Family Recovery Center`
    becomes `above and beyond family recovery center`. The ampersand is kept, so a
    spelling variant under one ID is separated.
  - Vendor ID `3624927P`: `INDUSTRIAL COUNCIL OF NEAR WEST CHICAGO` becomes
    `industrial council of near west city of chicago`, and
    `KINZIE INDUSTRIAL. DEVELOPMENT. CORPORATION` becomes
    `kinzie industrial. development.` Two different names under one ID: a rename, a
    reused ID, or a data error. The criterion cannot say which.
- **Faithfulness of the raw name:** violated, 4 classes, 7 items.
- **Collisions of the localized name:** `unsupported`. 51 groups of records share a
  localized name across two or more Vendor IDs (55 class pairs, summed over groups).
  No distinct judgments exist, so none is contradicted. The criterion neither
  requires nor forbids these merges; they are commitments of the localization that the
  criterion does not support.
- **Collisions of the raw name:** `unsupported`, 16 groups.
- **Controls:** all as expected. The positive control had no cross-class group; the
  negative control split all 2,073 related classes.

A post-hoc breakdown, **not a recorded expectation**, in
`results/independent_verification.json`: of the 51 localized cross-class groups, 16 are
the same raw name published under several Vendor IDs, and 35 join different raw names.
Examples of the 35: a trailing number such as 01 or 02, a `|CLEANED-UP` marker, `INC` against
`INC.`, `LLP` against `LLP 01`. Whether any of these pairs is the same legal entity is
not known.

## Independent Verification

[`verify_independent.py`](./verify_independent.py) recomputes every count in two ways
(plain Python, and SQLite SQL) without importing the interpreter, compares both with
`results/run.json`, and replays every example the interpreter reported. All agreed and
no replay problem was found. The LACE-style encoding in `lace/` also reproduced the
divergent counts and the distinct class-pair counts.

## What This Does Not Show

- It does not show that the localization is wrong. A merge the criterion does not
  support may be correct.
- It does not show anything about legal-entity identity.
- It does not compare the SE-based deduplication of this dataset with the original
  deduplication. Neither mechanism was located in the inspected repositories; the
  six-record difference reported on a 20,000-record test is not reproduced here.
- It tests one sample of one dataset.
- The expectations, program, and interpreter were written by the same author. An
  independent reader has not checked them.
