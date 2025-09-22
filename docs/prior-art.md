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

Conda is a binary-only package ecosystem. It was created by [package
maintainers who were frustrated with python's rough support for binary
packages](https://jakevdp.github.io/blog/2016/08/25/conda-myths-and-misconceptions/#Myth-#4:-Creating-conda-in-the-first-place-was-irresponsible-&-divisive).
The package collection includes both high-level integrations (PyTorch, 
GDAL, etc.) and low-level dependencies such as compilers and C++ runtimes.
As such, Conda has approximately the same control over the runtime environment
as base operating systems. It has proven especially useful for providing an
up-to-date package collection on older operating systems, where the system
package manager may not have a current package selection. Moreover, multiple
conda environments can exist on one system, giving the user an easy way
to switch between versions of software, or to use conflicting software
that otherwise could not coexist on a system. Conda environments are isolated
using separation on disk, with OS-standard environment variables guiding
commands to the currently-selected conda environment.

### Accessible metadata

Conda divides packages by platform (aka "subdir"), like `linux-64`. Within
each platform, a conda package filename is made up of three parts: 
[the package name, version, and build string](https://docs.conda.io/projects/conda-build/en/stable/concepts/package-naming-conv.html).
Conda does not rely on the filename for the resolution process. Instead,
each conda package contains metadata, and the metadata is aggregated into
a single, comprehensive [index per
subdir](https://docs.conda.io/projects/conda-build/en/stable/concepts/generating-index.html).
This usage of an index instead of a filename means that the filename need not
contain any meaningful information about a package - any information is purely
for human convenience. One further advantage of this metadata aggregation is
that [the index contents can be "patched" to correct
constraints](https://docs.conda.io/projects/conda-build/en/stable/concepts/generating-index.html#repodata-patching).
This is helpful when dependencies break unexpectedly (index can adjust upper
bounds to avoid break). The metadata in the index is generally not handled as
standalone data. Instead, it is incorporated into dependency expressions
somehow, such that the dependency solver can make choices based on the metadata.

### Compatibility and the need for more metadata

From its creation, conda was designed to use shared libraries that several
packages in an environment may utilize. This is [the opposite of
wheels](https://github.com/pypa/auditwheel), which have advised per-wheel
isolation. Aligning binaries to maintain compatibility can be difficult, and
gets more difficult as the number of ways that builds can vary goes up. Conda
packages were first produced only by Continuum Analytics (now Anaconda). It was
easy to maintain consistency, because Anaconda controlled the toolchain and the
version choices. Anaconda created binstar.org, which became anaconda.org, as a
central host for anyone to upload their conda packages. Several
users/organizations published large collections of packages to anaconda.org.
This was a great expansion of packages beyond the collection that Anaconda
offered on their official channel.  Unfortunately, there were no guarantees
about compatibility between channels, nor any metadata to express such
compatibility or lack thereof. Mixing packages from different channels often
yielded undefined behavior - crashes and/or corruption. At the same time, it was
common that any single channel wouldn't have all of the desired packages for an
environment, and it was tempting to mix packages from multiple channels. This
situation is shared by projects on PyPI that share dependencies.  It may be
possible for numpy and scipy to share a BLAS library because numpy and scipy are
built and maintained by the same people. It is more difficult for arbitrary
projects maintained by different people to align, hence the guidance that wheels
be standalone and independent of one another.

In other words, conda channels collect many packages built by one or a few
organizations, whereas PyPI collects many packages built by many organizations.

The creation of [conda-forge](https://conda-forge.org/docs/user/introduction/)
as a centralized recipe collection and build infrastructure dramatically
improved the multiple-source problem for conda. This community unified several
of the independent organizations, working with Anaconda to preserve
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
based on arbitrary metadata. The scheme allowed substitution of values in a
package recipe, and then calculated a hash for packages based on the keys and
values that were used by the substitution. The hashes served to avoid file
clobbering on disk - to give each package variant a unique key. The assumption
with the hashes was that users were not interactively choosing files to download
based on filename.  The solver would take care of figuring out the appropriate
package based on package metadata. This was and still is in contrast to tools
that use PEP 503/691 indices with plain file listings, primarily using the
filename for resolving which package to install. Filename matching schemes
do not scale well. They are based on string matching and ordering. Arbitrary
metadata is not feasible using a filename matching scheme. 

For example, if there are two packages (A) built with 
different versions of the same dependency, `A -> B-1`, `A -> B-2`, you could
choose a specific A package by specifying a constraint like `A, B==2`.

### Exposing user tools to specify variants

It becomes more challenging to express preference for packages with different 
dependencies. This is because when package name is the same among options, exclusivity
among those options is implicit. Given `A -> B`, `A -> C`, specifying a constraint of `A, C`
does not preclude `B` being installed. When this situation arises, it becomes helpful
to utilize a metapackage that restores exclusivity within one package name. Metapackages 
are packages with only metadata. An example are often used to make these preferences simpler for end users. For example, in
conda-forge, there are [metapackages named after various MPI implementations
that select a particular variant of one package, with variants being
differentiated by build
string](https://conda-forge.org/docs/maintainer/knowledge_base/#preferring-a-provider-usually-nompi).

In [2019, the conda community developed the notion of a "virtual package" for
CUDA](https://github.com/conda/conda/pull/8267).  A virtual package detects the
system state and injects that state into the solver as package constraints. 
Other packages that have been built with a need for particular hardware would
have a constraint to match the expected detected hardware value. Virtual
packages have also served to help users understand base operating system
compatiblity (required glibc version).  This is similar to [the newest Manylinux
standard](https://peps.python.org/pep-0600/), except that conda's resolver is
treating this as a package constraint rather than a filename component.

Conda added [plugin support for virtual packages in
2022](https://github.com/conda/conda/pull/11854), but the plugins have not
proliferated much beyond [the core collection in the conda
repository](https://github.com/conda/conda/tree/main/conda/plugins/virtual_packages). 
Other conda ecosystem installers incorporate their own detection routines
([rattler](https://github.com/conda/rattler/tree/b5331baae3629a25f43b137649adad2c61bcab53/crates/rattler_virtual_packages/src),
[mamba](https://github.com/mamba-org/mamba/blob/a1b92c2a62eab6294d7cca42e5dc211623a28f20/libmamba/src/core/virtual_packages.cpp)).
