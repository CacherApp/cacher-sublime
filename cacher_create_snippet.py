import sublime_plugin
import sublime
import ntpath
from .lib import store


def validate_input(expr):
    return len(expr) > 0


def library_labels(library_guid):
    libraries = list()
    libraries.append(store.get_val("personal_library"))
    libraries += list(map(lambda team: team["library"], store.get_val("teams")))

    library = list(filter(lambda lib: lib["guid"] == library_guid, libraries))[0]
    return library["labels"]


class SnippetLabelInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Attach label (optional)"

    def list_items(self):
        library_guid = store.get_val("personal_library")["guid"]

        if "snippet_library" in self.args:
            library_guid = self.args["snippet_library"]

        labels = library_labels(library_guid)
        label_items = list(map(lambda lab: (lab["title"], lab["guid"]), labels))

        return [
            ("(No label)", None)
        ] + label_items

    @staticmethod
    def confirm(label_guid):
        return label_guid


class SnippetPublicPrivateInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Select snippet permission"

    @staticmethod
    def list_items():
        return [
            ("Private", True),
            ("Public", False)
        ]

    @staticmethod
    def confirm(is_private):
        return is_private

    @staticmethod
    def next_input(args):
        library_guid = store.get_val("personal_library")["guid"]

        if "snippet_library" in args:
            library_guid = args["snippet_library"]

        # Only show labels if available
        if len(library_labels(library_guid)) > 0:
            return SnippetLabelInputHandler(args)
        else:
            return None


class SnippetFilenameInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Enter filename (required)"

    def initial_text(self):
        # Fetch the filename from active view
        group = None
        if "group" in self.args:
            group = self.args["group"]

        index = None
        if "index" in self.args:
            index = self.args["index"]

        if (group is not None and group >= 0) and (index is not None and index >= 0):
            # Creating snippet from tab context
            view = sublime.active_window().sheets_in_group(group)[index].view()
            return ntpath.basename(view.file_name())
        else:
            # Otherwise use filename of active view
            view = sublime.active_window().active_view()
            return ntpath.basename(view.file_name())

    @staticmethod
    def validate(expr):
        return validate_input(expr)

    @staticmethod
    def confirm(filename):
        return filename

    @staticmethod
    def next_input(args):
        return SnippetPublicPrivateInputHandler(args)


class SnippetDescriptionInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Enter snippet description (optional)"

    @staticmethod
    def confirm(description):
        return description

    @staticmethod
    def next_input(args):
        if ("files" in args) and len(args["files"]) > 0:
            return SnippetPublicPrivateInputHandler(args)
        else:
            return SnippetFilenameInputHandler(args)


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
                (team["name"], team["library"]["guid"])
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
    def run(snippet_library,
            snippet_title,
            snippet_description,
            snippet_filename,
            snippet_public_private,
            snippet_label,
            **args):
        group = None
        if "group" in args:
            group = args["group"]

        index = None
        if "index" in args:
            index = args["index"]

        files = None
        if "files" in args:
            files = args["files"]

        print(snippet_library)
        print(snippet_title)
        print(snippet_description)
        print(snippet_filename)
        print(snippet_public_private)
        print(snippet_label)
        print(args)

        if (group is not None and group >= 0) and (index is not None and index >= 0):
            # Creating snippet from tab context
            view = sublime.active_window().sheets_in_group(group)[index].view()
            body = view.substr(sublime.Region(0, view.size()))
        elif files is not None and len(files) > 0:
            # Create snippet from selected file(s)
            print(files)

    @staticmethod
    def input(args):
        # Don't pick library if we don't need to
        teams = store.get_val("teams")
        if len(teams) > 0:
            return SnippetLibraryInputHandler(args)
        else:
            return SnippetTitleInputHandler(args)

    def __create_snippet(self):
        print("create")
