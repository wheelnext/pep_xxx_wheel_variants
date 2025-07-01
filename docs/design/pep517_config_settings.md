# PEP517 config settings

## Purpose

This documents documents the PEP517 build backend `config_settings` API
used in [the variant-capable fork of meson-python](
https://github.com/wheelnext/meson-python/tree/wheel-variants).


## Configuration keys

The following configuration keys are recognized:

- `variant` specifying one or more variant properties as strings
- `variant-name` specifying one or more variant properties as strings
- `variant-label` specifying the variant label as a string
- `null-variant` taking any string to enable building a null variant

As the result of existing design, all these configuration keys take
string values, or in case of multi-value keys strings or lists
of strings.


### `variant` and `variant-name`

The `variant` and `variant-name` keys take variant properties
in the string `namespace :: feature :: value` form. For user
convenience, spaces are optional.

The `variant` key specifies properties that are passed down
to the `meson setup` operation as a `variant` option. The option
is given a list of variant properties passed via the key in string form.
The build system in question must support the relevant option, e.g.:

```meson
option('variant', type: 'array', value: [], description: 'Wheel variant keys')
```

The `variant-name` key specifies properties that are added to the wheel
metadata but not passed down to `meson setup`.

The total set of properties used for the variant wheel is the union
of properties passed via `variant` and `variant-name`.


### `variant-label`

The `variant-label` key can be used to override the label used
in the built variant wheel. If it is not specified, the variant hash
is used instead.


### `null-variant`

The `null-variant` key enables building a null variant. It can take
any string (including an empty string).

When a null variant is built, `variant`, `variant-name`
and `variant-label` keys must not be present.


## Examples

```console
# Build a x86_64::level::v3 variant, passing it down to meson
# produces: ...-fa7c1393.whl
python -m build -w -Cvariant=x86_64::level::v3

# Build a x86_64::level::v3 variant without explicit meson support
# produces: ...-fa7c1393.whl
export CFLAGS='-march=x86-64-v3'
python -m build -w -Cvariant-name=x86_64::level::v3

# Build a x86_64::level::v3 + x86_64::aes variant
# produces: ...-7e3cb5eb.whl
python -m build -w -Cvariant=x86_64::level::v3 -Cvariant=x86_64::aes::on

# Build a x86_64::level::v3 variant with a custom label
# produces: ...-x8664v3.whl
python -m build -w -Cvariant=x86_64::level::v3 -Cvariant-label=x8664v3

# Build a null variant
# produces: ...-00000000.whl
python -m build -w -Cnull-variant
```
