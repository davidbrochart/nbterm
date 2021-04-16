import json

from .cell import Cell  # type: ignore


class Format:

    nb_path: str

    def read_nb(self) -> None:
        with open(self.nb_path) as f:
            self.nb_json = json.load(f)
        self.cells = [
            Cell(self, idx=idx, cell_json=self.nb_json["cells"][idx])
            for idx, cell in enumerate(self.nb_json["cells"])
        ]

    def save_nb(self, path: str = "") -> None:
        path = path or self.nb_path
        if path:
            with open(path, "wt") as f:
                json.dump(self.nb_json, f, indent=1)
                f.write("\n")

    def create_nb(self) -> None:
        self.nb_json = {
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
        self.cells = [Cell(self, idx=0, cell_json=self.nb_json["cells"][0])]
