from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str

    # Acceptable values in priority order
    values: list[str]


class FictionalTechPlugin:
    namespace = "fictional_tech"
    is_build_plugin = False

    def _get_supported_technologies(self) -> list[str]:
        """Lookup the system to decide what `technology` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["auto_chef"]

    def _get_supported_quantum(self) -> list[str]:
        """Lookup the system to decide what `quantum` are supported on this system.
        Returns a list of strings in order of priority."""
        return ["foam", "superposition"]

    def _get_supported_risk_exposure(self) -> list[str]:
        """Lookup the system to decide what `risk_exposure` are supported on this
        system.
        Returns a list of strings in order of priority."""
        return ["25"]

    def get_supported_configs(self, known_properties: list[Any] | None) -> list[VariantFeatureConfig]:
        keyconfigs = []

        # Top Priority
        if (values := self._get_supported_technologies()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="technology", values=values))

        # Second Priority
        if (values := self._get_supported_quantum()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="quantum", values=values))

        # Third Priority
        if (values := self._get_supported_risk_exposure()) is not None:
            keyconfigs.append(VariantFeatureConfig(name="risk_exposure", values=values))

        return keyconfigs

    def get_all_configs(self, known_properties: list[Any] | None) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="technology", values=["auto_chef", "improb_drive"]
            ),
            VariantFeatureConfig(name="quantum", values=["foam", "superposition"]),
            VariantFeatureConfig(name="risk_exposure", values=["25", "1000000000"]),
        ]

    def get_build_setup(self, properties: list[Any]) -> dict[str, list[str]]:
        """Get build variables for a variant made of specified properties"""
        return {}
