"""extract_components.py - Read the authorized Freeze 01 validation cases into tables.

WHAT: Reads one SPDX source document and one CycloneDX target document and writes
      one row per component (source packages and target components).
WHY: IdentityOps programs read CSV tables. This script only reads fields; it does
     not decide anything about identity and does not call the pilot's evaluator.
HOW: python examples/sbom/extract_components.py --pilot PATH_TO_PILOT_CHECKOUT
OBS: Only the two authorized validation cases are read:
     validation/cyclonedx-cli-424 and validation/cyclonedx-cli-424-first-post.
     Nothing under generalization/ is opened.
OBS: Columns written:
       frame         stable row key, s01.. for source and t01.. for target
       role          source or target
       ref           SPDXID or bom-ref/name of the component
       name          component name
       anchor_hash   "sha256:<hex>" or empty when the component has no SHA-256
       original_purl   every PURL string as the document wrote it (slot, then properties)
       canonical_purl  PURLs in the format's canonical slot, as normalized by packageurl-python
       any_slot_purl   PURLs in the canonical slot or in any property value, normalized the same way
       purl_errors     library rejection messages, empty when every PURL parsed
OBS: ADAPTER: Package URL normalization is delegated to the reference library
     packageurl-python (PackageURL.from_string / to_string). This script does not
     define normalization rules. Its version is written to adapter.toml by
     record_adapter.py. Normalized-string equality is evidence for the PURL
     criterion only; it is not by itself a claim that two components are the same.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

from packageurl import PackageURL

CASES = {
    "known_bad": "cyclonedx-cli-424",
    "known_good": "cyclonedx-cli-424-first-post",
}


def normalize_purl(raw: str) -> tuple[str, str]:
    """Return (normalized PURL, error text) using the reference Package URL library.

    The library parses and re-serializes; this script adds no rules of its own.
    A string the library rejects yields an empty normalized form and the error text,
    so the rejection is recorded rather than silently repaired.
    """
    try:
        return PackageURL.from_string(raw).to_string(), ""
    except ValueError as error:
        return "", str(error)


def joined(purls: list[str]) -> str:
    """Return distinct library-normalized PURLs, sorted and joined by '|'."""
    return "|".join(sorted({normalize_purl(purl)[0] for purl in purls if purl} - {""}))


def originals(purls: list[str]) -> str:
    """Return the PURL strings exactly as the document wrote them, joined by '|'."""
    return "|".join(purl for purl in purls if purl)


def errors(purls: list[str]) -> str:
    """Return library rejection messages for the PURLs, joined by '|'."""
    return "|".join(
        message for purl in purls if purl and (message := normalize_purl(purl)[1])
    )


def source_rows(document: dict) -> list[dict[str, str]]:
    """Return one row per SPDX package."""
    rows = []
    for number, package in enumerate(document["packages"], start=1):
        checksums = [
            item["checksumValue"]
            for item in package.get("checksums", [])
            if item.get("algorithm") == "SHA256"
        ]
        purls = [
            ref["referenceLocator"]
            for ref in package.get("externalRefs", [])
            if ref.get("referenceCategory") == "PACKAGE-MANAGER"
            and ref.get("referenceType") == "purl"
        ]
        rows.append(
            {
                "frame": f"s{number:02d}",
                "role": "source",
                "ref": package["SPDXID"],
                "name": package["name"],
                "anchor_hash": f"sha256:{checksums[0]}" if checksums else "",
                "original_purl": originals(purls),
                "canonical_purl": joined(purls),
                "any_slot_purl": joined(purls),
                "purl_errors": errors(purls),
            }
        )
    return rows


def target_rows(document: dict) -> list[dict[str, str]]:
    """Return one row per CycloneDX component."""
    rows = []
    for number, component in enumerate(document["components"], start=1):
        hashes = [
            item["content"]
            for item in component.get("hashes", [])
            if item.get("alg") == "SHA-256"
        ]
        slot = [component["purl"]] if component.get("purl") else []
        elsewhere = [
            prop["value"]
            for prop in component.get("properties", [])
            if str(prop.get("value", "")).startswith("pkg:")
        ]
        rows.append(
            {
                "frame": f"t{number:02d}",
                "role": "target",
                "ref": component.get("bom-ref", component["name"]),
                "name": component["name"],
                "anchor_hash": f"sha256:{hashes[0]}" if hashes else "",
                "original_purl": originals(slot + elsewhere),
                "canonical_purl": joined(slot),
                "any_slot_purl": joined(slot + elsewhere),
                "purl_errors": errors(slot + elsewhere),
            }
        )
    return rows


def main() -> int:
    """Write one table per authorized case."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pilot", type=Path, required=True, help="checkout of the SBOM pilot repo"
    )
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "data")
    args = parser.parse_args()
    validation = args.pilot / "validation"
    source_path = validation / CASES["known_bad"] / "source.spdx.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    header = [
        "frame",
        "role",
        "ref",
        "name",
        "anchor_hash",
        "original_purl",
        "canonical_purl",
        "any_slot_purl",
        "purl_errors",
    ]
    for case, folder in CASES.items():
        target_path = validation / folder / "target.cdx.json"
        target = json.loads(target_path.read_text(encoding="utf-8"))
        rows = source_rows(source) + target_rows(target)
        out_path = args.output / f"components_{case}.csv"
        with out_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
        sys.stdout.write(f"{out_path.name} rows={len(rows)} sha256={digest}\n")
        sys.stdout.write(
            f"  target {folder}/target.cdx.json sha256={hashlib.sha256(target_path.read_bytes()).hexdigest()}\n"
        )
    sys.stdout.write(
        f"  source sha256={hashlib.sha256(source_path.read_bytes()).hexdigest()}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
