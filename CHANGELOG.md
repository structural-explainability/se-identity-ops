# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

### Changed

- Experiment B delegates PURL normalization to `packageurl-python` instead of a
  script-local canonicalizer; identical output on all 9 PURLs, component tables gain
  `original_purl` and `purl_errors` columns, and input digests are re-pinned.
- Experiment A states Vendor ID as a source-provided identifier whose referential
  meaning has not yet been independently established; the regime is renamed
  `source_vendor_id`. No count changed.

### Added

- Experiment D (`examples/purl_authorities`): the same program over three independent
  Package URL implementations, with predictions committed before the first run, a post
  hoc validity program, an independent recomputation, and `adapter.toml` records.
- `adapter.toml` provenance records for Experiments A and B, `tests/test_adapters.py`,
  and decision D-013 (domain semantics come from external authorities).

### Planned

- A real persistence dataset (see `examples/persistence/LIMITATION.md`).
- Run ASPEN and ASPEN+ on the Chicago slice and compare explanations.
- An independently documented criterion for what Vendor ID denotes, with expectations recorded first.
- A differential test of the Python interpreter against a compiled Lean executable.
- Report distinct class pairs next to the per-group sum in `collisions`.
- Decide whether probes need a check of their own.

---

## [0.1.0] - 2026-11-02

First experimental version. Partial: see the README.

### Added

- Language: six declarations (`source`, `carrier`, `regime`, `surface`, `probe`,
  `operator`) and five operations (`judge`, `propose`, `apply`, `check`, `explain`).
- Typed syntax, parser, static checker, deterministic reference interpreter with
  immutable snapshots, and a command-line tool.
- Lean 4 core: syntax, state semantics, and proved properties over the Persistence
  commitment calculus.
- Experiment A (Chicago vendors, 20,000 real records), Experiment B (two Freeze 01
  validation cases), and Experiment C (synthetic controls only), each with expected
  results committed before the run.
- Independent recomputation for A and a comparison with the pilot's recorded results
  for B.
- LACE-style clingo encodings of all three experiments and their comparison.
- `SPEC.md`, `SEMANTICS.md`, `DOUBTS.md`, `DECISIONS.md`, prior-art comparison.
