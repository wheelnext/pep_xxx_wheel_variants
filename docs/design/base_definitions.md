# Base definitions for wheel variants

## Purpose

This document aims to streamline the terminology used within the code,
project documentation and discussions.


## Variants

*Variant wheels* refer to wheels that share the same distribution name,
version, build number and compatible tags, but have different contents
and are distinguished by unique variant properties. For example, variant
wheels may provide package versions built for different accelerators,
CPU optimizations, etc.

Variant wheels function as an extension of the wheel format.
A particular distribution may feature a regular (non-variant) wheel
in addition to variant wheels, in which case it serves both
as a lowest-precedence variant, and as a fallback for installers that
do not support variants.


## Variant descriptions, properties, features

*Variant description* is the whole set of metadata describing
a particular variant.  It consists of zero or more variant properties,
and it has a corresponding *variant hash*.

*Variant property* is a 3-tuple describing a single specific feature
that the variant was built for.  It has a form of:

    namespace :: feature-name :: feature-value

For example:

    CUDA :: runtime :: 12.8

*Namespace* identifies the plugin providing particular features,
and must be globally unique. For example, the `CUDA` namespace
is claimed by a CUDA plugin, and all feature provided by that plugin
will use that namespace.

*Feature name* names the particular feature within the plugin, and must
be unique within the namespace. For example, the `runtime` feature name
within the `CUDA` namespace identifies the CUDA runtime version.

*Feature* is a term referring to all possible values corresponding
to a particular `(namespace, feature-name)` pair: `CUDA :: runtime`
in the example.

*Feature value* is the selected feature value for the given variant.
It must be unique within the feature. In the example, `CUDA :: runtime`
feature has a value of `12.8`.


## Null variant

The *null variant* is a special variant with zero properties. For this
variant, the special variant hash value of `00000000` is used. The null
variant is always considered supported. All non-null variants are
preferred over it, but it is preferred over the non-variant wheel.

Null variants can only be installed by package managers supporting
variant wheels. An example use case is a package that provides:

- one or more GPU-accelerated variants that are used when
  the appropriate GPU acceleratio is available,

- a null CPU-only variant that is used when no GPU acceleration
  is available,

- a regular CPU+GPU wheel that is larger than the other wheels, and it
  is used when variant wheels are not supported and therefore it is
  impossible to automatically select a wheel matching the available
  acceleration.


## Variant label, wheel filename

*Variant label* is a string that is added to the wheel filename
to uniquely identify it as a specific variant. It defaults
to the variant hash, but a custom string up to 8 characters can be used
instead to provide a human-readable label for the variant.

Therefore the complete wheel filename follows the following template:

```
{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}(-{variant label})?.whl
```

Variant wheel filename examples follow:

- a regular wheel: `example-1.0.0-py3-none-any.whl
- variant wheel with hash: `example-1.0.0-py3-none-any-abcd1234.whl`
- variant wheel with custom label: `example-1.0.0-py3-none-any-accel.whl`



## Plugins

*Plugins* provide the underlying architecture for building
and installing variant wheels. Every plugin claims a single namespace.
The plugin defines all valid feature names and values within that
namespace, as well as their meanings.

A plugin implements a specific API that provides routines to:

- query all valid feature names and values

- query feature names and versions that are compatible with
  the environment in question, as well as their relative precedence
  (possibly none)

For example, the CUDA plugin both defines all valid values
for `CUDA :: runtime`, i.e. all known CUDA runtime versions, but also
indicates which values are valid for a given environment.  That is,
it detects whether CUDA runtime is installed, and either returns
a preference-sorted list of compatible CUDA runtime versions,
or indicates that the runtime is not installed and no CUDA variants
can be installed.
