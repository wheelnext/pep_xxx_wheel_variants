import re


def get_variant_hash_from_wheel(filename: str, USE_LEGACY: bool) -> bool:
    if USE_LEGACY:
        wheel_file_re = re.compile(
            r"""^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]*?))
            ((-(?P<build>\d[^-]*?))?-(?P<pyver>[^\s-]+?)-(?P<abi>[^\s-]+?)-(?P<plat>[^\s-]+?)
            \.whl|\.dist-info)$""",
            re.VERBOSE,
        )
    else:
        # wheel_file_re = re.compile(
        #     r"""^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]*?))
        #     ((-(?P<build>\d[^-]*?))?-(?P<pyver>[^\s-]+?)-(?P<abi>[^\s-]+?)-(?P<plat>[^\s-]+?)
        #     \.whl2|\.dist-info)$""",
        #     re.VERBOSE,
        # )
        wheel_file_re = re.compile(
            r"""^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]*?))
            ((-(?P<build>\d[^-]*?))?(-\#(?P<variant_hash>[0-9a-fA-F]{8}))?-(?P<pyver>[^\s-]+?)
            -(?P<abi>[^\s-]+?)-(?P<plat>[^\s-]+?)\.whl|\.dist-info)$""",
            re.VERBOSE,
        )

    wheel_info = wheel_file_re.match(filename)

    return wheel_info is not None


if __name__ == "__main__":
    filename = "dummy_project-0.0.1-py3-none-any.whl"

    print(f"{get_variant_hash_from_wheel(filename=filename, USE_LEGACY=True)=}")
    print(f"{get_variant_hash_from_wheel(filename=filename, USE_LEGACY=False)=}")

    print("\n-------------------------\n")

    filename = "dummy_project-0.0.1-py3-none-any.whl2"

    print(f"{get_variant_hash_from_wheel(filename=filename, USE_LEGACY=True)=}")
    print(f"{get_variant_hash_from_wheel(filename=filename, USE_LEGACY=False)=}")
