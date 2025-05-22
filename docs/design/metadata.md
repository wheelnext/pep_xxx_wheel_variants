# Metadata formats

## Purpose

This document describes the three metadata formats used for variant
wheels: `pyproject.toml` tables, distribution metadata fields
and `variants.json` file. All three formats are related, as they share
a common part and form a single pipeline:

    pyproject.toml → distribution (wheel) metadata → variants.json

The `pyproject.toml` file is used to build the wheels. As a common
project configuration format, it also specifies the metadata used later
to install them.

When the wheels are built, the build backend transfers the relevant
metadata into the distribution metadata, along with the built variant
description. This information is used when installing the wheels.

Additionally, for the purpose of indexing, the metadata from multiple
wheels is collected into a single `variants.json` format file. This file
can be afterwards fetched by the installers to determine which variants
are available and how to install the provider plugins required to
determine which variants are supported. This makes it possible to select
a specific variant wheel without having to download them all.


## The common metadata

### Default priorities

The wheel metadata can specify three lists of default priorities:

1. *Namespace priorities* that define both the list of namespaces
   that are used by default when installing the package in question,
   and their initial order. Said order may be altered afterwards by user
   configuration. This list must be defined and non-empty.

2. *Feature priorities* that override the order of features. The initial
   order is determined by ordering the namespaces according to their
   priorities (as indicated in point 1.), then replacing them by all
   their features as ordered by the provider plugin. Afterwards, all
   features defined in the feature priority list are moved to
   the beginning of the resulting list, while the relative order
   of the remaining items remains the same. Said order may be altered
   by user configuration. This list is optional.

3. *Property priorities* that override the order of properties.
   The initial order is determined by ordering the features according
   to their priorities (as indicated in point 2.), then replacing them
   by all their properties as ordered by the provider plugin.
   Afterwards, all properties defined in the feature priority list
   are moved to the beginning of the resulting list, while the relative
   order of the remaining items remains the same. Said order may be
   altered by user configuration. This list is optional.

### Provider information

The wheel metadata also includes the provider metadata dictionary,
keyed on namespaces. This dictionary is obligatory, and must include
the metadata for all namespaces that are listed in default namespace
priorities. The values include the following information:

