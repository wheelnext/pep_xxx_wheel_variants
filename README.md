# Wheel Variants - Testing Instructions

This repository contains a simple demo of the `WheelVariant` implementation.

## Important: Foreword / Disclaimer

The Wheel Variant Demo only supports Windows & Linux on `X86_64` / `AMD64` CPU.
We did not built any variant-artifact for MacOS or ARM CPUs.

## A. Let's validate that an "old installer" is non-affected by any of these changes

### 1. Create a virtualenv to protect your environment
```bash
# 1. Create a virtualenv
# WARNING: Installing Wheel-Variant PEP overwrites PIP.
# Do not install this in your main python environment.
$ python3 -m venv .venv
$ source .venv/bin/activate
$ cd .venv

# 2. Set the index to the WheelNext Static Wheel Server: MockHouse & Backup to PyPI
$ pip config set --site global.index-url https://variants-index.wheelnext.dev/
>>> Writing to /path/to/venv/pip.conf
```

### 2. Test Install a Variant-Enabled package with "normal `pip`"

By doing this - It **should** install the normal package (aka. non variant), proving the backward compatibility of the design.

```bash
$ pip install --dry-run torch torchaudio torchvision

>>> Looking in indexes: https://variants-index.wheelnext.dev/
>>> Collecting torch
>>>   Downloading https://variants-index.wheelnext.dev/torch/torch-2.7.0-cp312-cp312-manylinux_2_28_x86_64.whl (865.8 MB)  # Notice no variant-hash
>>> ...
>>> Would install
        ...
        torch-2.7.0
        torchaudio-2.7.0
        torchvision-0.22.0
```

### What happened ?

As you can expect - PIP picked up the default Torch build (same as published on PyPI: CPU + NVIDIA CUDA 12.6).
Built as a normal Python Wheel (aka. non variant)

## B. Let's install a variant-enabled Python package manager

### 1. Create a virtualenv to protect your environment
```bash
# 1. Create a virtualenv
# WARNING: Installing Wheel-Variant PEP overwrites PIP.
# Do not install this in your main python environment.
$ virtualenv .venv
$ source .venv/bin/activate

# 2. Set the index to the WheelNext Static Wheel Server: MockHouse & Backup to PyPI
$ pip config set --site global.index-url https://variants-index.wheelnext.dev/
>>> Writing to /path/to/venv/pip.conf
```

### 2. Let's install variant-enabled PIP

**Danger:** This command will overwrite your installed `pip`. Make sure you are in the virtualenv

```bash
# Install the PEP XXX - Wheel Variants Meta Package, that will give you the modified libraries:
# - pip
# - variantlib (a new package)
$ pip install pep-xxx-wheel-variants
>>> Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1.dev1  # and some extra stuff

# Let's verify everything is good:
$ pip --version
>>> pip 25.1.dev0+pep-xxx-wheel-variants from ...  # <=============== Check you can see `+pep-xxx-wheel-variants`

$ variantlib --version
>>> variantlib version: 0.0.1.dev1
```

### 3. Test Wheel Variant functionality

#### 3.1 Without any Variant Provider - PIP should install a CPU only build

```bash
$ pip install --dry-run torch torchaudio torchvision

>>> Looking in indexes: https://variants-index.wheelnext.dev/
>>>   Discovering Wheel Variant plugins...
>>>   Variant `652626b1` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11.8]` are not supported or have been explicitly rejected.
>>>   Variant `ba4b552f` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.8]` are not supported or have been explicitly rejected.
>>>   Variant `bee95d34` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.6]` are not supported or have been explicitly rejected.
>>>   Total Number of Compatible Variants: 1
>>>   Total Number of Tags Generated: 2,136
>>> Collecting torch
>>>   Downloading https://variants-index.wheelnext.dev/torch/torch-2.7.0-cp312-cp312-manylinux_2_28_x86_64-00000000.whl (175.4 MB)
>>> Collecting torchaudio
>>>   Downloading https://variants-index.wheelnext.dev/torchaudio/torchaudio-2.7.0-cp312-cp312-manylinux_2_28_x86_64-00000000.whl (1.8 MB)
>>> Collecting torchvision
>>>   Downloading https://variants-index.wheelnext.dev/torchvision/torchvision-0.22.0-cp312-cp312-manylinux_2_28_x86_64-00000000.whl (2.0 MB)
>>>
>>> ...
>>>
>>> Would install
        ...
        torch-2.7.0-00000000
        torchaudio-2.7.0-00000000
        torchvision-0.22.0-00000000
