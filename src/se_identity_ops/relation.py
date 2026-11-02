"""relation.py - Same and distinct commitments over a finite carrier.

WHAT: A union-find implementation of the commitment calculus that
      `se-theory-persistence` defines in Lean: generated identity, consistency,
      and the Required, Forbidden, and Undetermined statuses of a pair.
WHY: The interpreter needs these statuses on carriers of 20,000 items, so they
     are computed by closure rather than by enumerating equivalence relations.
     Tests compare this code with an exhaustive enumeration on small carriers.
OBS: Correspondence with the Lean theory is an obligation, not a proof. The
     Lean statements are `Required`, `Forbidden`, `Undetermined`, `Consistent`,
     `generated_iff_reach_symmStep`, and `forbidden_iff_forall_admissible`.
OBS: Statuses are defined for consistent commitments. An inconsistent set of
     commitments is reported as inconsistent with a witness, never as a status.
"""

from collections import deque
from dataclasses import dataclass

from .results import DerivationStep


@dataclass(frozen=True, slots=True)
class SamePair:
    """A same-commitment between two items.

    Attributes:
        first: First item.
        second: Second item.
        ground: "judgment" or "step".
        detail: Label of the judgment or step.
        source: Source name, or empty string.
    """

    first: str
    second: str
    ground: str
    detail: str
    source: str


@dataclass(frozen=True, slots=True)
class DistinctPair:
    """A distinct-commitment between two items.

    Attributes:
        first: First item.
        second: Second item.
        label: Label of the judgment.
        source: Source name, or empty string.
    """

    first: str
    second: str
    label: str
    source: str


