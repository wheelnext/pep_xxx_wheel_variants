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

## Static and dynamic plugins

There are two plugin classes: static and dynamic.

In a static plugin, the list of all valid variant properties is fixed for
a specific plugin version, and the ordered list of supported variant
properties is determined independently of provided wheel variants.
This makes it possible to invoke the plugin once in order to obtain
the list of supported properties, and cache that result for multiple
packages to use. The cache needs to be invalidated only if the plugin
version changes or the relevant aspects of the system configuration
change.

An example of a static plugin could be a plugin controlling processor
architecture versions. One can assume that a specific version
of the plugin will only support a limited set of architecture
variations, and therefore the complete list of all valid properties
can be enumerated.

In dynamic plugins, the list of all valid variants does not need
to be fixed. Valid properties usually follow specific rules,
and the list can change within the same plugin version, dependent
on the build environment. The plugin receives a list of properties
used by the specific package, and selects and orders supported
properties based on it. As a result, the plugin needs to be invoked
separately for every installed package, and the results cannot be cached
across packages.

An example of a dynamic plugin is one that pins the package to
a specific range of runtime versions. In that case, any version
specifier can constitute a valid property (and therefore they can be
infinitely many valid values), and the plugin determines whether
the installed version matches the ranges specified for each variant.

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
    @abstractmethod
    def values(self) -> list[str]:
        """Ordered list of values, most preferred first"""
        raise NotImplementedError
```

A "variant feature config" must provide two properties or attributes:

- ``name`` specifying the feature name, as a string

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
    values: list[str]
```


### Variant property

The variant property type is used to represent a single variant property
with a specific value. It is defined using the following protocol:

```python
from abc import abstractmethod
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class VariantPropertyType(Protocol):
    """A protocol for variant properties"""

    @property
    @abstractmethod
    def namespace(self) -> str:
        """Namespace (from plugin)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def feature(self) -> str:
        """Feature name (within the namespace)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> str:
        """Feature value"""
        raise NotImplementedError
```

A "variant property" must define three properties or attributes:

- `namespace` specifying the namespace, as a string

- `feature` specifying the feature name, as a string

- `value` specifying the feature value, as a string

Example implementation:

```python
from dataclasses import dataclass


@dataclass
class VariantProperty:
    namespace: str
    feature: str
    value: str
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

    @property
    @abstractmethod
    def dynamic(self) -> bool:
        """Is this a dynamic plugin?"""
        raise NotImplementedError

    @abstractmethod
    def get_supported_configs(self) -> list[VariantFeatureConfigType]:
        """Get supported configs for the current system"""
        raise NotImplementedError

    @abstractmethod
    def validate_property(self, variant_property: VariantPropertyType) -> bool:
        """Validate variant property, returns True if it's valid"""
        raise NotImplementedError

    def get_build_setup(
        self, properties: list[VariantPropertyType]
    ) -> dict[str, list[str]]:
        """Get build variables for a variant made of specified properties"""
        return {}
```


### Properties

The plugin class must define the following properties or attributes:

- `namespace` specifying the plugin's namespace.

- `dynamic` specifying whether the plugin is of dynamic or static class.
  The value should be `True` for dynamic plugins, and `False` for static
  plugins.

Example implementation:

```python
class MyPlugin:
    namespace = "example"
    dynamic = False
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

If the plugin in question is a static plugin (`dynamic = False`),
the `known_properties` parameter is always `None`, and the method must
return a fixed list of supported features. If it is a dynamic plugin
(`dynamic = True`), a merged list of all properties used in available
variant wheels is provided, and the return value must include a subset
of these properties that are supported. However, the plugin is permitted
to return additional supported values not on the list.

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


### `validate_property`

Purpose: verify whether the specified property is valid for this plugin

Required: yes

Prototype:

```python
    @abstractmethod
    def validate_property(self, variant_property: VariantPropertyType) -> bool:
        ...
```

This method is called while building a variant wheel, in order to
determine whether the variant properties are valid. It is called once
for every property defined within the plugin's namespace, and must
return `True` if it is valid, `False` otherwise.

Note that all properties matching the values returned
by `get_supported_configs()` must evaluate as valid.

Example implementation:

```python
    # all valid properties as:
    # example :: accelerated :: yes
    # example :: version :: v4
    # example :: version :: v3
    # example :: version :: v2
    # example :: version :: v1

    def validate_property(self, variant_property: VariantPropertyType) -> bool:
        assert variant_property.namespace == self.namespace
        if variant_property.feature == "accelerated":
            return variant_property.value == "yes"
        if variant_property.feature == "version":
            return variant_property.value in ["v1", "v2", "v3", "v4"]
        return False
```


### Future extensions

The future versions of this specification, as well as third-party
extensions may introduce additional properties and methods on the plugin
instances. The implementations should ignore additional attributes.

For best compatibility, it is recommended that all private attributes
are prefixed with a underscore (`_`) character to avoid incidental
conflicts with future extensions.