```

### What happened ?

PIP is not aware of any NVIDIA CUDA support and reports it:
```bash
>>>   Variant `652626b1` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11.8]` are not supported or have been explicitly rejected.
>>>   Variant `ba4b552f` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.8]` are not supported or have been explicitly rejected.
>>>   Variant `bee95d34` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.6]` are not supported or have been explicitly rejected.
```

Consequently the "default variant build": `null-variant` (a variant containing no property) is being picked up:
```
torch-2.7.0-00000000
torchaudio-2.7.0-00000000
torchvision-0.22.0-00000000
```

In the case of PyTorch, the `Null-Variant` is a *CPU-only* PyTorch build.

#### 3.2 Installing the NVIDIA Variant Provider - PIP should install a CUDA-accelerated build

**DISCLAIMER:**
- This part requires CUDA 11.8 or >=12.6 and an NVIDIA GPU to function.
- The behavior can be mocked using the environment variable: `NV_PROVIDER_FORCE_DRIVER_VERSION==major.minor`

```bash
# This can be used to "pretend" the system has a specific driver.
# However it won't make the wheel functional without the proper environment - can be used to test installation though
export NV_PROVIDER_FORCE_DRIVER_VERSION="11.8"
export NV_PROVIDER_FORCE_DRIVER_VERSION="12.6"
export NV_PROVIDER_FORCE_DRIVER_VERSION="12.7"
export NV_PROVIDER_FORCE_DRIVER_VERSION="12.8"
```

Let's install the NVIDIA Variant Provider Plugin:
```bash
$ pip install nvidia-variant-provider
>>> Successfully installed nvidia-variant-provider-1.0.0
```

Let's test the install:
```bash
# Provides a list of variant provider plugins installed on the machine.
$ variantlib plugins list
>>> variantlib.loader - INFO - Discovering Wheel Variant plugins...
>>> variantlib.loader - INFO - Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 1.0.0
>>> nvidia

# All the "known properties" by the variant provider plugins. They don't need to be compatible on this machine.
$ variantlib plugins get-all-configs
>>> variantlib.loader - INFO - Discovering Wheel Variant plugins...
>>> variantlib.loader - INFO - Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 1.0.0
>>> nvidia :: driver :: 11.0
>>> nvidia :: driver :: 11.1
>>> ...
>>> nvidia :: driver :: 11.8
>>> nvidia :: driver :: 12.0
>>> nvidia :: driver :: 12.1
>>> ...
>>> nvidia :: driver :: 12.8
>>> nvidia :: driver :: 11
>>> nvidia :: driver :: 12

$ nvidia-smi | head -n 4

>>> +-----------------------------------------------------------------------------------------+
>>> | NVIDIA-SMI 570.133.20             Driver Version: 570.133.20     CUDA Version: 12.8     |
>>> |-----------------------------------------+------------------------+----------------------+

# VariantLib can be used to query the compatibility of the platform for each installed plugin
# In this case - this computer has CUDA 12.8 and therefore this platform has the following
# compatibility of variant properties.
# NOTE: properties are given following a default ordering provided by the provider plugin
#       within one single namespace. This ordering should not be assumed final or absolute.
$ variantlib plugins get-supported-configs
>>> variantlib.loader - INFO - Discovering Wheel Variant plugins...
>>> variantlib.loader - INFO - Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 1.0.0
>>> nvidia :: driver :: 12.8
>>> ...
>>> nvidia :: driver :: 12.0
>>> nvidia :: driver :: 12
```

$ pip install --dry-run torch torchaudio torchvision

