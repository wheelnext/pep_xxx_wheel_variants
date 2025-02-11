# PEP ### - Wheel Variant Support

### Foreword & Context

This repository shows a prototype concept of how `Python Wheels` could be made specific to any hardware - platform - device (internal or external) - silicone - etc.

We would like to argue that Python today supports a very wide variety of platforms, unfortunately the existing following are not sufficient to cover today's needs:
- Python ABI version
- OS
- CPU architecture 
- Build ID

All of which summarized by the following regex:
```python
r"^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]+?))(-(?P<build>\d[^\s-]*))?-(?P<pyver>[^\s-]+?)-(?P<abi>[^\s-]+?)-(?P<plat>\S+)\.whl$"
```

We argue in this PEP, that multiple wheels with the same Python ABI / OS / CPU Arch can be built to support different platforms (in a large meaning): CPU-only vs GPU-enabled vs FPGA-enabled.

### Today, all solutions are suboptimal

- Using dedidacated indexes per platform (one index for GPU wheels, one index for CPU wheels, etc.). All of which sharing usually the exact same name though having vastly different behavior and/or dependencies and/or features. And to add to the injury, if users don't read the documentation with attention, they are most likely to end up with a non-functioning install or very suboptimal (having a GPU build on a system which doesn't have a GPU - at best unnecessary downloads - at worst it won't work altogether). Obviously this approach breaks every core python assumptions: `pip freeze` & friends because a "wheel / package" with version is not unique.

- Including all dependencies imaginable in one MEGA-Wheel (CPU, NVIDIA GPU, AMD GPU, Google TPU, FPGA, etc.) and detecting at runtime "what the platform supports" and activating the corresponding code-paths/dependencies. This usually makes heavy use of lazy imports and can rapidly lead to a very bloated download/install sequence due to the plaetora of unnecessary dependencies installed. This appraoch essentially trades "efficiency & network impact" for user friendliness (limited need to "read the documentation": just install and it works). This approach unfortunately also comes at a high cost "for the community" putting a high stress and load on WareHouse (PyPI.org) and we are already reaching the limit of what "this approach can do" (total repo size, maximum size per wheel, bandwidth generated, etc.).

- One can also create package / metapackage (alias package - empty shells just redirecting properly) dedicated per "platform": `mypackage-gpu` or `mypackage-cpu`. This approach has some advantages, but still minor drawbacks:
  - Where do you stop: `mypackage-cpu-arm-v7` or `mypackage-cpu-arm-v7.1` ?
  Obviously if you don't force yourself to "stay as generic as possible" you rapidly end up with a literal explosion of packages (imagine combining multiple "variables" in a combinatorial way).
  - **MOST IMPORTANTLY:** this approach is total death blow to python dependency management. How can a package express a dependency of `mypackage` if there exist 15 of them. Extra environments maybe ? You better read the documentation VERY closely. The easiest/most reasonable is most certainly to on-purpose omit the explicit dependency `package -> mypackage` and - at runtime - if the import of `mypackage` fails, issue a well formatted error message sending the user to the documentation on what version of `mypackage` to install and how.

### Wheel Variants: a mechanism to automatically detect "best package match" for the target platform.

A `Wheel Variant` is defined as a "*flavored package*" specific to a certain number of attributes externally defined / detected and controlled.

Let's imagine the creators of `TARS` (i.e. InterStellar) would want to create a `Wheel Variant` of `numpy`. Because there is absolutely zero doubt InterStellar AI is powered by Python, they consequently need to access `numpy` for trajectory calculations.

### Provider Plugins - How do you detect what platform you're on and decide on the best match.

Which leads us to the concept of `Provider Plugin`, we need a system to detect the user platform is `TARS` and consequently grab the appropriate `Python Wheel`. Most likely that system will be designed, released and maintained by the creator/manufacturer of `TARS`, but nothing prevents anyone to `fork the provider plugin` and alter the selection logic (license permitting).

Let's say that in our case we `fictional_hw`, to be `Provider Plugin`, it's able to "scan our machine and determine the best-matching `Variant` for this machine.

### Why a plugin you may ask ?

*Oh my dear friend - I'm glad you ask!* 

