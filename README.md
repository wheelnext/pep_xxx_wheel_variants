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
$ virtualenv .venv
$ source .venv/bin/activate

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

# Linux / MacOs
$ pip install pep-xxx-wheel-variants
>>> Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1.dev1  # and some extra stuff

# Windows
$ $python.exe -m pip install pep-xxx-wheel-variants
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
```bash
torch-2.7.0-00000000 
torchaudio-2.7.0-00000000 
torchvision-0.22.0-00000000
```

In the case of PyTorch, the `Null-Variant` is a *CPU-only* PyTorch build.

```bash
############################## Variant: `00000000` #############################
################################################################################
```

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

Alright now let's try to re-run the command to install `torch torchaudio torchvision`. We should get:
- `torch torchaudio torchvision` built for `CUDA 12.8`
- `CUDA Libraries` built for `CUDA 12`

```bash
$ pip install --dry-run torch torchaudio torchvision

>>> Looking in indexes: https://variants-index.wheelnext.dev/
>>>   Discovering Wheel Variant plugins...
>>>   Loading plugin from entry point: x86_64; provided by package variant_x86_64 0
>>>   Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 1.0.0
>>>   Variant `652626b1` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11.8]` are not supported or have been explicitly rejected.
>>>   Total Number of Compatible Variants: 3
>>>   Total Number of Tags Generated: 4,272
>>> Collecting torch
>>>   Using cached https://variants-index.wheelnext.dev/torch/torch-2.7.0-cp312-cp312-manylinux_2_28_x86_64-ba4b552f.whl (1096.4 MB)
>>> Collecting torchaudio
>>>   Using cached https://variants-index.wheelnext.dev/torchaudio/torchaudio-2.7.0-cp312-cp312-manylinux_2_28_x86_64-ba4b552f.whl (3.9 MB)
>>> Collecting torchvision
>>>   Using cached https://variants-index.wheelnext.dev/torchvision/torchvision-0.22.0-cp312-cp312-manylinux_2_28_x86_64-ba4b552f.whl (8.7 MB)
>>> 
>>> ...
>>>
>>> Would install
        ...
        torch-2.7.0-ba4b552f
        torchaudio-2.7.0-ba4b552f
        torchvision-0.22.0-ba4b552f
```

### What happened ?

PIP is aware of NVIDIA CUDA and is able to detect the driver version. As my system reports it, NVIDIA CUDA 12.8 is installed on the machine,
which explains why the NVIDIA CUDA 11.8 build of PyTorch was rejected.
Notice that the NVIDIA CUDA 12.6 build was not rejected - just less favored compared to NVIDIA CUDA 12.8 and therefore not installed.

```bash
>>>   Variant `652626b1` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11.8]` are not supported or have been explicitly rejected
```

The installed variant corresponds:

```bash
############################## Variant: `ba4b552f` #############################
Variant: nvidia :: driver :: 12.8
Variant-provider: nvidia: nvidia-variant-provider
################################################################################
```

**Only on Linux:** If we look further we can see the following being installed:
(On windows libraries are statically linked)

```bash
 Would install ... nvidia-cublas-12.8.3.14-aa00cb06 nvidia-cuda-cupti-12.8.57-aa00cb06 nvidia-cuda-nvrtc-12.8.61-aa00cb06 nvidia-cuda-runtime-12.8.57-aa00cb06 nvidia-cudnn-9.7.1.26-aa00cb06 nvidia-cufft-11.3.3.41-aa00cb06 nvidia-cufile-1.13.0.11-aa00cb06 nvidia-curand-10.3.9.55-aa00cb06 nvidia-cusolver-11.7.2.55-aa00cb06 nvidia-cusparse-12.5.7.53-aa00cb06 nvidia-cusparselt-0.6.3-aa00cb06 nvidia-nccl-2.26.2-aa00cb06 nvidia-nvjitlink-12.8.61-aa00cb06 nvidia-nvtx-12.8.55-aa00cb06 ...
 ```

 Which indicates that the right variant of NVIDIA CUDA Libraries was selected and installed:

 ```bash
 ############################## Variant: `aa00cb06` #############################
Variant: nvidia :: driver :: 12
Variant-provider: nvidia: nvidia-variant-provider
################################################################################
```

### What's next ?

We invite you to try playing with `NV_PROVIDER_FORCE_DRIVER_VERSION` and see how it changes the output.
- Valid Values: `[CUDA 11] >=11.8` and `[CUDA 12] >=12.6`
- Any other values (different major than 11/12 or major.minor not supported): installation of the `null-variant` (CPU only)
