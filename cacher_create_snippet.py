import sublime_plugin
import sublime
from .lib import store


def validate_input(expr):
    return len(expr) > 0


class SnippetDescriptionInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Enter snippet description (optional)"

    @staticmethod
    def validate(expr):
        return validate_input(expr)

    @staticmethod
    def confirm(description):
        return description


class SnippetTitleInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Enter snippet title (required)"

    @staticmethod
    def validate(expr):
        return validate_input(expr)

    @staticmethod
    def confirm(title):
        return title

    @staticmethod
    def next_input(args):
        return SnippetDescriptionInputHandler(args)


class SnippetLibraryInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Select library for new snippet"

    @staticmethod
    def list_items():
        items = []

        # Personal
        personal_library_guid = store.get_val("personal_library")["guid"]
        items.append(
            ("Personal Library", personal_library_guid)
        )

        # Teams
        for team in store.get_val("teams"):
            items.append(
                (team["name"], team["guid"])
            )

        return items

    @staticmethod
    def confirm(guid):
        return guid

    @staticmethod
    def next_input(args):
        return SnippetTitleInputHandler(args)


class CacherCreateSnippetCommand(sublime_plugin.WindowCommand):
    @staticmethod
    def run(snippet_library, snippet_title, snippet_description, **args):
        group = args["group"]
        index = args["index"]
        files = args["files"]

        print(snippet_library)
        print(snippet_title)
        print(snippet_description)
        print(args)

        if (group and group >= 0) and (index and index >= 0):
            # Creating snippet from tab context
            view = sublime.active_window().sheets_in_group(group)[index].view()
            body = view.substr(sublime.Region(0, view.size()))
        elif files and len(files) > 0:
            # Create snippet from selected file(s)
            print(files)

    @staticmethod
    def input(args):
        # Don't pick library if we don't need to
        teams = store.get_val("teams")
        if len(teams) > 0:
            return SnippetLibraryInputHandler(args)
        else:
            personal_library_guid = store.get_val("personal_library")["guid"]
            return SnippetTitleInputHandler(args)
