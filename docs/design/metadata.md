# Metadata format

## Purpose

This document describes the metadata format used for variant wheels.
The format is used in three locations, with slight variations:

1. in the source repository, as a `pyproject.toml` file,

2. in the built wheel, as a `*.dist-info/variant.json` file,

3. on the wheel index, as a `{name}-{version}-variants.json` file.

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
+- providers
|  +- <namespace>
|     +- enable-if     : str | None
|     +- install-time  : bool = True
|     +- optional      : bool = False
|     +- plugin-api    : str | None
|     +- requires      : list[str]
|
+- default-priorities
|  +- namespace        : list[str]
|  +- feature
|     +- <namespace>   : list[str]
|  +- property
|     +- <namespace>
|        +- <feature>  : list[str]
|
+- static-properties
|  +- <namespace>
|     +- <feature>     : list[str]
|
+- variants
   +- <variant-label>
      +- <namespace>
         +- <feature>  : list[str]
```

### Provider information

```
+- providers
|  +- <namespace>
|     +- enable-if     : str | None
|     +- install-time  : bool = True
|     +- optional      : bool = False
|     +- plugin-api    : str | None
|     +- requires      : list[str]
```

`providers` is a dictionary, the keys are namespaces, the values are
dictionaries with provider information. It specifies how to install and
use variant providers. A provider information dictionary must be
declared in `pyproject.toml` for every supported variant namespace. It
must be copied to `variant.json` as-is, including data for providers
that are not used in the particular wheel.

A provider information dictionary can contain the following keys:

- `enable-if: str`: An environment marker defining when the plugin
  should be used. If the environment marker does not match the running
  environment, the provider will be disabled and the variants using its
  properties will be deemed incompatible. If not provided, the plugin
  will be used in all environments.

- `install-time: bool`: Whether this is an install-time provider.
  Defaults to `true`. `false` means that it is an AoT provider instead.

- `optional: bool`: Whether the provider is optional, as a boolean
  value. Defaults to `false`. If it is true, the provider is considered
  optional and should not be used unless the user opts in to it,
  effectively rendering the variants using its properties incompatible.
  If it is false or missing, the provider is considered obligatory.

- `plugin-api: str`: The API endpoint for the plugin. If it is
  specified, it must be an object reference as explained in the "API
  endpoint" section. If it is missing, the package name from the first
  dependency specifier in `requires` is used, after replacing all `-`
  characters with `_` in the normalized package name.

- `requires: list[str]`: A list of one or more package dependency
  specifiers. When installing the provider, all the items are processed
  (provided their environment markers match), but they must always
  resolve to a single distribution to be installed. Multiple
  dependencies can be used when different plugins providing the same
  namespace need to be used conditionally to environment markers, e.g.
  for different Python versions or platforms.

For install-time providers (i.e. when `install-time` is true), the
`requires` key is obligatory. For AoT providers (i.e. otherwise), the
`requires` key is optional. If it specified, it needs to specify an AoT
provider plugin that is queried at build time to fill
`static-properties`. If it is not specified, `static-properties` need to
be specified in `pyproject.toml`.

### Default priorities

```
+- default-priorities
|  +- namespace        : list[str]
|  +- feature
|     +- <namespace>   : list[str]
|  +- property
|     +- <namespace>
|        +- <feature>  : list[str]
```

The `default-priorities` dictionary controls the ordering of variants.

It has a single required key:

- `namespace: list[str]`: All namespaces used by the wheel variants,
  ordered in decreasing priority.  This list must have the same members
  as the keys of the `providers` dictionary.

It may have the following optional keys:

- `feature: dict[str, list[str]]`: A dictionary with namespaces as keys,
  and ordered list of corresponding feature names as values. The values
  in each list override the default ordering from the provider output.
  They are listed from the highest priority to the lowest priority.
  Features not present on the list are considered of lower priority than
  those present, and their relative priority is defined by the plugin.

- `property: dict[str, dict[str, list[str]]]`: A nested dictionary with
  namespaces as first-level keys, feature names as second-level keys and
  ordered lists of corresponding property values as second-level values.
  The values present in the list override the default ordering from the
  provider output. They are listed from the the highest priority to the
  lowest priority.  Properties not present on the list are considered of
  lower priority than these present, and their relative priority is
  defined by the plugin output.

### Static properties

```
+- static-properties
|  +- <namespace>
|     +- <feature>     : list[str]
```

The `static-properties` dictionary specifies the supported properties
for AoT providers. It is a nested dictionary with namespaces as first
level keys, feature name as second level keys and ordered lists of
feature values as second level values.

In `pyproject.toml` file, the namespaces present in this dictionary in
`pyproject.toml` file must correspond to all AoT providers without a
plugin (i.e. with `install-time` of `false` and no `requires`). When
building a wheel, the build backend must query the AoT provider plugins
(i.e. these with `install-time` being false and non-empty `requires`) to
obtain supported properties and embed them into the dictionary.
Therefore, the dictionary in `variant.json` and `*-variants.json` must
contain namespaces for all AoT providers (i.e. all providers with
`install-time` being false).

Since TOML and JSON dictionaries are unsorted, so are the features in
the `static-properties` dictionary.  If more than one feature is
specified for a namespace, then the order for all features must be
specified in `default-priorities.feature.{namespace}`. If an AoT plugin
is used to fill `static-properties`, then the features not already in
the list in `pyproject.toml` must be appended to it.

The list of values is ordered from the most preferred to the least
preferred, same as the lists returned by `get_supported_configs()`
plugin API call. The `default-priorities.property` dict can be used to
override the property ordering.

### Variants

```
+- variants
   +- <variant-label>
      +- <namespace>
         +- <feature>  : list[str]
