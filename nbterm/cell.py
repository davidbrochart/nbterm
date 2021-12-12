import copy
import uuid
from typing import Dict, List, Any, Optional, Union, cast

from prompt_toolkit import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.console import Console


ONE_COL: Window = Window(width=1)
ONE_ROW: Window = Window(height=1)
CONSOLE: Optional[Console] = None


def set_console(console: Console):
    global CONSOLE
    CONSOLE = console


def rich_print(
    string: str, console: Optional[Console] = None, style: str = "", end: str = ""
):
    console = console or CONSOLE
    assert console is not None
    with console.capture() as capture:
        console.print(string, style=style, end=end)
    return capture.get()


def get_output_text_and_height(outputs: List[Dict[str, Any]]):
    text_list = []
    height = 0
    for output in outputs:
        if output["output_type"] == "stream":
            text = "".join(output["text"])
            height += text.count("\n")
            if output["name"] == "stderr":
                # TODO: take terminal width into account
                lines = text.splitlines()
                lines = [line + " " * (200 - len(line)) for line in lines]
                text = "\n".join(lines)
                text = rich_print(text, style="white on red", end="\n")
        elif output["output_type"] == "error":
            text = "\n".join(output["traceback"])
            height += text.count("\n")
        elif output["output_type"] == "execute_result":
            text = "\n".join(output["data"].get("text/plain", ""))
            height += text.count("\n")
        else:
            continue
        text_list.append(text)
    text_ansi = ANSI("".join(text_list))
    if text_ansi and not height:
        height = 1
    return text_ansi, height


def empty_cell_json():
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [],
        "outputs": [],
    }


