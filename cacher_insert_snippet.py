import sublime_plugin
import sublime


class InsertSnippetInputHandler(sublime_plugin.ListInputHandler):
    def list_items(self):
        return [
            ("This is a function which will toggle the visibility"
             " of a resource depending on what step in the play all sequence "
             "an animation is in", "1"),
            ("Two", "2")
        ]

    def preview(self, value):
        if value == "1":
            return "foobar"
        else:
            return "Doo what"

    def placeholder(self):
        return "Search by title"


class CacherInsertSnippet(sublime_plugin.WindowCommand):
    def input(self, args):
        return InsertSnippetInputHandler()

