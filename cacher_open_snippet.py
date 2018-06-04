import sublime_plugin
import webbrowser
from .lib import snippets, util


class OpenSnippetInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        return snippets.snippets_for_list()


class CacherOpenSnippet(sublime_plugin.TextCommand):
    @staticmethod
    def run(edit, open_snippet):
        if not open_snippet:
            return

        snippet = snippets.snippet_with_guid(open_snippet)
        if not snippet:
            return

        if snippet["team"]:
            webbrowser.open("{0}/enter?action=goto_team_snippet&t={1}&s={2}"
                            .format(util.settings().get("appHost"), snippet["team"]["guid"], snippet["guid"]))
        else:
            webbrowser.open("{0}/enter?action=goto_snippet&s={1}"
                            .format(util.settings().get("appHost"), snippet["guid"]))

    @staticmethod
    def input(args):
        return OpenSnippetInputHandler()
