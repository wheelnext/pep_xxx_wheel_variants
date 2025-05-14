# Wheel Variants - XGBoost Tutorial

This tutorial contains a simple demo of the `Wheel-Variant` implementation for `XGBoost`.

> [!CAUTION]  
> This Wheel Variant Demo currently contains **very experimental code**.<br>
> This should be considered as a feature-preview and in no-way used in production.

| Linux x86_64 | Linux AARCH64 | Windows AMD64 | MacOS x86_64 | MacOS ARM64 |
| :----------: | :-----------: | :-----------: | :----------: | :---------: |
|  ✅          |  ❌            | ✅            |  ❌          |  ❌         |

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
$ python3 -m pip install --dry-run xgboost

Looking in indexes: https://variants-index.wheelnext.dev/
Collecting xgboost
  Downloading https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-py3-none-manylinux_2_28_x86_64.whl (5.1 MB)

Would install xgboost-3.1.0
```

### What happened ?

As you can expect - PIP picked up the default `xgboost` build - same as published on PyPI.
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

$ python3 -m pip install --dry-run xgboost

Looking in indexes: https://variants-index.wheelnext.dev/
  Fetching https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-variants.json
  Using environment: uv ...
  Installing packages in current environment:
  - nvidia-variant-provider == 0.0.1
  Loading plugin via nvidia_variant_provider.plugin:NvidiaVariantPlugin
  Total Number of Compatible Variants: 2
Fetching https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-variants.json

#################### xgboost==3.1.0; variant_hash=3f631cc2 #####################
Variant-property: nvidia :: cuda :: 12
################################################################################

Collecting xgboost
  Downloading https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-py3-none-manylinux_2_28_x86_64-3f631cc2.whl (265.2 MB)

Would install xgboost-3.1.0-3f631cc2
```

#### What happened ?

PIP is aware `xgboost` is variant-enabled thanks to the presence of [`xgboost-3.1.0-variants.json`](https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-variants.json)

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
The following variants were available: https://variants-index.wheelnext.dev/xgboost/

> [!IMPORTANT] 
> In our case - this machine has the most recent `NVIDIA CUDA` version available so all variants under the CUDA 12 major are compatible.<br>
> If you have an older CUDA version, you will see some variants rejected.

Consequently, the installed variant corresponds to:

```bash
#################### xgboost==3.1.0; variant_hash=3f631cc2 #####################
Variant-property: nvidia :: cuda :: 12
################################################################################
```

### What's next ?

We invite you to try playing with `NV_PROVIDER_FORCE_DRIVER_VERSION` environment variable and see how it changes the output.
- Valid Values: `[CUDA 11] >=11.8` and `[CUDA 12] >=12.6`
- Any other values (different major than 11/12 or major.minor not supported): installation of the `null-variant` (CPU only)

```bash
export NV_PROVIDER_FORCE_DRIVER_VERSION="11.8"
python3 -m pip install --dry-run xgboost
...
```













# Wheel Variants - XGBoost Tutorial

This tutorial contains a simple demo of the `Wheel-Variant` implementation for `XGBoost`.

> [!CAUTION]  
> The Wheel Variant Demo only supports Windows & Linux on `X86_64` / `AMD64` CPU.<br>
> We did not built any variant-artifact for MacOS or ARM CPUs.

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
$ python3 -m pip install --dry-run xgboost

Looking in indexes: https://variants-index.wheelnext.dev/
Collecting xgboost
  Using cached https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-py3-none-manylinux_2_28_x86_64.whl (5.1 MB)  # Notice no variant-hash
...
Would install numpy-2.2.5 scipy-1.15.2 xgboost-3.1.0
```

### What happened ?

As you can expect - PIP picked up the default XGBoost build (same as published under `xgboost-cpu` on PyPI).
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

#### 2.1 Without any Variant Provider - PIP should install the same build as before

```bash
$ python3 -m pip install --dry-run xgboost

Looking in indexes: https://variants-index.wheelnext.dev/
  Discovering Wheel Variant plugins...
  Variant `aa00cb06` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12]` are not supported or have been explicitly rejected.
  Total Number of Compatible Variants: 1
Collecting xgboost
  Using cached https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-py3-none-manylinux_2_28_x86_64.whl (5.1 MB)


  Variant `3b930df5` has been rejected because one or many of the variant properties `[x86_64 :: level :: v1]` are not supported or have been explicitly rejected.
  Variant `40aba78e` has been rejected because one or many of the variant properties `[x86_64 :: level :: v2]` are not supported or have been explicitly rejected.
  Variant `cfdbe307` has been rejected because one or many of the variant properties `[x86_64 :: level :: v4]` are not supported or have been explicitly rejected.
  Variant `fa7c1393` has been rejected because one or many of the variant properties `[x86_64 :: level :: v3]` are not supported or have been explicitly rejected.
  Total Number of Compatible Variants: 1
Collecting numpy (from xgboost)
  Using cached https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (15.6 MB)

Collecting scipy (from xgboost)
  Using cached scipy-1.15.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (61 kB)

Would install numpy-2.2.5 scipy-1.15.2 xgboost-3.1.0
```

#### What happened ?

`XGBoost` is available as CUDA accelarated, PIP detects it, however it is not aware of any NVIDIA CUDA support 
and reports it:
```bash
Variant `aa00cb06` has been rejected because one or many of the variant properties `[nvidia :: driver :: 12]` are not supported or have been explicitly rejected.
```

