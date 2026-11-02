"""cli.py - Command line entry point.

WHAT: `se-identity-ops check FILE` runs static checks. `se-identity-ops run FILE`
      executes a program and prints one line per operation. `--json PATH` also
      writes the complete result as deterministic JSON.
WHY: Experiments must be re-runnable by one command that writes a result file.
OBS: Exit code 0 means the program ran. It does not mean any check was satisfied.
     A refuted or undetermined check is a result, not an error.
"""

import argparse
import json
from pathlib import Path
import sys

from .checker import check_program
from .interpreter import RunError, run_program
from .parser import ParseError, parse


def _read_program(path: Path):  # noqa: ANN202
    """Parse a program file."""
    return parse(path.read_text(encoding="utf-8"), path.name)


def main(argv: list[str] | None = None) -> int:
    """Run the command line tool.

    Args:
        argv: Arguments after the program name; defaults to `sys.argv[1:]`.

    Returns:
        Process exit code: 0 on success, 1 on a parse, check, or run error.
    """
    parser = argparse.ArgumentParser(prog="se-identity-ops", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check_command = commands.add_parser("check", help="parse and check a program")
    check_command.add_argument("file", type=Path)
    run_command = commands.add_parser("run", help="execute a program")
    run_command.add_argument("file", type=Path)
    run_command.add_argument("--json", type=Path, default=None, help="write full results here")
    args = parser.parse_args(argv)

    try:
        program = _read_program(args.file)
    except ParseError as error:
        sys.stderr.write(f"{args.file}: {error}\n")
        return 1
    diagnostics = check_program(program)
    if diagnostics:
        for diagnostic in diagnostics:
            sys.stderr.write(f"{args.file}: {diagnostic}\n")
        return 1
    if args.command == "check":
        sys.stdout.write(f"{args.file}: {len(program.statements)} statements, no diagnostics\n")
        return 0
    try:
        run = run_program(program, args.file.resolve().parent)
    except RunError as error:
        sys.stderr.write(f"{args.file}: {error}\n")
        return 1
    for result in run.results:
        sys.stdout.write(f"{result.operation:8} {result.label:24} {result.outcome.value:12} {result.word}\n")
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(run.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
