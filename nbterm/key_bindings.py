import asyncio

from prompt_toolkit.filters import Condition


class DefaultKeyBindings:

    cell_entered: bool

    def bind_keys(self):
        @Condition
        def in_cell() -> bool:
            return self.cell_entered

        @Condition
        def not_in_cell() -> bool:
            return not self.cell_entered

        @self.key_bindings.add("c-q", filter=not_in_cell)
        def c_q(event):
            asyncio.create_task(self.kd.stop())
            self.app.exit()

        @self.key_bindings.add("c-s", filter=not_in_cell)
        def c_s(event):
            self.save_nb()

        @self.key_bindings.add("escape", filter=in_cell, eager=True)
        def escape(event):
            self.current_cell.update_json()
            self.exit_cell()

        @self.key_bindings.add("up", filter=not_in_cell)
        def up(event):
            self.focus(self.current_cell.idx - 1)

        @self.key_bindings.add("down", filter=not_in_cell)
        def down(event):
            self.focus(self.current_cell.idx + 1)

        @self.key_bindings.add("enter", filter=not_in_cell)
        def enter(event):
            self.enter_cell()

        @self.key_bindings.add("c-l", filter=not_in_cell)
        def c_l(event):
            self.current_cell.clear_output()

        @self.key_bindings.add("c-n", filter=not_in_cell)
        def c_n(event):
            self.current_cell.set_as_markdown()

        @self.key_bindings.add("c-o", filter=not_in_cell)
        def c_o(event):
            self.current_cell.set_as_code()

        @self.key_bindings.add("c-e", filter=not_in_cell)
        async def c_e(event):
            self.executing_cells.append(self.current_cell)
            await self.current_cell.run()

        @self.key_bindings.add("c-r", filter=not_in_cell)
        async def c_r(event):
            self.executing_cells.append(self.current_cell)
            if self.current_cell.idx == len(self.cells) - 1:
                self.insert_cell(self.current_cell.idx + 1)
            self.focus(self.current_cell.idx + 1)
            await self.executing_cells[-1].run()

        @self.key_bindings.add("c-d", filter=not_in_cell)
        def c_d(event):
            self.delete_cell(self.current_cell.idx)

        @self.key_bindings.add("c-i", filter=not_in_cell)
        def c_i(event):
            self.insert_cell(self.current_cell.idx)

        @self.key_bindings.add("c-j", filter=not_in_cell)
        def c_j(event):
            self.insert_cell(self.current_cell.idx + 1)
