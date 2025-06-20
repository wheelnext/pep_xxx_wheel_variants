# Base definitions for wheel variants

## Purpose

This document aims to streamline the terminology used within the code, project
documentation and discussions.

## Variants

_Variant wheels_ refer to wheels that share the same distribution name, version,
build number and compatible tags, but have different contents and are
distinguished by unique variant properties. For example, variant wheels may
provide package versions built for different accelerators, CPU optimizations,
etc.

Variant wheels function as an extension of the wheel format. A particular
distribution may feature a regular (non-variant) wheel in addition to variant
wheels, in which case it serves both as a lowest-precedence variant, and as a
fallback for installers that do not support variants.

## Variant descriptions, properties, features

_Variant description_ is the whole set of metadata describing a particular
variant. It consists of one or more variant properties, and it has a
corresponding _variant hash_.

_Variant property_ is a 3-tuple describing a single specific feature that the
variant was built for. It has a form of:

    namespace :: feature-name :: feature-value

For example:

    CUDA :: runtime :: 12.8

_Namespace_ identifies the plugin providing particular features, and must be
globally unique. For example, the `CUDA` namespace is claimed by a CUDA plugin,
and all feature provided by that plugin will use that namespace.

_Feature name_ names the particular feature within the plugin, and must be
unique within the namespace. For example, the `runtime` feature name within the
`CUDA` namespace identifies the CUDA runtime version.

_Feature_ is a term referring to all possible values corresponding to a
particular `(namespace, feature-name)` pair: `CUDA :: runtime` in the example.

_Feature value_ is the selected feature value for the given variant. It must be
unique within the feature. In the example, `CUDA :: runtime` feature has a value
of `12.8`.

## Plugins

_Plugins_ provide the underlying architecture for building and installing
variant wheels. Every plugin claims a single namespace. The plugin defines all
valid feature names and values within that namespace, as well as their meanings.

A plugin implements a specific API that provides routines to:

- query all valid feature names and values

- query feature names and versions that are compatible with the environment in
  question, as well as their relative precedence (possibly none)

For example, the CUDA plugin both defines all valid values for
`CUDA :: runtime`, i.e. all known CUDA runtime versions, but also indicates
which values are valid for a given environment. That is, it detects whether CUDA
runtime is installed, and either returns a preference-sorted list of compatible
CUDA runtime versions, or indicates that the runtime is not installed and no
CUDA variants can be installed.
