# Wheel Variants - PyTorch Tutorial

This tutorial contains a simple demo of the `Wheel-Variant` implementation for `pytorch`.

> [!CAUTION]  
> This Wheel Variant Demo currently contains **very experimental code**.<br>
> This should be considered as a feature-preview and in no-way used in production.

| Linux x86_64 | Linux AARCH64    | Windows AMD64 | MacOS x86_64 | MacOS ARM64 |
| :----------: | :--------------: | :-----------: | :----------: | :---------: |
|  ✅          |  ✅ (CUDA 12.9+) | ✅            |  ❌          |  ❌          |

## Where to report issues / ask questions ?

Please go to: https://github.com/wheelnext/pep_xxx_wheel_variants/issues/new 

## A. Let's setup the environment to become `variant-aware`

### 1. Create a virtualenv to isolate your environment

```bash
# 1. Create a virtualenv
# WARNING: Installing Wheel-Variant PEP overwrites PIP.
# Do not install this in your main python environment.
$ python3 -m venv .venv
$ source .venv/bin/activate

# 2. Install the Experiment support for Wheel Variants

# Linux / MacOs
$ python3 -m pip install https://variants-index.wheelnext.dev/pep-xxx-wheel-variants/pep_xxx_wheel_variants-1.0.0-py2.py3-none-any.whl
Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1  # and some extra stuff

# Windows
$ $python.exe -m pip install https://variants-index.wheelnext.dev/pep-xxx-wheel-variants/pep_xxx_wheel_variants-1.0.0-py2.py3-none-any.whl
>>> Successfully installed pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0+pep.xxx.wheel.variants variantlib-0.0.1  # and some extra stuff

# Let's verify everything is good:
$ python3 -m pip --version
pip 25.1.dev0+pep-xxx-wheel-variants from ...  # <=============== Check you can see `+pep-xxx-wheel-variants`

$ variantlib --version
variantlib version: 0.0.1

# 3. Finally, let's set the index to the WheelNext Wheel Variant Server
$ python3 -m pip config set --site global.index-url https://variants-index.wheelnext.dev/
Writing to /path/to/.venv/pip.conf
```

### 2. Test Wheel Variant functionality

Now with the new variant-enabled `pip` let's see what is the result.

```bash
$ nvidia-smi | head

Wed Jul 23 15:40:20 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 575.57.08              Driver Version: 575.57.08      CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Quadro RTX 8000                On  |   00000000:1A:00.0 Off |                  Off |
| 33%   37C    P8             23W /  260W |       7MiB /  49152MiB |      0%      Default |
```

That means that this machine is compatible with:
- Any variant which was built for CUDA 12.9 or under.
- Any variant which doesn't declare any specific SM support or SM [7.5, ..., 7.0] 

```bash
$ python3 -m pip install --dry-run torch

Looking in indexes: https://variants-index.wheelnext.dev/
  Installing variant providers ... done

####################### torch==2.8.0; variant_hash=cu129 #######################
Variant-property: nvidia :: cuda_version_lower_bound :: 12.9
Variant-property: nvidia :: sm_arch :: 100_real
Variant-property: nvidia :: sm_arch :: 120_real
Variant-property: nvidia :: sm_arch :: 120_virtual
Variant-property: nvidia :: sm_arch :: 75_real
Variant-property: nvidia :: sm_arch :: 80_real
Variant-property: nvidia :: sm_arch :: 86_real
Variant-property: nvidia :: sm_arch :: 90_real
################################################################################

Collecting torch
  Downloading https://variants-index.wheelnext.dev/torch/torch-2.8.0-cp313-cp313-manylinux_2_28_x86_64-cu129.whl (1239.3 MB)
```

#### What happened ?

PIP is aware `torch` is variant-enabled thanks to the presence of [`torch-2.8.0-variants.json`](https://variants-index.wheelnext.dev/torch/torch-2.8.0-variants.json)

The file contains the instructions on how to install the NVIDIA variant plugin and parse the variants properties

```json
{
    "$schema": "https://variants-schema.wheelnext.dev/",
    "default-priorities": {
        "namespace": [
            "nvidia"
        ]
    },
    "providers": {
        "nvidia": {
            "enable-if": "platform_system == 'Linux' or platform_system == 'Windows'",
            "plugin-api": "nvidia_variant_provider.plugin:NvidiaVariantPlugin",
            "requires": [
                "nvidia-variant-provider>=0.0.1,<1.0.0"
            ]
        }
    },
    "variants": {
        "00000000": {},
        "cu126": {
            "nvidia": {
                "cuda_version_lower_bound": [
                    "12.6"
                ],
                "sm_arch": [
                    "50_real",
                    "60_real",
                    "70_real",
                    "75_real",
                    "80_real",
                    "86_real",
                    "90_real"
                ]
            }
        },
        "cu128": {
            "nvidia": {
                "cuda_version_lower_bound": [
                    "12.8"
                ],
                "sm_arch": [
                    "100_real",
                    "120_real",
                    "75_real",
                    "80_real",
                    "86_real",
                    "90_real"
                ]
            }
        },
        "cu129": {
            "nvidia": {
                "cuda_version_lower_bound": [
                    "12.9"
                ],
                "sm_arch": [
                    "100_real",
                    "120_real",
                    "120_virtual",
                    "75_real",
                    "80_real",
                    "86_real",
                    "90_real"
                ]
            }
        }
    }
}
```

In this case, the `nvidia` plugin shall be installed by default (see `default-priorities` key).

This platform contains an NVIDIA GPU and CUDA 12.9 - `pip` installs the right plugin and is able to detect which `NVIDIA CUDA` variants this system supports.
The following variants were available: https://variants-index.wheelnext.dev/torch/

> [!IMPORTANT] 
> In our case - this machine has the most recent `NVIDIA CUDA` version available so all variants under the CUDA 12 major are compatible.<br>
> If you have an older CUDA version, you will see some variants rejected.

Consequently, the installed variant corresponds to:

```bash
####################### torch==2.8.0; variant_hash=cu129 #######################
Variant-property: nvidia :: cuda_version_lower_bound :: 12.9
Variant-property: nvidia :: sm_arch :: 100_real
Variant-property: nvidia :: sm_arch :: 120_real
Variant-property: nvidia :: sm_arch :: 120_virtual
Variant-property: nvidia :: sm_arch :: 75_real
Variant-property: nvidia :: sm_arch :: 80_real
Variant-property: nvidia :: sm_arch :: 86_real
Variant-property: nvidia :: sm_arch :: 90_real
################################################################################
```

### What's next ?

We invite you to try playing with `overwrite environment variables` to get a good intuition of the the impact of NVIDIA LibCUDA and NVIDIA SM on the final selection.

```bash
export NV_VARIANT_PROVIDER_FORCE_CUDA_DRIVER_VERSION = "12.8"  # Try any of the following: ["12.5", "12.6", "12.8", "12.9", "13.0"]
export NV_VARIANT_PROVIDER_FORCE_SM_ARCH = "9.0"               # Try any of the following: ["4.0", "5.0", "7.5", "9.0", "10.0", "12.0"]
pip install --dry-run torch 
```

If you have questions or find something unexpected - please open a GitHub issue !
