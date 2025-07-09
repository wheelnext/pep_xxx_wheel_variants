# Metadata format

## Purpose

This document describes the metadata format used for variant wheels.
The format is used in three locations, with slight variations:

1. in the source repository, as a `pyproject.toml` file,

2. in the built wheel, as a `*.dist-info/variant.json` file,

3. on the wheel index, as a `*-variants.json` file.

All three variants share a common structure, with some of its element
shared across all of them, and some being specific to a single variant,
as described further in the document. This structure is then serialized
into TOML or JSON appropriately.

These variations fit into the common wheel building pipeline where
a source tree is used to build one or more wheels, and the wheels
are afterwards published on an index. The `pyproject.toml` file
provides the metadata needed to build the wheels, as well as the shared
metadata needed to install them. This metadata is then amended with
information on the specific variant build, and copied into the wheel.
When wheels are uploaded into the index, the metadata from all of them
is read and merged into a single JSON file that can be used
by the client to efficiently evaluate the available variants without
having to fetch metadata from every wheel separately.


## The metadata structure

### The metadata tree

The metadata is a dictionary rooted at a specific point, specified
for each file separately. The top-level keys of this dictionary
are strings corresponding to specific metadata blocks, and their values
are further dictionaries representing this blocks. The complete
structure can be visualized using the following tree:

```
(root)
|
+-- providers
|   +- <namespace>
|      +- requires      : list[str]
|      +- enable-if     : str | None
|      +- plugin-api    : str | None
|      +- optional      : bool = False
|
+-- default-priorities
|   +- namespace        : list[str]
|   +- feature
|      +- <namespace>   : list[str]
|   +- property
|      +- <namespace>
|         +- <feature>  : list[str]
|
+-- variants
    +- <variant-label>
       +- <namespace>
          +- <feature>  : list[str]
```

### Provider information

```
+-- providers
|   +- <namespace>
|      +- requires      : list[str]
|      +- enable-if     : str | None
|      +- plugin-api    : str | None
|      +- optional      : bool = False
```

The wheel metadata includes the provider metadata dictionary that
specifies which variant providers (plugins) are available, under what
conditions they are used, how to install them and how to use them.

It resides under the `providers` key. It is a dictionary using namespace
names as keys, with values being dictionaries describing the provider
for a given namespace. This sub-dictionary has up to three keys:

