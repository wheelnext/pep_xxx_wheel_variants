import itertools
import json
from pathlib import Path
from typing import Generator

from variantlib.config import KeyConfig
from variantlib.config import ProviderConfig
from variantlib.meta import VariantMeta

config_custom_hw = ProviderConfig(
    provider="custom_hw",
    configs=[
        KeyConfig(key="driver_version", values=["1.3", "1.2", "1.1", "1"]),
        KeyConfig(key="hw_architecture", values=["3.4", "3"]),
    ],
)

config_networking = ProviderConfig(
    provider="networking",
    configs=[
        KeyConfig(key="speed", values=["10GBPS", "1GBPS", "100MBPS"]),
    ],
)

configs = [config_custom_hw, config_networking]


output_f = Path("yolo.json")
with output_f.open(mode="w") as outfile:
    json.dump(
        list(get_combinations(configs)),
        outfile,
        default=lambda o: o.to_dict(),
        indent=4,
    )
