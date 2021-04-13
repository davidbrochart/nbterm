import os
import itertools
import asyncio

from prompt_toolkit import ANSI
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit import Application
import kernel_driver

from .cell import Cell, EMPTY_PREFIX
from .format import read_nb, create_nb
from .key_bindings import default_kb


class Notebook:
    def __init__(self, nb_path):
        self.nb_path = nb_path
        if os.path.exists(nb_path):
            read_nb(self)
        else:
            create_nb(self)
        self.create_layout()
        self._current_cell = self.cells[0]
        self.executing_cells = []
        self._cell_entered = False
        self.bind_keys()
        self.app = Application(
            layout=self.layout, key_bindings=self.key_bindings, full_screen=True
        )
        kernel_name = self.nb_json["metadata"]["kernelspec"]["name"]
        try:
            self.kd = kernel_driver.KernelDriver(kernel_name=kernel_name, log=False)
            kernel_driver.driver._output_hook_default = self._output_hook
        except RuntimeError:
            self.kd = None
        self.focus(0)
        self.execution_count = 0
        self.idle = None
        asyncio.run(self.main())

    def create_layout(self):
        inout_cells = list(
            itertools.chain.from_iterable(
                [
                    (
                        VSplit([cell.input_prefix, cell.input]),
                        VSplit([EMPTY_PREFIX, cell.output]),
                    )
                    for cell in self.cells
                ]
            )
        )
        root_container = ScrollablePane(HSplit(inout_cells))
        self.layout = Layout(root_container)

    def focus(self, idx):
        if 0 <= idx < len(self.cells):
            self.app.layout.focus(self.cells[idx].input_window)
            self._current_cell = self.cells[idx]

    def exit_cell(self):
        self._cell_entered = False
        self.current_cell.set_input_readonly()

    @property
    def current_cell(self):
        return self._current_cell

    @property
    def cell_entered(self):
        return self._cell_entered

    def enter_cell(self):
        self._cell_entered = True
        self.current_cell.set_input_editable()

    def insert_cell(self, idx):
        cell = Cell(idx=idx)
        self.cells.insert(idx, cell)
        for cell in self.cells[idx + 1 :]:  # noqa
            cell.idx = cell.idx + 1
        self.create_layout()
        self.app.layout = self.layout
        self.focus(idx)
        self.nb_json["cells"].insert(idx, self.current_cell.json)

    def bind_keys(self):
        self.key_bindings = default_kb(self)

    def _output_hook(self, msg):
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]
        if msg_type == "stream":
            text = self.executing_cells[0].output.content.text
            text += content["text"]
            height = text.count("\n") + 1
        elif msg_type in ("display_data", "execute_result"):
            text = content["data"].get("text/plain", "")
            height = text.count("\n") + 1
        elif msg_type == "error":
            text = "\n".join(content["traceback"])
            height = text.count("\n") + 1
            text = ANSI(text)
        else:
            return
        self.executing_cells[0].output.content = FormattedTextControl(text=text)
        self.executing_cells[0].output.height = height
        self.app.invalidate()

    async def main(self):
        if self.kd:
            asyncio.create_task(self.kd.start())
        await self.app.run_async()
