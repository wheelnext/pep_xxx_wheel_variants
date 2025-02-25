# Wheel Variants - Testing Instructions

This repository contains a simple demo of the `WheelVariant` implementation.

## 1. Create a virtualenv to protect your environment
```bash
# 1. Create a virtualenv 
# WARNING: Installing PEP 771 overwrites a bunch of standard python library.
# Do not install this in your main python environment.
$ virtualenv .venv
$ source .venv/bin/activate

# 2. Set the index to the WheelNext Static Wheel Server: MockHouse & Backup to PyPI
$ pip config set --site global.index-url https://mockhouse.wheelnext.dev/pep-xxx-variants/
>>> Writing to /path/to/venv/pip.conf
```

## 2. Test Install a Variant-Enabled package with "normal `pip`"

```bash
$ pip install --dry-run dummy-project

>>> Looking in indexes: https://mockhouse.wheelnext.dev/pep-xxx-variants/
>>> Collecting dummy-project
>>>   Downloading https://mockhouse.wheelnext.dev/pep-xxx-variants/dummy-project/dummy_project-0.0.1-py3-none-any.whl (1.3 kB)
>>> Would install dummy_project-0.0.1
```

## 3. Install the Wheel-Variant enabled environment

**Danger:** This command will overwrite your installed `pip`. Make sure you are in the virtualenv

```bash
# Install the PEP XXX - Wheel Variants Meta Package, that will give you the modified libraries:
# - pip
# - variantlib (a new package)
$ pip install --extra-index-url=https://pypi.org/simple/ pep-xxx-wheel-variants 
>>> Successfully installed attrs-24.3.0 pep-xxx-wheel-variants-1.0.0 pip-25.1.dev0 variantlib-0.0.1.dev1

# Let's verify everything is good:
$ pip --version
>>> pip 25.1.dev0+pep-xxx-wheel-variants from  ...  # <=============== Check you can see `+pep-xxx-wheel-variants`

$ pip freeze | grep variantlib
>>> variantlib @ git+https://github.com/wheelnext/variantlib.git@<some_hash>
```

## 4. Test Wheel Variant functionality

### 4.1 Without any variant plugin

If you don't install a plugin => We would expect no variant behavior to be enabled

```bash
$ pip install --dry-run dummy-project

>>> Looking in indexes: https://mockhouse.wheelnext.dev/pep-xxx-variants/
>>> Collecting dummy-project
>>>   Downloading https://mockhouse.wheelnext.dev/pep-xxx-variants/dummy-project/dummy_project-0.0.1-py3-none-any.whl (1.3 kB)
>>> Would install dummy_project-0.0.1
```

### 4.2 Installing `provider_fictional_hw` plugin

```bash
# Ensuring the environment is clear of plugins
$ pip uninstall -y provider_fictional_hw provider_fictional_tech
$ pip install --extra-index-url=https://pypi.org/simple/ git+https://github.com/wheelnext/provider_fictional_hw.git@main

# Verifying the install
$ pip freeze | grep provider_fictional_hw
>>> provider_fictional_hw @ git+https://github.com/wheelnext/provider_fictional_hw.git@<some_hash>
```

### 4.3 Installing `provider_fictional_tech` plugin

```bash
# Ensuring the environment is clear of plugins
$ pip uninstall -y provider_fictional_hw provider_fictional_tech
$ pip install --extra-index-url=https://pypi.org/simple/ git+https://github.com/wheelnext/provider_fictional_tech.git@main

# Verifying the install
$ pip freeze | grep provider_fictional_tech
>>> provider_fictional_hw @ git+https://github.com/wheelnext/provider_fictional_tech.git@<some_hash>
```

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
