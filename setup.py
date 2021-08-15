import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(here, "nbtermix", "_version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="nbtermix",
    version=version_ns["__version__"],
    url="https://github.com/mtatton/nbterm",
    author="Michael Tatton",
    description="Fork of nbterm. Jupyter Notebooks in Your terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["nbtermix"],
    python_requires=">=3.7",
    install_requires=[
        "prompt-toolkit>=3.0.16",
        "typer",
        "pygments",
        "rich",
        "kernel_driver>=0.0.6",
    ],
    extras_require={
        "test": [
            "mypy",
            "flake8",
            "black",
            "pytest",
            "ipykernel",
        ],
    },
    entry_points={
        "console_scripts": ["nbtermix = nbtermix.nbterm:cli"],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
