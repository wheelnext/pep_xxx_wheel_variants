from __future__ import annotations

from dataclasses import dataclass

FeatureIndex = int
PropertyIndex = int


class VariantProperty:
    namespace: str
    feature: str
    value: str

    def to_str(self) -> str:
        """Convert the VariantProperty to a string representation."""
        return f"{self.namespace} :: {self.feature} :: {self.value}"


@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str

    # Acceptable values in priority order
    values: list[str]


class FictionalHWPlugin:
    namespace = "fictional_hw"

    def _get_supported_architectures(self) -> list[str]:
        """Lookup the system to decide what `architecture` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["deepthought", "hal9000"]

    def _get_supported_compute_capability(self) -> list[str]:
        """Lookup the system to decide what `compute_capability` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return ["10", "6", "2"]

    def _get_supported_compute_accuracy(self) -> list[str]:
        """Lookup the system to decide what `compute_accuracy` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return ["1000", "0", "10"]

    def _get_supported_humor(self):
        """Lookup the system to decide what `humor` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["0", "2"]

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

        # 2. Filter Non Compatible VariantProperties and Sort the properties by feature
        #    and value.

        # Note: Since Python3.7, Python guarantees that `dict.keys()` conserve the
        #       insertion order. Here we are using this feature.

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
