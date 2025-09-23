# Prior art

## Gentoo

[Gentoo Linux](https://www.gentoo.org) is a source-first distribution
with support for extensive package customization. The primary means of
this customization are so-called [USE
flags](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/USE): boolean
flags exposed by individual packages and permitting fine-tuning the
enabled features, optional dependencies and some build parameters. For
example, a flag called `jpegxl` controls the support for JPEG XL image
format, `cpu_flags_x86_avx2` controls building SIMD code utilizing AVX2
extension set, while `llvm_slot_21` indicates that the package will be
built against LLVM 21.

Gentoo permits using [binary
packages](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Features#Binary_package_support)
both as a primary installation method and a local cache for packages
previously built from source. Among the metadata, binary packages store
the configured USE flags and some other build parameters. Multiple
binary packages can be created from a single source package version, in
which case the successive packages are distinguished by monotonically
increasing build numbers. The dependency resolver uses a combined
package cache file to determine whether any of the available binary
packages can fulfill the request, and falls back to building from source
if none can.

The interesting technical details about USE flags are:

1. Flags are defined for each package separately (with the exception of
   a few special flags). Their meanings can be either described globally
   or per package. The default values can be specified at package or
   profile (a system configuration such as “amd64 multilib desktop”)
   level.

2. Global flags can be grouped for improved UX. Examples of groups are
   `CPU_FLAGS_X86` that control SIMD code for x86 processors, and
   `LLVM_SLOT` that select the LLVM version to build against.

3. With the exception of a few special flags, there is no automation to
   select the right flags. For `CPU_FLAGS_X86`, Gentoo provides an
   external tool to query the CPU and provide a suggested value, but it
   needs to be run manually, and rerun when new flags are added to
   Gentoo. The package managers also generally suggest flag changes
   needed to satisfy the dependency resolution.

4. Dependencies, package sources and build rules can be conditional to
   use flags:
   * `flag? ( … )` is used only when the flag is enabled
   * `!flag? ( … )` is used only when the flag is disabled

5. Particular states of USE flags can be expressed on dependencies,
   using a syntax similar to Python extras: `dep[flag1,flag2...]`.
   * `flag` indicates that the flag must be enabled on the dependency
   * `!flag` indicates that the flag must be disabled on the dependency
   * `flag?` indicates that it must be enabled if it is enabled on this
     package
   * `flag=` indicates that it must have the same state as on this
     package
   * `!flag=` indicates that it must have the opposite state than on
     this package
   * `!flag?` indicates that it must be disabled if it is disabled on
     this package

6. Constraints can be placed upon state of USE flags within a package:
   * `flag` specifies that the flag must be enabled
   * `!flag` specifies that the flag must be disabled
   * `flag? ( … )` and `!flag? ( … )` conditions can be used like in
     dependencies  
   * `|| ( flag1 flag2 … )` indicates that at least one of the specified
     flags must be enabled
   * `^^ ( flag1 flag2 … )` indicates that exactly one of the specified
     flags must be enabled
   * `?? ( flag1 flag2 … )` indicates that at most one of the specified
     flags must be enabled

This syntax has been generally seen as sufficient for Gentoo. However,
its simplicity largely stems from the fact that USE flags have boolean
values. This also has the downside that multiple flags need to be used
to express enumerations.

## Conda

TL;DR: The first part of this section describes the historical context that spurred the
development of variants in the Conda ecosystem. Skip ahead to [How to capture
more metadata](#how-to-capture-more-metadata) for more technical discussion.

Conda is a binary-only package ecosystem. Similar to the Python wheel ecosystem,
there are several tools that share package collections and index formats. Where
the Python wheel ecosystem has pip, uv, poetry and others, the Conda package
ecosystem has conda, mamba, pixi and others (collectively dubbed "conda
installer tools"). The conda ecosystem was created by [package maintainers who
were frustrated with python's rough support for binary
packages](https://jakevdp.github.io/blog/2016/08/25/conda-myths-and-misconceptions/#Myth-#4:-Creating-conda-in-the-first-place-was-irresponsible-&-divisive).
The package collection includes both high-level integrations (PyTorch, GDAL,
etc.) and low-level dependencies such as compilers and C++ runtimes.  As such,
Conda environments have approximately the same control over the runtime
environment as base operating systems. It has proven especially useful for
providing an up-to-date package collection on older operating systems, where the
system package manager may not have a current package selection. Moreover,
multiple conda environments can exist on one system, giving the user an easy way
to switch between versions of software, or to use conflicting software that
otherwise could not coexist on a system. Conda environments are isolated using
separation on disk, with OS-standard environment variables guiding commands to
the currently-selected conda environment. For better and worse, this is less
rigid separation than containers. 

### Accessible metadata

Conda divides packages by platform (aka "subdir"), like `linux-64`. Within
each platform, a conda package filename is made up of three parts: 
[the package name, version, and build string](https://docs.conda.io/projects/conda-build/en/stable/concepts/package-naming-conv.html).

Conda does not rely on the filename for the resolution process. Instead, each
conda package contains metadata, and the metadata is aggregated into a single,
comprehensive [index per
subdir](https://docs.conda.io/projects/conda-build/en/stable/concepts/generating-index.html).
This usage of an index for resolution instead of a filename means that the
filename need not contain any meaningful information about a package. Any
information in the filename aside from name uniqueness is purely for human
convenience.  This is a very useful property for any attempt to encode
arbitrary metadata, because it allows metadata to expand beyond the limits
imposed by filename length. In comparison, tools that use PEP
[503](https://peps.python.org/pep-0503/)/[691](https://peps.python.org/pep-0691/)
employ filename parsing and sorting to achieve resolution. PEP
[503](https://peps.python.org/pep-0503/) emphasized this with its limited HTML
views, while PEP [691](https://peps.python.org/pep-0691/) offers new potential
for tools to consume broader metadata.

One further advantage of this metadata aggregation is that [the index contents
can be "patched" to correct
constraints](https://docs.conda.io/projects/conda-build/en/stable/concepts/generating-index.html#repodata-patching).
This is helpful when dependencies break unexpectedly. The index can adjust upper
bounds to avoid breakage. The analog to this in PEP
[503](https://peps.python.org/pep-0503/)/[691](https://peps.python.org/pep-0691/)
indexes is that the troublesome package would be yanked and replaced with a
.post revision. Patching the repodata means that unnecessary updates are limited
and file hashes for a given release stay the same. This comes at the cost of
having the index metadata not necessarily agree with the contents of the conda
package. For this reason, online indices are treated as the source of truth for
metadata, rather than package contents.

### Compatibility and the need for more metadata

Conda was designed to use shared libraries that several packages in an
environment may utilize. This is [the opposite of
wheels](https://github.com/pypa/auditwheel), which have advised per-wheel
isolation. Aligning binaries to maintain compatibility can be difficult, and
gets more difficult as the number of ways that builds can vary goes up. Conda
packages were first produced only by Continuum Analytics (now Anaconda). It was
easy to maintain consistency, because Anaconda controlled the toolchain and the
version choices. Continuum created binstar.org, which became anaconda.org, as a
central host for anyone to upload their conda packages. Several
users/organizations published large collections of packages to anaconda.org,
with each organization choosing their own toolchain and dependency versions.
Some chose newer toolchains to support newer C++ projects, such as OpenCV or the
nascent TensorFlow. This was a great expansion of packages beyond the collection
that Anaconda offered on their official channel.  Unfortunately, there were no
guarantees about compatibility between channels, nor any metadata to express
such compatibility or lack thereof. Mixing packages from different channels
often yielded undefined behavior - crashes and/or corruption. At the same time,
it was common that any single channel wouldn't have all of the desired packages
for your particular environment, and it was tempting to mix packages from
multiple channels. This issue is shared by projects on PyPI that share binary
dependencies.  It may be possible for numpy and scipy to share a BLAS library
because numpy and scipy are built and maintained by the same people. It is more
difficult for arbitrary projects maintained by different people to align. This
alignment must ultimately happen on the end user's system, with arbitrarily
complicated environments.

In other words, conda channels collect many packages built by one or a few
organizations, and any organization may provide the same package built in
different ways.  PyPI collects many packages, with each package built by one
particular organization. The only room for customization is in either
maintaining private indexes, or in publishing packages to PyPI under different
names (such as [intel-numpy](https://pypi.org/project/intel-numpy/))

The creation of [conda-forge](https://conda-forge.org/docs/user/introduction/)
as a centralized recipe collection and build infrastructure dramatically
improved the multiple-source problem for conda. This community unified several
of the independent organizations and worked with Anaconda to preserve
compatibility with Anaconda's default package collection. The toolchain was
unified, and the community negotiated which library versions were the officially
supported versions. Updates were an agreed-on choice by the community.

Even so, conda packages did not have a standard way to differentiate builds of a
package with different dependencies. This made it difficult to "migrate" the
package ecosystem, such as to update a core library, and then rebuild all of its
downstream packages. Compatibility pinning was very manual and error-prone. The
conda filename format included specifiers for a few things in the package
(python version, numpy version mainly), but most package dependencies were not
represented in any way in the filename. This is similar to [Python's platform
compatibility tags
](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/).
Compatibility tags capture a few bits of important information, but can't
differentiate between builds of a given package against different binary
dependencies. The need to encode and act on arbitrary metadata in conda packages
is basically the same state that motivated the current wheel variant rework
effort.

### How to capture more metadata

In
[2016](https://github.com/conda/conda-build/issues/1142)-[2017](https://www.anaconda.com/blog/package-better-conda-build-3),
the conda community developed a "variant" scheme that differentiated packages
based on arbitrary metadata. This section described how conda-build went down
this path, but the hard requirements are much less rigid than the scheme here.
The only implementation detail that matters is that there is a way to have
multiple packages with the same name and version, but which may have different
dependencies, and must have different filenames so as to not clobber one
another. You could theoretically do all of this in the filename, but in
practice, that is infeasible for arbitrary metadata, with parsing scaling
especially poorly.

The conda-build scheme allowed substitution of values in a package recipe, and
then calculated a hash for packages based on the keys and values that were used
by the substitution. Let's say we have a package that we want to vary
dependencies in, between two implementations of BLAS linear algebra libraries.
This was common at the time, with Anaconda wanting to provide MKL-based builds,
while community package builders kept to OpenBLAS for simpler licensing.

Before conda-build 3:

`somepackage-1.2.3-py27_0.tar.bz2`

the build details varied, depending on which channel you got your package from.
The variant tracking was present (py for python version, np for numpy version,
etc.), but this was limited to a few commom axes of variance. Users *could*
manage their build string manually and insert arbitrary identifiers, but this
was cumbersome.

After conda-build 3:

`somepackage-1.2.3-py27hdeadbeef_0.tar.bz2`

The extra hash component would be calculated based on the values "used" - that
is, substituted somehow into the raw recipe. These values would be collected into a JSON file, like

```json
  {
    "blas_impl": "mkl"
  }
```

or 


```json
  {
    "blas_impl": "openblas"
  }
```

and the hash of these JSON files is that is recorded by default in the filename
as a uniqueifier. The hashes served to avoid file clobbering on disk - to give
each package variant a unique key. The assumption with the hashes was that users
were not interactively choosing files to download based on filename.  The variant
JSON data was not used for any solving purposes. Rather, each package varied in
its dependencies, and selecting variants was now a question of how clients should
specify them to the solver. This is advantageous relative to encoding metadata
in the filename, because arbitrary metadata in the filename makes parsing infeasible.

The index metadata for our example above might look something like (some fields omitted for brevity):

```json
  "packages.conda": {
      "somepackage-1.2.3-py310h12341234_0.conda": {
        "build": "py310h1234abcd_0",
        "depends": [
          "openblas"
        ],
    },
      "somepackage-1.2.3-py310habcdabcd_0.conda": {
        "build": "py310habcd1234_0"
        "depends": [
          "mkl"
        ],
    }
  }
```

You can specify the package and the implementation you want:

`conda install somepackage mkl` 

and you'd get that variant. Because the consumption of the variant scheme was
based solely on package constraints, it did not require any new understanding of
metadata, it did not require any special support in any of the conda ecosystem
tools (conda, mamba, pixi, rattler). Any build tools did not need to match
conda-build's implementation of variant encoding (the hash scheme), so long as
they ensured that filenames did not clash on disk.

#### Alignment within an environment

It's generally unrealistic to have only one consumer of a given variant in an
environment. There needs to be a way of avoiding multiple BLAS implementations
in one environment. In the solver's mind, there's nothing preventing `openblas`
and `mkl` in one environment - the only mechanism we have for exclusivity is
some package with the same name, but different build string. In the conda
ecosystem, these are called "mutex metapackages". To prevent `openblas` and
`mkl` from being coinstalled, we make a separate metadata-only package, say
`blas`. The `somepackage` built with `openblas` depends on `blas=*=openblas` and the `mkl`
build depends on `blas=*=mkl`. By creating these packages and dependencies, we
keep all packages that use blas to one implementation.

These are software-based variants, which are completely determined by the conda
installer tool. Hardware-based variants are determined by properties external to
the conda installer tool, and will be covered below.

**Existing software-based variants**

* [BLAS](https://conda-forge.org/docs/maintainer/knowledge_base/#blas)
* MPI ([consuming](https://conda-forge.org/docs/user/tipsandtricks/#using-external-message-passing-interface-mpi-libraries), [building](https://conda-forge.org/docs/maintainer/knowledge_base/#message-passing-interface-mpi))
* [OpenMP](https://conda-forge.org/docs/maintainer/knowledge_base/#openmp) 
* [Noarch vs native code](https://conda-forge.org/blog/2024/10/15/python-noarch-variants/)

These importance of these variants is to ensure consistency of a particular
library implementation across all the packages in an environment.

### Exposing user tools to specify variants

The desired variant can be selected by specifying the implementation package,
which is implicitly installing and thus "activating" the mutex metapackage, like:

`conda create -n env somepackage mkl`

One can also specify the mutex metapackage explicitly, which can be convenient
for looping over variants in recipe builds:

`conda create -n env somepackage "blas=*={{variant_value}}`

There are no standards for this behavior. It has been iterated on for many
years, particularly with MPI libraries. [Conda-forge's
docs](https://conda-forge.org/docs/maintainer/knowledge_base/#preferring-a-provider-usually-nompi)
go into more detail, particularly on default values when no provider is
specified.

#### System detection for guiding variant selection

In [2019, the conda community developed the notion of a "virtual package" for
CUDA](https://github.com/conda/conda/pull/8267).  A virtual package detects the
system state and injects that state into the solver as package constraints. At
build time, the recipe specifies which virtual package values are required for
installation. For example, packages that use the [cudatoolkit package to build
CUDA packages will pick up a dependency on the `__cuda` virtual
package](https://github.com/conda-forge/cudatoolkit-feedstock/blob/0f01f6edfe22e77ac068daa46505711a1481272e/recipe/meta.yaml#L705)
(trimmed for brevity):

```
requirements:
  ...
  run_constrained:
    - __cuda >={{ major_minor }}
```

The built package would express a dependency on something like `__cuda >=12.8`,
assuming `major_minor` for the CUDA toolkit was 12.8.

At install time, the conda installer tool will check the CUDA version that is
present, and choose an appropriate build. If no compatible build exists, such as
the user having too old or too new of a CUDA package, the the conda installer tool
will error out.

Other packages that have been built with a need for particular hardware would
have a constraint to match the expected detected hardware value. Virtual
packages have also served to help conda installer tools understand base
operating system compatiblity (required glibc version) so that they do not
install incompatible packages.  This is similar to [the newest Manylinux
standard](https://peps.python.org/pep-0600/) platform tags, except that conda's
resolver is treating this as a package constraint rather than a filename
component.

Conda added [plugin support for virtual packages in
2022](https://github.com/conda/conda/pull/11854), but the plugins have not
proliferated much beyond [the core collection in the conda
repository](https://github.com/conda/conda/tree/main/conda/plugins/virtual_packages). 
Other conda installer tools incorporate their own detection routines
([rattler](https://github.com/conda/rattler/tree/b5331baae3629a25f43b137649adad2c61bcab53/crates/rattler_virtual_packages/src),
[mamba](https://github.com/mamba-org/mamba/blob/a1b92c2a62eab6294d7cca42e5dc211623a28f20/libmamba/src/core/virtual_packages.cpp)).
At time of writing, there is no sharing of hardware/system property detection
among conda installer tools.

**Current virtual packages include**

* archspec - CPU ID and capability
* OS, including system libraries (Linux/glibc, BSD, MacOS, Windows)
* CUDA driver version
