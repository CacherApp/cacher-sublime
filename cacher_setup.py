import sublime
import sublime_plugin


class SetupInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, view):
        self.view = view


class CacherSetupCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "Hello, Cacher!")

    def input(self, args):
        return SetupInputHandler(self.view)
