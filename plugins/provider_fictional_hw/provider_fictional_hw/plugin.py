from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol
from typing import runtime_checkable

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


class FictionalHWPlugin:
    namespace = "fictional_hw"
    is_build_plugin = False

    @classmethod
    def _get_supported_architectures(cls) -> list[str]:
        """Lookup the system to decide what `architecture` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["deepthought", "hal9000"]

    @classmethod
    def _get_supported_compute_capability(cls) -> list[str]:
        """Lookup the system to decide what `compute_capability` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return ["10", "6", "2"]

    @classmethod
    def _get_supported_compute_accuracy(cls) -> list[str]:
        """Lookup the system to decide what `compute_accuracy` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return ["1000", "0", "10"]

    @classmethod
    def get_supported_configs(cls) -> list[VariantFeatureConfig]:
        keyconfigs = []

        # Top Priority
        if (values := cls._get_supported_architectures()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="architecture", values=values))

        # Second Priority
        if (values := cls._get_supported_compute_capability()) is not None:
            keyconfigs.append(
                VariantFeatureConfig(name="compute_capability", values=values)
            )

        # Third Priority
        if (values := cls._get_supported_compute_accuracy()) is not None:
            keyconfigs.append(
                VariantFeatureConfig(name="compute_accuracy", values=values)
            )

        return keyconfigs

    @classmethod
    def get_all_configs(cls) -> list[VariantFeatureConfig]:
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

    @classmethod
    def get_build_setup(
        cls, properties: list[VariantPropertyType]
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
        VProp(namespace=plugin.namespace, feature="compute_capability", value="10"),
        VProp(namespace=plugin.namespace, feature="compute_capability", value="6"),
        VProp(namespace=plugin.namespace, feature="compute_capability", value="2"),
        # 3. `compute_accuracy`: selection `<= 0.995` sorted from high to low
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="1000"),
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="0"),
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="10"),
        # ---------------------------- Should NOT Work ---------------------------- #
        # 1. `architecture`: only ["deepthought", "hal9000"] in this order
        VProp(namespace=plugin.namespace, feature="architecture", value="jarvis"),
        VProp(namespace=plugin.namespace, feature="architecture", value="tar"),
        # 2. `compute_capability`: selection `Version("8.3.2") in SpecifierSet`
        #    sorted from least specific to most - forward compat first.
        VProp(namespace=plugin.namespace, feature="compute_capability", value="9.0"),
        VProp(namespace=plugin.namespace, feature="compute_capability", value="9_0"),
        # 3. `compute_accuracy`: selection `<= 0.995` sorted from high to low
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value=str(9e-1)),
        VProp(namespace=plugin.namespace, feature="compute_accuracy", value="0.9999"),
    ]
    print(f"{plugin.get_supported_configs(vprops)=}")  # type: ignore  # noqa: PGH003,T201
