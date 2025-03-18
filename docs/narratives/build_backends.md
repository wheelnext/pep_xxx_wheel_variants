# Building wheel variants - UX design

## Querying plugin variables and values

Before we start building, we need to know what variants can potentially be built.
For now we assume that a plugin provides:

1. Variables (e.g., `blas`, `mpi`, `threading`, `cuda`, `rocm`, `psabi`, `simd`,)
2. Values (the known set of values for each variable)

This may look something like this:

```bash
$ cuda-plugin --list-variables
cuda
...
$ cuda-plugin --list-values cuda
11.6
12.0
12.4
12.6

$ x86-plugin --list-variables
psabi

$ x86-plugin --list-values psabi
x86-64-v1
x86-64-v2
x86-64-v3
x86-64-v4
```

However the details of the UX for the plugin itself don't matter too much for
our purposes in this document - let's assume that other tools have access to
these variables and values, which are determined with some combination of the
plugin's built-in functionality and user-provided configuration.


## Telling build backend to build a particular variant

A wheel variant build is invoked through a build frontend (e.g., `pip`, `build`,
`uv build`). There's multiple possible ways for the actual build (dependencies
linked against, compiler flags, etc.) to be influenced:

1. The plugin may set some standard environment variables (e.g., `CFLAGS`,
   `CXXFLAGS`, `LDFLAGS`).
2. The build backend may recognize a variant variable plus value and do
   something specific to that (e.g., try detecting and linking a dependency).
3. The user building the wheel may take actions to ensure the build does the
   desired things to produce the wheel variant, e.g.:

   - Provide the variant name and value
   - Install required build-time dependencies before starting the build
   - Apply patches to the package's source code before starting the build
   - Modify environment variables
   - Pass custom build flags to the backend via `--config-settings`
   - Post-process the wheel, either with a tool like `auditwheel` or manually

The simplest case is only (1). Invoking such a build for a package that respects
`CFLAGS`/`LDFLAGS` and needs nothing else could look like:

```bash
# E.g., a default psabi-v3 usage with meson-python
$ python -m build -Cvariant="psabi=x86-64-v3"
```

What actually happens under the hood for that build command? The build frontend,
`build` in this case, only passes on the `-C` (shorthand for `--config-settings`)
to the build backend. The build backend, `meson-python` in this case, may do the
following:

1. Query the plugins, find that `x86-plugin` provides the `psabi` variable, then
   retrieve what that means in terms of `CFLAGS`/`CXXFLAGS`/`LDFLAGS` (that's
   all one can probably support inside the plugin).
2. Pass on those flags, either by amending those environment variables *or* by
   translating them to CLI flags (e.g., C compiler flags can be passed like
   `-Dc_args=xxx`, which is nicer for logging than amending environment
   variables).
3. Once the build is complete and the wheel is being assembled, modify the
   wheel filename and modify the `METADATA` file to insert the variant content

Now let's look at a more complicated example: building a NumPy wheel for
`psabi=x86-64-v3`. The difference is that NumPy contains SIMD code and custom
build flags to control whether and how that code gets included and used.
The build backend cannot know this, hence the user invoking the build must
instruct `meson-python` to only handle step (3) above, and not attempt to do
(1) and (2). This is done by using the `-Cvariant-name` config setting, rather
than `-Cvariant`:

```bash
# Build a NumPy psabi=x86-64-v3 wheel; this requires nonstandard flags (we want
# to keep >v3 runtime-dispatched features)
$ python -m build --wheel -Cvariant-name="psabi=x86-64-v3" -Csetup-args=-Dcpu-baseline=AVX2,FMA3 -Csetup-args=-Dcpu-dispatch=AVX512F,AVX512_SKX
```

Note that we've introduced two ways of specifying a variant build so far (which
is probably all we'll need):

- `-Cvariant=variable=value`: specify the wheel variant to build *and* let
  the plugin add defaults (compile and link flags)
- `-Cvariant-name=variable=value`: only specify the wheel variant to build

So far so good for how to build x86-64 SIMD variants. Let's look at a second
realistic case, namely BLAS variants. The difference is that we need not only
compile and link flags, but also a different dependency - during the build,
the correct shared library must be found *and* before the build, the user
must have prepared the build environment correctly to ensure the shared library
is actually present.

Given the different dependencies here, and the relevant linker flags being
different per build system, the plugin has no way to provide any compile/link
flags here or do anything else that's helpful (it doesn't know after all which
build backend we'll be using).

