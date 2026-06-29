# setup.py — builds tap_core.pyx into a compiled C extension
from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    name="tap_core",
    ext_modules=cythonize(
        "tap_core.pyx",
        compiler_directives={
            "language_level": "3",
            "boundscheck":    False,
            "wraparound":     False,
            "cdivision":      True,
        },
        annotate=True,      # generates tap_core.html for inspection
    ),
    include_dirs=[np.get_include()],
)
