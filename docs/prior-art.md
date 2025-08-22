# Prior art

## Gentoo

Gentoo is a source-first distribution with binary package support.
Binary packages can be used either as a primary installation method
from a remote source, or as a cache for packages previously built
from source. Source and binary packages can be freely mixed, with
the package manager automatically building from source when a matching
binary package is not available.

There are three main build parametrization methods in Gentoo:

1. So-called USE flags that are defined at package level, and primarily
   are used as switches for optional features and dependencies. They
   are also sometimes used to control use of CPU instruction sets
   (e.g. `CPU_FLAGS_X86`) or dependency versions (e.g. `LLVM_SLOT`).

2. Dependency binding (the `:=` operator) that is used to indicate
   that the package is bound to the current ABI (usually `SOVERSION`)
   of the particular dependency, and needs to be rebuilt to use a newer
   ABI version.

3. Regular environment variables that are used for more fine-tuning,
   primarily including generic variables such as `CC` or `CFLAGS`.

Gentoo binary packages store the USE flags, dependency bounds and some
standard environment variables within the metadata, and use them to
determine whether a particular binary package can satisfy the request.
To support different binary package variants, the filename contains
a monotonically increasing `build-id` (e.g. `-1`, `-2`...). The metadata
from all binary packages is cached in a single file that is used
by the package manager to find the right binary package.

USE flags are effectively boolean, with each flag being either enabled
or disabled. The default state for flags can be provided at global,
profile (a system configuration such as "amd64 multilib desktop with
systemd") and package level, and can be overriden by the user (for all
packages or for specific packages).

There is almost no automation to select flags. When 
For `CPU_FLAGS*` variables Gentoo provides a separate tool to query
the CPU, and output the suggested value. However, this is entirely
manual and needs to be repeated whenever new flags are added to Gentoo.


There are three bits of syntax related to USE flags:

1. Dependencies can be expressed conditionally to flags, using
   USE-conditional groups:

   - `flag? ( ... )` - dependencies apply only if `flag` is *enabled*
   - `!flag? ( ... )` - dependencies apply only if `flag` is *disabled*

2. Dependencies can be used to require state of USE flags on other
   packages, using USE dependencies `dep[flag1,flag2...]`, where `flag`
   can use one of the following forms:

   - `flag` - must be *enabled* on the dependency
   - `-flag` - must be *disabled* on the dependency
   - `flag?` - must be *enabled* on the dependency if it is *enabled*
     on this package (shorthand for `flag? ( dep[flag] )`
   - `flag=` - must have the *same state* on the dependency as on this
     package (shorthand for `flag? ( dep[flag] ) !flag? ( dep[-flag] )`)
   - `!flag=` - must have the *opposite state* on the dependency,
     compared to this package (`flag? ( dep[-flag] ) !flag? ( dep[flag] )`)
   - `!flag?` - must be *disabled* on the dependency if it is *disabled*
     on this package (`!flag? ( dep[-flag] )`)

   The two last variants are almost never used.

3. Constraints can be placed to restrict how different flags can be
   combined in the package (so called `REQUIRED_USE`). Individual
   constraints may use the following features:

   - `flag` - must be *enabled*
   - `!flag` - must be *disabled*
   - `flag? ( ... )` and `!flag? ( ... )` - constraints conditional
     to other flags, just like in dependencies
   - `|| ( flag1 flag2 ... )` - *at least one* flag from the group must
     be enabled
   - `^^ ( flag1 flag2 ... )` - *exactly one* flag from the group must
     be enabled
   - `?? ( flag1 flag2 ... )` - *at most one* flag from the group must
     be enabled

The boolean nature of USE flags makes providing a reasonable complete
syntax simple. However, it implies that enumerations (such as versions)
need to be redefined as long lists of flags, along with long lists
of dependencies and constraints. Ebuilds are bash scripts, so this
is often done using loops.

## Conda

Conda is a binary-only package ecosystem. It was created by [package
maintainers who were frustrated with python's rough support for binary
packages](https://jakevdp.github.io/blog/2016/08/25/conda-myths-and-misconceptions/#Myth-#4:-Creating-conda-in-the-first-place-was-irresponsible-&-divisive).
The package collection includes both high-level integrations (PyTorch, 
GDAL, etc.) and low-level dependencies such as compilers and C++ runtimes.
As such, Conda has approximately the same control over the runtime environment
as base operating systems. It has proven especially useful for providing an
up-to-date package collection on older operating systems, where the system
package manager may not have a current package selection.

Conda is based around dependency solvers, and these solvers enable
sharing core libraries. Conda benefits greatly from build tooling
being concentrated (though not standardized). A given package builder group
(e.g. Anaconda, Conda-forge) mostly produces binary-compatible packages,
because they are self-consistent. As time passed and the package 
ecosystem grew, it became harder to simultaneously satisfy everyone's 
needs. Furthermore, users mixing packages from different sources often
had a poor user experience with lots of problem. The conda filename format 
included specifiers for a few things in the package (python version, numpy version mainly), but most package
dependencies were not represented in any way in the filename. This
prevented builds of a given package with two different options,
such as version of a dependency. This is analogous to [Python's platform compatibility tags
](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/), 
except that conda captures the platform itself as a folder. This is basically the same 
state that motivated the current wheel variant rework effort. Importantly, conda
does not rely on the filename to resolve packages. Instead, a centralized index 
aggregates package metadata and presents it all together, all at once.

In [2016](https://github.com/conda/conda-build/issues/1142)-[2017](https://www.anaconda.com/blog/package-better-conda-build-3), the conda community 
developed a "variant" scheme that [differentiated packages based on arbitrary metadata]. The
scheme allowed substitution of values in a package recipe, and then calculated a hash for packages
based on the keys and values that were used by the substitution. Some users thought that the
hashes were opaque, and indeed, they were, but they were not meant to be human readable. The assumption
was that users were not interactively choosing files to download based on filename. The solver would take care 
of figuring out the appropriate package based on package metadata. Contemporaneously,
PyPI provided plain file listings, and many tools that use PyPI still only use the filename 
for resolving which package to install. Instead of resolving using filename, conda matches
input specs to package metadata. In practice, this means that if you can express some attribute
of what you want as a package constraint, you can choose that attribute. Metapackages, which
are packages with only metadata, are often used to make these preferences simpler for end users. For example,
in conda-forge, there are [metapackages named after various MPI implementations that select a particular variant of one package, with variants being differentiated by build string](https://conda-forge.org/docs/maintainer/knowledge_base/#preferring-a-provider-usually-nompi).

In [2019, the conda community developed the notion of a "virtual package" for CUDA](https://github.com/conda/conda/pull/8267).
A virtual package detects the system state and injects that state into the solver as package constraints. 
Other packages that have been built with a need for particular hardware would have a constraint to match 
the expected detected hardware value. Virtual packages have also served to help users understand base 
operating system compatiblity (required glibc version). 
This is similar to [the newest Manylinux standard](https://peps.python.org/pep-0600/), except that 
conda's resolver is treating this as a package constraint rather than a filename component.

Conda added [plugin support for virtual packages in 2022](https://github.com/conda/conda/pull/11854),
but the plugins have not proliferated much beyond [the core collection in the conda repository](https://github.com/conda/conda/tree/main/conda/plugins/virtual_packages).
This makes hardware detection functionality a standard, built-in part of conda.
