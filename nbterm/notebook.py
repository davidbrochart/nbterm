import itertools
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

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
from .types import PathLike


class Notebook(Help, Format, KeyBindings):
    app: Optional[Application]
    layout: Layout
    copied_cell: Optional[Cell]
    console: Console
    _run_notebook_nb_path: str
    cells: List[Cell]
    executing_cells: List[Cell]
    json: Dict[str, Any]
    kd: Optional[KernelDriver]
    execution_count: int
    current_cell_idx: int
    idle: Optional[asyncio.Event]
    lexer: Optional[PygmentsLexer] = PygmentsLexer(PythonLexer)
    language: str
    kernel_name: str
    no_kernel: bool
    save_path: Optional[Path]
    dirty: bool
    quitting: bool
    kernel_busy: bool
    kernel_cwd: str

    def __init__(
        self,
        nb_path: Optional[PathLike] = None,
        no_kernel: bool = False,
        save_path: Optional[PathLike] = None,
    ):
        if nb_path:
            if os.path.isdir(nb_path):
                self.kernel_cwd = os.path.abspath(nb_path)
                self.nb_path = ""
            else:
                self.kernel_cwd = os.path.abspath(os.path.dirname(nb_path))
                assert os.path.isdir(self.kernel_cwd)
                self.nb_path = os.path.relpath(
                    os.path.abspath(nb_path), self.kernel_cwd
                )
            os.chdir(self.kernel_cwd)
        else:
            self.kernel_cwd = os.getcwd()
            self.nb_path = ""
        self.app = None
        self.copied_cell = None
        self.console = Console()
        set_console(self.console)
        self.nb_path = Path(nb_path) if nb_path else None
        self.save_path = Path(save_path) if save_path else None
        self.no_kernel = no_kernel
        self.executing_cells = []
        if self.nb_path and self.nb_path.exists():
            self.read_nb()
        else:
            self.create_nb()
        self.dirty = False
        self.quitting = False
        self.kernel_busy = False
        self.execution_count = 1
        self.current_cell_idx = 0
        self.idle = None
        self.edit_mode = False
        self.help_mode = False

    def set_language(self):
        self.kernel_name = self.json["metadata"]["kernelspec"]["name"]
        if self.kernel_name.startswith("python"):
            self.lexer = PygmentsLexer(PythonLexer)
            self.language = "python"
        elif self.kernel_name.startswith("xcpp"):
            self.lexer = PygmentsLexer(CppLexer)
            self.language = "cpp"
        else:
            self.lexer = None
            self.language = ""
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
        self.executing_cells = [self.current_cell]
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

    def update_layout(self, idx: Optional[int] = None):
        if self.app:
            self.create_layout()
            self.app.layout = self.layout
        if idx is None:
            idx = self.current_cell_idx
        self.focus(idx)

    def create_layout(self):
        inout_cells = list(
            itertools.chain.from_iterable(
                [
                    (
                        VSplit([cell.input_prefix, cell.input]),
                        VSplit([cell.output_prefix, ONE_COL, cell.output, ONE_COL]),
                    )
                    for cell in self.cells
                ]
            )
        )
        nb_window = ScrollablePane(HSplit(inout_cells))

        def get_top_bar_text():
            text = ""
            if self.dirty:
                text += "+ "
            text += os.path.basename(self.nb_path)
            if self.dirty and self.quitting:
                text += (
                    " (no write since last change, please exit again to confirm, "
                    "or save your changes)"
                )
            return text

        def get_bottom_bar_text():
            text = ""
            if self.kd and not self.no_kernel and self.kernel_name:
                kernel_status = ["idle", "busy"][self.kernel_busy]
                text += f"{self.kernel_name} ({kernel_status}) at "
            else:
                text += "[NO KERNEL] "
            text += self.kernel_cwd
            return text

        self.top_bar = FormattedTextToolbar(
            get_top_bar_text, style="#ffffff bg:#444444"
        )
        self.bottom_bar = FormattedTextToolbar(
            get_bottom_bar_text, style="#ffffff bg:#444444"
        )
        root_container = HSplit([self.top_bar, nb_window, self.bottom_bar])
        self.layout = Layout(root_container)

    def focus(self, idx: int):
        if 0 <= idx < len(self.cells):
            if self.app:
                self.app.layout.focus(self.cells[idx].input_window)
            self.current_cell_idx = idx

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
            self.update_layout(idx - 1)

    def move_down(self):
        idx = self.current_cell_idx
        if idx < len(self.cells) - 1:
            self.dirty = True
            self.cells[idx], self.cells[idx + 1] = self.cells[idx + 1], self.cells[idx]
            self.update_layout(idx + 1)

    def clear_output(self):
        self.current_cell.clear_output()

    def markdown_cell(self):
        self.current_cell.set_as_markdown()

    def code_cell(self):
        self.current_cell.set_as_code()

    async def queue_run_cell(self, and_select_below: bool = False):
        if self.kd:
            self.executing_cells.append(self.current_cell)
            if and_select_below:
                if self.current_cell_idx == len(self.cells) - 1:
                    self.insert_cell(self.current_cell_idx + 1)
                self.focus(self.current_cell_idx + 1)
            await self.executing_cells[-1].run()

    def cut_cell(self, idx: Optional[int] = None):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx
        self.copied_cell = self.cells.pop(idx)
        if not self.cells:
            self.cells = [Cell(self)]
        elif idx == len(self.cells):
            idx -= 1
        self.update_layout(idx)

    def copy_cell(self, idx: Optional[int] = None):
        if idx is None:
            idx = self.current_cell_idx
        idx = self.current_cell_idx
        self.copied_cell = self.cells[idx]

    def paste_cell(self, idx: Optional[int] = None, below=False):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx + below
        if self.copied_cell is not None:
            pasted_cell = self.copied_cell.copy()
            self.cells.insert(idx, pasted_cell)
            self.update_layout(idx)

    def insert_cell(self, idx: Optional[int] = None, below=False):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx + below
        self.cells.insert(idx, Cell(self))
        self.update_layout(idx)

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
            text = rich_print(f"Out[{self.execution_count}]:", style="red", end="")
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
        text, height = get_output_text_and_height(outputs)
        self.executing_cells[0].output.content = FormattedTextControl(text=text)
        self.executing_cells[0].output.height = height
        if self.app:
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
        self.focus(self.current_cell_idx - 1)

    def go_down(self):
        self.focus(self.current_cell_idx + 1)
