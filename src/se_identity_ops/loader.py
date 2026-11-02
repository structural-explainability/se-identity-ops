"""loader.py - Load source tables and verify their digests.

WHAT: Reads a CSV file named by a `source` declaration and checks its SHA-256.
WHY: Every observation and criterion in a program must trace to bytes that can
     be re-checked. A digest mismatch stops the run before any result exists.
OBS: Files are read as UTF-8 with the standard `csv` module. The first row names
     the columns. Values are kept as text; no value is converted or trimmed.
"""

import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path

from .syntax import SourceDecl


class SourceError(Exception):
    """Raised when a source file is missing, altered, or malformed."""


@dataclass(frozen=True, slots=True)
class Table:
    """A loaded source table.

    Attributes:
        name: Source name.
        path: Resolved file path.
        sha256: Verified lowercase hex digest.
        columns: Column names in file order.
        rows: Row values in file order, each row a tuple matching `columns`.
    """

    name: str
    path: Path
    sha256: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def column(self, name: str) -> tuple[str, ...]:
        """Return all values of one column in row order.

        Raises:
            SourceError: If the column does not exist.
        """
        if name not in self.columns:
            raise SourceError(f"source '{self.name}' has no column '{name}'")
        position = self.columns.index(name)
        return tuple(row[position] for row in self.rows)


def file_sha256(path: Path) -> str:
    """Return the lowercase hex SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_table(decl: SourceDecl, base_dir: Path) -> Table:
    """Load and verify one source file.

    Args:
        decl: The source declaration.
        base_dir: Directory the declared path is relative to.

    Returns:
        The loaded table.

    Raises:
        SourceError: If the file is missing, its digest differs, or a row has the
            wrong number of values.
    """
    path = (base_dir / decl.file).resolve()
    if not path.is_file():
        raise SourceError(f"line {decl.line}: source file not found: {decl.file}")
    actual = file_sha256(path)
    if actual != decl.sha256:
        raise SourceError(
            f"line {decl.line}: sha256 of {decl.file} is {actual}, program declares {decl.sha256}"
        )
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = tuple(next(reader))
        except StopIteration:
            raise SourceError(
                f"line {decl.line}: source file is empty: {decl.file}"
            ) from None
        rows: list[tuple[str, ...]] = []
        for number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise SourceError(
                    f"{decl.file} row {number} has {len(row)} values, expected {len(header)}"
                )
            rows.append(tuple(row))
    return Table(decl.name, path, actual, header, tuple(rows))
