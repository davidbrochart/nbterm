from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings


def default_kb(nb):
    kb = KeyBindings()

    @Condition
    def in_cell():
        return nb.cell_entered

    @Condition
    def not_in_cell():
        return not nb.cell_entered

    @kb.add("c-q", filter=not_in_cell)
    def _(event):
        nb.app.exit()

    @kb.add("c-s", filter=not_in_cell)
    def _(event):
        nb.save_nb()

    @kb.add("escape", filter=in_cell)
    def _(event):
        nb.current_cell.update_json()
        nb.exit_cell()

    @kb.add("up", filter=not_in_cell)
    def _(event):
        cell_idx = nb.current_cell.idx
        if cell_idx > 0:
            nb.focus(cell_idx - 1)

    @kb.add("down", filter=not_in_cell)
    def _(event):
        cell_idx = nb.current_cell.idx
        if cell_idx < len(nb.cells) - 1:
            nb.focus(cell_idx + 1)

    @kb.add("enter", filter=not_in_cell)
    def _(event):
        nb.enter_cell()

    @kb.add("c-l", filter=not_in_cell)
    def _(event):
        nb.current_cell.clear_output()

    @kb.add("c-e", filter=not_in_cell)
    def _(event):
        nb.current_cell.run()

    @kb.add("c-r", filter=not_in_cell)
    def _(event):
        nb.current_cell.run()
        cell_idx = nb.current_cell.idx
        if cell_idx < len(nb.cells) - 1:
            nb.focus(cell_idx + 1)

    @kb.add("c-i", filter=not_in_cell)
    def _(event):
        cell_idx = nb.current_cell.idx
        nb.insert_cell(cell_idx)

    @kb.add("c-j", filter=not_in_cell)
    def _(event):
        cell_idx = nb.current_cell.idx + 1
        nb.insert_cell(cell_idx)

    return kb
