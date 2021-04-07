import json

from .cell import Cell


def read_nb(nb):
    with open(nb.nb_path) as f:
        nb.nb_json = json.load(f)
    nb.cells = [
        Cell(idx=idx, cell_json=nb.nb_json["cells"][idx])
        for idx, cell in enumerate(nb.nb_json["cells"])
    ]


def save_nb(nb):
    if nb.nb_path:
        with open(nb.nb_path, "wt") as f:
            json.dump(nb.nb_json, f)


def create_nb(nb):
    nb.nb_json = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 0,
                "metadata": {},
                "source": [],
                "outputs": [],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "version": "3.9.2",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }
    nb.cells = [Cell(idx=0, cell_json=nb.nb_json["cells"][0])]
