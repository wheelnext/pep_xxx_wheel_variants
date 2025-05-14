# Wheel Variants - PyTorch Tutorial

This tutorial contains a simple demo of the `Wheel-Variant` implementation for `pytorch`.

> [!CAUTION]  
> This Wheel Variant Demo currently contains **very experimental code**.<br>
> This should be considered as a feature-preview and in no-way used in production.

| Linux x86_64 | Linux AARCH64 | Windows AMD64 | MacOS x86_64 | MacOS ARM64 |
| :----------: | :-----------: | :-----------: | :----------: | :---------: |
|  ✅          |  ❌            | ✅            |  ❌          |  ❌          |

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
$ python3 -m pip config set --site global.index-url https://variants-index.wheelnext.dev/
Writing to /path/to/venv/pip.conf
```

### 2. Test Install a Variant-Enabled package with "normal `pip`"

By doing this - It **should** install the normal package (aka. non variant), proving the backward compatibility of the design.

```bash
$ python3 -m pip install --dry-run torch

Looking in indexes: https://variants-index.wheelnext.dev/
Collecting torch
  Using cached https://variants-index.wheelnext.dev/torch/torch-2.7.0-cp312-cp312-manylinux_2_28_x86_64.whl (865.8 MB)

Would install torch-2.7.0
```

### What happened ?

As you can expect - PIP picked up the default `torch` build - same as published on PyPI.
Built as a normal Python Wheel (aka. `non variant`)

## B. Let's install a variant-enabled Python package manager

### 1. Let's install variant-enabled PIP

> [!CAUTION]
> This command will overwrite your environment's `pip`. Make sure you are in the virtualenv.

```bash
# Install the PEP XXX - Wheel Variants Meta Package, that will give you the modified libraries:
# - pip
# - variantlib (a new package)
$ python3 -m pip install pep-xxx-wheel-variants
Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1  # and some extra stuff

# Let's verify everything is good:
$ python3 -m pip --version
pip 25.1.dev0+pep-xxx-wheel-variants from ...  # <=============== Check you can see `+pep-xxx-wheel-variants`

$ variantlib --version
variantlib version: 0.0.1
```

### 2. Test Wheel Variant functionality

Now with the new variant-enabled `pip` let's see what is the result.

```bash
$ nvidia-smi | head -n 4
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.133.20             Driver Version: 570.133.20     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+

# That means that this machine with any variant with NVIDIA CUDA >=12.0,<=12.8.

$ python3 -m pip install --dry-run torch

Looking in indexes: https://variants-index.wheelnext.dev/
  Fetching https://variants-index.wheelnext.dev/torch/torch-2.7.0-variants.json
  Using environment: uv ...
  Installing packages in current environment:
  - nvidia-variant-provider == 0.0.1
  Loading plugin via nvidia_variant_provider.plugin:NvidiaVariantPlugin
  Variant `1065b45d` has been rejected because one or many of the variant properties `[nvidia :: cuda :: 11.8]` are not supported or have been explicitly rejected.
  Total Number of Compatible Variants: 3
Fetching https://variants-index.wheelnext.dev/torch/torch-2.7.0-variants.json

##################### torch==2.7.0; variant_hash=d5784ad6 ######################
Variant-property: nvidia :: cuda :: 12.8
################################################################################

Collecting torch
  Using cached https://variants-index.wheelnext.dev/torch/torch-2.7.0-cp312-cp312-manylinux_2_28_x86_64-d5784ad6.whl (1096.4 MB)

Would install torch-2.7.0-d5784ad6
```

#### What happened ?

PIP is aware `torch` is variant-enabled thanks to the presence of [`torch-2.7.0-variants.json`](https://variants-index.wheelnext.dev/torch/torch-2.7.0-variants.json)

The file contains the instructions on how to install the NVIDIA variant plugin and parse the variants properties

```json
{
    "default-priorities": {
        "feature": [],
        "namespace": [
            "nvidia"
        ],
        "property": []
    },
    "providers": {
        "nvidia": {
            "plugin-api": "nvidia_variant_provider.plugin:NvidiaVariantPlugin",
            "requires": [
                "nvidia-variant-provider == 0.0.1"
            ]
        }
    },
    ...
}
```

In this case both the `nvidia` plugin shall be installed by default (see `default-priorities` key).

This platform contains an NVIDIA GPU and CUDA 12.8 - `pip` installs the right plugin and is able to detect which `NVIDIA CUDA` variants this system supports.
The following variants were available: https://variants-index.wheelnext.dev/torch/

> [!IMPORTANT] 
> In our case - this machine has the most recent `NVIDIA CUDA` version available so all variants under the CUDA 12 major are compatible.<br>
> If you have an older CUDA version, you will see some variants rejected.

Consequently, the installed variant corresponds to:

```bash
##################### torch==2.7.0; variant_hash=d5784ad6 ######################
Variant-property: nvidia :: cuda :: 12.8
################################################################################
```

### What's next ?

We invite you to try playing with `NV_PROVIDER_FORCE_DRIVER_VERSION` environment variable and see how it changes the output.
- Valid Values: `[CUDA 11] >=11.8` and `[CUDA 12] >=12.6`
- Any other values (different major than 11/12 or major.minor not supported): installation of the `null-variant` (CPU only)

```bash
export NV_PROVIDER_FORCE_DRIVER_VERSION="11.8"
pip install --dry-run torch 
...
```
