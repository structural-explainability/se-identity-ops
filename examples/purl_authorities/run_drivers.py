"""run_drivers.py - Run three Package URL implementations on the corpus and write tables.

WHAT: Runs packageurl-python, packageurl-js and packageurl-go on corpus.csv, then
      writes data/purl_authorities.csv (the table the IdentityOps program reads)
      and results/implementations.json (raw outputs, errors, and versions).
WHY: The IdentityOps program is fixed. Only the adapter changes. This script is the
     adapter layer: it calls each implementation and records what it returned.
HOW: python examples/purl_authorities/run_drivers.py
OBS: No normalization rules are defined here. A rejected input is recorded with a
     marker value so that rejection is visible and never silently repaired:
       <impl>_norm  rejected inputs are written REJECTED:<set_id>, so two rejected
                    spellings of one set agree with each other
       <impl>_row   rejected inputs are written REJECTED:<row>, so a rejected input
                    is never related to anything by that implementation
       <impl>_valid accepted or rejected (used only by the post hoc validity program)
OBS: Needs node and go on PATH, and `npm ci` run in drivers/js beforehand.
"""

import csv
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).parent
CORPUS = HERE / "corpus.csv"
IMPLEMENTATIONS = ("py", "js", "go")


def run_json(command: list[str], cwd: Path) -> list[dict]:
    """Run a driver and return its parsed JSON output."""
    environment = {
        **os.environ,
        "GOFLAGS": "-mod=mod",
        "GOSUMDB": "off",
        "GOPROXY": "off",
    }
    completed = subprocess.run(
        command, cwd=cwd, env=environment, capture_output=True, text=True, check=True
    )
    return json.loads(completed.stdout)


def versions() -> dict[str, str]:
    """Return the exact versions of the three implementations."""
    js_package = json.loads(
        (HERE / "drivers/js/node_modules/packageurl-js/package.json").read_text(
            encoding="utf-8"
        )
    )
    go_mod = (HERE / "drivers/go/go.mod").read_text(encoding="utf-8")
    go_version = next(
        line.split()[2] if line.startswith("require") else line.split()[1]
        for line in go_mod.splitlines()
        if "packageurl-go" in line
    )
    return {
        "py": f"packageurl-python {version('packageurl-python')}",
        "js": f"packageurl-js {js_package['version']}",
        "go": f"packageurl-go {go_version}",
    }


def main() -> int:
    """Write the table and the raw results."""
    raw = {
        "py": run_json(
            [sys.executable, str(HERE / "drivers/python_driver.py"), str(CORPUS)], HERE
        ),
        "js": run_json(["node", "driver.mjs", str(CORPUS)], HERE / "drivers/js"),
        "go": run_json(["go", "run", ".", str(CORPUS)], HERE / "drivers/go"),
    }
    with CORPUS.open(encoding="utf-8", newline="") as handle:
        corpus = list(csv.DictReader(handle))
    by_row = {
        name: {item["row"]: item for item in items} for name, items in raw.items()
    }
    header = ["row", "set_id", "family", "input"]
    header += [f"{name}_norm" for name in IMPLEMENTATIONS]
    header += [f"{name}_row" for name in IMPLEMENTATIONS]
    header += [f"{name}_valid" for name in IMPLEMENTATIONS]
    rows = []
    for record in corpus:
        line = dict(record)
        for name in IMPLEMENTATIONS:
            result = by_row[name][record["row"]]
            line[f"{name}_norm"] = (
                result["output"] if result["ok"] else f"REJECTED:{record['set_id']}"
            )
            line[f"{name}_row"] = (
                result["output"] if result["ok"] else f"REJECTED:{record['row']}"
            )
            line[f"{name}_valid"] = "accepted" if result["ok"] else "rejected"
        rows.append(line)
    (HERE / "data").mkdir(exist_ok=True)
    (HERE / "results").mkdir(exist_ok=True)
    with (HERE / "data/purl_authorities.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "versions": versions(),
        "results": [
            {
                "row": record["row"],
                "input": record["input"],
                **{
                    name: {
                        "ok": by_row[name][record["row"]]["ok"],
                        "output": by_row[name][record["row"]]["output"],
                        "error": by_row[name][record["row"]]["error"],
                    }
                    for name in IMPLEMENTATIONS
                },
            }
            for record in corpus
        ],
    }
    (HERE / "results/implementations.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sys.stdout.write(f"wrote {len(rows)} rows; versions {report['versions']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