>>> Looking in indexes: https://variants-index.wheelnext.dev/
>>>   Discovering Wheel Variant plugins...
>>>   Variant `652626b1` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11.8]` are not supported or have been explicitly rejected.
>>>   Variant `ba4b552f` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.8]` are not supported or have been explicitly rejected.
>>>   Variant `bee95d34` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.6]` are not supported or have been explicitly rejected.
>>>   Total Number of Compatible Variants: 1
>>>   Total Number of Tags Generated: 2,136
>>> Collecting torch
>>>   Downloading https://variants-index.wheelnext.dev/torch/torch-2.7.0-cp312-cp312-manylinux_2_28_x86_64-00000000.whl (175.4 MB)
>>> Collecting torchaudio
>>>   Downloading https://variants-index.wheelnext.dev/torchaudio/torchaudio-2.7.0-cp312-cp312-manylinux_2_28_x86_64-00000000.whl (1.8 MB)
>>> Collecting torchvision
>>>   Downloading https://variants-index.wheelnext.dev/torchvision/torchvision-0.22.0-cp312-cp312-manylinux_2_28_x86_64-00000000.whl (2.0 MB)
>>>
>>> ...
>>>
>>> Would install
        ...
        torch-2.7.0-00000000
        torchaudio-2.7.0-00000000
        torchvision-0.22.0-00000000
```

### What happened ?

PIP is not aware of any NVIDIA CUDA support and reports it:
```bash
>>>   Variant `652626b1` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11.8]` are not supported or have been explicitly rejected.
>>>   Variant `ba4b552f` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.8]` are not supported or have been explicitly rejected.
>>>   Variant `bee95d34` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12.6]` are not supported or have been explicitly rejected.
```

Consequently the "default variant build": `null-variant` (a variant containing no property) is being picked up:
```
torch-2.7.0-00000000
torchaudio-2.7.0-00000000
torchvision-0.22.0-00000000
```

In the case of PyTorch, the `Null-Variant` is a *CPU-only* PyTorch build.












### 4.4 Installing both `provider_fictional_hw` & `provider_fictional_tech` plugins

```bash
# Ensuring the environment is clear of plugins
$ pip uninstall -y provider_fictional_hw provider_fictional_tech
$ pip install --extra-index-url=https://pypi.org/simple/ \
    git+https://github.com/wheelnext/provider_fictional_hw.git@main \
    git+https://github.com/wheelnext/provider_fictional_tech.git@main

# Verifying the install
$ pip freeze | grep provider_fictional_hw
>>> provider_fictional_hw @ git+https://github.com/wheelnext/provider_fictional_hw.git@<some_hash>

$ pip freeze | grep provider_fictional_tech
>>> provider_fictional_hw @ git+https://github.com/wheelnext/provider_fictional_tech.git@<some_hash>
```

And then let's install `dummy_plugin` again:

```bash
$ pip install --dry-run dummy-project

>>> VariantLib: Discovering Wheel Variant plugins...
>>> VariantLib: Loading plugin: fictional_hw - v1.0.0
>>> VariantLib: Loading plugin: fictional_tech - v1.0.0
>>> Total Number of Compatible Variants: 1,727
>>> Total Number of Tags Generated: 1,130,112
>>> Looking in indexes: https://mockhouse.wheelnext.dev/pep-xxx-variants/
>>>   Total Number of Tags Generated: 1,130,112
>>> Collecting dummy-project
>>>   Using cached https://mockhouse.wheelnext.dev/pep-xxx-variants/dummy-project/dummy_project-0.0.1-~6b4c8391~-py3-none-any.whl (1.4 kB)
>>> Would install dummy_project-0.0.1-~6b4c8391
```

Which corresponds as the following WheelVariant:
```
############################## Variant: `6b4c8391` #############################
Variant Metadata: fictional_hw :: architecture :: deepthought
Variant Metadata: fictional_hw :: compute_accuracy :: 10
Variant Metadata: fictional_hw :: compute_capability :: 10
Variant Metadata: fictional_hw :: humor :: 0
Variant Metadata: fictional_tech :: quantum :: FOAM
################################################################################
```
