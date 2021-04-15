import os
import itertools
import asyncio
from typing import List, Dict, Any

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit import Application
import kernel_driver  # type: ignore

from .cell import Cell, EMPTY_PREFIX, get_output_text_and_height  # type: ignore
from .format import Format  # type: ignore
from .key_bindings import DefaultKeyBindings  # type: ignore


class Notebook(Format, DefaultKeyBindings):
    def __init__(self, nb_path: str):
        self.nb_path = nb_path
        self.cells: List[Cell] = []
        self.executing_cells: List[Cell] = []
        self.nb_json: Dict[str, Any] = {}
        self.key_bindings = KeyBindings()
        self.bind_keys()
        if os.path.exists(nb_path):
            self.read_nb()
        else:
            self.create_nb()
        self.create_layout()
        self._current_cell = self.cells[0]
        self._cell_entered = False
        self.app: Application = Application(
            layout=self.layout, key_bindings=self.key_bindings, full_screen=True
        )
        kernel_name = self.nb_json["metadata"]["kernelspec"]["name"]
        try:
            self.kd = kernel_driver.KernelDriver(kernel_name=kernel_name, log=False)
            kernel_driver.driver._output_hook_default = self.output_hook
        except RuntimeError:
            self.kd = None
        self.focus(0)
        self.execution_count = 1
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

    def focus(self, idx: int):
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

    def insert_cell(self, idx: int):
        cell = Cell(self, idx=idx)
        self.cells.insert(idx, cell)
        for cell in self.cells[idx + 1 :]:  # noqa
            cell.idx = cell.idx + 1
        self.create_layout()
        self.app.layout = self.layout
        self.focus(idx)
        self.nb_json["cells"].insert(idx, self.current_cell.json)

    def output_hook(self, msg: Dict[str, Any]):
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]
        outputs = self.executing_cells[0].json["outputs"]
        if msg_type == "stream":
            if (not outputs) or (outputs[-1]["name"] != content["name"]):
                outputs.append(
                    {"name": content["name"], "output_type": msg_type, "text": []}
                )
            outputs[-1]["text"].append(content["text"])
        elif msg_type in ("display_data", "execute_result"):
            outputs.append(
                {
                    "data": {"text/plain": [content["data"].get("text/plain", "")]},
                    "execution_count": self.execution_count,
                    "metadata": {},
                    "output_type": msg_type,
                }
            )
        elif msg_type == "error":
            outputs.append(
                {
                    "ename": content["ename"],
                    "evalue": content["evalue"],
                    "output_type": "error",
                    "traceback": content["traceback"],
                }
            )
        else:
            return
        text, height = get_output_text_and_height(outputs)
        self.executing_cells[0].output.content = FormattedTextControl(text=text)
        self.executing_cells[0].output.height = height
        self.app.invalidate()

    async def main(self):
        if self.kd:
            asyncio.create_task(self.kd.start())
        await self.app.run_async()
