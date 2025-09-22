# Plugin API

## Purpose

This document describes the API used by variant provider plugins.
The plugins are a central point of the variant specification, defining
the valid metadata, and providing routines necessary to install
and build variants.

This document provides the API described both in text and using
Python [Protocols]( https://typing.python.org/en/latest/spec/protocol.html)
for convenience.


## Basic design

Every provider plugin operates within a single namespace. The namespace
is used as key for all plugin-related operations. All the properties
defined by the plugin are in the plugin's namespace, and the plugin
defines all the valid feature names and values within that namespace.

Within a single package, only one plugin can be used for a given
namespace. Attempting to load a second plugin sharing the same namespace
must cause a fatal error. However, it is possible for multiple plugins
using the namespace to exist, which implies that they become mutually
exclusive. For example, this could happen if a plugin becomes
unmaintained and needs to be forked into a new package.

Plugins are expected to be automatically installed when installing
variant-enabled packages, in order to facilitate variant
selection. Therefore, it is necessary that the packages providing
plugins are installable with the same indices enabled that are used
to install the package in question. In particular, packages published
to PyPI must not rely on plugins that need to be installed from other
indices.

Plugins are implemented using a Python class. Their API can be
accessed using two methods:

1. An explicit object reference, as the "plugin API" metadata.

2. An installed entry point in the `variant_plugins` group. The name
   of the entry point is insignificant, and the value provides
   the object reference.

Both formats use the object reference notation from the [entry point
specification](https://packaging.python.org/en/latest/specifications/entry-points/).
That is, they are in the form of:

```
importable.module:ClassName
```

The resulting plugin is instantiated by the equivalent of:

```python
import importable.module

plugin_instance = importable.module.ClassName()
```

The explicit "plugin API" key is the primary method of using the plugin.
It is part of the variant metadata, and it is therefore used while
building and installing wheels.

The entry point method is provided to increase the convenience of using
variant-related tools. It is therefore normally used with plugins that
are installed to user's main system. It can be used e.g. to detect
and print all supported variant properties, to help user configure
variant preferences or provide defaults to `pyproject.toml`.


## Behavior stability and versioning

It is recommended that the plugin's output remains stable within
the plugin's lifetime, and that packages do not pin to specific plugin
versions. This ensures that the installer can vendor or reimplement
the newest version of the plugin while ensuring that variant wheels
created earlier would still be installable.

If a need arises to introduce a breaking change in the plugin's output,
it is recommended to add a new API endpoint to the plugin. The old
endpoints should continue being provided, preserving the previous
output.


## Helper classes

### Variant feature config

The variant feature config class is used to define a single variant
feature, along with a list of possible values. Depending on the context,
the order of values may be significant. It is defined using
the following protocol:

```python
from abc import abstractmethod
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class VariantFeatureConfigType(Protocol):
    """A protocol for VariantFeature configs"""

    @property
    @abstractmethod
    def name(self) -> str:
        """feature name"""
        raise NotImplementedError

    @property
    def multi_value(self) -> bool:
        """Does this property allow multiple values per variant?"""
        raise NotImplementedError

    @property
    @abstractmethod
    def values(self) -> list[str]:
        """Ordered list of values, most preferred first"""
        raise NotImplementedError
```

A "variant feature config" must provide two properties or attributes:

- ``name`` specifying the feature name, as a string.

- ``multi_value`` specifying whether the feature is allowed to have
  multiple corresponding values within a single variant wheel. If it is
  `False`, then it is an error to specify multiple values for
  the feature.

- ``values`` specifying feature values, as a list of strings.
  In contexts where the order is significant, the values must be
  orderred from the most preferred to the least preferred.

All features are interpreted as being in the plugin's namespace.

Example implementation:

```python
from dataclasses import dataclass


@dataclass
class VariantFeatureConfig:
    name: str
    multi_value: bool
    values: list[str]
```


## Plugin class

### Protocol

The plugin class must implement the following protocol:

```python
from abc import abstractmethod
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class PluginType(Protocol):
    """A protocol for plugin classes"""

    @property
    @abstractmethod
    def namespace(self) -> str:
        """Get provider namespace"""
        raise NotImplementedError

    @abstractmethod
    def get_all_configs(self) -> list[VariantFeatureConfigType]:
        """Get all valid configs for the plugin"""
        raise NotImplementedError

    @abstractmethod
    def get_supported_configs(self) -> list[VariantFeatureConfigType]:
        """Get supported configs for the current system"""
        raise NotImplementedError
```


### Properties

The plugin class must define the following properties or attributes:

- `namespace` specifying the plugin's namespace.

Example implementation:

```python
class MyPlugin:
    namespace = "example"
```


### `get_all_configs`

Purpose: get all valid features and their values

Required: yes

Prototype:

```python
    @abstractmethod
    def get_all_configs(self) -> list[VariantFeatureConfigType]:
        ...
```

This method is used to validate available features and their values
for the given plugin version. It must return a list of "variant feature
configs", where every config defines a single feature along with all
its valid values. The list must be fixed for a given plugin version,
it is primarily used to verify properties prior to building a variant
wheel.

Example implementation:

```python
    # all valid properties as:
    # example :: accelerated :: yes
    # example :: version :: v4
    # example :: version :: v3
    # example :: version :: v2
    # example :: version :: v1

    def get_all_configs(self) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig("accelerated", ["yes"]),
            VariantFeatureConfig("version", ["v1", "v2", "v3", "v4"]),
        ]
```


### `get_supported_configs`

Purpose: get features and their values supported on this system

Required: yes

Prototype:

```python
    @abstractmethod
    def get_supported_configs(
        self, known_properties: frozenset[VariantPropertyType] | None
    ) -> list[VariantFeatureConfigType]:
        ...
```

This method is used to determine which features are supported on this
system. It must return a list of "variant feature configs", where every
config defines a single feature along with all the supported values.
The values should be ordered from the most preferred value to the least
preferred.

Example implementation:

```python
    # defines features compatible with the system as:
    # example :: version :: v2 (more preferred)
    # example :: version :: v1 (less preferred)
    # (a wheel with no "example :: version" is the least preferred)
    #
    # the system does not support "example :: accelerated" at all

    def get_supported_configs(
        self, known_properties: frozenset[VariantPropertyType] | None
    ) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig("version", ["v2", "v1"]),
        ]
```


### Future extensions

The future versions of this specification, as well as third-party
extensions may introduce additional properties and methods on the plugin
instances. The implementations should ignore additional attributes.

For best compatibility, it is recommended that all private attributes
are prefixed with a underscore (`_`) character to avoid incidental
conflicts with future extensions.
