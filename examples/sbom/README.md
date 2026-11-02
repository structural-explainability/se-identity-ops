# Experiment B: SBOM and PURL Identity

## Question

For components anchored by content hash, does a converted SBOM keep the PURL in the
canonical slot, and if not, is it present anywhere in the target?

## Evidence Role

**Engineering validation.** Both cases were known when the pilot was designed, so
reproducing them is not evidence of generalization. This run shows that the language
can express the frozen commitment's consequences on these two documents. It does not
show that the language generalizes and it does not find anything the pilot had not
already found.

## Inputs and Boundary

Read from `structural-explainability/se-pilot-identity-preservation-supply-chain-software`
at commit `f9c676ba79b1fec1fe78dba015103998dd0193c7`:

- `validation/cyclonedx-cli-424/source.spdx.json`, the SPDX source;
- `validation/cyclonedx-cli-424/target.cdx.json`, the known-bad conversion (cyclonedx-cli
  0.31.0);
- `validation/cyclonedx-cli-424-first-post/target.cdx.json`, the known-good conversion
  (0.32.0);
- the pilot's recorded `result.json` for each case, for comparison.

**Not opened:** anything under `generalization/`, any Freeze 02 material, and the
vulnerability-matching registered-report study. Freeze 02 is a later boundary; no
output examined here is a Freeze 02 generalization output. This work does not modify
the pilot.

`extract_components.py` reads those fields into the two tables under `data/`. It does
not run or reimplement the pilot's evaluator.

**PURL normalization is not defined here.** It is delegated to the reference library
`packageurl-python` (`PackageURL.from_string(raw).to_string()`), recorded with its
version and digests in [`adapter.toml`](./adapter.toml). Each row keeps the PURL strings
as the document wrote them (`original_purl`), the library's normalized form
(`canonical_purl`, `any_slot_purl`), and any library rejection (`purl_errors`). An
earlier script-local canonicalizer was replaced; on all 9 PURL occurrences in these two
cases it gave identical output, so no outcome changed. Equal normalized strings are
evidence for the PURL criterion, not a claim that two components are the same.

## Declared Criterion

`component_anchor`: a source package and a target component are the same component
when they share a SHA-256 content hash (the frozen commitment's anchor). A component
with no hash is **unanchored**; the criterion is silent about it.

## Results

- **Known-bad.** Under the canonical slot (`component.purl`) the anchored pair is split
  for 3 components (`base-files`, `netbase`, `tzdata`). Reading any slot (including
  property values), no pair is split. This is the pilot's relocated shape.
- **Known-good.** Neither probe splits any anchored pair.
- **Coverage.** 8 of 14 frames have no hash (4 source packages, 4 target components),
  so the criterion is silent about them: `undetermined`, `partial`.
- **Controls.** All as expected: the anchor value as a probe is faithful; the frame role
  splits every anchored pair.

All ten expectations were met and both relations held.

## Comparison With the Pilot's Record

[`verify_independent.py`](./verify_independent.py) re-reads the documents directly and
decides, for each hash-anchored source package, whether its PURL is in the target's
canonical slot, in a property, or missing. It compares that decision with the pilot's
recorded verdict (`VIOLATED_RELOCATED` or `PRESERVED`) and with the IdentityOps run.
All six pairs agree.

The pilot's vocabulary is richer than IdentityOps' two probes: dropped, altered,
unsupported, underdetermined, and unanchorable have no equivalent here. The pilot's
`NOT_APPLICABLE` (the source has no PURL) and IdentityOps' unanchored (no hash)
coincide on these documents but are different notions.

## An Observation About the Inputs

In the clone at that commit, the SHA-256 recorded in `metadata.toml` for each case's
`target.cdx.json` does not match the file's actual digest, before or after converting
line endings. The source file's digest matches. The pilot's tests check recorded
hashes only for the release and reverse sweeps. This is recorded as a doubt, not
resolved. IdentityOps pins the digest of the bytes it read.

## What This Does Not Show

- Nothing about Freeze 02 or any generalization claim.
- Anything about the PURL specification beyond what the library does on these inputs (nine `pkg:deb` PURLs).
- That IdentityOps handles qualifiers, namespaces, or other formats.
