import os
import json
import asyncio
import itertools

import click
from prompt_toolkit import Application, ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.widgets import Frame
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

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


class Notebook:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            self.read_nb()
        else:
            self.cells = [Cell()]
        self.create_layout()
        self._current_cell = self.cells[0]
        self._cell_entered = False
        self.bind_keys()
        self.app = Application(
            layout=self.layout, key_bindings=self.key_bindings, full_screen=True
        )
        self.run()

    def read_nb(self):
        with open(self.path) as f:
            self.nb_json = json.load(f)
        self.cells = [
            Cell(idx=idx, cell_json=self.nb_json["cells"][idx])
            for idx, cell in enumerate(self.nb_json["cells"])
        ]

    def save_nb(self):
        with open(self.path, "wt") as f:
            json.dump(self.nb_json, f)

    def create_layout(self):
        inout_cells = list(
            itertools.chain.from_iterable(
                [(cell.input, cell.output) for cell in self.cells]
            )
        )
        root_container = ScrollablePane(HSplit(inout_cells))
        self.layout = Layout(root_container)

    def focus(self, idx):
        self.app.layout.focus(self.cells[idx].input_window)
        self._current_cell = self.cells[idx]

    def exit_cell(self):
        self._cell_entered = False
        self.current_cell.set_readonly()

    @property
    def current_cell(self):
        return self._current_cell

    @property
    def cell_entered(self):
        return self._cell_entered

    def enter_cell(self):
        self._cell_entered = True
        self.current_cell.set_editable()

    def insert_cell(self, idx):
        cell = Cell(idx=idx)
        self.cells.insert(idx, cell)
        for cell in self.cells[idx + 1 :]:  # noqa
            cell.idx = cell.idx + 1
        self.create_layout()
        self.app.layout = self.layout
        self.focus(idx)
        self.nb_json["cells"].insert(idx, self.current_cell.cell_json)

    def bind_keys(self):
        kb = KeyBindings()

        @Condition
        def in_cell():
            return self.cell_entered

        @Condition
        def not_in_cell():
            return not self.cell_entered

        @kb.add("c-q", filter=not_in_cell)
        def _(event):
            self.app.exit()

        @kb.add("c-s", filter=not_in_cell)
        def _(event):
            self.save_nb()

        @kb.add("escape", filter=in_cell)
        def _(event):
            self.current_cell.update_json()
            self.exit_cell()

        @kb.add("up", filter=not_in_cell)
        def _(event):
            cell_idx = self.current_cell.idx
            if cell_idx > 0:
                self.focus(cell_idx - 1)

        @kb.add("down", filter=not_in_cell)
        def _(event):
            cell_idx = self.current_cell.idx
            if cell_idx < len(self.cells) - 1:
                self.focus(cell_idx + 1)

        @kb.add("enter", filter=not_in_cell)
        def _(event):
            self.enter_cell()

        @kb.add("c-l", filter=not_in_cell)
        def _(event):
            self.current_cell.clear_output()

        @kb.add("c-e", filter=not_in_cell)
        def _(event):
            self.current_cell.run()

        @kb.add("c-r", filter=not_in_cell)
        def _(event):
            self.current_cell.run()
            cell_idx = self.current_cell.idx
            if cell_idx < len(self.cells) - 1:
                self.focus(cell_idx + 1)

        @kb.add("c-i", filter=not_in_cell)
        def _(event):
            cell_idx = self.current_cell.idx
            self.insert_cell(cell_idx)

        @kb.add("c-j", filter=not_in_cell)
        def _(event):
            cell_idx = self.current_cell.idx + 1
            self.insert_cell(cell_idx)

        self.key_bindings = kb

    def run(self):
        asyncio.run(self.app.run_async())


@click.command()
@click.argument("nb-path", default="")
def cli(nb_path):
    Notebook(nb_path)


if __name__ == "__main__":
    cli()
