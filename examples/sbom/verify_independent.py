"""verify_independent.py - Check Experiment B against the pilot's own recorded results.

WHAT: Re-reads the authorized SPDX and CycloneDX documents directly, decides for
      each hash-anchored component whether its PURL is in the target's canonical
      slot, relocated to a property, or missing, and compares that decision with
      (a) the pilot's recorded evaluator result.json and (b) the IdentityOps run.
WHY: The IdentityOps run should agree with an independent reading of the same
     bytes and with the pilot's recorded adjudication, or the disagreement
     should be visible.
HOW: python examples/sbom/verify_independent.py --pilot PATH_TO_PILOT_CHECKOUT
OBS: Imports nothing from se_identity_ops and does not run the pilot's evaluator.
     It reads the pilot's recorded result.json files.
OBS: It records, without judging them, the digests declared in each case's
     metadata.toml next to the digests of the files actually read.
OBS: Nothing under generalization/ is opened.
OBS: Independent of the IdentityOps interpreter, not of the Package URL library:
     both this script and extract_components.py delegate PURL normalization to
     packageurl-python, so the library is a shared external authority here.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tomllib

from packageurl import PackageURL

HERE = Path(__file__).parent
CASES = {
    "known_bad": ("cyclonedx-cli-424", "cyclonedx-cli-424"),
    "known_good": ("cyclonedx-cli-424-first-post", "cyclonedx-cli-424-first-post"),
}


def canonical(purl: str) -> str:
    """Return the Package URL normalized by the reference library packageurl-python."""
    return PackageURL.from_string(purl).to_string()


def sha256_of(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_source(path: Path) -> list[dict[str, str]]:
    """Return hash-anchored SPDX packages with their PURLs, in package order."""
    document = json.loads(path.read_text(encoding="utf-8"))
    found = []
    for number, package in enumerate(document["packages"], start=1):
        hashes = [
            c["checksumValue"]
            for c in package.get("checksums", [])
            if c["algorithm"] == "SHA256"
        ]
        purls = [
            r["referenceLocator"]
            for r in package.get("externalRefs", [])
            if r.get("referenceCategory") == "PACKAGE-MANAGER"
            and r.get("referenceType") == "purl"
        ]
        found.append(
            {
                "frame": f"s{number:02d}",
                "ref": package["SPDXID"],
                "hash": hashes[0] if hashes else "",
                "purl": canonical(purls[0]) if purls else "",
            }
        )
    return found


def read_target(path: Path) -> list[dict[str, str]]:
    """Return CycloneDX components with canonical-slot and property PURLs, in order."""
    document = json.loads(path.read_text(encoding="utf-8"))
    found = []
    for number, component in enumerate(document["components"], start=1):
        hashes = [
            h["content"] for h in component.get("hashes", []) if h["alg"] == "SHA-256"
        ]
        properties = [
            canonical(p["value"])
            for p in component.get("properties", [])
            if str(p.get("value", "")).startswith("pkg:")
        ]
        found.append(
            {
                "frame": f"t{number:02d}",
                "hash": hashes[0] if hashes else "",
                "slot": canonical(component["purl"]) if component.get("purl") else "",
                "properties": "|".join(sorted(properties)),
            }
        )
    return found


def decide(source: dict[str, str], targets: list[dict[str, str]]) -> dict[str, str]:
    """Decide where a source PURL ended up in the anchored target component."""
    matches = [t for t in targets if t["hash"] and t["hash"] == source["hash"]]
    if len(matches) != 1:
        return {"decision": "unanchorable", "target_frame": ""}
    target = matches[0]
    if target["slot"] == source["purl"]:
        decision = "preserved"
    elif source["purl"] in target["properties"].split("|"):
        decision = "relocated"
    else:
        decision = "missing"
    return {"decision": decision, "target_frame": target["frame"]}


EVALUATOR_TO_DECISION = {"PRESERVED": "preserved", "VIOLATED_RELOCATED": "relocated"}


def main() -> int:
    """Compare the interpreter output, an independent reading, and the pilot's record."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, required=True)
    args = parser.parse_args()
    validation = args.pilot / "validation"
    source_path = validation / "cyclonedx-cli-424" / "source.spdx.json"
    sources = read_source(source_path)
    report: dict[str, object] = {"cases": {}}
    ok = True
    for case, (folder, _unused) in CASES.items():
        target_path = validation / folder / "target.cdx.json"
        targets = read_target(target_path)
        recorded = json.loads(
            (validation / folder / "result.json").read_text(encoding="utf-8")
        )["results"]
        verdict_by_ref = {entry["ref"]: entry["verdict"] for entry in recorded}
        metadata = tomllib.loads(
            (validation / folder / "metadata.toml").read_text(encoding="utf-8")
        )
        run = json.loads(
            (HERE / "results" / f"{case}.json").read_text(encoding="utf-8")
        )
        canonical_result = next(
            r
            for r in run["results"]
            if r["label"] == "b_canonical" and r["operation"] == "check"
        )
        any_slot_result = next(
            r
            for r in run["results"]
            if r["label"] == "b_any_slot" and r["operation"] == "check"
        )
        witness = canonical_result["explanation"]["witness"]
        diverging_sources = {
            witness[name]
            for name in witness
            if name.endswith(".first") and name.startswith("example_")
        }
        rows = []
        for source in sources:
            if not source["hash"]:
                continue
            decision = decide(source, targets)
            interpreter_split = source["frame"] in diverging_sources
            evaluator = verdict_by_ref.get(source["ref"], "absent")
            consistent = EVALUATOR_TO_DECISION.get(evaluator) == decision[
                "decision"
            ] and interpreter_split == (decision["decision"] != "preserved")
            ok = ok and consistent
            rows.append(
                {
                    "source_frame": source["frame"],
                    "independent_decision": decision["decision"],
                    "pilot_recorded_verdict": evaluator,
                    "interpreter_canonical_probe_splits_pair": interpreter_split,
                    "agree": consistent,
                }
            )
        declared_target = metadata.get("target", {}).get("sha256", "")
        declared_source = metadata.get("source", {}).get("sha256", "")
        report["cases"][case] = {  # type: ignore[index]
            "components": rows,
            "any_slot_outcome": f"{any_slot_result['outcome']}/{any_slot_result['word']}",
            "digests": {
                "source_declared": declared_source.lower(),
                "source_actual": sha256_of(source_path),
                "target_declared": declared_target.lower(),
                "target_actual": sha256_of(target_path),
                "target_matches_declared": declared_target.lower()
                == sha256_of(target_path),
            },
        }
    report["all_agree"] = ok
    out = HERE / "results" / "independent_verification.json"
    out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for case, body in report["cases"].items():  # type: ignore[union-attr]
        for row in body["components"]:
            sys.stdout.write(
                f"{case:11} {row['source_frame']} {row['independent_decision']:10} pilot={row['pilot_recorded_verdict']:20} agree={row['agree']}\n"
            )
        digests = body["digests"]
        sys.stdout.write(
            f"{case:11} target digest matches metadata.toml: {digests['target_matches_declared']}\n"
        )
    sys.stdout.write(f"all agree: {ok}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
