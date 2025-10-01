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


class FictionalTechPlugin:
    namespace = "fictional_tech"
    is_build_plugin = False

    @classmethod
    def _get_supported_technologies(cls) -> list[str]:
        """Lookup the system to decide what `technology` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["auto_chef"]

    @classmethod
    def _get_supported_quantum(cls) -> list[str]:
        """Lookup the system to decide what `quantum` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["foam", "superposition"]

    @classmethod
    def _get_supported_risk_exposure(cls) -> list[str]:
        """Lookup the system to decide what `risk_exposure` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return ["25"]

    @classmethod
    def get_supported_configs(cls) -> list[VariantFeatureConfig]:
        keyconfigs = []

        # Top Priority
        if (values := cls._get_supported_technologies()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="technology", values=values))

        # Second Priority
        if (values := cls._get_supported_quantum()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="quantum", values=values))

        # Third Priority
        if (values := cls._get_supported_risk_exposure()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="risk_exposure", values=values))

        return keyconfigs

    @classmethod
    def get_all_configs(cls) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="technology", values=["auto_chef", "improb_drive"]
            ),
            VariantFeatureConfig(name="quantum", values=["foam", "superposition"]),
            VariantFeatureConfig(name="risk_exposure", values=["25", "1000000000"]),
        ]

    @classmethod
    def get_build_setup(
        cls, properties: list[VariantPropertyType]
    ) -> dict[str, list[str]]:
        """Get build variables for a variant made of specified properties"""
        return {}
