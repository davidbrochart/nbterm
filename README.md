[![Build Status](https://github.com/davidbrochart/nbtermix/workflows/CI/badge.svg)](https://github.com/davidbrochart/nbtermix/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# nbtermix

Lets you view, edit and execute Jupyter Notebooks in the terminal.

## Install

Using pip:

```
pip install nbtermix
```

Using conda:

```
mamba install nbtermix -c conda-forge
```

You will also need a kernel, e.g. `ipykernel` or `xeus-python` for Python, `xeus-cling` for C++.

## Usage

Open an interactive notebook:

```
$ nbtermix my_notebook.ipynb
```

Run a notebook in batch mode:

```
$ nbtermix --run my_notebook.ipynb
```

## Key bindings

There are two modes: edit mode, and command mode.

- `e`: enter the edit mode, allowing to type into the cell.
- `esc`: exit the edit mode and enter the command mode.

In edit mode:
- `ctrl-e`: run cell.
- `ctrl-r`: run cell and select below in edit mode.
- `ctrl-t`: open cell result in external editor.
- `ctrl-w`: open cell in external editor.
- `ctrl-f`: save tmp file from cell and execute it.
- `ctrl-s`: save.
 
In command mode:

- `up` or k: select cell above.
- `down` or j: select cell below.
- `ctrl-g`: go to last cell.
- `1` `g`: go to first cell.
- `ctrl-up`: move cell above.
- `ctrl-down`: move cell below.
- `a`: insert cell above.
- `b`: insert cell below.
- `x`: cut the cell.
- `c`: copy the cell.
- `ctrl-v`: paste cell above.
- `v`: paste cell below.
- `o`: set as code cell.
- `r`: set as Markdown cell.
- `l`: clear cell outputs.
- `f`: fold current cell input.
- `ctrl-f`: Search
- `n`: Repeat last search.
- `ctrl-n`: Search backwards.
- `m`,`<any>`: Set mark <key>.
- `'`,`<any>`: Go to mark <key>.
- `ctrl-e` or `enter`: run cell.
- `ctrl-r` or `alt-enter`: run cell and select below.
- `ctrl-s`: save.
- `ctrl-p`: run all cells.
- `ctrl-q`: exit.
- `ctrl-h`: show help.

## Kernels

For more kernels visit:

![Jupyter kernels . jupyter/jupyter Wiki](https://github.com/jupyter/jupyter/wiki/Jupyter-kernels)

This nbtermix is tested on (install only if You know what You're doing):

### c kernel

```
pip install jupyter-c-kernel
install_c_kernel
```

### java kernel

```
wget https://github.com/SpencerPark/IJava/releases/download/v1.3.0/ijava-1.3.0.zip
unzip ijava-1.3.0.zip -d ijava
cd ijava
python install.py
apt-get isntall default-jdk
```

### javascript kernel

```
apt-get install nodejs npm libczmq-dev
npm install -g --unsafe-perm npm
npm install -g --unsafe-perm ijavascript
ijsinstall --install=global
```

### php kernel

```
apt-get install php composer php-zmq
wget https://litipk.github.io/Jupyter-PHP-Installer/dist/jupyter-php-installer.phar
chmod u+x jupyter-php-installer.phar
./jupyter-php-installer.phar install
```

### sqlite kernel from sqlok

```
pip3 install sqli-kernel
sqlik_install
```

### python3 kernel

```
out of the box
```

## Testing environment

using Python 3.9 and iPyKernel==6.0.0

```
pip install ipykernel==6.0.0

$ jupyter --version:

jupyter core     : 4.7.1
ipython          : 7.25.0
ipykernel        : 6.0.0
jupyter client   : 6.1.12

```

## Runtime Environment recommendations


Keep separated environment for the nbtermix

```
|= mkdir -p ~/pyenv
cd ~/pyenv
|= virtualenv -p /usr/bin/python3.9 nbtermix
|= source ~/pyenv/nbtermix/bin/activate
```

## CHANGELOG

```
minor changes to v.0.0.15 by mtatton
+ added folding for terminal space saving
+ renamed to nbtermix

minor changes to v.0.0.14 by mtatton
minor changes to v.0.0.13 by mtatton
minor changes to v.0.0.12 by mtatton
```
