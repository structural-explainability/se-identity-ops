# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

### Planned

- A real persistence dataset (see `examples/persistence/LIMITATION.md`).
- Run ASPEN and ASPEN+ on the Chicago slice and compare explanations.
- A legal-entity criterion for the Chicago audit, with expectations recorded first.
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
