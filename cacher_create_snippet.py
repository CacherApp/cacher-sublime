import sublime_plugin
import sublime
import ntpath
import json
import urllib

from .lib import util, filetypes


def library_labels(library_guid):
    store = util.store()

    libraries = list()
    libraries.append(store.get("personal_library"))
    libraries += list(map(lambda team: team["library"], store.get("teams")))

    library = list(filter(lambda lib: lib["guid"] == library_guid, libraries))[0]
    return library["labels"]


class SnippetLibraryInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Select library"

    @staticmethod
    def list_items():
        store = util.store()
        items = []

        # Personal
        personal_library_guid = store.get("personal_library")["guid"]
        items.append(
            ("Personal Library", personal_library_guid)
        )

        # Teams
        for team in store.get("teams"):
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


class SnippetTitleInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Title (required)"

    @staticmethod
    def validate(expr):
        return util.validate_input(expr)

    @staticmethod
    def confirm(title):
        return title

    @staticmethod
    def next_input(args):
        return SnippetDescriptionInputHandler(args)


class SnippetDescriptionInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Description (optional)"

    @staticmethod
    def confirm(description):
        return description

    @staticmethod
    def next_input(args):
        if ("files" in args) and len(args["files"]) > 0:
            return SnippetPublicPrivateInputHandler(args)
        else:
            return SnippetFilenameInputHandler(args)


class SnippetFilenameInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Filename (required)"

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
            if view.file_name() is None:
                return "untitled"
            else:
                return ntpath.basename(view.file_name())

    @staticmethod
    def validate(expr):
        return util.validate_input(expr)

    @staticmethod
    def confirm(filename):
        return filename

    @staticmethod
    def next_input(args):
        return SnippetPublicPrivateInputHandler(args)


class SnippetPublicPrivateInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Permission"

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
        library_guid = util.store().get("personal_library")["guid"]

        if "snippet_library" in args:
            library_guid = args["snippet_library"]

        # Only show labels if available
        if len(library_labels(library_guid)) > 0:
            return SnippetLabelInputHandler(args)
        else:
            return None


class SnippetLabelInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def placeholder():
        return "Label (optional)"

    def list_items(self):
        library_guid = util.store().get("personal_library")["guid"]

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


class CacherCreateSnippetCommand(sublime_plugin.WindowCommand):
    def run(self, snippet_library, **args):
        # group, index of view in window
        group = None
        if "group" in args:
            group = args["group"]

        index = None
        if "index" in args:
            index = args["index"]

        files = None
        if "files" in args:
            files = args["files"]

        snippet = {
            "title": args["snippet_title"],
            "description": args["snippet_description"],
            "isPrivate": args["snippet_public_private"]
        }

        if (group is not None and group >= 0) and (index is not None and index >= 0):
            # Creating snippet from tab context
            view = sublime.active_window().sheets_in_group(group)[index].view()
            content = view.substr(sublime.Region(0, view.size()))
            filetype = filetypes.get_mode_for_filename(args["snippet_filename"])

            snippet["files"] = [{
                "filename": args["snippet_filename"],
                "content": content,
                "filetype": filetype,
                "isShared": False
            }]
        elif files is not None and len(files) > 0:
            # Create snippet from selected file(s)
            snippet_files = []

            for file in files:
                with open(file, "r") as f:
                    filetype = filetypes.get_mode_for_filename(file)

                    snippet_files.append({
                        "filename": ntpath.basename(file),
                        "content": f.read(),
                        "filetype": filetype,
                        "isShared": False
                    })

            snippet["files"] = snippet_files
        else:
            # Content is either selection or the entire file content
            view = sublime.active_window().active_view()
            region = view.sel()[0]
            if region.empty():
                # Just the entire file
                content = view.substr(sublime.Region(0, view.size()))
            else:
                # The selection
                content = view.substr(region)

            filetype = filetypes.get_mode_for_filename(args["snippet_filename"])

            snippet["files"] = [{
                "filename": args["snippet_filename"],
                "content": content,
                "filetype": filetype,
                "isShared": False
            }]

        labels = []
        if "snippet_label" in args and args["snippet_label"] is not None:
            labels = [args["snippet_label"]]

        self.__create_snippet(snippet, labels, snippet_library)

    @staticmethod
    def input(args):
        return SnippetLibraryInputHandler(args)

    @staticmethod
    def __create_snippet(snippet, labels, library_guid):
        url = "{0}/sublime/snippets".format(util.settings().get("apiHost"))
        data = {
            "snippet": snippet,
            "labels": labels,
            "libraryGuid": library_guid
        }

        try:
            req = urllib.request.Request(url, headers=util.request_headers(), method="POST")

            json_data = json.dumps(data)
            json_data_bytes = json_data.encode("utf-8")
            req.add_header("Content-Type", "application/json; charset=utf-8")
            req.add_header("Content-Length", len(json_data_bytes))

            urllib.request.urlopen(req, json_data_bytes)
            sublime.status_message("Cacher: Saved \"{0}\"".format(snippet["title"]))
            sublime.active_window().run_command("cacher_refresh")
        except urllib.error.HTTPError as e:
            sublime.error_message("There was an error creating your snippet. Please try again.")
            print(e)
        except IOError:
            util.prompt_user_setup()