The core of the rational is that it's impossible to modify PIP (send PRs, etc.) every single time a new hardware / fix / etc. needs to get released. This would instantly turn into a massive burden for `PIP` maintainers and nobody wants that. At the same time,`Provider Plugin` may need to quickly iterate / adjust / modify their "selection logic" (bug fix, security fix, new product released/announced). And lastly because it's not part of `PIP` it becomes very easy for whoever needs it (that need should stay pretty rare though) to "fork and modify" the selection logic from a hardware vendor (at your own risk) and fit your needs. 

So really, everybody wins in this context to have that "selection logic" external from `PIP`.

### I thought PIP does not have a public API - How do you implement a "Plugin" ?

*Oh my dear friend - I'm glad you ask (again I know, you have good questions not my fault) !* 

Turns out there's a very elegant (I foresee some people ?preparing to? disagreeing already) way to allow a "plugin" interface without providing a public API to `PIP` in any sort of way.

Turns out a `packageA` can register an entrypoint for another `packageB`.

This PEP will be supported by a library called `variantlib`, we propose that all plugins register an entrypoint as follows:

```toml
[project.entry-points."variantlib.plugins"]
my_plugin = "my_plugin.plugin:MyVariantPlugin"
```

The only constraint is the following, `MyVariantPlugin` needs to follow the following "structure and signature"

```python 
# We will come back on `ProviderConfig` later.
# For now - it's a "standardized way" to express arbitrary metadata 
# or attributes that are supported on this machine.
from variantlib.config import ProviderConfig

from my_plugin import __version__


class MyVariantPlugin:
    __provider_name__ = "my_plugin"
    __version__ = __version__

    def run(self) -> ProviderConfig | None:
        """If the plugin is able to determine this platform/machine supports
        custom "attributes/metadata" (defined and known by this plugin): 
        => It returns a `ProviderConfig`, otherwise `None` (aka. ignore me).
        ...
```

Nothing more - nothing less.

And in case you need the rest of the story, on PIP side we can then apply the following:

```python
from importlib.metadata import entry_points
plugins = entry_points().select(group="variantlib.plugins")

for plugin in plugins:  
    logger.info(f"Loading plugin: {plugin.name} - v{plugin.dist.version}")

    # Dynamically load the plugin class
    plugin_class = plugin.load()  

    # Instantiate the plugin
    plugin_instance = plugin_class()  

    # Call the `run` method of the plugin
    ... = plugin_instance.run()  

    # do something with the result of the plugins
```

**This approach has so many advantages:**

- It's *standardized* and the proposed plugin standard is really minimalistic and easy to follow / modify as needed.
- `PIP` still does not need to commit to any public API (no `from pip import XYZ` in sight) 
- Does not require to overwrite files / folders of other packages or drop files within the tree of another package.
- Last and not the least complete auto-discovery ! The user need to do nothing beyond `pip install myplugin` and the plugin gets auto-discovered when `PIP` needs it.

## The Variant-Platform matching process

Alright so now let's put everything back together. We have:
- a package `mypackage` version `A.B.C` - packaged as a normal wheel and as a `Wheel Variant` for `TARS` platform.

- a `Variant Provider` plugin `fictional_hw` which plugs into `variantlib` providing (hence the name) what kind of `Wheel Variant` are suitable for this machine and in what order of preference.

- some new logic inside `PIP` which queries `variantlib.plugins` to determine if there is any existing `Wheel Variant` matching the user platform.

We are almost there - let's clear a few points before full demo.

### How can we upload different "wheels" if they all represent the same "release" ?

*Oh my dear friend - I'm glad you ask (again again I know, you have very good questions) !* 

