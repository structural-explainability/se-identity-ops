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
- An independently documented criterion for what Vendor ID denotes, with expectations recorded first.
- A differential test of the Python interpreter against a compiled Lean executable.
- Report distinct class pairs next to the per-group sum in `collisions`.
- Decide whether probes need a check of their own.

---

## [0.1.0] - 2026-11-03

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
- Experiment A states Vendor ID as a source-provided identifier whose referential
  meaning has not yet been independently established;
  the regime is renamed `source_vendor_id`.
- LACE-style clingo encodings of Experiments A, B, and C and their comparison.
- `SPEC.md`, `SEMANTICS.md`, `DOUBTS.md`, `DECISIONS.md`, related-work comparison.
- Experiment D (`examples/purl_authorities`): the same program over three independent
  Package URL implementations, with predictions committed before the first run, a post
  hoc validity program, an independent recomputation, and `adapter.toml` records.
- `adapter.toml` provenance records for Experiments A and B, `tests/test_adapters.py`,
  and decision D-013 (domain semantics come from external authorities).

---

## Notes on Versioning and Releases

- We use **SemVer**:
  - **MAJOR** - breaking changes
  - **MINOR** - backward-compatible features
  - **PATCH** - fixes, documentation, tests, tooling
- Versions are driven by git tags. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

## Release Procedure (Required)

Follow these steps exactly when creating a new release.

### One-Time Zenodo Authorization

1. Sign in to Zenodo.
2. Open your profile menu in the upper-right.
3. Select GitHub.
4. Click Sync now.
5. Find this repository under structural-explainability/.
6. Turn on the repository toggle/slider.
7. Refresh the page and confirm it appears as enabled.
8. Zenodo will ingest future GitHub Releases from this repo.

### Task 1. Update release metadata (manual edits)

1.1. `CITATION.cff` - update `version` and `date-released`
1.2. `CHANGELOG.md` - add section, move unreleased entries, update links
1.3. `pyproject.toml` - update build system `fallback-version`

### Task 2. Set Up and Validate

First, as needed:
cd examples/purl_authorities/drivers/js
and run before running drivers:

```shell
npm ci
```

Return to root project folder and run:

```pwsh
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\sit.ps1


uv lock
foreach ($v in '3.12','3.13','3.14','3.15') {
  Write-Host "=== Python $v"
  uv run --isolated --frozen --python $v --no-default-groups --group dev python -m pytest -q
}

uvx gha-tools autoupdate --pin=all --write .github/workflows

uvx zizmor@latest .github/
# suppressed and informational are okay

uvx cffconvert --validate
uvx se-manifest-schema validate-manifest --strict

uv run python -c "import shutil; from pathlib import Path; shutil.rmtree(Path('dist'), ignore_errors=True)"

uv build
uvx twine check --strict dist/*

uv run python -c "import pathlib, zipfile; wheels=list(pathlib.Path('dist').glob('*.whl')); assert wheels, 'No wheel found'; wheel=wheels[-1]; names=zipfile.ZipFile(wheel).namelist(); packaged=[n for n in names if n.startswith('se_identity_ops/')]; print(packaged); assert packaged, 'Package files missing from wheel'"
```

### Task 3. Git Add-Commit-Push, Then Tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

### Task 4. Verify the Release and Zenodo archive

The release-on-tag workflow publishes a GitHub Release
for MAJOR and MINOR tags only (vX.Y.0).
PATCH tags (vX.Y.Z, Z > 0) stay as tags.

To verify:

```shell
gh release view vX.Y.Z  # confirm Release exists with notes + artifacts
gh run list --workflow=release-pypi.yml   # confirm the workflow succeeded
```

If Zenodo archiving is enabled, confirm that the release has a
version-specific DOI and is linked to the repository's concept DOI.
Record the DOI in CITATION.cff only when it has been assigned and verified.

```shell
uvx --from se-manifest-schema se-manifest check-version --require-tag
```

Confirms CITATION.cff version matches the pushed git tag.
Run this after `git push origin vX.Y.Z`; it will fail before that point.

## Only As Needed (delete a tag)

```shell
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-identity-ops/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/structural-explainability/se-identity-ops/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
