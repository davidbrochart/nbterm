import json
from pathlib import Path
from typing import Optional

from .cell import Cell
from .types import PathLike


class Format:

    nb_path: Optional[Path]
    save_path: Optional[Path]

    def read_nb(self) -> None:
        if self.nb_path is None:
            raise FileNotFoundError(
                "No nb_path was provided, cannot read existing notebook."
            )

        with self.nb_path.open() as f:
            self.json = json.load(f)
        self.set_language()  # type: ignore
        self.cells = [
            Cell(self, cell_json=cell_json) for cell_json in self.json["cells"]
        ]
        del self.json["cells"]

    def save(self, path: Optional[PathLike] = None) -> None:
        self.dirty = False
        path = (Path(path) if path else None) or self.save_path or self.nb_path
        if path:
            nb_json = {"cells": [cell.json for cell in self.cells]}
            nb_json.update(self.json)
            with path.open("wt") as f:
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
        self.set_language()  # type: ignore
        self.cells = [Cell(self)]
