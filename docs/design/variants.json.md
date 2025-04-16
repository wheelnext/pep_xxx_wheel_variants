# variants.json

## Purpose

This document describes the `variants.json` file used to document wheel
variants published on an index.


## Base requirements

Every index page that links at least one variant wheel must also include
a link to a `variants.json` file that describes variants found on that
index page. Every variant hash found on that page must be listed
in `variants.json`. The file can list additional variant hashes,
in particular a single `variants.json` file can be shared across
multiple index pages, in particular between multiple packages.

The file must be a valid JSON document whose top-level element is
an object. The contents of that object must conform to this
specification, or any future version of it. The only required key
is `variants`, all other keys are optional. Tools must ignore unknown
keys, to account for future extensions.


## Example file

```
{
  "providers" : {
     "fictional_hw" : "provider_fictional_hw",
     "fictional_tech" : "provider_fictional_tech"
  },
  "variants": {
    "6b4c8391": {
      "fictional_hw": {
        "architecture": "deepthought",
        "compute_accuracy": "10",
        "compute_capability": "10",
        "humor": "0"
      },
      "fictional_tech": {
        "quantum": "FOAM"
      }
    },
    "9091cdc4": {
      "fictional_tech": {
        "quantum": "SUPERPOSITION",
        "risk_exposure": "25",
        "technology": "auto_chef"
      }
    }
  }
}
```


## `variants` key

The `variants` key is the only obligatory key. It is used to describe
the properties corresponding to individual variant hashes, and can
be used by packaging tools to select a variant without having to fetch
the wheel and read its metadata.

The value of `variants` key is an object mapping variant hashes into
compacted variant description. A compacted variant descriptions are
objects mapping namespaces into objects that map feature names into
their respective values.

For example, the following properties:

```
fictional_hw :: architecture :: deepthought
fictional_hw :: compute_accuracy :: 10
fictional_tech :: quantum :: FOAM
```

would be expressed as:

```
{
  "fictional_hw": {
    "architecture": "deepthought",
    "compute_accuracy": "10"
  },
  "fictional_tech": {
    "quantum": "FOAM"
  }
}
```


## `providers` key

The optional `providers` key is an object mapping variant namespaces
into [dependency
specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
that indicate which packages provide the plugins implementing said
namespace. The tools may use this list to install the necessary plugins
or to inform the user which packages are missing for variant support.
