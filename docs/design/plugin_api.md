# Plugin API

## Purpose

This document describes the API used by variant provider plugins. The plugins
are a central point of the variant specification, defining the valid metadata,
and providing routines necessary to install and build variants.

This document provides the API described both in text and using Python
[Protocols](https://typing.python.org/en/latest/spec/protocol.html) for
convenience.

## Basic design

Every provider plugin operates within a single namespace. The namespace is used
as key for all plugin-related operations. All the properties defined by the
plugin are in the plugin's namespace, and the plugin defines all the valid
feature names and values within that namespace.

Within a single package, only one plugin can be used for a given namespace.
Attempting to load a second plugin sharing the same namespace must cause a fatal
error. However, it is possible for multiple plugins using the namespace to
exist, which implies that they become mutually exclusive. For example, this
could happen if a plugin becomes unmaintained and needs to be forked into a new
package.

Plugins are expected to be automatically installed when installing
variant-enabled packages, in order to facilitate variant selection. Therefore,
it is necessary that the packages providing plugins are installable with the
same indices enabled that are used to install the package in question. In
particular, packages published to PyPI must not rely on plugins that need to be
installed from other indices.

Plugins are implemented using a Python class. Their API can be accessed using
two methods:

1. An explicit object reference, as the "plugin API" metadata.

2. An installed entry point in the `variant_plugins` group. The name of the
   entry point is insignificant, and the value provides the object reference.

Both formats use the object reference notation from the
[entry point specification](https://packaging.python.org/en/latest/specifications/entry-points/).
That is, they are in the form of:

```
importable.module:ClassName
```

The resulting plugin is instantiated by the equivalent of:

```python
import importable.module

plugin_instance = importable.module.ClassName()
```

The explicit "plugin API" key is the primary method of using the plugin. It is
part of the variant metadata, and it is therefore used while building and
installing wheels.

The entry point method is provided to increase the convenience of using
variant-related tools. It is therefore normally used with plugins that are
installed to user's main system. It can be used e.g. to detect and print all
supported variant properties, to help user configure variant preferences or
provide defaults to `pyproject.toml`.

## Helper classes

### Variant feature config

The variant feature config class is used to define a single variant feature,
along with a list of possible values. Depending on the context, the order of
values may be significant. It is defined using the following protocol:

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

- `name` specifying the feature name, as a string

- `values` specifying feature values, as a list of strings. In contexts where
  the order is significant, the values must be orderred from the most preferred
  to the least preferred.

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

The variant property type is used to represent a single variant property with a
specific value. It is defined using the following protocol:

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

    @abstractmethod
    def get_all_configs(self) -> list[VariantFeatureConfigType]:
        """Get all configs for the plugin"""
        raise NotImplementedError

    @abstractmethod
    def get_supported_configs(self) -> list[VariantFeatureConfigType]:
        """Get supported configs for the current system"""
        raise NotImplementedError

    def get_build_setup(
        self, properties: list[VariantPropertyType]
    ) -> dict[str, list[str]]:
        """Get build variables for a variant made of specified properties"""
        return {}
```

### Properties

The plugin class must define a single property or attribute:

- `namespace` specifying the plugin's namespace

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
    def get_all_configs(self) -> list[VariantFeatureConfigType]:
        ...
```

This method is used to determine all the valid features within the provider's
namespace. It must return a list of "variant feature configs", where every
config defines a single feature along with all its possible values. The order of
the returned values is insignificant.

Example implementation:

```python
    # defines all valid features as:
    # example :: accelerated :: yes
    # example :: version :: v4
    # example :: version :: v3
    # example :: version :: v2
    # example :: version :: v1

    def get_all_configs(self) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig("accelerated", ["yes"]),
            VariantFeatureConfig("version", ["v4", "v3", "v2", "v1"]),
        ]
```

### `get_supported_configs`

Purpose: get features and their values supported on this system

Required: yes

Prototype:

```python
    def get_supported_configs(self) -> list[VariantFeatureConfigType]:
        ...
```

This method is used to determine which features are supported on this system. It
must return a list of "variant feature configs", where every config defines a
single feature along with all the supported values. The values should be ordered
from the most preferred value to the least preferred.

Example implementation:

```python
    # defines features compatible with the system as:
    # example :: version :: v2 (more preferred)
    # example :: version :: v1 (less preferred)
    # (a wheel with no "example :: version" is the least preferred)
    #
    # the system does not support "example :: accelerated" at all

    def get_supported_configs(self) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig("version", ["v2", "v1"]),
        ]
```

### `get_build_setup`

Purpose: get build variables for the built variant

Required: no

Prototype:

```python
    def get_build_setup(
        self, properties: list[VariantPropertyType]
    ) -> dict[str, list[str]]:
        ...
```

This method is used to obtain "build variables" that are used by the build
backend to configure the build of a specific variant. It is passed a list of
variant properties, filtered to include only these matching the namespace used
by the plugin. It must return a dictionary that maps build variable names into a
list of string values. If multiple plugins include the same variable, their
values are concatenated, in an undefined order.

The exact list of build variables and the meaning of their values is out of the
scope for this document. Build backends should ignore the values they do not
recognize or support.

The build setup implementation is likely to change, see
[discussion on build setup](https://github.com/wheelnext/pep_xxx_wheel_variants/issues/23).

Example implementation:

```python
    def get_build_setup(
        self, properties: list[VariantPropertyType]
    ) -> dict[str, list[str]]:
        cflags = []

        for prop in properties:
            assert prop.namespace == self.namespace
            if prop.feature == "version":
                cflags.append(f"-march=example-{prop.value}")
            elif prop.feature == "accelerated":
                assert prop.value == "yes"
                cflags.append("-maccelerate")

        return {"cflags": cflags}
```

### Future extensions

The future versions of this specification, as well as third-party extensions may
introduce additional properties and methods on the plugin instances. The
implementations should ignore additional attributes.

For best compatibility, it is recommended that all private attributes are
prefixed with a underscore (`_`) character to avoid incidental conflicts with
future extensions.
