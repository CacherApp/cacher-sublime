import sublime_plugin
from .lib import snippets, util


class OpenSnippetPageInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        return snippets.snippets_for_list()


class CacherOpenSnippetPage(sublime_plugin.ApplicationCommand):
    @staticmethod
    def run(open_snippet_page):
        if not open_snippet_page:
            return

        util.open_url(
            host=util.settings().get("snippetsHost"),
            path="/snippet/{0}".format(open_snippet_page)
        )

    @staticmethod
    def input(args):
        return OpenSnippetPageInputHandler()