1. `requires: list[str]` -- that specifies one or more [dependency specifiers](
   https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
   specifying how the provider should be installed. This key is required.

2. `enable-if: str | None` -- that optionally specifies an [environment marker](
   https://packaging.python.org/en/latest/specifications/dependency-specifiers/#environment-markers)
   specifying when the plugin should be used. If it specified, the plugin
   will not be installed and loaded if the environment does not match
   the specified markers. If it not specified, the plugin is enabled
   unconditionally.

3. `plugin-api: str` -- that specifies how to load plugins. If specified,
   it follows the same format as object references
   in the [entry points specification](
   https://packaging.python.org/en/latest/specifications/entry-points/).
   It can be one of:

   - `importable.module:ClassName`
   - `importable.module:attribute`
   - `importable.module`

   If not specified, it will be inferred from the first package name
   found in `requires`, with any dashes replaced with underscores.
   For example, if the dependency is `foo-bar[extra] >= 1.2.3`,
   its corresponding `plugin-api` will be inferred as `foo_bar`.

   If a callable is specified, the provider will be instantiated
   by the equivalent of:

   ```python
   import importable.module

   plugin_instance = importable.module.ClassName()
   ```

   If a non-callable object (e.g. a module or a global object)
   is specified, it will be used directly, similarly to:

   ```python
   import importable.module

   plugin_instance = importable.module.attribute
   ```

4. `optional: bool = False` -- that can be used to make a particular
   provider optional. If it is False or not specified, the plugin
   is required and is used unconditionally. If it is True, the plugin
   is considered optional and the tools should not load it unless
   explicitly requested by the user.


### Default priorities

```
+-- default-priorities
|   +- namespace        : list[str]
|   +- feature
|      +- <namespace>   : list[str]
|   +- property
|      +- <namespace>
|         +- <feature>  : list[str]
```

The default priority block is used to establish the default preferences
between variants. It must specify the order for all namespaces used
by the package. It may also override the priorities of individual
features and property values provided by the plugins. The priorities
specified here can in turn be overridden by the user.

The block resides under the `default-priorities` key. It is a dictionary
with up to three keys:

1. `namespace: list[str]` -- that lists all namespaces used
   by the package from the most preferred to the least preferred.

2. `feature` -- that can be used to override preferred feature order
   of individual providers. It is a dictionary whose keys are namespaces,
   and values are lists of feature names. The features are listed from
   the most preferred to the least preferred. Not all features provided
   by the plugin need be listed. The remaining features will be given
   lower priority than these listed, while preserving their relative
   order provided by the plugin.

3. `property` -- that can be used to override preferred property value
   order of individual providers. It consists of two nested dictionaries,
   with the key of the top dictionary specifying the namespace name,
   and the key of the subsequent dictionary specifying the feature name.
   The values are property values, ordered from the most preferred
   to the least preferred. Conversely, not all property values provided
   by the plugin need be listed. The remaining properties will be given
   lower priority than these listed, while preserving their relative
   order provided by the plugin.


### Variants

```
+-- variants
    +- <variant-label>
       +- <namespace>
          +- <feature>  : str
```

The variants block is present only in wheel metadata, and in wheel
index `*-variants.json` file. In both cases it is obligatory.
In the former file, it specifies the variant that the wheel was built
for. In the latter, it lists all variants available for the package
version.

It resides under the `variants` key. It is a dictionary using variant
labels as keys, with values listing the properties for a given variant
in a form of a nested dictionary. The keys of the top dictionary
specify namespaces names, the keys of the subsequent dictionary feature
names and their values are the corresponding property values.


## Specific file formats

### `pyproject.toml`

The `pyproject.toml` file is the standard project configuration file
as defined in [pyproject.toml specification](
https://packaging.python.org/en/latest/specifications/pyproject-toml/#pyproject-toml-spec).
The variant metadata is rooted at the top-level `variant` table.
This format does not include the `variants` dictionary.

Example `pyproject.toml` tables, with explanatory comments:

```toml
[variant.default-priorities]
# prefer x86_64 plugin over aarch64
namespace = ["x86_64", "aarch64"]
# prefer aarch64 version and x86_64 level features over other features
# (specific CPU extensions like "sse4.1")
feature.aarch64 = ["version"]
feature.x86_64 = ["level"]
# prefer x86-64-v3 and then older (even if CPU is newer)
property.x86_64.level = ["v3", "v2", "v1"]

[variant.providers.aarch64]
# example using different package based on Python version
requires = [
    "provider-variant-aarch64 >=0.0.1,<1; python_version >= '3.9'",
    "legacy-provider-variant-aarch64 >=0.0.1,<1; python_version < '3.9'",
]
# use only on aarch64/arm machines
enable-if = "platform_machine == 'aarch64' or 'arm' in platform_machine"
plugin-api = "provider_variant_aarch64.plugin:AArch64Plugin"

[variant.providers.x86_64]
requires = ["provider-variant-x86-64 >=0.0.1,<1"]
# use only on x86_64 machines
enable-if = "platform_machine == 'x86_64' or platform_machine == 'AMD64'"
plugin-api = "provider_variant_x86_64.plugin:X8664Plugin"
```

### `*.dist-info/variant.json`

The `variant.json` file is placed inside variant wheels,
in the `*.dist-info` directory containing the wheel metadata. It is
serialized into JSON, with variant metadata dictionary being the top
object. In addition to the shared metadata copied from `pyproject.toml`,
it contains a `variants` object that must list exactly one variant --
the variant provided by the wheel.

The `default-priorities` and `providers` for all wheels of the same package
version on the same index must be the same and be equal to value in
`*-variants.json`.

The `variant.json` file corresponding to the wheel built from
the example `pyproject.toml` file for x86-64-v3 would look like:

```json
{
    "default-priorities": {
        "feature": {
            "aarch64": [
                "version"
            ],
            "x86_64": [
                "level"
            ]
        },
        "namespace": [
            "x86_64",
            "aarch64"
        ],
        "property": {
            "x86_64": {
                "level": [
                    "v3",
                    "v2",
                    "v1"
                ]
            }
        }
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
        "fa7c1393": {
            "x86_64": {
                "level": ["v3"]
            }
        }
    }
}
```

### `*-variants.json`

For every package version that includes at least one variant wheel,
there must exist a corresponding `{name}-{version}-variants.json`
file, where the package name and version are normalized according
to the same rules as wheel files, as found in the [Binary Distribution
Format specification](
https://packaging.python.org/en/latest/specifications/binary-distribution-format/#escaping-and-unicode).
The link to this file must be present on all index pages where
the variant wheels are linked, to facilitate discovery.

This file uses the same structure as `variant.json`, except that
the `variants` object is permitted to list multiple variants, and should
list all variants available for the package version in question.

The file can be created from existing variant wheels using the following
command:

```console
$ variantlib generate-index-json -d dist/
variantlib.commands.generate_index_json - INFO - Processing wheel: `numpy-2.2.5-cp313-cp313-linux_x86_64-40aba78e.whl` with variant label: `40aba78e`
variantlib.commands.generate_index_json - INFO - Processing wheel: `numpy-2.2.5-cp313-cp313-linux_x86_64-fa7c1393.whl` with variant label: `fa7c1393`
```

The `foo-1.2.3-variants.json` corresponding to the package with two
wheel variants, one of them listed in the previous example, would look
like:

```json
{
    "default-priorities": {
        "feature": {
            "aarch64": [
                "version"
            ],
            "x86_64": [
                "level"
            ]
        },
        "namespace": [
            "x86_64",
            "aarch64"
        ],
        "property": {
            "x86_64": {
                "level": [
                    "v3",
                    "v2",
                    "v1"
                ]
            }
        }
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
                "level": ["v2"]
            }
        },
        "fa7c1393": {
            "x86_64": {
                "level": ["v3"]
            }
        }
    }
}
```
