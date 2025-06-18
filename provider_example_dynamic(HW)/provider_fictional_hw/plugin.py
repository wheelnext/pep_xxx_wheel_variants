from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol
from typing import runtime_checkable

from packaging.specifiers import SpecifierSet
from packaging.version import Version

FeatureIndex = int
PropertyIndex = int


@runtime_checkable
class VariantProperty(Protocol):
    namespace: str
    feature: str
    value: str


@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str

    # Acceptable values in priority order
    values: list[str]


class FictionalHWPlugin:
    namespace = "fictional_hw"

    def _get_supported_architectures(self) -> list[str] | None:
        """Lookup the system to decide what `architecture` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["deepthought", "hal9000"]

    def _get_compute_capability(self) -> Version | None:
        """Lookup the system to decide what `compute_capability` is supported on
        this system.
        Returns a list of strings in order of priority."""
        return Version("8.3.2")

    def _get_supported_compute_accuracy(self) -> float | None:
        """Lookup the system to decide what `compute_accuracy` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return 0.995

    def filter_and_sort_properties(
        self, vprops: list[VariantProperty]
    ) -> list[VariantProperty]:
        """Filter and sort the properties based on the plugin's logic."""

        # 1.A Validation: Validate input types.
        assert isinstance(vprops, list)
        assert all(isinstance(vprop, VariantProperty) for vprop in vprops)

        # 1.B Validation: Ensure all properties belong to the proper namespace.
        issues_found: list[str] = [
            f"Property `{vprop}` does not belong to namespace {self.namespace}"
            for vprop in vprops
            if vprop.namespace != self.namespace
        ]
        if issues_found:
            raise ValueError(
                f"Non compatible properties found in variant plugin "
                f"`{self.namespace}`:\n"
                f"{'\n- '.join(issues_found)}"
            )

        # 2. Aggregate Variant Property values per feature.
        prop_values = defaultdict(list)
        for vprop in vprops:
            prop_values[vprop.feature].append(vprop.value)

        # 3. Filter and sort supported variant property values.
        keyconfigs = []

        # Top Priority
        if (supported_values := self._get_supported_architectures()) is not None:
            key = "architecture"
            keyconfigs.append(
                VariantFeatureConfig(
                    name=key,
                    values=[val for val in prop_values[key] if val in supported_values],
                )
            )

        # Second Priority
        if (version := self._get_compute_capability()) is not None:
            key = "compute_capability"
            keyconfigs.append(
                VariantFeatureConfig(
                    name=key,
                    values=[
                        val for val in prop_values[key] if version in SpecifierSet(val)
                    ],
                )
            )

        # Third Priority
        if (accuracy := self._get_supported_compute_accuracy()) is not None:
            # Sorting order: from lowest required accuracy to the highest
            key = "compute_accuracy"
            keyconfigs.append(
                VariantFeatureConfig(
                    name=key,
                    values=sorted(
                        [
                            needed_accuracy
                            for needed_accuracy in prop_values[key]
                            if needed_accuracy <= accuracy
                        ]
                    ),
                )
            )

        # =========================================== #

        # fmt: off
        ordering: dict[str, list[str]] = {
            "architecture": self._get_supported_architectures(),            # Priority 1
            "compute_capability": self._get_supported_compute_capability(), # Priority 2
            "humor": self._get_supported_humor(),                           # Priority 3
            "compute_accuracy": self._get_supported_compute_accuracy(),     # Priority 4
        }
        # fmt: on

        def _is_compatible(vprop: VariantProperty) -> bool:
            """Check if the property is compatible with the system."""
            return vprop.value in ordering.get(vprop.feature, [])

        vprops_data_filtered = filter(_is_compatible, vprops)

        def property_rank(prop: VariantProperty) -> tuple[FeatureIndex, PropertyIndex]:
            """Sort key for the properties."""
            feature_index = list(ordering.keys()).index(prop.feature)
            value_index = ordering[prop.feature].index(prop.value)
            return (feature_index, value_index)

        return sorted(vprops_data_filtered, key=property_rank)

    def get_all_configs(self) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="architecture", values=["deepthought", "hal9000", "mother", "tars"]
            ),
            VariantFeatureConfig(
                name="compute_capability",
                values=[str(x) for x in range(0, 11, 2)],
            ),
            VariantFeatureConfig(
                name="humor", values=[str(x) for x in range(0, 11, 2)]
            ),
            VariantFeatureConfig(
                name="compute_accuracy", values=[str(x) for x in range(0, 11, 2)]
            ),
        ]
