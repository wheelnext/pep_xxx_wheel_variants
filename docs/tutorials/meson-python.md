# Building variant wheels with meson-python

## Purpose

This document provides a quick guide how to utilize [the variant-capable
fork of `meson-python`](
https://github.com/wheelnext/meson-python/tree/wheel-variants) in order
to build variant wheels. We also provide [a forked version of NumPy
with sample variant configuration](
https://github.com/wheelnext/numpy/tree/wheel-variants).


## Determining the plugins to use

Provider plugins determine the available variants. Currently,
the wheelnext project provides the following plugins:

| Package                                                                           | Use case                                | Example property             | `plugin-api`                                         |
|-----------------------------------------------------------------------------------|-----------------------------------------|------------------------------|------------------------------------------------------|
| [nvidia-variant-provider](https://github.com/wheelnext/nvidia-variant-provider)   | CUDA driver version                     | `nvidia :: cuda :: 12.8`     | `nvidia_variant_provider.plugin:NvidiaVariantPlugin` |
| [provider-variant-aarch64](https://github.com/wheelnext/provider-variant-aarch64) | ARM architecture version, extensions    | `aarch64 :: version :: 8.3a` | `provider_variant_aarch64.plugin:AArch64Plugin`      |
| [provider-variant-x86-64](https://github.com/wheelnext/provider-variant-x86-64)   | x86_64 architecture version, extensions | `x86_64 :: level :: 3`       | `provider_variant_x86_64.plugin:X8664Plugin`         |

To determine the exact list of properties available, install the plugin,
`variantlib` and use the `variantlib plugins` commands, e.g.:

```console
$ pip install -q git+https://github.com/wheelnext/provider-variant-aarch64 git+https://github.com/wheelnext/variantlib
$ variantlib plugins -p provider_variant_aarch64.plugin:AArch64Plugin get-all-configs
variantlib.plugins.py_envs - INFO - Using externally managed python environment
variantlib.plugins.loader - INFO - Loading plugin via provider_variant_aarch64.plugin:AArch64Plugin
aarch64 :: version :: 8.1a
aarch64 :: version :: 8.2a
aarch64 :: version :: 8.3a
aarch64 :: version :: 8.4a
aarch64 :: version :: 8.5a
aarch64 :: version :: 8a
aarch64 :: version :: 9.0a
```

The package names and links to repositories are provided in the first
column, while the `plugin-api` argument to `-p` is provided in the last.

## Updating `pyproject.toml`

To enable variant support within a project using `meson-python`,
the following changes need to be made to its `pyproject.toml` file:

1. The `build-system.requires` list must use the wheelnext fork
   of `meson-python`. It must also list all provider plugins that
   the package in question is going to use. For example:

   ```toml
   [build-system]
   build-backend = "mesonpy"
   requires = [
       "meson-python @ https://github.com/wheelnext/meson-python/archive/wheel-variants.tar.gz",
   ]
   ```

   Note that since the relevant packages are still in development
   and are not published on PyPI, the lists includes URLs to download
   their git archives.

2. `variant.providers.*` section need to be added, indicating how to
   install the provider plugins, and how to import their provider
   classes. For example:

   ```toml
   [variant.providers.aarch64]
   requires = ["provider-variant-aarch64 @ https://github.com/wheelnext/provider-variant-aarch64/archive/main.tar.gz"]
   plugin-api = "provider_variant_aarch64.plugin:AArch64Plugin"

   [variant.providers.x86_64]
   requires = ["provider-variant-x86-64 @ https://github.com/wheelnext/provider-variant-x86-64/archive/dev.tar.gz"]
   plugin-api = "provider_variant_x86_64.plugin:X8664Plugin"
   ```

   The last component of the table name must correspond to the plugin's
   property namespace. The `requires` key indicates how to install
   the plugin, whereas the `plugin-api` key needs to be the value
   taken from the plugin table.

3. Finally, a list of namespace priorities needs to be defined for
   the plugins that will be installed by default. The list will
   determine which variants will take precedence when installing.
   For example:

   ```toml
   [variant.default-priorities]
   namespace = ["aarch64", "x86_64"]
   ```

   Note that in this particular case the variants are mutually
   exclusive, so the actual order does not matter.


## Building without explicit `meson.build` support

At this point, it is already possible to start building variant wheels.
For example, to build a wheel for `x86_64 :: level :: v3` baseline,
the following command can be used:

```console
$ pip install -q build
$ pyproject-build -w -Cvariant-name=x86_64::level::v3
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - Cython >= 3.0.6
  - meson-python @ https://github.com/wheelnext/meson-python/archive/wheel-variants.tar.gz
* Getting build dependencies for wheel...
* Installing packages in isolated environment:
  - provider-variant-x86-64 @ https://github.com/wheelnext/provider-variant-x86-64/archive/dev.tar.gz
* Building wheel...
+ /tmp/build-env-l7iyan__/bin/python /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/vendored-meson/meson/meson.py setup /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/.mesonpy-kwf3nvob -Dbuildtype=release -Db_ndebug=if-release -Db_vscrt=md --native-file=/home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/.mesonpy-kwf3nvob/meson-python-native-file.ini
The Meson build system
Version: 1.5.2
Source dir: /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy
Build dir: /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/.mesonpy-kwf3nvob
Build type: native build
Project name: NumPy
Project version: 2.2.5
C compiler for the host machine: ccache cc (gcc 14.2.1 "cc (Gentoo 14.2.1_p20250419 p8) 14.2.1 20250419")
C linker for the host machine: cc ld.bfd 2.44
C++ compiler for the host machine: ccache c++ (gcc 14.2.1 "c++ (Gentoo 14.2.1_p20250419 p8) 14.2.1 20250419")
C++ linker for the host machine: c++ ld.bfd 2.44
Cython compiler for the host machine: cython (cython 3.1.0)
Host machine cpu family: x86_64
Host machine cpu: x86_64
Program python found: YES (/tmp/build-env-l7iyan__/bin/python)
Found pkg-config: YES (/usr/bin/pkg-config) 2.4.3
Run-time dependency python found: YES 3.13
Has header "Python.h" with dependency python-3.13: YES 
Compiler for C supports arguments -fno-strict-aliasing: YES 
Message: Appending option "detect" to "cpu-baseline" due to detecting global architecture c_arg "-march=x86-64-v3"
[...]
Message:
CPU Optimization Options
  baseline:
    Requested : min+detect
    Enabled   : SSE SSE2 SSE3 SSSE3 SSE41 POPCNT SSE42 AVX F16C FMA3 AVX2
  dispatch:
    Requested : max -xop -fma4
    Enabled   : AVX512F AVX512CD AVX512_KNL AVX512_KNM AVX512_SKX AVX512_CLX AVX512_CNL AVX512_ICL AVX512_SPR
[...]
Successfully built numpy-2.2.5-cp313-cp313-linux_x86_64-fa7c1393.whl
```

The `-Cvariant-name=...` option specifies the variant property to build
for. It can be used multiple times to combine multiple properties.
In the case of `aarch64 :: version` and `x86_64 :: level` properties,
this option also automatically adjusts compiler flags to build
for the specified baseline. In case of other plugins and properties,
a manual setup may be necessary to ensure that the specified variant
is actually built — rather than just marked.


## Updating `meson.build` (optional)

In addition to using the standard provider plugin functionality, it is
also possible to explicitly pass built variant properties to the Meson
build system. In order to facilitate this, the `variant` option needs
to be added to `meson.options` (or `meson_options.txt`) file:

```meson
option('variant', type: 'array', value: [],
        description: 'Wheel variant keys')
```

The option takes an array of variant properties
in the `namespace :: feature :: value` form. For example, the following
code can be used in `meson.build` to get the value
of `x86_64 :: level` feature and put it into `x86_64_variant` varible,
if used:

```meson
x86_64_variant = ''

foreach vprop : get_option('variant')
  split_prop = vprop.split('::')
  if split_prop.length() != 3
    error('Invalid variant property: ' + vprop)
  endif
  if split_prop[0].strip() == 'x86_64' and split_prop[1].strip() == 'level'
    if host_machine.cpu_family() != 'x86_64'
      error('Variant valid only on x86_64: ' + vprop)
    endif
    x86_64_variant = split_prop[2].strip()
  else
    error('Unsupported variant property: ' + vprop)
  endif
endforeach
```

To use this option, `-Cvariant=` option needs to be used instead of
`-Cvariant-name=`. Variant properties specified via this option are
additionally passed to `meson setup`:

```console
$ pyproject-build -w -Cvariant=x86_64::level::v3
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - Cython >= 3.0.6
  - meson-python @ https://github.com/wheelnext/meson-python/archive/wheel-variants.tar.gz
* Getting build dependencies for wheel...
* Installing packages in isolated environment:
  - provider-variant-x86-64 @ https://github.com/wheelnext/provider-variant-x86-64/archive/dev.tar.gz
* Building wheel...
+ /tmp/build-env-i6vx2yun/bin/python /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/vendored-meson/meson/meson.py setup /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy /home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/.mesonpy-fs73v6oq -Dbuildtype=release -Db_ndebug=if-release -Db_vscrt=md -Dvariant=['x86_64 :: level :: v3'] --native-file=/home/mgorny/git/wheelnext/pep_xxx_wheel_variants/numpy/.mesonpy-fs73v6oq/meson-python-native-file.ini
[...]
Message:
CPU Optimization Options
  baseline:
    Requested : AVX2
    Enabled   : SSE SSE2 SSE3 SSSE3 SSE41 POPCNT SSE42 AVX F16C FMA3 AVX2
  dispatch:
    Requested :
    Enabled   :
[...]
Successfully built numpy-2.2.5-cp313-cp313-linux_x86_64-fa7c1393.whl
```

Note that the `-Cvariant` property resulted in `-Dvariant` option
being passed to `meson setup`, which in turn changed the CPU
optimization options.
