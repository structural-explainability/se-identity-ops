#Requires -Version 7.0

<#
============================================================
sit.ps1 (ALL-PY-SRC-REPOS)
============================================================
Updated: 2026-09-25

This is a PowerShell script for managing
the development environment of the project.

PowerShell (pwsh) is available for all major operating systems
and is a popular terminal for developers.

To get situated, run this script in your PowerShell terminal:

.\sit.ps1

As Needed:

Windows PowerShell ERROR: Execution Policy / Not Digitally Signed
When running a PowerShell script (.ps1) on Windows, you may see:

File cannot be loaded because it is not digitally signed.
You cannot run this script on the current system.

If you have reviewed the script and trust its source,
you can temporarily allow it to run in the current PowerShell session.

Run:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Then:

.\sit.ps1

#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# set up or update Python environment
uvx pup-clean --delete
uv self update
uv python install

# RESEARCH-FREEZE: do not run "uv lock --upgrade" in this repository.
# WHY: This is research software. The locked dependency versions are part of the
#      experimental record. Adapters name exact library versions in adapter.toml,
#      tests check them, and result files are reproduced byte for byte. An upgrade can
#      change a library's behavior or a result without any change to our own code.
# IF NEWER VERSIONS ARE NEEDED (for example, uv audit reports a vulnerability):
#   1. Make the change in its own commit and record WHY in CHANGELOG.md and DOUBTS.md.
#   2. Upgrade only what is needed: uv lock --upgrade-package NAME
#   3. Run uv sync, then the tests.
#   4. If an adapter library changed, update its version and digests in the
#      adapter.toml files. Do not edit or regenerate committed results; a rerun is a
#      new result and is recorded separately.
# uv lock --upgrade

uv sync
uv audit

# set up and run git hooks
uvx prek install --force
uvx prek update
git add -A
uvx prek run --all-files
# repeat if changes were made
uvx prek run --all-files

# run common chores
uv run ruff format .
uv run ruff check . --fix
uv run ty check
uv run python -m pytest
uv run python -m zensical build

Write-Host "All commands executed successfully."
Write-Host "Run a Python module to verify .venv/ is working correctly."
