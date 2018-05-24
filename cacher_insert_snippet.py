import sublime_plugin
import sublime
from .lib import store, snippets

snippets.initialize()


class InsertSnippetInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        list_snippets = []

        for snippet in store.get_val("snippets"):
            description = snippet["description"] or ""

            if snippet["team"]:
                description = "[{0}] {1}".format(snippet["team"]["name"], description)

            if len(snippet["labels"]) > 0:
                for label in snippet["labels"]:
                    description = "({0}) {1}".format(label, description)

            title = "{0} - {1}".format(snippet["title"], description)
            list_snippets.append(
                (title, snippet["guid"])
            )

        return list_snippets

    @staticmethod
    def preview(value):
        return ""

    @staticmethod
    def placeholder():
        return ""


class CacherInsertSnippet(sublime_plugin.WindowCommand):
    def run(self, insert_snippet):
        print(insert_snippet)

    def input(self, args):
        return InsertSnippetInputHandler()

