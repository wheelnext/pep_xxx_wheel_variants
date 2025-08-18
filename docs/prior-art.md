# Prior art

## Gentoo

Gentoo is a source-first distribution with binary package support.
Binary packages can be used either as a primary installation method
from a remote source, or as a cache for packages previously built
from source. Source and binary packages can be freely mixed, with
the package manager automatically buildig from source when a matching
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

The choice of features is mostly manual in Gentoo. The distribution
provides some defaults, and users often adjust the remaining flags
to their needs. Packages can express dependencies on specific USE
configurations of other packages, in which case the package manager
suggests adjustments.

For `CPU_FLAGS*` variables Gentoo provides a separate tool to query
the CPU, and output the suggested value. However, this is entirely
manual and needs to be repeated whenever new flags are added to Gentoo.
