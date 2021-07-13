import json
from pathlib import Path
from typing import Optional

from .cell import Cell


class Format:

    nb_path: Path
    save_path: Optional[Path]

    def read_nb(self) -> None:
        with open(self.nb_path) as f:
            self.json = json.load(f)
        self.set_language()  # type: ignore
        self.cells = [
            Cell(self, cell_json=cell_json) for cell_json in self.json["cells"]
        ]
        del self.json["cells"]

    def save(self, path: Optional[Path] = None) -> None:
        self.dirty = False
        path = path or self.save_path or self.nb_path
        nb_json = {"cells": [cell.json for cell in self.cells]}
        nb_json.update(self.json)
        with open(path, "wt") as f:
            json.dump(nb_json, f, indent=1)
            f.write("\n")

    def create_nb(self, kernelName="python3") -> None:
        if kernelName == "python3":
            self.json = {
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python",
                    },
                    "language_info": {
                        "file_extension": ".py",
                        "mimetype": "text/x-python",
                        "name": "python",
                        "version": "3.9.3",
                    },
                },
                "nbformat": 4,
                "nbformat_minor": 4,
            }
        elif kernelName == "c":
            self.json = {
                "metadata": {
                    "kernelspec": {
                        "display_name": "C",
                        "language": "c",
                        "name": "c",
                    },
                    "language_info": {
                        "file_extension": ".c",
                        "mimetype": "text/plain",
                        "name": "c",
                    },
                },
                "nbformat": 4,
                "nbformat_minor": 4,
            }
        elif kernelName == "jupyter-php":
            self.json = {
                "metadata": {
                    "kernelspec": {
                        "display_name": "PHP",
                        "language": "php",
                        "name": "jupyter-php",
                    },
                    "language_info": {
                        "file_extension": ".php",
                        "mimetype": "text/x-php",
                        "name": "PHP",
                    },
                },
                "nbformat": 4,
                "nbformat_minor": 4,
            }
        elif kernelName == "javascript":
            self.json = {
                "metadata": {
                    "kernelspec": {
                        "display_name": "JavaScript",
                        "language": "js",
                        "name": "javascript",
                    },
                    "language_info": {
                        "file_extension": ".py",
                        "mimetype": "text/x-python",
                        "name": "javascript",
                    },
                },
                "nbformat": 4,
                "nbformat_minor": 4,
            }
        else:
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
                        "version": "3.9.3",
                    },
                },
                "nbformat": 4,
                "nbformat_minor": 4,
            }

        self.set_language()  # type: ignore
        self.cells = [Cell(self)]
