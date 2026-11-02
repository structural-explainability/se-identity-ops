#Requires -Version 7.3

<#
=================================
rel.ps1 (SE-IDENTITY-OPS: adapted from ALL SE LEAN REPOS)
=================================
Updated: 2026-11-02

WHAT: Run the repository Lean release-validation sequence.
WHEN: Before tagging a release, and after changing any Lean file, lakefile.toml,
      lean-toolchain, CITATION.cff, SE_MANIFEST.toml, or Markdown.
WHY: Confirms the Lean core builds with warnings as failures, its tests run, no
     axiom or native_decide is introduced, and the repository files validate.
HOW: Run from the repository root in PowerShell 7.3 or later:

     .\rel.ps1

TOOLS: elan, lake, uvx (cffconvert, se-manifest-schema), npx (markdownlint-cli2).
SKILLS: Lean 4, Lake, release validation, PowerShell.
OBS: It does not build or publish the Python package. Python checks are in sit.ps1
     and in pytest.
OBS: Pre-checks: .github/workflows/ci-lean.yml. This script runs the same commands.
OBS: Adapted from se-theory-persistence/rel.ps1. Omitted because this repository has
     no reference/ folder, no lint/ folder, and no generated data/ artifacts:
     the Batteries lint step and the theory-reference export and validation steps (E, F).
OBS: This repository depends on se-theory-persistence, which shares the SE module
     root, so leanchecker and axiom-audit cannot resolve the modules (step C).
     The source scan runs instead, as in ci-lean.yml.
OBS: #Requires 7.3 because $PSNativeCommandUseErrorActionPreference needs it.
CUSTOM: Update the axiom-audit tag together with ci-lean.yml.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

# Axiom audit repository configuration
# To update the tool later:
# 1. Change the tag below; C2 re-clones when the checked-out tag differs.
# 2. Update ci-lean.yml as needed.
$AxiomAuditURL = "https://github.com/leanprover-community/axiom-audit.git"
$AxiomAuditBranch = "v0.1.2"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Section,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Script,

        [int[]]$AllowedExitCodes = @(0)
    )

    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Section
    Write-Host "============================================================"
    Write-Host $Command

    $allowsNonzeroExit = @(
        $AllowedExitCodes | Where-Object { $_ -ne 0 }
    ).Count -gt 0

    if (-not $allowsNonzeroExit) {
        # WHY: Preserve normal fail-fast behavior for strict steps.
        & $Script
        return
    }

    $oldNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
    $exitCode = 0

    try {
        # WHY: Explicitly advisory steps may report findings without stopping
        # the release-validation sequence.
        $PSNativeCommandUseErrorActionPreference = $false

        & $Script
        $exitCode = $LASTEXITCODE
    }
    finally {
        $PSNativeCommandUseErrorActionPreference = $oldNativeErrorPreference
    }

    if ($exitCode -notin $AllowedExitCodes) {
        throw "$Section failed with exit code $exitCode."
    }

    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "Command reported findings with allowed exit code $exitCode."
        Write-Host "Release validation will continue."
    }
}

# ============================================================
# === A) Update environment ===
# ============================================================

Invoke-Step "A0) Update elan" "elan self update" {
    elan self update
    elan --version
}

Invoke-Step "A1) Update Lean dependencies" "lake update" {
    lake update
}

Invoke-Step "A2) Lean and lake versions" "lean --version; lake --version" {
    lean --version
    lake --version
}

Invoke-Step "A3) Clean Lean build output" "lake clean" {
    # WHY: Remove stale .olean files from renamed or deleted modules and from
    #      older toolchains. Otherwise leanchecker (C1) can fail on an orphaned
    #      file with "incompatible header".
    lake clean
}

# ============================================================
# === B) Lean build and tests ===
# ============================================================

Invoke-Step "B1) Build Lean library" "lake build --wfail" {
    lake build --wfail
}

Invoke-Step "B2) Run Lean tests" "lake test" {
    lake test
}

# ============================================================
# === C) Check lean and SE project files ===
# ============================================================

