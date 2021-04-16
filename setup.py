from setuptools import setup

setup(
    name="nbterm",
    version="0.0.3",
    url="https://github.com/davidbrochart/nbterm.git",
    author="David Brochart",
    author_email="david.brochart@gmail.com",
    description="A tool for viewing, editing and executing Jupyter Notebooks in the terminal",
    packages=["nbterm"],
    python_requires=">=3.7",
    install_requires=[
        "prompt-toolkit>=3.0.16",
        "typer",
        "pygments",
        "rich",
        "kernel_driver",
    ],
    extras_require={
        "test": [
            "mypy",
            "flake8",
            "black",
        ],
    },
    entry_points={
        "console_scripts": ["nbterm = nbterm.nbterm:cli"],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