- The *plugin API* value that specifies how to load plugins. It is
  obligatory. It follows the same format as object references
  in the [entry points specification](
  https://packaging.python.org/en/latest/specifications/entry-points/),
  that is:

  ```
  importable.module:ClassName
  ```

  The plugin will be instantiated by the equivalent of:

  ```python
  import importable.module

  plugin_instance = importable.module.ClassName()
  ```

- The list of *plugin requirements* that consists of zero or more
  [dependency specifiers](
  https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
  specifying how the provider should be installed. This is optional, but it is
  necessary to support installing plugins in an isolated environment.

- An optional *enable-if* clause that specifies an [environment marker](
  https://packaging.python.org/en/latest/specifications/dependency-specifiers/#environment-markers)
  specifying when the plugin should be used. If it specified, the plugin
  will not be installed and loaded if the environment does not match
  the specified markers. If it not specified, the plugin is enabled
  unconditionally.


## `pyproject.toml` file

### Base information

The `pyproject.toml` file is the standard project configuration file
as defined in [pyproject.toml specification](
https://packaging.python.org/en/latest/specifications/pyproject-toml/#pyproject-toml-spec).
Variant-enabled packages utilize a dedicated top-level `variant` table.

### Example contents

```toml
[variant.default-priorities]
namespace = ["x86_64", "aarch64"]
feature = ["x86_64::level"]
property = ["x86_64::avx2::on"]

[variant.providers.aarch64]
requires = [
    "provider-variant-aarch64 >=0.0.1,<1; python_version >= '3.9'",
    "legacy-provider-variant-aarch64 >=0.0.1,<1; python_version < '3.9'",
]
enable-if = "platform_machine == 'aarch64' or 'arm' in platform_machine"
plugin-api = "provider_variant_aarch64.plugin:AArch64Plugin"

[variant.providers.x86_64]
requires = ["provider-variant-x86-64 >=0.0.1,<1"]
enable-if = "platform_machine == 'x86_64' or platform_machine == 'AMD64'"
plugin-api = "provider_variant_x86_64.plugin:X8664Plugin"
```

### `default-priorities` subtable

The `variant.default-priorities` table contains the [default prority
information](#default-priorities). It may contain the following keys:

- `namespace` specifying the default namespace priority list. This is
  a list of strings, where every string must be a namespace name.
  As indicated in the common metadata section, this key is obligatory.

- `feature` specifying the default feature priority list. This is a list
  of the canonical feature strings (`namespace :: feature`). This key
  is optional.

- `property` specifying the default property priority list. This is
  a list of the canonical property strings
  (`namespace :: feature :: value`). This key is optional.

### `providers` subtable

The `variant.providers` table contains the [provider information](
#provider-information). It contains subtables keyed after namespaces,
and must contain a subtable for every namespace specified
in `variant.default-priorities.namespace` list.

Every subtable may contain the following keys:

- `plugin-api` that is a string forming the object reference used
  to load the plugin. It is required.

- `requires` that is a list of strings, where every string is
  a dependency specifier expressing how to install the provider plugin.
  It is optional, but it is necessary to support installing plugins
  in an isolated environment.

- `enable-if` that is a string forming an environment marker,
  specifying the condition under which the plugin is enabled. It is
  optional, and the plugin is always enabled if it missing.


## Distribution metadata

### Base information

The distribution metadata is defined in the [core metadata
specifications](
https://packaging.python.org/en/latest/specifications/core-metadata/).
The wheel variant format adds headers corresponding to the common
metadata and to the wheel variant description.

### Example headers

```email
Metadata-Version: 2.1
Name: numpy
Version: 2.2.5
[...]
Variant-Property: x86_64 :: level :: v3
Variant-Hash: fa7c1393
Variant-Requires: aarch64: provider-variant-aarch64 >=0.0.1,<1; python_version >= '3.9'
Variant-Requires: aarch64: legacy-provider-variant-aarch64 >=0.0.1,<1; python_version < '3.9'
Variant-Enable-If: aarch64: platform_machine == 'aarch64' or 'arm' in platform_machine
Variant-Plugin-API: aarch64: provider_variant_aarch64.plugin:AArch64Plugin
Variant-Requires: x86_64: provider-variant-x86-64 >=0.0.1,<1
Variant-Enable-If: x86_64: platform_machine == 'x86_64' or platform_machine == 'AMD64'
Variant-Plugin-API: x86_64: provider_variant_x86_64.plugin:X8664Plugin
Variant-Default-Namespace-Priorities: x86_64, aarch64
Variant-Default-Feature-Priorities: x86_64 :: level
Variant-Default-Property-Priorities: x86_64 :: avx2 :: on
```

### Default priority headers

The [default prority information](#default-priorities) is mapped into
three headers:

- `Variant-Default-Namespace-Priorities` containing the default
  namespace priorities. This header must occur exactly once.

- `Variant-Default-Feature-Priorities` containing the default feature
  priorities. This header must occur at most once.

- `Variant-Default-Property-Priorities` containing the default property
  priorities. This header must occur at most once.

The value corresponding to each of these headers is a comma-separated
list of the canonical string forms.

### Provider information headers

The [provider information](#provider-information) is mapped into three
headers:

- `Variant-Plugin-API` containing the object reference string to load
  the plugin. It must occur exactly once for every namespace.

- `Variant-Requires` specifying a single dependency for a given
  provider. It is optional, and can occur multiple times for the same
  namespace, in order to specify multiple dependencies.

- `Variant-Enable-If` specifying the condition for when the plugin
  is enabled. It is optional, and can occur at most once for every
  namespace. When missing, the plugin is always enabled.

The values of these headers are expressed using the following form:

```
namespace: value
```

Therefore, the headers are repeated for every provider namespace.

### Variant description headers

In addition to the common metadata, distribution metadata includes
two headers containing wheel variant description:

- `Variant-Hash` is a 8-character hexadecimal number representing
  the variant hash. It must occur exactly once, and match the value
  found in the filename.

- `Variant-Property` specifies a single property of the built variant,
  in its canonical string form (`namespace :: feature :: value`).
  This header can be repeated to specify multiple properties. It can
  also be omitted if the wheel is so-called null variant.


## `variants.json` files

### Base information

For every package version that includes at least one variant wheel,
there must exist a corresponding `{name}-{version}-variants.json`
file, where the package name and version are normalized according
to the same rules as wheel files, as found in the [Binary Distribution
Format specification](
https://packaging.python.org/en/latest/specifications/binary-distribution-format/#escaping-and-unicode).
The link to this file must be present on all index pages where
the variant wheels are linked, to facilitate discovery.

This file must be a valid JSON document, whose top-level element
is an object. Aside from common variant metadata, the JSON file contains
the dictionary of all available variants. Said dictionary must contain
information for all variants found in the index. It can also list
additional variants, to facilitate sharing the same file between
multiple packages.

### Example file

```json
{
    "default-priorities": {
        "feature": [
            "x86_64 :: level"
        ],
        "namespace": [
            "x86_64",
            "aarch64"
        ],
        "property": [
            "x86_64 :: avx2 :: on"
        ]
    },
    "providers": {
        "aarch64": {
            "enable-if": "platform_machine == 'aarch64' or 'arm' in platform_machine",
            "plugin-api": "provider_variant_aarch64.plugin:AArch64Plugin",
            "requires": [
                "provider-variant-aarch64 >=0.0.1,<1; python_version >= '3.9'",
                "legacy-provider-variant-aarch64 >=0.0.1,<1; python_version < '3.9'"
            ]
        },
        "x86_64": {
            "enable-if": "platform_machine == 'x86_64' or platform_machine == 'AMD64'",
            "plugin-api": "provider_variant_x86_64.plugin:X8664Plugin",
            "requires": [
                "provider-variant-x86-64 >=0.0.1,<1"
            ]
        }
    },
    "variants": {
        "40aba78e": {
            "x86_64": {
                "level": "v2"
            }
        },
        "fa7c1393": {
            "x86_64": {
                "level": "v3"
            }
        }
    }
}
```

### Default priority object

The [default prority information](#default-priorities) is mapped into
the `default-priorities` first-order object. It may contain
the following keys:

- `namespace` containing the default namespace priorities. This key
  is obligatory.

- `feature` containing the default feature priorities. This key
  is optional.

- `property` containing the default property priorities. This key
  is optional.

The values corresponding to the keys must be arrays of canonical string
forms.

### Provider information object

The [provider information](#provider-information) is mapped into
the `providers` first-order object. Its keys correspond to namespaces,
while values are objects that may contain the following keys:

- `plugin-api` containing the object reference string to load
  the plugin. It is obligatory.

- `requires` specifying dependencies for a given provider. It is
  optional. If specified, it must be an array of dependency strings.

- `enable-if` specifying the environment marker string for when
  the plugin is enabled. It is optional. When missing, the plugin
  is always enabled.

### Variants object

In addition to the common metadata, the JSON file must contain
a first-order `variants` object. Its keys correspond to the known
variant hashes (as 8-character hexadecimal numbers), while values
contain compacted variant properties.

For the purpose of compacting, all features from a single namespace
are collected in a single object, whose keys correspond to feature names
and values to their values. Afterwards, these objects are used as values
for objects whose keys are namespaces.
