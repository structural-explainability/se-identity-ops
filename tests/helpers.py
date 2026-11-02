"""helpers.py - Build and run small programs for tests.

WHAT: Writes CSV source files to a temporary folder, fills in their SHA-256
      digests, parses the program, and runs it.
WHY: Every test then exercises the same path a real program uses.
"""

import csv
import hashlib
from pathlib import Path

from se_identity_ops import Run, parse, run_program


def write_table(
    folder: Path, name: str, header: list[str], rows: list[list[str]]
) -> str:
    """Write a CSV file and return its SHA-256 digest."""
    path = folder / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_text(
    folder: Path,
    body: str,
    tables: dict[str, tuple[list[str], list[list[str]]]] | None = None,
) -> Run:
    """Run program text, replacing `@SHA:name@` with the digest of table `name`."""
    text = body
    for name, (header, rows) in (tables or {}).items():
        digest = write_table(folder, name, header, rows)
        text = text.replace(f"@SHA:{name}@", digest)
    return run_program(parse(text, "test.ido"), folder)


VENDORS = (
    ["row", "vid", "name"],
    [
        ["r1", "V1", "acme"],
        ["r2", "V2", "acme"],
        ["r3", "V1", "acme corp"],
        ["r4", "", "zed"],
        ["r5", "V3", "zed"],
        ["r6", "V4", "solo"],
    ],
)

VENDOR_PRELUDE = """
source s file "vendors.csv" sha256 "@SHA:vendors@"
carrier recs from s key "row"
regime reg on recs by "vid" source s meaning "registration-level, not legal-entity"
surface norm on recs column "name" source s
probe seen on recs column "name" source s
"""
