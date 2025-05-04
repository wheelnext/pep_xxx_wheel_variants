# SPDX-License-Identifier: MIT

"""
This file is imported from https://github.com/pypa/build/blob/35d86b8/src/build/env.py
Some modifications have been made to make the code standalone.

If possible, this code should stay as close to the original as possible.
"""

import importlib
import importlib.util
import pathlib

from variantlib.installer import IsolatedPythonEnv
from variantlib.installer import NonIsolatedPythonEnv

package_name = "dummy-project"

with NonIsolatedPythonEnv(installer="uv") as env:
    # with NonIsolatedPythonEnv(installer="uv") as env:
    env.install([package_name])

    import_name = package_name.replace("-", "_")
    if env.python_executable is None:
        your_module = importlib.import_module(import_name)

    else:
        spec = importlib.util.spec_from_file_location(
            name=import_name,
            location=pathlib.Path(env.python_executable).parent,
        )
        your_module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(your_module)

    print(f"{your_module.__version__=}")
