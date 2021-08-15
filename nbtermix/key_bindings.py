from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings as KeBi


class KeyBindings:

    edit_mode: bool
    help_mode: bool

    # Handling of escape.
    key_bindings = KeBi()
    handle = key_bindings.add
    handle("escape", eager=True)

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

        @self.key_bindings.add("c-t", filter=edit_mode)
        def ce_mode_t(event):
            # self.cell_edit_mode = True
            self.edit_result_in_editor()

        @self.key_bindings.add("c-w", filter=edit_mode)
        def ce_mode_w(event):
            self.edit_in_editor()
            self.save()

        @self.key_bindings.add("c-f", filter=edit_mode)
        def ce_mode_f(event):
            self.run_in_console()
            self.update_layout()

        @self.key_bindings.add("c-e", filter=edit_mode)
        async def e_mod_c_e(event):
            self.edit_mode = False
            self.exit_cell()

        @self.key_bindings.add("c-s", filter=edit_mode)
        def e_mod_c_s(event):
            self.quitting = False
            self.save()

        @self.key_bindings.add("c-r", filter=edit_mode)
        async def e_mod_c_r(event):
            self.edit_mode = False
            self.exit_cell()
            await self.queue_run_cell(and_select_below=True)
            self.quitting = False
            self.enter_cell()

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
        @self.key_bindings.add("c-x", filter=not_help_mode)
        async def c_q(event):
            await self.exit()

        @self.key_bindings.add("c-s", filter=command_mode)
        def c_s(event):
            self.quitting = False
            self.save()

        # @self.key_bindings.add("enter", filter=command_mode)
        @self.key_bindings.add("e", filter=command_mode)
        def e(event):
            self.quitting = False
            self.enter_cell()

        @self.key_bindings.add("escape", filter=edit_mode, eager=True)
        def escape(event):
            self.quitting = False
            self.exit_cell()

        @self.key_bindings.add("f", filter=command_mode)
        def f(event):
            self.toggle_fold()

        @self.key_bindings.add("up", filter=command_mode)
        @self.key_bindings.add("k", filter=command_mode)
        def up(event):
            self.quitting = False
            self.go_up()

        @self.key_bindings.add("down", filter=command_mode)
        @self.key_bindings.add("j", filter=command_mode)
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

        @self.key_bindings.add("r", filter=command_mode)
        def m(event):
            self.quitting = False
            self.markdown_cell()

        @self.key_bindings.add("o", filter=command_mode)
        def o(event):
            self.quitting = False
            self.code_cell()

        @self.key_bindings.add("c-e", filter=command_mode)
        @self.key_bindings.add("enter", filter=command_mode)
        async def c_e(event):
            self.quitting = False
            await self.queue_run_cell()

        @self.key_bindings.add("c-r", filter=command_mode)
        # ALT + ENTER (works as shift enter either)
        @self.key_bindings.add("escape", "enter", filter=command_mode)
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

        @self.key_bindings.add("c-p", filter=command_mode)
        async def c_p(event):
            await self.run_all()

        @self.key_bindings.add("c-g", filter=command_mode)
        def G(event):
            self.goto_last_cell()

        @self.key_bindings.add("1", "g", filter=command_mode)
        def k_1_g(event):
            self.goto_first_cell()

        @self.key_bindings.add("c-f", filter=command_mode)
        def c_f(event):
            self.nb_search()

        @self.key_bindings.add("n", filter=command_mode)
        def n(event):
            self.nb_repeat_search()

        @self.key_bindings.add("c-n", filter=command_mode)
        def c_n(event):
            self.nb_search_backwards()

        @self.key_bindings.add("m", "<any>", filter=command_mode)
        def set_m(event):
            skey = ord(event.key_sequence[1].key)
            self.nb_set_mark(skey)

        @self.key_bindings.add("'", "<any>", filter=command_mode)
        def goto_m(event):
            skey = ord(event.key_sequence[1].key)
            self.nb_goto_mark(skey)
