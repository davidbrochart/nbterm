from setuptools import setup

setup(
    name="nbterm",
    version="0.0.1",
    url="https://github.com/davidbrochart/nbterm.git",
    author="David Brochart",
    author_email="david.brochart@gmail.com",
    description="A tool for viewing, editing and executing Jupyter Notebooks in the terminal",
    packages=["nbterm"],
    python_requires=">=3.7",
    install_requires=[
        "prompt-toolkit>=3",
        "click",
        "pygments",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
