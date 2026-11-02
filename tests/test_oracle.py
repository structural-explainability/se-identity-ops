"""Exhaustive small-state comparison with an independent oracle.

The oracle follows the semantic definitions in `se-theory-persistence` directly:
it enumerates every equivalence relation on a small carrier, keeps the admissible
ones (containing every same-pair, containing no distinct pair), and reads the
status of a pair off that set:

- required: every admissible relation identifies the pair;
- forbidden: every admissible relation separates the pair;
- undetermined: some do and some do not;
- inconsistent: there is no admissible relation.

The interpreter computes statuses by closure (union-find). This test compares the
two on every assignment of {none, same, distinct} to every pair, for carriers of
size 3 and 4, and on a fixed pseudo-random sample for sizes 5 and 6. It shows
agreement on those carriers. It is not a proof for all carriers.
"""

from itertools import combinations, product
from pathlib import Path
import random

from se_identity_ops import parse, run_program
from se_identity_ops.relation import DistinctPair, Relation, SamePair

from .helpers import write_table


def set_partitions(size: int) -> list[tuple[int, ...]]:
    """Return every equivalence relation on range(size) as block numbers (restricted growth)."""
    found: list[tuple[int, ...]] = []

    def extend(prefix: tuple[int, ...], blocks: int) -> None:
        if len(prefix) == size:
            found.append(prefix)
            return
        for block in range(blocks + 1):
            extend((*prefix, block), max(blocks, block + 1))

    extend((), 0)
    return found


def oracle_status(
    partitions: list[tuple[int, ...]],
    same: list[tuple[int, int]],
    distinct: list[tuple[int, int]],
    x: int,
    y: int,
) -> str:
    """Return the status of (x, y) by enumeration."""
    admissible = [
        blocks
        for blocks in partitions
        if all(blocks[a] == blocks[b] for a, b in same)
        and all(blocks[a] != blocks[b] for a, b in distinct)
    ]
    if not admissible:
        return "inconsistent"
    if all(blocks[x] == blocks[y] for blocks in admissible):
        return "required"
    if all(blocks[x] != blocks[y] for blocks in admissible):
        return "forbidden"
    return "undetermined"


def closure_status(
    names: tuple[str, ...], same: list[tuple[int, int]], distinct: list[tuple[int, int]], x: int, y: int
) -> str:
    """Return the status of (x, y) from the interpreter's relation code."""
    relation = Relation(
        names,
        None,
        "",
        tuple(SamePair(names[a], names[b], "judgment", f"s{a}{b}", "") for a, b in same),
        tuple(DistinctPair(names[a], names[b], f"d{a}{b}", "") for a, b in distinct),
    )
    return relation.status(names[x], names[y])


def assignments_all(size: int) -> list[tuple[list[tuple[int, int]], list[tuple[int, int]]]]:
    """Return every (same, distinct) assignment over the pairs of a carrier."""
    pairs = list(combinations(range(size), 2))
    out = []
    for choice in product((0, 1, 2), repeat=len(pairs)):
        same = [pair for pair, mark in zip(pairs, choice, strict=True) if mark == 1]
        distinct = [pair for pair, mark in zip(pairs, choice, strict=True) if mark == 2]
        out.append((same, distinct))
    return out


def check_size(size: int, sample: int | None) -> int:
    """Compare oracle and closure on a carrier; return the number of comparisons."""
    names = tuple(f"i{n}" for n in range(size))
    partitions = set_partitions(size)
    pairs = list(combinations(range(size), 2))
    cases = assignments_all(size) if sample is None else None
    if cases is None:
        generator = random.Random(20261102)
        cases = []
        for _ in range(sample or 0):
            choice = [generator.choice((0, 0, 1, 2)) for _ in pairs]
            cases.append(
                (
                    [pair for pair, mark in zip(pairs, choice, strict=True) if mark == 1],
                    [pair for pair, mark in zip(pairs, choice, strict=True) if mark == 2],
                )
            )
    compared = 0
    for same, distinct in cases:
        for x, y in pairs:
            expected = oracle_status(partitions, same, distinct, x, y)
            actual = closure_status(names, same, distinct, x, y)
            assert actual == expected, (size, same, distinct, x, y, expected, actual)
            compared += 1
    return compared


def test_closure_matches_enumeration_on_all_assignments_for_three_and_four_items() -> None:
    """Every assignment on 3 and 4 items gives the same status both ways."""
    assert check_size(3, None) == 27 * 3
    assert check_size(4, None) == 729 * 6


def test_closure_matches_enumeration_on_a_fixed_sample_for_five_and_six_items() -> None:
    """A fixed pseudo-random sample on 5 and 6 items agrees too."""
    assert check_size(5, 1500) == 1500 * 10
    assert check_size(6, 300) == 300 * 15


def test_interpreter_end_to_end_matches_enumeration_on_three_items(tmp_path: Path) -> None:
    """Judgments given to the interpreter, in a fixed order, give the oracle's statuses.

    The interpreter records every judgment, including contradictory ones, so for
    an inconsistent assignment every status query reports 'inconsistent'.
    """
    digest = write_table(tmp_path, "evidence", ["note"], [["unit test evidence"]])
    names = ("a", "b", "c")
    partitions = set_partitions(3)
    pairs = list(combinations(range(3), 2))
    for same, distinct in assignments_all(3):
        lines = [
            f'source s file "evidence.csv" sha256 "{digest}"',
            "carrier c items a b c",
            'regime r on c explicit source s meaning "unit test"',
        ]
        number = 0
        for a, b in same:
            lines.append(f'judge j{number} same {names[a]} {names[b]} under r from s scope "t"')
            number += 1
        for a, b in distinct:
            lines.append(f'judge j{number} distinct {names[a]} {names[b]} under r from s scope "t"')
            number += 1
        for x, y in pairs:
            lines.append(f"check q{x}{y} status {names[x]} {names[y]} under r")
        run = run_program(parse("\n".join(lines) + "\n"), tmp_path)
        for x, y in pairs:
            expected = oracle_status(partitions, same, distinct, x, y)
            assert run.result(f"q{x}{y}").word == expected, (same, distinct, x, y)
