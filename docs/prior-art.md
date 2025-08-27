# Prior art

## Gentoo

[Gentoo Linux](https://www.gentoo.org) is a source-first distribution with support for extensive package customization. The primary means of this customization are so-called [USE flags](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/USE): boolean flags exposed by individual packages and permitting fine-tuning the enabled features, optional dependencies and some build parameters. For example, a flag called `jpegxl` controls the support for JPEG XL image format, `cpu_flags_x86_avx2` controls building SIMD code utilizing AVX2 extension set, while `llvm_slot_21` indicates that the package will be built against LLVM 21\.

Gentoo permits using [binary packages](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Features#Binary_package_support) both as a primary installation method and a local cache for packages previously built from source. Among the metadata, binary packages store the configured USE flags and some other build parameters. Multiple binary packages can be created from a single source package version, in which case the successive packages are distinguished by monotonically increasing build numbers. The dependency resolver uses a combined package cache file to determine whether any of the available binary packages can fulfill the request, and falls back to building from source if none can.

The interesting technical details about USE flags are:

1. Flags are defined for each package separately (with the exception of a few special flags). Their meanings can be either described globally or per package. The default values can be specified at package or profile (a system configuration such as “amd64 multilib desktop”) level.  
2. Global flags can be grouped for improved UX. Examples of groups are `CPU_FLAGS_X86` that control SIMD code for x86 processors, and `LLVM_SLOT` that select the LLVM version to build against.  
3. With the exception of a few special flags, there is no automation to select the right flags. For `CPU_FLAGS_X86`, Gentoo provides an external tool to query the CPU and provide a suggested value, but it needs to be run manually, and rerun when new flags are added to Gentoo. The package managers also generally suggest flag changes needed to satisfy the dependency resolution.  
4. Dependencies, package sources and build rules can be conditional to use flags:  
   * `flag? ( … )` is used only when the flag is enabled  
   * `!flag? ( … )` is used only when the flag is disabled  
5. Particular states of USE flags can be expressed on dependencies, using a syntax similar to Python extras: `dep[flag1,flag2…]`.  
   * `flag` indicates that the flag must be enabled on the dependency  
   * `!flag` indicates that the flag must be disabled on the dependency  
   * `flag?` indicates that it must be enabled if it is enabled on this package  
   * `flag=` indicates that it must have the same state as on this package  
   * `!flag=` indicates that it must have the opposite state than on this package  
   * `!flag?` indicates that it must be disabled if it is disabled on this package  
6. Constraints can be placed upon state of USE flags within a package:  
   * `flag` specifies that the flag must be enabled  
   * `!flag` specifies that the flag must be disabled  
   * `flag? ( … )` and `!flag? ( … )` conditions can be used like in dependencies  
   * `|| ( flag1 flag2 … )` indicates that at least one of the specified flags must be enabled  
   * `^^ ( flag1 flag2 … )` indicates that exactly one of the specified flags must be enabled  
   * `?? ( flag1 flag2 … )` indicates that at most one of the specified flags must be enabled

This syntax has been generally seen as sufficient for Gentoo. However, its simplicity largely stems from the fact that USE flags have boolean values. This also has the downside that multiple flags need to be used to express enumerations.
