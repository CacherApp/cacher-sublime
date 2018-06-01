import sublime_plugin
import webbrowser
from .lib import snippets, util

config = util.load_config()


class OpenSnippetPageInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        return snippets.snippets_for_list()


class CacherOpenSnippetPage(sublime_plugin.TextCommand):
    @staticmethod
    def run(edit, open_snippet_page):
        if not open_snippet_page:
            return

        webbrowser.open("{0}/snippet/{1}".format(config["hosts"]["snippets"], open_snippet_page))

    @staticmethod
    def input(args):
        return OpenSnippetPageInputHandler()
