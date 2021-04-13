import asyncio

from prompt_toolkit import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer
from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown

# TODO: take language into account
lexer = PygmentsLexer(PythonLexer)

console = Console()


EMPTY_PREFIX = Window(width=10)


class Cell:
    def __init__(self, idx=0, cell_json=None):
        # TODO: create cell of type other than code
        if cell_json is None:
            cell_json = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [],
                "outputs": [],
            }
        self.input_prefix = Window(width=10)
        input_text = "".join(cell_json["source"])
        if cell_json["cell_type"] == "code":
            execution_count = cell_json["execution_count"] or " "
            self.input_prefix.content = FormattedTextControl(
                text=f"\nIn [{execution_count}]:"
            )
        if "outputs" in cell_json:
            outputs = cell_json["outputs"]
        else:
            outputs = []
        self.json = cell_json
        output_text = ""
        for output in outputs:
            if "text" in output:
                output_text += "".join(output["text"])
            elif "traceback" in output:
                output_text += "".join(output["traceback"])
        self.idx = idx
        self.input_window = Window()
        self.input_buffer = Buffer(on_text_changed=self.input_text_changed)
        self.input_buffer.text = input_text
        self.set_input_readonly()
        self.input = Frame(self.input_window)
        self.output = Window(content=FormattedTextControl(text=ANSI(output_text)))
        self.output.height = output_text.count("\n") + 1

    def input_text_changed(self, _=None):
        line_nb = self.input_buffer.text.count("\n")
        self.input_window.height = line_nb + 1

    def set_as_markdown(self):
        self.json["cell_type"] = "markdown"
        self.set_input_readonly()

    def set_as_code(self):
        self.json["cell_type"] = "code"
        self.set_input_readonly()

    def set_input_readonly(self):
        if self.json["cell_type"] == "markdown":
            md = Markdown(self.input_buffer.text)
            with console.capture() as capture:
                console.print(md)
            text = capture.get()
        elif self.json["cell_type"] == "code":
            code = Syntax(self.input_buffer.text, "python")
            with console.capture() as capture:
                console.print(code)
            text = capture.get()
        self.input_window.content = FormattedTextControl(text=ANSI(text))
        self.input_window.height = text.count("\n")

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
        self.output.height = 1

    def update_json(self):
        src_list = [line + "\n" for line in self.input_buffer.text.split("\n")]
        src_list[-1] = src_list[-1][:-1]
        self.json["source"] = src_list
        # TODO: update output

    async def run(self, nb):
        code = self.input_buffer.text.strip()
        if code:
            self.input_prefix.content = FormattedTextControl(text="\nIn [*]:")
        if nb.idle is None:
            nb.idle = asyncio.Event()
        else:
            await nb.idle.wait()
        nb.idle.clear()
        if code:
            await nb.kd.execute(self.input_buffer.text)
            nb.execution_count += 1
            self.input_prefix.content = FormattedTextControl(
                text=f"\nIn [{nb.execution_count}]:"
            )
            self.json["execution_count"] = nb.execution_count
            nb.app.invalidate()
        nb.executing_cells.pop(0)
        nb.idle.set()
