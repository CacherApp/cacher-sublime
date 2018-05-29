import sublime_plugin


class CacherCreateSnippetCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.active_view().show_popup_menu(
            ["foobar", "two"],
            lambda index: print(index)
        )
