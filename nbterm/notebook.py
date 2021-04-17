import os
import itertools
import asyncio
from typing import List, Dict, Any, Optional, cast

from prompt_toolkit import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit import Application
from rich.console import Console
import kernel_driver  # type: ignore

from .cell import Cell, ONE_COL, rich_print, get_output_text_and_height  # type: ignore
from .format import Format  # type: ignore
from .key_bindings import DefaultKeyBindings  # type: ignore


class Notebook(Format, DefaultKeyBindings):

    app: Optional[Application]

    def __init__(self, nb_path: str):
        self.console = Console()
        self.nb_path = nb_path
        self.cells: List[Cell] = []
        self.executing_cells: List[Cell] = []
        self.nb_json: Dict[str, Any] = {}
        if os.path.exists(nb_path):
            self.read_nb()
        else:
            self.create_nb()
        kernel_name = self.nb_json["metadata"]["kernelspec"]["name"]
        try:
            self.kd = kernel_driver.KernelDriver(kernel_name=kernel_name, log=False)
            kernel_driver.driver._output_hook_default = self.output_hook
        except RuntimeError:
            self.kd = None
        self.execution_count = 1
        self.idle = None
        self.current_cell = self.cells[0]

    def run(self):
        self.app = None
        asyncio.run(self._run())

    def show(self):
        self.key_bindings = KeyBindings()
        self.bind_keys()
        self.create_layout()
        self.cell_entered = False
        self.app: Application = Application(
            layout=self.layout, key_bindings=self.key_bindings, full_screen=True
        )
        self.focus(0)
        asyncio.run(self._show())

    def create_layout(self):
        inout_cells = list(
            itertools.chain.from_iterable(
                [
                    (
                        VSplit([cell.input_prefix, cell.input]),
                        VSplit([cell.output_prefix, ONE_COL, cell.output]),
                    )
                    for cell in self.cells
                ]
            )
        )
        root_container = ScrollablePane(HSplit(inout_cells))
        self.layout = Layout(root_container)

    def focus(self, idx: int):
        if 0 <= idx < len(self.cells):
            if self.app:
                self.app.layout.focus(self.cells[idx].input_window)
            self.current_cell = self.cells[idx]

    def exit_cell(self):
        self.cell_entered = False
        self.current_cell.set_input_readonly()

    def enter_cell(self):
        self.cell_entered = True
        self.current_cell.set_input_editable()

    def delete_cell(self, idx: int):
        del self.cells[idx]
        del self.nb_json["cells"][idx]
        if not self.cells:
            self.cells = [Cell(self, idx=0)]
            self.nb_json["cells"] = [self.current_cell.json]
        elif idx == len(self.cells):
            idx -= 1
        else:
            for cell in self.cells[idx:]:
                cell.idx = cell.idx - 1
        self.create_layout()
        self.app = cast(Application, self.app)
        self.app.layout = self.layout
        self.focus(idx)

    def insert_cell(self, idx: int):
        cell = Cell(self, idx=idx)
        self.cells.insert(idx, cell)
        for cell in self.cells[idx + 1 :]:  # noqa
            cell.idx = cell.idx + 1
        self.create_layout()
        self.app = cast(Application, self.app)
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
            text = rich_print(
                f"Out[{self.execution_count}]:", self.console, style="red", end=""
            )
            self.executing_cells[0].output_prefix.content = FormattedTextControl(
                text=ANSI(text)
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
        text, height = get_output_text_and_height(outputs, self.console)
        self.executing_cells[0].output.content = FormattedTextControl(text=text)
        self.executing_cells[0].output.height = height
        if self.app:
            self.app.invalidate()

    @property
    def run_notebook_path(self):
        return self._run_notebook_path

    async def _run(self):
        await self.kd.start()
        while True:
            self.executing_cells = [self.current_cell]
            await self.current_cell.run()
            if self.current_cell.idx == len(self.cells) - 1:
                break
            self.focus(self.current_cell.idx + 1)
        i = self.nb_path.rfind(".")
        self._run_notebook_path = self.nb_path[:i] + "_run" + self.nb_path[i:]
        self.save_nb(self._run_notebook_path)

    async def _show(self):
        if self.kd:
            asyncio.create_task(self.kd.start())
        await self.app.run_async()