Similarly, `Numpy` is being optimized for different `x86_64` versions, PIP detects it, however it is not aware 
of which `x86_64` version this machine is and reports it:
```bash
Variant `3b930df5` has been rejected because one or many of the variant properties `[x86_64 :: level :: v1]` are not supported or have been explicitly rejected.
Variant `40aba78e` has been rejected because one or many of the variant properties `[x86_64 :: level :: v2]` are not supported or have been explicitly rejected.
Variant `cfdbe307` has been rejected because one or many of the variant properties `[x86_64 :: level :: v4]` are not supported or have been explicitly rejected.
Variant `fa7c1393` has been rejected because one or many of the variant properties `[x86_64 :: level :: v3]` are not supported or have been explicitly rejected.
```

Consequently the "default wheel" - a `non-variant` is being picked up:
```bash
numpy-2.2.5 
scipy-1.15.2 
xgboost-3.1.0
```

#### 2.2 Installing the NVIDIA Variant Provider - PIP should install a CUDA-accelerated build

> [!WARNING]
> - This part requires CUDA 11.8 or >=12.6 and an NVIDIA GPU to function.
> - The behavior can be mocked using the environment variable: `NV_PROVIDER_FORCE_DRIVER_VERSION==major.minor`

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
$ python3 -m pip install nvidia-variant-provider
Successfully installed nvidia-variant-provider-0.0.1
```

Let's test the install:

```bash
# Provides a list of variant provider plugins installed on the machine.
$ variantlib plugins list
variantlib.loader - INFO - Discovering Wheel Variant plugins...
variantlib.loader - INFO - Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 0.0.1
nvidia

# All the "known properties" by the variant provider plugins. They don't need to be compatible on this machine.
$ variantlib plugins get-all-configs
variantlib.loader - INFO - Discovering Wheel Variant plugins...
variantlib.loader - INFO - Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 0.0.1
nvidia :: driver :: 11.0
nvidia :: driver :: 11.1
...
nvidia :: driver :: 11.8
nvidia :: driver :: 12.0
nvidia :: driver :: 12.1
...
nvidia :: driver :: 12.8
nvidia :: driver :: 11
nvidia :: driver :: 12

$ nvidia-smi | head -n 4

+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.133.20             Driver Version: 570.133.20     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+

# VariantLib can be used to query the compatibility of the platform for each installed plugin
# In this case - this computer has CUDA 12.8 and therefore this platform has the following
# compatibility of variant properties.
# NOTE: properties are given following a default ordering provided by the provider plugin
#       within one single namespace. This ordering should not be assumed final or absolute.

$ variantlib plugins get-supported-configs
variantlib.loader - INFO - Discovering Wheel Variant plugins...
variantlib.loader - INFO - Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 0.0.1
nvidia :: driver :: 12.8
...
nvidia :: driver :: 12.0
nvidia :: driver :: 12
```

Alright now let's try to re-run the command to install `xgboost`. We should get:
- `xgboost` built for `CUDA 12`
- `NVIDIA-NCCL` built for `CUDA 12`

```bash
$ python3 -m pip install --dry-run xgboost

Looking in indexes: https://variants-index.wheelnext.dev/
    Discovering Wheel Variant plugins...
  Loading plugin from entry point: nvidia_variant_provider; provided by package nvidia-variant-provider 0.0.1
  Total Number of Compatible Variants: 2
Collecting xgboost
  Using cached https://variants-index.wheelnext.dev/xgboost/xgboost-3.1.0-py3-none-manylinux_2_28_x86_64-aa00cb06.whl (265.2 MB)

  Variant `3b930df5` has been rejected because one or many of the variant properties `[x86_64 :: level :: v1]` are not supported or have been explicitly rejected.
  Variant `40aba78e` has been rejected because one or many of the variant properties `[x86_64 :: level :: v2]` are not supported or have been explicitly rejected.
  Variant `cfdbe307` has been rejected because one or many of the variant properties `[x86_64 :: level :: v4]` are not supported or have been explicitly rejected.
  Variant `fa7c1393` has been rejected because one or many of the variant properties `[x86_64 :: level :: v3]` are not supported or have been explicitly rejected.
  Total Number of Compatible Variants: 1
Collecting numpy (from xgboost)
  Using cached https://variants-index.wheelnext.dev/numpy/numpy-2.2.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (15.6 MB)

  Variant `73be618d` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11]` are not supported or have been explicitly rejected.
  Total Number of Compatible Variants: 2
Collecting nvidia-nccl (from xgboost)
  Using cached https://variants-index.wheelnext.dev/nvidia-nccl/nvidia_nccl-2.26.2-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64-aa00cb06.whl (201.3 MB)

Would install numpy-2.2.5 nvidia-nccl-2.26.2-aa00cb06 scipy-1.15.2 xgboost-3.1.0-aa00cb06
```

#### What happened ?

PIP is aware of NVIDIA CUDA and is able to detect the driver version. As my system reports it (see `nvidia-smi` above).
NVIDIA CUDA 12.8 is installed on the machine, which explains why the NVIDIA CUDA 11 build of `NVIDIA-NCCL` was rejected.

```bash
Variant `73be618d` has been rejected because one or many of the variant properties `[nvidia :: driver :: 11]` are not supported or have been explicitly rejected.
```

> [!IMPORTANT]  
> Numpy is also `variant-enabled`. Please refer to the [`numpy` tutorial](./Numpy.md) to learn how to install `numpy` as a variant.

> [!NOTE] 
> **Exclusively on Linux** *[on Windows CUDA Libraries are statically linked]*
> `nvidia-nccl` is only downloaded on Linux. 

The installed variant corresponds:

```bash
############################## Variant: `aa00cb06` #############################
Variant: nvidia :: driver :: 12
Variant-provider: nvidia: nvidia-variant-provider
################################################################################
```

### What's next ?

We invite you to try playing with `NV_PROVIDER_FORCE_DRIVER_VERSION` and see how it changes the output.
- Valid Values: `[CUDA 12] any version`
- Any other values: installation of the normal `non-variant` Wheel (CPU only)
