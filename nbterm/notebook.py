import os
import json
import itertools
import asyncio

from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit import Application

from .cell import Cell
from .key_bindings import default_kb


class Notebook:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            self.read_nb()
        else:
            self.cells = [Cell()]
        self.create_layout()
        self._current_cell = self.cells[0]
        self._cell_entered = False
        self.bind_keys()
        self.app = Application(
            layout=self.layout, key_bindings=self.key_bindings, full_screen=True
        )
        self.run()

    def read_nb(self):
        with open(self.path) as f:
            self.nb_json = json.load(f)
        self.cells = [
            Cell(idx=idx, cell_json=self.nb_json["cells"][idx])
            for idx, cell in enumerate(self.nb_json["cells"])
        ]

    def save_nb(self):
        with open(self.path, "wt") as f:
            json.dump(self.nb_json, f)

    def create_layout(self):
        inout_cells = list(
            itertools.chain.from_iterable(
                [(cell.input, cell.output) for cell in self.cells]
            )
        )
        root_container = ScrollablePane(HSplit(inout_cells))
        self.layout = Layout(root_container)

    def focus(self, idx):
        self.app.layout.focus(self.cells[idx].input_window)
        self._current_cell = self.cells[idx]

    def exit_cell(self):
        self._cell_entered = False
        self.current_cell.set_readonly()

    @property
    def current_cell(self):
        return self._current_cell

    @property
    def cell_entered(self):
        return self._cell_entered

    def enter_cell(self):
        self._cell_entered = True
        self.current_cell.set_editable()

    def insert_cell(self, idx):
        cell = Cell(idx=idx)
        self.cells.insert(idx, cell)
        for cell in self.cells[idx + 1 :]:  # noqa
            cell.idx = cell.idx + 1
        self.create_layout()
        self.app.layout = self.layout
        self.focus(idx)
        self.nb_json["cells"].insert(idx, self.current_cell.cell_json)

    def bind_keys(self):
        self.key_bindings = default_kb(self)

    def run(self):
        asyncio.run(self.app.run_async())