$packagesDir = Join-Path $PSScriptRoot ".lake\packages"
$hasSeDependencies = $false

if (Test-Path -LiteralPath $packagesDir) {
    $seDependencies = @(Get-ChildItem -LiteralPath $packagesDir -Directory -Filter "se-theory-*")
    $hasSeDependencies = $seDependencies.Count -gt 0
}

Invoke-Step "C1) Run Lean env checker" "lake env leanchecker SE SETest" {
    if ($hasSeDependencies) {
        Write-Host "SKIPPED: this repo depends on other SE theory packages that share the SE module root; leanchecker cannot resolve their modules."
        return
    }

    lake env leanchecker SE SETest
}

Invoke-Step `
    "C2) Audit axioms" `
    "axiom-audit --allow propext,Classical.choice,Quot.sound" {
    # WHY: Same axiom-audit tag that the pinned lean-action runs in ci-lean.yml C2.
    #      Update both together.
    if ($hasSeDependencies) {
        Write-Host "This repo depends on other SE theory packages that share the SE module root; axiom-audit cannot resolve their modules."
        Write-Host "Falling back to a source scan for axiom declarations and native_decide."

        $scanRoots = @(
            @(
                (Join-Path $PSScriptRoot "SE")
                (Join-Path $PSScriptRoot "SETest")
            ) | Where-Object { Test-Path -LiteralPath $_ }
        )

        if ($scanRoots.Count -eq 0) {
            Write-Host "No SE or SETest folder found to scan."
            return
        }

        $hits = @(
            Get-ChildItem -LiteralPath $scanRoots -Filter "*.lean" -File -Recurse |
                Select-String -CaseSensitive -Pattern '^\s*(?:(?:public|private|protected|noncomputable)\s+)*axiom\b|native_decide'
        )

        if ($hits.Count -gt 0) {
            foreach ($hit in $hits) {
                Write-Host "$($hit.Path):$($hit.LineNumber): $($hit.Line.Trim())"
            }
            throw "Found axiom declarations or native_decide in source."
        }

        Write-Host "No axiom declarations or native_decide found in SE and SETest source."
        return
    }

    $auditDir = Join-Path $PSScriptRoot ".lake\axiom-audit"

    # WHY: Re-clone when the checked-out tag is not the pinned tag, so changing
    #      $AxiomAuditBranch cannot leave a stale audit tool in place.
    if (Test-Path -LiteralPath $auditDir) {
        $currentTags = @(git -C $auditDir tag --points-at HEAD)
        if ($currentTags -notcontains $AxiomAuditBranch) {
            Remove-Item -LiteralPath $auditDir -Recurse -Force
        }
    }

    if (-not (Test-Path -LiteralPath $auditDir)) {
        git -c advice.detachedHead=false clone --depth 1 --branch $AxiomAuditBranch $AxiomAuditURL $auditDir
    }

    Copy-Item `
        -LiteralPath (Join-Path $PSScriptRoot "lean-toolchain") `
        -Destination (Join-Path $auditDir "lean-toolchain") `
        -Force

    Push-Location $auditDir
    try {
        lake build
    }
    finally {
        Pop-Location
    }

    lake env (Join-Path $auditDir ".lake\build\bin\axiom-audit.exe") --allow propext,Classical.choice,Quot.sound
}

# ============================================================
# === D) DO SE PROJECT CHECKS ===
# ============================================================

Invoke-Step "D1) Validate CITATION.cff" "uvx cffconvert --validate" {
    uvx cffconvert --validate
}

Invoke-Step "D2) Validate SE manifest" "uvx se-manifest-schema validate-manifest --strict" {
    uvx se-manifest-schema validate-manifest --strict
}

Invoke-Step "D3) Check Markdown with markdownlint" "npx markdownlint-cli2" {
    npx markdownlint-cli2
}

# ============================================================
# === R) Repository status ===
# ============================================================

Invoke-Step "R1) Show repository status" "git status --short" {
    git status --short
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Repository validation completed successfully."
Write-Host "============================================================"
