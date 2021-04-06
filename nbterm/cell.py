from prompt_toolkit import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

# TODO: take language into account
lexer = PygmentsLexer(PythonLexer)


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
        if "source" in cell_json:
            input_text = "".join(cell_json["source"])
        else:
            input_text = ""
        if "outputs" in cell_json:
            outputs = cell_json["outputs"]
        else:
            outputs = []
        self.cell_json = cell_json
        output_text = ""
        for output in outputs:
            if "text" in output:
                output_text += "".join(output["text"])
            elif "traceback" in output:
                output_text += "".join(output["traceback"])
        self.idx = idx
        self.input_window = None
        self.set_readonly(input_text)
        self.text_changed()
        self.input = Frame(self.input_window)
        self.output = Window(content=FormattedTextControl(text=ANSI(output_text)))
        self.output.height = output_text.count("\n") + 1

    def text_changed(self, _=None):
        line_nb = self.buffer.text.count("\n")
        self.input_window.height = line_nb + 1

    def set_readonly(self, text=None):
        if text is None:
            text = self.buffer.text
        self.buffer = Buffer(read_only=True)
        self.buffer.set_document(Document(text), bypass_readonly=True)
        if self.input_window is None:
            self.input_window = Window(
                content=BufferControl(buffer=self.buffer, lexer=lexer)
            )
        else:
            self.input_window.content = BufferControl(buffer=self.buffer, lexer=lexer)

    def set_editable(self):
        text = self.buffer.text
        self.buffer = Buffer(read_only=False, on_text_changed=self.text_changed)
        self.buffer.text = text
        self.input_window.content = BufferControl(buffer=self.buffer, lexer=lexer)

    def clear_output(self):
        self.output.content = FormattedTextControl(text="")
        self.output.height = 0

    def update_json(self):
        src_list = [line + "\n" for line in self.buffer.text.split("\n")]
        src_list[-1] = src_list[-1][:-1]
        self.cell_json["source"] = src_list
        # TODO: update output
