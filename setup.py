from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
import pybind11

ext_modules = [
    Pybind11Extension(
        "gil_demo",
        ["gil_demo.cpp"],
        include_dirs=[pybind11.get_cmake_dir()],
    ),
]

setup(
    name="gil_demo",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
)