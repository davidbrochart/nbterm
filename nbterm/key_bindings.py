import asyncio

from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

from .format import save_nb


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
        asyncio.create_task(nb.kd.stop())
        nb.app.exit()

    @kb.add("c-s", filter=not_in_cell)
    def _(event):
        save_nb(nb)

    @kb.add("escape", filter=in_cell)
    def _(event):
        nb.current_cell.update_json()
        nb.exit_cell()

    @kb.add("up", filter=not_in_cell)
    def _(event):
        nb.focus(nb.current_cell.idx - 1)

    @kb.add("down", filter=not_in_cell)
    def _(event):
        nb.focus(nb.current_cell.idx + 1)

    @kb.add("enter", filter=not_in_cell)
    def _(event):
        nb.enter_cell()

    @kb.add("c-l", filter=not_in_cell)
    def _(event):
        nb.current_cell.clear_output()

    @kb.add("c-n", filter=not_in_cell)
    def _(event):
        nb.current_cell.set_as_markdown()

    @kb.add("c-o", filter=not_in_cell)
    def _(event):
        nb.current_cell.set_as_code()

    @kb.add("c-e", filter=not_in_cell)
    async def _(event):
        nb.executing_cells.append(nb.current_cell)
        nb.current_cell.clear_output()
        await nb.current_cell.run(nb)

    @kb.add("c-r", filter=not_in_cell)
    async def _(event):
        nb.executing_cells.append(nb.current_cell)
        nb.current_cell.clear_output()
        if nb.current_cell.idx == len(nb.cells) - 1:
            nb.insert_cell(nb.current_cell.idx + 1)
        nb.focus(nb.current_cell.idx + 1)
        await nb.executing_cells[-1].run(nb)

    @kb.add("c-i", filter=not_in_cell)
    def _(event):
        nb.insert_cell(nb.current_cell.idx)

    @kb.add("c-j", filter=not_in_cell)
    def _(event):
        nb.insert_cell(nb.current_cell.idx + 1)

    return kb