class Relation:
    """Commitments over one carrier under one regime.

    Same-commitments come from a key column (items with an equal non-empty key
    value) and from explicit same pairs. Distinct-commitments come from explicit
    distinct pairs only. Nothing is inferred to be distinct.
    """

    def __init__(
        self,
        items: tuple[str, ...],
        keys: tuple[str, ...] | None,
        key_column: str,
        same_pairs: tuple[SamePair, ...],
        distinct_pairs: tuple[DistinctPair, ...],
    ) -> None:
        """Build the relation.

        Args:
            items: Item names in carrier order.
            keys: Key value of each item in carrier order, or None for a regime
                with no key column. An empty string means the criterion is silent
                about that item.
            key_column: Name of the key column, used in derivations.
            same_pairs: Explicit same-commitments.
            distinct_pairs: Explicit distinct-commitments.
        """
        self.items = items
        self.index = {name: position for position, name in enumerate(items)}
        self.key_column = key_column
        self.keys = keys
        self.same_pairs = same_pairs
        self.distinct_pairs = distinct_pairs
        self._parent = list(range(len(items)))
        self._key_representative: dict[str, int] = {}
        if keys is not None:
            for position, key in enumerate(keys):
                if not key:
                    continue
                if key in self._key_representative:
                    self._union(self._key_representative[key], position)
                else:
                    self._key_representative[key] = position
        for pair in same_pairs:
            self._union(self.index[pair.first], self.index[pair.second])

    def _find(self, position: int) -> int:
        """Return the class representative of an item position."""
        root = position
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[position] != root:
            self._parent[position], position = root, self._parent[position]
        return root

    def _union(self, first: int, second: int) -> None:
        """Merge the classes of two item positions, keeping the smaller root."""
        root_first = self._find(first)
        root_second = self._find(second)
        if root_first == root_second:
            return
        if root_first < root_second:
            self._parent[root_second] = root_first
        else:
            self._parent[root_first] = root_second

    def class_of(self, item: str) -> int:
        """Return the class number of an item (smallest member position)."""
        return self._find(self.index[item])

    def has_key(self, item: str) -> bool:
        """Return whether the key column places the item in a class."""
        return self.keys is not None and bool(self.keys[self.index[item]])

    def required(self, first: str, second: str) -> bool:
        """Return whether the pair is generated-identical."""
        return self.class_of(first) == self.class_of(second)

    def conflicts(self) -> tuple[DistinctPair, ...]:
        """Return distinct-commitments whose endpoints are generated-identical."""
        return tuple(
            pair
            for pair in self.distinct_pairs
            if self.required(pair.first, pair.second)
        )

    def consistent(self) -> bool:
        """Return whether no distinct-commitment lies inside a class."""
        return not self.conflicts()

    def forbidden_by(self, first: str, second: str) -> DistinctPair | None:
        """Return a distinct-commitment that forbids identifying the pair, or None.

        Identifying `first` and `second` would join their two classes. The pair is
        forbidden when some distinct-commitment has its endpoints in those two classes.
        """
        class_first = self.class_of(first)
        class_second = self.class_of(second)
        if class_first == class_second:
            return None
        wanted = {class_first, class_second}
        for pair in self.distinct_pairs:
            if {self.class_of(pair.first), self.class_of(pair.second)} == wanted:
                return pair
        return None

    def status(self, first: str, second: str) -> str:
        """Return 'required', 'forbidden', 'undetermined', or 'inconsistent'."""
        if not self.consistent():
            return "inconsistent"
        if self.required(first, second):
            return "required"
        if self.forbidden_by(first, second) is not None:
            return "forbidden"
        return "undetermined"

    def path(self, first: str, second: str) -> tuple[DerivationStep, ...]:
        """Return a shortest chain of same-commitments joining two items.

        The chain uses key hops (item to the first item with the same key value)
        and explicit pairs, each in either direction.

        Args:
            first: Start item.
            second: End item.

        Returns:
            Steps from `first` to `second`; empty when they are the same item.

        Raises:
            ValueError: If the two items are not generated-identical.
        """
        if first == second:
            return ()
        if not self.required(first, second):
            raise ValueError(f"'{first}' and '{second}' are not generated-identical")
        adjacency: dict[int, list[tuple[int, DerivationStep]]] = {}
        for pair in self.same_pairs:
            a = self.index[pair.first]
            b = self.index[pair.second]
            adjacency.setdefault(a, []).append(
                (
                    b,
                    DerivationStep(
                        pair.first, pair.second, pair.ground, pair.detail, pair.source
                    ),
                )
            )
            adjacency.setdefault(b, []).append(
                (
                    a,
                    DerivationStep(
                        pair.second, pair.first, pair.ground, pair.detail, pair.source
                    ),
                )
            )
        start = self.index[first]
        goal = self.index[second]
        previous: dict[int, tuple[int, DerivationStep]] = {}
        seen = {start}
        queue: deque[int] = deque([start])
        while queue:
            here = queue.popleft()
            if here == goal:
                break
            for there, step in self._neighbors(here, adjacency):
                if there not in seen:
                    seen.add(there)
                    previous[there] = (here, step)
                    queue.append(there)
        chain: list[DerivationStep] = []
        cursor = goal
        while cursor != start:
            before, step = previous[cursor]
            chain.append(step)
            cursor = before
        chain.reverse()
        return tuple(chain)

    def _neighbors(
        self, here: int, adjacency: dict[int, list[tuple[int, DerivationStep]]]
    ) -> list[tuple[int, DerivationStep]]:
        """Return neighbors of an item in a fixed order: key hop first, then pairs."""
        found: list[tuple[int, DerivationStep]] = []
        if self.keys is not None and self.keys[here]:
            key = self.keys[here]
            representative = self._key_representative[key]
            detail = f"{self.key_column}={key}"
            if representative != here:
                found.append(
                    (
                        representative,
                        DerivationStep(
                            self.items[here],
                            self.items[representative],
                            "key",
                            detail,
                            "",
                        ),
                    )
                )
            else:
                for position, other_key in enumerate(self.keys):
                    if other_key == key and position != here:
                        found.append(
                            (
                                position,
                                DerivationStep(
                                    self.items[here],
                                    self.items[position],
                                    "key",
                                    detail,
                                    "",
                                ),
                            )
                        )
        found.extend(sorted(adjacency.get(here, []), key=lambda entry: entry[0]))
        return found
