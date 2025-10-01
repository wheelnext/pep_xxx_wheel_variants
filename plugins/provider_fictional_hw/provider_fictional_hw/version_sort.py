from __future__ import annotations

from typing import TYPE_CHECKING

from packaging._structures import Infinity
from packaging._structures import InfinityType
from packaging._structures import NegativeInfinity
from packaging._structures import NegativeInfinityType
from packaging.version import Version

if TYPE_CHECKING:
    from provider_fictional_hw.plugin import InputPreservingSpecifierSet


def sort_specifier_sets(
    specifier_sets: list[InputPreservingSpecifierSet],
) -> list[InputPreservingSpecifierSet]:
    """Sort a list of SpecifierSets.

    Sort first by the maximum lower bound, then by the maximum upper bound.

    Args:
        specifier_sets: A list of SpecifierSet objects.

    Returns:
        A list of SpecifierSet objects sorted according to the described criteria.
    """

    def get_max_bound(
        specifier_set, bound_type
    ) -> NegativeInfinityType | InfinityType | Version:
        """Get the greatest lower bound (infimum) or least upper bound (supremum) of a
        SpecifierSet."""
        if bound_type not in ["lower", "upper"]:
            raise ValueError(f"Invalid bound type: {bound_type}")
        operators = (
            {">", ">=", "~=", "==", "==="}
            if bound_type == "lower"
            else {"<", "<=", "=="}
        )
        bounds = [Version(s.version) for s in specifier_set if s.operator in operators]
        if len(bounds) == 0:
            return NegativeInfinity if bound_type == "lower" else Infinity
        func = min if bound_type == "lower" else max
        return func(bounds)

    return sorted(
        specifier_sets,
        key=lambda ss: (get_max_bound(ss, "lower"), get_max_bound(ss, "upper")),
    )
