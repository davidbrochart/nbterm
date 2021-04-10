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


class Cell:
    def __init__(self, idx=0, cell_json=None):
        # TODO: create cell of type other than code
        if cell_json is None:
            cell_json = {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "source": [],
                "outputs": [],
            }
        if cell_json["cell_type"] == "markdown":
            input_text = "".join(cell_json["source"])
        elif cell_json["cell_type"] == "code":
            input_text = "".join(cell_json["source"])
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
        self.input_window.content = BufferControl(buffer=self.input_buffer, lexer=lexer)
        self.input_window.height = self.input_buffer.text.count("\n") + 1

    def clear_output(self):
        self.output.content = FormattedTextControl(text="")
        self.output.height = 0

    def update_json(self):
        src_list = [line + "\n" for line in self.input_buffer.text.split("\n")]
        src_list[-1] = src_list[-1][:-1]
        self.json["source"] = src_list
        # TODO: update output

    async def run(self, kd):
        await kd.execute(self.input_buffer.text)
