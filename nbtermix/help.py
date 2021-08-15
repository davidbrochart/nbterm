from rich.markdown import Markdown
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit import ANSI

from .cell import rich_print

md = Markdown(
    "## nbtermix help\n"
    "There are two modes: edit mode, and command mode.\n"
    "\n"
    "- `e`: enter the edit mode, allowing to type into the cell.\n"
    "- `esc`: exit the edit mode and enter the command mode.\n"
    "\n"
    "In edit mode:\n"
    "- `ctrl-e`: run cell.\n"
    "- `ctrl-r`: run cell and select below in edit mode.\n"
    "- `ctrl-t`: open cell result in external editor.\n"
    "- `ctrl-w`: open cell in external editor.\n"
    "- `ctrl-f`: save tmp file from cell and execute it.\n"
    "- `ctrl-s`: save.\n"
    "\n"
    "In command mode:\n"
    "\n"
    "- `up` or `k`: select cell above.\n"
    "- `down` or `j`: select cell below.\n"
    "- `ctrl-g`: go to last cell.\n"
    "- `1` `g`: go to first cell.\n"
    "- `ctrl-up`: move cell above.\n"
    "- `ctrl-down`: move cell below.\n"
    "- `a`: insert cell above.\n"
    "- `b`: insert cell below.\n"
    "- `x`: cut the cell.\n"
    "- `c`: copy the cell.\n"
    "- `ctrl-v`: paste cell above.\n"
    "- `v`: paste cell below.\n"
    "- `o`: set as code cell.\n"
    "- `r`: set as Markdown cell.\n"
    "- `l`: clear cell outputs.\n"
    "- `f`: fold current cell input.\n"
    "- `ctrl-f`: Search.\n"
    "- `n`: Repeat last search.\n"
    "- `ctrl-n`: Search backwards.\n"
    "- `m`,`<any>`: Set mark <key>.\n"
    "- `'`,`<any>`: Go to mark <key>.\n"
    "- `ctrl-e` or `enter`: run cell.\n"
    "- `ctrl-r` or `alt-enter`: run cell and select below.\n"
    "- `ctrl-s`: save.\n"
    "- `ctrl-p`: run all cells.\n"
    "- `ctrl-q`: exit.\n"
    "- `ctrl-h`: show help.\n"
)


class Help:

    help_mode: bool
    help_text: str
    help_window: Window
    help_line: int

    def show_help(self):
        self.help_mode = True
        self.help_text = rich_print(md)
        self.help_window = Window(
            content=FormattedTextControl(text=ANSI(self.help_text))
        )
        self.app.layout = Layout(self.help_window)
        self.help_line = 0

    def scroll_help_up(self):
        if self.help_line > 0:
            self.help_line -= 1
            text = "\n".join(self.help_text.split("\n")[self.help_line :])  # noqa
            self.help_window.content = FormattedTextControl(text=ANSI(text))

    def scroll_help_down(self):
        if self.help_line < self.help_text.count("\n"):
            self.help_line += 1
            text = "\n".join(self.help_text.split("\n")[self.help_line :])  # noqa
            self.help_window.content = FormattedTextControl(text=ANSI(text))

    def quit_help(self):
        self.help_mode = False
        self.update_layout()
        self.help_text = rich_print(md, self.console)
        self.help_window = Window(
            content=FormattedTextControl(text=ANSI(self.help_text))
        )
