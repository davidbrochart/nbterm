import os
from pathlib import Path
import itertools
import asyncio
from typing import List, Dict, Tuple, Any, Optional, cast

from prompt_toolkit import ANSI
from prompt_toolkit.key_binding import KeyBindings as PtKeyBindings
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.widgets.toolbars import FormattedTextToolbar
from pygments.lexers.python import PythonLexer  # type: ignore
from pygments.lexers.c_cpp import CppLexer  # type: ignore
from prompt_toolkit import Application
from rich.console import Console
import kernel_driver  # type: ignore
from kernel_driver import KernelDriver

from .cell import (
    Cell,
    ONE_COL,
    set_console,
    rich_print,
    get_output_text_and_height,
)
from .help import Help
from .format import Format
from .key_bindings import KeyBindings


class Notebook(Help, Format, KeyBindings):

    app: Optional[Application]
    layout: Layout
    copied_cell: Optional[Cell]
    console: Console
    _run_notebook_nb_path: str
    cells: List[Cell]
    executing_cells: Dict[int, Cell]
    json: Dict[str, Any]
    kd: Optional[KernelDriver]
    execution_count: int
    msg_id_2_execution_count: Dict[str, int]
    current_cell_idx: int
    top_cell_idx: int
    bottom_cell_idx: int
    lexer: Optional[PygmentsLexer] = PygmentsLexer(PythonLexer)
    language: str
    kernel_name: str
    no_kernel: bool
    dirty: bool
    quitting: bool
    kernel_cwd: Path

    def __init__(
        self,
        nb_path: Path,
        kernel_cwd: Path = Path("."),
        no_kernel: bool = False,
        save_path: Optional[Path] = None,
    ):
        self.nb_path = nb_path.resolve()
        self.kernel_cwd = kernel_cwd.resolve()
        os.chdir(self.kernel_cwd)
        self.app = None
        self.copied_cell = None
        self.console = Console()
        set_console(self.console)
        self.save_path = save_path
        self.no_kernel = no_kernel
        self.executing_cells = {}
        self.top_cell_idx = 0
        self.bottom_cell_idx = -1
        self.current_cell_idx = 0
        if self.nb_path.is_file():
            self.read_nb()
        else:
            self.create_nb()
        self.dirty = False
        self.quitting = False
        self.execution_count = 0
        self.msg_id_2_execution_count = {}
        self.edit_mode = False
        self.help_mode = False

    def set_language(self):
        self.kernel_name = self.json["metadata"]["kernelspec"]["name"]
        self.language = self.json["metadata"]["kernelspec"]["language"]
        if self.language == "python":
            self.lexer = PygmentsLexer(PythonLexer)
        elif self.language == "cpp":
            self.lexer = PygmentsLexer(CppLexer)
        else:
            self.lexer = None
        if self.no_kernel:
            self.kd = None
        else:
            try:
                self.kd = KernelDriver(kernel_name=self.kernel_name, log=False)
                kernel_driver.driver._output_hook_default = self.output_hook
            except RuntimeError:
                self.kd = None

    @property
    def current_cell(self):
        return self.cells[self.current_cell_idx]

    async def run_cell(self, idx: Optional[int] = None):
        if idx is None:
            idx = self.current_cell_idx
        self.focus(idx)
        await self.current_cell.run()

    async def run_all(self):
        await self.kd.start()
        for i in range(len(self.cells)):
            await self.run_cell(i)

    def show(self):
        self.key_bindings = PtKeyBindings()
        self.bind_keys()
        self.create_layout()
        self.app = Application(
            layout=self.layout, key_bindings=self.key_bindings, full_screen=True
        )
        self.focus(0)
        asyncio.run(self._show())

    def update_layout(self):
        if self.app:
            self.create_layout()
            self.app.layout = self.layout

    def create_layout(self):
        inout_cells = list(
            itertools.chain.from_iterable(
                [
                    (
                        VSplit([cell.input_prefix, cell.input]),
                        VSplit([cell.output_prefix, ONE_COL, cell.output, ONE_COL]),
                    )
                    for cell in self.cells[
                        self.top_cell_idx : self.bottom_cell_idx + 1  # noqa
                    ]
                ]
            )
        )
        nb_window = ScrollablePane(HSplit(inout_cells), show_scrollbar=False)

        def get_top_bar_text():
            text = ""
            if self.dirty:
                text += "+ "
            text += str(self.nb_path.relative_to(self.kernel_cwd))
            if self.dirty and self.quitting:
                text += (
                    " (no write since last change, please exit again to confirm, "
                    "or save your changes)"
                )
            return text

        def get_bottom_bar_text():
            text = ""
            if self.kd and not self.no_kernel and self.kernel_name:
                if self.executing_cells:
                    kernel_status = "busy"
                else:
                    kernel_status = "idle"
                text += f"{self.kernel_name} ({kernel_status})"
            else:
                text += "[NO KERNEL]"
            text += (
                f" @ {self.kernel_cwd} - {self.current_cell_idx + 1}/{len(self.cells)}"
            )
            return text

        self.top_bar = FormattedTextToolbar(
            get_top_bar_text, style="#ffffff bg:#444444"
        )
        self.bottom_bar = FormattedTextToolbar(
            get_bottom_bar_text, style="#ffffff bg:#444444"
        )
        root_container = HSplit([self.top_bar, nb_window, self.bottom_bar])
        self.layout = Layout(root_container)

    def focus(self, idx: int, update_layout: bool = False, no_change: bool = False):
        """
        Focus on a cell.

        Parameters
        ----------
        idx : int
            Index of the cell to focus on.
        update_layout : bool, optional
            If True, force the update of the layout. Default is False.
        no_change : bool optional
            If True, the cells didn't change. Default is False.
        """
        if 0 <= idx < len(self.cells):
            if self.app:
                if self.update_visible_cells(idx, no_change) or update_layout:
                    self.update_layout()
                self.app.layout.focus(self.cells[idx].input_window)
            self.current_cell_idx = idx

    def update_visible_cells(self, idx: int, no_change: bool) -> bool:
        self.app = cast(Application, self.app)
        size = self.app.renderer.output.get_size()
        available_height = size.rows - 2  # status bars
        if idx < self.top_cell_idx or self.bottom_cell_idx == -1:
            # scroll up
            (
                self.top_cell_idx,
                self.bottom_cell_idx,
            ) = self.get_visible_cell_idx_from_top(idx, available_height)
            return True
        if idx > self.bottom_cell_idx:
            # scroll down
            (
                self.top_cell_idx,
                self.bottom_cell_idx,
            ) = self.get_visible_cell_idx_from_bottom(idx, available_height)
            return True
        if no_change:
            return False
        # there might be less or more cells, or the cells' content may have changed
        top_cell_idx_keep, bottom_cell_idx_keep = (
            self.top_cell_idx,
            self.bottom_cell_idx,
        )
        while True:
            (
                self.top_cell_idx,
                self.bottom_cell_idx,
            ) = self.get_visible_cell_idx_from_top(self.top_cell_idx, available_height)
            if self.top_cell_idx <= idx <= self.bottom_cell_idx:
                break
            self.top_cell_idx += 1
        return not (
            self.top_cell_idx == top_cell_idx_keep
            and self.bottom_cell_idx == bottom_cell_idx_keep
        )

    def get_visible_cell_idx_from_top(
        self, idx: int, available_height: int
    ) -> Tuple[int, int]:
        cell_nb = -1
        for cell in self.cells[idx:]:
            available_height -= cell.get_height()
            cell_nb += 1
            if available_height <= 0:
                break
        # bottom cell may be clipped by ScrollablePane
        return idx, idx + cell_nb

    def get_visible_cell_idx_from_bottom(
        self, idx: int, available_height: int
    ) -> Tuple[int, int]:
        cell_nb = -1
        for cell in self.cells[idx::-1]:
            available_height -= cell.get_height()
            cell_nb += 1
            if available_height <= 0:
                break
        # top cell may be clipped by ScrollablePane
        return idx - cell_nb, idx

    def exit_cell(self):
        self.edit_mode = False
        self.current_cell.update_json()
        self.current_cell.set_input_readonly()

    def enter_cell(self):
        self.edit_mode = True
        self.current_cell.set_input_editable()

    def move_up(self):
        idx = self.current_cell_idx
        if idx > 0:
            self.dirty = True
            self.cells[idx - 1], self.cells[idx] = self.cells[idx], self.cells[idx - 1]
            self.focus(idx - 1, update_layout=True)

    def move_down(self):
        idx = self.current_cell_idx
        if idx < len(self.cells) - 1:
            self.dirty = True
            self.cells[idx], self.cells[idx + 1] = self.cells[idx + 1], self.cells[idx]
            self.focus(idx + 1, update_layout=True)

    def clear_output(self):
        self.current_cell.clear_output()

    def markdown_cell(self):
        self.current_cell.set_as_markdown()

    def code_cell(self):
        self.current_cell.set_as_code()

    def raw_cell(self):
        self.current_cell.set_as_raw()

    async def queue_run_cell(self, and_select_below: bool = False):
        if self.kd:
            cell = self.current_cell
            if and_select_below:
                if self.current_cell_idx == len(self.cells) - 1:
                    self.insert_cell(self.current_cell_idx + 1)
                self.focus(self.current_cell_idx + 1)
            await cell.run()

    def cut_cell(self, idx: Optional[int] = None):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx
        self.copied_cell = self.cells.pop(idx)
        if not self.cells:
            self.cells = [Cell(self)]
        elif idx == len(self.cells):
            idx -= 1
        self.focus(idx, update_layout=True)

    def copy_cell(self, idx: Optional[int] = None):
        if idx is None:
            idx = self.current_cell_idx
        idx = self.current_cell_idx
        self.copied_cell = self.cells[idx]

    def paste_cell(self, idx: Optional[int] = None, below=False):
        if self.copied_cell is not None:
            self.dirty = True
            if idx is None:
                idx = self.current_cell_idx + below
            pasted_cell = self.copied_cell.copy()
            self.cells.insert(idx, pasted_cell)
            self.focus(idx, update_layout=True)

    def insert_cell(self, idx: Optional[int] = None, below=False):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx + below
        self.cells.insert(idx, Cell(self))
        self.focus(idx, update_layout=True)

    def output_hook(self, msg: Dict[str, Any]):
        msg_id = msg["parent_header"]["msg_id"]
        execution_count = self.msg_id_2_execution_count[msg_id]
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]
        outputs = self.executing_cells[execution_count].json["outputs"]
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
                    "execution_count": execution_count,
                    "metadata": {},
                    "output_type": msg_type,
                }
            )
            text = rich_print(f"Out[{execution_count}]:", style="red", end="")
            self.executing_cells[
                execution_count
            ].output_prefix.content = FormattedTextControl(text=ANSI(text))
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
        self.executing_cells[execution_count].output.content = FormattedTextControl(
            text=text
        )
        height_keep = self.executing_cells[execution_count].output.height
        self.executing_cells[execution_count].output.height = height
        if self.app and height_keep != height:
            # height has changed
            self.focus(self.current_cell_idx, update_layout=True)
            self.app.invalidate()

    async def _show(self):
        if self.kd:
            asyncio.create_task(self.kd.start())
        await self.app.run_async()

    async def exit(self):
        if self.dirty and not self.quitting:
            self.quitting = True
            return
        if self.kd:
            await self.kd.stop()
        self.app.exit()

    def go_up(self):
        self.focus(self.current_cell_idx - 1, no_change=True)

    def go_down(self):
        self.focus(self.current_cell_idx + 1, no_change=True)
