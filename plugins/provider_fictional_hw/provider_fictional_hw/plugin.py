from __future__ import annotations

import warnings
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Protocol
from typing import runtime_checkable

from packaging.specifiers import InvalidSpecifier
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from provider_fictional_hw.version_sort import sort_specifier_sets

FeatureIndex = int
PropertyIndex = int

VariantNamespace = str
VariantFeatureName = str
VariantFeatureValue = str


@runtime_checkable
class VariantPropertyType(Protocol):
    """A protocol for variant properties"""

    @property
    @abstractmethod
    def namespace(self) -> VariantNamespace:
        """Namespace (from plugin)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def feature(self) -> VariantFeatureName:
        """Feature name (within the namespace)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> VariantFeatureValue:
        """Feature value"""
        raise NotImplementedError


@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str

    # Acceptable values in priority order
    values: list[str]


class InputPreservingSpecifierSet(SpecifierSet):
    original_value: str

    def __init__(
        self,
        specifiers: str = "",
        prereleases: bool | None = None,
    ) -> None:
        self.original_value = specifiers
        super().__init__(specifiers=specifiers, prereleases=prereleases)


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

    def get_supported_configs(
        self, known_properties: frozenset[VariantPropertyType] | None
    ) -> list[VariantFeatureConfig]:
        """Filter and sort the properties based on the plugin's logic."""

        # 1.A - Validation: Validate input types.
        assert isinstance(known_properties, frozenset)
        assert all(isinstance(vprop, VariantPropertyType) for vprop in known_properties)

        if not known_properties:
            # Nothing In => Nothing Out
            return []

        prop_values: dict[VariantFeatureName, list[VariantFeatureValue]] = defaultdict(
            list
        )
        for vprop in known_properties:
            prop_values[vprop.feature].append(vprop.value)

        # 1.B - Validation: Ensure all properties belong to the proper namespace.
        issues_found: list[str] = [
            f"Property `{vprop}` does not belong to namespace {self.namespace}"
            for vprop in known_properties
            if vprop.namespace != self.namespace
        ]
        if issues_found:
            raise ValueError(
                f"Non compatible properties found in variant plugin "
                f"`{self.namespace}`:"
                + ("\n- " + ("\n- ".join(issues_found)) if issues_found else "")
            )

        # 2. Group Variant Property values per feature.
        prop_values: dict[VariantFeatureName, list[VariantFeatureValue]] = defaultdict(
            list
        )
        for vprop in known_properties:
            prop_values[vprop.feature].append(vprop.value)

        # 3. Filter and sort supported variant property values.
        keyconfigs: list[VariantFeatureConfig] = []

        # Top Priority: `architecture`
        # - using a fixed list[str] as ordering
        # - `known_properties` not used
        if (values := self._get_supported_architectures()) is not None:
            keyconfigs.append(
                VariantFeatureConfig(
                    name="architecture",
                    values=values,
                )
            )

        # Second Priority: `compute_capability`
        # - using dynamically computer version comparison using `SpecifierSet`
        if (version := self._get_compute_capability()) is not None:
            key = "compute_capability"
            vprops_specset: list[InputPreservingSpecifierSet] = []
            for vprop in prop_values[key]:
                try:
                    vprops_specset.append(InputPreservingSpecifierSet(vprop))
                except InvalidSpecifier:  # noqa: PERF203
                    warnings.warn(
                        f"The variant property `{self.namespace} :: {key} :: {vprop}` "
                        f"is not a valid `SpecifierSet`. Will be ignored.",
                        UserWarning,
                        stacklevel=1,
                    )

            vprops_specset = sort_specifier_sets(vprops_specset)
            vprops_specset.reverse()  # most generic to most specific, forward first

            keyconfigs.append(
                VariantFeatureConfig(
                    name=key,
                    values=[
                        specset.original_value
                        for specset in vprops_specset
                        if version in specset
                    ],
                )
            )

        # Third Priority: `compute_accuracy`
        # - using `float` comparison
        if (accuracy := self._get_supported_compute_accuracy()) is not None:
            # Sorting order: from lowest required accuracy to the highest
            key = "compute_accuracy"
            values = sorted(
                [
                    needed_accuracy
                    for needed_accuracy in prop_values[key]
                    if float(needed_accuracy) <= accuracy
                ],
                key=lambda x: float(x),
                reverse=True,
            )
            if values:
                keyconfigs.append(VariantFeatureConfig(name=key, values=values))

        return keyconfigs

    def get_all_configs(
        self, known_properties: list[Any] | None
    ) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="architecture", values=["deepthought", "hal9000", "mother", "tars"]
            ),
            VariantFeatureConfig(
                name="compute_capability",
                values=[str(x) for x in range(0, 11, 2)],
            ),
            VariantFeatureConfig(
                name="compute_accuracy", values=[str(x) for x in range(0, 11, 2)]
            ),
        ]

    def get_build_setup(
        self, properties: list[VariantPropertyType]
    ) -> dict[str, list[str]]:
        """Get build variables for a variant made of specified properties"""
        return {}


if __name__ == "__main__":
    plugin = FictionalHWPlugin()
    print(f"{plugin.get_all_configs(None)=}")  # noqa: T201

    @dataclass(frozen=True)
    class VProp:
        namespace: str
        feature: str
        value: str

    vprops: list[VProp] = [
        # ------------------------------ Should Work ------------------------------ #
        # 1. `architecture`: only ["deepthought", "hal9000"] in this order
        VProp(namespace=plugin.namespace, feature="architecture", value="hal9000"),
        VProp(namespace=plugin.namespace, feature="architecture", value="deepthought"),
        # 2. `compute_capability`: selection `Version("8.3.2") in SpecifierSet`
        #    sorted from least specific to most - forward compat first.
        VProp(namespace=plugin.namespace, feature="compute_capability", value=">=8"),
        VProp(namespace=plugin.namespace, feature="compute_capability", value="<9"),
        VProp(
            namespace=plugin.namespace,
            feature="compute_capability",
            value=">=5.0,<10.0",
        ),
        # 3. `compute_accuracy`: selection `<= 0.995` sorted from high to low
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="0.7"),
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="0.99"),
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="0.8"),
        # ---------------------------- Should NOT Work ---------------------------- #
        # 1. `architecture`: only ["deepthought", "hal9000"] in this order
        VProp(namespace=plugin.namespace, feature="architecture", value="jarvis"),
        VProp(namespace=plugin.namespace, feature="architecture", value="tar"),
        # 2. `compute_capability`: selection `Version("8.3.2") in SpecifierSet`
        #    sorted from least specific to most - forward compat first.
        VProp(namespace=plugin.namespace, feature="compute_capability", value=">=9"),
        VProp(namespace=plugin.namespace, feature="compute_capability", value="<8"),
        VProp(
            namespace=plugin.namespace,
            feature="compute_capability",
            value=">=8,<9,!=8.3.2",
        ),
        # 3. `compute_accuracy`: selection `<= 0.995` sorted from high to low
        VProp(
            namespace=plugin.namespace, feature="compute_accuracy", value=str(9.99e-1)
        ),
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="0.9999"),
    ]
    print(f"{plugin.get_supported_configs(vprops)=}")  # type: ignore  # noqa: PGH003,T201