```

The `variants` dictionary is used in `variant.json` to indicate the
variant that the wheel was built for, and in `*-variants.json` to
indicate all the wheel variants available. It's a 3-level dictionary
listing all properties per variant label: The first level keys are
variant labels, the second level keys are namespaces, the third level
are feature names, and the third level values are lists of feature
values.

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
# prefer CPU features over BLAS/LAPACK variants
namespace = ["x86_64", "aarch64", "blas_lapack"]

# prefer aarch64 version and x86_64 level features over other features
# (specific CPU extensions like "sse4.1")
feature.aarch64 = ["version"]
feature.x86_64 = ["level"]

# prefer x86-64-v3 and then older (even if CPU is newer)
property.x86_64.level = ["v3", "v2", "v1"]

[variant.providers.aarch64]
# example using different package based on Python version
requires = [
    "provider-variant-aarch64 >=0.0.1; python_version >= '3.12'",
    "legacy-provider-variant-aarch64 >=0.0.1; python_version < '3.12'",
]
# use only on aarch64/arm machines
enable-if = "platform_machine == 'aarch64' or 'arm' in platform_machine"
plugin-api = "provider_variant_aarch64.plugin:AArch64Plugin"

[variant.providers.x86_64]
requires = ["provider-variant-x86-64 >=0.0.1"]
# use only on x86_64 machines
enable-if = "platform_machine == 'x86_64' or platform_machine == 'AMD64'"
plugin-api = "provider_variant_x86_64.plugin:X8664Plugin"

[variant.providers.blas_lapack]
# plugin-api inferred from requires
requires = ["blas-lapack-variant-provider"]
# plugin used only when building package, properties will be inlined
# into variant.json
install-time = false
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
the example `pyproject.toml` file for x86-64-v3 OpenBLAS variant would
look like:

```jsonc
{
   "default-priorities": {
      "feature": {
         "aarch64": ["version"],
         "x86_64": ["level"]
      },
      "namespace": ["x86_64", "aarch64", "blas_lapack"],
      "property": {
         "x86_64": {
            "level": ["v3", "v2", "v1"]
         }
      }
   },
   "providers": {
      "aarch64": {
         "enable-if": "platform_machine == 'aarch64' or 'arm' in platform_machine",
         "plugin-api": "provider_variant_aarch64.plugin:AArch64Plugin",
         "requires": [
            "provider-variant-aarch64 >=0.0.1; python_version >= '3.9'",
            "legacy-provider-variant-aarch64 >=0.0.1; python_version < '3.9'"
         ]
      },
      "blas_lapack": {
         "install-time": false,
         "requires": ["blas-lapack-variant-provider"]
      },
      "x86_64": {
         "enable-if": "platform_machine == 'x86_64' or platform_machine == 'AMD64'",
         "plugin-api": "provider_variant_x86_64.plugin:X8664Plugin",
         "requires": ["provider-variant-x86-64 >=0.0.1"]
      }
   },
   "static-properties": {
      "blas_lapack": {
         "provider": ["accelerate", "openblas", "mkl"]
      },
   },
   "variants": {
      // always a single entry, expressing the variant properties of the wheel
      "x8664v3_openblas": {
         "blas_lapack": {
            "provider": ["openblas"]
         },
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

```jsonc
{
   "default-priorities": {
      // identical to above
   },
   "providers": {
      // identical to above
   },
   "static-properties": {
      // identical to above
   },
   "variants": {
      // all available wheel variants
      "x8664v3_openblas": {
         "blas_lapack": {
            "provider": ["openblas"]
         },
         "x86_64": {
            "level": ["v3"]
         }
      },
      "x8664v4_mkl": {
         "blas_lapack": {
            "provider": ["mkl"]
         },
         "x86_64": {
            "level": ["v4"]
         }
      }
  }
}
```