class Cell:

    input: Union[Frame, HSplit]
    output: Window
    json: Dict[str, Any]
    input_prefix: Window
    output_prefix: Window
    input_window: Window
    input_buffer: Buffer

    def __init__(self, notebook, cell_json: Optional[Dict[str, Any]] = None):
        self.notebook = notebook
        self.json = cell_json or empty_cell_json()
        self.input_prefix = Window(width=10)
        self.output_prefix = Window(width=10, height=0)
        input_text = "".join(self.json["source"])
        if self.json["cell_type"] == "code":
            execution_count = self.json["execution_count"] or " "
            text = rich_print(
                f"\nIn [{execution_count}]:",
                style="green",
            )
            self.input_prefix.content = FormattedTextControl(text=ANSI(text))
            outputs = self.json["outputs"]
            for output in outputs:
                if "execution_count" in output:
                    text = rich_print(
                        f"Out[{output['execution_count']}]:",
                        style="red",
                    )
                    self.output_prefix.content = FormattedTextControl(text=ANSI(text))
                    break
        else:
            outputs = []
        output_text, output_height = get_output_text_and_height(outputs)
        self.input_window = Window()
        self.input_buffer = Buffer(on_text_changed=self.input_text_changed)
        self.input_buffer.text = input_text
        self.set_input_readonly()
        if self.json["cell_type"] == "markdown":
            self.input = HSplit(
                [ONE_ROW, VSplit([ONE_COL, self.input_window]), ONE_ROW]
            )
        else:
            self.input = Frame(self.input_window)
        self.output = Window(content=FormattedTextControl(text=output_text))
        self.output.height = output_height

    def get_height(self) -> int:
        input_height = cast(int, self.input_window.height) + 2  # include frame
        output_height = cast(int, self.output.height)
        return input_height + output_height

    def copy(self):
        cell_json = copy.deepcopy(self.json)
        cell = Cell(self.notebook, cell_json=cell_json)
        return cell

    def input_text_changed(self, _=None):
        self.notebook.dirty = True
        self.notebook.quitting = False
        line_nb = self.input_buffer.text.count("\n") + 1
        height_keep = self.input_window.height
        self.input_window.height = line_nb
        if height_keep is not None and line_nb != height_keep:
            # height has changed
            self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)

    def set_as_markdown(self):
        prev_cell_type = self.json["cell_type"]
        if prev_cell_type != "markdown":
            self.notebook.dirty = True
            self.json["cell_type"] = "markdown"
            if "outputs" in self.json:
                del self.json["outputs"]
            if "execution_count" in self.json:
                del self.json["execution_count"]
            self.input_prefix.content = FormattedTextControl(text="")
            self.clear_output()
            self.set_input_readonly()
            if prev_cell_type == "code":
                self.input = HSplit(
                    [ONE_ROW, VSplit([ONE_COL, self.input_window]), ONE_ROW]
                )
                self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)

    def set_as_code(self):
        prev_cell_type = self.json["cell_type"]
        if prev_cell_type != "code":
            self.notebook.dirty = True
            self.json["cell_type"] = "code"
            self.json["outputs"] = []
            self.json["execution_count"] = None
            text = rich_print("\nIn [ ]:", style="green")
            self.input_prefix.content = FormattedTextControl(text=ANSI(text))
            self.set_input_readonly()
            if prev_cell_type == "markdown":
                self.input = Frame(self.input_window)
                self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)

    def set_input_readonly(self):
        if self.json["cell_type"] == "markdown":
            text = self.input_buffer.text or "Type *Markdown*"
            md = Markdown(text)
            text = rich_print(md)[:-1]  # remove trailing "\n"
        elif self.json["cell_type"] == "code":
            code = Syntax(self.input_buffer.text, self.notebook.language)
            text = rich_print(code)[:-1]  # remove trailing "\n"
        line_nb = text.count("\n") + 1
        self.input_window.content = FormattedTextControl(text=ANSI(text))
        height_keep = self.input_window.height
        self.input_window.height = line_nb
        if (
            self.notebook.app is not None
            and height_keep is not None
            and line_nb != height_keep
        ):
            # height has changed
            self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)

    def set_input_editable(self):
        if self.json["cell_type"] == "code":
            self.input_window.content = BufferControl(
                buffer=self.input_buffer, lexer=self.notebook.lexer
            )
        else:
            self.input_window.content = BufferControl(buffer=self.input_buffer)
        self.input_window.height = self.input_buffer.text.count("\n") + 1

    def clear_output(self):
        if self.output.height > 0:
            self.notebook.dirty = True
            self.output.height = 0
            self.output.content = FormattedTextControl(text="")
            self.output_prefix.content = FormattedTextControl(text="")
            self.output_prefix.height = 0
            if self.json["cell_type"] == "code":
                self.json["outputs"] = []
            if self.notebook.app:
                self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)

    def update_json(self):
        src_list = [line + "\n" for line in self.input_buffer.text.splitlines()]
        src_list[-1] = src_list[-1][:-1]
        self.json["source"] = src_list

    async def run(self):
        self.clear_output()
        if self.json["cell_type"] == "code":
            code = self.input_buffer.text.strip()
            if code:
                if self not in self.notebook.executing_cells.values():
                    self.notebook.dirty = True
                    executing_text = rich_print("\nIn [*]:", style="green")
                    self.input_prefix.content = FormattedTextControl(
                        text=ANSI(executing_text)
                    )
                    self.notebook.execution_count += 1
                    execution_count = self.notebook.execution_count
                    msg_id = uuid.uuid4().hex
                    self.notebook.msg_id_2_execution_count[msg_id] = execution_count
                    self.notebook.executing_cells[execution_count] = self
                    await self.notebook.kd.execute(
                        self.input_buffer.text, msg_id=msg_id
                    )
                    del self.notebook.executing_cells[execution_count]
                    text = rich_print(
                        f"\nIn [{execution_count}]:",
                        style="green",
                    )
                    self.input_prefix.content = FormattedTextControl(text=ANSI(text))
                    self.json["execution_count"] = execution_count
                    if self.notebook.app:
                        self.notebook.app.invalidate()
            else:
                self.clear_output()
        else:
            self.clear_output()
