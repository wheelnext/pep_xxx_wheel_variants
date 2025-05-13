# Wheel Variants - Numpy Tutorial

This tutorial contains a simple demo of the `Wheel-Variant` implementation for `Numpy`.

> [!CAUTION]  
> This Wheel Variant Demo currently supports Linux, macOS on `X86_64` and `AArch64` CPU, and Windows x64.<br>
> There are no wheels for other platforms provided.

## Where to report issues / ask questions ?

Please go to: https://github.com/wheelnext/pep_xxx_wheel_variants/issues/new 

## A. Let's validate that an "old installer" is non-affected by any of these changes

### 1. Create a virtualenv to isolate your environment

```bash
# 1. Create a virtualenv
# WARNING: Installing Wheel-Variant PEP overwrites PIP.
# Do not install this in your main python environment.
$ python3 -m venv .venv
$ source .venv/bin/activate

# 2. Set the index to the WheelNext Static Wheel Server: MockHouse & Backup to PyPI
$ pip config set --site global.index-url https://variants-index.wheelnext.dev/
Writing to /path/to/venv/pip.conf
```

### 2. Test Install a Variant-Enabled package with "normal `pip`"

By doing this - It **should** install the normal package (aka. non variant), proving the backward compatibility of the design.

```bash
$ pip install --dry-run numpy

Looking in indexes: https://variants-index.wheelnext.dev/
Collecting numpy
  Using cached https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (15.6 MB)

Would install numpy-2.2.5
```

### What happened ?

As you can expect - PIP picked up the default `numpy` build - same as published on PyPI.
Built as a normal Python Wheel (aka. `non variant`)

## B. Let's install a variant-enabled Python package manager

### 1. Let's install variant-enabled PIP

> [!CAUTION]
> This command will overwrite your environment's `pip`. Make sure you are in the virtualenv.

```bash
# Install the PEP XXX - Wheel Variants Meta Package, that will give you the modified libraries:
# - pip
# - variantlib (a new package)

# Linux / MacOs
$ pip install pep-xxx-wheel-variants
Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1  # and some extra stuff

# Windows
$ $python.exe -m pip install pep-xxx-wheel-variants
>>> Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1  # and some extra stuff

# Let's verify everything is good:
$ pip --version
pip 25.1.dev0+pep-xxx-wheel-variants from ...  # <=============== Check you can see `+pep-xxx-wheel-variants`

$ variantlib --version
variantlib version: 0.0.1
```

### 2. Test Wheel Variant functionality

Now with the new variant-enabled `pip` let's see what is the result.

```bash
$ pip install --dry-run numpy

Looking in indexes: https://variants-index.wheelnext.dev/
  Fetching https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-variants.json
  Using environment: uv ...
  Installing packages in current environment:
  - provider-variant-x86-64 == 0.0.1; 'aarch' not in platform_machine and 'arm' not in platform_machine
  Loading plugin via provider_variant_x86_64.plugin:X8664Plugin
  Variant `09300f2f` has been rejected because one or many of the variant properties `[aarch64 :: version :: 8.4a]` are not supported or have been explicitly rejected.
  Variant `522ebbc7` has been rejected because one or many of the variant properties `[aarch64 :: version :: 8.3a]` are not supported or have been explicitly rejected.
  Variant `802e12ea` has been rejected because one or many of the variant properties `[aarch64 :: version :: 8.1a]` are not supported or have been explicitly rejected.
  Variant `ab33065c` has been rejected because one or many of the variant properties `[aarch64 :: version :: 8a]` are not supported or have been explicitly rejected.
  Variant `c87a4099` has been rejected because one or many of the variant properties `[aarch64 :: version :: 8.5a]` are not supported or have been explicitly rejected.
  Variant `e9a738cd` has been rejected because one or many of the variant properties `[aarch64 :: version :: 8.2a]` are not supported or have been explicitly rejected.
  Total Number of Compatible Variants: 5

Fetching https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-variants.json

##################### numpy==2.2.5; variant_hash=cfdbe307 ######################
Variant-property: x86_64 :: level :: v4
################################################################################

Collecting numpy
  Using cached https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-cp312-cp312-linux_x86_64-cfdbe307.whl (17.6 MB)

Would install numpy-2.2.5-cfdbe307
```

#### What happened ?

PIP is aware `numpy` is variant-enabled thanks to the presence of [`numpy-2.2.5-variants.json`](https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-variants.json)

The file contains the instructions on how to install the variant plugins and parse the variants properties

```json
{
    "default-priorities": {
        "feature": [],
        "namespace": [
            "x86_64",
            "aarch64"
        ],
        "property": []
    },
    "providers": {
        "aarch64": {
            "plugin-api": "provider_variant_aarch64.plugin:AArch64Plugin",
            "requires": [
                "provider-variant-aarch64 == 0.0.1; 'aarch' in platform_machine or 'arm' in platform_machine"
            ]
        },
        "x86_64": {
            "plugin-api": "provider_variant_x86_64.plugin:X8664Plugin",
            "requires": [
                "provider-variant-x86-64 == 0.0.1; 'aarch' not in platform_machine and 'arm' not in platform_machine"
            ]
        }
    },
    ...
}
```

In this case both the `x86_64` and `aarch64` plugins shall be installed by default (see `default-priorities` key).
With their relative "priority" not changing anything given that they are mutually exclusive.

This platform contains an `x86_64` CPU - `pip` installs the right plugin and is able to detect which `x86_64` version this system supports.
The following variants were available: https://variants-index.wheelnext.dev/numpy/

> [!IMPORTANT] 
> In our case - this machine has the most advanced/recent `x86_64` version available so all `x86_64` variants are compatibles.
> If you have a CPU with a `x86_64` version < 4 you will see some of the variant(s) rejected.

Consequently, the installed variant corresponds to:

```bash
############################## Variant: `cfdbe307` #############################
Variant: x86_64 :: level :: v4
################################################################################
```

### What's next ?

Tell us what you think / try the other tutorials.
