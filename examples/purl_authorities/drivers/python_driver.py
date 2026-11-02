"""python_driver.py - Run packageurl-python on the corpus and print one JSON array.

WHAT: Reads corpus.csv (row, set_id, family, input). For each input it calls
      PackageURL.from_string and then to_string, and records the normalized string
      or the error text.
WHY: The first authority for the operation. The other two are independent
     implementations of the same specification.
HOW: python drivers/python_driver.py corpus.csv
OBS: This file adds no normalization rules of its own.
"""

import csv
import json
from pathlib import Path
import sys

from packageurl import PackageURL


def main() -> int:
    """Print one result per corpus row."""
    results = []
    with Path(sys.argv[1]).open(encoding="utf-8", newline="") as handle:
        for record in csv.DictReader(handle):
            try:
                output = PackageURL.from_string(record["input"]).to_string()
                results.append(
                    {"row": record["row"], "ok": True, "output": output, "error": ""}
                )
            except ValueError as error:
                results.append(
                    {
                        "row": record["row"],
                        "ok": False,
                        "output": "",
                        "error": str(error),
                    }
                )
    sys.stdout.write(json.dumps(results, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
