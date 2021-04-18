from prompt_toolkit.filters import Condition


class KeyBindings:

    edit_mode: bool

    def bind_keys(self):
        @Condition
        def edit_mode() -> bool:
            return self.edit_mode

        @Condition
        def command_mode() -> bool:
            return not self.edit_mode

        @self.key_bindings.add("c-q")
        async def c_q(event):
            await self.exit()

        @self.key_bindings.add("c-s", filter=command_mode)
        def c_s(event):
            self.save()

        @self.key_bindings.add("enter", filter=command_mode)
        def enter(event):
            self.enter_cell()

        @self.key_bindings.add("escape", filter=edit_mode, eager=True)
        def escape(event):
            self.exit_cell()

        @self.key_bindings.add("up", filter=command_mode)
        def up(event):
            self.go_up()

        @self.key_bindings.add("down", filter=command_mode)
        def down(event):
            self.go_down()

        @self.key_bindings.add("c-up", filter=command_mode)
        def c_up(event):
            self.move_up()

        @self.key_bindings.add("c-down", filter=command_mode)
        def c_down(event):
            self.move_down()

        @self.key_bindings.add("l", filter=command_mode)
        def l(event):  # noqa
            self.clear_output()

        @self.key_bindings.add("m", filter=command_mode)
        def m(event):
            self.markdown_cell()

        @self.key_bindings.add("o", filter=command_mode)
        def o(event):
            self.code_cell()

        @self.key_bindings.add("c-e", filter=command_mode)
        async def c_e(event):
            await self.run_cell()

        @self.key_bindings.add("c-r", filter=command_mode)
        async def c_r(event):
            await self.run_cell(and_select_below=True)

        @self.key_bindings.add("x", filter=command_mode)
        def x(event):
            self.cut_cell()

        @self.key_bindings.add("c", filter=command_mode)
        def c(event):
            self.copy_cell()

        @self.key_bindings.add("c-v", filter=command_mode)
        def c_v(event):
            self.paste_cell()

        @self.key_bindings.add("v", filter=command_mode)
        def v(event):
            self.paste_cell(below=True)

        @self.key_bindings.add("a", filter=command_mode)
        def a(event):
            self.insert_cell()

        @self.key_bindings.add("b", filter=command_mode)
        def b(event):
            self.insert_cell(below=True)