For multiple reasons (explained below), we propose to slightly modify the regex above by adding a new capture group: `(-@(?P<variant_hash>[0-9a-f]{8}))?` (essentially `@abcd1234` for those who don't speak fluently - not you I know that you know, other people :D).

This `hash` is constructed in a standardized by `variantlib` (which algorithm to use could be debated - for now `hashlib.shake_128()`)  and only use 8 characters which is plenty to guarantee unicity.

This `hash` is prefixed by `@` to make the filename extremely obvious to be a variant (aka. not generic but rather platform specific): `mypackage-0.0.1-@9091cdc4-py3-none-any.whl`. The choice of `@` (instead of `#` for instance) was made because it's one of the very rare character with doesn't need escaping or convey a special meaning in a URL (like `#` or `?`). Ultimately it could be anything easy to recognize and that doesn't require complex escape or unintended consequence. `@` is unique and "fill all the boxes".

Modifying the "wheel validation" regex has one "hidden" major advantage: it makes any `Variant Wheel` an invalid filename for any version of PIP which does not support variants. Consequently guaranteeing, this PEP does break any old release of `PIP` by publishing `Python Wheels` in a previously unsupported.

Consequently on disk - we have the following:

```bash
mypackage-0.0.1-py3-none-any.whl
mypackage-0.0.1-@e684be6f-py3-none-any.whl
mypackage-0.0.1-@9091cdc4-py3-none-any.whl
mypackage-0.0.1-@6b4c8391-py3-none-any.whl
mypackage-0.0.1-@57768a46-py3-none-any.whl
mypackage-0.0.1-@4f8ae729-py3-none-any.whl
mypackage-0.0.1-@36266d4d-py3-none-any.whl
```

If the user need to know what `mypackage-0.0.1-@e684be6f-py3-none-any.whl` corresponds to, they can open the `METADATA` file which contains the relevant variant information (which has been hashed).

### From the plugin to the Variant Hash to the Install

Let's pretend the user is doing `pip install fictional_hw` (the plugin) and then later `pip install package`, how does the whole process look like under the hood ?

1. `PIP` asks `variantlib` to collect all the `ProviderConfig` and generate a combinatorial product of possibilities which are "possible on this machine":
   1. `variantlib` calls on each `installed plugin` and ask them to analyze the platform (a few example below)
      - do you support AVX 512 ?
      - do you have the NVIDIA driver installed ? which version ?
      - which version of ARM is your CPU (e.g. ARMv7, ARMv8, etc.)
      - what type of networking do you have (e.g. ethernet vs roc-e vs infiniband, etc.)

   2. Each Plugin generate a `ProviderConfig` and returns it. This object contains all the attribute the plugin was able to match this machine/platform with

   3. `variantlib` creates a combinatorial product of all the attributes provided by the all the plugins, respecting the priority order (user-controllable).

2. `variantlib` generates the `hash value` for each configuration compatible on this machine and `PIP` searches - in order - if any matching `Wheel Variant` is available on the indexes.

3. Finally, if a `Variant-match` was found => the best match (given the priority order) is installed, if none was found - the non-variant package is installed: `mypackage-0.0.1-py3-none-any.whl`

All that process happens very fast because it's essentially just a generation of hashes and a look up in a hashmap if a given hash value exists. It's near-invisible to the user.

-----------------------

## A few design details important for user experience

It is crucial to understand that Wheel Variants are a totally optional mechanism that probably 99% of packages will never need. However, many of the very important projects for the Python Community may have a serious usecase for them. Namely those shipping with compiled binaries.

This proposal aims to propose a framework and mechanism to specify arbitrary information and resolve them on the user-machine. We try to be as little specific and/or opiniated on what "information" may mean (hence we used fictional references). We believe this proposal can be used in ways we don't necessarily anticipate today and it's by design. We want to leave the freedom in the design to not specify what doesn't need to specified.

Below are a few detail points of "User Experience" that we tried to consider in the demonstrator - they appear important to us and we wanted to be able to provide a full answer to allow you to project yourself into a `Variant-enabled` future.

1. The relative priority of `pluginA` vs `pluginB` should be either controllable using `pip.conf` or using a `pip install --flag` We obviously want to let the user decide what plugin should take the precedence if two plugins are installed simultaneously.

2. We might envision a command `pip organize_variant_provider` that will provide a new UI and modify the `pip.conf` for you in the background (e.g. chose the most important plugin, now chosen the second most important, etc.).

3. This mostly concerns supercomputers AFAIK - Some usecases share a unique `virtualenv` (in read-only) between thousands of workers. The node doing the install of the virtualenv does not necessarily have access to the "real production environment", consequently it's important to be able to force the resolution to variant `abcd1234` if the user asks for it `pip install --force-variant=abcd1234 mypackage`. It's niche but important.

4. A user may also want to disable the `variant` feature/behavior altogether: `pip install --no-variant mypackage`

5. I believe for `lockfiles` (discussed in other places) we may want `variant infos` to be included (I honestly don't have opinion). 

6. To the contrary, I would argue we don't want `variant infos` to be inside `pip freeze`. It is frequently used to generate `requirements.txt` files: `pip freeze > requirements.txt`, the whole point of `Wheel Variants` is to let `PIP` decide what `Wheel Variant` (if any) is most appropriate for a given machine. Forcing the variant hash into `pip freeze` (or the dependencies/optional-dependencies inside `pyproject.toml`), entirely defeats the purpose to have this "resolution" eagerly executed.

7. Each variant provider plugin may want to provide a "debug command" `myprovider debug --verbose` or so giving the details of how the platform is being analyzed and resolved. We don't believe that interface shall be standardized, it shall be up to the plugin authors to decide what information they believe useful to help the user understand why they don't get the variant they expect to get.
   - Maybe a different plugin has the priority
   - Maybe the detection mechanism has a problem (e.g. some library is missing in the `LD_LIBRARY_PATH`)
   - Maybe provide a link to a forum / discord / slack / stackoverflow / email / github to get support.
   - etc.


---------------

### Demo - we designed a simplified `pip` copy to show the design & behavior without diving too deep into the details (yet).

```bash
pip install -i http://localhost:5000/simple/ myypackage
[I 2025-01-28 02:08:34.091 pip.commands.install:57 v0.1.0] Received install request for: `myypackage` from index: http://localhost:5000/simple/.
[I 2025-01-28 02:08:34.092 pip.repository:30 v0.1.0] Querying `http://localhost:5000/simple/myypackage/` for package `myypackage`
[I 2025-01-28 02:08:34.096 pip.repository:38 v0.1.0] Successfully fetched package data from `http://localhost:5000/simple/myypackage/`
[I 2025-01-28 02:08:34.097 pip.commands.install:70 v0.1.0] 
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-@e684be6f-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-@9091cdc4-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-@6b4c8391-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-@57768a46-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-@4f8ae729-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:75 v0.1.0] Found: `myypackage-0.0.1-@36266d4d-py3-none-any.whl`
[I 2025-01-28 02:08:34.097 pip.commands.install:79 v0.1.0] 
[I 2025-01-28 02:08:34.097 pip.variant_hash:69 v0.1.0] Discovering plugins...
[I 2025-01-28 02:08:34.108 pip.variant_hash:86 v0.1.0] Loading plugin: fictional_tech - v1.0.0
[I 2025-01-28 02:08:34.110 pip.variant_hash:86 v0.1.0] Loading plugin: fictional_hw - v1.0.0
[I 2025-01-28 02:08:34.129 pip.commands.install:100 v0.1.0] ######################### Selected Variant: `9091cdc4` #########################
[I 2025-01-28 02:08:34.129 pip.commands.install:102 v0.1.0] Variant-Data: fictional_tech :: quantum :: SUPERPOSITION
[I 2025-01-28 02:08:34.129 pip.commands.install:102 v0.1.0] Variant-Data: fictional_tech :: risk_exposure :: 25
[I 2025-01-28 02:08:34.129 pip.commands.install:102 v0.1.0] Variant-Data: fictional_tech :: technology :: auto_chef
[I 2025-01-28 02:08:34.129 pip.commands.install:103 v0.1.0] ################################################################################
[I 2025-01-28 02:08:34.129 pip.commands.install:127 v0.1.0] 
[I 2025-01-28 02:08:34.129 pip.commands.install:128 v0.1.0] Installing: myypackage-0.0.1-@9091cdc4-py3-none-any.whl ...
[========================================] 100%
[I 2025-01-28 02:08:36.259 pip.commands.install:130 v0.1.0] 
[I 2025-01-28 02:08:36.259 pip.commands.install:132 v0.1.0] The package: `myypackage` (Version: `0.0.1`) was installed with success ...
```
