import sublime_plugin
import sublime
from .lib import snippets, util


# Called when Cacher loads
def plugin_loaded():
    if not util.credentials_exist():
        util.prompt_user_setup()
    else:
        snippets.initialize()


class InsertSnippetInputHandler(sublime_plugin.ListInputHandler):
    @staticmethod
    def list_items():
        list_snippets = []

        for snippet in util.store().get("snippets"):
            for file in snippet["files"]:
                description = snippet.get("description", "")

                if snippet["team"]:
                    description = "[{0}] {1}".format(snippet["team"]["name"], description)

                if len(snippet["labels"]) > 0:
                    for label in snippet["labels"]:
                        description = "({0}) {1}".format(label, description)

                title = "{0} / {1} - {2}".format(snippet["title"], file["filename"], description)
                list_snippets.append(
                    (title, file["content"])
                )

        return list_snippets

    @staticmethod
    def preview(value):
        if not value:
            return ""

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
        if not insert_snippet:
            return

        selection = self.view.sel()
        for region in selection:
            self.view.replace(edit, region, insert_snippet)

    @staticmethod
    def input(args):
        return InsertSnippetInputHandler()

