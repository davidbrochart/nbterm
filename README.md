[![Build Status](https://github.com/davidbrochart/nbterm/workflows/CI/badge.svg)](https://github.com/davidbrochart/nbterm/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# nbterm

Lets you view, edit and execute Jupyter Notebooks in the terminal.

## Install

Using pip:

```
pip install nbterm
```

Using conda:

```
mamba install nbterm -c conda-forge
```

You will also need a kernel, e.g. `ipykernel` or `xeus-python` for Python, `xeus-cling` for C++.

## Usage

Open an interactive notebook:

```
$ nbterm my_notebook.ipynb
```

Run a notebook in batch mode:

```
$ nbterm --run my_notebook.ipynb
```

## Key bindings

There are two modes: edit mode, and command mode.

- `enter`: enter the edit mode, allowing to type into the cell.
- `esc`: exit the edit mode and enter the command mode.

In command mode:

- `up`: select cell above.
- `down`: select cell below.
- `ctrl-up`: move cell above.
- `ctrl-down`: move cell below.
- `a`: insert cell above.
- `b`: insert cell below.
- `x`: cut the cell.
- `c`: copy the cell.
- `ctrl-v`: paste cell above.
- `v`: paste cell below.
- `o`: set as code cell.
- `m`: set as Markdown cell.
- `l`: clear cell outputs.
- `ctrl-e`: run cell.
- `ctrl-r`: run cell and select below.
- `ctrl-s`: save.
- `ctrl-q`: exit.
- `ctrl-h`: show help.
