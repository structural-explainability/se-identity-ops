"""prepare_observations.py - Record the US-IL localization mechanism's output.

WHAT: Reads the Chicago vendor sample, runs every Vendor Name through the
      compiled harness (the Civic Interconnect US-IL localization function),
      and writes one observation row per input row.

WHY: IdentityOps audits recorded behavior of an existing mechanism. This script
     records that behavior. It does not implement any normalization rule.

HOW: Build the harness (see harness/Cargo.toml), then run:

     python examples/chicago/prepare_observations.py \
         --sample path/to/chicago_contracts_vendors_sample_20k.csv \
         --harness path/to/cep-harness \
         --output examples/chicago/data/vendors_20k_observed.csv

OBS: Row keys are r00001, r00002, ... in input order, so every observation can
     be traced to its input row.
OBS: The recorded output file and its SHA-256 are committed. Re-running needs
     the Rust toolchain and the upstream checkout, and is not part of CI.
"""

import argparse
import csv
import hashlib
from pathlib import Path
import subprocess
import sys


def sha256_of(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    """Run the harness over the sample and write the observation file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.sample.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    names = [row["Vendor Name"] for row in rows]
    for name in names:
        if "\n" in name or "\r" in name:
            sys.stderr.write(
                "A vendor name contains a line break; the harness is line based.\n"
            )
            return 1

    completed = subprocess.run(
        [str(args.harness)],
        input="\n".join(names) + "\n",
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    outputs = completed.stdout.split("\n")[:-1]
    if len(outputs) != len(rows):
        sys.stderr.write(f"Expected {len(rows)} outputs, got {len(outputs)}.\n")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["row", "vendor_id", "vendor_name", "localized_name"])
        for index, (row, localized) in enumerate(
            zip(rows, outputs, strict=True), start=1
        ):
            writer.writerow(
                [f"r{index:05d}", row["Vendor ID"], row["Vendor Name"], localized]
            )

    sys.stdout.write(f"sample sha256: {sha256_of(args.sample)}\n")
    sys.stdout.write(f"output sha256: {sha256_of(args.output)}\n")
    sys.stdout.write(f"rows: {len(rows)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
