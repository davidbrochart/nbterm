import asyncio
import copy
from typing import Dict, List, Any, Optional, Union

from prompt_toolkit import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer  # type: ignore
from rich.syntax import Syntax
from rich.markdown import Markdown

# TODO: take language into account
lexer: PygmentsLexer = PygmentsLexer(PythonLexer)


ONE_COL: Window = Window(width=1)
ONE_ROW: Window = Window(height=1)


def rich_print(string, console, style="", end="\n"):
    with console.capture() as capture:
        console.print(string, style=style, end=end)
    return capture.get()


def get_output_text_and_height(outputs: List[Dict[str, Any]], console):
    text_list = []
    height = 0
    for output in outputs:
        if output["output_type"] == "stream":
            text = "".join(output["text"])
            height += text.count("\n") or 1
            if output["name"] == "stderr":
                text = rich_print(text, console, style="white on red", end="")
        elif output["output_type"] == "error":
            text = "\n".join(output["traceback"])
            height += text.count("\n") + 1
        elif output["output_type"] == "execute_result":
            text = "\n".join(output["data"].get("text/plain", ""))
            height += text.count("\n") or 1
        text_list.append(text)
    text_ansi = ANSI("".join(text_list))
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
                self.notebook.console,
                style="green",
                end="",
            )
            self.input_prefix.content = FormattedTextControl(text=ANSI(text))
            outputs = self.json["outputs"]
            for output in outputs:
                if "execution_count" in output:
                    text = rich_print(
                        f"Out[{output['execution_count']}]:",
                        self.notebook.console,
                        style="red",
                        end="",
                    )
                    self.output_prefix.content = FormattedTextControl(text=ANSI(text))
                    break
        else:
            outputs = []
        output_text, output_height = get_output_text_and_height(
            outputs, self.notebook.console
        )
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

    def copy(self):
        cell_json = copy.deepcopy(self.json)
        cell = Cell(self.notebook, cell_json=cell_json)
        return cell

    def input_text_changed(self, _=None):
        line_nb = self.input_buffer.text.count("\n")
        self.input_window.height = line_nb + 1

    def set_as_markdown(self):
        prev_cell_type = self.json["cell_type"]
        if prev_cell_type != "markdown":
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
                self.notebook.update_layout(self.notebook.current_cell_idx)

    def set_as_code(self):
        prev_cell_type = self.json["cell_type"]
        if prev_cell_type != "code":
            self.json["cell_type"] = "code"
            self.json["outputs"] = []
            self.json["execution_count"] = None
            text = rich_print("\nIn [ ]:", self.notebook.console, style="green", end="")
            self.input_prefix.content = FormattedTextControl(text=ANSI(text))
            self.set_input_readonly()
            if prev_cell_type == "markdown":
                self.input = Frame(self.input_window)
                self.notebook.update_layout(self.notebook.current_cell_idx)

    def set_input_readonly(self):
        if self.json["cell_type"] == "markdown":
            text = self.input_buffer.text or "Type *Markdown*"
            md = Markdown(text)
            text = rich_print(md, self.notebook.console)
        elif self.json["cell_type"] == "code":
            code = Syntax(self.input_buffer.text, "python")
            text = rich_print(code, self.notebook.console)
        self.input_window.content = FormattedTextControl(text=ANSI(text))
        self.input_window.height = text.count("\n") or 1

    def set_input_editable(self):
        if self.json["cell_type"] == "code":
            self.input_window.content = BufferControl(
                buffer=self.input_buffer, lexer=lexer
            )
        else:
            self.input_window.content = BufferControl(buffer=self.input_buffer)
        self.input_window.height = self.input_buffer.text.count("\n") + 1

    def clear_output(self):
        self.output.content = FormattedTextControl(text="")
        self.output.height = 0
        self.output_prefix.content = FormattedTextControl(text="")
        self.output_prefix.height = 0
        if self.json["cell_type"] == "code":
            self.json["outputs"] = []

    def update_json(self):
        src_list = [line + "\n" for line in self.input_buffer.text.split("\n")]
        src_list[-1] = src_list[-1][:-1]
        self.json["source"] = src_list

    async def run(self):
        if self.notebook.executing_cells[0] is not self:
            self.clear_output()
        if self.json["cell_type"] == "code":
            code = self.input_buffer.text.strip()
            if code:
                executing_text = rich_print(
                    "\nIn [*]:", self.notebook.console, style="green", end=""
                )
                if self.notebook.executing_cells[0] is self:
                    already_executing = True
                else:
                    already_executing = False
                    self.input_prefix.content = FormattedTextControl(
                        text=ANSI(executing_text)
                    )
                if self.notebook.idle is None:
                    self.notebook.idle = asyncio.Event()
                else:
                    while True:
                        await self.notebook.idle.wait()
                        if self.notebook.executing_cells[0] is self:
                            break
                    self.notebook.idle.clear()
                if already_executing:
                    self.input_prefix.content = FormattedTextControl(
                        text=ANSI(executing_text)
                    )
                    self.clear_output()
                await self.notebook.kd.execute(self.input_buffer.text)
                text = rich_print(
                    f"\nIn [{self.notebook.execution_count}]:",
                    self.notebook.console,
                    style="green",
                    end="",
                )
                self.input_prefix.content = FormattedTextControl(text=ANSI(text))
                self.json["execution_count"] = self.notebook.execution_count
                self.notebook.execution_count += 1
                if self.notebook.app:
                    self.notebook.app.invalidate()
                self.notebook.executing_cells.remove(self)
                self.notebook.idle.set()
            else:
                self.clear_output()
        else:
            self.clear_output()
            self.notebook.executing_cells.remove(self)
