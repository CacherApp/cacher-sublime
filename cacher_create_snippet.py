import sublime_plugin
import sublime


class SnippetLibraryInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        return [
            ("Persona", "Team 1")
        ]


class CacherCreateSnippetCommand(sublime_plugin.WindowCommand):
    @staticmethod
    def run(snippet_library, **args):
        group = args["group"]
        index = args["index"]

        # Creating snippet from tab context
        if (group and group >= 0) and (index and index >= 0):
            view = sublime.active_window().sheets_in_group(group)[index].view()
            body = view.substr(sublime.Region(0, view.size()))

    @staticmethod
    def input(args):
        return SnippetLibraryInputHandler()
