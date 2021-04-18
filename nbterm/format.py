import json

from .cell import Cell


class Format:

    nb_path: str

    def read_nb(self) -> None:
        with open(self.nb_path) as f:
            self.json = json.load(f)
        self.cells = [
            Cell(self, cell_json=cell_json) for cell_json in self.json["cells"]
        ]
        del self.json["cells"]

    def save(self, path: str = "") -> None:
        path = path or self.nb_path
        if path:
            nb_json = {"cells": [cell.json for cell in self.cells]}
            nb_json.update(self.json)
            with open(path, "wt") as f:
                json.dump(nb_json, f, indent=1)
                f.write("\n")

    def create_nb(self) -> None:
        self.json = {
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
        self.cells = [Cell(self)]
