import sublime_plugin
import sublime
from .lib import store, snippets

snippets.initialize()


class InsertSnippetInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        list_snippets = []

        for snippet in store.get_val("snippets"):
            for file in snippet["files"]:
                description = snippet["description"] or ""

                if snippet["team"]:
                    description = "[{0}] {1}".format(snippet["team"]["name"], description)

                if len(snippet["labels"]) > 0:
                    for label in snippet["labels"]:
                        description = "({0}) {1}".format(label, description)

                title = "{0} - {1}".format(snippet["title"], description)
                list_snippets.append(
                    (title, file["content"])
                )

        return list_snippets

    @staticmethod
    def preview(value):
        # Just the first 10 lines
        content = ""
        for line in value.splitlines()[:11]:
            content += line + "<br />"

        preview_content = sublime.Html(content)
        return preview_content

    @staticmethod
    def placeholder():
        return "Search by title"


class CacherInsertSnippet(sublime_plugin.TextCommand):
    def run(self, edit, insert_snippet):
        selection = self.view.sel()
        for region in selection:
            self.view.replace(edit, region, insert_snippet)

    @staticmethod
    def input(args):
        return InsertSnippetInputHandler()

