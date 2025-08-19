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
