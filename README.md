[![Build Status](https://github.com/davidbrochart/nbterm/workflows/CI/badge.svg)](https://github.com/davidbrochart/nbterm/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# nbterm

Lets you view, edit and execute Jupyter Notebooks in the terminal.

## Key bindings

There are two modes: cell mode, and notebook mode.

- `enter`: enter the cell mode, allowing to modify the content of the cell.
- `esc`: exit the cell mode and enter the notebook mode.

When in notebook mode:

- `up` and `down` arrows: navigate through cells.
- `ctrl-i`: insert a new cell before the current one.
- `ctrl-j`: insert a new cell after the current one.
- `ctrl-d`: delete the cell.
- `ctrl-o`: set the cell type to Code.
- `ctrl-n`: set the cell type to Markdown.
- `ctrl-l`: clear the output of the cell.
- `ctrl-e`: execute the cell and stay on it.
- `ctrl-r`: execute the cell and move to the next one.
- `ctrl-s`: save the notebook.
- `ctrl-q`: exit the application.
