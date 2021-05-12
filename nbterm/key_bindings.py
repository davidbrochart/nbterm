from prompt_toolkit.filters import Condition


class KeyBindings:

    edit_mode: bool
    help_mode: bool

    def bind_keys(self):
        @Condition
        def edit_mode() -> bool:
            return self.edit_mode and not self.help_mode

        @Condition
        def command_mode() -> bool:
            return not self.edit_mode and not self.help_mode

        @Condition
        def help_mode() -> bool:
            return self.help_mode

        @Condition
        def not_help_mode() -> bool:
            return not self.help_mode

        @self.key_bindings.add("enter", filter=help_mode)
        @self.key_bindings.add("c-q", filter=help_mode)
        @self.key_bindings.add("escape", filter=help_mode)
        def quit_help(event):
            self.quitting = False
            self.quit_help()

        @self.key_bindings.add("up", filter=help_mode)
        def scroll_help_up(event):
            self.scroll_help_up()

        @self.key_bindings.add("down", filter=help_mode)
        def scroll_help_down(event):
            self.scroll_help_down()

        @self.key_bindings.add("c-h", filter=command_mode)
        def c_h(event):
            self.quitting = False
            self.show_help()

        @self.key_bindings.add("c-q", filter=not_help_mode)
        async def c_q(event):
            await self.exit()

        @self.key_bindings.add("c-s", filter=command_mode)
        def c_s(event):
            self.quitting = False
            self.save()

        @self.key_bindings.add("enter", filter=command_mode)
        def enter_cell(event):
            self.quitting = False
            self.enter_cell()

        @self.key_bindings.add("escape", filter=edit_mode, eager=True)
        def escape(event):
            self.quitting = False
            self.exit_cell()

        @self.key_bindings.add("up", filter=command_mode)
        def up(event):
            self.quitting = False
            self.go_up()

        @self.key_bindings.add("down", filter=command_mode)
        def down(event):
            self.quitting = False
            self.go_down()

        @self.key_bindings.add("c-up", filter=command_mode)
        def c_up(event):
            self.quitting = False
            self.move_up()

        @self.key_bindings.add("c-down", filter=command_mode)
        def c_down(event):
            self.quitting = False
            self.move_down()

        @self.key_bindings.add("l", filter=command_mode)
        def l(event):  # noqa
            self.quitting = False
            self.clear_output()

        @self.key_bindings.add("m", filter=command_mode)
        def m(event):
            self.quitting = False
            self.markdown_cell()

        @self.key_bindings.add("o", filter=command_mode)
        def o(event):
            self.quitting = False
            self.code_cell()

        @self.key_bindings.add("c-e", filter=command_mode)
        async def c_e(event):
            self.quitting = False
            await self.queue_run_cell()

        @self.key_bindings.add("c-r", filter=command_mode)
        async def c_r(event):
            self.quitting = False
            await self.queue_run_cell(and_select_below=True)

        @self.key_bindings.add("x", filter=command_mode)
        def x(event):
            self.quitting = False
            self.cut_cell()

        @self.key_bindings.add("c", filter=command_mode)
        def c(event):
            self.quitting = False
            self.copy_cell()

        @self.key_bindings.add("c-v", filter=command_mode)
        def c_v(event):
            self.quitting = False
            self.paste_cell()

        @self.key_bindings.add("v", filter=command_mode)
        def v(event):
            self.quitting = False
            self.paste_cell(below=True)

        @self.key_bindings.add("a", filter=command_mode)
        def a(event):
            self.quitting = False
            self.insert_cell()

        @self.key_bindings.add("b", filter=command_mode)
        def b(event):
            self.quitting = False
            self.insert_cell(below=True)