Here is what the plugin's variables and values may be:

```bash
$ blas-plugin --list-variables
blas
lapack

$ blas-plugin --list-values blas
openblas
accelerate
mkl
blis
netlib
```

Now what will the simple case from earlier, using `-Cvariant=blas=mkl`, do?
`meson-python` itself doesn't know what to do for that variant, so (design choice)
it may error or it may pass on `-Cvariant=blas=mkl` to `meson setup`, at which
point it will error there unless a `variant` build option is implemented in
NumPy's `meson.options` file (not present today, but easy to do).

```bash
$ python -m build -Cvariant="blas=mkl"
```

To make it work with the build options NumPy has today, the build invocation
should be:
```bash
# Now let the package builder pass the argument.
$ python -m build -Cvariant-name=blas=mkl -Csetup-args=-Dblas=mkl
```

The above gives us the ingredients to build a single `numpy` variant wheel.
Handling a whole set of build variants at once can be automated on top of that -
for now there doesn't seem to be a need for custom tooling to handle that.
The next section shows a pragmatic way this can be done with tools we already have.

# Building a matrix of variant wheels

If an individual variant is easy to build through a build frontend, then scripting
a matrix should be straightforward.

For wheels distributed to PyPI, an easy way to do this may be to leverage what
is already being done for building a set of wheels for diffent platforms and
Python versions, which is typically to use a build matrix in GitHub Actions:

```yaml
jobs:
  build_wheel_variants:
    name: Wheel, ${{ matrix.python[0] }}-${{ matrix.buildplat[1] }}
      ${{ matrix.buildplat[2] }} ${{ matrix.buildplat[3] }}
      ${{ matrix.buildplat[4] }}
    runs-on: ${{ matrix.buildplat[0] }}

    strategy:
      matrix:
        buildplat:
        - [ubuntu-22.04, manylinux, x86_64, "", ""]
        - [ubuntu-22.04, musllinux, x86_64, "", ""]
        - [ubuntu-22.04, manylinux, x86_64, "psabi-v3", ""]
        - [ubuntu-22.04, manylinux, x86_64, "psabi-v3", "mkl"]
        python: ["cp312", "cp313"]

    steps:
      - name: Checkout source of pacakge
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Setup Python interpreter to run cibuildwheel
        uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5.3.0
        with:
          python-version: 3.13

      - name: Handle variant builds
        run: |
          # psabi (x86-64 SIMD) variants
          if [[ ${{ matrix.buildplat[2] }} != '' ]]; then
            # Will still include dispatching for AVX512 features as well, it just
            # increases the baseline features that are required.
            export VARIANT_CONFIG=\"variant-name=${{ matrix.buildplat[2] }} cpu-baseline=AVX2,FMA3\"
          fi

          # BLAS variant
          if [[ ${{ matrix.buildplat[3] }} == 'mkl' ]]; then
            python -m pip install mkl
            export VARIANT_CONFIG=\"variant-name=mkl setup-args=-Dblas=mkl\ $VARIANT_CONFIG"
          fi
          echo CIBW_CONFIG_SETTINGS=$VARIANT_CONFIG >> "$GITHUB_ENV"

      - name: Build wheels
        uses: pypa/cibuildwheel@7940a4c0e76eb2030e473a5f864f291f63ee879b # v2.21.3
        env:
          CIBW_BUILD: ${{ matrix.python[0] }}-${{ matrix.buildplat[1] }}*
          CIBW_ARCHS: ${{ matrix.buildplat[2] }}
          TODO: pass on build variants!

      - uses: actions/upload-artifact@b4b15b8c7c6ac21ea08fcf65892d2ee8f75cf882 # v4.4.3
        with:
          path: ./wheelhouse/*.whl
          name: ${{ matrix.python[0] }}-${{ matrix.buildplat[1] }}
            ${{ matrix.buildplat[2] }} ${{ matrix.buildplat[3] }}
            ${{ matrix.buildplat[4] }}
```

This should yield four wheels named like (plus four more with `cp312` instead of `cp313`):
```
numpy-2.2.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
numpy-2.2.4-cp313-cp313-manylinux_2_17_x86_64.musllinux2014_x86_64.whl
numpy-2.2.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64-h03981ea44+psabi-x86-64-v3.whl
numpy-2.2.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64-h0f4317532+psabi-x86-64v3+blas-mkl.whl
```
